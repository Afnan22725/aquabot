#!/usr/bin/env python3
"""
Test script for sample management functionality
"""

import sys
import os
import json
from datetime import datetime

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from logger import DataLogger

def test_sample_management():
    """Test the sample management functionality"""
    print("Testing Sample Management System...")
    print("=" * 50)
    
    # Initialize logger
    logger = DataLogger('config/settings.json')
    
    # Test adding sample locations
    test_locations = [
        (37.7749, -122.4194),  # San Francisco
        (34.0522, -118.2437),  # Los Angeles  
        (40.7128, -74.0060),   # New York
    ]
    
    print("1. Adding test samples...")
    for i, (lat, lon) in enumerate(test_locations, 1):
        sample_id = logger.log_sample(pump_id=i, duration=5, location=(lat, lon))
        print(f"   Added sample {sample_id} at ({lat}, {lon})")
    
    # Test getting all samples
    print("\n2. Retrieving all samples...")
    samples = logger.get_all_samples()
    print(f"   Found {len(samples)} samples")
    
    for sample in samples:
        print(f"   - {sample['sample_id'][:8]}... | Pump {sample['pump_id']} | {sample['latitude']:.4f}, {sample['longitude']:.4f}")
    
    # Test statistics
    print("\n3. Getting statistics...")
    stats = logger.get_statistics()
    print(f"   Total samples: {stats['total_samples']}")
    print(f"   Samples today: {stats['samples_today']}")
    
    # Test exports
    print("\n4. Testing exports...")
    
    # Export GeoJSON
    geojson_file = logger.export_to_geojson()
    print(f"   GeoJSON exported to: {geojson_file}")
    
    # Export CSV
    csv_file = logger.export_to_csv()
    print(f"   CSV exported to: {csv_file}")
    
    # Verify files exist
    if os.path.exists(geojson_file):
        print(f"   ✓ GeoJSON file created successfully")
        # Show first few lines
        with open(geojson_file, 'r') as f:
            content = f.read()[:200]
            print(f"     Preview: {content}...")
    else:
        print(f"   ✗ GeoJSON file not found")
    
    if os.path.exists(csv_file):
        print(f"   ✓ CSV file created successfully")
        # Show first few lines
        with open(csv_file, 'r') as f:
            lines = f.readlines()[:3]
            print(f"     Lines: {len(lines)}")
            for line in lines:
                print(f"     {line.strip()}")
    else:
        print(f"   ✗ CSV file not found")
    
    print("\n" + "=" * 50)
    print("Sample Management Test Complete!")

if __name__ == "__main__":
    test_sample_management()