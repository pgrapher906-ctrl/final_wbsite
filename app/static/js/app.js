document.addEventListener('DOMContentLoaded', function() {
    let map = L.map('map').setView([17.7296, 83.3212], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    let allData = [];

    const oceanTypes = ['open ocean water', 'coastal water', 'estuarine water', 'deep sea water', 'marine surface water'];
    const pondGroupTypes = ['pond water', 'drinking water', 'ground water', 'borewell water'];

    function updateTableHeaders(view) {
        const headerRow = document.getElementById('table-header-row');
        // REMOVE DO column when view is Ocean
        let headers = ['TIME', 'TYPE', 'COORDINATES', 'PH', 'DO (PPM)', 'TDS', 'TEMP', 'EVIDENCE'];
        if (view === 'Ocean') {
            headers = ['TIME', 'TYPE', 'COORDINATES', 'PH', 'TDS', 'TEMP', 'EVIDENCE'];
        }
        headerRow.innerHTML = headers.map(h => `<th>${h}</th>`).join('');
    }

    function renderDashboard(data, view) {
        updateTableHeaders(view);
        const tableBody = document.getElementById('data-table-body');
        tableBody.innerHTML = '';

        data.forEach(row => {
            const isOcean = oceanTypes.includes(row.water_type.toLowerCase());
            const tr = document.createElement('tr');
            
            let cells = `
                <td>${new Date(row.timestamp).toLocaleTimeString()}</td>
                <td><span class="badge rounded-pill ${isOcean ? 'bg-primary' : 'bg-success'}">${row.water_type}</span></td>
                <td>${parseFloat(row.latitude).toFixed(4)}, ${parseFloat(row.longitude).toFixed(4)}</td>
                <td>${row.ph}</td>`;
            
            // Add DO value only if not in Ocean view
            if (view !== 'Ocean') {
                cells += `<td>${row.do || '-'}</td>`;
            }

            cells += `
                <td>${row.tds}</td>
                <td>${row.temperature}°C</td>
                <td><a href="/image/${row.id}" target="_blank" class="text-primary fw-bold text-decoration-none">View</a></td>`;
            
            tr.innerHTML = cells;
            tableBody.appendChild(tr);
        });

        // Update Stats
        document.getElementById('ocean-count').innerText = allData.filter(d => oceanTypes.includes(d.water_type.toLowerCase())).length;
        document.getElementById('pond-count').innerText = allData.filter(d => pondGroupTypes.includes(d.water_type.toLowerCase())).length;
    }

    function triggerBoxAnimation(btn, view) {
        const splash = document.createElement('span');
        splash.className = 'click-splash';
        btn.appendChild(splash);
        setTimeout(() => splash.remove(), 600);
        if (view !== 'All') {
            const icon = document.createElement('i');
            icon.className = `fas ${view === 'Ocean' ? 'fa-fish' : 'fa-droplet'} box-icon`;
            btn.appendChild(icon);
            setTimeout(() => icon.remove(), 1200);
        }
    }

    fetch('/api/data').then(res => res.json()).then(data => {
        allData = data || [];
        renderDashboard(allData, 'All');
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
            renderDashboard(filtered, view);
        });
    });
});
