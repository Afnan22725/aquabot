import pigpio
import time
from threading import Lock

class ServoController:
    def __init__(self, pin_config):
        self.pi = pigpio.pi()
        
        if not self.pi.connected:
            raise RuntimeError("Failed to connect to pigpio daemon. Is 'pigpiod' running?")
        
        self.pan_pin = pin_config.get('camera_pan', 12)  # GPIO12 default
        self.tilt_pin = pin_config.get('camera_tilt', 13)  # GPIO13 default
        
        # Servo angle limits (0-180 degrees)
        self.pan_angle = 90   # Center position
        self.tilt_angle = 90  # Center position
        self.min_angle = 0
        self.max_angle = 180
        
        # Servo PWM pulse width range (500-2500 microseconds)
        self.min_pulse = 500
        self.max_pulse = 2500
        
        # Thread safety
        self.lock = Lock()
        
        # Setup pins
        self.pi.set_mode(self.pan_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.tilt_pin, pigpio.OUTPUT)
        
        # Initialize servos to center position
        self.set_angles(self.pan_angle, self.tilt_angle)
        
    def angle_to_pulse_width(self, angle):
        """Convert servo angle (0-180) to pulse width (500-2500μs)"""
        if angle < self.min_angle:
            angle = self.min_angle
        elif angle > self.max_angle:
            angle = self.max_angle
            
        pulse_range = self.max_pulse - self.min_pulse
        angle_range = self.max_angle - self.min_angle
        pulse_width = self.min_pulse + (angle / angle_range) * pulse_range
        return int(pulse_width)
    
    def set_pan_angle(self, angle):
        """Set pan servo angle"""
        with self.lock:
            if self.min_angle <= angle <= self.max_angle:
                self.pan_angle = angle
                pulse_width = self.angle_to_pulse_width(angle)
                self.pi.set_servo_pulsewidth(self.pan_pin, pulse_width)
                return True
            return False
    
    def set_tilt_angle(self, angle):
        """Set tilt servo angle"""
        with self.lock:
            if self.min_angle <= angle <= self.max_angle:
                self.tilt_angle = angle
                pulse_width = self.angle_to_pulse_width(angle)
                self.pi.set_servo_pulsewidth(self.tilt_pin, pulse_width)
                return True
            return False
    
    def set_angles(self, pan_angle, tilt_angle):
        """Set both servo angles simultaneously"""
        success_pan = self.set_pan_angle(pan_angle)
        success_tilt = self.set_tilt_angle(tilt_angle)
        return success_pan and success_tilt
    
    def move_pan(self, direction, step=1):
        """Move pan servo by step amount in given direction"""
        if direction == "left":
            new_angle = min(self.pan_angle + step, self.max_angle)
        elif direction == "right":
            new_angle = max(self.pan_angle - step, self.min_angle)
        else:
            return False
            
        return self.set_pan_angle(new_angle)
    
    def move_tilt(self, direction, step=1):
        """Move tilt servo by step amount in given direction"""
        if direction == "up":
            new_angle = max(self.tilt_angle - step, self.min_angle)
        elif direction == "down":
            new_angle = min(self.tilt_angle + step, self.max_angle)
        else:
            return False
            
        return self.set_tilt_angle(new_angle)
    
    def center_camera(self):
        """Center both servos to 90 degrees"""
        return self.set_angles(90, 90)
    
    def handle_command(self, command, value=None):
        """Handle camera control commands from WebSocket"""
        try:
            if command == "pan":
                direction = value.get("direction")
                step = value.get("step", 1)
                return self.move_pan(direction, step)
                
            elif command == "tilt":
                direction = value.get("direction")
                step = value.get("step", 1)
                return self.move_tilt(direction, step)
                
            elif command == "set_pan":
                angle = value.get("angle")
                return self.set_pan_angle(angle)
                
            elif command == "set_tilt":
                angle = value.get("angle")
                return self.set_tilt_angle(angle)
                
            elif command == "center":
                return self.center_camera()
                
            elif command == "preset":
                preset_name = value.get("name")
                return self.apply_preset(preset_name)
                
            else:
                print(f"Unknown servo command: {command}")
                return False
                
        except Exception as e:
            print(f"Servo command error: {e}")
            return False
    
    def apply_preset(self, preset_name):
        """Apply predefined camera positions"""
        presets = {
            "center": (90, 90),
            "front": (90, 45),
            "left": (135, 90),
            "right": (45, 90),
            "down": (90, 135),
            "up": (90, 45)
        }
        
        if preset_name in presets:
            pan, tilt = presets[preset_name]
            return self.set_angles(pan, tilt)
        return False
    
    def get_status(self):
        """Get current servo positions"""
        return {
            "pan_angle": self.pan_angle,
            "tilt_angle": self.tilt_angle,
            "pan_pin": self.pan_pin,
            "tilt_pin": self.tilt_pin
        }
    
    def smooth_move(self, target_pan, target_tilt, steps=20, delay=0.02):
        """Smooth movement to target position"""
        current_pan = self.pan_angle
        current_tilt = self.tilt_angle
        
        pan_step = (target_pan - current_pan) / steps
        tilt_step = (target_tilt - current_tilt) / steps
        
        for i in range(steps):
            new_pan = current_pan + (pan_step * (i + 1))
            new_tilt = current_tilt + (tilt_step * (i + 1))
            
            self.set_angles(new_pan, new_tilt)
            time.sleep(delay)
    
    def cleanup(self):
        """Clean up servo resources"""
        try:
            # Center servos before shutdown
            self.center_camera()
            time.sleep(0.5)
            
            # Turn off PWM
            self.pi.set_servo_pulsewidth(self.pan_pin, 0)
            self.pi.set_servo_pulsewidth(self.tilt_pin, 0)
            
            # Close pigpio connection
            self.pi.stop()
            print("Servo controller cleanup completed")
            
        except Exception as e:
            print(f"Error during servo cleanup: {e}")