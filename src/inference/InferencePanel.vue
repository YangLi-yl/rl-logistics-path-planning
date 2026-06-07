<template>
  <div class="inference-panel">
    <h1>路径规划推理</h1>
    
    <div class="inference-content">
      <!-- 左侧配置面板 -->
      <div class="config-panel">
        <div class="header-actions">
          <h2>配送配置</h2>
          <button class="refresh-btn" @click="refreshData">
            <i class="el-icon-refresh"></i> 刷新数据
          </button>
        </div>
        <div class="form-group">
          <label for="startAddress">起点地址</label>
          <el-autocomplete
            v-model="startAddress"
            :fetch-suggestions="querySearch"
            placeholder="请输入地址或坐标（longitude,latitude）"
            :trigger-on-focus="false"
            clearable
            @select="handleAddressSelect('start')"
            @change="parseCoordinates('start')"
          >
            <template #prefix>
              <i class="el-icon-search"></i>
            </template>
          </el-autocomplete>
          <input
            type="hidden"
            id="startPosition"
            v-model="startPosition"
          />
          <span v-if="startAddressError" class="error-message">{{ startAddressError }}</span>
        </div>
        
        <div class="form-group">
          <div class="section-header">
            <label>配送点 ({{ deliveryPoints.length }}/5)</label>
            <button 
              class="add-btn" 
              @click="addDeliveryPoint"
              :disabled="deliveryPoints.length >= 5"
            >
              添加配送点
            </button>
          </div>
          <div class="delivery-points">
            <div 
              v-for="(point, index) in deliveryPoints" 
              :key="index"
              class="delivery-point-item"
            >
              <div class="delivery-point-field">
                <label>地址</label>
                <el-autocomplete
                  v-model="point.address"
                  :fetch-suggestions="querySearch"
                  placeholder="请输入地址或坐标"
                  :trigger-on-focus="false"
                  clearable
                  @select="handleAddressSelect('delivery', index)"
                  @change="handlePointInputChange(index)"
                >
                  <template #prefix>
                    <i class="el-icon-search"></i>
                  </template>
                </el-autocomplete>
                <input
                  type="hidden"
                  v-model="point.coordinates"
                />
              </div>
              
              <div class="delivery-point-field">
                <label>时间窗</label>
                <div class="time-window">
                  <el-time-picker
                    v-model="point.timeWindow[0]"
                    format="HH:mm"
                    value-format="HH:mm"
                    placeholder="开始时间"
                    size="small"
                    @change="handlePointInputChange(index)"
                  />
                  <span class="time-separator">至</span>
                  <el-time-picker
                    v-model="point.timeWindow[1]"
                    format="HH:mm"
                    value-format="HH:mm"
                    placeholder="结束时间"
                    size="small"
                    @change="handlePointInputChange(index)"
                  />
                </div>
              </div>
              
              <div class="delivery-point-field">
                <label>货物重量</label>
                <div class="weight-input">
                  <el-input-number
                    v-model="point.weight"
                    :min="0.1"
                    :max="1000"
                    :step="0.1"
                    placeholder="重量"
                    size="small"
                    @change="handlePointInputChange(index)"
                  />
                  <el-select 
                    v-model="point.weightUnit"
                    size="small"
                    class="unit-select"
                    @change="handlePointInputChange(index)"
                  >
                    <option value="kg">kg</option>
                    <option value="ton">吨</option>
                  </el-select>
                </div>
              </div>
              
              <!-- 错误信息显示 -->
              <div v-if="point.errors.length > 0" class="delivery-point-errors">
                <ul>
                  <li v-for="(error, idx) in point.errors" :key="idx" class="error-item">
                    {{ error }}
                  </li>
                </ul>
              </div>
              
              <button 
                class="remove-btn"
                @click="removeDeliveryPoint(index)"
              >
                删除
              </button>
            </div>
            <div v-if="deliveryPoints.length >= 5" class="limit-warning">
              单次任务最多只能添加5个配送点
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <label for="algorithm">选择算法</label>
          <select id="algorithm" v-model="selectedAlgorithm">
            <option value="ppo">PPO模型</option>
            <option value="greedy">贪心算法</option>
          </select>
        </div>
        
        <div class="form-group" v-if="selectedAlgorithm === 'ppo'">
          <label for="modelSelect">选择模型版本</label>
          <select id="modelSelect" v-model="selectedModel">
            <option v-for="model in availableModels" :key="model.key" :value="model.key">
              {{ model.type }} v{{ model.version }} ({{ model.isLoaded ? '已加载' : '未加载' }})
            </option>
          </select>
        </div>
        
        <!-- 批量导入功能 -->
        <div class="form-group">
          <label>批量导入配送点</label>
          <div class="excel-import-section">
            <div class="excel-import-actions">
              <div class="excel-import">
                <input
                  type="file"
                  id="excelImport"
                  accept=".xlsx,.xls"
                  @change="handleExcelImport"
                  class="file-input"
                />
                <label for="excelImport" class="import-btn">
                  <span>选择Excel文件</span>
                </label>
              </div>
              <button class="template-btn" @click="downloadTemplate">
                下载模板
              </button>
            </div>
            <div class="file-status">
              {{ selectedFileName ? `已选择: ${selectedFileName}` : '未选择文件' }}
            </div>
            
            <!-- Excel数据预览 -->
            <div v-if="excelPreviewData.length > 0" class="excel-preview">
              <h4>数据预览</h4>
              <div class="preview-table-container">
                <table class="preview-table">
                  <thead>
                    <tr>
                      <th>序号</th>
                      <th>地址</th>
                      <th>经度</th>
                      <th>纬度</th>
                      <th>时间窗开始</th>
                      <th>时间窗结束</th>
                      <th>重量</th>
                      <th>单位</th>
                      <th>状态</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr 
                      v-for="(row, index) in excelPreviewData" 
                      :key="index"
                      :class="{ 'error-row': row.errors && row.errors.length > 0 }"
                    >
                      <td>{{ index + 1 }}</td>
                      <td>{{ row.address }}</td>
                      <td>{{ row.longitude }}</td>
                      <td>{{ row.latitude }}</td>
                      <td>{{ row.timeWindowStart }}</td>
                      <td>{{ row.timeWindowEnd }}</td>
                      <td>{{ row.weight }}</td>
                      <td>{{ row.unit }}</td>
                      <td>
                        <span v-if="row.errors && row.errors.length > 0" class="status-error">
                          错误
                        </span>
                        <span v-else class="status-success">
                          有效
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <!-- 导入操作按钮 -->
              <div class="import-preview-actions">
                <button class="cancel-preview-btn" @click="cancelPreview">
                  取消
                </button>
                <button class="confirm-import-btn" @click="confirmImport">
                  确认导入 ({{ validPreviewDataCount }}/{{ excelPreviewData.length }})
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <label for="vehicleType">车型选择</label>
          <select id="vehicleType" v-model="selectedVehicleType" @change="handleVehicleTypeChange">
            <option value="small">小型车 (载重≤500kg)</option>
            <option value="medium">中型车 (载重≤2吨)</option>
            <option value="large">大型车 (载重≤5吨)</option>
          </select>
        </div>
        
        <button 
          class="start-btn" 
          @click="startInference"
          :disabled="!canStartInference"
        >
          开始路径规划
        </button>
        
        <div v-if="inferenceLoading" class="loading">
          <div class="loading-spinner"></div>
          <p>正在计算最优路径...</p>
        </div>
      </div>
      
      <!-- 右侧地图面板 -->
      <div class="map-panel">
        <h2>校园地图</h2>
        <div class="map-container">
          <AmapMap
            :start-point="startPointArray"
            :delivery-points="deliveryPointsArray"
            :path="plannedPath"
            :campus-center="[CAMPUS_CONFIG.CENTER.lng, CAMPUS_CONFIG.CENTER.lat]"
            :campus-radius="CAMPUS_CONFIG.MAX_DISTANCE"
            :show-campus-boundary="true"
            style="width: 100%; height: 100%;"
            @start-point-changed="handleStartPointChanged"
            @delivery-point-changed="handleDeliveryPointChanged"
            @location-changed="handleLocationChanged"
            @location-error="handleLocationError"
          />
        </div>
        
        <div v-if="inferenceResult" class="result-panel">
          <h3>规划结果</h3>
          <div class="result-info">
            <p><strong>总距离:</strong> {{ inferenceResult.total_distance }} 米</p>
            <p><strong>总时间:</strong> {{ inferenceResult.total_time }} 分钟</p>
            <p><strong>路径顺序:</strong></p>
            <ol>
              <li v-for="(point, index) in inferenceResult.path" :key="index">
                {{ point[0].toFixed(4) }}, {{ point[1].toFixed(4) }}
              </li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AmapMap from '../components/AmapMap.vue'
import { inferRoute, getAvailableModels } from '../api/model'
import { geocode, getAddressSuggestions } from '../api/geocode'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'

// 配送点审核状态
enum DeliveryPointStatus {
  PENDING = 'pending', // 待审核
  APPROVED = 'approved', // 已通过
  REJECTED = 'rejected', // 已拒绝
  INVALID = 'invalid' // 无效（位置超出范围）
}

// 配送点接口定义
interface DeliveryPoint {
  id: number
  address: string
  coordinates: string
  timeWindow: [string, string]
  weight: number
  weightUnit: 'kg' | 'ton'
  errors: string[] // 错误信息数组
  distance?: number // 与校区中心的距离（米）
  status: DeliveryPointStatus // 审核状态
}

// 起点地址输入
const startAddress = ref('中国石油大学(华东)行政楼')
const startPosition = ref('120.3925,36.0655') // 中国石油大学华东行政楼准确GCJ-02坐标
const startAddressError = ref('')

// 搜索加载状态
const searchLoading = ref(false)

// 本地存储键名
const LOCAL_STORAGE_KEYS = {
  START_ADDRESS: 'campus_logistics_start_address',
  START_POSITION: 'campus_logistics_start_position',
  DELIVERY_POINTS: 'campus_logistics_delivery_points'
}

// 从本地存储加载数据的类型定义
interface LocalStorageData {
  startAddress: string
  startPosition: string
  deliveryPoints: DeliveryPoint[]
}

// 从本地存储加载数据
const loadFromLocalStorage = (): LocalStorageData | null => {
  try {
    const startAddressDefault = localStorage.getItem(LOCAL_STORAGE_KEYS.START_ADDRESS) || '中国石油大学(华东)行政楼'
    const startPositionDefault = localStorage.getItem(LOCAL_STORAGE_KEYS.START_POSITION) || '120.3925,36.0655'
    const deliveryPointsStr = localStorage.getItem(LOCAL_STORAGE_KEYS.DELIVERY_POINTS)
    
    let deliveryPointsDefault: DeliveryPoint[] = [
      {
        id: 1,
        address: '中国石油大学(华东)图书馆',
        coordinates: '120.3975,36.0675', // 图书馆准确GCJ-02坐标
        timeWindow: ['09:00', '12:00'],
        weight: 50,
        weightUnit: 'kg',
        errors: [],
        status: DeliveryPointStatus.APPROVED
      },
      {
        id: 2,
        address: '中国石油大学(华东)行政楼',
        coordinates: '120.3925,36.0655', // 行政楼准确GCJ-02坐标
        timeWindow: ['10:00', '14:00'],
        weight: 30,
        weightUnit: 'kg',
        errors: [],
        status: DeliveryPointStatus.APPROVED
      },
      {
        id: 3,
        address: '中国石油大学(华东)体育馆',
        coordinates: '120.3960,36.0630', // 体育馆准确GCJ-02坐标
        timeWindow: ['13:00', '16:00'],
        weight: 20,
        weightUnit: 'kg',
        errors: [],
        status: DeliveryPointStatus.APPROVED
      }
    ]
    
    if (deliveryPointsStr) {
      const parsedPoints = JSON.parse(deliveryPointsStr)
      if (Array.isArray(parsedPoints) && parsedPoints.length > 0) {
        // 确保每个配送点都有完整的字段
        deliveryPointsDefault = parsedPoints.map(point => ({
          id: point.id || Date.now() + Math.random(),
          address: point.address || '',
          coordinates: point.coordinates || '',
          timeWindow: point.timeWindow || ['09:00', '12:00'],
          weight: point.weight || 0,
          weightUnit: point.weightUnit || 'kg',
          errors: point.errors || [],
          status: point.status || DeliveryPointStatus.PENDING
        }))
      }
    }
    
    return {
      startAddress: startAddressDefault,
      startPosition: startPositionDefault,
      deliveryPoints: deliveryPointsDefault
    }
  } catch (error) {
    console.error('从本地存储加载数据失败:', error)
    return null
  }
}

// 保存数据到本地存储
const saveToLocalStorage = () => {
  try {
    localStorage.setItem(LOCAL_STORAGE_KEYS.START_ADDRESS, startAddress.value)
    localStorage.setItem(LOCAL_STORAGE_KEYS.START_POSITION, startPosition.value)
    localStorage.setItem(LOCAL_STORAGE_KEYS.DELIVERY_POINTS, JSON.stringify(deliveryPoints.value))
  } catch (error) {
    console.error('保存数据到本地存储失败:', error)
    ElMessage.error('保存数据失败，请检查浏览器本地存储权限')
  }
}

// 配送点输入数组
const deliveryPoints = ref<DeliveryPoint[]>([])

// 选择的算法
const selectedAlgorithm = ref('greedy')

// 模型选择
const selectedModel = ref('')
const availableModels = ref<any[]>([])

// 车型选择
const selectedVehicleType = ref('small')

// 推理加载状态
const inferenceLoading = ref(false)

// 推理结果
const inferenceResult = ref<any>(null)

// 计划路径
const plannedPath = computed(() => {
  if (inferenceResult.value) {
    return inferenceResult.value.path
  }
  return []
})

// 起点数组格式
const startPointArray = computed(() => {
  const [lng, lat] = startPosition.value.split(',').map(Number)
  if (isNaN(lng) || isNaN(lat)) {
    return null
  }
  return [lng, lat] as [number, number]
})

// 配送点坐标数组格式（用于地图显示）
const deliveryPointsArray = computed(() => {
  return deliveryPoints.value
    .map(point => {
      const [lng, lat] = point.coordinates.split(',').map(Number)
      return {
        coordinates: [lng, lat] as [number, number],
        weight: point.weight || 0,
        weightUnit: point.weightUnit || 'kg'
      }
    })
    .filter(({ coordinates }) => !isNaN(coordinates[0]) && !isNaN(coordinates[1]))
})

// 配送点完整数据数组（用于API调用）
const deliveryPointsForApi = computed(() => {
  return deliveryPoints.value
    .map(point => {
      const [lng, lat] = point.coordinates.split(',').map(Number)
      
      // 转换时间窗为分钟数
      const [startHour, startMin] = point.timeWindow[0].split(':').map(Number)
      const [endHour, endMin] = point.timeWindow[1].split(':').map(Number)
      const startTime = startHour * 60 + startMin
      const endTime = endHour * 60 + endMin
      
      return {
        lon: lng,
        lat: lat,
        weight: point.weightUnit === 'ton' ? point.weight * 1000 : point.weight,
        time_window: [startTime, endTime] as [number, number]
      }
    })
    .filter(point => !isNaN(point.lon) && !isNaN(point.lat))
})

// 批量导入相关状态
const selectedFileName = ref('')
const excelPreviewData = ref<any[]>([])

// Excel预览数据接口
interface ExcelPreviewRow {
  address: string
  longitude: number
  latitude: number
  timeWindowStart: string
  timeWindowEnd: string
  weight: number
  unit: string
  errors?: string[]
}

// 有效预览数据数量
const validPreviewDataCount = computed(() => {
  return excelPreviewData.value.filter(row => !row.errors || row.errors.length === 0).length
})

// 数据校验函数
const validateDeliveryPoint = (point: DeliveryPoint): string[] => {
  const errors: string[] = []
  
  // 地址和坐标验证
  if (!point.address) {
    errors.push('请输入地址')
  }
  
  if (!point.coordinates) {
    errors.push('请输入坐标')
  } else {
    const [lng, lat] = point.coordinates.split(',').map(Number)
    if (isNaN(lng) || isNaN(lat)) {
      errors.push('坐标格式错误，应为longitude,latitude')
    } else {
        // 坐标范围验证（中国大致范围）
        if (lng < 73 || lng > 135) {
          errors.push('经度超出中国范围（73-135）')
        }
        if (lat < 18 || lat > 54) {
          errors.push('纬度超出中国范围（18-54）')
        }
        
        // 坐标范围验证（中国石油大学华东校区附近1公里范围内）
        const locationValidation = validateCampusLocation(point.coordinates)
        point.distance = locationValidation.distance // 存储距离信息
        if (!locationValidation.valid) {
          errors.push(`配送点应设置在${CAMPUS_CONFIG.NAME}1公里范围内，当前位置超出校区范围${locationValidation.distance - CAMPUS_CONFIG.MAX_DISTANCE}米`)
          point.status = DeliveryPointStatus.INVALID // 超出范围的配送点标记为无效
        } else {
          // 位置有效但需要审核
          if (point.status !== DeliveryPointStatus.APPROVED) {
            point.status = DeliveryPointStatus.PENDING
          }
        }
      }
  }
  
  // 时间窗验证
  if (!point.timeWindow[0] || !point.timeWindow[1]) {
    errors.push('请设置完整的时间窗')
  } else {
    const [startHour, startMin] = point.timeWindow[0].split(':').map(Number)
    const [endHour, endMin] = point.timeWindow[1].split(':').map(Number)
    if (isNaN(startHour) || isNaN(startMin) || isNaN(endHour) || isNaN(endMin)) {
      errors.push('时间格式错误，应为HH:mm')
    } else {
      const startTime = startHour * 60 + startMin
      const endTime = endHour * 60 + endMin
      if (startTime >= endTime) {
        errors.push('开始时间必须早于结束时间')
      }
    }
  }
  
  // 重量验证
  if (!point.weight || point.weight <= 0) {
    errors.push('请输入有效的重量')
  } else {
    // 根据车型限制重量
    const maxWeight = {
      small: 500, // 小型车最大载重500kg
      medium: 2000, // 中型车最大载重2吨
      large: 5000 // 大型车最大载重5吨
    }[selectedVehicleType.value] || 500 // 默认使用小型车的重量限制
    
    const weightInKg = point.weightUnit === 'ton' ? point.weight * 1000 : point.weight
    if (weightInKg > maxWeight) {
      errors.push(`单配送点重量超过车型限制（最大${maxWeight}kg）`)
    }
  }
  
  return errors
}

// 批量验证所有配送点
const validateAllDeliveryPoints = () => {
  let allValid = true
  
  // 验证每个配送点
  deliveryPoints.value.forEach(point => {
    const errors = validateDeliveryPoint(point)
    point.errors = errors
    if (errors.length > 0) {
      allValid = false
    }
  })
  
  return allValid
}

// 计算总重量
const totalWeight = computed(() => {
  return deliveryPoints.value.reduce((total, point) => {
    const weightInKg = point.weightUnit === 'ton' ? point.weight * 1000 : point.weight
    return total + (isNaN(weightInKg) ? 0 : weightInKg)
  }, 0)
})

// 表单验证状态
const canStartInference = computed(() => {
  // 检查起点
  if (!startPointArray.value) {
    startAddressError.value = '请输入有效的起点地址或坐标'
    return false
  } else {
    // 验证起点是否在中国石油大学华东校区附近
    const startCoordinates = `${startPointArray.value[0]},${startPointArray.value[1]}`
    const locationValidation = validateCampusLocation(startCoordinates)
    if (!locationValidation.valid) {
      startAddressError.value = '起点应设置在中国石油大学华东校区范围内（1公里内）'
      return false
    }
    startAddressError.value = ''
  }
  
  // 检查配送点数量
  if (deliveryPoints.value.length === 0) {
    return false
  }
  
  if (deliveryPoints.value.length > 5) {
    return false
  }
  
  // 验证所有配送点
  const allPointsValid = validateAllDeliveryPoints()
  if (!allPointsValid) {
    return false
  }
  
  // 检查总重量限制
  const maxTotalWeight = {
    small: 500, // 小型车最大载重500kg
    medium: 2000, // 中型车最大载重2吨
    large: 5000 // 大型车最大载重5吨
  }[selectedVehicleType.value] || 500 // 默认使用小型车的重量限制
  
  if (totalWeight.value > maxTotalWeight) {
    return false
  }
  
  return true
})

// 地址搜索建议
const querySearch = async (queryString: string, callback: any) => {
  if (!queryString.trim()) {
    callback([])
    return
  }
  
  searchLoading.value = true
  
  try {
    // 使用高德地图API获取地址建议
    const result = await getAddressSuggestions(queryString, '青岛市')
    
    if (result.status === '1') {
      // 转换为前端组件需要的格式
      const suggestions = result.tips.map(tip => ({
        value: tip.name,
        address: `${tip.province}${tip.city}${tip.district}${tip.address}`,
        coordinates: tip.location
      }))
      
      callback(suggestions)
    } else {
      console.error('地址搜索建议获取失败:', result.info)
      ElMessage.warning(`地址搜索失败: ${result.info}`)
      // API调用失败时返回空结果
      callback([])
    }
  } catch (error: any) {
    console.error('地址搜索建议API调用失败:', error)
    
    // 根据错误类型显示不同的提示
    if (error.message?.includes('NETWORK_ERROR') || error.message?.includes('网络')) {
      ElMessage.warning('网络连接失败，请检查网络设置')
    } else if (error.message?.includes('USERKEY_PLAT_NOMATCH')) {
      ElMessage.warning('API密钥配置有误，请联系管理员')
    } else {
      ElMessage.warning('地址搜索服务暂时不可用，请稍后重试')
    }
    
    // API调用失败时返回空结果
    callback([])
  } finally {
    searchLoading.value = false
  }
}

// 处理地址选择
const handleAddressSelect = async (type: 'start' | 'delivery', index?: number) => {
  let address: string
  
  if (type === 'start') {
    address = startAddress.value
  } else if (index !== undefined) {
    address = deliveryPoints.value[index].address
  } else {
    return
  }
  
  inferenceLoading.value = true
  
  try {
    // 使用高德地图API获取精确坐标
    const result = await geocode(address, '青岛市')
    
    if (result.status === '1' && result.geocodes.length > 0) {
      const coordinates = result.geocodes[0].location
      const formattedAddress = result.geocodes[0].formatted_address
      
      if (type === 'start') {
        startPosition.value = coordinates
        startAddressError.value = ''
        ElMessage.success(`成功获取起点坐标: ${formattedAddress}`)
        // 保存到本地存储
        saveToLocalStorage()
      } else if (index !== undefined) {
        deliveryPoints.value[index].coordinates = coordinates
        // 验证配送点
        validateSingleDeliveryPoint(index)
        ElMessage.success(`成功获取配送点${index + 1}坐标: ${formattedAddress}`)
        // 保存到本地存储
        saveToLocalStorage()
      }
      
      // 验证坐标是否在合理范围内（青岛地区）
      const [lng, lat] = coordinates.split(',').map(Number)
      if (lng < 120.0 || lng > 121.0 || lat < 35.5 || lat > 37.0) {
        ElMessage.warning('检测到坐标可能不准确，请确认地址是否正确')
      }
    } else {
      console.error('地理编码失败:', result.info)
      ElMessage.warning(`获取坐标失败: ${result.info}，将尝试直接解析地址`)
      // 如果API调用失败，尝试直接解析坐标字符串
      parseCoordinates(type, index)
    }
  } catch (error: any) {
    console.error('地理编码API调用失败:', error)
    
    // 根据错误类型显示不同的提示
    if (error.message?.includes('NETWORK_ERROR') || error.message?.includes('网络')) {
      ElMessage.error('网络连接失败，请检查网络设置后重试')
    } else if (error.message?.includes('USERKEY_PLAT_NOMATCH')) {
      ElMessage.error('API密钥配置有误，无法获取精确坐标')
    } else {
      ElMessage.error('获取地址坐标失败，请稍后重试或直接输入坐标')
    }
    
    // API调用失败时，尝试直接解析坐标字符串
    parseCoordinates(type, index)
  } finally {
    inferenceLoading.value = false
  }
}

// 校区中心点配置（可配置化）
const CAMPUS_CONFIG = {
  CENTER: { lng: 120.3945, lat: 36.0665 }, // 中国石油大学华东校区中心坐标
  MAX_DISTANCE: 1000, // 1公里范围
  NAME: '中国石油大学(华东)'
}

// 角度转弧度
const toRadians = (degrees: number): number => {
  return degrees * Math.PI / 180
}

// 计算两点之间的地理距离（米）
const calculateDistance = (point1: { lng: number; lat: number }, point2: { lng: number; lat: number }): number => {
  const R = 6371000 // 地球半径（米）
  const φ1 = toRadians(point1.lat)
  const φ2 = toRadians(point2.lat)
  const Δφ = toRadians(point2.lat - point1.lat)
  const Δλ = toRadians(point2.lng - point1.lng)
  
  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) * Math.sin(Δλ / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  
  return R * c // 距离（米）
}

// 验证坐标是否在中国石油大学华东校区附近（1公里范围内）
const validateCampusLocation = (coordinates: string): { valid: boolean; distance: number } => {
  // 输入验证
  if (!coordinates) {
    return { valid: false, distance: 0 }
  }
  
  // 解析坐标
  const [lng, lat] = coordinates.split(',').map(Number)
  if (isNaN(lng) || isNaN(lat)) {
    return { valid: false, distance: 0 }
  }
  
  const point = { lng, lat }
  
  // 允许当前设置的起点位置绕过1公里限制
  const [startLng, startLat] = startPosition.value.split(',').map(Number)
  const startPoint = { lng: startLng, lat: startLat }
  
  if (calculateDistance(point, startPoint) < 1) { // 距离小于1米视为同一点
    return { valid: true, distance: 0 }
  }
  
  // 计算与校区中心的距离
  const distance = calculateDistance(point, CAMPUS_CONFIG.CENTER)
  
  // 最大距离1000米（1公里）
  const isValid = distance <= CAMPUS_CONFIG.MAX_DISTANCE
  
  return { valid: isValid, distance: Math.round(distance) }
}

// 解析坐标字符串
const parseCoordinates = (type: 'start' | 'delivery', index?: number) => {
  if (type === 'start') {
    const [lng, lat] = startAddress.value.split(',').map(Number)
    if (!isNaN(lng) && !isNaN(lat)) {
      startPosition.value = `${lng},${lat}`
      startAddressError.value = ''
      // 保存到本地存储
      saveToLocalStorage()
    } else {
      startPosition.value = ''
      startAddressError.value = '请输入有效的坐标格式（longitude,latitude）'
    }
  } else if (index !== undefined) {
    // 检查地址字段是否包含坐标格式数据
    const addressValue = deliveryPoints.value[index].address
    const parsedCoordinates = addressValue.split(',').map(Number)
    
    // 只有当解析出有效坐标时才更新coordinates字段
    if (parsedCoordinates.length === 2 && !isNaN(parsedCoordinates[0]) && !isNaN(parsedCoordinates[1])) {
      deliveryPoints.value[index].coordinates = `${parsedCoordinates[0]},${parsedCoordinates[1]}`
      // 保存到本地存储
      saveToLocalStorage()
    } 
    // 如果地址不是坐标格式，保持原有coordinates不变
    // 验证配送点
    validateSingleDeliveryPoint(index)
  }
}

// 实时验证配送点
const validateSingleDeliveryPoint = (index: number) => {
  const point = deliveryPoints.value[index]
  const errors = validateDeliveryPoint(point)
  point.errors = errors
}

// 监听配送点输入变化，实现实时验证
const handlePointInputChange = (index: number) => {
  validateSingleDeliveryPoint(index)
  // 保存到本地存储
  saveToLocalStorage()
}

// 监听车型变化，重新验证所有配送点
const handleVehicleTypeChange = () => {
  validateAllDeliveryPoints()
}

// 添加配送点
const addDeliveryPoint = () => {
  if (deliveryPoints.value.length >= 5) {
    ElMessage.warning('单次任务最多只能添加5个配送点')
    return
  }
  
  deliveryPoints.value.push({
    id: Date.now(),
    address: '',
    coordinates: '',
    timeWindow: ['', ''],
    weight: 0.1,
    weightUnit: 'kg',
    errors: [],
    status: DeliveryPointStatus.PENDING
  })
  
  // 保存到本地存储
  saveToLocalStorage()
}

// 删除配送点
const removeDeliveryPoint = (index: number) => {
  deliveryPoints.value.splice(index, 1)
  // 保存到本地存储
  saveToLocalStorage()
}

// 刷新数据（从本地存储重新加载）
const refreshData = async () => {
  try {
    const savedData = loadFromLocalStorage()
    if (savedData) {
      startAddress.value = savedData.startAddress
      startPosition.value = savedData.startPosition
      deliveryPoints.value = savedData.deliveryPoints
      ElMessage.success('数据刷新成功')
    } else {
      ElMessage.warning('未找到保存的数据，正在获取默认配置和最新坐标...')
      // 重置为默认数据（初始不包含坐标，后续通过API获取）
      const defaultPoints: DeliveryPoint[] = [
        {
          id: 1,
          address: '中国石油大学(华东)图书馆',
          coordinates: '', // 初始为空，后续通过API获取
          timeWindow: ['09:00', '12:00'] as [string, string],
          weight: 50,
          weightUnit: 'kg' as const,
          errors: [],
          status: DeliveryPointStatus.APPROVED
        },
        {
          id: 2,
          address: '中国石油大学(华东)行政楼',
          coordinates: '', // 初始为空，后续通过API获取
          timeWindow: ['10:00', '14:00'] as [string, string],
          weight: 30,
          weightUnit: 'kg' as const,
          errors: [],
          status: DeliveryPointStatus.APPROVED
        },
        {
          id: 3,
          address: '中国石油大学(华东)体育馆',
          coordinates: '', // 初始为空，后续通过API获取
          timeWindow: ['13:00', '16:00'] as [string, string],
          weight: 20,
          weightUnit: 'kg' as const,
          errors: [],
          status: DeliveryPointStatus.APPROVED
        }
      ]
      
      deliveryPoints.value = defaultPoints
      startAddress.value = '中国石油大学(华东)行政楼'
      startPosition.value = '' // 初始为空，后续通过API获取
      
      // 立即通过高德地图API获取所有坐标
      await Promise.all([
        // 获取起点坐标
        (async () => {
          const result = await geocode(startAddress.value, '青岛市')
          if (result.status === '1' && result.geocodes.length > 0) {
            startPosition.value = result.geocodes[0].location
          }
        })(),
        // 获取所有配送点坐标
        ...deliveryPoints.value.map(async (point, index) => {
          const result = await geocode(point.address, '青岛市')
          if (result.status === '1' && result.geocodes.length > 0) {
            deliveryPoints.value[index].coordinates = result.geocodes[0].location
          }
        })
      ])
      
      // 验证所有配送点
      validateAllDeliveryPoints()
      
      // 保存默认数据到本地存储
      saveToLocalStorage()
      
      ElMessage.success('默认数据加载完成并获取最新坐标')
    }
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.error('数据刷新失败，请检查网络连接或浏览器本地存储权限')
  }
}

// 处理起点位置变化
const handleStartPointChanged = (newPosition: [number, number]) => {
  // 更新起点坐标
  startPosition.value = `${newPosition[0].toFixed(6)},${newPosition[1].toFixed(6)}`
  // 保存到本地存储
  saveToLocalStorage()
}

// 处理配送点位置变化
const handleDeliveryPointChanged = (index: number, newPosition: [number, number]) => {
  // 更新配送点坐标
  if (deliveryPoints.value[index]) {
    deliveryPoints.value[index].coordinates = `${newPosition[0].toFixed(6)},${newPosition[1].toFixed(6)}`
    // 验证配送点
    validateSingleDeliveryPoint(index)
    // 保存到本地存储
    saveToLocalStorage()
  }
}

// 处理位置变化事件
const handleLocationChanged = (location: [number, number], data?: any) => {
  console.log('[LOCATION SYNC] 位置数据更新:', location)
  
  // 更新起点位置为当前定位位置
  startPosition.value = `${location[0].toFixed(6)},${location[1].toFixed(6)}`
  
  // 如果提供了地址信息，更新起点地址
  if (data && data.formattedAddress) {
    startAddress.value = data.formattedAddress
  } else {
    // 否则通过逆地理编码获取地址
    // 这里可以调用高德地图的逆地理编码API
    startAddress.value = `当前位置 (${location[0].toFixed(4)}, ${location[1].toFixed(4)})`
  }
  
  // 清除起点地址错误
  startAddressError.value = ''
  
  // 保存到本地存储
  saveToLocalStorage()
  
  ElMessage.success('定位成功，已更新起点位置')
}

// 处理定位错误事件
const handleLocationError = (error: any) => {
  console.error('[LOCATION ERROR] 定位失败:', error)
  
  // 根据错误类型显示不同的错误信息
  let errorMessage = '定位失败，请检查定位权限和网络连接'
  
  if (error.message?.includes('PERMISSION_DENIED')) {
    errorMessage = '定位权限被拒绝，请在浏览器设置中允许定位'
  } else if (error.message?.includes('POSITION_UNAVAILABLE')) {
    errorMessage = '无法获取位置信息，可能是GPS信号弱或设备不支持'
  } else if (error.message?.includes('TIMEOUT')) {
    errorMessage = '定位超时，请稍后重试'
  }
  
  // 显示错误信息
  ElMessage.error(errorMessage)
}

// 处理Excel文件导入
const handleExcelImport = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) {
    return
  }
  
  const file = input.files[0]
  selectedFileName.value = file.name
  
  // 读取Excel文件
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target?.result as ArrayBuffer)
      const workbook = XLSX.read(data, { type: 'array' })
      
      // 获取第一个工作表
      const firstSheetName = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[firstSheetName]
      
      // 解析工作表数据
      const jsonData = XLSX.utils.sheet_to_json(worksheet)
      
      // 验证和格式化数据
      excelPreviewData.value = jsonData.map((row: any) => {
        const previewRow: ExcelPreviewRow = {
          address: row['地址'] || '',
          longitude: parseFloat(row['经度']) || 0,
          latitude: parseFloat(row['纬度']) || 0,
          timeWindowStart: row['时间窗开始'] || '',
          timeWindowEnd: row['时间窗结束'] || '',
          weight: parseFloat(row['重量']) || 0,
          unit: row['单位'] || 'kg'
        }
        
        // 验证数据
        previewRow.errors = validateExcelRow(previewRow)
        
        return previewRow
      })
      
      ElMessage.success('Excel文件读取成功，共 ' + jsonData.length + ' 行数据')
    } catch (error) {
      console.error('Excel解析错误:', error)
      ElMessage.error('Excel文件解析失败，请检查文件格式')
    }
  }
  
  reader.readAsArrayBuffer(file)
}

// 验证Excel行数据
const validateExcelRow = (row: ExcelPreviewRow): string[] => {
  const errors: string[] = []
  
  // 地址验证
  if (!row.address) {
    errors.push('地址不能为空')
  }
  
  // 坐标验证
  if (isNaN(row.longitude) || isNaN(row.latitude)) {
    errors.push('坐标格式错误')
  } else {
    if (row.longitude < 73 || row.longitude > 135) {
      errors.push('经度超出中国范围（73-135）')
    }
    if (row.latitude < 18 || row.latitude > 54) {
      errors.push('纬度超出中国范围（18-54）')
    }
  }
  
  // 时间窗验证
  if (!row.timeWindowStart || !row.timeWindowEnd) {
    errors.push('时间窗不能为空')
  } else {
    const [startHour, startMin] = row.timeWindowStart.split(':').map(Number)
    const [endHour, endMin] = row.timeWindowEnd.split(':').map(Number)
    if (isNaN(startHour) || isNaN(startMin) || isNaN(endHour) || isNaN(endMin)) {
      errors.push('时间格式错误，应为HH:mm')
    } else {
      const startTime = startHour * 60 + startMin
      const endTime = endHour * 60 + endMin
      if (startTime >= endTime) {
        errors.push('开始时间必须早于结束时间')
      }
    }
  }
  
  // 重量验证
  if (isNaN(row.weight) || row.weight <= 0) {
    errors.push('重量必须大于0')
  }
  
  // 单位验证
  if (row.unit !== 'kg' && row.unit !== '吨') {
    errors.push('单位必须是kg或吨')
  }
  
  return errors
}

// 下载Excel模板
const downloadTemplate = () => {
  // 创建模板数据
  const templateData = [
    { '地址': '示例地址1', '经度': '120.394887', '纬度': '36.066204', '时间窗开始': '09:00', '时间窗结束': '12:00', '重量': '50', '单位': 'kg' },
    { '地址': '示例地址2', '经度': '120.398', '纬度': '36.068', '时间窗开始': '10:00', '时间窗结束': '14:00', '重量': '30', '单位': 'kg' },
    { '地址': '示例地址3', '经度': '120.392', '纬度': '36.065', '时间窗开始': '13:00', '时间窗结束': '16:00', '重量': '20', '单位': 'kg' }
  ]
  
  // 创建工作表
  const worksheet = XLSX.utils.json_to_sheet(templateData)
  
  // 创建工作簿
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, '配送点模板')
  
  // 下载文件
  XLSX.writeFile(workbook, '配送点导入模板.xlsx')
  
  ElMessage.success('模板下载成功')
}

// 确认导入有效数据
const confirmImport = () => {
  // 过滤有效数据
  const validData = excelPreviewData.value.filter(row => !row.errors || row.errors.length === 0)
  
  // 检查总数量限制
  if (deliveryPoints.value.length + validData.length > 5) {
    ElMessage.error(`单次任务最多只能添加5个配送点，当前已添加${deliveryPoints.value.length}个，本次只能导入${5 - deliveryPoints.value.length}个`)
    return
  }
  
  // 导入有效数据
  validData.forEach(row => {
    deliveryPoints.value.push({
      id: Date.now() + Math.random(),
      address: row.address,
      coordinates: `${row.longitude},${row.latitude}`,
      timeWindow: [row.timeWindowStart, row.timeWindowEnd],
      weight: row.weight,
      weightUnit: row.unit === '吨' ? 'ton' : 'kg',
      errors: [],
      status: DeliveryPointStatus.PENDING
    })
  })
  
  ElMessage.success(`成功导入 ${validData.length} 个配送点`)
  
  // 清空预览
  cancelPreview()
}

// 取消预览
const cancelPreview = () => {
  excelPreviewData.value = []
  selectedFileName.value = ''
  
  // 重置文件输入
  const input = document.getElementById('excelImport') as HTMLInputElement
  if (input) {
    input.value = ''
  }
}

// 组件加载时获取可用模型列表和本地存储数据
onMounted(async () => {
  try {
    // 首先加载本地存储的数据
    const savedData = loadFromLocalStorage()
    if (savedData) {
      startAddress.value = savedData.startAddress
      startPosition.value = savedData.startPosition
      deliveryPoints.value = savedData.deliveryPoints
    } else {
      // 如果没有保存的数据，使用默认数据（初始不包含坐标，后续通过API获取）
      const defaultPoints: DeliveryPoint[] = [
        {
          id: 1,
          address: '中国石油大学(华东)图书馆',
          coordinates: '', // 初始为空，后续通过API获取
          timeWindow: ['09:00', '12:00'] as [string, string],
          weight: 50,
          weightUnit: 'kg' as const,
          errors: [],
          status: DeliveryPointStatus.APPROVED
        },
        {
          id: 2,
          address: '中国石油大学(华东)行政楼',
          coordinates: '', // 初始为空，后续通过API获取
          timeWindow: ['10:00', '14:00'] as [string, string],
          weight: 30,
          weightUnit: 'kg' as const,
          errors: [],
          status: DeliveryPointStatus.APPROVED
        },
        {
          id: 3,
          address: '中国石油大学(华东)体育馆',
          coordinates: '', // 初始为空，后续通过API获取
          timeWindow: ['13:00', '16:00'] as [string, string],
          weight: 20,
          weightUnit: 'kg' as const,
          errors: [],
          status: DeliveryPointStatus.APPROVED
        }
      ]
      
      deliveryPoints.value = defaultPoints
      startAddress.value = '中国石油大学(华东)行政楼'
      startPosition.value = '' // 初始为空，后续通过API获取
      
      // 立即通过高德地图API获取所有坐标
      await Promise.all([
        // 获取起点坐标
        (async () => {
          const result = await geocode(startAddress.value, '青岛市')
          if (result.status === '1' && result.geocodes.length > 0) {
            startPosition.value = result.geocodes[0].location
          }
        })(),
        // 获取所有配送点坐标
        ...deliveryPoints.value.map(async (point, index) => {
          const result = await geocode(point.address, '青岛市')
          if (result.status === '1' && result.geocodes.length > 0) {
            deliveryPoints.value[index].coordinates = result.geocodes[0].location
          }
        })
      ])
    }
    
    // 验证所有配送点
    validateAllDeliveryPoints()
    
    // 然后获取可用模型列表
    const models = await getAvailableModels()
    availableModels.value = models
    
    // 默认选择第一个模型（如果有）
    if (models.length > 0) {
      selectedModel.value = models[0].key
    }
  } catch (error) {
    console.error('组件初始化失败:', error)
    ElMessage.error('组件初始化失败，请刷新页面重试')
  }
})

// 开始推理
const startInference = async () => {
  // 验证输入
  if (!canStartInference.value) {
    ElMessage.error('请检查输入信息是否完整有效')
    return
  }
  
  try {
    inferenceLoading.value = true
    
    // 调用API进行路径规划
    const result = await inferRoute({
      start_position: startPointArray.value!,
      delivery_points: deliveryPointsForApi.value,
      algorithm: selectedAlgorithm.value,
      model_key: selectedAlgorithm.value === 'ppo' ? selectedModel.value : undefined
    })
    
    inferenceResult.value = result
    ElMessage.success('路径规划完成')
  } catch (error) {
    console.error('路径规划失败:', error)
    
    // 提供更详细的错误信息
    let errorMsg = '路径规划失败，请检查输入或网络连接'
    if (error instanceof Error) {
      errorMsg = `路径规划失败: ${error.message}`
    } else if (typeof error === 'object' && error !== null && 'message' in error) {
      errorMsg = `路径规划失败: ${String(error.message)}`
    }
    
    ElMessage.error(errorMsg)
  } finally {
    inferenceLoading.value = false
  }
}</script>

<style scoped>
.inference-panel {
  max-width: 100%;
}

.inference-content {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 2rem;
  margin-top: 1.5rem;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-actions h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #303133;
}

.refresh-btn {
  background-color: #409EFF;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
}

.refresh-btn:hover {
  background-color: #66B1FF;
}

.refresh-btn:active {
  background-color: #337ECC;
}

.config-panel {
  background-color: #f5f5f5;
  padding: 1.5rem;
  border-radius: 8px;
  max-height: 80vh;
  overflow-y: auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header label {
  font-weight: 600;
  margin-bottom: 0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.form-group input,
.form-group select,
.form-group .el-autocomplete,
.form-group .el-time-picker {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

/* 为el-input-number单独设置样式，避免影响内部布局 */
.form-group .el-input-number {
  width: 100%;
  font-size: 1rem;
}

.error-message {
  color: #f44336;
  font-size: 0.8rem;
  margin-top: 0.25rem;
  display: block;
}

.delivery-points {
  margin-bottom: 1rem;
}

.delivery-point-item {
  margin-bottom: 1rem;
  padding: 1rem;
  background-color: white;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.delivery-point-field {
  margin-bottom: 0.75rem;
}

.delivery-point-field:last-child {
  margin-bottom: 0;
}

.delivery-point-field label {
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  font-weight: normal;
}

.time-window {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.time-window .el-time-picker {
  flex: 1;
}

.time-separator {
  margin: 0 0.5rem;
  color: #666;
}

.weight-input {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.weight-input .el-input-number {
  flex: 1;
}

/* 修改货物重量输入框的数字字体颜色 */
.weight-input .el-input-number .el-input__inner {
  color: #0056b3; /* 深蓝色，符合WCAG对比度标准 */
  font-weight: 500;
}

.unit-select {
  width: 80px;
}

.add-btn, .remove-btn, .start-btn {
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.add-btn {
  background-color: #4CAF50;
  color: white;
  width: auto;
  padding: 0.5rem 1rem;
}

.add-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.remove-btn {
  background-color: #f44336;
  color: white;
  width: 100%;
  margin-top: 0.75rem;
  padding: 0.5rem 1rem;
}

.start-btn {
  background-color: #2196F3;
  color: white;
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  margin-top: 1rem;
  transition: all 0.3s ease;
}

.start-btn:hover:not(:disabled) {
  background-color: #1976D2;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.start-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(33, 150, 243, 0.2);
}

.start-btn:disabled {
  background-color: #cccccc;
  color: #666666;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
  box-shadow: none;
}

.limit-warning {
  color: #f44336;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  text-align: center;
}

/* 批量导入样式 */
.excel-import-section {
  margin-top: 0.75rem;
}

.excel-import-actions {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.excel-import {
  position: relative;
  display: inline-block;
}

.file-input {
  position: absolute;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.import-btn,
.template-btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s;
}

.import-btn {
  background-color: #409eff;
  color: white;
}

.import-btn:hover {
  background-color: #66b1ff;
}

.template-btn {
  background-color: #67c23a;
  color: white;
}

.template-btn:hover {
  background-color: #85ce61;
}

.file-status {
  font-size: 0.9rem;
  color: #606266;
  margin-bottom: 1rem;
}

/* Excel预览样式 */
.excel-preview {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #fafafa;
}

.excel-preview h4 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #303133;
}

.preview-table-container {
  overflow-x: auto;
  margin-bottom: 1rem;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
}

.preview-table th,
.preview-table td {
  padding: 0.75rem;
  text-align: left;
  border: 1px solid #ebeef5;
}

.preview-table th {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
}

.preview-table td {
  font-size: 0.9rem;
  color: #606266;
}

.error-row {
  background-color: #fff3f3;
}

.status-error {
  color: #f44336;
  font-weight: 500;
}

.status-success {
  color: #67c23a;
  font-weight: 500;
}

/* 导入预览操作按钮 */
.import-preview-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.cancel-preview-btn,
.confirm-import-btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s;
}

.cancel-preview-btn {
  background-color: #909399;
  color: white;
}

.cancel-preview-btn:hover {
  background-color: #a6a9ad;
}

.confirm-import-btn {
  background-color: #67c23a;
  color: white;
}

.confirm-import-btn:hover {
  background-color: #85ce61;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 1rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.map-panel {
  display: flex;
  flex-direction: column;
}

.map-container {
  width: 100%;
  height: 600px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.result-panel {
  background-color: #f5f5f5;
  padding: 1.5rem;
  border-radius: 8px;
}

.result-panel h3 {
  margin-top: 0;
  margin-bottom: 1rem;
}

.result-info p {
  margin-bottom: 0.5rem;
}

.result-info ol {
  margin: 0.5rem 0 0 1.5rem;
}

.result-info li {
  margin-bottom: 0.25rem;
}

/* 配送点错误信息样式 */
.delivery-point-errors {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background-color: #fff3f3;
  border-radius: 4px;
  border-left: 4px solid #f44336;
}

.delivery-point-errors ul {
  margin: 0;
  padding-left: 1.25rem;
}

.delivery-point-errors li {
  color: #f44336;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.delivery-point-errors li:last-child {
  margin-bottom: 0;
}

/* 自定义Element Plus组件样式 */
:deep(.el-autocomplete),
:deep(.el-time-picker),
:deep(.el-input-number),
:deep(.el-select) {
  width: 100%;
}

:deep(.el-input__inner) {
  border-radius: 4px;
}

:deep(.el-time-spinner__wrapper) {
  width: 50% !important;
}

:deep(.el-input-group__append) {
  padding: 0 10px;
}
</style>
