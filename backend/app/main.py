from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
import datetime
import json
import sqlite3
import traceback
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../model')))

# 导入推理模块
from inference.model_infer import CampusLogisticsInfer

app = FastAPI(title="校园物流配送系统", description="路径规划推理API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化推理引擎
infer_engine = CampusLogisticsInfer()

# 数据库连接
DB_PATH = os.path.join(os.path.dirname(__file__), '../upc_campus_logistics.db')

def get_db_connection():
    return sqlite3.connect(DB_PATH)

# 创建表的函数
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 先删除旧表（如果存在）
    cursor.execute('DROP TABLE IF EXISTS planning_history')
    
    # 创建路径规划历史表
    cursor.execute('''
    CREATE TABLE planning_history (
        id TEXT PRIMARY KEY,
        start_time TEXT,
        start_position TEXT,
        delivery_points TEXT,
        algorithm TEXT,
        model_key TEXT,
        vehicle_type TEXT,
        delivery_order TEXT,
        total_distance_km REAL,
        total_distance_m REAL,
        estimated_time_min REAL,
        success INTEGER,
        error TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

# 创建表
create_tables()

from pydantic import BaseModel, Field

class DeliveryPoint(BaseModel):
    lon: float = Field(..., description="经度")
    lat: float = Field(..., description="纬度")
    weight: float = Field(..., description="货物重量")
    time_window: list[int] = Field(..., description="时间窗 [开始分钟, 结束分钟]")

class InferenceRequest(BaseModel):
    start_position: list[float] = Field(..., description="起点坐标 [经度, 纬度]")
    delivery_points: list[DeliveryPoint] = Field(..., description="配送点列表")
    algorithm: str = Field(default="greedy", description="路径规划算法")
    model_key: str = Field(default=None, description="模型键")
    vehicle_type: str = Field(default="small", description="车型")

@app.post("/api/inference")
async def inference(request: InferenceRequest):
    """路径规划推理接口"""
    start_position = request.start_position
    delivery_points = request.delivery_points
    algorithm = request.algorithm
    model_key = request.model_key
    vehicle_type = request.vehicle_type
    try:
        # 记录请求开始时间
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        request_id = str(uuid.uuid4())
        
        print(f"\n[请求ID: {request_id}] 开始处理路径规划请求")
        print(f"起点: {start_position}")
        print(f"配送点数量: {len(delivery_points)}")
        print(f"算法: {algorithm}")
        print(f"车型: {vehicle_type}")
        
        # 转换输入数据格式
        formatted_points = []
        for point in delivery_points:
            formatted_points.append({
                "lon": point.lon,
                "lat": point.lat,
                "weight": point.weight,
                "time_window": (point.time_window[0], point.time_window[1])
            })
        
        # 调用推理引擎
        result = infer_engine.infer_path(
            start_position=start_position,
            delivery_points=formatted_points,
            algorithm=algorithm
        )
        
        print(f"推理结果: {result}")
        
        # 准备响应数据
        response_data = {
            "success": True,
            "delivery_order": result["delivery_order"],
            "total_distance": result["total_distance_m"],
            "total_time": result["estimated_time_min"]
        }
        
        # 保存到数据库
        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        
        # 将Pydantic模型转换为字典以便JSON序列化
        delivery_points_dict = [point.model_dump() for point in delivery_points]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 插入历史记录
        cursor.execute('''
        INSERT INTO planning_history (
            id, start_time, start_position, delivery_points, algorithm, model_key, 
            vehicle_type, delivery_order, total_distance_km, total_distance_m, 
            estimated_time_min, success, error, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request_id,
            start_time,
            json.dumps(start_position),
            json.dumps(delivery_points_dict),
            algorithm,
            model_key,
            vehicle_type,
            json.dumps(result["delivery_order"]),
            float(result["total_distance_km"]),  # 转换为Python原生float
            float(result["total_distance_m"]),  # 转换为Python原生float
            float(result["estimated_time_min"]),  # 转换为Python原生float
            1,  # success
            None,  # error
            created_at,
            created_at
        ))
        
        conn.commit()
        conn.close()
        
        print(f"[请求ID: {request_id}] 请求处理完成")
        
        return response_data
        
    except Exception as e:
        # 处理错误
        error_msg = str(e)
        traceback.print_exc()
        
        # 保存错误到数据库
        end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 处理变量的存在性和序列化
            start_pos_json = json.dumps(start_position) if 'start_position' in locals() else '[]'
            
            # 处理delivery_points的序列化
            if 'delivery_points' in locals() and delivery_points:
                if hasattr(delivery_points[0], 'model_dump'):
                    # 是Pydantic模型
                    delivery_points_dict = [point.model_dump() for point in delivery_points]
                    delivery_points_json = json.dumps(delivery_points_dict)
                else:
                    # 已经是字典
                    delivery_points_json = json.dumps(delivery_points)
            else:
                delivery_points_json = '[]'
            
            cursor.execute('''
            INSERT INTO planning_history (
                id, start_time, start_position, delivery_points, algorithm, model_key, 
                vehicle_type, delivery_order, total_distance_km, total_distance_m, 
                estimated_time_min, success, error, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                start_pos_json,
                delivery_points_json,
                algorithm if 'algorithm' in locals() else 'unknown',
                model_key if 'model_key' in locals() else None,
                vehicle_type if 'vehicle_type' in locals() else 'unknown',
                json.dumps([]),
                0.0,
                0.0,
                0.0,
                0,  # success
                error_msg,
                created_at,
                created_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as db_error:
            print(f"保存错误到数据库失败: {db_error}")
        
        raise HTTPException(status_code=500, detail={
            "success": False,
            "error": error_msg,
            "message": "请求处理失败"
        })

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

@app.get("/")
async def root():
    """应用根路径"""
    return {
        "app": "校园物流配送系统",
        "version": "1.0.0",
        "description": "基于强化学习的智能路径规划系统",
        "api_endpoints": {
            "health": "/api/health",
            "inference": "/api/inference"
        },
        "status": "running",
        "timestamp": datetime.datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
