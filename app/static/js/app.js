document.addEventListener('DOMContentLoaded', function() {
    let map = L.map('map').setView([17.7296, 83.3212], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    let markersLayer = L.layerGroup().addTo(map);
    let allData = [];

    const oceanTypes = ['open ocean water', 'coastal water', 'estuarine water', 'deep sea water', 'marine surface water', 'drinking water'];

    function renderDashboard(data) {
        const tableBody = document.getElementById('data-table-body');
        tableBody.innerHTML = '';
        markersLayer.clearLayers(); 

        // Update Live Counters
        const oceanCount = allData.filter(d => oceanTypes.includes(d.water_type.toLowerCase())).length;
        const pondCount = allData.filter(d => d.water_type.toLowerCase().includes('pond')).length;
        
        document.getElementById('ocean-count').innerText = oceanCount;
        document.getElementById('pond-count').innerText = pondCount;

        data.forEach(row => {
            const isOcean = oceanTypes.includes(row.water_type.toLowerCase());
            
            if (row.latitude && row.longitude) {
                const markerColor = isOcean ? '#457b9d' : '#2a9d8f';
                L.circleMarker([row.latitude, row.longitude], {
                    radius: 11, fillColor: markerColor, color: "#fff", weight: 3, fillOpacity: 0.9
                }).bindPopup(`<b>${row.water_type}</b>`).addTo(markersLayer);
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${new Date(row.timestamp).toLocaleTimeString()}</td>
                <td><span class="badge rounded-pill ${isOcean ? 'bg-primary' : 'bg-success'}">${row.water_type}</span></td>
                <td>${parseFloat(row.latitude).toFixed(4)}, ${parseFloat(row.longitude).toFixed(4)}</td>
                <td>${row.ph}</td><td>${row.tds}</td><td>${row.temperature}°C</td>
                <td><a href="/image/${row.id}" target="_blank" class="text-primary text-decoration-none fw-bold">View</a></td>
            `;
            tableBody.appendChild(tr);
        });
    }

    fetch('/api/data').then(res => res.json()).then(data => {
        allData = data || [];
        renderDashboard(allData);
    });

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const viewType = this.getAttribute('data-view');
            let filtered;

            if (viewType === 'Ocean') {
                filtered = allData.filter(d => oceanTypes.includes(d.water_type.toLowerCase()));
            } else if (viewType === 'Pond') {
                filtered = allData.filter(d => d.water_type.toLowerCase().includes('pond'));
            } else {
                filtered = allData;
            }
            renderDashboard(filtered);
        });
    });

    document.getElementById('btn-detect').addEventListener('click', function() {
        navigator.geolocation.getCurrentPosition(pos => {
            document.getElementById('lat-input').value = pos.coords.latitude.toFixed(6);
            document.getElementById('lon-input').value = pos.coords.longitude.toFixed(6);
            map.setView([pos.coords.latitude, pos.coords.longitude], 14);
        });
    });
});
