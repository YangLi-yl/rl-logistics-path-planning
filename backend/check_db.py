import sqlite3

conn = sqlite3.connect('upc_campus_logistics.db')
cursor = conn.cursor()

# 检查表结构
print('planning_history表结构:')
cursor.execute('PRAGMA table_info(planning_history)')
for row in cursor.fetchall():
    print(f'字段ID: {row[0]}, 字段名: {row[1]}, 数据类型: {row[2]}, 是否为空: {row[3]}, 默认值: {row[4]}, 主键: {row[5]}')

# 测试插入一条简单记录
try:
    print('\n测试插入简单记录...')
    cursor.execute('''
    INSERT INTO planning_history (
        id, start_time, start_position, delivery_points, algorithm, model_key, 
        vehicle_type, delivery_order, total_distance_km, total_distance_m, 
        estimated_time_min, success, error, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'test123',
        '2026-01-16 00:00:00.000000',
        '[120.0, 36.0]',
        '[]',
        'greedy',
        None,
        'small',
        '[0]',
        0.0,
        0.0,
        0.0,
        1,
        None,
        '2026-01-16 00:00:00.000000',
        '2026-01-16 00:00:00.000000'
    ))
    conn.commit()
    print('插入成功!')
    
    # 删除测试记录
    cursor.execute('DELETE FROM planning_history WHERE id = ?', ('test123',))
    conn.commit()
    print('测试记录已删除')
except Exception as e:
    print(f'插入失败: {e}')
    conn.rollback()

conn.close()
