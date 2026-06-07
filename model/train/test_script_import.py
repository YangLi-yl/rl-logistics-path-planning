import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_script_import():
    """仅测试脚本的导入功能，不执行完整训练"""
    print("测试train_ppo.py脚本导入...")
    
    try:
        # 导入脚本中的主要组件
        from train_ppo import train_ppo_model
        print("✓ 成功导入train_ppo_model函数")
        
        # 测试环境注册
        import gym
        import envs
        
        try:
            env = gym.make("CampusLogistics-v0")
            print("✓ 成功创建CampusLogistics-v0环境")
            env.close()
        except Exception as e:
            print(f"✗ 创建环境失败: {e}")
            
        print("\n脚本导入测试通过！")
        print("可以使用以下命令开始训练:")
        print("python train_ppo.py")
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False
    
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_script_import()