#!/bin/bash

# Raspberry Pi Deployment Setup Script for Boat Dashboard
# Run this script on your Raspberry Pi after copying the files

echo "🚤 Raspberry Pi Boat Dashboard Deployment Setup"
echo "=============================================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python dependencies
echo "🐍 Installing Python packages..."
sudo apt install -y python3-pip python3-venv python3-dev

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    git \
    cmake \
    build-essential \
    pkg-config \
    libjpeg-dev \
    libtiff5-dev \
    libjasper-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libcanberra-gtk-module \
    libatlas-base-dev \
    gfortran \
    python3-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    libqt5gui5 \
    libqt5webkit5 \
    libqt5test5 \
    python3-pyqt5

# Create virtual environment
echo "🏠 Setting up virtual environment..."
cd /home/pi/boat-dashboard
python3 -m venv boat_env
source boat_env/bin/activate

# Install Python packages
echo "📋 Installing Python dependencies..."
pip install --upgrade pip
pip install \
    websockets \
    opencv-python-headless \
    numpy \
    psutil \
    pyserial \
    adafruit-circuitpython-ina3221 \
    adafruit-blinka \
    adafruit-circuitpython-mpu6050 \
    RPi.GPIO \
    gpiozero \
    pigpio

# Enable GPIO and camera interfaces
echo "🔌 Enabling GPIO and Camera..."
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_serial 0

# Enable pigpio daemon
echo "🎛️ Setting up pigpio daemon..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# Set permissions for GPIO
echo "🔐 Setting GPIO permissions..."
sudo usermod -a -G gpio pi
sudo usermod -a -G dialout pi

# Create systemd service
echo "🔄 Creating systemd service..."
sudo tee /etc/systemd/system/boat-dashboard.service > /dev/null <<EOF
[Unit]
Description=Boat Dashboard Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/boat-dashboard
Environment=PATH=/home/pi/boat-dashboard/boat_env/bin
ExecStart=/home/pi/boat-dashboard/boat_env/bin/python server/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
echo "🚀 Enabling boat dashboard service..."
sudo systemctl daemon-reload
sudo systemctl enable boat-dashboard.service

# Create log directory
echo "📝 Setting up logging..."
mkdir -p logs
mkdir -p samples

# Set proper permissions
echo "🔒 Setting file permissions..."
chmod +x boat_env/bin/activate
chmod 644 config/settings.json
chmod 755 server/*.py

echo ""
echo "✅ Deployment setup complete!"
echo ""
echo "🔧 Manual steps required:"
echo "1. Connect your hardware (GPS, IMU, Camera, Motors, Pumps, Servos)"
echo "2. Verify GPIO pin assignments in config/settings.json"
echo "3. Test camera: 'raspistill -o test.jpg'"
echo "4. Test GPS connection: 'sudo cat /dev/serial0'"
echo "5. Start the service: 'sudo systemctl start boat-dashboard'"
echo "6. Check status: 'sudo systemctl status boat-dashboard'"
echo "7. View logs: 'sudo journalctl -u boat-dashboard -f'"
echo ""
echo "🌐 Web Interface will be available at:"
echo "   http://RASPBERRY_PI_IP:8000"
echo "   (Replace RASPBERRY_PI_IP with your Pi's actual IP address)"
echo ""
echo "📱 To find your Pi's IP address: 'hostname -I'"