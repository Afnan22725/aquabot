// Client-side JavaScript
// WebSocket connection
let ws = null;
let reconnectInterval = null;
const host = window.location.hostname || "10.35.254.6";
const port = 8000;

// Map variables
let map = null;
let boatMarker = null;
let pathLayer = null;
let sampleMarkers = [];
let pathPoints = [];

// 3D visualization variables
let scene, camera, renderer, boatModel;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    init3DVisualization();
    setupEventListeners();
    setupSampleManagement();
    connectWebSocket();
    
    // Start animation loop for 3D visualization
    animate();
});

// Initialize Leaflet map
function initMap() {
    map = L.map('map').setView([0, 0], 2);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    
    // Add custom boat icon
    const boatIcon = L.icon({
        iconUrl: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MTIgNTEyIj48cGF0aCBmaWxsPSIjMWU4OGU1IiBkPSJNNDgzLjEgMTY2LjRjLTQuMi0xMC43LTE1LjItMTcuMi0yNi45LTE3LjJIMjU2aC0yMDAuMmMtMTEuNyAwLTIyLjcgNi41LTI2LjkgMTcuMmMtNC4yIDEwLjctMi40IDIzIDQuNSA0MS41bDExMi4xIDIyNC4yYzYuOSAxMy44IDIxLjIgMjIuNiAzNi43IDIyLjZzMjkuOC04LjggMzYuNy0yMi42TDQ3OC42IDIwOGM2LjktMTguNSA4LjctMzAuOCA0LjUtNDEuNnptLTMwMS4yIDI0OS40Yy0xMC40IDAtMTguOC04LjQtMTguOC0xOC44czguNC0xOC44IDE4LjgtMTguOCAxOC44IDguNCAxOC44IDE4LjgtOC40IDE4LjgtMTguOCAxOC44em0yMDMuMi0xMjUuNGMwIDQ0LjItMzUuOCA4MC04MCA4MHM4MC0zNS44IDgwLTgwLTM1LjgtODAtODAtODAtODAgMzUuOC04MCA4MHoiLz48L3N2Zz4=',
        iconSize: [30, 30],
        iconAnchor: [15, 15],
        popupAnchor: [0, -15]
    });
    
    boatMarker = L.marker([0, 0], {icon: boatIcon}).addTo(map);
    boatMarker.bindPopup("Boat Position");
    
    // Initialize path layer
    pathLayer = L.polyline([], {color: 'blue'}).addTo(map);
}

// Initialize Three.js 3D visualization
function init3DVisualization() {
    // Setup scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87ceeb);
    
    // Setup camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(5, 3, 5);
    camera.lookAt(0, 0, 0);
    
    // Setup renderer
    renderer = new THREE.WebGLRenderer({antialias: true});
    renderer.setSize(document.getElementById('boat-container').clientWidth, 
                     document.getElementById('boat-container').clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.getElementById('boat-container').appendChild(renderer.domElement);
    
    // Enhanced lighting for realism
    const light = new THREE.DirectionalLight(0xffffff, 1.2);
    light.position.set(5, 10, 7);
    scene.add(light);
    
    scene.add(new THREE.AmbientLight(0x404040));
    
    // Create PVC catamaran boat model
    createPVCBoatModel();
    
    // Handle window resize
    window.addEventListener('resize', function() {
        camera.aspect = document.getElementById('boat-container').clientWidth / document.getElementById('boat-container').clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(document.getElementById('boat-container').clientWidth, document.getElementById('boat-container').clientHeight);
    });
}

// Create a simple boat model (catamaran style)
function createPVCBoatModel() {
    // Remove old boat objects (keep lights & camera)
    while (scene.children.length > 2) {
        scene.remove(scene.children[2]);
    }

    const boatGroup = new THREE.Group();

    /* =========================
       PVC PIPE HULLS (PARALLEL)
    ========================= */
    const pipeLength = 3.0;
    const pipeRadius = 0.18;

    const pvcMaterial = new THREE.MeshPhongMaterial({
        color: 0xffffff,
        shininess: 80
    });

    const pipeGeometry = new THREE.CylinderGeometry(
        pipeRadius,
        pipeRadius,
        pipeLength,
        32
    );

    function createHull(zPos) {
        const hull = new THREE.Mesh(pipeGeometry, pvcMaterial);
        hull.rotation.z = Math.PI / 2;   // Lay pipe horizontally
        hull.position.z = zPos;          // PARALLEL spacing
        hull.position.y = 0;
        boatGroup.add(hull);

        // End caps
        const capGeometry = new THREE.SphereGeometry(pipeRadius, 32, 32);

        const frontCap = new THREE.Mesh(capGeometry, pvcMaterial);
        frontCap.position.set(pipeLength / 2, 0, zPos);
        boatGroup.add(frontCap);

        const backCap = new THREE.Mesh(capGeometry, pvcMaterial);
        backCap.position.set(-pipeLength / 2, 0, zPos);
        boatGroup.add(backCap);
    }

    // TWO PARALLEL PVC PIPES
    createHull(-0.6);
    createHull(0.6);

    /* =========================
       UNDER-HULL ALUMINUM BARS (PARALLEL)
    ========================== */
    const aluminumMaterial = new THREE.MeshPhongMaterial({
        color: 0x9e9e9e,
        shininess: 100
    });

    const barGeometry = new THREE.BoxGeometry(3.0, 0.06, 0.05);
    
   

    /* =========================
       SUPPORT FRAME (ALUMINUM)
       CONNECTS BOTH HULLS
    ========================== */
    const frameMaterial = new THREE.MeshPhongMaterial({
        color: 0x9e9e9e,
        shininess: 100
    });

    // Cross beams go ACROSS the hulls (Z direction)
    const crossBeamGeometry = new THREE.BoxGeometry(0.08, 0.06, 1.35);

    // Positions along boat length (X)
    const beamXPositions = [-0.9, 0, 0.9];

    for (let x of beamXPositions) {
        const beam = new THREE.Mesh(crossBeamGeometry, frameMaterial);
        beam.position.set(x, 0.12, 0); // sits just above hulls
        boatGroup.add(beam);
    }

    // Optional longitudinal rails (adds realism)
    const railGeometry = new THREE.BoxGeometry(3.0, 0.05, 0.06);

    for (let z of [-0.4, 0.4]) {
        const rail = new THREE.Mesh(railGeometry, frameMaterial);
        rail.position.set(0, 0.18, z);
        boatGroup.add(rail);
    }

    /* =========================
       CONTROL BOX (MOUNTED ON FRAME)
    ========================== */
    const boxGeometry = new THREE.BoxGeometry(0.8, 0.35, 0.5);
    const boxMaterial = new THREE.MeshPhongMaterial({
        color: 0x2e7d32
    });

    const controlBox = new THREE.Mesh(boxGeometry, boxMaterial);
    controlBox.position.y = 0.45;  // sits ON the frame
    boatGroup.add(controlBox);

    // Lid
    const lidGeometry = new THREE.BoxGeometry(0.82, 0.05, 0.52);
    const lidMaterial = new THREE.MeshPhongMaterial({
        color: 0x1b5e20
    });

    const lid = new THREE.Mesh(lidGeometry, lidMaterial);
    lid.position.y = 0.65;
    boatGroup.add(lid);

    /* =========================
       GPS ANTENNA
    ========================== */
    const antennaGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.4, 8);
    const antennaMaterial = new THREE.MeshPhongMaterial({ color: 0x000000 });

    const antenna = new THREE.Mesh(antennaGeometry, antennaMaterial);
    antenna.position.set(0.3, 0.9, 0);
    boatGroup.add(antenna);

    scene.add(boatGroup);
    boatModel = boatGroup;

    return boatGroup;
}

// Animation loop for 3D visualization
function animate() {
    requestAnimationFrame(animate);

    // gentle floating effect
    scene.children.forEach(obj => {
        if (obj.type === "Group") {
            obj.position.y = Math.sin(Date.now() * 0.002) * 0.02;
            obj.rotation.y += 0.001;
        }
    });

    renderer.render(scene, camera);
}

// Setup UI event listeners
function setupEventListeners() {
    // Motor controls
    document.getElementById('btn-forward').addEventListener('click', () => sendControl('forward'));
    document.getElementById('btn-backward').addEventListener('click', () => sendControl('backward'));
    document.getElementById('btn-left').addEventListener('click', () => sendControl('left'));
    document.getElementById('btn-right').addEventListener('click', () => sendControl('right'));
    document.getElementById('btn-stop').addEventListener('click', () => sendControl('stop'));
    
    // Camera controls
    setupCameraControls();
    
    // Pump controls
    document.querySelectorAll('.pump-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const pumpId = this.getAttribute('data-pump');
            const durationInput = document.getElementById(`pump${pumpId}-duration`);
            const duration = parseInt(durationInput.value) || 5;
            activatePump(pumpId, duration);
        });
    });
    
    // Map center button
    document.getElementById('center-map').addEventListener('click', centerMapOnBoat);
    
    // Window resize handling
    window.addEventListener('resize', onWindowResize);
}

// Handle window resize
function onWindowResize() {
    if (camera && renderer) {
        camera.aspect = document.getElementById('boat-container').clientWidth / 
                        document.getElementById('boat-container').clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(document.getElementById('boat-container').clientWidth, 
                         document.getElementById('boat-container').clientHeight);
    }
}

// WebSocket connection
function connectWebSocket() {
    try {
        ws = new WebSocket(`ws://${host}:${port}`);
        
        ws.onopen = function() {
            console.log("Connected to boat server");
            updateConnectionStatus(true);
            clearInterval(reconnectInterval);
        };
        
        ws.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                
                switch(data.type) {
                    case 'config':
                        console.log("Received configuration");
                        break;
                        
                    case 'telemetry':
                        updateTelemetry(data.data);
                        break;
                        
                    case 'video':
                        document.getElementById('video-feed').src = data.data;
                        break;
                        
                    case 'servo_status':
                        console.log('Received servo status:', data.data);
                        updateServoStatus(data.data);
                        break;
                        
                    case 'samples_data':
                        console.log('Received sample data:', data.data);
                        handleSampleData(data.data);
                        break;
                        
                    default:
                        console.log('Unknown message type:', data.type);
                }
            } catch (e) {
                console.error("Error parsing message:", e);
            }
        };
        
        ws.onclose = function() {
            console.log("Disconnected from boat server");
            updateConnectionStatus(false);
            
            // Attempt to reconnect every 3 seconds
            if (!reconnectInterval) {
                reconnectInterval = setInterval(connectWebSocket, 3000);
            }
        };
        
        ws.onerror = function(error) {
            console.error("WebSocket error:", error);
        };
        
    } catch (error) {
        console.error("WebSocket connection error:", error);
    }
}

// Update connection status UI
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    const statusDot = statusElement.querySelector('.status-dot');
    const statusText = statusElement.querySelector('span:last-child');
    
    if (connected) {
        statusDot.className = 'status-dot connected';
        statusText.textContent = 'Connected';
    } else {
        statusDot.className = 'status-dot disconnected';
        statusText.textContent = 'Disconnected';
    }
}

// Send control command to boat
function sendControl(command) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'control',
            command: command
        }));
    }
}

// Activate pump
function activatePump(pumpId, duration) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'pump',
            pump_id: parseInt(pumpId),
            duration: duration
        }));
        
        // Visual feedback
        const btn = document.querySelector(`.pump-btn[data-pump="${pumpId}"]`);
        const originalText = btn.textContent;
        btn.textContent = 'Activating...';
        btn.disabled = true;
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.disabled = false;
        }, duration * 1000);
    }
}

// Get battery icon based on percentage
function getBatteryIcon(percentage) {
    if (percentage >= 75) {
        return 'fas fa-battery-full';
    } else if (percentage >= 50) {
        return 'fas fa-battery-three-quarters';
    } else if (percentage >= 25) {
        return 'fas fa-battery-half';
    } else if (percentage >= 10) {
        return 'fas fa-battery-quarter';
    } else {
        return 'fas fa-battery-empty';
    }
}

// Update telemetry data display
function updateTelemetry(data) {
    // Update GPS data
    if (data.gps) {
        document.getElementById('gps-data').innerHTML = `
            Lat: ${data.gps.lat}<br>
            Lon: ${data.gps.lon}<br>
            Alt: ${data.gps.alt}m<br>
            Sats: ${data.gps.satellites}
        `;
        
        document.getElementById('gps-status').querySelector('span:last-child').textContent = 
            data.gps.fix ? 'GPS Fix' : 'No Fix';
        
        updateMap(data.gps);
    }
    
    // Update IMU data
    if (data.imu) {
        document.getElementById('imu-data').innerHTML = `
            Accel: X${data.imu.accel.x} Y${data.imu.accel.y} Z${data.imu.accel.z}<br>
            Gyro: X${data.imu.gyro.x} Y${data.imu.gyro.y} Z${data.imu.gyro.z}<br>
            Temp: ${data.imu.temp}°C
        `;
        
        updateBoatOrientation(data.imu);
    }
    
    // Update battery data
    if (data.battery) {
        const batteryData = data.battery;
        document.getElementById('battery-data').innerHTML = `
            Voltage: ${batteryData.voltage}V<br>
            Level: ${batteryData.percentage}%<br>
            Status: <span class="battery-status-${batteryData.status.toLowerCase()}">${batteryData.status}</span>
        `;
        
        // Update header battery status with percentage and icon
        const batteryStatus = document.getElementById('battery-status');
        const batteryIcon = batteryStatus.querySelector('i');
        const batteryText = batteryStatus.querySelector('span');
        
        batteryText.textContent = `Battery: ${batteryData.percentage}%`;
        
        // Update battery icon based on percentage
        batteryIcon.className = getBatteryIcon(batteryData.percentage);
        
        // Update battery status color
        batteryStatus.className = `status-item battery-${batteryData.status.toLowerCase()}`;
    }
    
    // Update system data
    if (data.system) {
        document.getElementById('system-data').innerHTML = `
            CPU Temp: ${data.system.cpu_temp || 'N/A'}°C<br>
            CPU Usage: ${data.system.cpu_usage}%<br>
            Memory: ${data.system.memory_usage}%<br>
            Disk: ${data.system.disk_usage}%<br>
            Uptime: ${data.system.uptime}
        `;
    }
    
    // Update servo status
    if (data.servos) {
        updateServoStatus(data.servos);
    }
}

// Update map with new GPS position
function updateMap(gpsData) {
    if (!gpsData || !gpsData.lat || !gpsData.lon) return;
    
    const newPos = [gpsData.lat, gpsData.lon];
    
    // Update boat marker
    boatMarker.setLatLng(newPos);
    
    // Add to path
    pathPoints.push(newPos);
    pathLayer.setLatLngs(pathPoints);
    
    // Auto-center map if needed
    if (pathPoints.length === 1) {
        map.setView(newPos, 15);
    }
}

// Center map on boat position
function centerMapOnBoat() {
    if (pathPoints.length > 0) {
        map.setView(pathPoints[pathPoints.length - 1], 15);
    }
}

// Update 3D boat orientation based on IMU data
function updateBoatOrientation(imuData) {
    // Apply rotation to the entire scene
    // Using accelerometer data for pitch and roll
    const pitch = Math.atan2(imuData.accel.y, imuData.accel.z);
    const roll = Math.atan2(imuData.accel.x, imuData.accel.z);
    
    scene.rotation.x = pitch;
    scene.rotation.z = roll;
    
    // Update heading display
    document.getElementById('heading-value').textContent = 
        `${Math.round(roll * 180 / Math.PI)}°`;
}

// Camera control functions
function setupCameraControls() {
    console.log('Setting up camera controls...');
    
    // Check if camera controls exist in DOM
    const cameraButtons = document.querySelectorAll('.camera-btn[data-command]');
    const presetButtons = document.querySelectorAll('.preset-btn');
    
    console.log('Found camera buttons:', cameraButtons.length);
    console.log('Found preset buttons:', presetButtons.length);
    
    // Camera direction controls
    cameraButtons.forEach(btn => {
        console.log('Adding listeners to button:', btn.id);
        // Mouse/touch events for responsive control
        btn.addEventListener('mousedown', handleCameraControl);
        btn.addEventListener('touchstart', handleCameraControl);
        
        btn.addEventListener('mouseup', stopCameraControl);
        btn.addEventListener('touchend', stopCameraControl);
        btn.addEventListener('mouseleave', stopCameraControl);
    });
    
    // Camera preset buttons
    presetButtons.forEach(btn => {
        console.log('Adding listeners to preset button:', btn.getAttribute('data-preset'));
        btn.addEventListener('click', function() {
            const preset = this.getAttribute('data-preset');
            console.log('Preset clicked:', preset);
            sendServoCommand('preset', { name: preset });
        });
    });
    
    // Keyboard controls for camera
    document.addEventListener('keydown', handleKeyboardCamera);
    document.addEventListener('keyup', handleKeyboardCamera);
    
    console.log('Camera controls setup completed');
}

let cameraControlInterval = null;
let isControllingCamera = false;

function handleCameraControl(event) {
    event.preventDefault();
    
    const command = this.getAttribute('data-command');
    const direction = this.getAttribute('data-direction');
    
    if (command === 'center') {
        sendServoCommand('center');
        return;
    }
    
    // Start continuous control
    isControllingCamera = true;
    
    // Immediate first command
    sendServoCommand(command, { direction: direction, step: 2 });
    
    // Continue sending commands while button is held
    cameraControlInterval = setInterval(() => {
        if (isControllingCamera) {
            sendServoCommand(command, { direction: direction, step: 1 });
        }
    }, 100);
}

function stopCameraControl(event) {
    event.preventDefault();
    isControllingCamera = false;
    
    if (cameraControlInterval) {
        clearInterval(cameraControlInterval);
        cameraControlInterval = null;
    }
}

// Keyboard controls for camera (WASD)
const pressedKeys = new Set();

function handleKeyboardCamera(event) {
    if (event.type === 'keydown') {
        if (pressedKeys.has(event.code)) return; // Prevent repeat
        pressedKeys.add(event.code);
    } else {
        pressedKeys.delete(event.code);
    }
    
    // Handle camera movement keys
    switch(event.code) {
        case 'KeyW':
            if (event.type === 'keydown') {
                sendServoCommand('tilt', { direction: 'up', step: 2 });
            }
            break;
        case 'KeyS':
            if (event.type === 'keydown') {
                sendServoCommand('tilt', { direction: 'down', step: 2 });
            }
            break;
        case 'KeyA':
            if (event.type === 'keydown') {
                sendServoCommand('pan', { direction: 'left', step: 2 });
            }
            break;
        case 'KeyD':
            if (event.type === 'keydown') {
                sendServoCommand('pan', { direction: 'right', step: 2 });
            }
            break;
        case 'Space':
            if (event.type === 'keydown') {
                event.preventDefault();
                sendServoCommand('center');
            }
            break;
    }
}

// Send servo control command
function sendServoCommand(command, value = {}) {
    console.log('Sending servo command:', command, value);
    
    if (ws && ws.readyState === WebSocket.OPEN) {
        const message = {
            type: 'servo',
            command: command,
            value: value
        };
        console.log('Sending WebSocket message:', message);
        ws.send(JSON.stringify(message));
    } else {
        console.error('WebSocket not connected, state:', ws ? ws.readyState : 'null');
    }
}

// Update servo status display
function updateServoStatus(servoData) {
    if (servoData) {
        document.getElementById('pan-angle').textContent = `${Math.round(servoData.pan_angle)}°`;
        document.getElementById('tilt-angle').textContent = `${Math.round(servoData.tilt_angle)}°`;
    }
}

// Sample Management Functions
function setupSampleManagement() {
    // Refresh samples button
    document.getElementById('refresh-samples').addEventListener('click', () => {
        requestSampleData('get_all');
        requestSampleData('get_statistics');
    });
    
    // Show samples on map button
    document.getElementById('show-samples-map').addEventListener('click', () => {
        requestSampleData('get_all');
    });
    
    // Export buttons
    document.getElementById('export-geojson').addEventListener('click', () => {
        requestSampleData('export_geojson');
    });
    
    document.getElementById('export-csv').addEventListener('click', () => {
        requestSampleData('export_csv');
    });
    
    // Load initial data
    setTimeout(() => {
        requestSampleData('get_all');
        requestSampleData('get_statistics');
    }, 2000); // Wait 2 seconds after page load
}

function requestSampleData(command) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        const message = {
            type: 'samples',
            command: command
        };
        console.log('Requesting sample data:', command);
        ws.send(JSON.stringify(message));
    } else {
        console.error('WebSocket not connected for sample data request');
    }
}

function handleSampleData(data) {
    console.log('Received sample data:', data);
    
    switch (data.command) {
        case 'all_samples':
            displaySamples(data.samples);
            showSamplesOnMap(data.samples);
            break;
            
        case 'statistics':
            updateSampleStatistics(data.statistics);
            break;
            
        case 'geojson_exported':
            showExportMessage(data.message);
            break;
            
        case 'csv_exported':
            showExportMessage(data.message);
            break;
    }
}

function displaySamples(samples) {
    const samplesList = document.getElementById('samples-list');
    
    if (!samples || samples.length === 0) {
        samplesList.innerHTML = '<p class="no-samples">No samples collected yet</p>';
        return;
    }
    
    // Sort samples by timestamp (newest first)
    const sortedSamples = samples.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    // Display only the 10 most recent samples
    const recentSamples = sortedSamples.slice(0, 10);
    
    let html = '';
    recentSamples.forEach(sample => {
        const date = new Date(sample.timestamp);
        const timeStr = date.toLocaleString();
        
        html += `
            <div class="sample-item">
                <div class="sample-header">
                    <span class="sample-id">Sample #${sample.sample_id.slice(-8)}</span>
                    <span class="sample-time">${timeStr}</span>
                </div>
                <div class="sample-details">
                    Pump ${sample.pump_id} • Duration: ${sample.duration}s
                    ${sample.latitude && sample.longitude ? 
                        `<br><span class="sample-location">📍 ${sample.latitude.toFixed(6)}, ${sample.longitude.toFixed(6)}</span>` : 
                        '<br><span style="color: var(--warning)">⚠️ No GPS location</span>'
                    }
                </div>
            </div>
        `;
    });
    
    samplesList.innerHTML = html;
}

function showSamplesOnMap(samples) {
    // Clear existing sample markers
    sampleMarkers.forEach(marker => {
        map.removeLayer(marker);
    });
    sampleMarkers = [];
    
    if (!samples || samples.length === 0) return;
    
    // Add markers for each sample with location
    samples.forEach(sample => {
        if (sample.latitude && sample.longitude) {
            const sampleIcon = L.divIcon({
                className: 'sample-marker',
                html: `<div style="background: var(--success); border: 2px solid white; border-radius: 50%; width: 12px; height: 12px;"></div>`,
                iconSize: [12, 12],
                iconAnchor: [6, 6]
            });
            
            const marker = L.marker([sample.latitude, sample.longitude], {icon: sampleIcon});
            
            const popupContent = `
                <div class="sample-popup">
                    <div class="popup-title">Sample #${sample.sample_id.slice(-8)}</div>
                    <div><strong>Pump:</strong> ${sample.pump_id}</div>
                    <div><strong>Duration:</strong> ${sample.duration}s</div>
                    <div><strong>Time:</strong> ${new Date(sample.timestamp).toLocaleString()}</div>
                    <div><strong>Location:</strong> ${sample.latitude.toFixed(6)}, ${sample.longitude.toFixed(6)}</div>
                </div>
            `;
            
            marker.bindPopup(popupContent);
            marker.addTo(map);
            sampleMarkers.push(marker);
        }
    });
    
    console.log(`Added ${sampleMarkers.length} sample markers to map`);
}

function updateSampleStatistics(stats) {
    if (!stats) return;
    
    document.getElementById('total-samples').textContent = stats.total_samples || '0';
    document.getElementById('today-samples').textContent = stats.samples_today || '0';
    
    console.log('Updated sample statistics:', stats);
}

function showExportMessage(message) {
    // Create a simple notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success);
        color: white;
        padding: 15px;
        border-radius: 5px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    // Add slide-in animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.remove();
        style.remove();
    }, 5000);
}