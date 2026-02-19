document.addEventListener('DOMContentLoaded', function() {
    let map = L.map('map').setView([17.7296, 83.3212], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    let markersLayer = L.layerGroup().addTo(map);

    function renderPoints(data) {
        markersLayer.clearLayers(); 
        data.forEach(row => {
            if (row.latitude && row.longitude) {
                const isOcean = row.water_type.toLowerCase().includes('ocean');
                const markerColor = isOcean ? '#457b9d' : '#2a9d8f';
                L.circleMarker([row.latitude, row.longitude], {
                    radius: 11, fillColor: markerColor, color: "#fff", weight: 3, fillOpacity: 0.9
                }).bindPopup(`<b>${row.water_type}</b>`).addTo(markersLayer);
            }
        });
    }

    fetch('/api/data').then(res => res.json()).then(data => {
        renderPoints(data || []);
    });

    document.getElementById('btn-detect').addEventListener('click', function() {
        navigator.geolocation.getCurrentPosition(pos => {
            map.setView([pos.coords.latitude, pos.coords.longitude], 14);
        });
    });
});
