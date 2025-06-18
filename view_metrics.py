from database import SessionLocal, Metric, Device, User
from datetime import datetime, timedelta
import pandas as pd

def get_metrics(hours=24):
    db = SessionLocal()
    try:
        # Получаем метрики за последние N часов
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        metrics = db.query(Metric).filter(Metric.timestamp >= time_threshold).all()
        
        # Преобразуем в DataFrame для удобного просмотра
        data = []
        for m in metrics:
            # Получаем информацию об устройстве
            device = db.query(Device).filter(Device.id == m.device_id).first()
            device_name = device.device_id if device else f"Device_{m.device_id}"
            
            data.append({
                'device_id': device_name,
                'timestamp': m.timestamp,
                'cpu_percent': m.cpu_percent,
                'ram_percent': m.ram_percent,
                'disk_percent': m.disk_percent,
                'net_in_mb': round(m.net_in_bytes / (1024 * 1024), 2),
                'net_out_mb': round(m.net_out_bytes / (1024 * 1024), 2)
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            print("\nПоследние метрики:")
            print(df.tail())
            
            print("\nСтатистика по CPU:")
            print(df.groupby('device_id')['cpu_percent'].agg(['mean', 'max', 'min']))
            
            print("\nСтатистика по RAM:")
            print(df.groupby('device_id')['ram_percent'].agg(['mean', 'max', 'min']))
        else:
            print("Нет данных за указанный период")
            
    finally:
        db.close()

def get_devices_info():
    db = SessionLocal()
    try:
        devices = db.query(Device).all()
        print("\nЗарегистрированные устройства:")
        for device in devices:
            user = db.query(User).filter(User.id == device.user_id).first()
            print(f"- {device.device_name} (ID: {device.device_id}, Владелец: {user.username})")
            
    finally:
        db.close()

if __name__ == "__main__":
    get_devices_info()
    get_metrics() 