# Гайд по установке на Orange Pi 3B

## 1. Подготовка Orange Pi

### 1.1 Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Установка необходимых пакетов
```bash
sudo apt install -y python3 python3-pip python3-venv git postgresql postgresql-contrib
```

## 2. Настройка PostgreSQL

### 2.1 Запуск PostgreSQL
```bash
# Запуск сервиса
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Проверка статуса
sudo systemctl status postgresql
```

### 2.2 Создание базы данных и пользователя
```bash
# Переключение на пользователя postgres
sudo -u postgres psql

# В консоли PostgreSQL выполните:
CREATE DATABASE monitoring;
CREATE USER monitoring WITH PASSWORD 'monitoring';
GRANT ALL PRIVILEGES ON DATABASE monitoring TO monitoring;
\q
```

### 2.3 Проверка подключения
```bash
# Подключение к базе данных
psql -U monitoring -d monitoring -h localhost

# В консоли PostgreSQL проверьте:
\l
\dt
\q
```

## 3. Установка агента мониторинга

### 3.1 Клонирование репозитория
```bash
git clone https://github.com/valuncilh/monitor-agent.git
cd monitor-agent
```

### 3.2 Создание виртуального окружения
```bash
python3 -m venv env
source env/bin/activate
```

### 3.3 Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3.4 Настройка конфигурации
```bash
# Создание .env файла
echo "DATABASE_URL=postgresql://monitoring:monitoring@localhost:5432/monitoring" > .env

# Редактирование config.ini
nano config.ini
```

Содержимое `config.ini`:
```ini
[Agent]
device_id = orange_pi_001
server_url = http://localhost:8000/api/metrics
interval = 60
```

## 4. Создание таблиц в базе данных

### 4.1 Инициализация базы данных
```bash
# Запуск скрипта инициализации
python init_database.py
```

### 4.2 Проверка создания таблиц
```bash
psql -U monitoring -d monitoring -c "\dt"
```

Вы должны увидеть таблицы:
- `users` - пользователи системы
- `devices` - устройства для мониторинга
- `metrics` - метрики устройств

### 4.3 Структура таблиц
```sql
-- Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблица устройств
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    device_name VARCHAR NOT NULL,
    device_id VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблица метрик
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    cpu_percent FLOAT NOT NULL,
    ram_percent FLOAT NOT NULL,
    disk_percent FLOAT NOT NULL,
    net_in_bytes BIGINT NOT NULL,
    net_out_bytes BIGINT NOT NULL
);
```

## 5. Запуск сервера мониторинга

### 5.1 Запуск сервера
```bash
# В виртуальном окружении
python main.py
```

### 5.2 Проверка работы сервера
```bash
# Проверка доступности API
curl http://localhost:8000/api/metrics

# Проверка документации API
curl http://localhost:8000/docs

# Проверка устройств
curl http://localhost:8000/api/devices

# Проверка пользователей
curl http://localhost:8000/api/users
```

## 6. Настройка агента как системного сервиса

### 6.1 Создание systemd сервиса
```bash
sudo tee /etc/systemd/system/monitor-agent.service << EOF
[Unit]
Description=Monitoring Agent
After=network.target postgresql.service

[Service]
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/env/bin"
ExecStart=$(pwd)/env/bin/python agent.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

### 6.2 Запуск сервиса
```bash
sudo systemctl daemon-reload
sudo systemctl enable monitor-agent
sudo systemctl start monitor-agent
```

### 6.3 Проверка статуса
```bash
sudo systemctl status monitor-agent
```

## 7. Проверка сбора данных

### 7.1 Просмотр логов агента
```bash
journalctl -u monitor-agent -f
```

### 7.2 Проверка данных в базе
```bash
# Подключение к базе данных
psql -U monitoring -d monitoring

# Просмотр пользователей
SELECT * FROM users;

# Просмотр устройств
SELECT d.device_name, d.device_id, u.username 
FROM devices d 
JOIN users u ON d.user_id = u.id;

# Просмотр последних метрик
SELECT 
    d.device_id,
    m.timestamp,
    m.cpu_percent,
    m.ram_percent,
    m.disk_percent
FROM metrics m
JOIN devices d ON m.device_id = d.id
ORDER BY m.timestamp DESC 
LIMIT 5;

# Статистика по устройствам
SELECT 
    d.device_id,
    AVG(m.cpu_percent) as avg_cpu,
    AVG(m.ram_percent) as avg_ram,
    COUNT(*) as total_records
FROM metrics m
JOIN devices d ON m.device_id = d.id
GROUP BY d.device_id;

\q
```

### 7.3 Использование скрипта просмотра
```bash
python view_metrics.py
```

## 8. Настройка веб-интерфейса

### 8.1 Открытие порта (если нужно)
```bash
sudo ufw allow 8000/tcp
```

### 8.2 Доступ к веб-интерфейсу
Откройте в браузере:
```
http://IP_АДРЕС_ORANGE_PI:8000/docs
```

### 8.3 API endpoints для проверки:
- `GET /api/metrics` - все метрики
- `GET /api/metrics/{device_id}` - метрики конкретного устройства
- `GET /api/devices` - список устройств
- `GET /api/users` - список пользователей
- `POST /api/metrics` - получение метрик от агента

## 9. Мониторинг и обслуживание

### 9.1 Просмотр логов
```bash
# Логи агента
journalctl -u monitor-agent -f

# Логи PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### 9.2 Резервное копирование базы данных
```bash
# Создание бэкапа
pg_dump -U monitoring monitoring > backup_$(date +%Y%m%d).sql

# Восстановление
psql -U monitoring monitoring < backup_20240318.sql
```

### 9.3 Перезапуск сервисов
```bash
# Перезапуск агента
sudo systemctl restart monitor-agent

# Перезапуск PostgreSQL
sudo systemctl restart postgresql
```

## 10. Устранение неполадок

### 10.1 Проверка подключения к базе данных
```bash
# Тест подключения
psql -U monitoring -d monitoring -c "SELECT version();"
```

### 10.2 Проверка прав доступа
```bash
# Проверка прав пользователя
sudo -u postgres psql -c "\du"
```

### 10.3 Проверка сетевого подключения
```bash
# Проверка доступности API
curl -v http://localhost:8000/api/metrics
```

### 10.4 Просмотр ошибок в логах
```bash
# Системные логи
sudo journalctl -xe

# Логи конкретного сервиса
sudo journalctl -u monitor-agent -n 50
```

### 10.5 Пересоздание базы данных
```bash
# Если нужно пересоздать базу данных
sudo -u postgres psql -c "DROP DATABASE IF EXISTS monitoring;"
sudo -u postgres psql -c "CREATE DATABASE monitoring;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monitoring TO monitoring;"

# Запуск инициализации
python init_database.py
``` 