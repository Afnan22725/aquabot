# Relay control and sample logging
import pigpio
import asyncio

class PumpController:
    def __init__(self, pump_pins, pump_config):
        self.pi = pigpio.pi()
        self.pump_pins = pump_pins
        self.default_duration = pump_config['default']
        
        # Setup pump pins
        for pin in self.pump_pins:
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.write(pin, 1)  # Turn off initially
            
    def activate_pump(self, pump_id, duration, location=None):
        """Activate a pump for specified duration"""
        if pump_id < 1 or pump_id > len(self.pump_pins):
            print(f"Invalid pump ID: {pump_id}")
            return
            
        pin = self.pump_pins[pump_id - 1]
        
        # Turn on pump
        self.pi.write(pin, 0)
        print(f"Pump {pump_id} activated for {duration}s")
        
        # Schedule turn off
        asyncio.create_task(self.deactivate_pump(pin, duration))
        
    async def deactivate_pump(self, pin, duration):
        """Deactivate pump after duration"""
        await asyncio.sleep(duration)
        self.pi.write(pin, 1)
        print(f"Pump on pin {pin} deactivated")
        
    def cleanup(self):
        """Clean up pump resources"""
        for pin in self.pump_pins:
            self.pi.write(pin, 1)  # Turn off all pumps