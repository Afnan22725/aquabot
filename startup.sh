#!/bin/bash

# Boat Dashboard Startup Script
# This script handles initialization and startup of the boat dashboard server

BOAT_DIR="/home/pi/boat-dashboard"
VENV_DIR="$BOAT_DIR/boat_env"
SERVER_SCRIPT="$BOAT_DIR/server/main.py"
LOG_FILE="/var/log/boat-dashboard.log"
PID_FILE="/var/run/boat-dashboard.pid"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | sudo tee -a $LOG_FILE
}

# Function to check if pigpiod is running
check_pigpiod() {
    if ! pgrep -x "pigpiod" > /dev/null; then
        log_message "Starting pigpiod daemon..."
        sudo pigpiod
        sleep 2
    fi
}

# Function to wait for network
wait_for_network() {
    log_message "Waiting for network connectivity..."
    while ! ping -c 1 google.com &> /dev/null; do
        sleep 5
    done
    log_message "Network is available"
}

# Function to check hardware connections
check_hardware() {
    log_message "Checking hardware connections..."
    
    # Check I2C devices
    i2cdevices=$(i2cdetect -y 1 2>/dev/null | grep -E "[0-9a-f]{2}" | wc -l)
    log_message "Found $i2cdevices I2C devices"
    
    # Check serial ports
    if [ -e "/dev/serial0" ]; then
        log_message "GPS serial port available"
    else
        log_message "WARNING: GPS serial port not found"
    fi
    
    # Check camera
    if vcgencmd get_camera 2>/dev/null | grep -q "detected=1"; then
        log_message "Camera detected"
    else
        log_message "WARNING: Camera not detected"
    fi
}

# Function to start the boat server
start_boat_server() {
    log_message "Starting boat dashboard server..."
    
    cd $BOAT_DIR
    
    # Activate virtual environment and start server
    source $VENV_DIR/bin/activate
    python $SERVER_SCRIPT &
    
    # Store PID
    echo $! > $PID_FILE
    log_message "Boat server started with PID $(cat $PID_FILE)"
}

# Main startup sequence
main() {
    log_message "=== Boat Dashboard Startup ==="
    
    # Wait a bit for system to fully boot
    sleep 10
    
    # Wait for network
    wait_for_network
    
    # Check and start required services
    check_pigpiod
    
    # Hardware checks
    check_hardware
    
    # Start the boat server
    start_boat_server
    
    log_message "Startup sequence completed"
}

# Run main function
main