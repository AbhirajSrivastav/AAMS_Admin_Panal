// Reports JavaScript for AAMS
// ---------------------------

async function initReports() {
    await loadDailyChart();
    await loadStatusPie();
    await loadWeeklyTable();
}

async function loadDailyChart() {
    const ctx = document.getElementById('dailyChart');
    if (!ctx) return;

    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Present', 'Absent', 'Late'],
                datasets: [{
                    data: [
                        stats.present_today || 0,
                        stats.absent_today || 0,
                        stats.late_today || 0
                    ],
                    backgroundColor: ['#22c55e', '#ef4444', '#f59e0b']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#fff' } }
                }
            }
        });
    } catch (e) {
        console.error('Failed to load daily chart:', e);
    }
}

async function loadStatusPie() {
    const ctx = document.getElementById('statusPie');
    if (!ctx) return;

    try {
        const response = await fetch('/api/students');
        const students = await response.json();
        const active = students.filter(s => s.status === 'Active').length;
        const inactive = students.filter(s => s.status === 'Inactive').length;

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Active', 'Inactive'],
                datasets: [{
                    data: [active, inactive],
                    backgroundColor: ['#22c55e', '#ef4444']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#fff' } }
                }
            }
        });
    } catch (e) {
        console.error('Failed to load status pie:', e);
    }
}

async function loadWeeklyTable() {
    try {
        const response = await fetch('/api/weekly-stats');
        const data = await response.json();
        const tbody = document.querySelector('#weeklyTable tbody');
        if (!tbody) return;
        tbody.innerHTML = data.map(d => `
            <tr>
                <td>${d.date}</td>
                <td>${d.present || 0}</td>
                <td>${d.absent || 0}</td>
                <td>${d.late || 0}</td>
            </tr>
        `).join('');
    } catch (e) {
        console.error('Failed to load weekly table:', e);
    }
}

document.addEventListener('DOMContentLoaded', initReports);

