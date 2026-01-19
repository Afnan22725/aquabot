# Water Sample Collection Location Management

## Overview

The boat dashboard now includes comprehensive water sample collection location management with the ability to save sample data locally and download it via the internet. This system tracks GPS coordinates of each water sample collection point and provides various export formats.

## Features

### 🗺️ Sample Location Tracking
- **GPS Integration**: Automatically captures GPS coordinates when water samples are collected
- **Sample Identification**: Each sample gets a unique UUID for tracking
- **Timestamp Recording**: Precise timestamp for each collection
- **Pump Information**: Records which pump was used and duration

### 📊 Sample Management Dashboard
- **Real-time Statistics**: View total samples and daily collection counts
- **Recent Samples List**: Display of the 10 most recent samples
- **Map Visualization**: Show all sample locations as markers on the map
- **Interactive Popups**: Click sample markers to see detailed information

### 💾 Data Storage & Export
- **Dual Format Storage**: JSON for structured data, CSV for compatibility
- **GeoJSON Export**: Industry-standard geospatial format for GIS applications
- **CSV Export**: Spreadsheet-compatible format
- **Local File Management**: Organized file structure with timestamps

### 🌐 Web Interface Controls
- **Refresh Data**: Update sample display and statistics
- **Show on Map**: Toggle sample markers on the main GPS map
- **Export Buttons**: One-click export to GeoJSON or CSV formats
- **Visual Feedback**: Success notifications for export operations

## File Structure

```
boat-dashboard/
├── server/
│   ├── logger.py              # Enhanced DataLogger class
│   ├── main.py               # WebSocket server with sample handlers
│   └── ...
├── web/
│   ├── index.html            # Dashboard with sample management panel
│   ├── app.js               # JavaScript for sample functionality  
│   ├── style.css            # Styling for sample management UI
│   └── ...
├── config/
│   └── settings.json         # Configuration with logging settings
├── samples/                  # Sample data directory (created automatically)
│   ├── samples.json         # JSON data storage
│   ├── water_samples_YYYYMMDD_HHMMSS.csv
│   └── water_samples_YYYYMMDD_HHMMSS.geojson
└── test_samples.py          # Test script for sample management
```

## Configuration

### settings.json Configuration
```json
{
  "logging": {
    "csv_file": "water_samples.csv",
    "json_file": "samples/samples.json",
    "samples_dir": "samples/"
  }
}
```

### Environment Setup
- **GPS Requirements**: Functional GPS module for location data
- **Storage**: Sufficient disk space for sample data files
- **Network**: WebSocket connection for real-time updates

## Usage

### Collecting Samples
1. Navigate to water collection location
2. Wait for GPS lock (green status indicator)
3. Select pump and duration
4. Click "Activate" - location will be automatically recorded

### Managing Sample Data
1. **View Recent Samples**: See list in the Sample Management panel
2. **Refresh Data**: Click "Refresh Data" to update display
3. **Show on Map**: Click "Show on Map" to display all sample markers
4. **Export Data**: Use "Export GeoJSON" or "Export CSV" buttons

### Downloading Sample Data
- **Local Access**: Files saved in `samples/` directory
- **Remote Access**: Files accessible via file system or web server
- **Format Options**:
  - **CSV**: Compatible with Excel, Google Sheets
  - **GeoJSON**: Compatible with QGIS, ArcGIS, online mapping tools

## Data Formats

### JSON Storage Format
```json
{
  "sample_id": "uuid4-string",
  "pump_id": 1,
  "duration": 5,
  "latitude": 37.7749,
  "longitude": -122.4194,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### CSV Export Format
```csv
sample_id,pump_id,duration,latitude,longitude,timestamp
abc123...,1,5,37.7749,-122.4194,2024-01-15T10:30:00Z
```

### GeoJSON Export Format
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-122.4194, 37.7749]
      },
      "properties": {
        "sample_id": "abc123...",
        "pump_id": 1,
        "duration": 5,
        "timestamp": "2024-01-15T10:30:00Z"
      }
    }
  ]
}
```

## API Reference

### WebSocket Messages

#### Request Sample Data
```javascript
{
  "type": "samples",
  "command": "get_all" | "get_statistics" | "export_geojson" | "export_csv"
}
```

#### Sample Data Response
```javascript
{
  "type": "samples_data",
  "data": {
    "command": "all_samples",
    "samples": [/* sample objects */]
  }
}
```

### Python API

#### DataLogger Methods
```python
# Initialize logger
logger = DataLogger('config/settings.json')

# Log a sample
sample_id = logger.log_sample(pump_id=1, duration=5, location=(lat, lon))

# Get all samples
samples = logger.get_all_samples()

# Get statistics
stats = logger.get_statistics()

# Export data
geojson_file = logger.export_to_geojson()
csv_file = logger.export_to_csv()
```

## Integration with GIS Software

### QGIS Integration
1. Export data as GeoJSON
2. In QGIS: Layer → Add Layer → Add Vector Layer
3. Select the exported GeoJSON file
4. Sample points will appear on map with attributes

### Google Earth Integration
1. Convert GeoJSON to KML (online converters available)
2. Import KML file into Google Earth
3. View sample locations with popup information

### Web Mapping
- **Leaflet**: Direct GeoJSON loading support
- **OpenLayers**: Native GeoJSON handling
- **Mapbox**: GeoJSON data source integration

## Troubleshooting

### Common Issues

**No GPS Data**
- Check GPS module connection
- Verify GPS has lock (may take 30+ seconds outdoors)
- Ensure GPS module is configured correctly

**Export Files Not Created**
- Check write permissions on samples directory
- Verify disk space availability
- Check server logs for error messages

**Map Markers Not Showing**
- Ensure GPS coordinates are valid (not 0,0)
- Check browser console for JavaScript errors
- Verify WebSocket connection is active

### Debugging

**Server-side Logging**
```bash
# Check server logs
tail -f server.log

# Test sample management
python test_samples.py
```

**Client-side Debugging**
- Open browser Developer Tools (F12)
- Check Console tab for JavaScript errors
- Monitor Network tab for WebSocket messages

## Performance Considerations

- **Large Datasets**: For >1000 samples, consider pagination
- **Map Performance**: Cluster markers for better performance
- **Export Speed**: Large exports may take time - provide user feedback
- **Storage**: Monitor disk usage for long-term deployments

## Future Enhancements

- **Sample Clustering**: Group nearby samples on map
- **Advanced Filtering**: Filter by date, pump, location
- **Cloud Sync**: Automatic backup to cloud storage
- **Mobile App**: Dedicated mobile interface
- **Offline Mode**: Local storage when internet unavailable