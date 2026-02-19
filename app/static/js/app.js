/**
 * NRSC AquaFlow Dashboard Logic
 * Version: 2.1 (Viewer Optimized)
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // --- Global Variables ---
    let map = null;
    let markersLayer = null;
    let userMarker = null;
    let allData = []; // Stores all fetched data for filtering

    // --- 1. Initialize Map ---
    function initMap() {
        // Default Center: India
        map = L.map('map').setView([20.5937, 78.9629], 5);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        markersLayer = L.layerGroup().addTo(map);
    }

    // --- 2. Fetch Data from API ---
    function loadDashboardData() {
        const tableBody = document.getElementById('data-table-body');
        
        fetch('/api/data')
            .then(response => {
                if (!response.ok) throw new Error("Network response was not ok");
                return response.json();
            })
            .then(data => {
                allData = data; // Save data globally
                renderDashboard(data); // Render everything
            })
            .catch(error => {
                console.error('Error:', error);
                tableBody.innerHTML = `<tr><td colspan="9" class="text-center text-danger">Error loading data: ${error.message}</td></tr>`;
            });
    }

    // --- 3. Render Table and Map ---
    function renderDashboard(data) {
        const tableBody = document.getElementById('data-table-body');
        tableBody.innerHTML = ''; // Clear existing rows
        markersLayer.clearLayers(); // Clear existing map pins

        if (data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">No records found for this selection.</td></tr>`;
            return;
        }

        data.forEach(row => {
            // A. Add Map Marker
            const markerColor = row.water_type.toLowerCase().includes('ocean') ? 'blue' : 'grey';
            const popupContent = `
                <b>${row.water_type}</b><br>
                pH: ${row.ph || 'N/A'}<br>
                TDS: ${row.tds || 'N/A'}<br>
                <small>${new Date(row.timestamp).toLocaleString()}</small>
            `;
            
            const marker = L.marker([row.latitude, row.longitude])
                .bindPopup(popupContent);
            markersLayer.addLayer(marker);

            // B. Add Table Row
            const tr = document.createElement('tr');
            
            // Badge Logic
            const badgeClass = row.water_type.toLowerCase().includes('ocean') ? 'bg-primary' : 'bg-secondary';
            
            // Image Button Logic
            const imageBtn = row.has_image 
                ? `<a href="/image/${row.id}" target="_blank" class="btn btn-sm btn-outline-primary"><i class="fas fa-image"></i> View</a>` 
                : '<span class="text-muted">-</span>';

            tr.innerHTML = `
                <td>${new Date(row.timestamp).toLocaleString()}</td>
                <td><span class="badge ${badgeClass}">${row.water_type}</span></td>
                <td>${row.latitude.toFixed(4)}</td>
                <td>${row.longitude.toFixed(4)}</td>
                <td>${row.pin_id || '--'}</td>
                <td>${row.ph || '--'}</td>
                <td>${row.tds || '--'}</td>
                <td>${row.temperature || '--'}°C</td>
                <td>${imageBtn}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // --- 4. GPS Detection Logic ---
    const btnDetect = document.getElementById('btn-detect');
    if (btnDetect) {
        btnDetect.addEventListener('click', function() {
            const originalText = btnDetect.innerHTML;
            
            if (!navigator.geolocation) {
                alert("Geolocation is not supported by your browser.");
                return;
            }

            btnDetect.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Locating...';
            btnDetect.disabled = true;

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    // Success
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;

                    // Update Inputs
                    document.getElementById('lat-input').value = lat.toFixed(6);
                    document.getElementById('lon-input').value = lon.toFixed(6);

                    // Move Map
                    map.setView([lat, lon], 12);

                    // Add User Marker
                    if (userMarker) map.removeLayer(userMarker);
                    userMarker = L.marker([lat, lon], {
                        icon: L.divIcon({
                            className: 'user-location-dot',
                            html: '<div style="width:15px;height:15px;background:red;border-radius:50%;border:2px solid white;box-shadow:0 0 5px rgba(0,0,0,0.5);"></div>'
                        })
                    }).addTo(map).bindPopup("<b>You are here</b>").openPopup();

                    btnDetect.innerHTML = '<i class="fas fa-check"></i> Location Found';
                    btnDetect.classList.remove('btn-detect');
                    btnDetect.classList.add('btn-success');
                    btnDetect.disabled = false;
                },
                (error) => {
                    // Error
                    console.error("GPS Error:", error);
                    alert("Unable to retrieve location. Please allow GPS access.");
                    btnDetect.innerHTML = originalText;
                    btnDetect.disabled = false;
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        });
    }

    // --- 5. Filtering Logic (Ocean vs Pond) ---
    const filterBtns = document.querySelectorAll('.filter-btn');
    const exportBtn = document.getElementById('btn-export');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // 1. Update Buttons Visual
            filterBtns.forEach(b => b.style.opacity = '0.6');
            this.style.opacity = '1';

            // 2. Filter Data
            const type = this.getAttribute('data-type'); // "Ocean" or "Pond"
            console.log("Filtering by:", type);

            if (type === 'All') {
                renderDashboard(allData);
            } else {
                const filtered = allData.filter(item => 
                    item.water_type.toLowerCase().includes(type.toLowerCase())
                );
                renderDashboard(filtered);
            }

            // 3. Update Export Link
            exportBtn.href = `/export/${type}`;
        });
    });

    // --- Start Application ---
    initMap();
    loadDashboardData();
});
