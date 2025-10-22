document.addEventListener('DOMContentLoaded', function() {
    loadNodes();
    setupEventListeners();
});

function loadNodes(filters = {}) {
    const loadingElement = document.getElementById('table-loading');
    const noDataElement = document.getElementById('table-no-data');
    const tableBody = document.getElementById('nodes-table-body');

    // Показываем загрузку
    loadingElement.style.display = 'block';
    noDataElement.style.display = 'none';
    tableBody.innerHTML = '';

    // Строим URL с фильтрами
    let url = '/api/network-nodes/';
    const params = new URLSearchParams();

    if (filters.node_type) {
        params.append('node_type', filters.node_type);
    }
    if (filters.city) {
        params.append('city', filters.city);
    }
    if (filters.search) {
        params.append('search', filters.search);
    }

    params.append('page_size', 1000);

    if (params.toString()) {
        url += '?' + params.toString();
    }

    console.log('Fetching URL:', url);

    // Загружаем данные с API
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data); // Отладочная информация
            const nodes = data.results || data;
            displayNodes(nodes);
        })
        .catch(error => {
            console.error('Error loading nodes:', error);
            showError('Ошибка загрузки данных' + error.message);
        })
        .finally(() => {
            loadingElement.style.display = 'none';
        });
}

function displayNodes(nodes) {
    const tableBody = document.getElementById('nodes-table-body');
    const noDataElement = document.getElementById('table-no-data');

    if (!nodes || nodes.length === 0) {
        noDataElement.style.display = 'block';
        tableBody.innerHTML = '';
        return;
    }

    noDataElement.style.display = 'none';

    tableBody.innerHTML = nodes.map(node => `
        <tr>
            <td>${escapeHtml(node.name)}</td>
            <td>
                <span class="node-type-badge ${node.node_type}">
                    ${getNodeTypeDisplay(node.node_type)}
                </span>
            </td>
            <td>${escapeHtml(node.city)}</td>
            <td>${escapeHtml(node.country)}</td>
            <td>${escapeHtml(node.email)}</td>
            <td>
                <span class="debt-amount ${node.debt > 0 ? 'positive' : 'zero'}">
                    ${parseFloat(node.debt).toFixed(2)} ₽
                </span>
            </td>
            <td class="actions">
                <button class="action-btn view" onclick="viewNodeDetails(${node.id})">
                    Просмотр
                </button>
                <button class="action-btn products" onclick="viewNodeProducts(${node.id})">
                    Продукты
                </button>
            </td>
        </tr>
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

function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) return '';
    return unsafe
        .toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function setupEventListeners() {
    // Кнопка "Применить"
    document.getElementById('apply-filters').addEventListener('click', function() {
        applyFilters();
    });

    // Кнопка "Сбросить"
    document.getElementById('reset-filters').addEventListener('click', function() {
        resetFilters();
    });

    // Поиск при нажатии Enter
    document.getElementById('search-filter').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            applyFilters();
        }
    });

    // Автозагрузка при изменении фильтров (опционально)
    document.getElementById('type-filter').addEventListener('change', function() {
        applyFilters();
    });

    document.getElementById('city-filter').addEventListener('change', function() {
        applyFilters();
    });
}

function applyFilters() {
    const filters = {
        node_type: document.getElementById('type-filter').value,
        city: document.getElementById('city-filter').value,
        search: document.getElementById('search-filter').value.trim()
    };

    console.log('Applying filters:', filters);
    loadNodes(filters);
}

function resetFilters() {
    document.getElementById('type-filter').value = '';
    document.getElementById('city-filter').value = '';
    document.getElementById('search-filter').value = '';
    loadNodes();
}

function showError(message) {
    const tableBody = document.getElementById('nodes-table-body');
    const noDataElement = document.getElementById('table-no-data');

    tableBody.innerHTML = '';
    noDataElement.textContent = message;
    noDataElement.style.display = 'block';
}

// Функции для модального окна (заглушки)
function viewNodeDetails(nodeId) {
    alert(`Просмотр узла с ID: ${nodeId}\nЗдесь будет открыто модальное окно с деталями`);
    // В будущем можно реализовать загрузку деталей узла
    // fetch(`/api/network-nodes/${nodeId}/`)
    //     .then(response => response.json())
    //     .then(data => showNodeModal(data));
}

function viewNodeProducts(nodeId) {
    alert(`Продукты узла с ID: ${nodeId}\nЗдесь будет открыта страница с продуктами узла`);
    // В будущем можно реализовать переход на страницу продуктов
    // window.location.href = `/node-products/?node=${nodeId}`;
}

// Функции для модального окна
function showNodeModal(nodeData) {
    const modal = document.getElementById('node-modal');
    const modalContent = document.getElementById('modal-content');

    modalContent.innerHTML = `
        <h3>${escapeHtml(nodeData.name)}</h3>
        <div class="modal-details">
            <div class="modal-detail">
                <span class="detail-label">Тип:</span>
                <span class="detail-value">${getNodeTypeDisplay(nodeData.node_type)}</span>
            </div>
            <div class="modal-detail">
                <span class="detail-label">Email:</span>
                <span class="detail-value">${escapeHtml(nodeData.email)}</span>
            </div>
            <div class="modal-detail">
                <span class="detail-label">Адрес:</span>
                <span class="detail-value">${escapeHtml(nodeData.city)}, ${escapeHtml(nodeData.country)}, ${escapeHtml(nodeData.street)} ${escapeHtml(nodeData.house_number)}</span>
            </div>
            <div class="modal-detail">
                <span class="detail-label">Задолженность:</span>
                <span class="detail-value ${nodeData.debt > 0 ? 'positive' : 'zero'}">${parseFloat(nodeData.debt).toFixed(2)} ₽</span>
            </div>
            ${nodeData.supplier ? `
            <div class="modal-detail">
                <span class="detail-label">Поставщик:</span>
                <span class="detail-value">${escapeHtml(nodeData.supplier.name)}</span>
            </div>
            ` : ''}
        </div>
    `;

    modal.style.display = 'block';
}

// Закрытие модального окна
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('node-modal');
    const closeBtn = document.querySelector('.close');

    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
