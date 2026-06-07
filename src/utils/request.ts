import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { API_CONFIG } from './config'

/**
 * 请求响应类型
 */
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  error?: string
}

/**
 * 创建带有重试机制的axios实例
 * @param config 自定义配置
 * @returns axios实例
 */
export const createApiClient = (config?: AxiosRequestConfig): AxiosInstance => {
  const api = axios.create({
    baseURL: API_CONFIG.BASE_URL,
    timeout: API_CONFIG.TIMEOUT,
    ...config
  })

  // 请求拦截器
  api.interceptors.request.use(
    (config: any) => {
      // 可以在这里添加认证信息
      return config
    },
    (error: any) => {
      return Promise.reject(error)
    }
  )

  // 响应拦截器
  api.interceptors.response.use(
    (response: AxiosResponse<ApiResponse>) => {
      return response
    },
    (error: any) => {
      return Promise.reject(error)
    }
  )

  return api
}

/**
 * 带有重试机制的请求函数
 * @param apiClient axios实例
 * @param method 请求方法
 * @param url 请求URL
 * @param data 请求数据
 * @param config 请求配置
 * @param retryTimes 剩余重试次数
 * @returns 请求结果
 */
export const requestWithRetry = async <T = any>(
  apiClient: AxiosInstance,
  method: 'get' | 'post' | 'put' | 'delete',
  url: string,
  data?: any,
  config?: AxiosRequestConfig,
  retryTimes: number = API_CONFIG.RETRY_TIMES
): Promise<AxiosResponse<ApiResponse<T>>> => {
  try {
    const response = await apiClient.request<ApiResponse<T>>({
      method,
      url,
      data,
      ...config
    })

    return response
  } catch (error) {
    if (retryTimes > 0) {
      console.log(`请求失败，剩余重试次数: ${retryTimes}`)
      // 指数退避策略
      await new Promise((resolve) => setTimeout(resolve, Math.pow(2, 3 - retryTimes) * 1000))
      return requestWithRetry(apiClient, method, url, data, config, retryTimes - 1)
    }

    // 处理错误
    const errorResponse: AxiosResponse<ApiResponse<T>> = {
      data: {
        success: false,
        data: null as any,
        error: error instanceof Error ? error.message : 'Unknown error',
        message: '请求失败，请稍后重试'
      },
      status: 500,
      statusText: 'Internal Server Error',
      headers: {},
      config: {
        method,
        url,
        data,
        ...config
      }
    } as AxiosResponse<ApiResponse<T>>

    return errorResponse
  }
}

// 创建默认的API客户端
export const apiClient = createApiClient()