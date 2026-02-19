document.addEventListener('DOMContentLoaded', function() {
    let map = L.map('map').setView([17.7296, 83.3212], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    let markersLayer = L.layerGroup().addTo(map);
    let allData = [];

    function renderDashboard(data) {
        const tableBody = document.getElementById('data-table-body');
        tableBody.innerHTML = '';
        markersLayer.clearLayers(); 

        data.forEach(row => {
            if (row.latitude && row.longitude) {
                const isOcean = row.water_type.toLowerCase().includes('ocean');
                const markerColor = isOcean ? '#457b9d' : '#2a9d8f';
                L.circleMarker([row.latitude, row.longitude], {
                    radius: 10, fillColor: markerColor, color: "#fff", weight: 2, fillOpacity: 0.8
                }).bindPopup(`<b>${row.water_type}</b>`).addTo(markersLayer);
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${new Date(row.timestamp).toLocaleTimeString()}</td>
                <td>${row.water_type}</td>
                <td>${row.latitude}, ${row.longitude}</td>
                <td>${row.ph}</td><td>${row.tds}</td><td>${row.temperature}°C</td>
                <td><a href="/image/${row.id}" target="_blank">View</a></td>
            `;
            tableBody.appendChild(tr);
        });
    }

    fetch('/api/data').then(res => res.json()).then(data => {
        allData = data || [];
        renderDashboard(allData);
    });
});
