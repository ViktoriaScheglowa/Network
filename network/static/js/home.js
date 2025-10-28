document.addEventListener('DOMContentLoaded', function() {
    loadStatistics();
    loadNodes();
    setupEventListeners();
});

function loadStatistics() {
    fetch('/api/network-nodes/statistics/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('factories-count').textContent = data.factories;
            document.getElementById('retail-count').textContent = data.retail_chains;
            document.getElementById('entrepreneurs-count').textContent = data.entrepreneurs;
            document.getElementById('total-nodes').textContent = data.total_nodes;
        })
        .catch(error => console.error('Error loading statistics:', error));
}

function loadNodes(city = '') {
    const url = city ? `/api/network-nodes/?city=${city}` : '/api/network-nodes/';

    fetch(url)
        .then(response => response.json())
        .then(data => {
            displayNodes(data.results || data);
        })
        .catch(error => console.error('Error loading nodes:', error));
}

function displayNodes(nodes) {
    const container = document.getElementById('nodes-container');
    const loading = document.getElementById('loading-message');
    const noData = document.getElementById('no-nodes-message');

    loading.style.display = 'none';

    if (!nodes || nodes.length === 0) {
        noData.style.display = 'block';
        container.innerHTML = '';
        return;
    }

    noData.style.display = 'none';

    container.innerHTML = nodes.map(node => `
        <div class="node-card ${node.node_type}">
            <div class="node-header">
                <div class="node-name">${node.name}</div>
                <div class="node-type">${getNodeTypeDisplay(node.node_type)}</div>
            </div>
            <div class="node-details">
                <div class="node-detail">
                    <i>📍</i> ${node.city}, ${node.country}
                </div>
                <div class="node-detail">
                    <i>📧</i> ${node.email}
                </div>
                <div class="node-detail">
                    <i>🏠</i> ${node.street}, ${node.house_number}
                </div>
                <div class="debt ${node.debt > 0 ? 'positive' : 'zero'}">
                    <i>💰</i> Задолженность: ${parseFloat(node.debt).toFixed(2)} ₽
                </div>
            </div>
        </div>
    `).join('');
}

function getNodeTypeDisplay(nodeType) {
    const types = {
        'factory': 'Завод',
        'retail': 'Розничная сеть',
        'entrepreneur': 'Индивидуальный предприниматель'
    };
    return types[nodeType] || nodeType;
}

function setupEventListeners() {
    document.getElementById('apply-filter').addEventListener('click', function() {
        const city = document.getElementById('city-filter').value;
        loadNodes(city);
    });

    document.getElementById('reset-filter').addEventListener('click', function() {
        document.getElementById('city-filter').value = '';
        loadNodes();
    });
}