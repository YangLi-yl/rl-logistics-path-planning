import gym
import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入自定义环境
from envs.campus_logistics_env import CampusLogisticsEnv

def test_environment():
    """测试校园物流环境"""
    print("创建校园物流环境...")
    env = CampusLogisticsEnv(config={'max_points': 5})
    
    print("\n测试reset方法...")
    obs = env.reset()
    print(f"初始观察空间形状: {obs.shape}")
    print(f"初始观察空间内容: {obs[:10]}...")
    
    print("\n测试render方法...")
    env.render()
    
    print("\n测试step方法...")
    for i in range(3):
        print(f"\n步骤 {i+1}:")
        # 随机选择一个动作
        action = 0  # 选择第一个剩余配送点
        obs, reward, done, info = env.step(action)
        print(f"动作: {action}")
        print(f"奖励: {reward}")
        print(f"完成状态: {done}")
        print(f"信息: {info}")
        print(f"观察空间内容: {obs[:10]}...")
        
        if done:
            print("环境已完成，重置环境...")
            obs = env.reset()
            print(f"重置后观察空间内容: {obs[:10]}...")
            break
    
    print("\n测试结束！")

if __name__ == "__main__":
    test_environment()