import axios from 'axios'

// 创建高德地图API实例
const amapApi = axios.create({
  baseURL: 'https://restapi.amap.com/v3', // 高德地图API基础URL
  timeout: 10000, // 超时时间10秒
  params: {
    key: import.meta.env.VITE_AMAP_KEY || '67c053cf8b991cf9b4462133824668cf' // 使用配置的API密钥或默认值
  }
})

// 响应拦截器
amapApi.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('高德地图API请求错误:', error)
    return Promise.reject(error)
  }
)

// 地理编码类型定义
export interface GeocodeResult {
  status: string
  info: string
  geocodes: Array<{
    formatted_address: string
    country: string
    province: string
    city: string
    district: string
    street: string
    number: string
    location: string // 坐标，格式为"lng,lat"
    level: string // 精确程度
    adcode: string
    citycode: string
  }>
}

// 地址搜索建议类型定义
export interface SuggestionResult {
  status: string
  info: string
  tips: Array<{
    id: string
    name: string
    district: string
    address: string
    location: string
    category: string
    city: string
    province: string
  }>
}

/**
 * 地址转坐标（地理编码）
 * @param address 地址字符串
 * @param city 城市名称，可选，用于缩小搜索范围
 * @returns 地理编码结果
 */
export const geocode = async (address: string, city?: string): Promise<GeocodeResult> => {
  const params: any = {
    address,
    output: 'JSON'
  }
  
  if (city) {
    params.city = city
  }
  
  return amapApi.get('/geocode/geo', { params })
}

/**
 * 坐标转地址（逆地理编码）
 * @param location 坐标，格式为"lng,lat"
 * @returns 逆地理编码结果
 */
export const reverseGeocode = async (location: string): Promise<GeocodeResult> => {
  return amapApi.get('/geocode/regeo', {
    params: {
      location,
      output: 'JSON'
    }
  })
}

/**
 * 地址搜索建议
 * @param keyword 搜索关键词
 * @param city 城市名称，可选，用于缩小搜索范围
 * @returns 搜索建议结果
 */
export const getAddressSuggestions = async (keyword: string, city?: string): Promise<SuggestionResult> => {
  const params: any = {
    keywords: keyword,
    output: 'JSON'
  }
  
  if (city) {
    params.city = city
  }
  
  return amapApi.get('/assistant/inputtips', { params })
}
