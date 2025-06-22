# Monitor Agent

Лёгкий агент мониторинга для Orange Pi и других устройств на базе Linux.

## Установка на Orange Pi

1. **Клонирование репозитория**
   ```bash
   git clone https://github.com/your-username/monitor-agent.git
   cd monitor-agent
   ```
2. **Запуск скрипта установки**
   ```bash
   chmod +x install.sh
   sudo ./install.sh your_device_id
   ```
   Скрипт автоматически:
   
   - Установит необходимые системные пакеты.
   - Создаст и активирует виртуальное окружение Python.
   - Установит зависимости (psutil, requests и др.).
   - Сконфигурирует config.ini с вашим device_id и server_url.
   - Настроит и запустит systemd-сервис monitor-agent.

## Конфигурация агента
После установки проверьте файл /opt/monitor-agent/config.ini:

```ini
[Agent]
# Уникальный идентификатор устройства
device_id = your_device_id

# URL вашего сервера с REST API
server_url = http://<SERVER_IP>:8000/api/metrics

# Интервал сбора метрик, в секундах
interval = 60
```

## Управление systemd-сервисом
```bash
# Проверить статус агента
sudo systemctl status monitor-agent

# Перезапустить агент
sudo systemctl restart monitor-agent

# Остановить агент
sudo systemctl stop monitor-agent

# Просмотреть логи агента
sudo journalctl -u monitor-agent -f
```

## API Endpoints

- `POST /api/metrics` - получение метрик от агента
- `