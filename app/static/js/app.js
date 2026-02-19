document.addEventListener('DOMContentLoaded', function() {
    console.log("AquaFlow Dashboard JS Initialized");

    let map = null;
    let markersLayer = null;
    let userMarker = null;
    let allData = [];

    // --- 1. Initialize Map (Crash-Proof) ---
    try {
        // Center on India by default
        map = L.map('map').setView([20.5937, 78.9629], 5);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        markersLayer = L.layerGroup().addTo(map);
    } catch (e) {
        console.error("Map initialization failed:", e);
    }

    // --- 2. Fetch Data from API ---
    const tableBody = document.getElementById('data-table-body');
    
    fetch('/api/data')
        .then(response => {
            if (!response.ok) throw new Error("Network response was not OK");
            return response.json();
        })
        .then(data => {
            console.log(`Loaded ${data.length} records from database.`);
            allData = data || [];
            renderDashboard(allData);
        })
        .catch(error => {
            console.error('Fetch Data Error:', error);
            tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">Error: Could not load data from server.</td></tr>`;
        });

    // --- 3. Render Dashboard (Table & Map) ---
    function renderDashboard(data) {
        tableBody.innerHTML = ''; 
        if (markersLayer) markersLayer.clearLayers(); 

        if (!data || data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-muted">No records found.</td></tr>`;
            return;
        }

        data.forEach(row => {
            // Safe Data Parsing (prevents blank screens if a row is empty)
            const wType = row.water_type ? String(row.water_type) : 'Unknown';
            const lat = parseFloat(row.latitude) || 0;
            const lon = parseFloat(row.longitude) || 0;
            const isOcean = wType.toLowerCase().includes('ocean');

            // Draw Map Pin
            if (lat !== 0 && lon !== 0 && markersLayer) {
                const marker = L.marker([lat, lon]).bindPopup(`<b>${wType}</b><br>pH: ${row.ph || 'N/A'}<br>Temp: ${row.temperature || 'N/A'}°C`);
                markersLayer.addLayer(marker);
            }

            // Draw Table Row
            const tr = document.createElement('tr');
            const badgeClass = isOcean ? 'bg-primary' : 'bg-secondary';
            
            // Image Button
            const imageBtn = row.has_image 
                ? `<a href="/image/${row.id}" target="_blank" class="btn btn-sm btn-outline-primary"><i class="fas fa-image"></i> View</a>` 
                : '<span class="text-muted">-</span>';

            tr.innerHTML = `
                <td>${row.timestamp ? new Date(row.timestamp).toLocaleString() : 'N/A'}</td>
                <td><span class="badge ${badgeClass}">${wType}</span></td>
                <td>${lat.toFixed(4)}</td>
                <td>${lon.toFixed(4)}</td>
                <td>${row.ph !== null ? row.ph : '-'}</td>
                <td>${row.tds !== null ? row.tds : '-'}</td>
                <td>${row.temperature !== null ? row.temperature + '°C' : '-'}</td>
                <td>${imageBtn}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // --- 4. GPS Location Logic ---
    const btnDetect = document.getElementById('btn-detect');
    if (btnDetect) {
        btnDetect.addEventListener('click', function() {
            if (!navigator.geolocation) {
                alert("Geolocation is not supported by your browser.");
                return;
            }
            
            const originalText = btnDetect.innerHTML;
            btnDetect.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Locating...';
            btnDetect.disabled = true;

            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    
                    document.getElementById('lat-input').value = lat.toFixed(6);
                    document.getElementById('lon-input').value = lon.toFixed(6);
                    
                    if (map) {
                        map.setView([lat, lon], 12);
                        if (userMarker) map.removeLayer(userMarker);
                        
                        // Add a distinct red marker for the user
                        userMarker = L.marker([lat, lon], {
                            icon: L.divIcon({
                                className: 'custom-user-marker',
                                html: '<div style="background:red;width:14px;height:14px;border-radius:50%;border:2px solid white;box-shadow:0 0 4px rgba(0,0,0,0.5);"></div>'
                            })
                        }).addTo(map).bindPopup("<b>You are here</b>").openPopup();
                    }
                    
                    btnDetect.innerHTML = '<i class="fas fa-check"></i> Location Found';
                    btnDetect.className = 'btn btn-success mb-3';
                    btnDetect.disabled = false;
                },
                (err) => {
                    console.error("GPS Error:", err);
                    alert("GPS Error. Please ensure location access is allowed in your browser.");
                    btnDetect.innerHTML = originalText;
                    btnDetect.disabled = false;
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        });
    }

    // --- 5. Project Filtering Logic ---
    const filterBtns = document.querySelectorAll('.filter-btn');
    const exportBtn = document.getElementById('btn-export');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Visual Toggle
            filterBtns.forEach(b => b.style.opacity = '0.6');
            this.style.opacity = '1';

            const type = this.getAttribute('data-type'); // Ocean, Pond, or All
            
            // Filter Data
            if (type === 'All') {
                renderDashboard(allData);
            } else {
                const filtered = allData.filter(item => 
                    (item.water_type || '').toLowerCase().includes(type.toLowerCase())
                );
                renderDashboard(filtered);
            }
            
            // Update the Export URL
            exportBtn.href = `/export/${type}`;
        });
    });
});
