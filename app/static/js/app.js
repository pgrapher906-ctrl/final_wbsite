// Global variables
let currentPage = 1;
let currentFilters = {
    water_type: '',
    start_date: '',
    end_date: '',
    sort_by: 'timestamp',
    sort_order: 'desc'
};

let gpsLocation = {
    latitude: null,
    longitude: null,
    accuracy: null,
    timestamp: null
};

// Helper function to handle API responses with authentication
function handleApiResponse(response) {
    if (response.status === 401) {
        // Redirect to login if unauthorized
        window.location.href = '/login';
        return null;
    }
    return response.json();
}

// Initialize app on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Water Quality Monitoring System initialized');
    
    // Load initial data
    loadReadings();
    loadStats();
    loadLocations();
    
    // Setup event listeners
    setupEventListeners();
    
    // Auto-refresh data every 30 seconds
    setInterval(loadReadings, 30000);
    setInterval(loadStats, 30000);
    
    // Fetch latest sensor data every 10 seconds
    setInterval(fetchLatestSensorData, 10000);
    
    // Load sensor data on startup
    fetchLatestSensorData();
});

// Setup event listeners
function setupEventListeners() {
    // GPS button
    document.getElementById('gpsButton').addEventListener('click', detectLocation);
    
    // Sensor form submission
    document.getElementById('sensorForm').addEventListener('submit', submitReading);
    
    // Filter form
    document.getElementById('filterWaterType').addEventListener('change', loadReadings);
    document.getElementById('filterStartDate').addEventListener('change', loadReadings);
    document.getElementById('filterEndDate').addEventListener('change', loadReadings);
    document.getElementById('sortBy').addEventListener('change', loadReadings);
}

// GPS Location Detection
function detectLocation() {
    const button = document.getElementById('gpsButton');
    const status = document.getElementById('locationStatus');
    
    button.disabled = true;
    button.classList.add('loading');
    const originalText = button.innerHTML;
    button.innerHTML = '<span id="gpsButtonText">⏳ Detecting...</span>';
    status.textContent = '';
    status.classList.remove('success', 'error');
    status.classList.add('loading');
    status.textContent = '🔍 Detecting your location...';
    
    if (!navigator.geolocation) {
        showLocationError('Geolocation is not supported by your browser');
        button.disabled = false;
        button.classList.remove('loading');
        button.innerHTML = originalText;
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            // Success
            gpsLocation.latitude = position.coords.latitude;
            gpsLocation.longitude = position.coords.longitude;
            gpsLocation.accuracy = position.coords.accuracy;
            gpsLocation.timestamp = new Date();
            
            // Update display
            document.getElementById('latitudeInput').value = gpsLocation.latitude.toFixed(6);
            document.getElementById('longitudeInput').value = gpsLocation.longitude.toFixed(6);
            document.getElementById('accuracyInput').value = gpsLocation.accuracy.toFixed(2) + ' meters';
            document.getElementById('updatedInput').value = gpsLocation.timestamp.toLocaleString();
            
            // Update status
            status.classList.remove('loading', 'error');
            status.classList.add('success');
            status.innerHTML = `✅ Location detected successfully!<br>📍 Latitude: <strong>${gpsLocation.latitude.toFixed(6)}</strong><br>📍 Longitude: <strong>${gpsLocation.longitude.toFixed(6)}</strong>`;
            
            // Show location on map in real-time
            showCurrentLocationOnMap(gpsLocation.latitude, gpsLocation.longitude);
            
            // Scroll to map to show location
            setTimeout(() => {
                document.getElementById('map-section').scrollIntoView({ behavior: 'smooth' });
            }, 300);
            
            button.disabled = false;
            button.classList.remove('loading');
            button.innerHTML = '<span id="gpsButtonText">🔄 Update Location</span>';
            
            // Auto-scroll to sensor form
            setTimeout(() => {
                document.getElementById('input-section').scrollIntoView({ behavior: 'smooth' });
            }, 1500);
            
            console.log('GPS Location:', gpsLocation);
        },
        function(error) {
            // Error
            showLocationError(getGeolocationErrorMessage(error));
            button.disabled = false;
            button.classList.remove('loading');
            button.innerHTML = originalText;
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

function getGeolocationErrorMessage(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            return '❌ Permission denied. Please enable location access in your browser settings.';
        case error.POSITION_UNAVAILABLE:
            return '❌ Position unavailable. Please check your GPS/location services.';
        case error.TIMEOUT:
            return '❌ Request timeout. Please try again.';
        default:
            return '❌ An error occurred: ' + error.message;
    }
}

function showLocationError(message) {
    const status = document.getElementById('locationStatus');
    status.classList.remove('loading', 'success');
    status.classList.add('error');
    status.textContent = message;
}

// Submit water quality reading
function submitReading(event) {
    event.preventDefault();
    
    // Validate GPS location
    if (!gpsLocation.latitude || !gpsLocation.longitude) {
        showSubmitStatus('Please detect GPS location first', 'error');
        return;
    }
    
    // Get form data
    const waterType = document.getElementById('waterType').value;
    if (!waterType) {
        showSubmitStatus('Please select a water type', 'error');
        return;
    }
    
    const formData = {
        timestamp: new Date().toISOString(),
        latitude: gpsLocation.latitude,
        longitude: gpsLocation.longitude,
        water_type: waterType,
        chlorophyll: getValue('chlorophyll'),
        pigments: getValue('pigments'),
        total_alkalinity: getValue('alkalinity'),
        dic: getValue('dic'),
        temperature: getValue('temperature'),
        sensor_id: document.getElementById('sensorId').value || null
    };
    
    // Show loading status
    showSubmitStatus('Submitting data...', 'info');
    
    // Send to backend
    fetch('/api/reading', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSubmitStatus('✅ Reading submitted successfully!', 'success');
            
            // Reset form
            document.getElementById('sensorForm').reset();
            
            // Reset GPS location for next reading
            gpsLocation = {
                latitude: null,
                longitude: null,
                accuracy: null,
                timestamp: null
            };
            document.getElementById('latitudeInput').value = '';
            document.getElementById('longitudeInput').value = '';
            document.getElementById('accuracyInput').value = '';
            document.getElementById('updatedInput').value = '';
            
            // Reload data
            loadReadings();
            loadStats();
            loadLocations();
            
            // Clear status after 3 seconds
            setTimeout(() => {
                showSubmitStatus('', '');
            }, 3000);
        } else {
            showSubmitStatus('❌ Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showSubmitStatus('❌ Error: ' + error.message, 'error');
    });
}

function getValue(id) {
    const value = document.getElementById(id).value;
    return value ? parseFloat(value) : null;
}

function showSubmitStatus(message, type) {
    const status = document.getElementById('submitStatus');
    status.textContent = message;
    status.className = 'status-message';
    if (message) {
        status.classList.add('show', type);
    }
}

// Load water quality readings
function loadReadings(page = 1) {
    currentPage = page;
    
    // Get filter values
    currentFilters.water_type = document.getElementById('filterWaterType').value;
    currentFilters.start_date = document.getElementById('filterStartDate').value;
    currentFilters.end_date = document.getElementById('filterEndDate').value;
    currentFilters.sort_by = document.getElementById('sortBy').value;
    
    // Build query string
    let queryParams = new URLSearchParams({
        page: page,
        per_page: 20,
        sort_by: currentFilters.sort_by,
        sort_order: currentFilters.sort_order
    });
    
    if (currentFilters.water_type) {
        queryParams.append('water_type', currentFilters.water_type);
    }
    if (currentFilters.start_date) {
        queryParams.append('start_date', currentFilters.start_date + 'T00:00:00');
    }
    if (currentFilters.end_date) {
        queryParams.append('end_date', currentFilters.end_date + 'T23:59:59');
    }
    
    // Fetch data
    fetch('/api/readings?' + queryParams.toString())
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            populateTable(data.data);
            populatePagination(data.pagination);
        } else {
            console.error('Error loading readings:', data.error);
            document.getElementById('tableBody').innerHTML = 
                '<tr><td colspan="12" class="text-center">Error loading data</td></tr>';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('tableBody').innerHTML = 
            '<tr><td colspan="12" class="text-center">Error loading data</td></tr>';
    });
}

function populateTable(readings) {
    const tbody = document.getElementById('tableBody');
    
    if (readings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="12" class="text-center">No data available</td></tr>';
        return;
    }
    
    tbody.innerHTML = readings.map(reading => `
        <tr>
            <td>${reading.date}</td>
            <td>${reading.time}</td>
            <td>${reading.latitude}</td>
            <td>${reading.longitude}</td>
            <td>${capitalizeFirst(reading.water_type)}</td>
            <td>${reading.chlorophyll !== null ? reading.chlorophyll.toFixed(2) : '--'}</td>
            <td>${reading.pigments !== null ? reading.pigments.toFixed(2) : '--'}</td>
            <td>${reading.total_alkalinity !== null ? reading.total_alkalinity.toFixed(2) : '--'}</td>
            <td>${reading.dic !== null ? reading.dic.toFixed(2) : '--'}</td>
            <td>${reading.temperature !== null ? reading.temperature.toFixed(1) : '--'}</td>
            <td>${reading.sensor_id || '--'}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-danger btn-small" onclick="deleteReading(${reading.id})">Delete</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function populatePagination(pagination) {
    const paginationDiv = document.getElementById('pagination');
    let html = '';
    
    // Previous button
    if (pagination.page > 1) {
        html += `<button onclick="loadReadings(${pagination.page - 1})">← Previous</button>`;
    }
    
    // Page buttons
    for (let i = 1; i <= pagination.pages; i++) {
        if (i === pagination.page) {
            html += `<button class="active">${i}</button>`;
        } else {
            html += `<button onclick="loadReadings(${i})">${i}</button>`;
        }
    }
    
    // Next button
    if (pagination.page < pagination.pages) {
        html += `<button onclick="loadReadings(${pagination.page + 1})">Next →</button>`;
    }
    
    paginationDiv.innerHTML = html;
}

// Delete reading
function deleteReading(id) {
    if (confirm('Are you sure you want to delete this reading?')) {
        fetch(`/api/reading/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadReadings();
                showSubmitStatus('✅ Reading deleted successfully', 'success');
                setTimeout(() => {
                    showSubmitStatus('', '');
                }, 3000);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

// Load statistics
function loadStats() {
    fetch('/api/stats')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const stats = data.data;
            document.getElementById('totalReadings').textContent = stats.total_readings;
            document.getElementById('avgTemperature').textContent = 
                stats.average_temperature !== null ? stats.average_temperature.toFixed(1) : '--';
            document.getElementById('avgChlorophyll').textContent = 
                stats.average_chlorophyll !== null ? stats.average_chlorophyll.toFixed(2) : '--';
            document.getElementById('waterTypesCount').textContent = stats.water_types_count;
        }
    })
    .catch(error => console.error('Error loading stats:', error));
}

// Global map variable
let map = null;
let markers = [];
let currentLocationMarker = null;

// Initialize Leaflet map
function initializeMap() {
    if (!map) {
        map = L.map('map').setView([40.7128, -74.0060], 4); // Default to NYC
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19,
            tileSize: 256
        }).addTo(map);
    }
}

// Show current GPS location on map
function showCurrentLocationOnMap(latitude, longitude) {
    // Initialize map if not already done
    initializeMap();
    
    // Remove previous current location marker
    if (currentLocationMarker) {
        map.removeLayer(currentLocationMarker);
    }
    
    // Create a marker for current GPS location with a distinctive style
    const currentIcon = L.divIcon({
        html: `<div style="
            background-color: #f44336;
            color: white;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            border: 4px solid white;
            box-shadow: 0 0 0 3px #f44336, 0 4px 12px rgba(244, 67, 54, 0.4);
            position: relative;
        ">
            📍
        </div>`,
        iconSize: [50, 50],
        className: 'current-location-marker'
    });
    
    currentLocationMarker = L.marker([latitude, longitude], {
        icon: currentIcon,
        title: 'Your Current Location'
    }).bindPopup(`
        <div style="text-align: center; padding: 10px;">
            <strong>Your Current Location</strong><br>
            📍 Latitude: ${latitude.toFixed(6)}<br>
            📍 Longitude: ${longitude.toFixed(6)}<br>
            <small style="color: #999;">Click Submit to save this reading</small>
        </div>
    `, { maxWidth: 300 }).addTo(map).openPopup();
    
    // Center and zoom to current location
    map.setView([latitude, longitude], 15);
}

function loadLocations() {
    // Initialize map if not already done
    initializeMap();
    
    fetch('/api/locations')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const locationsList = document.getElementById('locationsList');
            
            // Clear existing markers
            markers.forEach(marker => map.removeLayer(marker));
            markers = [];
            
            if (data.data.length === 0) {
                locationsList.innerHTML = '<p style="text-align: center; color: #999;">No measurement locations yet</p>';
                // Show default view
                map.setView([40.7128, -74.0060], 4);
            } else {
                // Add markers and build list
                let bounds = L.latLngBounds();
                let locationsHtml = '<div style="display: flex; flex-direction: column; gap: 0.5rem;">';
                
                data.data.forEach((loc, index) => {
                    const lat = parseFloat(loc.latitude);
                    const lng = parseFloat(loc.longitude);
                    
                    // Create custom marker icon based on water type
                    let markerColor = '#0088cc';
                    let markerIcon = '🌊';
                    
                    if (loc.water_type === 'drinking') markerColor = '#10b981';
                    else if (loc.water_type === 'groundwater') markerColor = '#8b5cf6';
                    else if (loc.water_type === 'ocean') markerColor = '#0088cc';
                    
                    // Create marker with custom HTML
                    const marker = L.marker([lat, lng], {
                        title: `${capitalizeFirst(loc.water_type)} Water`,
                        icon: L.divIcon({
                            html: `<div style="background-color: ${markerColor}; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-size: 20px; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">${markerIcon}</div>`,
                            iconSize: [40, 40],
                            className: 'custom-marker'
                        })
                    }).bindPopup(`<strong>${capitalizeFirst(loc.water_type)} Water</strong><br>📍 ${lat.toFixed(6)}, ${lng.toFixed(6)}`);
                    
                    marker.addTo(map);
                    markers.push(marker);
                    bounds.extend([lat, lng]);
                    
                    // Add to list
                    locationsHtml += `
                        <div class="location-item">
                            <div class="location-details">
                                <strong style="color: ${markerColor}">${capitalizeFirst(loc.water_type)}</strong>
                                <div class="location-coords">📍 ${lat.toFixed(6)}, ${lng.toFixed(6)}</div>
                            </div>
                            <span class="location-type">${loc.water_type.toUpperCase()}</span>
                        </div>
                    `;
                });
                
                locationsHtml += '</div>';
                locationsList.innerHTML = locationsHtml;
                
                // Fit map to show all markers
                if (bounds.isValid()) {
                    map.fitBounds(bounds, { padding: [50, 50] });
                }
            }
        }
    })
    .catch(error => console.error('Error loading locations:', error));
}

// Export to Excel
function exportToExcel() {
    let queryParams = new URLSearchParams();
    
    if (currentFilters.water_type) {
        queryParams.append('water_type', currentFilters.water_type);
    }
    if (currentFilters.start_date) {
        queryParams.append('start_date', currentFilters.start_date + 'T00:00:00');
    }
    if (currentFilters.end_date) {
        queryParams.append('end_date', currentFilters.end_date + 'T23:59:59');
    }
    
    window.location.href = '/api/export/excel?' + queryParams.toString();
}

// Reset filters
function resetFilters() {
    document.getElementById('filterWaterType').value = '';
    document.getElementById('filterStartDate').value = '';
    document.getElementById('filterEndDate').value = '';
    document.getElementById('sortBy').value = 'timestamp';
    loadReadings();
}

// Utility functions
function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ');
}

// Fetch latest sensor data from IoT hardware
function fetchLatestSensorData() {
    fetch('/api/sensor/latest')
    .then(response => response.json())
    .then(data => {
        if (data.success && data.data) {
            displaySensorData(data.data);
        }
    })
    .catch(error => console.log('No new sensor data'));
}

// Display sensor data in form fields
function displaySensorData(reading) {
    // Update location if available
    if (reading.latitude && reading.longitude) {
        gpsLocation.latitude = reading.latitude;
        gpsLocation.longitude = reading.longitude;
        gpsLocation.timestamp = new Date(reading.timestamp);
        
        document.getElementById('latitudeInput').value = reading.latitude.toFixed(6);
        document.getElementById('longitudeInput').value = reading.longitude.toFixed(6);
        document.getElementById('updatedInput').value = new Date(reading.timestamp).toLocaleString();
        
        const statusDiv = document.getElementById('locationStatus');
        statusDiv.classList.remove('loading', 'error');
        statusDiv.classList.add('success');
        statusDiv.innerHTML = `✅ Sensor Location Detected<br>Lat: ${reading.latitude.toFixed(6)}, Lon: ${reading.longitude.toFixed(6)}`;
    }
    
    // Update water quality parameters in form
    if (reading.water_type) {
        document.getElementById('waterType').value = reading.water_type;
    }
    if (reading.chlorophyll !== null && reading.chlorophyll !== undefined) {
        document.getElementById('chlorophyll').value = reading.chlorophyll;
    }
    if (reading.pigments !== null && reading.pigments !== undefined) {
        document.getElementById('pigments').value = reading.pigments;
    }
    if (reading.total_alkalinity !== null && reading.total_alkalinity !== undefined) {
        document.getElementById('alkalinity').value = reading.total_alkalinity;
    }
    if (reading.dic !== null && reading.dic !== undefined) {
        document.getElementById('dic').value = reading.dic;
    }
    if (reading.temperature !== null && reading.temperature !== undefined) {
        document.getElementById('temperature').value = reading.temperature;
    }
    if (reading.sensor_id) {
        document.getElementById('sensorId').value = reading.sensor_id;
    }
    
    // Show notification
    showSensorNotification(`📡 New sensor data received from ${reading.sensor_id || 'Hardware'}`, 'info');
}

// Show sensor notification
function showSensorNotification(message, type) {
    // Create notification element if not exists
    let notif = document.getElementById('sensorNotification');
    if (!notif) {
        notif = document.createElement('div');
        notif.id = 'sensorNotification';
        notif.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 6px;
            font-weight: 600;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        document.body.appendChild(notif);
    }
    
    notif.textContent = message;
    if (type === 'info') {
        notif.style.background = '#d1ecf1';
        notif.style.color = '#0c5460';
        notif.style.border = '1px solid #bee5eb';
    }
    notif.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        notif.style.display = 'none';
    }, 5000);
}

// Utility functions
function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ');
}
