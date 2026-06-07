#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
奖励函数计算器
根据用户需求实现复合奖励函数：
总奖励 = -行驶距离×距离系数 + 时间窗奖励（按时+50，轻微超时-50，严重超时-100）+ 负载平衡奖励（±20）+ 完成率奖励（完成所有点+200）
"""

def calculate_reward(distance_km: float, time_penalty: float, load_penalty: float, remaining_points: int) -> float:
    """
    计算配送任务的奖励值
    
    参数:
    distance_km: 行驶距离（公里）
    time_penalty: 时间惩罚（分钟）
    load_penalty: 负载惩罚
    remaining_points: 剩余配送点数量
    
    返回:
    奖励值
    """
    # 1. 行驶距离惩罚：-距离×距离系数
    distance_coefficient = 10.0  # 距离系数
    distance_reward = -distance_km * distance_coefficient
    
    # 2. 时间窗奖励：按时+50，轻微超时-50，严重超时-100
    time_window_reward = 50.0  # 默认按时奖励
    if time_penalty > 0:
        if time_penalty <= 30:  # 轻微超时（≤30分钟）
            time_window_reward = -50.0
        else:  # 严重超时（>30分钟）
            time_window_reward = -100.0
    
    # 3. 负载平衡奖励：±20
    # 根据剩余载重情况给予奖励或惩罚
    # 这里简化实现，根据剩余配送点数量调整
    load_balance_reward = 20.0 if remaining_points < 3 else -20.0
    
    # 4. 完成率奖励：完成所有点+200
    completion_reward = 200.0 if remaining_points == 0 else 0.0
    
    # 计算总奖励
    total_reward = distance_reward + time_window_reward + load_balance_reward + completion_reward
    
    return total_reward


if __name__ == "__main__":
    # 测试奖励函数
    test_cases = [
        # (distance_km, time_penalty, load_penalty, remaining_points)
        (1.5, 0.0, 0.0, 5),   # 按时，剩余5个点
        (2.0, 15.0, 0.0, 3),  # 轻微超时，剩余3个点
        (3.0, 45.0, 0.0, 1),  # 严重超时，剩余1个点
        (0.5, 0.0, 0.0, 0),   # 完成所有点
    ]
    
    for i, (distance, time_pen, load_pen, remaining) in enumerate(test_cases):
        reward = calculate_reward(distance, time_pen, load_pen, remaining)
        print(f"测试用例 {i+1}: 距离={distance}km, 时间惩罚={time_pen}min, 负载惩罚={load_pen}, 剩余点={remaining}")
        print(f"奖励: {reward}")
        print()
