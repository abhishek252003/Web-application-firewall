let isPolling = true;

// === Theme Toggle ===
document.getElementById('themeToggle').addEventListener('click', () => {
    document.body.classList.toggle('dark');
    localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
});

if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark');
}

// === Logs Polling ===
async function fetchLogs() {
    try {
        const response = await fetch('/api/logs');
        const logs = await response.json();
        const tbody = document.querySelector('#logsTable tbody');
        tbody.innerHTML = '';
        logs.forEach(log => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${log.id}</td>
                <td>${log.timestamp}</td>
                <td>${log.ip}</td>
                <td>${log.method}</td>
                <td>${log.path}</td>
                <td>${log.body || '-'}</td>
                <td>${log.status}</td>
                <td>${log.reason || '-'}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching logs:', error);
    }
}

function startPolling() {
    if (isPolling) {
        fetchLogs();
        setTimeout(startPolling, 5000);
    }
}

function togglePolling() {
    isPolling = !isPolling;
    document.getElementById('pauseButton').textContent = isPolling ? 'Pause Updates' : 'Resume Updates';
    if (isPolling) {
        startPolling();
    }
}

// === Blacklist ===
async function fetchBlacklist() {
    try {
        const response = await fetch('/api/blacklist');
        const blacklist = await response.json();
        const ul = document.getElementById('blacklist');
        ul.innerHTML = '';
        blacklist.forEach(ip => {
            const li = document.createElement('li');
            li.innerHTML = `${ip} <button onclick="removeIP('${ip}')">Remove</button>`;
            ul.appendChild(li);
        });
    } catch (error) {
        console.error('Error fetching blacklist:', error);
    }
}

async function blacklistIP(ip) {
    try {
        const response = await fetch('/api/blacklist', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ip })
        });
        if (response.ok) {
            fetchBlacklist();
            return true;
        }
        return false;
    } catch (error) {
        console.error('Error blacklisting IP:', error);
        return false;
    }
}

async function removeIP(ip) {
    try {
        const response = await fetch(`/api/blacklist/${ip}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            fetchBlacklist();
        } else {
            alert('Failed to remove IP');
        }
    } catch (error) {
        console.error('Error removing IP:', error);
    }
}

// === Rules ===
async function fetchRules() {
    try {
        const response = await fetch('/api/rules');
        const rules = await response.json();
        const ul = document.getElementById('rulesList');
        ul.innerHTML = '';
        rules.forEach(rule => {
            const li = document.createElement('li');
            li.innerHTML = `${rule.pattern} (${rule.description}) <button onclick="deleteRule(${rule.id})">Delete</button>`;
            ul.appendChild(li);
        });
    } catch (error) {
        console.error('Error fetching rules:', error);
    }
}

async function addRule() {
    const pattern = document.getElementById('ruleInput').value;
    const description = document.getElementById('ruleDesc').value;
    if (pattern && description) {
        try {
            const response = await fetch('/api/rules', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pattern, description })
            });
            if (response.ok) {
                fetchRules();
                document.getElementById('ruleInput').value = '';
                document.getElementById('ruleDesc').value = '';
            } else {
                const error = await response.json();
                alert(`Failed to add rule: ${error.error}`);
            }
        } catch (error) {
            console.error('Error adding rule:', error);
        }
    }
}

async function deleteRule(rule_id) {
    try {
        const response = await fetch(`/api/rules/${rule_id}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            fetchRules();
        } else {
            alert('Failed to delete rule');
        }
    } catch (error) {
        console.error('Error deleting rule:', error);
    }
}

// === Futuristic Chart.js Theme ===
const futuristicFont = {
    family: "'Orbitron', 'Segoe UI', sans-serif",
    size: 12,
    weight: 'bold',
    lineHeight: 1.6
};

const futuristicColors = {
    bg: '#0d1117',
    text: '#00ffe1',
    grid: '#1f2937',
    pieColors: ['#00ffe1', '#6fffe9', '#ff4c60', '#f1c40f', '#8e44ad']
};

Chart.defaults.plugins.tooltip.backgroundColor = '#101820';
Chart.defaults.plugins.tooltip.titleColor = '#00ffe1';
Chart.defaults.plugins.tooltip.bodyColor = '#ffffff';

// === Stats Charts ===
async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        const attackCtx = document.getElementById('attackChart').getContext('2d');
        new Chart(attackCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(stats.attacks),
                datasets: [{
                    label: 'Attack Attempts',
                    data: Object.values(stats.attacks),
                    backgroundColor: futuristicColors.pieColors,
                    borderColor: '#00ffe1',
                    borderWidth: 1,
                    barThickness: 20,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: futuristicColors.text,
                            font: futuristicFont
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: futuristicColors.text,
                            font: futuristicFont
                        },
                        grid: {
                            color: futuristicColors.grid
                        }
                    },
                    y: {
                        ticks: {
                            color: futuristicColors.text,
                            font: futuristicFont
                        },
                        grid: {
                            color: futuristicColors.grid
                        }
                    }
                }
            }
        });

        const statusCtx = document.getElementById('statusChart').getContext('2d');
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(stats.status),
                datasets: [{
                    data: Object.values(stats.status),
                    backgroundColor: [futuristicColors.pieColors[0], futuristicColors.pieColors[2]],
                    borderColor: '#000',
                    hoverBorderColor: '#00ffe1',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: futuristicColors.text,
                            font: futuristicFont,
                            boxWidth: 10
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// === Init ===
document.getElementById('blacklistForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const ip = document.getElementById('ipInput').value;
    if (ip) {
        if (await blacklistIP(ip)) {
            document.getElementById('ipInput').value = '';
        }
    }
});

document.getElementById('ruleForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    await addRule();
});

document.getElementById('pauseButton').addEventListener('click', togglePolling);

fetchLogs();
startPolling();
fetchBlacklist();
fetchRules();
fetchStats();