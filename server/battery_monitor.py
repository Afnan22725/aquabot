# INA3221 power monitoring
import board
import busio

class BatteryMonitor:
    def __init__(self):
        self.ina = None
        try:
            from adafruit_ina3221 import INA3221
            i2c = busio.I2C(board.SCL, board.SDA)
            self.ina = INA3221(i2c)
        except ImportError:
            print("INA3221 library not available")
        except Exception as e:
            print(f"INA3221 init error: {e}")
    
    def lifepo4_percentage(self, voltage):
        """Calculate LiFePO4 battery percentage from voltage"""
        table = [
            (13.6, 100),
            (13.4, 95),
            (13.3, 90),
            (13.2, 80),
            (13.1, 70),
            (13.0, 60),
            (12.9, 50),
            (12.8, 40),
            (12.7, 30),
            (12.6, 20),
            (12.4, 10),
            (12.0, 0)
        ]

        if voltage >= 13.6:
            return 100
        if voltage <= 12.0:
            return 0

        for i in range(len(table) - 1):
            v1, p1 = table[i]
            v2, p2 = table[i + 1]

            if v2 <= voltage <= v1:
                # Linear interpolation
                return int(p2 + (voltage - v2) * (p1 - p2) / (v1 - v2))

        return 0
            
    def read(self):
        """Read battery data with LiFePO4 percentage calculation"""
        if not self.ina:
            # Return simulated data for testing
            return {
                'voltage': 13.2,
                'percentage': 80,
                'status': 'Good'
            }
            
        try:
            # Read voltage from INA3221 (channel 1)
            voltage = self.ina.bus_voltage
            
            # Calculate battery percentage using LiFePO4 curve
            percentage = self.lifepo4_percentage(voltage)
            
            # Determine battery status
            if percentage >= 60:
                status = 'Good'
            elif percentage >= 30:
                status = 'Fair'
            elif percentage >= 10:
                status = 'Low'
            else:
                status = 'Critical'
            
            return {
                'voltage': round(voltage, 2),
                'percentage': percentage,
                'status': status
            }
        except Exception as e:
            print(f"Battery read error: {e}")
            return None