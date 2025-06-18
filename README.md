# Monitor Agent

Система мониторинга для Orange Pi и других устройств на базе Linux.

## Установка на Orange Pi

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/monitor-agent.git
cd monitor-agent
```

2. Запустите скрипт установки:
```bash
chmod +x install.sh
./install.sh
```

Скрипт установки выполнит:
- Установку необходимых системных пакетов
- Настройку PostgreSQL
- Создание виртуального окружения Python
- Установку зависимостей
- Настройку systemd сервиса

## Конфигурация

1. Настройте подключение к базе данных в файле `.env`:
```
DATABASE_URL=postgresql://monitoring:monitoring@localhost:5432/monitoring
```

2. Настройте параметры агента в `config.ini`:
```ini
[Agent]
device_id = your_device_id
server_url = http://your-server:8000/api/metrics
interval = 60
```

## Запуск сервера мониторинга

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

## API Endpoints

- `POST /api/metrics` - получение метрик от агента
- `GET /api/metrics` - получение всех метрик
- `GET /api/metrics/{device_id}` - получение метрик конкретного устройства

## Управление сервисом

```bash
# Статус сервиса
sudo systemctl status monitor-agent

# Перезапуск сервиса
sudo systemctl restart monitor-agent

# Остановка сервиса
sudo systemctl stop monitor-agent

# Просмотр логов
journalctl -u monitor-agent
``` 