import pigpio

class MotorController:
    def __init__(self, pin_config, esc_config):
        self.pi = pigpio.pi()  # Connect to local pigpio daemon

        if not self.pi.connected:
            raise RuntimeError("Failed to connect to pigpio daemon. Is 'pigpiod' running?")

        self.left_pin = pin_config['motor_left']
        self.right_pin = pin_config['motor_right']
        self.min_pulse = esc_config['min']
        self.max_pulse = esc_config['max']

        # Setup pins
        self.pi.set_mode(self.left_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.right_pin, pigpio.OUTPUT)
        self.stop()

    def handle_command(self, command):
        """Handle motor control commands"""
        actions = {
            'forward': self.forward,
            'backward': self.backward,
            'left': self.left,
            'right': self.right,
            'stop': self.stop
        }
        action = actions.get(command)
        if action:
            action()
        else:
            print(f"[WARN] Unknown command: {command}")

    def forward(self):
        """Move forward"""
        self.pi.set_servo_pulsewidth(self.left_pin, self.max_pulse)
        self.pi.set_servo_pulsewidth(self.right_pin, self.max_pulse)

    def backward(self):
        """Move backward"""
        mid = (self.max_pulse + self.min_pulse) // 2
        self.pi.set_servo_pulsewidth(self.left_pin, mid)
        self.pi.set_servo_pulsewidth(self.right_pin, mid)

    def left(self):
        """Turn left"""
        self.pi.set_servo_pulsewidth(self.left_pin, self.min_pulse)
        self.pi.set_servo_pulsewidth(self.right_pin, self.max_pulse)

    def right(self):
        """Turn right"""
        self.pi.set_servo_pulsewidth(self.left_pin, self.max_pulse)
        self.pi.set_servo_pulsewidth(self.right_pin, self.min_pulse)

    def stop(self):
        """Stop motors"""
        self.pi.set_servo_pulsewidth(self.left_pin, self.min_pulse)
        self.pi.set_servo_pulsewidth(self.right_pin, self.min_pulse)
