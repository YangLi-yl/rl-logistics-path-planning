import numpy as np

def calculate_reward(distance_km, time_penalty, load_penalty, remaining_points):
    """
    计算单步奖励值
    :param distance_km: 本次行驶距离（km）
    :param time_penalty: 时间窗违规惩罚值
    :param load_penalty: 载重违规惩罚值
    :param remaining_points: 剩余配送点数量
    :return: reward 奖励值
    """
    # 基础奖励：距离越短奖励越高（负向惩罚）
    distance_reward = -10 * distance_km  # 距离惩罚系数10
    # 完成配送奖励：剩余点越少奖励越高
    completion_reward = 5 * (20 - remaining_points)  # 最大配送点20个
    # 总奖励 = 距离奖励 + 完成奖励 - 时间惩罚 - 载重惩罚
    total_reward = distance_reward + completion_reward - time_penalty - load_penalty
    # 奖励值裁剪（避免极端值）
    total_reward = np.clip(total_reward, -200, 200)
    return total_reward
