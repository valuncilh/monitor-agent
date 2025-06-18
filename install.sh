#!/bin/bash
# install.sh — автоматическая установка мониторингового агента

set -e

# --- 1. Аргумент: device_id ---
DEVICE_ID="$1"
if [ -z "$DEVICE_ID" ]; then
  echo "Usage: $0 <DEVICE_ID>"
  exit 1
fi
echo "Installing monitor-agent with DEVICE_ID=$DEVICE_ID"

# --- 2. Зависимости ---
echo "Updating apt and installing dependencies..."
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-venv git \
     python3-psutil python3-requests postgresql postgresql-contrib

# --- 3. Клонирование репозитория ---
REPO_URL="https://github.com/youruser/monitor-agent.git"
INSTALL_DIR="/opt/monitor-agent"
echo "Cloning $REPO_URL into $INSTALL_DIR..."
sudo git clone "$REPO_URL" "$INSTALL_DIR"

# --- 4. Настройка конфига ---
echo "Configuring device_id in config.ini..."
sudo cp "$INSTALL_DIR/config.ini.example" "$INSTALL_DIR/config.ini"
sudo sed -i "s/REPLACE_WITH_DEVICE_ID/$DEVICE_ID/" "$INSTALL_DIR/config.ini"

# --- 5. Установка службы ---
echo "Installing systemd service..."
sudo cp "$INSTALL_DIR/monitor-agent.service" /etc/systemd/system/

# Создание базы данных
echo "Creating database..."
sudo -u postgres psql -c "CREATE DATABASE monitoring;"
sudo -u postgres psql -c "CREATE USER monitoring WITH PASSWORD 'monitoring';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monitoring TO monitoring;"

# Создание виртуального окружения
echo "Creating virtual environment..."
python3 -m venv env
source env/bin/activate

# Установка зависимостей
echo "Installing dependencies..."
pip install -r "$INSTALL_DIR/requirements.txt"

# Перезагрузка systemd и запуск сервиса
echo "Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable monitor-agent.service
sudo systemctl start monitor-agent.service

echo "Installation completed."
echo "Use: sudo systemctl status monitor-agent.service"
echo "     sudo journalctl -u monitor-agent.service -f"
