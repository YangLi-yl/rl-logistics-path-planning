# 测试reward_calculator的简单脚本
import sys
import os

# 打印当前目录和sys.path
print(f"当前工作目录: {os.getcwd()}")
print(f"sys.path: {sys.path}")

# 检查reward_calculator.py文件是否存在
file_path = "utils/reward_calculator.py"
print(f"\n检查文件是否存在: {file_path}")
print(f"文件存在: {os.path.exists(file_path)}")

# 尝试直接读取文件内容
print("\n文件内容:")
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)

# 尝试动态导入
print("\n尝试动态导入:")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("utils.reward_calculator", "utils/reward_calculator.py")
    reward_module = importlib.util.module_from_spec(spec)
    sys.modules["utils.reward_calculator"] = reward_module
    spec.loader.exec_module(reward_module)
    
    print(f"模块属性: {dir(reward_module)}")
    if hasattr(reward_module, 'calculate_reward'):
        print("找到calculate_reward函数!")
        test_reward = reward_module.calculate_reward(1.5, 0.0, 0.0, 5)
        print(f"测试结果: {test_reward}")
    else:
        print("未找到calculate_reward函数!")
except Exception as e:
    print(f"导入错误: {e}")
    import traceback
    traceback.print_exc()
