// 1. REAL-TIME CLOCK & DATE
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const clockElement = document.getElementById('clock');
    if (clockElement) {
        clockElement.innerText = timeString;
    }
}
setInterval(updateClock, 1000);
updateClock(); // Call once on load

// 2. DYNAMIC ATTENDANCE CHART (Chart.js)
let chartInstance = null;
let currentChartPeriod = 'week';

// Sample data for different periods
const attendanceData = {
    week: {
        labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        present: [275, 280, 282, 285, 283, 270, 265],
        absent: [8, 3, 2, 0, 1, 10, 15],
        late: [2, 2, 1, 0, 1, 5, 5]
    },
    month: {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        present: [1980, 1995, 1998, 2000],
        absent: [35, 28, 20, 15],
        late: [20, 18, 15, 10]
    },
    year: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        present: [7500, 7600, 7800, 7900, 8000, 7950, 8100, 8200, 8050, 8150, 8250, 8300],
        absent: [200, 180, 150, 120, 100, 150, 80, 50, 100, 70, 50, 40],
        late: [150, 145, 130, 120, 110, 115, 95, 85, 110, 95, 85, 75]
    }
};

function calculateAttendanceStats(data) {
    const totalPresent = data.present.reduce((a, b) => a + b, 0);
    const totalAbsent = data.absent.reduce((a, b) => a + b, 0);
    const totalLate = data.late.reduce((a, b) => a + b, 0);
    const total = totalPresent + totalAbsent + totalLate;
    
    return {
        avgPresent: Math.round(totalPresent / data.present.length),
        avgAbsent: Math.round(totalAbsent / data.absent.length),
        avgLate: Math.round(totalLate / data.late.length),
        rate: (totalPresent / total * 100).toFixed(1)
    };
}

function updateAttendanceStats(period) {
    const data = attendanceData[period];
    const stats = calculateAttendanceStats(data);
    
    document.getElementById('avgPresent').innerText = stats.avgPresent;
    document.getElementById('avgAbsent').innerText = stats.avgAbsent;
    document.getElementById('avgLate').innerText = stats.avgLate;
    document.getElementById('attendanceRate').innerText = stats.rate + '%';
}

function updatePeriodButtons(period) {
    document.getElementById('weekBtn').style.background = period === 'week' ? '#22c55e' : '#2d3748';
    document.getElementById('weekBtn').style.color = period === 'week' ? 'white' : '#94a3b8';
    document.getElementById('monthBtn').style.background = period === 'month' ? '#22c55e' : '#2d3748';
    document.getElementById('monthBtn').style.color = period === 'month' ? 'white' : '#94a3b8';
    document.getElementById('yearBtn').style.background = period === 'year' ? '#22c55e' : '#2d3748';
    document.getElementById('yearBtn').style.color = period === 'year' ? 'white' : '#94a3b8';
}

function updateAttendanceChart(period) {
    currentChartPeriod = period;
    updatePeriodButtons(period);
    updateAttendanceStats(period);
    
    const data = attendanceData[period];
    
    if (chartInstance) {
        chartInstance.data.labels = data.labels;
        chartInstance.data.datasets[0].data = data.present;
        chartInstance.data.datasets[1].data = data.absent;
        chartInstance.data.datasets[2].data = data.late;
        chartInstance.update();
    } else {
        initializeChart();
    }
}

function initializeChart() {
    const chartCanvas = document.getElementById('attendanceChart');
    if (!chartCanvas) {
        console.error('Chart canvas element not found');
        return;
    }
    
    try {
        const ctx = chartCanvas.getContext('2d');
        if (!ctx) {
            console.error('Failed to get 2D context');
            return;
        }
        
        // Destroy existing chart if it exists
        if (chartInstance) {
            chartInstance.destroy();
        }
        
        const data = attendanceData[currentChartPeriod];
        
        // Create new chart
        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Present',
                        data: data.present,
                        borderColor: '#22c55e',
                        backgroundColor: 'rgba(34, 197, 94, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        pointRadius: 5,
                        pointBackgroundColor: '#22c55e',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Absent',
                        data: data.absent,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.05)',
                        borderWidth: 2,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: '#ef4444',
                        fill: false,
                        yAxisID: 'y1'
                    },
                    {
                        label: 'Late',
                        data: data.late,
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.05)',
                        borderWidth: 2,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: '#f59e0b',
                        fill: false,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#94a3b8',
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(30, 41, 59, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#94a3b8',
                        borderColor: '#2d3748',
                        borderWidth: 1,
                        padding: 10,
                        displayColors: true
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        },
                        title: {
                            display: true,
                            text: 'Present Count',
                            color: '#94a3b8'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        grid: {
                            drawOnChartArea: false
                        },
                        ticks: {
                            color: '#94a3b8'
                        },
                        title: {
                            display: true,
                            text: 'Absent/Late Count',
                            color: '#94a3b8'
                        }
                    },
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            font: {
                                size: 11
                            }
                        }
                    }
                }
            }
        });
        console.log('Chart initialized successfully');
        updateAttendanceStats(currentChartPeriod);
    } catch (error) {
        console.error('Error initializing chart:', error);
    }
}

// Wait for Chart.js library to load, then initialize
if (typeof Chart !== 'undefined') {
    // Chart.js is available
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(initializeChart, 100);
        });
    } else {
        setTimeout(initializeChart, 100);
    }
} else {
    console.warn('Chart.js library not loaded yet');
    // Try again after a delay
    setTimeout(() => {
        if (typeof Chart !== 'undefined') {
            initializeChart();
        }
    }, 1000);
}


    // 3. ACTIVITY FEED SIMULATOR
    // This randomly adds "New Student Detected" to the feed
    const activityFeed = document.querySelector('.main-content .card:last-child');
    
    function addActivity(name, status) {
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const newItem = document.createElement('div');
        newItem.className = 'activity-item';
        newItem.style.opacity = '0';
        newItem.style.transition = 'opacity 0.5s ease-in';
        
        newItem.innerHTML = `
            ${time} - <strong>${name}</strong>: 
            <span class="${status === 'Present' ? 'present-text' : 'alert-text'}">${status}</span>
        `;
        
        // Insert at the top of the list (after the header)
        activityFeed.insertBefore(newItem, activityFeed.children[1]);
        setTimeout(() => newItem.style.opacity = '1', 10);
    }

    // Simulate a detection every 10 seconds
    setInterval(() => {
        const students = ["Rahul Sharma", "Sanya Malhotra", "Vikram Singh", "Anjali Rao"];
        const randomStudent = students[Math.floor(Math.random() * students.length)];  
        addActivity(randomStudent, "Present");
    }, 10000);

    // 4. UPDATE DASHBOARD WITH API DATA
    async function updateDashboard() {
        try {
            const response = await fetch('/api/stats');
            if (!response.ok) {
                console.error('Failed to fetch stats');
                return;
            }
            const data = await response.json();
            
            // Update dashboard cards by ID
            const totalElement = document.getElementById('total-count');
            const presentElement = document.getElementById('present-count');
            
            if (totalElement) {
                totalElement.innerText = data.total_detections || 0;
            }
            if (presentElement) {
                presentElement.innerText = data.unique_faces || 0;
            }
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }

    // Refresh stats every 5 seconds
    setInterval(updateDashboard, 5000);
    updateDashboard(); // Call once on load