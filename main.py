from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
from datetime import datetime
import json
import hashlib
from sqlalchemy.orm import Session
from database import get_db, Metric, Device, User, init_db

app = FastAPI(title="Monitoring Server")

class MetricsData(BaseModel):
    device_id: str
    metrics: Dict[str, Any]
    hash: str

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/api/metrics")
async def receive_metrics(data: MetricsData, db: Session = Depends(get_db)):
    # Проверка хеша
    payload_json = json.dumps(data.metrics, sort_keys=True)
    calculated_hash = hashlib.sha256(payload_json.encode()).hexdigest()
    
    if calculated_hash != data.hash:
        raise HTTPException(status_code=400, detail="Invalid hash")
    
    # Находим устройство по device_id
    device = db.query(Device).filter(Device.device_id == data.device_id).first()
    
    if not device:
        # Создаем тестового пользователя и устройство если их нет
        user = db.query(User).filter(User.username == "default_user").first()
        if not user:
            user = User(username="default_user", full_name="Default User")
            db.add(user)
            db.commit()
            db.refresh(user)
        
        device = Device(
            user_id=user.id,
            device_name=f"Device {data.device_id}",
            device_id=data.device_id
        )
        db.add(device)
        db.commit()
        db.refresh(device)
    
    # Создаем запись метрик
    metric_entry = Metric(
        device_id=device.id,
        timestamp=datetime.fromtimestamp(data.metrics['timestamp']),
        cpu_percent=data.metrics['cpu_percent'],
        ram_percent=data.metrics['ram_percent'],
        disk_percent=data.metrics['disk_percent'],
        net_in_bytes=data.metrics['net_in_bytes'],
        net_out_bytes=data.metrics['net_out_bytes']
    )
    
    db.add(metric_entry)
    db.commit()
    db.refresh(metric_entry)
    
    return {"status": "success", "message": "Metrics received"}

@app.get("/api/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    return db.query(Metric).all()

@app.get("/api/metrics/{device_id}")
async def get_device_metrics(device_id: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return db.query(Metric).filter(Metric.device_id == device.id).all()

@app.get("/api/devices")
async def get_devices(db: Session = Depends(get_db)):
    return db.query(Device).all()

@app.get("/api/users")
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 