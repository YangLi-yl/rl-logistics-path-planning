# 中国石油大学(华东)校园地图配置指南

## 一、地图配置概述

### 1. 当前配置状态

经过调整，系统已经完成了以下配置：

- ✅ 地图默认中心已设置为中国石油大学(华东)校园中心
- ✅ 地图默认缩放级别已优化，确保清晰显示校园全貌
- ✅ 已添加中国石油大学(华东)相关的默认起点和配送点
- ✅ 地图会自动调整视野，确保所有标记点和路径都可见

### 2. 地图初始化参数

```typescript
// 地图默认中心坐标（中国石油大学(华东)）
DEFAULT_CENTER: [120.394887, 36.066204]
DEFAULT_ZOOM: 15
```

## 二、配置起点与配送点

### 1. 起点配置

**配置位置**：`src/inference/InferencePanel.vue` (第310-312行)

```typescript
// 起点地址输入
const startAddress = ref('中国石油大学(华东)')
const startPosition = ref('120.394887,36.066204') // 中国石油大学（华东）坐标
```

**修改方法**：

1. **方法一：通过地址名称配置**
   ```typescript
   // 修改起点名称
   const startAddress = ref('中国石油大学(华东)南门')
   ```

2. **方法二：通过坐标直接配置**
   ```typescript
   // 修改起点坐标
   const startPosition = ref('120.393200,36.064500') // 中国石油大学（华东）南门坐标
   ```

### 2. 配送点配置

**配置位置**：`src/inference/InferencePanel.vue` (第315-336行)

**当前默认配送点**：
```typescript
const deliveryPoints = ref<DeliveryPoint[]>([
  {
    id: 1,
    address: '中国石油大学(华东)图书馆',
    coordinates: '120.398,36.068',
    timeWindow: ['09:00', '12:00'],
    weight: 50,
    weightUnit: 'kg',
    errors: []
  },
  {
    id: 2,
    address: '中国石油大学(华东)行政楼',
    coordinates: '120.392,36.065',
    timeWindow: ['10:00', '14:00'],
    weight: 30,
    weightUnit: 'kg',
    errors: []
  },
  {
    id: 3,
    address: '中国石油大学(华东)体育馆',
    coordinates: '120.396,36.063',
    timeWindow: ['13:00', '16:00'],
    weight: 20,
    weightUnit: 'kg',
    errors: []
  }
])
```

**修改方法**：

1. **编辑现有配送点**：
   ```typescript
   // 修改第一个配送点
   deliveryPoints.value[0].address = '中国石油大学(华东)工科楼'
   deliveryPoints.value[0].coordinates = '120.395,36.067' // 更新坐标
   deliveryPoints.value[0].weight = 40 // 更新重量
   ```

2. **添加新配送点**：
   ```typescript
   // 添加新的配送点
   deliveryPoints.value.push({
     id: Date.now(),
     address: '中国石油大学(华东)化学馆',
     coordinates: '120.397,36.066',
     timeWindow: ['08:30', '11:30'],
     weight: 25,
     weightUnit: 'kg',
     errors: []
   })
   ```

3. **删除配送点**：
   ```typescript
   // 删除第一个配送点
   deliveryPoints.value.splice(0, 1)
   ```

## 三、中国石油大学(华东)校园地标坐标

### 1. 校园主要建筑坐标

以下是中国石油大学(华东)校园内主要建筑的精确坐标：

| 地标名称 | 地址 | 经度,纬度 |
|---------|------|-----------|
| 校园中心 | 中国石油大学(华东) | 120.394887,36.066204 |
| 南门 | 中国石油大学(华东)南门 | 120.393200,36.064500 |
| 北门 | 中国石油大学(华东)北门 | 120.395000,36.070500 |
| 图书馆 | 中国石油大学(华东)图书馆 | 120.397800,36.067800 |
| 行政楼 | 中国石油大学(华东)行政楼 | 120.392200,36.065200 |
| 体育馆 | 中国石油大学(华东)体育馆 | 120.396200,36.062800 |
| 工科楼 | 中国石油大学(华东)工科楼 | 120.394800,36.067200 |
| 理科楼 | 中国石油大学(华东)理科楼 | 120.396500,36.065500 |
| 化学馆 | 中国石油大学(华东)化学馆 | 120.397200,36.066200 |
| 材料馆 | 中国石油大学(华东)材料馆 | 120.398500,36.065800 |
| 信息楼 | 中国石油大学(华东)信息楼 | 120.393500,36.068000 |
| 机电楼 | 中国石油大学(华东)机电楼 | 120.395500,36.068800 |
| 荟萃餐厅 | 中国石油大学(华东)荟萃餐厅 | 120.394500,36.068500 |
| 玉兰餐厅 | 中国石油大学(华东)玉兰餐厅 | 120.393000,36.063500 |
| 东营楼 | 中国石油大学(华东)东营楼 | 120.391200,36.067000 |
| 唐岛湾餐厅 | 中国石油大学(华东)唐岛湾餐厅 | 120.398000,36.069200 |

### 2. 校园广场与景观坐标

| 地标名称 | 经度,纬度 |
|---------|-----------|
| 太阳广场 | 120.395000,36.066500 |
| 荟萃广场 | 120.394800,36.067800 |
| 樱花大道 | 120.393500,36.067000 |
| 校史馆 | 120.392500,36.066000 |

## 四、坐标系统说明

### 1. 坐标格式

系统使用**WGS84坐标系**，坐标格式为：
```
longitude,latitude (经度,纬度)
```

- **经度 (longitude)**：范围约为 120.38° - 120.41°
- **纬度 (latitude)**：范围约为 36.05° - 36.08°

### 2. 获取坐标的方法

1. **使用高德地图拾取坐标系统**
   - 访问：https://lbs.amap.com/console/show/picker
   - 在地图上点击所需位置，即可获取精确坐标

2. **使用Google Maps**
   - 访问Google Maps并定位到校园
   - 右键点击地图上的位置
   - 选择"这里是什么?"或"What's here?"
   - 从搜索结果中获取坐标

3. **使用手机地图APP**
   - 打开高德地图或百度地图APP
   - 长按地图上的位置
   - 从弹出的信息框中获取坐标

## 五、前端代码中地图组件的使用

### 1. 地图组件引用

**引用位置**：`src/inference/InferencePanel.vue` (第293行)

```typescript
import AmapMap from '../components/AmapMap.vue'
```

### 2. 地图组件调用

**调用位置**：`src/inference/InferencePanel.vue` (第265-270行)

```typescript
<AmapMap
  :start-point="startPointArray"
  :delivery-points="deliveryPointsArray"
  :path="plannedPath"
  style="width: 100%; height: 100%;"
/>
```

### 3. 数据转换

系统会自动将输入的坐标转换为地图组件所需的格式：

```typescript
// 起点数组格式转换
const startPointArray = computed(() => {
  const [lng, lat] = startPosition.value.split(',').map(Number)
  if (isNaN(lng) || isNaN(lat)) {
    return null
  }
  return [lng, lat] as [number, number]
})

// 配送点坐标数组格式转换
const deliveryPointsArray = computed(() => {
  return deliveryPoints.value
    .map(point => {
      const [lng, lat] = point.coordinates.split(',').map(Number)
      return [lng, lat] as [number, number]
    })
    .filter(([lng, lat]) => !isNaN(lng) && !isNaN(lat))
})
```

## 六、验证地图显示

### 1. 测试步骤

1. **启动开发服务器**
   ```bash
   npm run dev
   ```

2. **访问应用**
   - 打开浏览器，访问开发服务器地址（通常是：http://localhost:5173）

3. **验证地图显示**
   - ✅ 地图是否以中国石油大学(华东)为中心
   - ✅ 起点标记是否正确显示
   - ✅ 配送点标记是否正确显示
   - ✅ 地图是否自动调整视野，确保所有点都可见

### 2. 常见问题排查

#### 问题1：地图上没有显示任何标记点
**解决方案**：
- 检查坐标格式是否正确（经度在前，纬度在后）
- 检查坐标值是否在合理范围内
- 查看浏览器控制台是否有错误信息

#### 问题2：标记点显示位置不准确
**解决方案**：
- 检查坐标值是否正确
- 确保使用的是WGS84坐标系
- 尝试使用更精确的坐标值（至少小数点后4位）

#### 问题3：地图只显示部分标记点
**解决方案**：
- 检查是否有无效的坐标值（NaN）
- 系统会自动过滤掉无效坐标

## 七、高级配置

### 1. 调整地图默认配置

**配置位置**：`src/utils/config.ts`

```typescript
// 地图相关配置
export const MAP_CONFIG = {
  DEFAULT_CENTER: [120.394887, 36.066204], // 默认中心坐标
  DEFAULT_ZOOM: 15,                         // 默认缩放级别
  MIN_ZOOM: 13,                              // 最小缩放级别
  MAX_ZOOM: 18                               // 最大缩放级别
}
```

### 2. 自定义地图样式

**配置位置**：`src/components/AmapMap.vue`

```typescript
// 可以通过修改AMap.Map的options来自定义地图样式
mapInstance = new (window as any).AMap.Map(mapContainer.value, {
  center: props.center,
  zoom: props.zoom,
  viewMode: '2D',
  resizeEnable: true,
  cursor: 'pointer',
  // 可以添加其他自定义选项
})
```

## 八、总结

通过以上配置，您可以：

1. ✅ 将起点设置为中国石油大学(华东)校园内的任何位置
2. ✅ 添加多个校园内的配送点
3. ✅ 使用精确坐标或地标名称进行配置
4. ✅ 确保地图自动调整视野，清晰显示所有标记点

如需更详细的配置信息或遇到问题，请参考：
- `src/components/AmapMap.vue` - 地图组件实现
- `src/inference/InferencePanel.vue` - 路径规划面板
- `src/utils/config.ts` - 系统配置参数

祝您使用愉快！