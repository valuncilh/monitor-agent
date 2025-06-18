from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
from datetime import datetime
import json
import hashlib
from sqlalchemy.orm import Session
from database import get_db, Metrics, init_db

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
    
    # Создаем запись в базе данных
    metrics_entry = Metrics(
        device_id=data.device_id,
        cpu_percent=data.metrics['cpu_percent'],
        ram_percent=data.metrics['ram_percent'],
        disk_percent=data.metrics['disk_percent'],
        net_in_bytes=data.metrics['net_in_bytes'],
        net_out_bytes=data.metrics['net_out_bytes'],
        timestamp=datetime.fromtimestamp(data.metrics['timestamp'])
    )
    
    db.add(metrics_entry)
    db.commit()
    db.refresh(metrics_entry)
    
    return {"status": "success", "message": "Metrics received"}

@app.get("/api/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    return db.query(Metrics).all()

@app.get("/api/metrics/{device_id}")
async def get_device_metrics(device_id: str, db: Session = Depends(get_db)):
    return db.query(Metrics).filter(Metrics.device_id == device_id).all()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 