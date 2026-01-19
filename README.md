# Boat Dashboard

# FPV Smart Boat System

A Raspberry Pi-powered smart boat system with live video streaming, GPS tracking, sensor monitoring, and remote control capabilities.

## Features

- **Live FPV Video Streaming**: Real-time video feed from Pi Camera
- **GPS Tracking**: Real-time location tracking with Leaflet.js map
- **Sensor Monitoring**: IMU (MPU6050) and battery (INA3221) data
- **Remote Control**: Web-based motor and pump control
- **Water Sampling**: GPS-logged water samples with relay-controlled pumps
- **3D Visualization**: Three.js boat model with IMU-based orientation
- **System Monitoring**: CPU temperature, memory usage, and uptime

## Hardware Requirements

- Raspberry Pi 3/4
- Pi Camera Module
- GPS Module (serial)
- MPU6050 IMU Sensor
- INA3221 Power Monitor
- ESC Motors (x2)
- Relay Module (4-channel)
- Water Pumps (x4)
- 4G Modem (for remote access)

## Installation

1. Clone the repository to your Raspberry Pi
2. Install required Python packages: