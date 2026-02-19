document.addEventListener('DOMContentLoaded', function() {
    let map = L.map('map').setView([17.7296, 83.3212], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    let markersLayer = L.layerGroup().addTo(map);
    let allData = [];

    function renderDashboard(data, activeFilter = 'All') {
        const tableBody = document.getElementById('data-table-body');
        const isPondView = activeFilter === 'Pond Water';
        tableBody.innerHTML = '';
        markersLayer.clearLayers(); 

        data.forEach(row => {
            const isOcean = row.water_type.toLowerCase().includes('ocean');
            
            // Draw Elegant Liquid Pins
            if (row.latitude && row.longitude) {
                const markerColor = isOcean ? '#457b9d' : '#2a9d8f';
                L.circleMarker([row.latitude, row.longitude], {
                    radius: 11,
                    fillColor: markerColor,
                    color: "#fff",
                    weight: 3,
                    fillOpacity: 0.9
                }).bindPopup(`<b>${row.water_type}</b>`).addTo(markersLayer);
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

    fetch('/api/data').then(res => res.json()).then(data => {
        allData = data || [];
        renderDashboard(allData);
    });

    // Handle Map Navigation
    document.getElementById('btn-detect').addEventListener('click', function() {
        navigator.geolocation.getCurrentPosition(pos => {
            map.setView([pos.coords.latitude, pos.coords.longitude], 14);
        });
    });
});
