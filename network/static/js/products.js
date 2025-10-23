document.addEventListener('DOMContentLoaded', function() {
    loadProducts();
    setupEventListeners();
});

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

    console.log('Fetching products from:', url);

    // Загружаем данные с API
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Received products data:', data);

            // Обрабатываем как пагинированные, так и непагинированные данные
            const products = data.results || data;
            displayProducts(products);
        })
        .catch(error => {
            console.error('Error loading products:', error);
            showError('Ошибка загрузки данных: ' + error.message);
        })
        .finally(() => {
            loadingElement.style.display = 'none';
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
                <div class="product-model">${escapeHtml(product.model || '')}</div>
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
                    ${product.network_nodes.slice(0, 5).map(node => `
                        <div class="node-item">
                            <div class="node-info">
                                <span class="node-name">${escapeHtml(node.node_name)}</span>
                                <span class="node-status">${node.is_available ? '✅' : '❌'}</span>
                            </div>
                            <div class="node-price">${parseFloat(node.price || 0).toFixed(2)} ₽</div>
                        </div>
                    `).join('')}
                    ${product.network_nodes.length > 5 ? `
                        <div class="node-item">
                            <div class="node-info">... и еще ${product.network_nodes.length - 5} узлов</div>
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
                    Подробнее
                </button>
                <button class="action-btn assign" onclick="assignProductToNode(${product.id})">
                    Назначить узлу
                </button>
            </div>
        </div>
    `).join('');
}

// Вспомогательные функции
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
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU');
    } catch (e) {
        return 'Неверный формат';
    }
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
}

// Применение фильтров
function applyFilters() {
    const filters = {
        search: document.getElementById('search-filter').value.trim()
    };

    console.log('Applying filters:', filters);
    loadProducts(filters);
}

// Сброс фильтров
function resetFilters() {
    document.getElementById('search-filter').value = '';
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
    // Загружаем узлы сети для выбора
    fetch('/api/network-nodes/')
        .then(response => response.json())
        .then(data => {
            const nodes = data.results || data;
            if (nodes.length === 0) {
                alert('Нет доступных узлов сети');
                return;
            }

            const nodeList = nodes.map(node =>
                `${node.id}. ${node.name} (${getNodeTypeDisplay(node.node_type)})`
            ).join('\n');

            const nodeId = prompt(`Назначить продукт узлу сети. Введите ID узла:\n\n${nodeList}`);

            if (nodeId && !isNaN(nodeId)) {
                const price = prompt('Введите цену продукта в этом узле:');
                if (price && !isNaN(price)) {
                    assignProductToNodeAPI(productId, parseInt(nodeId), parseFloat(price));
                }
            }
        })
        .catch(error => {
            console.error('Error loading network nodes:', error);
            alert('Ошибка загрузки узлов сети');
        });
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

// Вспомогательная функция для отображения типа узла
function getNodeTypeDisplay(nodeType) {
    const types = {
        'factory': 'Завод',
        'retail': 'Розничная сеть',
        'entrepreneur': 'Индивидуальный предприниматель'
    };
    return types[nodeType] || nodeType;
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
                <span class="detail-value">${escapeHtml(product.model || '')}</span>
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
            <h4>Доступен в узлах (${product.network_nodes.length}):</h4>
            <div class="nodes-list-modal">
                ${product.network_nodes.map(node => `
                    <div class="node-item-modal">
                        <div class="node-info-modal">
                            <strong>${escapeHtml(node.node_name)}</strong>
                            <br>
                            <small>${getNodeTypeDisplay(node.node_type)} • ${node.is_available ? 'Доступен' : 'Не доступен'}</small>
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
