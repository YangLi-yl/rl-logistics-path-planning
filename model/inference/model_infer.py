import gym
import numpy as np
from stable_baselines3 import PPO

class CampusLogisticsInfer:
    """模型推理类"""
    def __init__(self, model_path=None, max_delivery_points=20):
        """
        初始化推理类
        :param model_path: 训练好的模型路径
        :param max_delivery_points: 最大配送点数量（与训练时保持一致）
        """
        if model_path is None:
            import os
            # 获取当前文件所在目录的父目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '../..'))
            model_path = os.path.join(project_root, 'model', 'models', 'campus_logistics_ppo')
        self.model = PPO.load(model_path)
        # 直接创建环境实例，设置与训练时相同的max_delivery_points参数
        from envs.campus_logistics_env import CampusLogisticsEnv
        self.env = CampusLogisticsEnv(config={'max_points': max_delivery_points})
        self.env = self.env.unwrapped  # 获取底层环境对象

    def infer_path(self, start_position, delivery_points, algorithm="greedy"):
        """
        路径规划推理
        :param start_position: 起点坐标 (lon, lat)
        :param delivery_points: 配送点列表 [{"lon": x, "lat": y, "weight": w, "time_window": (s, e)}]
        :param algorithm: 路径规划算法 ("greedy" 或 "model")
        :return: 规划结果 {"delivery_order": [], "total_distance": 0.0, "estimated_time": 0.0}
        """
        print(f"开始推理 - 起点: {start_position}, 配送点数量: {len(delivery_points)}")
        print(f"环境最大配送点数量: {self.env.max_delivery_points}")
        print(f"使用算法: {algorithm}")
        
        # 检查配送点数量
        if len(delivery_points) > self.env.max_delivery_points:
            print(f"警告: 配送点数量({len(delivery_points)})超过环境最大限制({self.env.max_delivery_points})")
            return {"delivery_order": [], "total_distance_km": 0.0, "total_distance_m": 0.0, "estimated_time_min": 0.0}
        
        # 创建配送点索引映射，用于保持原始索引信息
        original_indices = list(range(len(delivery_points)))
        
        # 重置环境
        obs = self.env.reset()
        
        # 手动设置环境状态
        self.env.current_position = np.array(start_position, dtype=np.float32)
        self.env.remaining_points = delivery_points.copy()  # 使用副本避免修改原始数据
        self.env.remaining_load = self.env.vehicle_load_limit
        self.env.remaining_time = 1440.0
        self.env.traffic_factor = 1.0  # 固定路况系数
        self.env.done = False
        
        delivery_order = []  # 配送顺序（原始索引）
        total_distance = 0.0  # 总距离（km）
        total_time = 0.0      # 总时间（分钟）
        current_step = 0
        max_steps = 2 * len(delivery_points)  # 设置最大步数
        
        print(f"环境初始化完成 - 当前位置: {self.env.current_position}, 剩余点: {len(self.env.remaining_points)}, 剩余载重: {self.env.remaining_load}")
        
        # 路径规划主循环
        while not self.env.done and current_step < max_steps and len(self.env.remaining_points) > 0:
            print(f"\n步骤 {current_step}:")
            print(f"  当前位置: {self.env.current_position}")
            print(f"  剩余配送点: {len(self.env.remaining_points)}")
            
            # 根据选择的算法选择下一个配送点
            if algorithm == "model":
                # 使用模型进行预测
                obs = self.env._get_observation()
                action, _states = self.model.predict(obs, deterministic=True)
                print(f"  模型预测动作: {action}")
            else:
                # 使用贪心算法选择最近的配送点
                distances = []
                for i, point in enumerate(self.env.remaining_points):
                    distance = self.env._calculate_distance(
                        self.env.current_position[0], self.env.current_position[1],
                        point["lon"], point["lat"]
                    )
                    distances.append((distance, i))
                distances.sort()
                closest_distance, action = distances[0]
                print(f"  贪心算法选择最近的配送点 {action}, 距离: {closest_distance:.4f}km")
            
            # 保存当前状态用于计算距离
            current_pos = self.env.current_position.copy()
            target_point = self.env.remaining_points[action].copy()
            
            # 执行动作
            obs, reward, done, info = self.env.step(action)
            print(f"  执行结果 - 奖励: {reward:.2f}, 完成: {done}, 有效动作: {info['valid_action']}")
            
            if info["valid_action"]:
                # 获取原始配送点索引
                original_idx = original_indices[action]
                delivery_order.append(original_idx)
                
                # 计算行驶距离
                distance = self.env._calculate_distance(
                    current_pos[0], current_pos[1],
                    target_point["lon"], target_point["lat"]
                )
                total_distance += distance
                
                # 计算行驶时间
                travel_time = (distance / self.env.base_speed) * self.env.traffic_factor * 60
                total_time += travel_time
                
                print(f"  配送完成! 原始索引: {original_idx}, 动态索引: {action}, 距离: {distance:.4f}km, 时间: {travel_time:.2f}min")
                print(f"  当前配送顺序(原始索引): {delivery_order}")
                print(f"  当前总距离: {total_distance:.4f}km, 总时间: {total_time:.2f}min")
                
                # 更新原始索引列表
                del original_indices[action]
            else:
                print(f"  动作无效，跳过此配送点")
                
            # 更新结束标记
            self.env.done = done or len(self.env.remaining_points) == 0
            
            current_step += 1
        
        print(f"\n推理完成 - 步骤数: {current_step}, 配送顺序(原始索引): {delivery_order}, 总距离: {total_distance:.4f}km, 总时间: {total_time:.2f}min")
        print(f"结束状态 - done: {self.env.done}, 剩余点: {len(self.env.remaining_points)}")

        # 构造推理结果
        result = {
            "delivery_order": delivery_order,
            "total_distance_km": round(total_distance, 2),
            "total_distance_m": round(total_distance * 1000, 2),
            "estimated_time_min": round(total_time, 2)
        }
        return result
    
    def infer_from_json(self, json_input):
        """
        从JSON格式输入进行推理
        :param json_input: JSON格式的输入数据
        :return: JSON格式的推理结果
        
        输入格式示例：
        {
            "start_position": [119.9836, 36.3504],
            "delivery_points": [
                {"lon": 119.9782, "lat": 36.3489, "weight": 2.5, "time_window": [600, 690]},
                {"lon": 119.9901, "lat": 36.3527, "weight": 3.0, "time_window": [630, 720]}
            ],
            "algorithm": "model"  # 可选，"model"或"greedy"，默认"model"
        }
        
        输出格式示例：
        {
            "success": true,
            "delivery_order": [1, 0],
            "total_distance_km": 2.56,
            "total_distance_m": 2560.0,
            "estimated_time_min": 15.36
        }
        """
        try:
            # 解析输入参数
            start_position = tuple(json_input.get("start_position", []))
            delivery_points = json_input.get("delivery_points", [])
            algorithm = json_input.get("algorithm", "model")
            
            # 验证输入参数
            if not start_position or len(start_position) != 2:
                return {
                    "success": False,
                    "error": "Invalid start_position",
                    "message": "Start position must be a tuple with 2 elements (lon, lat)"
                }
            
            if not isinstance(delivery_points, list):
                return {
                    "success": False,
                    "error": "Invalid delivery_points",
                    "message": "Delivery points must be a list"
                }
            
            # 处理配送点的time_window（转换为元组）
            for point in delivery_points:
                if isinstance(point.get("time_window"), list):
                    point["time_window"] = tuple(point["time_window"])
            
            # 调用推理方法
            result = self.infer_path(start_position, delivery_points, algorithm)
            
            # 添加成功标记
            result["success"] = True
            
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "message": "An error occurred during inference"
            }

if __name__ == "__main__":
    import sys
    import os
    import json
    
    # 添加父目录到Python路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 导入环境
    import envs
    
    try:
        # 测试推理接口
        print("=" * 50)
        print("加载模型...")
        infer = CampusLogisticsInfer("../train/models/checkpoints/campus_ppo_440000_steps.zip")
        print("模型加载成功！")
        
        # 模拟校园配送点
        print("\n设置配送参数...")
        start_pos = (119.9836, 36.3504)  # 图书馆坐标
        delivery_points = [
            {"lon": 119.9782, "lat": 36.3489, "weight": 2.5, "time_window": (600, 690)},  # 宿舍区（10:00-11:30）
            {"lon": 119.9901, "lat": 36.3527, "weight": 3.0, "time_window": (630, 720)}   # 教学楼（10:30-12:00）
        ]
        print(f"起点：{start_pos}")
        print(f"配送点数量：{len(delivery_points)}")
        
        print("\n1. 测试传统推理接口...")
        # 默认使用贪心算法，因为模型预测目前存在问题
        result = infer.infer_path(start_pos, delivery_points, algorithm="greedy")
        
        print("\n" + "=" * 50)
        print("路径规划结果：")
        print("=" * 50)
        print(f"配送顺序索引：{result['delivery_order']}")
        print(f"总距离：{result['total_distance_m']}米")
        print(f"预计耗时：{result['estimated_time_min']}分钟")
        
        # 测试JSON接口
        print("\n" + "=" * 50)
        print("2. 测试JSON推理接口...")
        print("=" * 50)
        
        # 构造JSON输入
        json_input = {
            "start_position": [119.9836, 36.3504],
            "delivery_points": [
                {"lon": 119.9782, "lat": 36.3489, "weight": 2.5, "time_window": [600, 690]},
                {"lon": 119.9901, "lat": 36.3527, "weight": 3.0, "time_window": [630, 720]}
            ],
            "algorithm": "greedy"
        }
        
        print("JSON输入:")
        print(json.dumps(json_input, indent=2, ensure_ascii=False))
        
        result_json = infer.infer_from_json(json_input)
        
        print("\nJSON输出:")
        print(json.dumps(result_json, indent=2, ensure_ascii=False))
        
        print("\n" + "=" * 50)
        print("推理完成！")
        
    except Exception as e:
        print(f"\n推理过程中发生错误：{e}")
        import traceback
        traceback.print_exc()
