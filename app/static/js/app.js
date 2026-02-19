document.addEventListener('DOMContentLoaded', function() {
    let map = L.map('map').setView([17.7296, 83.3212], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    let markersLayer = L.layerGroup().addTo(map);
    let allData = [];

    const oceanTypes = ['open ocean water', 'coastal water', 'estuarine water', 'deep sea water', 'marine surface water'];
    const pondGroupTypes = ['pond water', 'drinking water', 'ground water', 'borewell water'];

    function renderDashboard(data) {
        const tableBody = document.getElementById('data-table-body');
        tableBody.innerHTML = '';
        
        data.forEach(row => {
            const isOcean = oceanTypes.includes(row.water_type.toLowerCase());
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${new Date(row.timestamp).toLocaleTimeString()}</td>
                <td><span class="badge rounded-pill ${isOcean ? 'bg-primary' : 'bg-success'}">${row.water_type}</span></td>
                <td>${parseFloat(row.latitude).toFixed(4)}, ${parseFloat(row.longitude).toFixed(4)}</td>
                <td>${row.ph}</td>
                <td>${row.do || '-'}</td>
                <td>${row.tds}</td>
                <td>${row.temperature}°C</td>
                <td><a href="/image/${row.id}" target="_blank" class="text-primary fw-bold text-decoration-none">View</a></td>
            `;
            tableBody.appendChild(tr);
        });
    }

    function triggerBoxAnimation(btn, view) {
        const splash = document.createElement('span');
        splash.className = 'click-splash';
        btn.appendChild(splash);
        setTimeout(() => splash.remove(), 600);

        if (view !== 'All') {
            const icon = document.createElement('i');
            icon.className = `fas ${view === 'Ocean' ? 'fa-fish' : 'fa-droplet'} box-icon`;
            icon.style.top = '35%';
            btn.appendChild(icon);
            setTimeout(() => icon.remove(), 1200);
        }
    }

    fetch('/api/data').then(res => res.json()).then(data => {
        allData = data || [];
        renderDashboard(allData);
    });

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.getAttribute('data-view');
            triggerBoxAnimation(this, view);
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const filtered = (view === 'All') ? allData : allData.filter(d => 
                view === 'Ocean' ? oceanTypes.includes(d.water_type.toLowerCase()) : pondGroupTypes.includes(d.water_type.toLowerCase())
            );
            renderDashboard(filtered);
        });
    });
});
