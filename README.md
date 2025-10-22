# 🏪 Electronics Network Platform
Платформа для управления сетью по продаже электроники с иерархической структурой поставщиков.
## 🚀 Возможности
* Управление узлами сети (заводы, розничные сети, индивидуальные предприниматели)
* Иерархическая структура поставщиков с автоматическим определением уровня
* Управление продуктами с привязкой к узлам сети
* Отслеживание задолженностей перед поставщиками
* REST API с полной документацией
* Админ-панель для управления данными
* Права доступа только для активных сотрудников
## 🏗️ Архитектура
Уровни иерархии:
* Уровень 0: Заводы (без поставщиков)
* Уровень 1: Розничные сети, работающие напрямую с заводами
* Уровень 2: Индивидуальные предприниматели и магазины

Модели данных:
* NetworkNode - узлы сети (заводы, магазины, ИП)
* Product - продукты/товары
* NetworkNodeProduct - связь узлов с продуктами (цена, количество)
* User - кастомная модель пользователя

## 🛠️ Технологический стек
* Python 3.10+
* Django 4.2
* Django REST Framework 3.14
* PostgreSQL 15
* DRF-YASG - документация API
* Django Filter - фильтрация данных
* CORS Headers - межсайтовые запросы

## Установка и запуск
1. Клонирование репозитория
git clone https://github.com/ViktoriaScheglowa/Network.git
cd Network
2. Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
 или
venv\Scripts\activate  # Windows
3. Установка зависимостей
pip install -r requirements.txt
4. Миграции базы данных
python manage.py makemigrations
python manage.py migrate
5. Создание суперпользователя
python manage.py createsuperuser
6. Запуск сервера
python manage.py runserver
Приложение будет доступно по адресу: http://localhost:8000
## 📚 API Endpoints
### Аутентификация
Все endpoints требуют аутентификации. Используйте:

Session аутентификацию через браузер
Basic аутентификацию для программного доступа

### Основные endpoints:
#### Узлы сети (/api/network-nodes/)
Метод	Endpoint	Описание
GET	/api/network-nodes/	Список всех узлов
POST	/api/network-nodes/	Создание узла
GET	/api/network-nodes/{id}/	Детали узла
PUT	/api/network-nodes/{id}/	Обновление узла
DELETE	/api/network-nodes/{id}/	Удаление узла
GET	/api/network-nodes/{id}/products/	Продукты узла
POST	/api/network-nodes/{id}/add-product/	Добавить продукт
DELETE	/api/network-nodes/{id}/remove-product/	Удалить продукт
GET	/api/network-nodes/{id}/supplier-chain/	Цепочка поставщиков
GET	/api/network-nodes/{id}/available-supplier-products/	Продукты поставщика
POST	/api/network-nodes/{id}/clear-debt/	Очистить задолженность
GET	/api/network-nodes/hierarchy/	Иерархия сети
GET	/api/network-nodes/statistics/	Статистика

#### Продукты (/api/products/)
Метод	Endpoint	Описание
GET	/api/products/	Список продуктов
POST	/api/products/	Создание продукта
GET	/api/products/{id}/	Детали продукта
PUT	/api/products/{id}/	Обновление продукта
DELETE	/api/products/{id}/	Удаление продукта
POST	/api/products/{id}/assign-to-node/	Назначить узлу
POST	/api/products/{id}/remove-from-node/	Удалить из узла
GET	/api/products/in-network/	Продукты в сети

#### Связи узел-продукт (/api/node-products/)
Метод	Endpoint	Описание
GET	/api/node-products/	Список связей
POST	/api/node-products/	Создание связи
GET	/api/node-products/{id}/	Детали связи
PUT	/api/node-products/{id}/	Обновление связи
DELETE	/api/node-products/{id}/	Удаление связи

### Фильтрация и поиск
#### Узлы сети:
?country=Russia - фильтр по стране
?city=Moscow - фильтр по городу
?node_type=factory - фильтр по типу узла
?has_debt=true - узлы с задолженностью
?search=keyword - поиск по названию, email, городу

#### Продукты:
?search=iphone - поиск по названию и модели
?release_date_after=2023-01-01 - продукты после даты

## ⚙️ Админ-панель
Админ-панель доступна по адресу: http://localhost:8000/admin/

### Возможности админ-панели:
📊 Просмотр всех узлов сети и продуктов
🔗 Ссылки на поставщиков со страниц узлов
🏙️ Фильтрация по городам
💰 Admin action для очистки задолженностей
🔍 Поиск по названиям и email

## 🔐 Права доступа
Доступ к API имеют только активные сотрудники
Требуется аутентификация для всех endpoints
Поле debt доступно только для чтения через API
Админ-панель доступна только staff-пользователям

## 📊 Документация API
Swagger UI: http://localhost:8000/swagger/

ReDoc: http://localhost:8000/redoc/

## Структура проекта
text
Network/
├── config/              # Настройки Django
├── network/              # Приложение сети
├── user/               # Управление пользователями
└── templates/          # HTML шаблоны

Лицензия
Этот проект распространяется под лицензией MIT. Подробнее см. в файле LICENSE.

📞 Поддержка
Для вопросов и предложений обращайтесь:

Email: vika.scheglowa@yandex.ru

GitHub: ViktoriaScheglowa
