# MPU6050 sensor reading
import board
import busio
from mpu6050 import mpu6050

class IMUReader:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.mpu = mpu6050(0x68)
        
    def read(self):
        """Read IMU data"""
        try:
            accel = self.mpu.get_accel_data()
            gyro = self.mpu.get_gyro_data()
            temp = self.mpu.get_temp()
            
            return {
                'accel': {
                    'x': round(accel['x'], 2),
                    'y': round(accel['y'], 2),
                    'z': round(accel['z'], 2)
                },
                'gyro': {
                    'x': round(gyro['x'], 2),
                    'y': round(gyro['y'], 2),
                    'z': round(gyro['z'], 2)
                },
                'temp': round(temp, 1)
            }
        except Exception as e:
            print(f"IMU read error: {e}")
            return None