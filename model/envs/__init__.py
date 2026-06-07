from gym.envs.registration import register
from .campus_logistics_env import CampusLogisticsEnv

# 注册自定义环境
register(
    id="CampusLogistics-v0",
    entry_point="envs.campus_logistics_env:CampusLogisticsEnv",
    kwargs={}
)
