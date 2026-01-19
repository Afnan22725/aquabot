import serial
import re
import time

class GPSReader:
    def __init__(self, config):
        self.serial_port = config['port']
        self.baudrate = config['baudrate']
        self.serial = None
        self.connect()
        
    def connect(self):
        """Connect to GPS serial port"""
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
                
            self.serial = serial.Serial(
                self.serial_port,
                baudrate=self.baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            print(f"GPS connected to {self.serial_port} at {self.baudrate} baud")
            time.sleep(2)  # Allow time for GPS to initialize
            return True
            
        except Exception as e:
            print(f"GPS connection error: {e}")
            self.serial = None
            return False
            
    def read(self):
        """Read and parse GPS data"""
        if not self.serial or not self.serial.is_open:
            if not self.connect():
                return None
                
        try:
            # Read multiple lines to increase chance of getting valid data
            for _ in range(10):
                line = self.serial.readline().decode('ascii', errors='ignore').strip()
                if line.startswith(('$GPGGA', '$GNGGA')):
                    return self.parse_gpgga(line)
                    
            return None  # No valid GPGGA sentence found
            
        except Exception as e:
            print(f"GPS read error: {e}")
            # Attempt to reconnect on error
            self.connect()
            return None
            
    def parse_gpgga(self, data):
        """Parse GPGGA NMEA sentence with better error handling"""
        try:
            parts = data.split(',')
            
            # Check if we have a valid fix (field 6)
            if len(parts) < 10 or parts[6] == '0':
                return {'fix': False, 'satellites': 0}
                
            # Parse latitude
            lat_raw = parts[2]
            if not lat_raw:
                return {'fix': False}
                
            lat_deg = float(lat_raw[:2])
            lat_min = float(lat_raw[2:])
            latitude = lat_deg + (lat_min / 60)
            if parts[3] == 'S':
                latitude *= -1
                
            # Parse longitude
            lon_raw = parts[4]
            if not lon_raw:
                return {'fix': False}
                
            lon_deg = float(lon_raw[:3])
            lon_min = float(lon_raw[3:])
            longitude = lon_deg + (lon_min / 60)
            if parts[5] == 'W':
                longitude *= -1
                
            # Parse other data
            altitude = float(parts[9]) if parts[9] else 0
            satellites = int(parts[7]) if parts[7] else 0
            
            return {
                'lat': round(latitude, 6),
                'lon': round(longitude, 6),
                'alt': round(altitude, 1),
                'satellites': satellites,
                'fix': True
            }
            
        except (ValueError, IndexError) as e:
            print(f"GPS parse error in data '{data}': {e}")
            return {'fix': False}
            
    def cleanup(self):
        """Clean up GPS resources"""
        if self.serial and self.serial.is_open:
            self.serial.close()
