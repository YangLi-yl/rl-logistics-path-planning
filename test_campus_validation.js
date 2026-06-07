// Test script to verify campus boundary validation logic

// Haversine formula function (same as in the application)
function toRadians(degrees) {
  return degrees * Math.PI / 180;
}

function calculateDistance(lat1, lng1, lat2, lng2) {
  const R = 6371000; // Earth radius in meters
  const φ1 = toRadians(lat1);
  const φ2 = toRadians(lat2);
  const Δφ = toRadians(lat2 - lat1);
  const Δλ = toRadians(lng2 - lng1);

  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c; // Distance in meters
}

// Campus center coordinates
const campusCenter = { lng: 120.3945, lat: 36.0665 };
console.log('中国石油大学华东校区中心坐标:', campusCenter);
console.log('----------------------------------------');

// Test points
const testPoints = [
  // Inside campus
  { name: '图书馆', lng: 120.3975, lat: 36.0675, expected: 'valid' },
  { name: '行政楼', lng: 120.3925, lat: 36.0655, expected: 'valid' },
  { name: '体育馆', lng: 120.3960, lat: 36.0630, expected: 'valid' },
  
  // Boundary points (approx 1km)
  { name: '边界测试点1', lng: 120.4055, lat: 36.0665, expected: 'valid' }, // East boundary
  { name: '边界测试点2', lng: 120.3835, lat: 36.0665, expected: 'valid' }, // West boundary
  { name: '边界测试点3', lng: 120.3945, lat: 36.0755, expected: 'valid' }, // North boundary
  { name: '边界测试点4', lng: 120.3945, lat: 36.0575, expected: 'valid' }, // South boundary
  
  // Outside campus (>1km)
  { name: '校外测试点1', lng: 120.4065, lat: 36.0665, expected: 'invalid' }, // East of boundary
  { name: '校外测试点2', lng: 120.3825, lat: 36.0665, expected: 'invalid' }, // West of boundary
  { name: '校外测试点3', lng: 120.3945, lat: 36.0765, expected: 'invalid' }, // North of boundary
  { name: '校外测试点4', lng: 120.3945, lat: 36.0565, expected: 'invalid' }, // South of boundary
  { name: '青岛大学', lng: 120.4682, lat: 36.0632, expected: 'invalid' } // Far outside
];

// Test each point
testPoints.forEach((point, index) => {
  const distance = calculateDistance(point.lat, point.lng, campusCenter.lat, campusCenter.lng);
  const isWithinRange = distance <= 1000;
  const status = isWithinRange ? 'valid' : 'invalid';
  const result = status === point.expected ? '✓ PASS' : '✗ FAIL';
  
  console.log(`${index + 1}. ${point.name}`);
  console.log(`   坐标: ${point.lng.toFixed(6)},${point.lat.toFixed(6)}`);
  console.log(`   距离中心: ${Math.round(distance)}米`);
  console.log(`   状态: ${status}, 预期: ${point.expected}`);
  console.log(`   结果: ${result}`);
  console.log('----------------------------------------');
});

// Calculate exact 1km boundary coordinates
console.log('精确1公里边界坐标计算:');
const bearing = [0, 90, 180, 270]; // North, East, South, West
bearing.forEach(b => {
  const θ = toRadians(b);
  const d = 1000; // 1km
  const R = 6371000;
  
  const φ1 = toRadians(campusCenter.lat);
  const λ1 = toRadians(campusCenter.lng);
  
  const φ2 = Math.asin(Math.sin(φ1) * Math.cos(d / R) +
                        Math.cos(φ1) * Math.sin(d / R) * Math.cos(θ));
  const λ2 = λ1 + Math.atan2(Math.sin(θ) * Math.sin(d / R) * Math.cos(φ1),
                             Math.cos(d / R) - Math.sin(φ1) * Math.sin(φ2));
  
  const lng2 = (λ2 * 180 / Math.PI + 540) % 360 - 180;
  const lat2 = φ2 * 180 / Math.PI;
  
  console.log(`${b}°方向边界点: ${lng2.toFixed(6)},${lat2.toFixed(6)}`);
});