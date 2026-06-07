# 简化的测试脚本
import sys
import os

# 直接导入需要的模块
import numpy as np

# 确保numpy版本正确
print(f"当前numpy版本: {np.__version__}")

# 直接测试reward_calculator
from utils.reward_calculator import calculate_reward

print("测试reward_calculator...")
test_reward = calculate_reward(distance_km=1.5, time_penalty=0.0, load_penalty=0.0, remaining_points=5)
print(f"奖励计算结果: {test_reward}")

# 测试环境
print("\n测试环境...")
try:
    from envs.campus_logistics_env import CampusLogisticsEnv
    
    # 创建环境
    env = CampusLogisticsEnv()
    print("环境创建成功!")
    
    # 测试reset
    print("测试reset()...")
    obs, info = env.reset()
    print(f"reset()成功，观测值形状: {obs.shape}")
    
    # 测试step
    print("测试step()...")
    obs, reward, terminated, truncated, info = env.step(0)
    print(f"step()成功!")
    print(f"奖励值: {reward}")
    print(f"是否终止: {terminated}")
    print(f"是否截断: {truncated}")
    print(f"信息: {info}")
    
    print("\n所有测试通过!")
    
except Exception as e:
    print(f"测试过程中发生错误: {e}")
    import traceback
    traceback.print_exc()
