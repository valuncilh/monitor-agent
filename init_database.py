#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных с тестовыми данными
"""

from database import SessionLocal, User, Device, init_db
from datetime import datetime

def create_test_data():
    """Создание тестовых пользователей и устройств"""
    db = SessionLocal()
    
    try:
        # Создание тестового пользователя
        test_user = User(
            username="test_user",
            full_name="Test User"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Создание тестового устройства
        test_device = Device(
            user_id=test_user.id,
            device_name="Orange Pi 3B",
            device_id="orange_pi_001"
        )
        db.add(test_device)
        db.commit()
        
        print("✅ Тестовые данные созданы успешно!")
        print(f"Пользователь: {test_user.username} (ID: {test_user.id})")
        print(f"Устройство: {test_device.device_name} (ID: {test_device.device_id})")
        
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых данных: {e}")
        db.rollback()
    finally:
        db.close()

def check_database():
    """Проверка структуры базы данных"""
    db = SessionLocal()
    
    try:
        # Проверка таблиц
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        print("\n📋 Структура базы данных:")
        for table in tables:
            print(f"- {table}")
            
        # Проверка данных
        users_count = db.query(User).count()
        devices_count = db.query(Device).count()
        
        print(f"\n📊 Количество записей:")
        print(f"- Пользователей: {users_count}")
        print(f"- Устройств: {devices_count}")
        
    except Exception as e:
        print(f"❌ Ошибка при проверке базы данных: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Инициализация базы данных...")
    
    # Создание таблиц
    init_db()
    print("✅ Таблицы созданы")
    
    # Проверка структуры
    check_database()
    
    # Создание тестовых данных
    create_test_data()
    
    print("\n🎉 Инициализация завершена!") 