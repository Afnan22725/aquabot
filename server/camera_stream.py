# Camera capture handling
import cv2
from picamera2 import Picamera2

class CameraStream:
    def __init__(self):
        self.camera = Picamera2()
        config = self.camera.create_preview_configuration(
            main={"format": "RGB888", "size": (640, 480)}
        )
        self.camera.configure(config)
        self.camera.start()
        
    def capture_frame(self):
        """Capture a frame from the camera"""
        try:
            return self.camera.capture_array()
        except Exception as e:
            print(f"Camera error: {e}")
            return None
            
    def cleanup(self):
        """Clean up camera resources"""
        self.camera.stop()