# System monitoring
import os
import time
import psutil

class SystemStatus:
    def __init__(self):
        self.start_time = time.time()
        
    def get_status(self):
        """Get system status information"""
        try:
            # CPU temperature
            temp = None
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = round(float(f.read()) / 1000, 1)
            except:
                temp = None
                
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Uptime
            uptime = time.time() - self.start_time
            hours, remainder = divmod(uptime, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
            
            return {
                'cpu_temp': temp,
                'cpu_usage': cpu_percent,
                'memory_usage': memory_percent,
                'disk_usage': disk_percent,
                'uptime': uptime_str
            }
            
        except Exception as e:
            print(f"System status error: {e}")
            return None