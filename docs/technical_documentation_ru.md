# AssetHub - Техническая документация для разработчиков

## Содержание

1. [Введение](#введение)
2. [Архитектура проекта](#архитектура-проекта)
   - [Общая структура](#общая-структура)
   - [Модули и их взаимодействие](#модули-и-их-взаимодействие)
   - [Диаграмма компонентов](#диаграмма-компонентов)
3. [Настройка окружения разработки](#настройка-окружения-разработки)
   - [Требования к системе](#требования-к-системе)
   - [Установка зависимостей](#установка-зависимостей)
   - [Настройка IDE](#настройка-ide)
4. [Модели данных](#модели-данных)
   - [Структура базы данных](#структура-базы-данных)
   - [Отношения между моделями](#отношения-между-моделями)
   - [Миграции](#миграции)
5. [Каталогизация и поиск](#каталогизация-и-поиск)
   - [Сканирование файлов](#сканирование-файлов)
   - [Индексация](#индексация)
   - [Поисковый движок](#поисковый-движок)
6. [Интеграция с внешними сервисами](#интеграция-с-внешними-сервисами)
   - [Архитектура провайдеров](#архитектура-провайдеров)
   - [Настройка API-ключей](#настройка-api-ключей)
   - [Добавление новых провайдеров](#добавление-новых-провайдеров)
7. [Пользовательский интерфейс](#пользовательский-интерфейс)
   - [Архитектура UI](#архитектура-ui)
   - [Компоненты интерфейса](#компоненты-интерфейса)
   - [Расширение интерфейса](#расширение-интерфейса)
8. [Плагин для 3ds Max](#плагин-для-3ds-max)
   - [Архитектура плагина](#архитектура-плагина)
   - [Интеграция с 3ds Max](#интеграция-с-3ds-max)
   - [Расширение функциональности плагина](#расширение-функциональности-плагина)
9. [Тестирование](#тестирование)
   - [Модульные тесты](#модульные-тесты)
   - [Интеграционные тесты](#интеграционные-тесты)
   - [UI-тесты](#ui-тесты)
10. [CI/CD](#cicd)
    - [Настройка GitHub Actions](#настройка-github-actions)
    - [Автоматическое тестирование](#автоматическое-тестирование)
    - [Сборка и публикация](#сборка-и-публикация)
11. [Стиль кода и лучшие практики](#стиль-кода-и-лучшие-практики)
    - [Соглашения о стиле кода](#соглашения-о-стиле-кода)
    - [Документирование кода](#документирование-кода)
    - [Обработка ошибок](#обработка-ошибок)
12. [Руководство по вкладу в проект](#руководство-по-вкладу-в-проект)
    - [Процесс разработки](#процесс-разработки)
    - [Pull Requests](#pull-requests)
    - [Code Review](#code-review)
13. [Часто задаваемые вопросы](#часто-задаваемые-вопросы)
14. [Приложения](#приложения)
    - [Глоссарий](#глоссарий)
    - [Ссылки на ресурсы](#ссылки-на-ресурсы)

## Введение

AssetHub — это универсальная платформа управления ресурсами для дизайнеров, работающих с 3ds Max. Платформа предоставляет централизованный доступ к локальным и облачным библиотекам 3D-моделей, текстур и материалов, значительно упрощая рабочий процесс визуализации проектов.

Данная документация предназначена для разработчиков, желающих расширить функциональность AssetHub, внести свой вклад в проект или интегрировать AssetHub с другими системами. Документация содержит подробное описание архитектуры, компонентов, API и процессов разработки.

### Цели проекта

- Упростить управление 3D-ресурсами для дизайнеров
- Обеспечить быстрый поиск и доступ к моделям, текстурам и материалам
- Интегрировать локальные и облачные библиотеки ресурсов
- Предоставить прямую интеграцию с 3ds Max
- Создать расширяемую платформу для добавления новых функций и интеграций

### Технологический стек

- **Язык программирования**: Python 3.9+
- **Управление зависимостями**: Poetry
- **База данных**: SQLite (SQLAlchemy ORM)
- **Поисковый движок**: Whoosh
- **Пользовательский интерфейс**: PyQt5
- **Интеграция с 3ds Max**: Python API для 3ds Max
- **Тестирование**: pytest
- **CI/CD**: GitHub Actions

## Архитектура проекта

### Общая структура

AssetHub построен на модульной архитектуре с четким разделением ответственности между компонентами. Проект организован в следующую структуру каталогов:

```
assethub_project/
├── assethub/
│   ├── core/              # Основная функциональность
│   │   ├── config.py      # Управление конфигурацией
│   │   └── models.py      # Модели данных
│   ├── catalog/           # Каталогизация и поиск ресурсов
│   │   ├── scanner.py     # Сканер файлов
│   │   ├── indexer.py     # Индексатор поиска
│   │   └── search.py      # Поисковый движок
│   ├── integration/       # Интеграция с внешними библиотеками
│   │   ├── providers/     # Реализации провайдеров
│   │   │   ├── base.py    # Базовый интерфейс провайдера
│   │   │   ├── turbosquid.py # Провайдер Turbosquid
│   │   │   └── cgtrader.py # Провайдер CGTrader
│   │   └── __init__.py    # Менеджер интеграции
│   ├── ui/                # Пользовательский интерфейс
│   │   └── app.py         # Основное приложение
│   ├── plugin/            # Плагин для 3ds Max
│   │   └── max_integration.py # Интеграция с 3ds Max
│   └── tests/             # Модульные тесты
├── docs/                  # Документация
├── main.py                # Точка входа в приложение
├── pyproject.toml         # Метаданные проекта и зависимости
└── README.md              # Обзор проекта
```

### Модули и их взаимодействие

AssetHub состоит из следующих основных модулей:

1. **Core Module** (assethub/core/):
   - Предоставляет базовую функциональность для всех других модулей
   - Управляет конфигурацией приложения
   - Определяет модели данных и взаимодействие с базой данных

2. **Catalog Module** (assethub/catalog/):
   - Отвечает за сканирование, индексацию и поиск ресурсов
   - Извлекает метаданные из файлов ресурсов
   - Обеспечивает быстрый поиск по различным критериям

3. **Integration Module** (assethub/integration/):
   - Управляет интеграцией с внешними библиотеками ресурсов
   - Предоставляет унифицированный интерфейс для различных провайдеров
   - Обрабатывает аутентификацию, поиск и загрузку ресурсов

4. **UI Module** (assethub/ui/):
   - Реализует пользовательский интерфейс приложения
   - Обеспечивает взаимодействие пользователя с функциями приложения
   - Отображает результаты поиска и детали ресурсов

5. **Plugin Module** (assethub/plugin/):
   - Обеспечивает интеграцию с 3ds Max
   - Позволяет импортировать ресурсы непосредственно в 3ds Max
   - Предоставляет доступ к функциям AssetHub из 3ds Max

### Диаграмма компонентов

```
+----------------+      +----------------+      +----------------+
|                |      |                |      |                |
|  UI Module     |<---->|  Core Module   |<---->| Plugin Module  |
|                |      |                |      |                |
+----------------+      +-------^--------+      +----------------+
                               |
                               |
                 +-------------+-------------+
                 |                           |
        +--------v---------+      +----------v-------+
        |                  |      |                  |
        | Catalog Module   |<---->| Integration      |
        |                  |      | Module           |
        +------------------+      +------------------+
```

## Настройка окружения разработки

### Требования к системе

- Windows 10 или новее (для полной функциональности с 3ds Max)
- Python 3.9-3.11
- Git
- 3ds Max 2020 или новее (для тестирования плагина)

### Установка зависимостей

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/dedvassi/assethub.git
   cd assethub
   ```

2. Создайте виртуальное окружение:
   ```bash
   # Используя venv
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/macOS
   
   # Или используя Poetry
   poetry install
   ```

3. Установите зависимости:
   ```bash
   # Используя pip
   pip install -e .
   
   # Или используя Poetry
   poetry install
   ```

### Настройка IDE

#### Visual Studio Code

1. Установите расширения:
   - Python
   - Pylance
   - Python Test Explorer
   - SQLite Viewer

2. Настройте settings.json:
   ```json
   {
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true,
     "python.linting.flake8Enabled": true,
     "python.formatting.provider": "black",
     "python.formatting.blackArgs": ["--line-length", "88"],
     "editor.formatOnSave": true,
     "python.testing.pytestEnabled": true,
     "python.testing.unittestEnabled": false,
     "python.testing.nosetestsEnabled": false,
     "python.testing.pytestArgs": [
       "assethub/tests"
     ]
   }
   ```

#### PyCharm

1. Откройте проект в PyCharm
2. Настройте интерпретатор Python:
   - File > Settings > Project > Python Interpreter
   - Выберите интерпретатор из виртуального окружения

3. Настройте инструменты форматирования:
   - File > Settings > Tools > Python Integrated Tools
   - Docstrings: Google
   - Test runner: pytest

## Модели данных

### Структура базы данных

AssetHub использует SQLAlchemy ORM для взаимодействия с базой данных SQLite. Основные модели данных определены в `assethub/core/models.py`:

1. **Asset** - представляет 3D-модель, текстуру или материал:
   - Основные атрибуты: id, name, description, file_path, file_size, file_type, file_format
   - Метаданные: created_at, updated_at, last_accessed, access_count
   - Информация об источнике: source, source_url, source_id
   - Специфические атрибуты для моделей: vertex_count, face_count, material_count
   - Специфические атрибуты для текстур: width, height, channels

2. **Tag** - представляет тег для ресурсов:
   - Атрибуты: id, name, description
   - Отношения: many-to-many с Asset

3. **Category** - представляет категорию для ресурсов:
   - Атрибуты: id, name, description, parent_id
   - Отношения: many-to-many с Asset, self-referential для иерархии категорий

4. **SearchIndex** - представляет метаданные поискового индекса:
   - Атрибуты: id, path, last_updated, document_count

### Отношения между моделями

```
Asset <---> Tag (Many-to-Many)
Asset <---> Category (Many-to-Many)
Category <---> Category (Self-referential, Parent-Child)
```

### Миграции

В текущей версии AssetHub не использует систему миграций, так как база данных создается автоматически при первом запуске приложения. В будущих версиях планируется добавить поддержку миграций с использованием Alembic.

## Каталогизация и поиск

### Сканирование файлов

Модуль `assethub/catalog/scanner.py` отвечает за сканирование директорий и файлов, извлечение метаданных и добавление ресурсов в базу данных.

Основные функции:

- `scan_directory(directory, recursive=True)` - сканирует директорию на наличие поддерживаемых файлов
- `scan_file(file_path)` - сканирует отдельный файл и извлекает метаданные
- `_get_file_type(file_path)` - определяет тип и формат файла по расширению
- `_extract_metadata(file_path, file_type, file_format)` - извлекает метаданные из файла

Поддерживаемые типы файлов:

- **Модели**: .obj, .fbx, .3ds, .max, .blend, .dae, .stl, .ply
- **Текстуры**: .jpg, .jpeg, .png, .tif, .tiff, .bmp, .tga, .hdr, .exr
- **Материалы**: .mtl, .mat, .xml, .json

### Индексация

Модуль `assethub/catalog/indexer.py` отвечает за создание и обновление поискового индекса с использованием библиотеки Whoosh.

Основные функции:

- `create_index()` - создает новый поисковый индекс
- `rebuild_index()` - перестраивает индекс с нуля
- `index_assets(assets)` - индексирует список ресурсов
- `remove_asset(asset_id)` - удаляет ресурс из индекса

Структура индекса:

```python
schema = Schema(
    id=ID(stored=True, unique=True),
    name=TEXT(stored=True, field_boost=2.0),
    description=TEXT(stored=True),
    file_path=ID(stored=True),
    file_type=TEXT(stored=True),
    file_format=TEXT(stored=True),
    tags=KEYWORD(stored=True, commas=True, lowercase=True),
    categories=KEYWORD(stored=True, commas=True, lowercase=True),
    source=TEXT(stored=True),
    content=TEXT
)
```

### Поисковый движок

Модуль `assethub/catalog/search.py` предоставляет функциональность поиска ресурсов с использованием индекса Whoosh.

Основные функции:

- `search(query_string, fields=None, filters=None, limit=50)` - выполняет поиск ресурсов
- `get_asset_by_id(asset_id)` - получает ресурс по ID
- `get_tags()` - получает все уникальные теги
- `get_categories()` - получает все уникальные категории
- `get_file_types()` - получает все уникальные типы файлов
- `get_file_formats()` - получает все уникальные форматы файлов

Пример использования:

```python
from assethub.catalog.search import AssetSearch

search_engine = AssetSearch()
results = search_engine.search("wooden chair", 
                              filters={"file_type": "model", "file_format": "obj"})
```

## Интеграция с внешними сервисами

### Архитектура провайдеров

AssetHub использует систему провайдеров для интеграции с внешними библиотеками ресурсов. Каждый провайдер реализует общий интерфейс, определенный в `assethub/integration/providers/base.py`.

Базовый класс провайдера:

```python
class BaseProvider(abc.ABC):
    """Base class for external asset library providers."""
    
    @abc.abstractmethod
    def connect(self):
        """Connect to the external library."""
        pass
        
    @abc.abstractmethod
    def search(self, query, asset_type=None, page=1, page_size=20):
        """Search for assets in the external library."""
        pass
        
    @abc.abstractmethod
    def get_asset_details(self, asset_id):
        """Get detailed information about an asset."""
        pass
        
    @abc.abstractmethod
    def download_asset(self, asset_id, destination_path):
        """Download an asset from the external library."""
        pass
        
    @abc.abstractmethod
    def get_preview(self, asset_id, destination_path):
        """Download a preview image for an asset."""
        pass
```

Текущие реализации провайдеров:

- `TurbosquidProvider` (assethub/integration/providers/turbosquid.py)
- `CGTraderProvider` (assethub/integration/providers/cgtrader.py)

### Настройка API-ключей

Для работы с внешними сервисами требуются API-ключи, которые хранятся в конфигурационном файле. По умолчанию конфигурационный файл находится в `~/.assethub/config.json`.

Структура конфигурационного файла:

```json
{
  "general": {
    "storage_path": "~/.assethub/assets",
    "index_path": "~/.assethub/index",
    "db_path": "~/.assethub/database.db"
  },
  "integration": {
    "turbosquid": {
      "api_key": "YOUR_TURBOSQUID_API_KEY",
      "api_url": "https://api.turbosquid.com/v1"
    },
    "cgtrader": {
      "api_key": "YOUR_CGTRADER_API_KEY",
      "api_url": "https://api.cgtrader.com/v1"
    }
  }
}
```

Для получения API-ключей:

1. **Turbosquid API**:
   - Зарегистрируйтесь на сайте [Turbosquid](https://www.turbosquid.com/)
   - Перейдите в раздел разработчиков: https://www.turbosquid.com/developers
   - Запросите доступ к API, заполнив форму запроса
   - После одобрения вы получите API-ключ в личном кабинете

2. **CGTrader API**:
   - Создайте аккаунт на [CGTrader](https://www.cgtrader.com/)
   - Перейдите в раздел API: https://www.cgtrader.com/pages/api
   - Заполните форму запроса на доступ к API
   - После рассмотрения запроса вам предоставят API-ключ

После получения ключей добавьте их в конфигурационный файл или используйте метод `config.set()`:

```python
from assethub.core.config import config

config.set("integration", "turbosquid", "api_key", "YOUR_TURBOSQUID_API_KEY")
config.set("integration", "cgtrader", "api_key", "YOUR_CGTRADER_API_KEY")
config.save_config()
```

### Добавление новых провайдеров

Для добавления нового провайдера:

1. Создайте новый файл в `assethub/integration/providers/` (например, `sketchfab.py`)
2. Реализуйте класс провайдера, наследующийся от `BaseProvider`
3. Зарегистрируйте провайдер в `assethub/integration/__init__.py`

Пример реализации нового провайдера:

```python
# assethub/integration/providers/sketchfab.py
import requests
from assethub.integration.providers.base import BaseProvider
from assethub.core.config import config

class SketchfabProvider(BaseProvider):
    """Provider for Sketchfab 3D model library."""
    
    def __init__(self):
        """Initialize the Sketchfab provider."""
        self.api_key = config.get("integration", "sketchfab", "api_key")
        self.api_url = config.get("integration", "sketchfab", "api_url", 
                                 "https://api.sketchfab.com/v3")
        self.session = None
        
    def connect(self):
        """Connect to Sketchfab API."""
        if not self.api_key:
            raise ValueError("Sketchfab API key not provided")
            
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        })
        return True
        
    def search(self, query, asset_type=None, page=1, page_size=20):
        """Search for assets in Sketchfab."""
        if not self.session:
            self.connect()
            
        params = {
            "q": query,
            "page": page,
            "count": page_size
        }
        
        if asset_type:
            params["type"] = asset_type
            
        response = self.session.get(f"{self.api_url}/models", params=params)
        response.raise_for_status()
        
        data = response.json()
        return {
            "results": data.get("results", []),
            "total": data.get("count", 0),
            "page": page,
            "page_size": page_size
        }
        
    def get_asset_details(self, asset_id):
        """Get detailed information about an asset."""
        if not self.session:
            self.connect()
            
        response = self.session.get(f"{self.api_url}/models/{asset_id}")
        response.raise_for_status()
        
        return response.json()
        
    def download_asset(self, asset_id, destination_path):
        """Download an asset from Sketchfab."""
        if not self.session:
            self.connect()
            
        # Request download URL
        response = self.session.get(f"{self.api_url}/models/{asset_id}/download")
        response.raise_for_status()
        
        download_data = response.json()
        download_url = download_data.get("download_url")
        
        if not download_url:
            raise ValueError("Download URL not available")
            
        # Download the file
        response = self.session.get(download_url, stream=True)
        response.raise_for_status()
        
        with open(destination_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return destination_path
        
    def get_preview(self, asset_id, destination_path):
        """Download a preview image for an asset."""
        if not self.session:
            self.connect()
            
        # Get asset details to find preview URL
        details = self.get_asset_details(asset_id)
        preview_url = details.get("thumbnails", {}).get("images", [{}])[0].get("url")
        
        if not preview_url:
            raise ValueError("Preview image not available")
            
        # Download the preview image
        response = self.session.get(preview_url, stream=True)
        response.raise_for_status()
        
        with open(destination_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return destination_path
```

Регистрация нового провайдера:

```python
# assethub/integration/__init__.py
from assethub.integration.providers.sketchfab import SketchfabProvider

# В методе _register_providers класса IntegrationManager
def _register_providers(self):
    """Register all available providers."""
    from assethub.integration.providers.turbosquid import TurbosquidProvider
    from assethub.integration.providers.cgtrader import CGTraderProvider
    from assethub.integration.providers.sketchfab import SketchfabProvider
    
    self.register_provider("turbosquid", TurbosquidProvider)
    self.register_provider("cgtrader", CGTraderProvider)
    self.register_provider("sketchfab", SketchfabProvider)
```

## Пользовательский интерфейс

### Архитектура UI

AssetHub использует PyQt5 для создания пользовательского интерфейса. Основной класс интерфейса — `AssetHubMainWindow`, определенный в `assethub/ui/app.py`.

Архитектура UI следует паттерну Model-View-Controller (MVC):

- **Model**: Модели данных из `assethub/core/models.py`
- **View**: Виджеты PyQt5 для отображения данных
- **Controller**: Обработчики событий и бизнес-логика в `AssetHubMainWindow`

### Компоненты интерфейса

Основные компоненты пользовательского интерфейса:

1. **Главное окно** (`AssetHubMainWindow`):
   - Содержит все остальные компоненты
   - Управляет общим состоянием приложения
   - Обрабатывает основные события

2. **Боковая панель** (`SidebarWidget`):
   - Отображает категории и теги
   - Позволяет фильтровать ресурсы

3. **Панель поиска** (`SearchWidget`):
   - Содержит поле ввода для поиска
   - Предоставляет фильтры по типу и формату файла

4. **Список результатов** (`ResultsListWidget`):
   - Отображает результаты поиска
   - Поддерживает выбор и контекстное меню

5. **Панель детализации** (`DetailWidget`):
   - Отображает подробную информацию о выбранном ресурсе
   - Предоставляет кнопки для действий с ресурсом

6. **Диалог сканирования** (`ScanDialog`):
   - Позволяет выбрать директорию для сканирования
   - Отображает прогресс сканирования

7. **Диалог настроек** (`SettingsDialog`):
   - Позволяет настроить параметры приложения
   - Управляет API-ключами для внешних сервисов

### Расширение интерфейса

Для расширения пользовательского интерфейса можно:

1. **Добавить новый виджет**:
   - Создайте новый класс, наследующийся от `QWidget`
   - Реализуйте необходимую функциональность
   - Интегрируйте виджет в главное окно

2. **Расширить существующий виджет**:
   - Наследуйтесь от существующего класса виджета
   - Переопределите необходимые методы
   - Замените оригинальный виджет на расширенный

3. **Добавить новое действие**:
   - Создайте новый метод в `AssetHubMainWindow`
   - Добавьте пункт меню или кнопку, вызывающую этот метод
   - Реализуйте обработку события

Пример добавления нового виджета:

```python
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal

class StatisticsWidget(QWidget):
    """Widget for displaying asset statistics."""
    
    refreshRequested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel("Asset Statistics")
        layout.addWidget(self.title_label)
        
        self.total_label = QLabel("Total assets: 0")
        layout.addWidget(self.total_label)
        
        self.models_label = QLabel("Models: 0")
        layout.addWidget(self.models_label)
        
        self.textures_label = QLabel("Textures: 0")
        layout.addWidget(self.textures_label)
        
        self.materials_label = QLabel("Materials: 0")
        layout.addWidget(self.materials_label)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refreshRequested.emit)
        layout.addWidget(self.refresh_button)
        
        layout.addStretch()
        
    def update_statistics(self, stats):
        """Update the statistics display."""
        self.total_label.setText(f"Total assets: {stats['total']}")
        self.models_label.setText(f"Models: {stats['models']}")
        self.textures_label.setText(f"Textures: {stats['textures']}")
        self.materials_label.setText(f"Materials: {stats['materials']}")
```

Интеграция нового виджета в главное окно:

```python
# В классе AssetHubMainWindow

def setup_ui(self):
    # ... существующий код ...
    
    # Добавление виджета статистики
    self.statistics_widget = StatisticsWidget()
    self.statistics_widget.refreshRequested.connect(self.update_statistics)
    self.right_layout.addWidget(self.statistics_widget)
    
    # ... существующий код ...

def update_statistics(self):
    """Update asset statistics."""
    session = get_session()
    total = session.query(Asset).count()
    models = session.query(Asset).filter(Asset.file_type == "model").count()
    textures = session.query(Asset).filter(Asset.file_type == "texture").count()
    materials = session.query(Asset).filter(Asset.file_type == "material").count()
    
    stats = {
        "total": total,
        "models": models,
        "textures": textures,
        "materials": materials
    }
    
    self.statistics_widget.update_statistics(stats)
```

## Плагин для 3ds Max

### Архитектура плагина

Плагин для 3ds Max реализован в модуле `assethub/plugin/max_integration.py`. Он использует Python API для 3ds Max для интеграции с AssetHub.

Основные компоненты плагина:

1. **AssetHubMaxPlugin** - основной класс плагина:
   - Инициализирует интерфейс плагина
   - Обрабатывает взаимодействие с 3ds Max
   - Управляет импортом ресурсов

2. **AssetHubMaxUI** - пользовательский интерфейс плагина:
   - Отображает окно поиска и выбора ресурсов
   - Предоставляет доступ к функциям AssetHub

### Интеграция с 3ds Max

Плагин интегрируется с 3ds Max через Python API. Для установки плагина:

1. Скопируйте файл `assethub/plugin/max_integration.py` в директорию скриптов 3ds Max:
   ```
   %APPDATA%\Autodesk\3ds Max 20XX\ENU\scripts\startup\
   ```

2. Перезапустите 3ds Max

3. Запустите плагин через меню MAXScript:
   ```
   MAXScript > Run Script > выберите max_integration.py
   ```

Плагин добавляет пункт меню "AssetHub" в главное меню 3ds Max, который открывает окно AssetHub для поиска и импорта ресурсов.

### Расширение функциональности плагина

Для расширения функциональности плагина:

1. **Добавление новых команд**:
   - Создайте новый метод в классе `AssetHubMaxPlugin`
   - Добавьте пункт меню или кнопку, вызывающую этот метод
   - Реализуйте обработку команды

2. **Расширение интерфейса**:
   - Модифицируйте класс `AssetHubMaxUI`
   - Добавьте новые элементы интерфейса
   - Свяжите их с соответствующими методами

3. **Добавление поддержки новых типов файлов**:
   - Расширьте метод `import_asset` для обработки новых типов файлов
   - Добавьте соответствующие импортеры

Пример добавления новой команды:

```python
# В классе AssetHubMaxPlugin

def export_scene_to_assethub(self):
    """Export current scene to AssetHub library."""
    # Get current scene file
    scene_file = rt.maxFileName
    if not scene_file:
        rt.messageBox("Please save the scene first.")
        return
        
    # Get scene info
    scene_name = os.path.splitext(os.path.basename(scene_file))[0]
    
    # Create export dialog
    result = rt.dotNetObject("System.Windows.Forms.SaveFileDialog")
    result.Filter = "3ds Max Files (*.max)|*.max"
    result.Title = "Export to AssetHub"
    result.FileName = scene_name
    result.InitialDirectory = config.get_storage_path()
    
    if result.ShowDialog() == rt.dotNetObject("System.Windows.Forms.DialogResult").OK:
        export_path = result.FileName
        
        # Save a copy of the scene
        rt.saveMaxFile(export_path, useNewFile=False, quiet=True)
        
        # Add to AssetHub
        session = get_session()
        scanner = AssetScanner()
        asset = scanner.scan_file(export_path)
        
        if asset:
            indexer = AssetIndexer()
            indexer.index_assets([asset])
            rt.messageBox(f"Scene exported to AssetHub: {asset.name}")
        else:
            rt.messageBox("Failed to export scene to AssetHub.")
```

Добавление пункта меню для новой команды:

```python
# В методе create_menu класса AssetHubMaxPlugin

def create_menu(self):
    """Create AssetHub menu in 3ds Max."""
    main_menu = rt.menuMan.getMainMenuBar()
    
    # Create AssetHub menu
    assethub_menu = rt.menuMan.createMenu("AssetHub")
    
    # Create menu items
    open_item = rt.menuMan.createActionItem("OpenAssetHub", "AssetHub")
    export_item = rt.menuMan.createActionItem("ExportToAssetHub", "AssetHub")
    
    # Add actions to menu items
    open_action = rt.callbacks.addScript(open_item, "on_execute", "python.execute(\"assethub_plugin.open_assethub()\")")
    export_action = rt.callbacks.addScript(export_item, "on_execute", "python.execute(\"assethub_plugin.export_scene_to_assethub()\")")
    
    # Add items to menu
    assethub_menu.addItem(open_item, -1)
    assethub_menu.addItem(export_item, -1)
    
    # Create menu item in main menu
    menu_item = rt.menuMan.createSubMenuItem("AssetHub", assethub_menu)
    main_menu.addItem(menu_item, -1)
    
    # Update UI
    rt.menuMan.updateMenuBar()
```

## Тестирование

### Модульные тесты

AssetHub использует pytest для модульного тестирования. Тесты находятся в директории `assethub/tests/`.

Запуск тестов:

```bash
# Запуск всех тестов
pytest assethub/tests/

# Запуск конкретного теста
pytest assethub/tests/test_core.py

# Запуск с покрытием кода
pytest --cov=assethub assethub/tests/
```

Структура тестов:

- `test_core.py` - тесты для модуля core
- `test_catalog.py` - тесты для модуля catalog
- `test_integration.py` - тесты для модуля integration
- `test_ui.py` - тесты для модуля ui
- `test_plugin.py` - тесты для модуля plugin

Пример теста:

```python
# assethub/tests/test_core.py
import os
import tempfile
import pytest
from assethub.core.config import Config
from assethub.core.models import Asset, Tag, Category, init_db, get_session

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    
    # Override database path
    original_db_path = os.environ.get("ASSETHUB_DB_PATH")
    os.environ["ASSETHUB_DB_PATH"] = path
    
    # Initialize database
    engine = init_db()
    
    yield path
    
    # Cleanup
    if original_db_path:
        os.environ["ASSETHUB_DB_PATH"] = original_db_path
    else:
        del os.environ["ASSETHUB_DB_PATH"]
    
    os.unlink(path)

def test_asset_creation(temp_db):
    """Test creating an asset in the database."""
    session = get_session()
    
    # Create a new asset
    asset = Asset(
        name="Test Asset",
        description="Test description",
        file_path="/path/to/test.obj",
        file_size=1024,
        file_type="model",
        file_format="obj"
    )
    
    session.add(asset)
    session.commit()
    
    # Retrieve the asset
    retrieved = session.query(Asset).filter(Asset.name == "Test Asset").first()
    
    assert retrieved is not None
    assert retrieved.name == "Test Asset"
    assert retrieved.file_type == "model"
    assert retrieved.file_format == "obj"
```

### Интеграционные тесты

Интеграционные тесты проверяют взаимодействие между различными модулями AssetHub. Они находятся в директории `assethub/tests/integration/`.

Пример интеграционного теста:

```python
# assethub/tests/integration/test_catalog_integration.py
import os
import tempfile
import shutil
import pytest
from assethub.core.models import init_db, get_session
from assethub.catalog.scanner import AssetScanner
from assethub.catalog.indexer import AssetIndexer
from assethub.catalog.search import AssetSearch

@pytest.fixture
def test_environment():
    """Set up a test environment with sample files."""
    # Create temporary directories
    temp_dir = tempfile.mkdtemp()
    assets_dir = os.path.join(temp_dir, "assets")
    index_dir = os.path.join(temp_dir, "index")
    db_path = os.path.join(temp_dir, "test.db")
    
    os.makedirs(assets_dir)
    os.makedirs(index_dir)
    
    # Create sample files
    with open(os.path.join(assets_dir, "test_model.obj"), "w") as f:
        f.write("# Test OBJ file\nv 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n")
    
    with open(os.path.join(assets_dir, "test_texture.jpg"), "wb") as f:
        f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C")
    
    # Override environment variables
    original_env = {}
    for var in ["ASSETHUB_DB_PATH", "ASSETHUB_INDEX_PATH", "ASSETHUB_STORAGE_PATH"]:
        original_env[var] = os.environ.get(var)
    
    os.environ["ASSETHUB_DB_PATH"] = db_path
    os.environ["ASSETHUB_INDEX_PATH"] = index_dir
    os.environ["ASSETHUB_STORAGE_PATH"] = assets_dir
    
    # Initialize database
    init_db()
    
    yield {
        "temp_dir": temp_dir,
        "assets_dir": assets_dir,
        "index_dir": index_dir,
        "db_path": db_path
    }
    
    # Cleanup
    for var, value in original_env.items():
        if value:
            os.environ[var] = value
        else:
            del os.environ[var]
    
    shutil.rmtree(temp_dir)

def test_scan_index_search(test_environment):
    """Test the full scan-index-search workflow."""
    assets_dir = test_environment["assets_dir"]
    
    # Scan assets
    scanner = AssetScanner()
    assets = scanner.scan_directory(assets_dir)
    
    assert len(assets) == 2
    assert any(asset.file_type == "model" for asset in assets)
    assert any(asset.file_type == "texture" for asset in assets)
    
    # Index assets
    indexer = AssetIndexer()
    indexer.create_index()
    indexer.index_assets(assets)
    
    # Search for assets
    search_engine = AssetSearch()
    
    # Search for models
    model_results = search_engine.search("model", filters={"file_type": "model"})
    assert len(model_results) == 1
    assert model_results[0].file_format == "obj"
    
    # Search for textures
    texture_results = search_engine.search("texture", filters={"file_type": "texture"})
    assert len(texture_results) == 1
    assert texture_results[0].file_format == "jpg"
```

### UI-тесты

UI-тесты проверяют функциональность пользовательского интерфейса. Они используют QtTest для симуляции пользовательских действий.

Пример UI-теста:

```python
# assethub/tests/ui/test_main_window.py
import pytest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from assethub.ui.app import AssetHubMainWindow

@pytest.fixture
def main_window(qtbot):
    """Create a main window for testing."""
    window = AssetHubMainWindow()
    qtbot.addWidget(window)
    return window

def test_search_functionality(main_window, qtbot):
    """Test the search functionality of the main window."""
    # Find the search input
    search_input = main_window.search_widget.search_input
    
    # Type a search query
    QTest.keyClicks(search_input, "test")
    
    # Press Enter to search
    QTest.keyPress(search_input, Qt.Key_Return)
    
    # Check that the search was performed
    assert main_window.results_widget.count() >= 0  # May be 0 if no results

def test_filter_by_type(main_window, qtbot):
    """Test filtering by file type."""
    # Find the type filter combo box
    type_combo = main_window.search_widget.type_combo
    
    # Select "Model" type
    type_combo.setCurrentText("Model")
    
    # Check that the filter was applied
    assert main_window.current_filters["file_type"] == "model"
```

## CI/CD

### Настройка GitHub Actions

AssetHub использует GitHub Actions для непрерывной интеграции и доставки. Конфигурация находится в файле `.github/workflows/ci.yml`.

Пример конфигурации CI/CD:

```yaml
name: AssetHub CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
        pip install -e .
    - name: Test with pytest
      run: |
        pytest --cov=assethub assethub/tests/

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: |
        python -m build
    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: dist
        path: dist/

  release:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main' && startsWith(github.event.head_commit.message, 'Release')

    steps:
    - uses: actions/checkout@v2
    - name: Download artifacts
      uses: actions/download-artifact@v2
      with:
        name: dist
        path: dist/
    - name: Create Release
      id: create_release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.event.head_commit.message }}
        release_name: ${{ github.event.head_commit.message }}
        draft: false
        prerelease: false
    - name: Upload Release Asset
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ steps.create_release.outputs.upload_url }}
        asset_path: ./dist/assethub-*.tar.gz
        asset_name: assethub.tar.gz
        asset_content_type: application/gzip
```

### Автоматическое тестирование

GitHub Actions автоматически запускает тесты при каждом push и pull request. Это обеспечивает непрерывную проверку качества кода.

Процесс тестирования включает:

1. Запуск модульных тестов
2. Проверка покрытия кода
3. Линтинг кода (проверка стиля)

### Сборка и публикация

При push в ветку main GitHub Actions автоматически собирает пакет и загружает его как артефакт.

Если сообщение коммита начинается с "Release", GitHub Actions также:

1. Создает новый релиз на GitHub
2. Загружает собранный пакет как ассет релиза

## Стиль кода и лучшие практики

### Соглашения о стиле кода

AssetHub следует стандарту PEP 8 для стиля кода Python с некоторыми дополнениями:

1. **Длина строки**: максимум 88 символов (совместимо с Black)
2. **Отступы**: 4 пробела (без табуляции)
3. **Именование**:
   - Классы: CamelCase
   - Функции и методы: snake_case
   - Переменные: snake_case
   - Константы: UPPER_CASE
4. **Документация**: Google style docstrings
5. **Импорты**: группировка импортов (стандартная библиотека, сторонние пакеты, локальные модули)

Пример стиля кода:

```python
"""
Module for asset scanning and metadata extraction.

This module provides functionality for scanning directories and files,
extracting metadata from various file formats, and adding assets to the database.
"""
import os
import logging
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from assethub.core.models import Asset, get_session
from assethub.core.config import config

# Constants
SUPPORTED_MODEL_FORMATS = ["obj", "fbx", "3ds", "max", "blend", "dae", "stl", "ply"]
SUPPORTED_TEXTURE_FORMATS = ["jpg", "jpeg", "png", "tif", "tiff", "bmp", "tga", "hdr", "exr"]
SUPPORTED_MATERIAL_FORMATS = ["mtl", "mat", "xml", "json"]

# Setup logging
logger = logging.getLogger(__name__)


class AssetScanner:
    """Scanner for asset files.
    
    This class provides functionality for scanning directories and files,
    extracting metadata, and adding assets to the database.
    
    Attributes:
        session: SQLAlchemy session for database operations.
    """
    
    def __init__(self):
        """Initialize the asset scanner."""
        self.session = get_session()
        
    def scan_directory(self, directory: str, recursive: bool = True) -> List[Asset]:
        """Scan a directory for assets.
        
        Args:
            directory: Path to the directory to scan.
            recursive: Whether to scan subdirectories recursively.
            
        Returns:
            List of Asset objects created from the scanned files.
            
        Raises:
            FileNotFoundError: If the directory does not exist.
        """
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
            
        logger.info(f"Scanning directory: {directory}")
        
        assets = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                asset = self.scan_file(file_path)
                if asset:
                    assets.append(asset)
                    
            if not recursive:
                break
                
        logger.info(f"Found {len(assets)} assets in {directory}")
        return assets
```

### Документирование кода

Весь код AssetHub должен быть документирован с использованием Google style docstrings:

1. **Модули**: общее описание модуля в начале файла
2. **Классы**: описание класса, атрибутов и методов
3. **Функции и методы**: описание, аргументы, возвращаемые значения, исключения
4. **Сложные блоки кода**: комментарии для объяснения логики

Пример документации:

```python
def search(self, query_string: str, fields: Optional[List[str]] = None,
           filters: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Asset]:
    """Search for assets matching the query.
    
    This method searches the index for assets matching the given query string
    and filters. It returns a list of Asset objects sorted by relevance.
    
    Args:
        query_string: The search query string.
        fields: List of fields to search in. If None, searches in all fields.
        filters: Dictionary of field-value pairs to filter results.
        limit: Maximum number of results to return.
        
    Returns:
        List of Asset objects matching the query.
        
    Raises:
        ValueError: If the search index does not exist.
        
    Examples:
        >>> search_engine = AssetSearch()
        >>> results = search_engine.search("wooden chair", 
        ...                               filters={"file_type": "model"})
    """
```

### Обработка ошибок

AssetHub использует следующие принципы обработки ошибок:

1. **Явное определение исключений**: использование специфических исключений вместо общих
2. **Документирование исключений**: указание возможных исключений в docstrings
3. **Логирование ошибок**: запись информации об ошибках в лог
4. **Пользовательские сообщения**: понятные сообщения об ошибках для пользователей

Пример обработки ошибок:

```python
def connect(self):
    """Connect to the external library.
    
    Returns:
        bool: True if connection successful, False otherwise.
        
    Raises:
        ValueError: If API key is not provided.
        ConnectionError: If connection to API fails.
    """
    if not self.api_key:
        logger.error("API key not provided")
        raise ValueError(f"{self.provider_name} API key not provided")
        
    try:
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        # Test connection
        response = self.session.get(f"{self.api_url}/test")
        response.raise_for_status()
        
        logger.info(f"Connected to {self.provider_name} API")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to {self.provider_name} API: {str(e)}")
        raise ConnectionError(f"Failed to connect to {self.provider_name} API: {str(e)}")
```

## Руководство по вкладу в проект

### Процесс разработки

AssetHub использует Git Flow для управления разработкой:

1. **main**: стабильная ветка с релизами
2. **develop**: основная ветка разработки
3. **feature/\***: ветки для новых функций
4. **bugfix/\***: ветки для исправления ошибок
5. **release/\***: ветки для подготовки релизов

Процесс разработки:

1. Создайте форк репозитория
2. Клонируйте форк на локальную машину
3. Создайте ветку для вашей задачи:
   ```bash
   git checkout -b feature/my-feature
   ```
4. Внесите изменения и закоммитьте их:
   ```bash
   git add .
   git commit -m "Add my feature"
   ```
5. Отправьте изменения в ваш форк:
   ```bash
   git push origin feature/my-feature
   ```
6. Создайте Pull Request в основной репозиторий

### Pull Requests

Pull Requests должны соответствовать следующим требованиям:

1. **Название**: краткое описание изменений
2. **Описание**: подробное описание изменений, причин и результатов
3. **Связанные задачи**: ссылки на связанные задачи или проблемы
4. **Тесты**: новые или обновленные тесты для изменений
5. **Документация**: обновленная документация, если необходимо

Шаблон Pull Request:

```markdown
## Описание

Краткое описание изменений.

## Связанные задачи

- #123: Название задачи

## Изменения

- Добавлена функция X
- Исправлена ошибка Y
- Улучшена производительность Z

## Тесты

- Добавлены тесты для функции X
- Обновлены тесты для функции Y

## Документация

- Обновлена документация для функции X
- Добавлены примеры использования

## Скриншоты (если применимо)

![Скриншот](url-to-screenshot)

## Чек-лист

- [ ] Код соответствует стилю проекта
- [ ] Добавлены или обновлены тесты
- [ ] Обновлена документация
- [ ] Код проходит все тесты
```

### Code Review

Процесс Code Review:

1. **Автоматические проверки**: CI/CD должен пройти успешно
2. **Ручная проверка**: как минимум один разработчик должен проверить код
3. **Обсуждение**: обсуждение изменений и предложения по улучшению
4. **Итерации**: внесение изменений по результатам обсуждения
5. **Утверждение**: утверждение изменений и слияние с основной веткой

Критерии проверки:

1. **Функциональность**: код должен выполнять заявленную функцию
2. **Качество**: код должен быть чистым, понятным и поддерживаемым
3. **Тесты**: должны быть добавлены или обновлены тесты
4. **Документация**: должна быть обновлена документация
5. **Производительность**: код должен быть эффективным
6. **Безопасность**: код не должен содержать уязвимостей

## Часто задаваемые вопросы

### Общие вопросы

**В: Как добавить поддержку нового формата файлов?**

О: Для добавления поддержки нового формата файлов:

1. Обновите списки поддерживаемых форматов в `assethub/catalog/scanner.py`
2. Добавьте функцию для извлечения метаданных из нового формата
3. Обновите метод `_extract_metadata` для обработки нового формата
4. Добавьте тесты для нового формата

**В: Как добавить новый провайдер внешней библиотеки?**

О: Для добавления нового провайдера:

1. Создайте новый файл в `assethub/integration/providers/`
2. Реализуйте класс провайдера, наследующийся от `BaseProvider`
3. Зарегистрируйте провайдер в `assethub/integration/__init__.py`
4. Добавьте настройки провайдера в конфигурационный файл
5. Обновите документацию

**В: Как настроить API-ключи для внешних сервисов?**

О: Для настройки API-ключей:

1. Получите API-ключи от соответствующих сервисов
2. Добавьте их в конфигурационный файл `~/.assethub/config.json`
3. Или используйте метод `config.set()` в коде:
   ```python
   from assethub.core.config import config
   config.set("integration", "turbosquid", "api_key", "YOUR_API_KEY")
   config.save_config()
   ```

### Технические вопросы

**В: Как добавить новую зависимость в проект?**

О: Для добавления новой зависимости:

1. Добавьте зависимость в `pyproject.toml`:
   ```toml
   [tool.poetry.dependencies]
   new-package = "^1.0.0"
   ```
2. Обновите зависимости:
   ```bash
   poetry update
   ```
3. Обновите документацию, если необходимо

**В: Как запустить тесты с покрытием кода?**

О: Для запуска тестов с покрытием кода:

```bash
pytest --cov=assethub assethub/tests/
```

**В: Как создать релиз?**

О: Для создания релиза:

1. Обновите версию в `pyproject.toml`
2. Обновите CHANGELOG.md
3. Создайте коммит с сообщением, начинающимся с "Release":
   ```bash
   git commit -m "Release v1.0.0"
   ```
4. Отправьте изменения в репозиторий:
   ```bash
   git push origin main
   ```
5. CI/CD автоматически создаст релиз на GitHub

## Приложения

### Глоссарий

- **Asset** - ресурс (3D-модель, текстура, материал)
- **Provider** - провайдер внешней библиотеки ресурсов
- **Scanner** - компонент для сканирования и извлечения метаданных из файлов
- **Indexer** - компонент для индексации ресурсов для быстрого поиска
- **Search Engine** - компонент для поиска ресурсов по индексу

### Ссылки на ресурсы

- [Python Documentation](https://docs.python.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Whoosh Documentation](https://whoosh.readthedocs.io/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [3ds Max Python API Documentation](https://help.autodesk.com/view/3DSMAX/2020/ENU/?guid=GUID-779A38D6-2A375-4F9B-B9A4-33221F1051A2)
