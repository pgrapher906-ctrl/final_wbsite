document.addEventListener('DOMContentLoaded', function() {
    let map = L.map('map').setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    let markersLayer = L.layerGroup().addTo(map);
    let allData = [];

    const oceanSubtypes = ['open ocean water', 'coastal water', 'estuarine water', 'deep sea water', 'marine surface water'];

    // --- Dynamic Render Dashboard ---
    function renderDashboard(data, currentFilter = 'All') {
        const headerRow = document.getElementById('table-headers');
        const tableBody = document.getElementById('data-table-body');
        
        // Dynamic Header Logic
        const isPondView = currentFilter === 'Pond Water';
        headerRow.innerHTML = `
            <th>Acquisition Time</th><th>Classification</th><th>Coordinates</th>
            <th>pH Level</th><th>TDS (PPM)</th>${isPondView ? '<th>DO (PPM)</th>' : ''}
            <th>Temp</th><th class="text-center">Evidence</th>
        `;

        tableBody.innerHTML = '';
        if (!data || data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="9" class="text-center p-4">No records found.</td></tr>`;
            return;
        }

        data.forEach(row => {
            const wType = row.water_type ? String(row.water_type) : 'Unknown';
            const isOcean = oceanSubtypes.includes(wType.toLowerCase());
            
            // Map Visuals
            const markerColor = isOcean ? '#0077be' : '#4a7c59';
            L.circleMarker([row.latitude, row.longitude], { radius: 8, fillColor: markerColor, color: "#fff", weight: 2, fillOpacity: 0.8 })
                .bindPopup(`<b>${wType}</b><br>pH: ${row.ph}<br>Temp: ${row.temperature}°C`)
                .addTo(markersLayer);

            // Table Row
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${new Date(row.timestamp).toLocaleString()}</td>
                <td><span class="badge ${isOcean ? 'badge-ocean' : 'badge-pond'}">${wType}</span></td>
                <td>${row.latitude.toFixed(4)}, ${row.longitude.toFixed(4)}</td>
                <td>${row.ph || '-'}</td><td>${row.tds || '-'}</td>
                ${isPondView ? `<td>${row.do || '-'}</td>` : ''}
                <td>${row.temperature ? row.temperature + '°C' : '-'}</td>
                <td class="text-center">${row.has_image ? `<a href="/image/${row.id}" target="_blank" class="btn btn-sm btn-link">View</a>` : '-'}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // Fetch initial data
    fetch('/api/data').then(res => res.json()).then(data => {
        allData = data || [];
        renderDashboard(allData);
    });

    // Filtering logic
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const type = this.getAttribute('data-type');
            
            let filtered = (type === 'All') ? allData : allData.filter(d => 
                (type === 'Ocean') ? oceanSubtypes.includes(d.water_type.toLowerCase()) : d.water_type === type
            );
            renderDashboard(filtered, type);
        });
    });

    // GPS Logic
    document.getElementById('btn-detect').addEventListener('click', function() {
        navigator.geolocation.getCurrentPosition(pos => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            document.getElementById('lat-input').value = lat.toFixed(6);
            document.getElementById('lon-input').value = lon.toFixed(6);
            map.setView([lat, lon], 12);
        });
    });
});
