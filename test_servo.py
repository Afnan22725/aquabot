#!/usr/bin/env python3
"""
Test script for servo camera controls
Run this on the Raspberry Pi to test servo movement
"""

import sys
import time
sys.path.append('/home/pi/boat-dashboard/server')

from servo_controller import ServoController

def test_servo_controller():
    print("Testing Servo Controller...")
    print("Make sure pigpiod is running: sudo pigpiod")
    
    try:
        # Initialize servo controller with default pins
        config = {
            'camera_pan': 12,
            'camera_tilt': 13
        }
        
        servo = ServoController(config)
        print(f"Servo controller initialized")
        print(f"Pan pin: GPIO{servo.pan_pin}, Tilt pin: GPIO{servo.tilt_pin}")
        
        # Test sequence
        print("\n=== Starting Test Sequence ===")
        
        # Center position
        print("1. Centering servos...")
        servo.center_camera()
        time.sleep(2)
        
        # Pan left and right
        print("2. Testing pan movement...")
        servo.set_pan_angle(45)  # Right
        time.sleep(1)
        servo.set_pan_angle(135)  # Left
        time.sleep(1)
        servo.set_pan_angle(90)  # Center
        time.sleep(1)
        
        # Tilt up and down
        print("3. Testing tilt movement...")
        servo.set_tilt_angle(45)  # Up
        time.sleep(1)
        servo.set_tilt_angle(135)  # Down
        time.sleep(1)
        servo.set_tilt_angle(90)  # Center
        time.sleep(1)
        
        # Test presets
        print("4. Testing presets...")
        presets = ['front', 'left', 'right', 'down', 'center']
        for preset in presets:
            print(f"   Applying preset: {preset}")
            servo.apply_preset(preset)
            time.sleep(1.5)
        
        # Test smooth movement
        print("5. Testing smooth movement...")
        servo.smooth_move(45, 45, steps=30)  # Smooth move to corner
        time.sleep(1)
        servo.smooth_move(90, 90, steps=30)  # Smooth return to center
        
        print("\n=== Test completed successfully! ===")
        print("Current status:", servo.get_status())
        
    except Exception as e:
        print(f"Error during test: {e}")
        
    finally:
        # Clean up
        print("\nCleaning up...")
        servo.cleanup()

def interactive_control():
    """Interactive servo control for manual testing"""
    print("\n=== Interactive Control Mode ===")
    print("Commands:")
    print("  w/s - Tilt up/down")
    print("  a/d - Pan left/right")
    print("  c   - Center")
    print("  q   - Quit")
    
    config = {'camera_pan': 12, 'camera_tilt': 13}
    servo = ServoController(config)
    
    try:
        while True:
            cmd = input("\nCommand: ").lower().strip()
            
            if cmd == 'q':
                break
            elif cmd == 'w':
                servo.move_tilt('up', 5)
                print(f"Tilt angle: {servo.tilt_angle}°")
            elif cmd == 's':
                servo.move_tilt('down', 5)
                print(f"Tilt angle: {servo.tilt_angle}°")
            elif cmd == 'a':
                servo.move_pan('left', 5)
                print(f"Pan angle: {servo.pan_angle}°")
            elif cmd == 'd':
                servo.move_pan('right', 5)
                print(f"Pan angle: {servo.pan_angle}°")
            elif cmd == 'c':
                servo.center_camera()
                print("Centered")
            else:
                print("Invalid command")
                
            print(f"Status: Pan={servo.pan_angle}°, Tilt={servo.tilt_angle}°")
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        servo.cleanup()

if __name__ == "__main__":
    print("Servo Controller Test")
    print("====================")
    
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        interactive_control()
    else:
        test_servo_controller()