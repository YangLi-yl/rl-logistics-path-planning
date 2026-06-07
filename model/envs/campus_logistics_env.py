import gym
import numpy as np
from gym import spaces
from utils.reward_calculator import calculate_reward

class CampusLogisticsEnv(gym.Env):
    """
    校园物流路径规划Gym环境
    场景约束：
    - 校园配送点数量：1-20个
    - 车辆载重上限：20kg（可配置）
    - 配送时间窗：每个配送点指定HH:MM-HH:MM时效范围
    - 动态路况：模拟校园路段拥堵系数（0.8-1.2倍基础耗时）
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, config=None):
        super(CampusLogisticsEnv, self).__init__()
        # 配置参数初始化
        self.config = config or {}
        self.max_delivery_points = self.config.get('max_points', 20)  # 最大配送点数量
        self.vehicle_load_limit = self.config.get('load_limit', 20.0)  # 车辆载重上限(kg)
        self.base_speed = self.config.get('base_speed', 5.0)  # 基础行驶速度(km/h)
        self.time_window_penalty = self.config.get('time_penalty', 10)  # 超时惩罚系数

        # 1. 定义状态空间（Observation Space）
        # 状态维度：当前坐标(2) + 剩余配送点坐标(n×2) + 剩余载重(1) + 剩余时间(1) + 路况系数(1)
        # 坐标范围：校园经纬度区间（示例：经度119.97-120.00，纬度36.34-36.36）
        obs_low = np.concatenate([
            [119.97, 36.34],  # 当前坐标下限
            np.full(2 * self.max_delivery_points, 119.97),  # 剩余配送点坐标下限
            [0.0],  # 剩余载重下限
            [0.0],  # 剩余时间下限
            [0.8]   # 路况系数下限
        ])
        obs_high = np.concatenate([
            [120.00, 36.36],  # 当前坐标上限
            np.full(2 * self.max_delivery_points, 120.00),  # 剩余配送点坐标上限
            [self.vehicle_load_limit],  # 剩余载重上限
            [1440.0],  # 剩余时间上限（分钟，24小时）
            [1.2]      # 路况系数上限
        ])
        self.observation_space = spaces.Box(
            low=obs_low,
            high=obs_high,
            dtype=np.float32
        )

        # 2. 定义动作空间（Action Space）
        # 动作：选择下一个配送点的索引（0~max_delivery_points-1），离散型
        self.action_space = spaces.Discrete(self.max_delivery_points)

        # 环境内部状态初始化
        self.current_position = None  # 当前坐标 (lon, lat)
        self.remaining_points = None  # 剩余配送点列表 [{"lon": x, "lat": y, "weight": w, "time_window": (start, end)}]
        self.remaining_load = None    # 剩余载重
        self.remaining_time = None    # 剩余时间（分钟）
        self.traffic_factor = None    # 路况系数
        self.done = None              # 回合结束标记

    def reset(self, seed=None):
        """
        重置环境至初始状态
        :param seed: 随机种子（可选）
        :return: initial_observation 初始状态观测值
        """
        if seed is not None:
            np.random.seed(seed)
        
        # 初始化随机配送点（模拟校园场景）
        self.current_position = np.array([
            np.random.uniform(119.97, 120.00),
            np.random.uniform(36.34, 36.36)
        ], dtype=np.float32)
        # 随机生成剩余配送点（数量1~max_delivery_points）
        n_points = np.random.randint(1, self.max_delivery_points + 1)
        self.remaining_points = []
        for _ in range(n_points):
            self.remaining_points.append({
                "lon": np.random.uniform(119.97, 120.00),
                "lat": np.random.uniform(36.34, 36.36),
                "weight": np.random.uniform(0.5, 5.0),  # 单个包裹重量0.5-5kg
                "time_window": (
                    np.random.randint(0, 1440),  # 时间窗开始（分钟）
                    np.random.randint(0, 1440)
                )
            })
        # 确保时间窗结束>开始
        for p in self.remaining_points:
            if p["time_window"][1] <= p["time_window"][0]:
                p["time_window"] = (p["time_window"][0], p["time_window"][0] + 60)
        self.remaining_load = self.vehicle_load_limit
        self.remaining_time = 1440.0  # 初始剩余时间24小时
        self.traffic_factor = np.random.uniform(0.8, 1.2)  # 随机路况系数
        self.done = False

        # 构造初始观测值
        obs = self._get_observation()
        return obs

    def step(self, action):
        """
        执行一步动作，更新环境状态
        :param action: 动作（配送点索引）
        :return: observation, reward, done, info
        """
        if self.done:
            raise ValueError("环境已结束，需先调用reset()重置")
        
        # 1. 验证动作有效性（索引是否在剩余配送点范围内）
        done = False
        info = {"valid_action": True}
        if action >= len(self.remaining_points):
            # 无效动作：惩罚奖励，不更新状态
            reward = -100.0
            info["valid_action"] = False
            obs = self._get_observation()
            return obs, reward, done, info

        # 2. 执行有效动作：选择下一个配送点
        target_point = self.remaining_points[action]
        # 计算行驶距离（经纬度转米，简化公式）
        distance_km = self._calculate_distance(
            self.current_position[0], self.current_position[1],
            target_point["lon"], target_point["lat"]
        )
        # 计算行驶时间（分钟）= 距离/速度 * 路况系数 * 60
        travel_time = (distance_km / self.base_speed) * self.traffic_factor * 60
        # 扣除行驶时间
        self.remaining_time -= travel_time

        # 3. 检查时间窗约束
        arrive_time = 1440.0 - self.remaining_time
        time_window_start, time_window_end = target_point["time_window"]
        time_penalty = 0.0
        if arrive_time < time_window_start or arrive_time > time_window_end:
            # 超时/早到惩罚
            time_penalty = self.time_window_penalty * abs(arrive_time - (time_window_start + time_window_end)/2)

        # 4. 检查载重约束
        load_penalty = 0.0
        if target_point["weight"] > self.remaining_load:
            # 超重惩罚
            load_penalty = 50.0
            reward = - (100.0 + time_penalty + load_penalty)
            self.done = True
            done = True
            obs = self._get_observation()
            return obs, reward, done, info

        # 5. 更新环境状态
        self.current_position = np.array([target_point["lon"], target_point["lat"]], dtype=np.float32)
        self.remaining_load -= target_point["weight"]
        del self.remaining_points[action]  # 移除已完成配送点

        # 6. 计算奖励
        reward = calculate_reward(
            distance_km=distance_km,
            time_penalty=time_penalty,
            load_penalty=load_penalty,
            remaining_points=len(self.remaining_points)
        )

        # 7. 判断回合结束条件
        if len(self.remaining_points) == 0:
            # 所有配送点完成，奖励加成
            reward += 200.0
            self.done = True
            done = True
        elif self.remaining_time <= 0:
            # 时间耗尽，惩罚
            reward -= 100.0
            self.done = True
            done = True

        # 构造新的观测值
        obs = self._get_observation()
        return obs, reward, done, info

    def _get_observation(self):
        """构造状态观测值（匹配observation_space格式）"""
        # 剩余配送点坐标展平（不足max_delivery_points则补0）
        remaining_coords = np.zeros(2 * self.max_delivery_points, dtype=np.float32)
        for i, p in enumerate(self.remaining_points):
            if i < self.max_delivery_points:
                remaining_coords[2*i] = p["lon"]
                remaining_coords[2*i+1] = p["lat"]
        # 拼接完整观测值
        obs = np.concatenate([
            self.current_position,
            remaining_coords,
            [self.remaining_load],
            [self.remaining_time],
            [self.traffic_factor]
        ], dtype=np.float32)
        return obs

    def _calculate_distance(self, lon1, lat1, lon2, lat2):
        """
        简化经纬度距离计算（单位：km）
        :param lon1/lat1: 起点经纬度
        :param lon2/lat2: 终点经纬度
        :return: distance_km 距离（公里）
        """
        # 地球半径（km）
        R = 6371.0
        # 转弧度
        lon1_rad = np.radians(lon1)
        lat1_rad = np.radians(lat1)
        lon2_rad = np.radians(lon2)
        lat2_rad = np.radians(lat2)
        # 经纬度差
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        # 哈弗辛公式
        a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = R * c
        return distance

    def render(self, mode='human'):
        """可视化环境状态（可选）"""
        if mode == 'human':
            print(f"当前位置：{self.current_position}")
            print(f"剩余配送点数量：{len(self.remaining_points)}")
            print(f"剩余载重：{self.remaining_load:.2f}kg")
            print(f"剩余时间：{self.remaining_time:.2f}分钟")
            print(f"路况系数：{self.traffic_factor:.2f}")
            print(f"回合结束：{self.done}")