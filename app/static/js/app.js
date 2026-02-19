document.addEventListener('DOMContentLoaded', function() {
    // 1. Initialize Map
    let map = L.map('map').setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);
    
    let markersLayer = L.layerGroup().addTo(map);
    let allData = [];

    const oceanSubtypes = ['open ocean water', 'coastal water', 'estuarine water', 'deep sea water', 'marine surface water'];

    // 2. Render Dashboard (Table + Map Points)
    function renderDashboard(data, activeFilter = 'All') {
        const headerRow = document.getElementById('table-headers');
        const tableBody = document.getElementById('data-table-body');
        
        // Dynamic Header based on Project
        const isPondView = activeFilter === 'Pond Water';
        headerRow.innerHTML = `
            <th>TIME</th><th>TYPE</th><th>COORDINATES</th>
            <th>PH</th><th>TDS (PPM)</th>${isPondView ? '<th>DO (PPM)</th>' : ''}
            <th>TEMP</th><th class="text-center">EVIDENCE</th>
        `;

        tableBody.innerHTML = '';
        markersLayer.clearLayers(); // Clear map before redrawing

        if (!data || data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="9" class="text-center p-4">No records found.</td></tr>`;
            return;
        }

        data.forEach(row => {
            const tr = document.createElement('tr');
            const wType = (row.water_type || '').toLowerCase();
            const isOcean = oceanSubtypes.includes(wType) || wType.includes('ocean');
            
            // --- POINT VIEW ON MAP ---
            if (row.latitude && row.longitude) {
                const markerColor = isOcean ? '#0077be' : '#4a7c59';
                const marker = L.circleMarker([row.latitude, row.longitude], {
                    radius: 9,
                    fillColor: markerColor,
                    color: "#fff",
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                }).bindPopup(`<b>${row.water_type}</b><br>pH: ${row.ph}<br>TDS: ${row.tds} PPM`);
                
                markersLayer.addLayer(marker);
            }

            // Table Body
            tr.innerHTML = `
                <td>${new Date(row.timestamp).toLocaleString()}</td>
                <td><span class="badge ${isOcean ? 'badge-ocean' : 'badge-pond'}">${row.water_type}</span></td>
                <td class="small font-monospace">${parseFloat(row.latitude).toFixed(4)}, ${parseFloat(row.longitude).toFixed(4)}</td>
                <td>${row.ph || '-'}</td><td>${row.tds || '-'}</td>
                ${isPondView ? `<td>${row.do || '-'}</td>` : ''}
                <td>${row.temperature}°C</td>
                <td class="text-center">
                    ${row.has_image ? `<a href="/image/${row.id}" target="_blank" class="btn btn-sm btn-link">View</a>` : '-'}
                </td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // 3. Filter Buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const type = this.getAttribute('data-type');
            
            let filtered = (type === 'All') ? allData : allData.filter(d => 
                (type === 'Ocean') ? (oceanSubtypes.includes(d.water_type.toLowerCase()) || d.water_type.toLowerCase().includes('ocean')) : d.water_type === type
            );
            renderDashboard(filtered, type);
        });
    });

    // 4. GPS Button
    document.getElementById('btn-detect').addEventListener('click', function() {
        navigator.geolocation.getCurrentPosition(pos => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            document.getElementById('lat-input').value = lat.toFixed(6);
            document.getElementById('lon-input').value = lon.toFixed(6);
            map.setView([lat, lon], 14);
            L.marker([lat, lon]).addTo(map).bindPopup("Current Acquisition Position").openPopup();
        });
    });

    fetch('/api/data').then(res => res.json()).then(data => {
        allData = data || [];
        renderDashboard(allData);
    });
});
