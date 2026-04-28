// Charts JavaScript for AAMS Dashboard
// ------------------------------------

let attendanceChart = null;

async function initAttendanceChart() {
    const ctx = document.getElementById('attendanceChart');
    if (!ctx) return;

    try {
        const response = await fetch('/api/weekly-stats');
        const data = await response.json();

        const labels = data.map(d => d.date);
        const present = data.map(d => parseInt(d.present) || 0);
        const absent = data.map(d => parseInt(d.absent) || 0);
        const late = data.map(d => parseInt(d.late) || 0);

        if (attendanceChart) {
            attendanceChart.destroy();
        }

        attendanceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    { label: 'Present', data: present, backgroundColor: '#22c55e' },
                    { label: 'Absent', data: absent, backgroundColor: '#ef4444' },
                    { label: 'Late', data: late, backgroundColor: '#f59e0b' }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#fff' } }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#2d3748' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#2d3748' } }
                }
            }
        });

        // Update summary stats
        const totalPresent = present.reduce((a, b) => a + b, 0);
        const totalAbsent = absent.reduce((a, b) => a + b, 0);
        const totalLate = late.reduce((a, b) => a + b, 0);
        const count = labels.length || 1;

        document.getElementById('avgPresent').textContent = Math.round(totalPresent / count);
        document.getElementById('avgAbsent').textContent = Math.round(totalAbsent / count);
        document.getElementById('avgLate').textContent = Math.round(totalLate / count);

        const total = totalPresent + totalAbsent + totalLate;
        const rate = total > 0 ? ((totalPresent + totalLate) / total * 100).toFixed(1) : 0;
        document.getElementById('attendanceRate').textContent = rate + '%';
    } catch (e) {
        console.error('Failed to load chart data:', e);
    }
}

function updateAttendanceChart(period) {
    document.querySelectorAll('.chart-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(period + 'Btn').classList.add('active');
    initAttendanceChart();
}

document.addEventListener('DOMContentLoaded', initAttendanceChart);

