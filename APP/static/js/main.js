// Main JavaScript for AAMS Dashboard
// ----------------------------------

function updateClock() {
    const now = new Date();
    document.getElementById('clock').textContent = now.toLocaleTimeString();
}
setInterval(updateClock, 1000);
updateClock();

// Fetch dashboard stats every 5 seconds
async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        document.getElementById('total-count').textContent = stats.total_students || 0;
        document.getElementById('present-count').textContent = stats.present_today || 0;
        document.getElementById('absent-count').textContent = stats.absent_today || 0;
        document.getElementById('late-count').textContent = stats.late_today || 0;
    } catch (e) {
        console.error('Failed to fetch stats:', e);
    }
}
setInterval(fetchStats, 5000);
fetchStats();

// Fetch recent activity every 10 seconds
async function fetchActivity() {
    try {
        const response = await fetch('/api/data?limit=10');
        const logs = await response.json();
        const container = document.getElementById('activityFeed');
        if (!container || logs.length === 0) return;
        container.innerHTML = logs.map(log => {
            const time = log.check_in_time ? new Date(log.check_in_time).toLocaleTimeString() : '';
            const statusClass = log.status === 'Present' ? 'present-text' : log.status === 'Late' ? 'orange' : 'alert-text';
            return `<div class="activity-item">${time} - <strong>${log.student_name || 'Unknown'}</strong>: <span class="${statusClass}">${log.status}</span></div>`;
        }).join('');
    } catch (e) {
        console.error('Failed to fetch activity:', e);
    }
}
setInterval(fetchActivity, 10000);
fetchActivity();

