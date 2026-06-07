import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_train_imports():
    """测试训练脚本的导入是否正常"""
    print("测试训练脚本的导入...")
    
    try:
        import gym
        print("✓ 成功导入 gym")
    except ImportError as e:
        print(f"✗ 导入 gym 失败: {e}")
        return False
    
    try:
        import torch
        print("✓ 成功导入 torch")
    except ImportError as e:
        print(f"✗ 导入 torch 失败: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ 成功导入 numpy")
    except ImportError as e:
        print(f"✗ 导入 numpy 失败: {e}")
        return False
    
    try:
        from stable_baselines3 import PPO
        print("✓ 成功导入 stable_baselines3.PPO")
    except ImportError as e:
        print(f"✗ 导入 stable_baselines3.PPO 失败: {e}")
        return False
    
    try:
        from stable_baselines3.common.env_util import make_vec_env
        print("✓ 成功导入 stable_baselines3.common.env_util.make_vec_env")
    except ImportError as e:
        print(f"✗ 导入 make_vec_env 失败: {e}")
        return False
    
    try:
        from stable_baselines3.common.callbacks import CheckpointCallback
        print("✓ 成功导入 stable_baselines3.common.callbacks.CheckpointCallback")
    except ImportError as e:
        print(f"✗ 导入 CheckpointCallback 失败: {e}")
        return False
    
    try:
        import envs
        print("✓ 成功导入 envs 模块")
    except ImportError as e:
        print(f"✗ 导入 envs 模块失败: {e}")
        return False
    
    try:
        # 测试环境注册是否成功
        env = gym.make("CampusLogistics-v0")
        print("✓ 成功创建 CampusLogistics-v0 环境")
        
        # 测试环境的基本功能
        obs = env.reset()
        print(f"✓ 成功调用 reset() 方法，观察空间形状: {obs.shape}")
        
        action = 0
        obs, reward, done, info = env.step(action)
        print(f"✓ 成功调用 step() 方法，奖励值: {reward}")
        
        env.close()
        print("✓ 成功关闭环境")
        
    except Exception as e:
        print(f"✗ 测试环境功能失败: {e}")
        return False
    
    print("\n所有导入和环境测试均成功！")
    return True

if __name__ == "__main__":
    test_train_imports()