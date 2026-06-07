import sys
import os
import warnings

# 忽略Gym的弃用警告
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gym
import torch
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import CheckpointCallback

# 注册自定义环境（需先导入）
import envs

def train_ppo_model():
    """训练PPO模型"""
    print("正在初始化训练环境...")
    
    # 1. 创建向量环境（提升训练效率）
    try:
        env = make_vec_env(
            "CampusLogistics-v0",
            n_envs=4,  # 并行环境数量
            seed=42
        )
        print("✓ 成功创建向量环境")
    except Exception as e:
        print(f"✗ 创建向量环境失败: {e}")
        return

    # 2. 初始化PPO模型
    try:
        model = PPO(
            policy="MlpPolicy",  # 多层感知机策略（适配连续状态空间）
            env=env,
            learning_rate=3e-4,  # 学习率
            n_steps=2048,        # 每批次步数
            batch_size=64,       # 批次大小
            gamma=0.99,          # 折扣因子
            gae_lambda=0.95,     # GAE系数
            ent_coef=0.01,       # 熵系数（鼓励探索）
            verbose=1,           # 日志输出级别
            device="auto"        # 自动选择CPU/GPU
        )
        print("✓ 成功初始化PPO模型")
    except Exception as e:
        print(f"✗ 初始化PPO模型失败: {e}")
        return

    # 3. 确保检查点目录存在
    checkpoint_dir = "./models/checkpoints/"
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    # 4. 训练回调（保存检查点）
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,  # 每10000步保存一次
        save_path=checkpoint_dir,
        name_prefix="campus_ppo"
    )

    # 5. 开始训练
    print("\n开始训练PPO模型...")
    print(f"总训练步数: 1,000,000")
    print(f"并行环境数: 4")
    print(f"检查点保存频率: 10,000步")
    print(f"检查点保存路径: {checkpoint_dir}")
    
    try:
        model.learn(
            total_timesteps=1000000,  # 总训练步数
            callback=checkpoint_callback,
            progress_bar=False  # 不显示进度条，避免依赖问题
        )
    except KeyboardInterrupt:
        print("\n训练被用户中断")
    except Exception as e:
        print(f"\n✗ 训练过程中发生错误: {e}")
        return

    # 6. 保存最终模型
    try:
        model_dir = "./models/"
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "campus_logistics_ppo")
        model.save(model_path)
        print(f"\n✓ 模型训练完成，已保存至 {model_path}")
    except Exception as e:
        print(f"\n✗ 保存模型失败: {e}")
        return

    # 7. 验证模型（随机测试5轮）
    print("\n开始验证模型...")
    try:
        env = gym.make("CampusLogistics-v0")
        for episode in range(5):
            obs = env.reset()
            done = False
            total_reward = 0
            step_count = 0
            
            while not done:
                action, _states = model.predict(obs, deterministic=True)
                obs, reward, done, info = env.step(action)
                total_reward += reward
                step_count += 1
                
                if step_count > 100:  # 防止无限循环
                    print("⚠️  步数超过100，强制结束回合")
                    break
            
            print(f"回合 {episode+1}: 总奖励 = {total_reward:.2f}, 步数 = {step_count}")
            
        env.close()
        print("✓ 模型验证完成")
    except Exception as e:
        print(f"✗ 模型验证失败: {e}")
        return

    print("\n🎉 训练脚本执行完成！")

if __name__ == "__main__":
    # 检查numpy版本
    if np.__version__ != "1.24.3":
        print(f"⚠️  当前numpy版本为 {np.__version__}，推荐使用 1.24.3 以确保兼容性")
        print("可以使用以下命令安装正确版本: pip install numpy==1.24.3")
    
    # 设置随机种子确保可复现
    torch.manual_seed(42)
    np.random.seed(42)
    
    # 运行训练函数
    train_ppo_model()
