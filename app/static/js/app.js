document.addEventListener('DOMContentLoaded', function() {
    let map = L.map('map').setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    let markersLayer = L.layerGroup().addTo(map);
    let allData = [];

    const oceanSubtypes = ['open ocean water', 'coastal water', 'estuarine water', 'deep sea water', 'marine surface water'];

    function renderDashboard(data, activeFilter = 'All') {
        const headerRow = document.getElementById('table-headers');
        const tableBody = document.getElementById('data-table-body');
        
        // Dynamic Header
        const isPondView = activeFilter === 'Pond Water';
        headerRow.innerHTML = `
            <th>TIME</th><th>TYPE</th><th>COORDINATES</th>
            <th>PH</th><th>TDS (PPM)</th>${isPondView ? '<th>DO (PPM)</th>' : ''}
            <th>TEMP</th><th class="text-center">EVIDENCE</th>
        `;

        tableBody.innerHTML = '';
        markersLayer.clearLayers(); // REDRAW MAP POINTS

        data.forEach(row => {
            const tr = document.createElement('tr');
            const isOcean = oceanSubtypes.includes(row.water_type.toLowerCase()) || row.water_type.toLowerCase().includes('ocean');
            
            // Map Marker Logic
            if (row.latitude && row.longitude) {
                const markerColor = isOcean ? '#0077be' : '#4a7c59';
                L.circleMarker([row.latitude, row.longitude], { radius: 8, fillColor: markerColor, color: "#fff", weight: 2, fillOpacity: 0.8 })
                    .bindPopup(`<b>${row.water_type}</b><br>pH: ${row.ph}`).addTo(markersLayer);
            }

            tr.innerHTML = `
                <td>${new Date(row.timestamp).toLocaleTimeString()}</td>
                <td><span class="badge ${isOcean ? 'badge-ocean' : 'badge-pond'}">${row.water_type}</span></td>
                <td>${parseFloat(row.latitude).toFixed(4)}, ${parseFloat(row.longitude).toFixed(4)}</td>
                <td>${row.ph || '-'}</td><td>${row.tds || '-'}</td>
                ${isPondView ? `<td>${row.do || '-'}</td>` : ''}
                <td>${row.temperature}°C</td>
                <td class="text-center">${row.has_image ? `<a href="/image/${row.id}" target="_blank" class="btn btn-sm btn-link">View</a>` : '-'}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // GPS
    document.getElementById('btn-detect').addEventListener('click', function() {
        navigator.geolocation.getCurrentPosition(pos => {
            document.getElementById('lat-input').value = pos.coords.latitude.toFixed(6);
            document.getElementById('lon-input').value = pos.coords.longitude.toFixed(6);
            map.setView([pos.coords.latitude, pos.coords.longitude], 12);
        });
    });

    fetch('/api/data').then(res => res.json()).then(data => {
        allData = data || [];
        renderDashboard(allData);
    });

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
});
