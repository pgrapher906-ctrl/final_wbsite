document.addEventListener('DOMContentLoaded', function() {
    let map = L.map('map').setView([17.7296, 83.3212], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    let markersLayer = L.layerGroup().addTo(map);
    let allData = [];

    const oceanSubtypes = ['open ocean water', 'coastal water', 'estuarine water', 'deep sea water', 'marine surface water'];

    function renderDashboard(data, activeFilter = 'All') {
        const headerRow = document.querySelector('thead tr');
        const tableBody = document.getElementById('data-table-body');
        
        const isPondView = activeFilter === 'Pond Water';
        headerRow.innerHTML = `
            <th>TIME</th><th>CLASSIFICATION</th><th>COORDINATES</th>
            <th>PH</th><th>TDS</th>${isPondView ? '<th>DO</th>' : ''}
            <th>TEMP</th><th>EVIDENCE</th>
        `;

        tableBody.innerHTML = '';
        markersLayer.clearLayers(); 

        data.forEach(row => {
            const isOcean = oceanSubtypes.includes(row.water_type.toLowerCase()) || row.water_type.toLowerCase().includes('ocean');
            
            // --- POINT VIEW ON MAP ---
            if (row.latitude && row.longitude) {
                const markerColor = isOcean ? '#457b9d' : '#2a9d8f';
                L.circleMarker([row.latitude, row.longitude], {
                    radius: 10, fillColor: markerColor, color: "#fff", weight: 2, fillOpacity: 0.8
                }).bindPopup(`<b>${row.water_type}</b><br>pH: ${row.ph}`).addTo(markersLayer);
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${new Date(row.timestamp).toLocaleTimeString()}</td>
                <td><span class="badge rounded-pill ${isOcean ? 'bg-primary' : 'bg-success'}">${row.water_type}</span></td>
                <td>${parseFloat(row.latitude).toFixed(4)}, ${parseFloat(row.longitude).toFixed(4)}</td>
                <td>${row.ph}</td><td>${row.tds}</td>
                ${isPondView ? `<td>${row.do || '-'}</td>` : ''}
                <td>${row.temperature}°C</td>
                <td>${row.has_image ? `<a href="/image/${row.id}" target="_blank" class="btn btn-sm btn-link">View</a>` : '-'}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    document.getElementById('btn-detect').addEventListener('click', function() {
        navigator.geolocation.getCurrentPosition(pos => {
            document.getElementById('lat-input').value = pos.coords.latitude.toFixed(6);
            document.getElementById('lon-input').value = pos.coords.longitude.toFixed(6);
            map.setView([pos.coords.latitude, pos.coords.longitude], 14);
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
                (type === 'Ocean') ? (oceanSubtypes.includes(d.water_type.toLowerCase())) : d.water_type === type
            );
            renderDashboard(filtered, type);
        });
    });
});
