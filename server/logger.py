# Enhanced data logging with sample collection features
import csv
import json
import os
from datetime import datetime, timezone
import uuid

class DataLogger:
    def __init__(self, config):
        self.csv_file = config['csv_file']
        self.json_file = config.get('json_file', 'water_samples.json')
        self.samples_dir = config.get('samples_dir', 'samples')
        
        # Create samples directory if it doesn't exist
        os.makedirs(self.samples_dir, exist_ok=True)
        
        self.setup_csv()
        self.setup_json()
        
    def setup_csv(self):
        """Setup CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'sample_id', 'pump_id', 'duration', 
                    'latitude', 'longitude', 'altitude', 'notes', 'water_temp', 
                    'air_temp', 'battery_voltage', 'weather_conditions'
                ])
                
    def setup_json(self):
        """Setup JSON file for sample metadata"""
        if not os.path.exists(self.json_file):
            initial_data = {
                'metadata': {
                    'created': datetime.now(timezone.utc).isoformat(),
                    'version': '1.0',
                    'boat_id': 'aquabot-001'
                },
                'samples': []
            }
            with open(self.json_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
                
    def log_sample(self, pump_id, duration, location, **kwargs):
        """Enhanced sample logging with additional data"""
        try:
            # Generate unique sample ID
            sample_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now(timezone.utc)
            
            # Extract additional data
            altitude = kwargs.get('altitude', 0)
            notes = kwargs.get('notes', '')
            water_temp = kwargs.get('water_temp', None)
            air_temp = kwargs.get('air_temp', None)
            battery_voltage = kwargs.get('battery_voltage', None)
            weather = kwargs.get('weather_conditions', '')
            
            # Log to CSV
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp.isoformat(),
                    sample_id,
                    pump_id,
                    duration,
                    location[0] if location else None,
                    location[1] if location else None,
                    altitude,
                    notes,
                    water_temp,
                    air_temp,
                    battery_voltage,
                    weather
                ])
            
            # Log to JSON
            sample_data = {
                'sample_id': sample_id,
                'timestamp': timestamp.isoformat(),
                'pump_id': pump_id,
                'duration': duration,
                'location': {
                    'latitude': location[0] if location else None,
                    'longitude': location[1] if location else None,
                    'altitude': altitude
                },
                'environmental': {
                    'water_temperature': water_temp,
                    'air_temperature': air_temp,
                    'weather_conditions': weather
                },
                'system': {
                    'battery_voltage': battery_voltage
                },
                'notes': notes,
                'status': 'collected'
            }
            
            # Read existing JSON data
            with open(self.json_file, 'r') as f:
                data = json.load(f)
            
            # Add new sample
            data['samples'].append(sample_data)
            data['metadata']['last_updated'] = timestamp.isoformat()
            data['metadata']['total_samples'] = len(data['samples'])
            
            # Write back to JSON
            with open(self.json_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Logged sample {sample_id} from pump {pump_id} at {location}")
            return sample_id
            
        except Exception as e:
            print(f"Logging error: {e}")
            return None
    
    def get_samples(self, limit=None):
        """Get all samples or limited number"""
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
            
            samples = data.get('samples', [])
            if limit:
                samples = samples[-limit:]  # Get most recent
                
            return samples
        except Exception as e:
            print(f"Error reading samples: {e}")
            return []
    
    def export_samples_csv(self, filename=None):
        """Export samples to downloadable CSV"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"water_samples_export_{timestamp}.csv"
        
        export_path = os.path.join(self.samples_dir, filename)
        
        try:
            samples = self.get_samples()
            
            with open(export_path, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write headers
                writer.writerow([
                    'Sample ID', 'Timestamp', 'Pump ID', 'Duration (s)', 
                    'Latitude', 'Longitude', 'Altitude (m)', 
                    'Water Temp (°C)', 'Air Temp (°C)', 'Battery (V)', 
                    'Weather', 'Notes', 'Status'
                ])
                
                # Write data
                for sample in samples:
                    writer.writerow([
                        sample['sample_id'],
                        sample['timestamp'],
                        sample['pump_id'],
                        sample['duration'],
                        sample['location']['latitude'],
                        sample['location']['longitude'],
                        sample['location']['altitude'],
                        sample['environmental']['water_temperature'],
                        sample['environmental']['air_temperature'],
                        sample['system']['battery_voltage'],
                        sample['environmental']['weather_conditions'],
                        sample['notes'],
                        sample['status']
                    ])
            
            return export_path
            
        except Exception as e:
            print(f"Export error: {e}")
            return None
    
    def export_samples_geojson(self, filename=None):
        """Export samples as GeoJSON for mapping"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"water_samples_map_{timestamp}.geojson"
        
        export_path = os.path.join(self.samples_dir, filename)
        
        try:
            samples = self.get_samples()
            
            features = []
            for sample in samples:
                if sample['location']['latitude'] and sample['location']['longitude']:
                    feature = {
                        "type": "Feature",
                        "properties": {
                            "sample_id": sample['sample_id'],
                            "timestamp": sample['timestamp'],
                            "pump_id": sample['pump_id'],
                            "duration": sample['duration'],
                            "water_temp": sample['environmental']['water_temperature'],
                            "air_temp": sample['environmental']['air_temperature'],
                            "weather": sample['environmental']['weather_conditions'],
                            "notes": sample['notes'],
                            "status": sample['status']
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                sample['location']['longitude'],
                                sample['location']['latitude'],
                                sample['location']['altitude'] or 0
                            ]
                        }
                    }
                    features.append(feature)
            
            geojson = {
                "type": "FeatureCollection",
                "metadata": {
                    "generated": datetime.now(timezone.utc).isoformat(),
                    "total_samples": len(features)
                },
                "features": features
            }
            
            with open(export_path, 'w') as f:
                json.dump(geojson, f, indent=2)
            
            return export_path
            
        except Exception as e:
            print(f"GeoJSON export error: {e}")
            return None
    
    def get_sample_statistics(self):
        """Get sample collection statistics"""
        try:
            samples = self.get_samples()
            
            if not samples:
                return {'total': 0}
            
            # Calculate statistics
            total = len(samples)
            by_pump = {}
            by_date = {}
            
            for sample in samples:
                # Count by pump
                pump_id = sample['pump_id']
                by_pump[pump_id] = by_pump.get(pump_id, 0) + 1
                
                # Count by date
                date = sample['timestamp'][:10]  # YYYY-MM-DD
                by_date[date] = by_date.get(date, 0) + 1
            
            # Get date range
            timestamps = [datetime.fromisoformat(s['timestamp'].replace('Z', '+00:00')) for s in samples]
            first_sample = min(timestamps)
            last_sample = max(timestamps)
            
            return {
                'total': total,
                'by_pump': by_pump,
                'by_date': by_date,
                'date_range': {
                    'first': first_sample.isoformat(),
                    'last': last_sample.isoformat()
                }
            }
            
        except Exception as e:
            print(f"Statistics error: {e}")
            return {'total': 0, 'error': str(e)}