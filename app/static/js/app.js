document.addEventListener('DOMContentLoaded', function() {
    let map = L.map('map').setView([17.7296, 83.3212], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    let markersLayer = L.layerGroup().addTo(map);

    function renderDashboard(data) {
        const tableBody = document.getElementById('data-table-body');
        tableBody.innerHTML = ''; // Clear table
        markersLayer.clearLayers(); 

        data.forEach(row => {
            // Update Map Pins
            if (row.latitude && row.longitude) {
                const isOcean = row.water_type.toLowerCase().includes('ocean');
                const markerColor = isOcean ? '#457b9d' : '#2a9d8f';
                L.circleMarker([row.latitude, row.longitude], {
                    radius: 11, fillColor: markerColor, color: "#fff", weight: 3, fillOpacity: 0.9
                }).bindPopup(`<b>${row.water_type}</b>`).addTo(markersLayer);
            }

            // Update Table Rows
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${new Date(row.timestamp).toLocaleTimeString()}</td>
                <td><span class="badge rounded-pill bg-info">${row.water_type}</span></td>
                <td>${row.latitude}, ${row.longitude}</td>
                <td>${row.ph}</td>
                <td>${row.tds}</td>
                <td>${row.temperature}°C</td>
                <td><a href="/image/${row.id}" target="_blank" class="text-decoration-none">View</a></td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // Load initial data
    fetch('/api/data').then(res => res.json()).then(data => {
        renderDashboard(data || []);
    });

    // Handle GET GPS button
    document.getElementById('btn-detect').addEventListener('click', function() {
        navigator.geolocation.getCurrentPosition(pos => {
            // Populate the restored input boxes
            document.getElementById('lat-input').value = pos.coords.latitude.toFixed(6);
            document.getElementById('lon-input').value = pos.coords.longitude.toFixed(6);
            map.setView([pos.coords.latitude, pos.coords.longitude], 14);
        });
    });
});
