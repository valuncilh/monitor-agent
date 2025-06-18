# Полное руководство по развертыванию системы мониторинга

## 1. Подготовка сервера (где будет база данных и веб-интерфейс)

### 1.1 Установка необходимого ПО
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Установка Python и зависимостей
sudo apt install -y python3 python3-pip python3-venv
```

### 1.2 Настройка PostgreSQL
```bash
# Создание базы данных и пользователя
sudo -u postgres psql -c "CREATE DATABASE monitoring;"
sudo -u postgres psql -c "CREATE USER monitoring WITH PASSWORD 'monitoring';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monitoring TO monitoring;"
```

### 1.3 Настройка файрвола
```bash
# Открываем порт для веб-интерфейса
sudo ufw allow 8000/tcp
```

## 2. Развертывание сервера мониторинга

### 2.1 Клонирование репозитория
```bash
git clone https://github.com/your-username/monitor-agent.git
cd monitor-agent
```

### 2.2 Настройка окружения
```bash
# Создание виртуального окружения
python3 -m venv env
source env/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
echo "DATABASE_URL=postgresql://monitoring:monitoring@localhost:5432/monitoring" > .env
```

### 2.3 Настройка systemd сервиса
```bash
# Создание сервиса
sudo tee /etc/systemd/system/monitor-server.service << EOF
[Unit]
Description=Monitoring Server
After=network.target postgresql.service

[Service]
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/env/bin"
ExecStart=$(pwd)/env/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Запуск сервиса
sudo systemctl daemon-reload
sudo systemctl enable monitor-server
sudo systemctl start monitor-server
```

## 3. Развертывание агента на Orange Pi

### 3.1 Подготовка Orange Pi
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv git
```

### 3.2 Установка агента
```bash
# Клонирование репозитория
git clone https://github.com/your-username/monitor-agent.git
cd monitor-agent

# Запуск скрипта установки
chmod +x install.sh
./install.sh
```

### 3.3 Настройка агента
```bash
# Редактирование конфигурации
nano config.ini
```
```ini
[Agent]
device_id = orange_pi_001
server_url = http://your-server-ip:8000/api/metrics
interval = 60
```

## 4. Проверка работоспособности

### 4.1 Проверка сервера
```bash
# Проверка статуса сервиса
sudo systemctl status monitor-server

# Просмотр логов
journalctl -u monitor-server -f
```

### 4.2 Проверка агента
```bash
# Проверка статуса сервиса
sudo systemctl status monitor-agent

# Просмотр логов
journalctl -u monitor-agent -f
```

### 4.3 Проверка получения данных
```bash
# Запуск скрипта просмотра метрик
python view_metrics.py
```

## 5. Доступ к веб-интерфейсу

### 5.1 Прямой доступ
Откройте в браузере:
```
http://your-server-ip:8000/docs
```

### 5.2 Проверка API
```bash
# Получение всех метрик
curl http://your-server-ip:8000/api/metrics

# Получение метрик конкретного устройства
curl http://your-server-ip:8000/api/metrics/orange_pi_001
```

## 6. Резервное копирование

### 6.1 Создание бэкапа
```bash
# Бэкап базы данных
pg_dump -U monitoring monitoring > backup_$(date +%Y%m%d).sql

# Бэкап конфигурации
tar -czf config_backup_$(date +%Y%m%d).tar.gz config.ini .env
```

### 6.2 Восстановление
```bash
# Восстановление базы данных
psql -U monitoring monitoring < backup_20240318.sql

# Восстановление конфигурации
tar -xzf config_backup_20240318.tar.gz
```

## 7. Мониторинг системы

### 7.1 Проверка логов
```bash
# Логи сервера
tail -f /var/log/syslog | grep monitor-server

# Логи агента
tail -f /var/log/syslog | grep monitor-agent
```

### 7.2 Проверка метрик
```bash
# Запуск скрипта просмотра
python view_metrics.py
```

## 8. Устранение неполадок

### 8.1 Проверка подключения
```bash
# Проверка доступности сервера
curl -v http://your-server-ip:8000/api/metrics

# Проверка PostgreSQL
psql -U monitoring -d monitoring -c "SELECT count(*) FROM metrics;"
```

### 8.2 Перезапуск сервисов
```bash
# Перезапуск сервера
sudo systemctl restart monitor-server

# Перезапуск агента
sudo systemctl restart monitor-agent
```

## 9. Обновление системы

### 9.1 Обновление сервера
```bash
cd monitor-agent
git pull
source env/bin/activate
pip install -r requirements.txt
sudo systemctl restart monitor-server
```

### 9.2 Обновление агента
```bash
cd monitor-agent
git pull
source env/bin/activate
pip install -r requirements.txt
sudo systemctl restart monitor-agent
``` 