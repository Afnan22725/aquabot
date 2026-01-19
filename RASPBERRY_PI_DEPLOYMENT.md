# Raspberry Pi Deployment Checklist

## ✅ **Code Compatibility Status**

### **🟢 READY FOR RASPBERRY PI**
All code is already compatible with Raspberry Pi OS (Linux):

1. **✅ Path Handling**: Uses `os.path.join()` and Unix-style paths
2. **✅ GPIO Libraries**: Uses RPi.GPIO and pigpio (Pi-specific)
3. **✅ Serial Communication**: Uses `/dev/serial0` for GPS
4. **✅ System Monitoring**: Reads from `/sys/class/thermal/thermal_zone0/temp`
5. **✅ File Operations**: Standard Python file I/O
6. **✅ Network**: WebSocket server on all interfaces (0.0.0.0)
7. **✅ Signal Handling**: Unix signals (SIGTERM, SIGINT)
8. **✅ Async/Await**: Modern Python asyncio

### **🔧 Hardware Configuration (Raspberry Pi)**
```json
{
  "pins": {
    "motor_left": 18,        // PWM GPIO 18
    "motor_right": 19,       // PWM GPIO 19
    "pumps": [17, 27, 22, 23], // Digital GPIO pins
    "camera_pan": 12,        // PWM GPIO 12 (servo)
    "camera_tilt": 13        // PWM GPIO 13 (servo)
  },
  "gps": {
    "port": "/dev/serial0",  // Pi UART port
    "baudrate": 9600
  }
}
```

## 🚀 **Deployment Instructions**

### **Step 1: Copy Files to Raspberry Pi**
```bash
scp -r boat-dashboard/ pi@YOUR_PI_IP:/home/pi/
```

### **Step 2: Run Deployment Script**
```bash
ssh pi@YOUR_PI_IP
cd /home/pi/boat-dashboard
chmod +x deploy_pi.sh
./deploy_pi.sh
```

### **Step 3: Hardware Connections**
- **GPS Module** → UART (TX to GPIO 14, RX to GPIO 15)
- **IMU (MPU6050)** → I2C (SDA to GPIO 2, SCL to GPIO 3)
- **Battery Monitor (INA3221)** → I2C (same bus as IMU)
- **Camera** → CSI connector
- **ESCs/Motors** → PWM pins 18, 19
- **Water Pumps** → GPIO pins 17, 27, 22, 23 (via relays)
- **Camera Servos** → PWM pins 12, 13

### **Step 4: Enable Interfaces**
```bash
sudo raspi-config
# Enable: Camera, SPI, I2C, Serial Port
```

### **Step 5: Test & Start Service**
```bash
# Test manually
cd /home/pi/boat-dashboard
source boat_env/bin/activate
python server/main.py

# Or start as service
sudo systemctl start boat-dashboard
sudo systemctl status boat-dashboard
```

## 🌐 **Access Web Interface**
- Open browser: `http://RASPBERRY_PI_IP:8000`
- Default port: 8000
- Accessible from any device on same network

## 📋 **Pre-Flight Checklist**

### **Hardware Verification**
- [ ] GPS module connected and getting fix
- [ ] Camera module detected (`raspistill -o test.jpg`)
- [ ] IMU responding on I2C bus (`i2cdetect -y 1`)
- [ ] Battery monitor connected
- [ ] ESCs calibrated and motors responsive
- [ ] Water pumps/relays wired correctly
- [ ] Servo motors moving smoothly

### **Software Verification**
- [ ] All Python dependencies installed
- [ ] GPIO permissions set correctly
- [ ] pigpio daemon running
- [ ] WebSocket server starts without errors
- [ ] Web interface loads properly
- [ ] Telemetry data updating in dashboard

### **Network & Remote Access**
- [ ] Pi connected to WiFi/Ethernet
- [ ] Port 8000 accessible from client devices
- [ ] SSH access working for remote troubleshooting
- [ ] Consider setting up VPN for internet access

## 🔍 **Troubleshooting**

### **Common Issues & Solutions**

**GPS Not Working**
```bash
# Check GPS connection
sudo cat /dev/serial0
# Should show NMEA sentences

# Enable serial in boot config
sudo nano /boot/config.txt
# Add: enable_uart=1
```

**Camera Not Detected**
```bash
# Test camera
raspistill -o test.jpg
vcgencmd get_camera

# Enable camera interface
sudo raspi-config
```

**GPIO Permission Denied**
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi
sudo usermod -a -G dialout pi
# Logout and login again
```

**Service Won't Start**
```bash
# Check service status
sudo systemctl status boat-dashboard
sudo journalctl -u boat-dashboard -f

# Check Python environment
source boat_env/bin/activate
python server/main.py
```

## 📊 **Performance Optimization**

### **For Better Performance**
1. **Increase GPU memory**: `gpu_mem=128` in `/boot/config.txt`
2. **Overclock safely**: Use `raspi-config` for modest overclock
3. **Reduce video resolution** if needed for bandwidth
4. **Monitor CPU temperature** during operation
5. **Use fast SD card** (Class 10 or better)

### **Power Management**
- Use quality power supply (5V 3A minimum)
- Consider UPS/battery backup for boat deployment
- Monitor power consumption with INA3221
- Implement low-power mode if needed

## 🔧 **Customization Options**

### **Pin Configuration**
Edit `config/settings.json` to match your hardware setup

### **Network Settings**
- Change WebSocket port in settings
- Configure WiFi access point mode for direct connection
- Set up port forwarding for internet access

### **Data Logging**
- Samples stored in `samples/` directory
- CSV and JSON formats supported
- GeoJSON export for GIS software

The code is fully ready for Raspberry Pi deployment! 🎉