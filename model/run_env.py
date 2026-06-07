# 运行campus_logistics_env.py来测试reset()和step()方法
import sys
import os

def main():
    print("===== 校园物流环境测试 =====")
    
    # 添加项目路径
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from envs.campus_logistics_env import CampusLogisticsEnv
        
        # 创建环境
        env = CampusLogisticsEnv()
        print("✓ 环境创建成功")
        
        # 测试reset()方法
        print("\n1. 测试reset()方法:")
        obs, info = env.reset()
        print(f"✓ reset()调用成功")
        print(f"   - 观测值形状: {obs.shape}")
        print(f"   - 初始位置: {obs[:2]}")
        print(f"   - 初始载重: {obs[-3]}")
        print(f"   - 初始时间: {obs[-2]}")
        print(f"   - 初始路况: {obs[-1]}")
        
        # 测试step()方法
        print("\n2. 测试step()方法:")
        obs, reward, terminated, truncated, info = env.step(0)
        print(f"✓ step()调用成功")
        print(f"   - 奖励值: {reward}")
        print(f"   - 终止状态: {terminated}")
        print(f"   - 截断状态: {truncated}")
        print(f"   - 动作有效性: {info['valid_action']}")
        
        print("\n===== 所有测试通过！环境可以正常使用 =====")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
