// ========================
// AI-Powered Threat Dashboard JS
// ========================

const socket = io();

// Dashboard stats
let totalThreats = 0;
let highAlerts = 0;
let recentAlerts = [];
let chartLabels = [];
let chartData = [];

// ------------------- Chart.js setup -------------------
const ctx = document.getElementById('threatChart').getContext('2d');
const threatChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: chartLabels,
        datasets: [{
            label: 'Threat Level',
            data: chartData,
            fill: true,
            borderColor: 'rgba(255, 99, 132, 1)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            tension: 0.3
        }]
    },
    options: {
        responsive: true,
        plugins: { legend: { display: true } },
        scales: { y: { beginAtZero: true, max: 100 } }
    }
});

// ------------------- SocketIO live updates -------------------
socket.on('threat_update', data => {
    const timestamp = new Date(data.timestamp * 1000).toLocaleTimeString();

    if (data.threat === 'malicious') {
        totalThreats++;
        if (data.value > 70) highAlerts++;
    }

    document.getElementById('totalThreats').textContent = totalThreats;
    document.getElementById('highAlerts').textContent = highAlerts;

    recentAlerts.unshift({ ...data, time: timestamp });
    if (recentAlerts.length > 5) recentAlerts.pop();
    renderRecentAlerts();

    // Update chart
    chartLabels.push(timestamp);
    chartData.push(data.value);
    if (chartLabels.length > 10) {
        chartLabels.shift();
        chartData.shift();
    }
    threatChart.update();
});

// ------------------- Render recent alerts -------------------
function renderRecentAlerts() {
    const alertsDiv = document.getElementById('recentAlerts');
    alertsDiv.innerHTML = '';
    recentAlerts.forEach(alert => {
        const alertClass = alert.threat === 'malicious' ? 
                           (alert.value > 70 ? 'alert-high' : 'alert-medium') : 'alert-low';
        alertsDiv.innerHTML += `
            <div class="${alertClass}">
                <strong>${alert.threat.toUpperCase()}</strong> - Value: ${alert.value}<br>
                <small>Time: ${alert.time} | Source: ${alert.source_ip || 'Unknown'}</small>
            </div>
        `;
    });
}

// ------------------- Manual threat analysis -------------------
function getFormFeatures() {
    return [
        parseFloat(document.getElementById('duration').value),
        parseInt(document.getElementById('protocol').value),
        parseInt(document.getElementById('failedLogins').value),
        // Placeholder for additional features
        ...Array(36).fill(0)
    ];
}

function analyzeThreat() {
    const data = {
        source_ip: document.getElementById('sourceIp').value,
        features: getFormFeatures()
    };

    fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(res => {
        displayResults(res);
        updateStats(res);
    })
    .catch(err => console.error('Analysis failed:', err));
}

function displayResults(result) {
    const resultsDiv = document.getElementById('analysisResults');
    const threatClass = result.predicted_class || 'unknown';
    const confidence = ((result.confidence || 0) * 100).toFixed(1);

    let alertClass = 'alert-low';
    if (threatClass !== 'normal' && result.confidence > 0.8) alertClass = 'alert-high';
    else if (threatClass !== 'normal') alertClass = 'alert-medium';

    resultsDiv.innerHTML = `
        <div class="${alertClass}">
            <h3>Threat Classification: ${threatClass.toUpperCase()}</h3>
            <p><strong>Confidence:</strong> ${confidence}%</p>
            <div>
                <h4>Probability Distribution:</h4>
                ${Object.entries(result.probabilities || {}).map(([key, value]) =>
                    `<p>${key}: ${(value*100).toFixed(1)}%</p>`).join('')}
            </div>
        </div>
    `;
    document.getElementById('resultsCard').style.display = 'block';
    addRecentAlert(threatClass, confidence, document.getElementById('sourceIp').value);
}

function addRecentAlert(type, confidence, ip) {
    const alertsDiv = document.getElementById('recentAlerts');
    const alertClass = type === 'normal' ? 'alert-low' :
                       confidence > 80 ? 'alert-high' : 'alert-medium';
    const alertHtml = `
        <div class="${alertClass}">
            <strong>${type.toUpperCase()}</strong> - Confidence: ${confidence}%<br>
            <small>Source: ${ip} | Time: ${new Date().toLocaleTimeString()}</small>
        </div>`;
    alertsDiv.innerHTML = alertHtml + alertsDiv.innerHTML;
}

function updateStats(result) {
    totalThreats++;
    document.getElementById('totalThreats').textContent = totalThreats;
    if (result.predicted_class !== 'normal' && result.confidence > 0.8) {
        highAlerts++;
        document.getElementById('highAlerts').textContent = highAlerts;
    }
}
