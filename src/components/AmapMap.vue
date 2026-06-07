<template>
  <div class="amap-container">
    <div ref="mapContainer" class="map-container"></div>
    <!-- 地图加载错误提示 -->
    <div v-if="mapError" class="map-error-overlay">
      <div class="map-error-content">
        <div class="map-error-icon">⚠️</div>
        <h3>地图加载失败</h3>
        <p>{{ mapErrorMessage }}</p>
        <div class="map-error-actions">
          <button @click="retryLoadMap" :disabled="isRetrying" class="retry-btn">
            {{ isRetrying ? '重试中...' : '重试' }}
          </button>
          <button @click="toggleOfflineMode" class="offline-btn">
            {{ isOfflineMode ? '退出离线模式' : '使用离线模式' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'

// 配送点数据结构
interface DeliveryPoint {
  coordinates: [number, number]
  weight: number
  weightUnit: 'kg' | 'ton'
}

// 组件属性定义
interface Props {
  // 地图中心点坐标
  center?: [number, number]
  // 缩放级别
  zoom?: number
  // 起点坐标
  startPoint?: [number, number] | null
  // 配送点数据数组
  deliveryPoints?: DeliveryPoint[]
  // 配送路径数组
  path?: Array<[number, number]>
  // 是否显示交通图层
  showTrafficLayer?: boolean
  // 是否启用路径动画
  animatePath?: boolean
  // 是否显示校区边界
  showCampusBoundary?: boolean
  // 校区边界半径（米）
  campusRadius?: number
  // 校区中心点
  campusCenter?: [number, number]
}

// 组件事件定义
interface Emits {
  // 配送点点击事件
  (e: 'delivery-point-click', index: number, coordinate: [number, number]): void
  // 地图点击事件
  (e: 'map-click', coordinate: [number, number]): void
  // 地图缩放变化事件
  (e: 'zoom-changed', zoom: number): void
  // 起点位置变化事件
  (e: 'start-point-changed', coordinate: [number, number]): void
  // 配送点位置变化事件
  (e: 'delivery-point-changed', index: number, coordinate: [number, number]): void
  // 位置变化事件
  (e: 'location-changed', coordinate: [number, number], data?: any): void
  // 定位错误事件
  (e: 'location-error', error: any): void
}

// 组件属性
const props = withDefaults(defineProps<Props>(), {
  center: () => [120.394887, 36.066204], // 中国石油大学（华东）坐标
  zoom: 16,
  startPoint: null,
  deliveryPoints: () => [],
  path: () => [],
  showTrafficLayer: false,
  animatePath: true,
  showCampusBoundary: true,
  campusRadius: 1000, // 默认1公里
  campusCenter: () => [120.3945, 36.0665] // 中国石油大学华东校区中心坐标
})

// 组件事件
const emit = defineEmits<Emits>()

// 交通图层实例
let trafficLayer: any = null

// 地图容器引用
const mapContainer = ref<HTMLElement | null>(null)
// 地图实例
let mapInstance: any = null
// 标记点实例数组
let markers: any[] = []
// 路径实例
let polyline: any = null
// 校区边界实例
let campusBoundary: any = null

// 错误状态管理
const mapError = ref(false)
const mapErrorMessage = ref('')
const isRetrying = ref(false)
const retryAttempts = ref(0)
const MAX_RETRY_ATTEMPTS = 3

// 离线模式
const isOfflineMode = ref(false)
const offlineMapData = ref({
  center: [120.394887, 36.066204],
  zoom: 16,
  bounds: [[120.38, 36.05], [120.41, 36.08]]
})

// 网络监听器清理函数
const networkListenerCleanup = ref<(() => void) | null>(null)

// 加载地图
const loadMap = async () => {
  if (!mapContainer.value) return
  
  // 重置错误状态
  mapError.value = false
  mapErrorMessage.value = ''
  
  try {
    // 如果处于离线模式，加载离线地图
    if (isOfflineMode.value) {
      loadOfflineMap()
      return
    }
    
    // 获取当前密钥
    const currentKey = import.meta.env.VITE_AMAP_KEY || '011b30e3bc887023f886c08cc71a319c'
    
    // 在开发环境中验证密钥有效性
    if (import.meta.env.DEV) {
      const isValid = await validateApiKey(currentKey)
      if (!isValid) {
        console.warn('[AMAP WARNING] API密钥可能无效，将自动切换到离线模式')
        toggleOfflineMode()
        return
      }
    }
    
    // 加载高德地图API，优先从环境变量获取密钥
    await AMapLoader.load({
      key: currentKey,
      version: '2.0',
      plugins: [
        'AMap.Scale', 'AMap.ToolBar', 'AMap.Marker', 'AMap.Polyline',
        'AMap.Traffic', 'AMap.InfoWindow', 'AMap.MouseTool',
        'AMap.Geolocation', 'AMap.LocateControl'
      ]
    })

    // 创建地图实例
    mapInstance = new (window as any).AMap.Map(mapContainer.value, {
      center: props.center,
      zoom: props.zoom,
      viewMode: '2D',
      resizeEnable: true,
      // 设置鼠标样式
      cursor: 'pointer'
    })

    // 添加地图控件
    // 比例尺控件
    mapInstance.addControl(new (window as any).AMap.Scale({
      position: 'LB' // 左下角
    }))
    // 工具栏控件
    mapInstance.addControl(new (window as any).AMap.ToolBar({
      position: 'RT', // 右上角
      offset: [10, 10],
      ruler: true, // 显示标尺
      autoPosition: true // 自动定位按钮
    }))
    
    // 添加定位控件（优雅降级处理）
    try {
      if (typeof (window as any).AMap.LocateControl === 'function') {
        mapInstance.addControl(new (window as any).AMap.LocateControl({
          position: 'RT', // 右上角
          offset: [10, 50],
          showButton: true, // 显示定位按钮
          showMarker: true, // 显示定位点标记
          showCircle: true, // 显示定位精度圈
          locateOnce: true, // 只定位一次
          timeout: 8000, // 定位超时时间
          zoomToAccuracy: true, // 定位成功后自动缩放至合适级别
          positionFixed: true // 定位控件固定在地图上
        }))
        console.info('[AMAP INFO] 定位控件加载成功')
      } else {
        console.warn('[AMAP WARNING] LocateControl 插件未加载成功，将禁用定位控件功能')
      }
    } catch (error) {
      console.error('[AMAP ERROR] 定位控件初始化失败:', error)
    }
    
    // 检查并请求定位权限
    const checkLocationPermission = async () => {
      try {
        const permissionStatus = await navigator.permissions.query({ name: 'geolocation' })
        console.log('[AMAP PERMISSION] 当前定位权限状态:', permissionStatus.state)
        
        // 监听权限状态变化
        permissionStatus.onchange = () => {
          console.log('[AMAP PERMISSION] 定位权限状态变化:', permissionStatus.state)
        }
        
        return permissionStatus.state
      } catch (error) {
        console.error('[AMAP PERMISSION] 权限检查失败:', error)
        return 'denied'
      }
    }
    
    // 检查网络连接状态
    const checkNetworkStatus = () => {
      const isOnline = navigator.onLine
      console.log('[AMAP NETWORK] 当前网络状态:', isOnline ? '在线' : '离线')
      return isOnline
    }
    
    // 监听网络状态变化
    const setupNetworkListener = () => {
      const handleNetworkChange = () => {
        const isOnline = navigator.onLine
        console.log('[AMAP NETWORK] 网络状态变化:', isOnline ? '在线' : '离线')
        
        if (isOnline) {
          // 网络恢复时，重新检查定位服务
          console.info('[AMAP INFO] 网络恢复，重新尝试定位')
        } else {
          console.warn('[AMAP WARNING] 网络断开，定位精度可能降低')
        }
      }
      
      window.addEventListener('online', handleNetworkChange)
      window.addEventListener('offline', handleNetworkChange)
      
      // 返回清理函数
      return () => {
        window.removeEventListener('online', handleNetworkChange)
        window.removeEventListener('offline', handleNetworkChange)
      }
    }
    
    // 配置高精度定位服务（优雅降级处理）
    let geolocation: any = null
    try {
      if (typeof (window as any).AMap.Geolocation === 'function') {
        geolocation = new (window as any).AMap.Geolocation({
          enableHighAccuracy: true, // 开启高精度定位
          timeout: 8000, // 定位超时时间
          maximumAge: 30000, // 缓存位置的最大时间
          convert: true, // 自动转换坐标系
          showButton: false, // 不单独显示定位按钮（使用LocateControl）
          zoomToAccuracy: true, // 定位成功后自动缩放
          panToLocation: true, // 定位成功后将定位点移动到地图中心
          needAddress: true, // 获取地址信息
          extensions: 'all' // 获取所有定位信息
        })
        
        // 检查定位权限
        const permissionState = await checkLocationPermission()
        if (permissionState === 'denied') {
          console.warn('[AMAP WARNING] 定位权限被拒绝，定位功能可能无法正常使用')
        } else if (permissionState === 'prompt') {
          console.info('[AMAP INFO] 定位权限需要用户确认')
        }
        
        console.info('[AMAP INFO] 定位服务加载成功')
      } else {
        console.warn('[AMAP WARNING] Geolocation 插件未加载成功，将禁用定位服务功能')
      }
    } catch (error) {
      console.error('[AMAP ERROR] 定位服务初始化失败:', error)
    }
    
    // 检查网络连接状态
    const isOnline = checkNetworkStatus()
    
    // 设置网络状态监听器
    networkListenerCleanup.value = setupNetworkListener()
    
    // 添加定位事件监听和控件（仅当定位服务初始化成功时）
    if (geolocation) {
      geolocation.on('complete', (data: any) => {
        console.log('[AMAP GEOLOCATION] 定位成功:', data)
        const location: [number, number] = [data.position.getLng(), data.position.getLat()]
        // 发出位置变更事件
        emit('location-changed', location, data)
      })
      
      geolocation.on('error', (data: any) => {
        console.error('[AMAP GEOLOCATION] 定位失败:', data)
        // 发出定位错误事件
        emit('location-error', data)
      })
      
      // 添加到地图实例
      mapInstance.addControl(geolocation)
    }

    // 地图点击事件
    mapInstance.on('click', (e: any) => {
      emit('map-click', [e.lnglat.getLng(), e.lnglat.getLat()])
    })

    // 地图缩放变化事件
    mapInstance.on('zoomend', () => {
      emit('zoom-changed', mapInstance.getZoom())
    })

    // 监听地图错误事件
    mapInstance.on('error', handleMapError)

    // 更新地图内容
    updateMapContent()
    // 更新交通图层
    updateTrafficLayer()
    
    // 重置重试计数
    retryAttempts.value = 0
  } catch (error: any) {
    // 输出规范的错误日志
    console.error('[AMAP ERROR] 地图加载失败:', {
      errorType: error.code || error.name || 'UnknownError',
      message: error.message || '地图加载过程中发生未知错误',
      stack: error.stack,
      timestamp: new Date().toISOString()
    })
    
    // 处理错误
    handleMapError(error)
  }
}

// 验证API密钥有效性
const validateApiKey = async (key: string): Promise<boolean> => {
  try {
    // 使用高德地图的地理编码API进行简单验证
    const response = await fetch(
      `https://restapi.amap.com/v3/geocode/geo?key=${key}&address=北京市`
    )
    
    const data = await response.json()
    
    // 检查响应状态
    return data.status === '1' || data.info !== 'INVALID_USER_KEY'
  } catch (error) {
    console.error('[AMAP ERROR] 密钥验证失败:', error)
    return false
  }
}

// 处理地图错误
const handleMapError = (error: any) => {
  mapError.value = true
  
  // 根据错误类型设置不同的错误消息和处理方式
  if (error.code === 'INVALID_USER_KEY' || error.message?.includes('INVALID_USER_KEY')) {
    mapErrorMessage.value = '地图API密钥无效，已切换到离线模式\n\n请配置有效的API密钥以使用完整功能：\n1. 复制.env.example为.env\n2. 填入有效的高德地图API密钥\n3. 重新启动应用'
    
    // 自动切换到离线模式
    toggleOfflineMode()
    
    // 记录详细错误日志
    console.error('[AMAP ERROR] API密钥验证失败:', {
      code: 'INVALID_USER_KEY',
      message: '高德地图API密钥无效',
      currentKey: import.meta.env.VITE_AMAP_KEY || '默认密钥',
      timestamp: new Date().toISOString()
    })
  } else if (error.message?.includes('NETWORK_ERROR') || error.message?.includes('网络')) {
    mapErrorMessage.value = '网络连接失败，请检查网络设置'
  } else if (error.message?.includes('PLUGIN_LOAD_FAILED')) {
    mapErrorMessage.value = '地图插件加载失败，请稍后重试'
  } else {
    mapErrorMessage.value = error.message || '地图加载失败，请稍后重试'
    console.error('[AMAP ERROR] 未知错误:', error)
  }
}

// 重试加载地图
const retryLoadMap = async () => {
  if (isRetrying.value) return
  
  isRetrying.value = true
  retryAttempts.value++
  
  try {
    // 指数退避策略
    const delay = Math.pow(2, retryAttempts.value) * 1000
    await new Promise(resolve => setTimeout(resolve, delay))
    
    await loadMap()
  } catch (error) {
    console.error('地图重试加载失败:', error)
    
    if (retryAttempts.value >= MAX_RETRY_ATTEMPTS) {
      mapErrorMessage.value = '多次尝试后仍无法加载地图，建议尝试离线模式'
    }
  } finally {
    isRetrying.value = false
  }
}

// 切换离线模式
const toggleOfflineMode = () => {
  isOfflineMode.value = !isOfflineMode.value
  mapError.value = false
  
  // 清除现有地图实例
  if (mapInstance) {
    mapInstance.destroy()
    mapInstance = null
  }
  
  // 重新加载地图
  loadMap()
}

// 加载离线地图
const loadOfflineMap = () => {
  if (!mapContainer.value) return
  
  // 创建一个简单的离线地图模拟
  const container = mapContainer.value
  container.innerHTML = ''
  
  // 添加离线地图背景
  const offlineBg = document.createElement('div')
  offlineBg.style.position = 'absolute'
  offlineBg.style.width = '100%'
  offlineBg.style.height = '100%'
  offlineBg.style.backgroundColor = '#f5f5f5'
  offlineBg.style.border = '1px solid #ddd'
  offlineBg.style.display = 'flex'
  offlineBg.style.alignItems = 'center'
  offlineBg.style.justifyContent = 'center'
  container.appendChild(offlineBg)
  
  // 添加离线地图提示
  const offlineHint = document.createElement('div')
  offlineHint.style.position = 'absolute'
  offlineHint.style.top = '20px'
  offlineHint.style.left = '20px'
  offlineHint.style.padding = '10px'
  offlineHint.style.backgroundColor = 'rgba(0, 0, 0, 0.7)'
  offlineHint.style.color = 'white'
  offlineHint.style.borderRadius = '4px'
  offlineHint.style.fontSize = '14px'
  offlineHint.textContent = '当前处于离线模式，仅显示基本标记点'
  container.appendChild(offlineHint)
  
  // 在离线模式下添加标记点
  updateMapContent()
}

// 更新地图内容
const updateMapContent = () => {
  // 清除旧的标记点
  clearMarkers()
  
  // 清除旧的路径
  if (polyline) {
    mapInstance.remove(polyline)
    polyline = null
  }
  
  // 清除旧的校区边界
  if (campusBoundary) {
    mapInstance.remove(campusBoundary)
    campusBoundary = null
  }
  
  // 如果处于离线模式且没有地图实例，使用离线模式的标记渲染
  if (isOfflineMode.value && !mapInstance) {
    renderOfflineMarkers()
    return
  }
  
  if (!mapInstance) return

  // 添加起点标记
  if (props.startPoint) {
    // 使用高德地图内置的起点标记样式
    const marker = new (window as any).AMap.Marker({
      position: props.startPoint,
      map: mapInstance,
      icon: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png',
      title: '起点',
      zIndex: 100, // 设置较高的层级，确保起点在最上层
      label: {
        content: '起点',
        direction: 'bottom', // 标签显示在标记下方
        offset: new (window as any).AMap.Pixel(0, 10) // 标签偏移量
      },
      draggable: true, // 启用拖拽功能
      cursor: 'move' // 鼠标悬停时显示移动光标
    })
    
    // 添加拖拽结束事件监听器
    marker.on('dragend', (e: any) => {
      // 获取新位置坐标
      const newPosition: [number, number] = [e.lnglat.getLng(), e.lnglat.getLat()]
      // 发出起点位置变化事件
      emit('start-point-changed', newPosition)
    })
    
    markers.push(marker)
  }

  // 添加配送点标记
  props.deliveryPoints.forEach((point, index) => {
    // 使用高德地图内置的标记样式
    const marker = new (window as any).AMap.Marker({
      position: point.coordinates,
      map: mapInstance,
      icon: new (window as any).AMap.Icon({
        size: new (window as any).AMap.Size(32, 32),
        image: `//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-${((index % 5) + 1)}.png`,
        imageSize: new (window as any).AMap.Size(32, 32)
      }),
      title: `配送点 ${index + 1} (重量: ${point.weight}${point.weightUnit === 'kg' ? 'kg' : '吨'})`,
      cursor: 'move', // 鼠标悬停时显示移动光标
      zIndex: 50 + index, // 确保配送点按顺序层级递增
      label: {
        content: String(index + 1), // 显示配送点编号
        direction: 'top', // 标签显示在标记上方
        offset: new (window as any).AMap.Pixel(0, -5), // 标签偏移量
        style: {
          backgroundColor: '#fff',
          borderRadius: '50%',
          border: '2px solid #3366FF',
          padding: '2px 6px',
          fontSize: '12px',
          fontWeight: 'bold',
          color: '#3366FF'
        }
      },
      draggable: true, // 启用拖拽功能
    })
    
    // 添加点击事件
    marker.on('click', () => {
      emit('delivery-point-click', index, point.coordinates)
    })
    
    // 添加拖拽结束事件监听器
    marker.on('dragend', (e: any) => {
      // 获取新位置坐标
      const newPosition: [number, number] = [e.lnglat.getLng(), e.lnglat.getLat()]
      // 发出配送点位置变化事件
      emit('delivery-point-changed', index, newPosition)
    })
    
    // 添加鼠标悬停事件
    marker.on('mouseover', () => {
      // 悬停时增大标记尺寸
      marker.setIcon(new (window as any).AMap.Icon({
        size: new (window as any).AMap.Size(40, 40),
        image: `//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-${((index % 5) + 1)}.png`,
        imageSize: new (window as any).AMap.Size(40, 40)
      }))
      // 调整标签样式
      marker.setLabel({
        content: String(index + 1),
        direction: 'top',
        offset: new (window as any).AMap.Pixel(0, -5),
        style: {
          backgroundColor: '#fff',
          borderRadius: '50%',
          border: '2px solid #3366FF',
          padding: '3px 8px',
          fontSize: '14px',
          fontWeight: 'bold',
          color: '#3366FF'
        }
      })
    })
    
    // 添加鼠标离开事件
    marker.on('mouseout', () => {
      // 恢复标记原始尺寸
      marker.setIcon(new (window as any).AMap.Icon({
        size: new (window as any).AMap.Size(32, 32),
        image: `//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-${((index % 5) + 1)}.png`,
        imageSize: new (window as any).AMap.Size(32, 32)
      }))
      // 恢复标签原始样式
      marker.setLabel({
        content: String(index + 1),
        direction: 'top',
        offset: new (window as any).AMap.Pixel(0, -5),
        style: {
          backgroundColor: '#fff',
          borderRadius: '50%',
          border: '2px solid #3366FF',
          padding: '2px 6px',
          fontSize: '12px',
          fontWeight: 'bold',
          color: '#3366FF'
        }
      })
    })
    
    markers.push(marker)
  })

  // 添加配送路径
  if (props.path.length > 1) {
    // 路径样式配置
    const polylineOptions: any = {
      path: props.path,
      map: mapInstance,
      strokeColor: '#3366FF',
      strokeWeight: 6,
      strokeStyle: 'solid',
      strokeOpacity: 0.8
    }

    // 如果启用路径动画
    if (props.animatePath) {
      polylineOptions.lineJoin = 'round'
      polylineOptions.lineCap = 'round'
      polylineOptions.strokeDasharray = [10, 5] // 虚线样式
      polylineOptions.strokeDashoffset = 200 // 动画起始偏移量
    }

    polyline = new (window as any).AMap.Polyline(polylineOptions)

    // 如果启用路径动画，添加动画效果
    if (props.animatePath) {
      let offset = 200
      const animate = () => {
        offset -= 2
        polyline.setOptions({ strokeDashoffset: offset })
        if (offset < -100) {
          offset = 200
        }
        requestAnimationFrame(animate)
      }
      animate()
    }
  }

  // 调整地图视野以显示所有标记点和路径
  mapInstance.setFitView()
  
  // 绘制校区边界
  if (props.showCampusBoundary) {
    drawCampusBoundary()
  }
}

// 绘制校区边界
const drawCampusBoundary = () => {
  if (!mapInstance || !props.campusCenter || !props.campusRadius) return
  
  try {
    // 创建圆形边界
    campusBoundary = new (window as any).AMap.Circle({
      map: mapInstance,
      center: props.campusCenter,
      radius: props.campusRadius, // 半径（米）
      strokeColor: '#FF0000', // 边界颜色
      strokeWeight: 2, // 边界宽度
      strokeOpacity: 0.8, // 边界透明度
      fillColor: '#FF0000', // 填充颜色
      fillOpacity: 0.1, // 填充透明度
      zIndex: 10, // 层级，确保在底层
      title: `中国石油大学(华东) ${props.campusRadius}米范围`
    })
    
    // 添加校区中心标记
    const centerMarker = new (window as any).AMap.Marker({
      position: props.campusCenter,
      map: mapInstance,
      title: `中国石油大学(华东)中心`,
      icon: new (window as any).AMap.Icon({
        size: new (window as any).AMap.Size(20, 20),
        image: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png',
        imageSize: new (window as any).AMap.Size(20, 20)
      }),
      label: {
        content: '校区中心',
        direction: 'bottom',
        offset: new (window as any).AMap.Pixel(0, 10),
        style: {
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          padding: '2px 8px',
          borderRadius: '4px',
          border: '1px solid #FF0000',
          color: '#FF0000',
          fontSize: '12px'
        }
      },
      zIndex: 20 // 确保中心标记在边界之上
    })
    
    markers.push(centerMarker)
    
    console.info('[AMAP INFO] 校区边界绘制成功')
  } catch (error) {
    console.error('[AMAP ERROR] 绘制校区边界失败:', error)
  }
}

// 清除所有标记点
const clearMarkers = () => {
  if (mapInstance && markers.length > 0) {
    mapInstance.remove(markers)
  } else if (isOfflineMode.value && mapContainer.value) {
    // 清除离线模式下的标记点
    const offlineMarkers = mapContainer.value.querySelectorAll('.offline-marker')
    offlineMarkers.forEach(marker => marker.remove())
  }
  markers = []
}

// 渲染离线模式下的标记点
const renderOfflineMarkers = () => {
  if (!mapContainer.value) return
  
  const container = mapContainer.value
  const containerRect = container.getBoundingClientRect()
  
  // 计算坐标到容器内像素的转换比例
  const [minLng, minLat] = offlineMapData.value.bounds[0]
  const [maxLng, maxLat] = offlineMapData.value.bounds[1]
  const lngRange = maxLng - minLng
  const latRange = maxLat - minLat
  
  const toPixel = (lng: number, lat: number) => {
    const x = ((lng - minLng) / lngRange) * containerRect.width
    const y = ((maxLat - lat) / latRange) * containerRect.height
    return { x, y }
  }
  
  // 添加起点标记
  if (props.startPoint) {
    const { x, y } = toPixel(props.startPoint[0], props.startPoint[1])
    const marker = document.createElement('div')
    marker.className = 'offline-marker offline-start-marker'
    marker.style.left = `${x - 15}px`
    marker.style.top = `${y - 15}px`
    marker.innerHTML = `
      <div class="offline-marker-content">
        <div class="offline-marker-icon">🏠</div>
        <div class="offline-marker-label">起点</div>
      </div>
    `
    container.appendChild(marker)
    markers.push(marker)
  }
  
  // 添加配送点标记
  props.deliveryPoints.forEach((point, index) => {
    const { x, y } = toPixel(point.coordinates[0], point.coordinates[1])
    const marker = document.createElement('div')
    marker.className = 'offline-marker offline-delivery-marker'
    marker.style.left = `${x - 15}px`
    marker.style.top = `${y - 15}px`
    marker.innerHTML = `
      <div class="offline-marker-content">
        <div class="offline-marker-icon">📦</div>
        <div class="offline-marker-label">${index + 1}</div>
        <div class="offline-marker-weight">${point.weight}${point.weightUnit === 'kg' ? 'kg' : '吨'}</div>
      </div>
    `
    
    // 添加点击事件
    marker.addEventListener('click', () => {
      emit('delivery-point-click', index, point.coordinates)
    })
    
    container.appendChild(marker)
    markers.push(marker)
  })
  
  // 绘制简单的路径连线
  if (props.path.length > 1) {
    const pathSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
    pathSvg.setAttribute('class', 'offline-path-svg')
    pathSvg.style.position = 'absolute'
    pathSvg.style.top = '0'
    pathSvg.style.left = '0'
    pathSvg.style.width = '100%'
    pathSvg.style.height = '100%'
    pathSvg.style.pointerEvents = 'none'
    
    let pathData = ''
    props.path.forEach((point, index) => {
      const { x, y } = toPixel(point[0], point[1])
      if (index === 0) {
        pathData += `M ${x} ${y}`
      } else {
        pathData += ` L ${x} ${y}`
      }
    })
    
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
    path.setAttribute('d', pathData)
    path.setAttribute('stroke', '#3366FF')
    path.setAttribute('stroke-width', '3')
    path.setAttribute('fill', 'none')
    path.setAttribute('stroke-dasharray', '10,5')
    
    pathSvg.appendChild(path)
    container.appendChild(pathSvg)
  }
}

// 更新交通图层
const updateTrafficLayer = () => {
  if (!mapInstance) return

  // 如果需要显示交通图层但还没有创建
  if (props.showTrafficLayer && !trafficLayer) {
    trafficLayer = new (window as any).AMap.Traffic({
      map: mapInstance
    })
  }
  // 如果不需要显示交通图层但已经创建
  else if (!props.showTrafficLayer && trafficLayer) {
    trafficLayer.hide()
    trafficLayer = null
  }
}

// 监听属性变化
watch(
  () => [props.startPoint, props.deliveryPoints, props.path, props.animatePath],
  () => {
    updateMapContent()
  },
  { deep: true }
)

// 监听交通图层属性变化
watch(
  () => props.showTrafficLayer,
  () => {
    updateTrafficLayer()
  }
)

// 全局错误监听函数
let globalErrorListener: (event: ErrorEvent) => void

// 组件挂载时加载地图
onMounted(() => {
  // 添加全局错误监听，捕获高德地图API可能产生的未处理错误
  globalErrorListener = (event: ErrorEvent) => {
    // 检查是否是高德地图相关的错误
    if (event.message?.includes('FlyDataAuthTask') || event.message?.includes('INVALID_USER_KEY')) {
      // 防止错误冒泡和重复处理
      event.preventDefault()
      event.stopPropagation()
      
      // 记录规范的错误日志
      console.error('[AMAP ERROR]', {
        code: 'INVALID_USER_KEY',
        message: '高德地图API密钥验证失败',
        details: event.message
      })
      
      // 切换到离线模式
      if (!isOfflineMode.value) {
        toggleOfflineMode()
      }
    }
  }
  
  // 添加全局错误监听
  window.addEventListener('error', globalErrorListener)
  
  // 加载地图
  loadMap()
})

// 组件卸载时清理资源
onUnmounted(() => {
  // 移除全局错误监听
  if (globalErrorListener) {
    window.removeEventListener('error', globalErrorListener)
  }
  
  // 清理网络监听器
  if (networkListenerCleanup.value) {
    networkListenerCleanup.value()
    networkListenerCleanup.value = null
  }
  
  // 清理地图资源
  if (mapInstance) {
    clearMarkers()
    if (polyline) {
      mapInstance.remove(polyline)
    }
    mapInstance.destroy()
    mapInstance = null
  }
})
</script>

<style scoped>
.amap-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.map-container {
  width: 100%;
  height: 100%;
}

/* 地图错误提示样式 */
.map-error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.map-error-content {
  text-align: center;
  background-color: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-width: 400px;
  width: 90%;
}

.map-error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.map-error-content h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.5rem;
}

.map-error-content p {
  margin: 0 0 1.5rem 0;
  color: #666;
}

.map-error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.retry-btn, .offline-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-btn {
  background-color: #409EFF;
  color: white;
}

.retry-btn:hover:not(:disabled) {
  background-color: #66B1FF;
}

.retry-btn:disabled {
  background-color: #C0C4CC;
  cursor: not-allowed;
}

.offline-btn {
  background-color: #67C23A;
  color: white;
}

.offline-btn:hover {
  background-color: #85CE61;
}

/* 离线模式标记样式 */
.offline-marker {
  position: absolute;
  width: 30px;
  height: 30px;
  cursor: pointer;
  transition: transform 0.2s ease;
  z-index: 100;
}

.offline-marker:hover {
  transform: scale(1.2);
}

.offline-marker-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.offline-marker-icon {
  font-size: 1.2rem;
  margin-bottom: 2px;
}

.offline-marker-label {
  font-size: 0.7rem;
  font-weight: bold;
  color: #333;
  white-space: nowrap;
}

.offline-marker-weight {
  font-size: 0.6rem;
  color: #666;
  white-space: nowrap;
  margin-top: 2px;
}

.offline-start-marker .offline-marker-label {
  color: #409EFF;
}

.offline-delivery-marker .offline-marker-label {
  color: #67C23A;
}

.offline-path-svg {
  z-index: 50;
}
</style>
