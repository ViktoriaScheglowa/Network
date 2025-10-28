document.addEventListener('DOMContentLoaded', function() {
    loadNodes();
    setupEventListeners();
    setupModalListeners();
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
            console.log('Received data:', data);
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
    // Кнопка "Применить" - основная точка фильтрации
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

// Функции для модального окна
function viewNodeDetails(nodeId) {
    console.log('Opening node details for ID:', nodeId);

    // Показываем загрузку в модальном окне
    const modal = document.getElementById('node-modal');
    const modalContent = document.getElementById('modal-content');

    modalContent.innerHTML = `
        <div class="loading">Загрузка данных...</div>
    `;
    modal.style.display = 'block';

    // Загружаем детали узла
    fetch(`/api/network-nodes/${nodeId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(nodeData => {
            console.log('Node data received:', nodeData);
            showNodeModal(nodeData);
        })
        .catch(error => {
            console.error('Error loading node details:', error);
            modalContent.innerHTML = `
                <div class="error-message">
                    Ошибка загрузки данных: ${error.message}
                </div>
            `;
        });
}

function viewNodeProducts(nodeId) {
    // Редирект на страницу продуктов узла
    window.location.href = `/node-products/?node=${nodeId}`;
}

// Функция для отображения модального окна с данными узла
function showNodeModal(nodeData) {
    const modalContent = document.getElementById('modal-content');

    // Определяем отображаемое имя поставщика и создаем ссылку если есть ID
    let supplierDisplay = 'Нет поставщика';
    let supplierId = null;

    if (nodeData.supplier_name) {
        supplierDisplay = escapeHtml(nodeData.supplier_name);
        supplierId = nodeData.supplier; // ID поставщика
    } else if (nodeData.supplier && typeof nodeData.supplier === 'object' && nodeData.supplier.name) {
        supplierDisplay = escapeHtml(nodeData.supplier.name);
        supplierId = nodeData.supplier.id;
    } else if (nodeData.supplier) {
        supplierDisplay = `ID: ${nodeData.supplier}`;
        supplierId = nodeData.supplier;
    }

    // Создаем HTML для поставщика (возможно с ссылкой)
    const supplierHtml = supplierId && supplierDisplay !== 'Нет поставщика'
        ? `<span class="supplier-link" onclick="viewNodeDetails(${supplierId})" style="color: #007bff; cursor: pointer; text-decoration: underline;">${supplierDisplay}</span>`
        : supplierDisplay;

    modalContent.innerHTML = `
        <h3>${escapeHtml(nodeData.name)}</h3>
        <div class="modal-details">
            <div class="modal-detail">
                <span class="detail-label">Тип:</span>
                <span class="detail-value">${getNodeTypeDisplay(nodeData.node_type)}</span>
            </div>
            <div class="modal-detail">
                <span class="detail-label">Email:</span>
                <span class="detail-value">${escapeHtml(nodeData.email || 'Не указан')}</span>
            </div>
            <div class="modal-detail">
                <span class="detail-label">Адрес:</span>
                <span class="detail-value">
                    ${escapeHtml(nodeData.city || 'Не указан')},
                    ${escapeHtml(nodeData.country || 'Не указана')}
                    ${nodeData.street ? `, ${escapeHtml(nodeData.street)}` : ''}
                    ${nodeData.house_number ? ` ${escapeHtml(nodeData.house_number)}` : ''}
                </span>
            </div>
            <div class="modal-detail">
                <span class="detail-label">Задолженность:</span>
                <span class="detail-value ${nodeData.debt > 0 ? 'positive' : 'zero'}">
                    ${parseFloat(nodeData.debt || 0).toFixed(2)} ₽
                </span>
            </div>
            <div class="modal-detail">
                <span class="detail-label">Поставщик:</span>
                <span class="detail-value">${supplierHtml}</span>
            </div>
            ${nodeData.hierarchy_level !== undefined ? `
            <div class="modal-detail">
                <span class="detail-label">Уровень иерархии:</span>
                <span class="detail-value">${nodeData.hierarchy_level}</span>
            </div>
            ` : ''}
            ${nodeData.created_at ? `
            <div class="modal-detail">
                <span class="detail-label">Дата создания:</span>
                <span class="detail-value">${new Date(nodeData.created_at).toLocaleDateString('ru-RU')}</span>
            </div>
            ` : ''}
        </div>
        <div class="modal-actions">
            ${nodeData.products_info && nodeData.products_info.length > 0 ? `
            <button class="btn-primary" onclick="viewNodeProducts(${nodeData.id})">Просмотреть продукты</button>
            ` : ''}
            <button class="btn-secondary" onclick="closeModal()">Закрыть</button>
        </div>
    `;
}

// Функция для закрытия модального окна
function closeModal() {
    const modal = document.getElementById('node-modal');
    modal.style.display = 'none';
}

function setupModalListeners() {
    const modal = document.getElementById('node-modal');
    const closeBtn = document.querySelector('.close');

    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            closeModal();
        });
    }

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModal();
        }
    });
}

function viewNodeProducts(nodeId) {
    console.log('Opening products for node ID:', nodeId);

    // Показываем загрузку в модальном окне
    const modal = document.getElementById('node-modal');
    const modalContent = document.getElementById('modal-content');

    modalContent.innerHTML = `
        <div class="loading">Загрузка продуктов...</div>
    `;
    modal.style.display = 'block';

    // Загружаем продукты узла
    fetch(`/api/network-nodes/${nodeId}/products/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(products => {
            console.log('Products data received:', products);
            showProductsModal(nodeId, products);
        })
        .catch(error => {
            console.error('Error loading products:', error);
            modalContent.innerHTML = `
                <div class="error-message">
                    Ошибка загрузки продуктов: ${error.message}
                </div>
            `;
        });
}

function showProductsModal(nodeId, products) {
    const modalContent = document.getElementById('modal-content');

    console.log('Products data for modal:', products);

    modalContent.innerHTML = `
        <h3>Продукты узла</h3>
        <div class="products-list">
            ${products && products.length > 0 ? `
                <table class="products-table">
                    <thead>
                        <tr>
                            <th>Название</th>
                            <th>Модель</th>
                            <th>Цена</th>
                            <th>Количество</th>
                            <th>Доступен</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${products.map(nodeProduct => {
                            // Данные продукта находятся в nodeProduct.product
                            const product = nodeProduct.product;
                            const productName = product.name || 'Не указано';
                            const productModel = product.model || 'Не указана';
                            const productPrice = nodeProduct.price || 0;
                            const productQuantity = nodeProduct.quantity || 0;
                            const isAvailable = nodeProduct.is_available ? 'Да' : 'Нет';

                            return `
                                <tr>
                                    <td>${escapeHtml(productName)}</td>
                                    <td>${escapeHtml(productModel)}</td>
                                    <td>${parseFloat(productPrice).toFixed(2)} ₽</td>
                                    <td>${productQuantity}</td>
                                    <td>${isAvailable}</td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
                <div class="products-summary" style="margin-top: 15px; padding: 10px; background: #f5f5f5; border-radius: 4px;">
                    <strong>Итого:</strong> ${products.length} продукт(ов) на сумму
                    ${products.reduce((total, nodeProduct) => {
                        const price = parseFloat(nodeProduct.price) || 0;
                        const quantity = parseInt(nodeProduct.quantity) || 0;
                        return total + (price * quantity);
                    }, 0).toFixed(2)} ₽
                </div>
            ` : `
                <p class="no-products">Нет продуктов для этого узла</p>
            `}
        </div>
        <div class="modal-actions" style="margin-top: 20px; text-align: right;">
            <button class="btn-secondary" onclick="closeModal()">Закрыть</button>
        </div>
    `;
}
