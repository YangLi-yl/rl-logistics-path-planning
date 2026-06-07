// 测试配送点坐标验证

// 中国石油大学华东校区中心坐标
const campusCenter = { lng: 120.3945, lat: 36.0665 };

// 测试配送点
const deliveryPoints = [
  { name: '图书馆', coordinates: '120.3975,36.0675' },
  { name: '行政楼', coordinates: '120.3925,36.0655' },
  { name: '体育馆', coordinates: '120.3960,36.0630' },
  { name: '边界内', coordinates: '120.3865,36.0665' }, // 约860米
  { name: '边界上', coordinates: '120.3855,36.0665' }, // 约1000米
  { name: '边界外', coordinates: '120.3845,36.0665' }  // 约1100米
];

// 测试 Haversine 公式实现
function testHaversine() {
  console.log('=== Haversine 公式测试 ===');
  
  const toRadians = (degrees) => degrees * Math.PI / 180;
  
  deliveryPoints.forEach(point => {
    const [lng, lat] = point.coordinates.split(',').map(Number);
    
    const R = 6371000; // 地球半径（米）
    const φ1 = toRadians(lat);
    const φ2 = toRadians(campusCenter.lat);
    const Δφ = toRadians(campusCenter.lat - lat);
    const Δλ = toRadians(campusCenter.lng - lng);
    
    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    
    const distance = R * c;
    const isValid = distance <= 1000;
    
    console.log(`${point.name}: ${point.coordinates}`);
    console.log(`  距离中心: ${Math.round(distance)} 米`);
    console.log(`  验证结果: ${isValid ? '有效' : '无效'}`);
    console.log();
  });
}

// 测试坐标解析
function testCoordinateParsing() {
  console.log('=== 坐标解析测试 ===');
  
  deliveryPoints.forEach(point => {
    const [lng, lat] = point.coordinates.split(',').map(Number);
    
    console.log(`${point.name}: ${point.coordinates}`);
    console.log(`  解析结果: lng=${lng}, lat=${lat}`);
    console.log(`  是否有效: ${!isNaN(lng) && !isNaN(lat)}`);
    console.log();
  });
}

// 运行测试
testCoordinateParsing();
testHaversine();
