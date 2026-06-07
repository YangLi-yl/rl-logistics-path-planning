/**
 * 系统配置文件
 */

// API相关配置
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || '/api',
  TIMEOUT: 30000,
  RETRY_TIMES: 3
}

// 地图相关配置
export const MAP_CONFIG = {
  DEFAULT_CENTER: [120.3945, 36.0665], // 默认中心坐标（中国石油大学(华东)校园中心 - 准确GCJ-02坐标）
  DEFAULT_ZOOM: 15,
  MIN_ZOOM: 13,
  MAX_ZOOM: 18
}

// 配送相关配置
export const DELIVERY_CONFIG = {
  MAX_DELIVERY_POINTS: 20,
  DEFAULT_VEHICLE_CAPACITY: 20, // 默认车辆载重（kg）
  DEFAULT_SPEED: 5, // 默认行驶速度（km/h）
  TIME_WINDOW_PENALTY: 10
}

// 训练相关配置
export const TRAINING_CONFIG = {
  DEFAULT_LEARNING_RATE: 3e-4,
  DEFAULT_TOTAL_TIMESTEPS: 1000000,
  DEFAULT_BATCH_SIZE: 64,
  DEFAULT_GAMMA: 0.99
}

// 界面相关配置
export const UI_CONFIG = {
  THEME_COLOR: '#42b883',
  SIDEBAR_WIDTH: 240,
  HEADER_HEIGHT: 64
}

