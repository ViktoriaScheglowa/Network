document.addEventListener('DOMContentLoaded', function() {
    loadNetworkNodes(); // Сначала загружаем узлы для фильтра
    loadProducts();
    setupEventListeners();
});

let networkNodes = []; // Глобальная переменная для хранения узлов

// Загрузка списка узлов сети для фильтра
function loadNetworkNodes() {
    fetch('/api/network-nodes/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            networkNodes = data.results || data;
            populateNodeFilter();
        })
        .catch(error => {
            console.error('Error loading network nodes:', error);
        });
}

// Заполнение фильтра узлов
function populateNodeFilter() {
    const nodeFilter = document.getElementById('node-filter');

    // Очищаем существующие опции (кроме первой)
    while (nodeFilter.children.length > 1) {
        nodeFilter.removeChild(nodeFilter.lastChild);
    }

    // Добавляем узлы в фильтр
    networkNodes.forEach(node => {
        const option = document.createElement('option');
        option.value = node.id;
        option.textContent = `${node.name} (${getNodeTypeDisplay(node.node_type)})`;
        nodeFilter.appendChild(option);
    });
}

// Загрузка продуктов
function loadProducts(filters = {}) {
    const loadingElement = document.getElementById('loading-message');
    const noDataElement = document.getElementById('no-products-message');
    const productsContainer = document.getElementById('products-container');

    // Показываем загрузку
    loadingElement.style.display = 'block';
    noDataElement.style.display = 'none';
    productsContainer.innerHTML = '';

    // Строим URL с фильтрами
    let url = '/api/products/';
    const params = new URLSearchParams();

    if (filters.search) {
        params.append('search', filters.search);
    }

    if (params.toString()) {
        url += '?' + params.toString();
    }

    // Загружаем данные с API
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Если выбран узел в фильтре, фильтруем продукты по узлу
            if (filters.node_id) {
                data = filterProductsByNode(data, filters.node_id);
            }
            displayProducts(data.results || data);
        })
        .catch(error => {
            console.error('Error loading products:', error);
            showError('Ошибка загрузки данных');
        })
        .finally(() => {
            loadingElement.style.display = 'none';
        });
}

// Фильтрация продуктов по узлу сети
function filterProductsByNode(products, nodeId) {
    return products.filter(product => {
        // Проверяем, есть ли продукт в указанном узле
        if (product.network_nodes && product.network_nodes.length > 0) {
            return product.network_nodes.some(node => node.node_id == nodeId);
        }
        return false;
    });
}

// Отображение продуктов
function displayProducts(products) {
    const productsContainer = document.getElementById('products-container');
    const noDataElement = document.getElementById('no-products-message');

    if (!products || products.length === 0) {
        noDataElement.style.display = 'block';
        productsContainer.innerHTML = '';
        return;
    }

    noDataElement.style.display = 'none';

    productsContainer.innerHTML = products.map(product => `
        <div class="product-card">
            <div class="product-header">
                <div class="product-name">${escapeHtml(product.name)}</div>
                <div class="product-model">${escapeHtml(product.model)}</div>
            </div>
            <div class="product-details">
                <div class="product-detail">
                    <i>📅</i> Дата выхода: ${formatDate(product.release_date)}
                </div>
                <div class="product-detail">
                    <i>🆔</i> ID: ${product.id}
                </div>
            </div>

            ${product.network_nodes && product.network_nodes.length > 0 ? `
            <div class="product-nodes">
                <h4>Доступен в узлах:</h4>
                <div class="nodes-list">
                    ${product.network_nodes.slice(0, 3).map(node => `
                        <div class="node-item">
                            <div class="node-info">
                                ${escapeHtml(node.node_name)}
                                ${node.is_available ? '✅' : '❌'}
                            </div>
                            <div class="node-price">${parseFloat(node.price || 0).toFixed(2)} ₽</div>
                        </div>
                    `).join('')}
                    ${product.network_nodes.length > 3 ? `
                        <div class="node-item">
                            <div class="node-info">... и еще ${product.network_nodes.length - 3} узлов</div>
                        </div>
                    ` : ''}
                </div>
            </div>
            ` : `
            <div class="product-nodes">
                <p style="color: #95a5a6; font-style: italic;">Не доступен ни в одном узле</p>
            </div>
            `}

            <div class="product-actions">
                <button class="action-btn view" onclick="viewProductDetails(${product.id})">
                    Просмотр
                </button>
                <button class="action-btn assign" onclick="assignProductToNode(${product.id})">
                    Назначить узлу
                </button>
            </div>
        </div>
    `).join('');
}

// Вспомогательные функции
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

function formatDate(dateString) {
    if (!dateString) return 'Не указана';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

// Настройка обработчиков событий
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

    // Автозагрузка при изменении фильтров
    document.getElementById('node-filter').addEventListener('change', function() {
        applyFilters();
    });
}

// Применение фильтров
function applyFilters() {
    const filters = {
        search: document.getElementById('search-filter').value.trim(),
        node_id: document.getElementById('node-filter').value
    };

    loadProducts(filters);
}

// Сброс фильтров
function resetFilters() {
    document.getElementById('search-filter').value = '';
    document.getElementById('node-filter').value = '';
    loadProducts();
}

// Показать ошибку
function showError(message) {
    const productsContainer = document.getElementById('products-container');
    const noDataElement = document.getElementById('no-products-message');

    productsContainer.innerHTML = '';
    noDataElement.textContent = message;
    noDataElement.style.display = 'block';
}

// Функции для работы с продуктами
function viewProductDetails(productId) {
    fetch(`/api/products/${productId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Product not found');
            }
            return response.json();
        })
        .then(product => {
            showProductModal(product);
        })
        .catch(error => {
            console.error('Error loading product details:', error);
            alert('Ошибка загрузки деталей продукта');
        });
}

function assignProductToNode(productId) {
    if (networkNodes.length === 0) {
        alert('Сначала нужно загрузить узлы сети');
        return;
    }

    // Создаем простое модальное окно для назначения продукта
    const nodeList = networkNodes.map(node =>
        `${node.id}. ${node.name} (${getNodeTypeDisplay(node.node_type)})`
    ).join('\n');

    const nodeId = prompt(`Назначить продукт узлу сети. Введите ID узла:\n\n${nodeList}`);

    if (nodeId && !isNaN(nodeId)) {
        const price = prompt('Введите цену продукта в этом узле:');
        if (price && !isNaN(price)) {
            assignProductToNodeAPI(productId, parseInt(nodeId), parseFloat(price));
        }
    }
}

function assignProductToNodeAPI(productId, nodeId, price) {
    const data = {
        product_id: productId,
        price: price,
        quantity: 1,
        is_available: true
    };

    fetch(`/api/network-nodes/${nodeId}/add-product/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.status === 403) {
            throw new Error('Доступ запрещен. Возможно, нужна аутентификация.');
        }
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(result => {
        alert('Продукт успешно назначен узлу!');
        loadProducts(); // Перезагружаем список
    })
    .catch(error => {
        console.error('Error assigning product:', error);
        alert('Ошибка назначения продукта узлу: ' + error.message);
    });
}

// Получение CSRF токена
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Модальное окно для деталей продукта
function showProductModal(product) {
    const modal = document.getElementById('product-modal');
    const modalContent = document.getElementById('modal-content');

    modalContent.innerHTML = `
        <h3>${escapeHtml(product.name)}</h3>
        <div class="modal-details">
            <div class="modal-detail">
                <span class="detail-label">Модель:</span>
                <span class="detail-value">${escapeHtml(product.model)}</span>
            </div>
            <div class="modal-detail">
                <span class="detail-label">Дата выхода:</span>
                <span class="detail-value">${formatDate(product.release_date)}</span>
            </div>
            <div class="modal-detail">
                <span class="detail-label">ID:</span>
                <span class="detail-value">${product.id}</span>
            </div>
            <div class="modal-detail">
                <span class="detail-label">Дата создания:</span>
                <span class="detail-value">${formatDate(product.created_at)}</span>
            </div>
        </div>

        ${product.network_nodes && product.network_nodes.length > 0 ? `
        <div class="modal-section">
            <h4>Доступен в узлах:</h4>
            <div class="nodes-list-modal">
                ${product.network_nodes.map(node => `
                    <div class="node-item-modal">
                        <div class="node-info-modal">
                            <strong>${escapeHtml(node.node_name)}</strong>
                            <br>
                            <small>${getNodeTypeDisplay(getNodeTypeById(node.node_id))} • ${node.is_available ? 'Доступен' : 'Не доступен'}</small>
                        </div>
                        <div class="node-details-modal">
                            <div>Цена: ${parseFloat(node.price || 0).toFixed(2)} ₽</div>
                            <div>Количество: ${node.quantity || 0} шт.</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : `
        <div class="modal-section">
            <p style="color: #95a5a6; font-style: italic;">Продукт не доступен ни в одном узле сети</p>
        </div>
        `}
    `;

    modal.style.display = 'block';
}

// Получение типа узла по ID
function getNodeTypeById(nodeId) {
    const node = networkNodes.find(n => n.id == nodeId);
    return node ? node.node_type : 'unknown';
}

// Закрытие модального окна
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('product-modal');
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
