import sqlite3

# 连接到数据库
conn = sqlite3.connect('upc_campus_logistics.db')
cursor = conn.cursor()

# 检查planning_history表是否存在start_time列
try:
    cursor.execute("PRAGMA table_info(planning_history)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print("当前表结构:")
    for col in columns:
        print(f"- {col}")
    
    # 如果缺少start_time列，添加它
    if 'start_time' not in columns:
        print("\n正在添加start_time列...")
        cursor.execute("ALTER TABLE planning_history ADD COLUMN start_time TEXT")
        conn.commit()
        print("成功添加start_time列!")
    else:
        print("\nstart_time列已经存在")
        
    # 检查其他可能缺失的列
    required_columns = ['start_time', 'vehicle_type', 'model_key', 'total_distance_km', 'success', 'error']
    for col in required_columns:
        if col not in columns:
            print(f"\n正在添加{col}列...")
            if col == 'vehicle_type':
                cursor.execute("ALTER TABLE planning_history ADD COLUMN vehicle_type TEXT")
            elif col == 'model_key':
                cursor.execute("ALTER TABLE planning_history ADD COLUMN model_key TEXT")
            elif col == 'total_distance_km':
                cursor.execute("ALTER TABLE planning_history ADD COLUMN total_distance_km REAL")
            elif col == 'success':
                cursor.execute("ALTER TABLE planning_history ADD COLUMN success INTEGER")
            elif col == 'error':
                cursor.execute("ALTER TABLE planning_history ADD COLUMN error TEXT")
            conn.commit()
            print(f"成功添加{col}列!")
            columns.append(col)
    
    print("\n修复后的表结构:")
    for col in columns:
        print(f"- {col}")
        
except Exception as e:
    print(f"错误: {e}")
finally:
    conn.close()
    print("\n数据库修复完成")
