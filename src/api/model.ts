import axios from 'axios'

// 创建API实例
const api = axios.create({
  baseURL: '/api', // 基础URL，会被vite.config.ts中的proxy代理到后端
  timeout: 30000, // 超时时间30秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config: any) => {
    // 可以在这里添加认证信息等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: any) => {
    return response.data
  },
  (error) => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// 类型定义

// 配送点类型
export interface DeliveryPoint {
  lon: number
  lat: number
  weight: number
  time_window: [number, number]
}

// 模型信息类型
export interface ModelInfo {
  key: string
  version: string
  type: string
  path: string
  is_loaded: boolean
  loaded_at: number
}

// 推理请求参数类型
export interface InferenceRequest {
  start_position: [number, number]
  delivery_points: DeliveryPoint[]
  algorithm?: 'model' | 'greedy'
  model_key?: string
}

// 推理响应结果类型
export interface InferenceResponse {
  success: boolean
  delivery_order: number[]
  total_distance_km: number
  total_distance_m: number
  estimated_time_min: number
  error?: string
  message?: string
}

// 训练任务状态类型
export interface TrainingTask {
  id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  model_name: string
  start_time: string
  end_time?: string
  progress: number
  metrics?: Record<string, number>
}

// API函数

/**
 * 调用模型推理接口进行路径规划
 * @param data 推理请求参数
 * @returns 推理结果
 */
export const inferPath = async (data: InferenceRequest): Promise<InferenceResponse> => {
  return await api.post('/inference', data)
}

/**
 * 调用路径规划接口
 * @param data 路径规划请求参数
 * @returns 路径规划结果
 */
export const inferRoute = async (data: {
  start_position: [number, number]
  delivery_points: Array<{
    lon: number
    lat: number
    weight: number
    time_window: [number, number]
  }>
  algorithm: string
  model_key?: string
}): Promise<{
  success: boolean
  path: [number, number][]
  total_distance: number
  total_time: number
}> => {
  // 将配送点转换为API需要的格式
  const formattedDeliveryPoints = data.delivery_points.map(point => ({
    lon: point.lon,
    lat: point.lat,
    weight: point.weight,
    time_window: point.time_window
  }))
  
  // 调用推理接口
  const response = await api.post('/inference', {
    start_position: data.start_position,
    delivery_points: formattedDeliveryPoints,
    algorithm: data.algorithm === 'greedy' ? 'greedy' : 'model',
    model_key: data.model_key
  })
  
  // 获取响应数据
  const result = response.data
  
  // 如果成功，构建路径数据
  if (result.success) {
    const path = [data.start_position]
    result.delivery_order.forEach((index: number) => {
      const point = data.delivery_points[index]
      path.push([point.lon, point.lat] as [number, number])
    })
    
    return {
      success: true,
      path,
      total_distance: result.total_distance_m,
      total_time: result.estimated_time_min
    }
  } else {
    throw new Error(result.error || '路径规划失败')
  }
}

/**
 * 获取训练任务列表
 * @returns 训练任务列表
 */
export const getTrainingTasks = async (): Promise<TrainingTask[]> => {
  return await api.get('/train/tasks')
}

/**
 * 开始新的训练任务
 * @param modelName 模型名称
 * @param config 训练配置
 * @returns 训练任务信息
 */
export const startTrainingTask = async (
  modelName: string,
  config: Record<string, any>
): Promise<TrainingTask> => {
  return await api.post('/train/start', { model_name: modelName, config })
}

/**
 * 停止训练任务
 * @param taskId 任务ID
 * @returns 操作结果
 */
export const stopTrainingTask = async (taskId: string): Promise<{ success: boolean }> => {
  return await api.put(`/train/stop/${taskId}`)
}

/**
 * 获取环境配置信息
 * @returns 环境配置
 */
export const getEnvironmentConfig = async (): Promise<Record<string, any>> => {
  return await api.get('/envs/config')
}

/**
 * 更新环境配置信息
 * @param config 新的配置
 * @returns 操作结果
 */
export const updateEnvironmentConfig = async (
  config: Record<string, any>
): Promise<{ success: boolean }> => {
  return await api.put('/envs/config', config)
}

/**
 * 获取可用模型列表
 * @returns 模型列表
 */
export const getAvailableModels = async (): Promise<ModelInfo[]> => {
  return await api.get('/inference/models')
}

/**
 * 重新加载模型
 * @returns 操作结果
 */
export const reloadModels = async (): Promise<{ success: boolean; message: string }> => {
  return await api.post('/inference/models/reload')
}

export default {
  inferPath,
  getTrainingTasks,
  startTrainingTask,
  stopTrainingTask,
  getEnvironmentConfig,
  updateEnvironmentConfig,
  getAvailableModels,
  reloadModels
}