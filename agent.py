#!/usr/bin/env python3
import os
import time
import json
import hashlib
import psutil
import requests
import configparser

# --- Загрузка конфигурации ---
cfg = configparser.ConfigParser()
cfg.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
conf = cfg['Agent']

DEVICE_ID  = conf.get('device_id')
SERVER_URL = conf.get('server_url')
INTERVAL   = conf.getint('interval', fallback=60)

if not DEVICE_ID or not SERVER_URL:
    raise RuntimeError("config.ini must define [Agent]device_id and server_url")

def collect_metrics():
    # CPU и RAM
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    # Диск (корневая файловая система)
    disk = psutil.disk_io_counters()
    # Для упрощения: абсолютные байты за интервал
    # Сохраним текущие накопленные счётчики, потом вычтем
    # Здесь просто показано использование %
    disk_usage = psutil.disk_usage('/').percent
    # Сеть: дельты байт за интервал
    net_before = psutil.net_io_counters()
    time.sleep(INTERVAL - 1)  # уже спали 1 сек для cpu_percent
    net_after = psutil.net_io_counters()
    net_in  = net_after.bytes_recv - net_before.bytes_recv
    net_out = net_after.bytes_sent - net_before.bytes_sent

    return {
        'cpu_percent': round(cpu, 2),
        'ram_percent': round(ram_percent, 2),
        'disk_percent': round(disk_usage, 2),
        'net_in_bytes': net_in,
        'net_out_bytes': net_out,
        'timestamp': int(time.time())
    }

def send(metrics: dict):
    # Сериализуем и хешируем
    payload_json = json.dumps(metrics, sort_keys=True)
    hash_value = hashlib.sha256(payload_json.encode()).hexdigest()
    # Собираем тело запроса
    body = {
        'device_id': DEVICE_ID,
        'metrics': metrics,
        'hash': hash_value
    }
    try:
        r = requests.post(SERVER_URL, json=body, timeout=10)
        r.raise_for_status()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sent OK, hash={hash_value}")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Send failed: {e}")

def main():
    print(f"Agent started: device_id={DEVICE_ID}, server={SERVER_URL}, interval={INTERVAL}s")
    while True:
        metrics = collect_metrics()
        send(metrics)

if __name__ == '__main__':
    main()
