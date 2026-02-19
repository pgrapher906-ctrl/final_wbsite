document.addEventListener('DOMContentLoaded', function() {
    console.log("NRSC AquaFlow Dashboard JS Initialized");

    let map = null;
    let markersLayer = null;
    let userMarker = null;
    let allData = [];

    // Define the list of subtypes that belong to the "Ocean" group
    const oceanSubtypes = [
        'open ocean water', 
        'coastal water', 
        'estuarine water', 
        'deep sea water', 
        'marine surface water'
    ];

    // --- 1. Initialize Map ---
    try {
        map = L.map('map').setView([20.5937, 78.9629], 5);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        markersLayer = L.layerGroup().addTo(map);
    } catch (e) {
        console.error("Map initialization failed:", e);
    }

    // --- 2. Fetch Data ---
    const tableBody = document.getElementById('data-table-body');
    
    fetch('/api/data')
        .then(response => {
            if (!response.ok) throw new Error("Network response was not OK");
            return response.json();
        })
        .then(data => {
            allData = data || [];
            renderDashboard(allData);
        })
        .catch(error => {
            console.error('Fetch Data Error:', error);
            tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">Error: Could not load data from server.</td></tr>`;
        });

    // --- 3. Render Dashboard ---
    function renderDashboard(data) {
        tableBody.innerHTML = ''; 
        if (markersLayer) markersLayer.clearLayers(); 

        if (!data || data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-muted">No records found.</td></tr>`;
            return;
        }

        data.forEach(row => {
            const wType = row.water_type ? String(row.water_type) : 'Unknown';
            const lat = parseFloat(row.latitude) || 0;
            const lon = parseFloat(row.longitude) || 0;
            
            // Check if this type belongs to the Ocean group
            const isOcean = oceanSubtypes.includes(wType.toLowerCase()) || wType.toLowerCase().includes('ocean');

            // Draw Map Circle Markers (Color-Coded)
            if (lat !== 0 && lon !== 0 && markersLayer) {
                const markerColor = isOcean ? '#0077be' : '#4a7c59'; // Blue for Ocean, Green for Pond
                
                const marker = L.circleMarker([lat, lon], {
                    radius: 8,
                    fillColor: markerColor,
                    color: "#fff",
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                }).bindPopup(`<b>${wType}</b><br>pH: ${row.ph || 'N/A'}<br>Temp: ${row.temperature || 'N/A'}°C`);
                
                markersLayer.addLayer(marker);
            }

            // Draw Table Row
            const tr = document.createElement('tr');
            const badgeClass = isOcean ? 'badge-ocean' : 'badge-pond';
            
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
                        userMarker = L.marker([lat, lon]).addTo(map).bindPopup("<b>Your Current Position</b>").openPopup();
                    }
                    
                    btnDetect.innerHTML = '<i class="fas fa-check"></i> Location Found';
                    btnDetect.className = 'btn btn-success btn-sm fw-bold';
                    btnDetect.disabled = false;
                },
                (err) => {
                    alert("GPS Error. Please ensure location access is allowed.");
                    btnDetect.innerHTML = '<i class="fas fa-crosshairs"></i> GET CURRENT GPS';
                    btnDetect.disabled = false;
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        });
    }

    // --- 5. Professional Group Filtering ---
    const filterBtns = document.querySelectorAll('.filter-btn');
    const exportBtn = document.getElementById('btn-export');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const filterType = this.getAttribute('data-type'); 
            
            let filtered = allData;

            if (filterType === 'Ocean') {
                // Filter for ALL ocean subtypes
                filtered = allData.filter(item => 
                    oceanSubtypes.includes((item.water_type || '').toLowerCase()) || 
                    (item.water_type || '').toLowerCase().includes('ocean')
                );
            } else if (filterType === 'Pond') {
                filtered = allData.filter(item => 
                    (item.water_type || '').toLowerCase().includes('pond')
                );
            } else if (filterType !== 'All') {
                // Filter for a specific subtype (e.g., "Coastal Water")
                filtered = allData.filter(item => item.water_type === filterType);
            }

            renderDashboard(filtered);
        });
    });
});
