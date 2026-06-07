# 直接运行环境测试脚本
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs.campus_logistics_env import CampusLogisticsEnv

if __name__ == "__main__":
    print("=== 直接测试CampusLogisticsEnv环境 ===")
    
    # 创建环境实例
    env = CampusLogisticsEnv()
    print("✓ 环境创建成功")
    
    # 测试reset()方法
    print("\n1. 测试reset()方法...")
    obs, info = env.reset()
    print("✓ reset()方法执行成功")
    print(f"   观测值形状: {obs.shape}")
    print(f"   初始信息: {info}")
    
    # 测试step()方法
    print("\n2. 测试step()方法...")
    obs, reward, terminated, truncated, info = env.step(0)
    print("✓ step()方法执行成功")
    print(f"   奖励值: {reward}")
    print(f"   是否终止: {terminated}")
    print(f"   是否截断: {truncated}")
    print(f"   信息: {info}")
    
    # 再测试一次step()方法
    print("\n3. 再次测试step()方法...")
    obs, reward, terminated, truncated, info = env.step(0)
    print("✓ step()方法再次执行成功")
    print(f"   奖励值: {reward}")
    print(f"   是否终止: {terminated}")
    print(f"   是否截断: {truncated}")
    print(f"   信息: {info}")
    
    print("\n🎉 所有测试通过！reset()和step()方法可正常执行，无报错")
