import asyncio
import json
import os
import signal
import sys
import cv2  # Added missing import
import base64  # Added missing import
from websockets.asyncio.server import serve

# Add the server directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from camera_stream import CameraStream
from gps_reader import GPSReader
from imu_reader import IMUReader
from battery_monitor import BatteryMonitor
from motor_control import MotorController
from pump_control import PumpController
from servo_controller import ServoController
from system_status import SystemStatus
from logger import DataLogger

class BoatServer:
    def __init__(self):
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), '../config/settings.json')
        with open(config_path) as f:
            self.config = json.load(f)
        
        # Initialize components
        self.camera = CameraStream()
        self.gps = GPSReader(self.config['gps'])
        self.imu = IMUReader()
        self.battery = BatteryMonitor()
        self.motors = MotorController(self.config['pins'], self.config['esc_range'])
        self.pumps = PumpController(self.config['pins']['pumps'], self.config['pump_durations'])
        self.servos = ServoController(self.config['pins'])
        self.system = SystemStatus()
        self.logger = DataLogger(self.config['data_logging'])
        
        # WebSocket connections
        self.connections = set()
        
        # Data storage
        self.telemetry_data = {
            'gps': None,
            'imu': None,
            'battery': None,
            'system': None,
            'servos': None
        }

    async def handle_connection(self, websocket):
        """Handle a new WebSocket connection"""
        self.connections.add(websocket)
        print(f"New connection: {websocket.remote_address}")
        
        try:
            # Send initial configuration
            await websocket.send(json.dumps({
                'type': 'config',
                'data': self.config
            }))
            
            # Handle messages from client
            async for message in websocket:
                await self.handle_message(message, websocket)
                
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            self.connections.remove(websocket)

    async def handle_message(self, message, websocket):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'control':
                # Handle motor control
                command = data.get('command')
                if command in ['forward', 'backward', 'left', 'right', 'stop']:
                    self.motors.handle_command(command)
                    
            elif msg_type == 'servo':
                # Handle servo camera control
                command = data.get('command')
                value = data.get('value', {})
                result = self.servos.handle_command(command, value)
                
                # Send servo status back to client
                servo_status = self.servos.get_status()
                await websocket.send(json.dumps({
                    'type': 'servo_status',
                    'data': servo_status
                }))
                    
            elif msg_type == 'pump':
                # Handle pump control
                pump_id = data.get('pump_id')
                duration = data.get('duration', self.config['pump_durations']['default'])
                
                # Get current GPS location before activating pump
                gps_data = self.telemetry_data['gps']
                if gps_data and 'lat' in gps_data and 'lon' in gps_data:
                    sample_location = (gps_data['lat'], gps_data['lon'])
                else:
                    sample_location = None
                    
                # Activate pump
                self.pumps.activate_pump(pump_id, duration, sample_location)
                
                # Log sample if location is available
                if sample_location:
                    self.logger.log_sample(pump_id, duration, sample_location)
                    
            elif msg_type == 'samples':
                # Handle sample data requests
                command = data.get('command')
                
                if command == 'get_all':
                    samples = self.logger.get_all_samples()
                    await websocket.send(json.dumps({
                        'type': 'samples_data',
                        'data': {
                            'command': 'all_samples',
                            'samples': samples
                        }
                    }))
                    
                elif command == 'get_statistics':
                    stats = self.logger.get_statistics()
                    await websocket.send(json.dumps({
                        'type': 'samples_data', 
                        'data': {
                            'command': 'statistics',
                            'statistics': stats
                        }
                    }))
                    
                elif command == 'export_geojson':
                    geojson_file = self.logger.export_to_geojson()
                    await websocket.send(json.dumps({
                        'type': 'samples_data',
                        'data': {
                            'command': 'geojson_exported',
                            'file': geojson_file,
                            'message': f'GeoJSON exported to {geojson_file}'
                        }
                    }))
                    
                elif command == 'export_csv':
                    csv_file = self.logger.export_to_csv()
                    await websocket.send(json.dumps({
                        'type': 'samples_data',
                        'data': {
                            'command': 'csv_exported', 
                            'file': csv_file,
                            'message': f'CSV exported to {csv_file}'
                        }
                    }))
                    
        except json.JSONDecodeError:
            print(f"Invalid JSON message: {message}")
        except Exception as e:
            print(f"Error handling message: {e}")

    async def broadcast_telemetry(self):
        """Broadcast telemetry data to all connected clients"""
        while True:
            try:
                # Update telemetry data
                self.telemetry_data['gps'] = self.gps.read()
                self.telemetry_data['imu'] = self.imu.read()
                self.telemetry_data['battery'] = self.battery.read()
                self.telemetry_data['system'] = self.system.get_status()
                self.telemetry_data['servos'] = self.servos.get_status()
                
                # Broadcast to all connections
                if self.connections:
                    message = json.dumps({
                        'type': 'telemetry',
                        'data': self.telemetry_data
                    })
                    
                    await asyncio.gather(
                        *[conn.send(message) for conn in self.connections],
                        return_exceptions=True
                    )
                    
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Telemetry broadcast error: {e}")
                await asyncio.sleep(1)

    async def broadcast_video(self):
        """Broadcast video frames to all connected clients"""
        while True:
            try:
                frame = self.camera.capture_frame()
                if frame is not None:
                    # Convert frame to base64
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                    
                    # Broadcast to all connections
                    if self.connections:
                        message = json.dumps({
                            'type': 'video',
                            'data': f"data:image/jpeg;base64,{jpg_as_text}"
                        })
                        
                        await asyncio.gather(
                            *[conn.send(message) for conn in self.connections],
                            return_exceptions=True
                        )
                else:
                    print("Warning: No frame captured from camera")
                
                await asyncio.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                print(f"Video broadcast error: {e}")
                await asyncio.sleep(1)

    async def run_server(self):
        """Run the WebSocket server with the new API"""
        # Start background tasks
        asyncio.create_task(self.broadcast_telemetry())
        asyncio.create_task(self.broadcast_video())
        
        # Start WebSocket server with new API
        async with serve(
            self.handle_connection,
            self.config['websocket']['host'],
            self.config['websocket']['port']
        ) as server:
            print(f"WebSocket server running on ws://{self.config['websocket']['host']}:{self.config['websocket']['port']}")
            await server.serve_forever()

    def cleanup(self):
        """Clean up resources"""
        try:
            self.motors.stop()
            self.pumps.cleanup()
            self.servos.cleanup()
            self.camera.cleanup()
            self.gps.cleanup()
            print("Server cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")

async def main():
    server = BoatServer()
    
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in [signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(server)))
    
    try:
        await server.run_server()
    except asyncio.CancelledError:
        print("Server was cancelled")
        server.cleanup()
    except Exception as e:
        print(f"Server error: {e}")
        server.cleanup()

async def shutdown(server):
    """Shutdown the server gracefully"""
    print("Shutting down server...")
    server.cleanup()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        print(f"Error during shutdown: {e}")
    finally:
        asyncio.get_event_loop().stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user")
