# AssetHub

AssetHub - универсальная платформа управления ресурсами для дизайнеров, работающих с 3ds Max. Платформа предоставляет централизованный доступ к локальным и облачным библиотекам 3D-моделей, текстур и материалов, значительно упрощая рабочий процесс визуализации проектов.

## Основные возможности

- **Каталогизация ресурсов**: Автоматическое сканирование и индексация локальных 3D-моделей, текстур и материалов
- **Интеллектуальный поиск**: Быстрый поиск ресурсов по имени, категории, типу и другим параметрам
- **Интеграция с внешними библиотеками**: Доступ к популярным онлайн-библиотекам 3D-моделей (Turbosquid, CGTrader)
- **Плагин для 3ds Max**: Прямая интеграция с 3ds Max для импорта моделей и текстур
- **Удобный интерфейс**: Интуитивно понятный пользовательский интерфейс для эффективной работы с ресурсами

## Установка

### Системные требования

- Windows 10 или новее
- Python 3.9-3.11
- 3ds Max 2020 или новее (для функций плагина)
- 4 ГБ оперативной памяти (рекомендуется 8 ГБ)
- 500 МБ свободного места на диске (не включая библиотеку ресурсов)

### Установка из исходного кода

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/assethub.git
   cd assethub
   ```

2. Установите зависимости:
   ```bash
   pip install -e .
   ```

3. Запустите приложение:
   ```bash
   python main.py
   ```

### Установка плагина для 3ds Max

1. Скопируйте файлы плагина в директорию скриптов 3ds Max:
   ```
   %APPDATA%\Autodesk\3ds Max 20XX\ENU\scripts\startup\
   ```

2. Перезапустите 3ds Max

3. Запустите плагин через меню MAXScript:
   ```
   MAXScript > Run Script > выберите max_integration.py
   ```

## Документация

Подробная документация доступна в директории `docs/`:

- [Руководство пользователя](docs/user_manual_ru.md) - подробное руководство по использованию AssetHub
- [Developer Guide](docs/developer_guide.md) - руководство для разработчиков, желающих расширить функциональность AssetHub

## Структура проекта

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

## Начало работы

1. Запустите AssetHub
2. Нажмите кнопку "Scan Directory" в боковой панели
3. Выберите директорию с вашими 3D-моделями, текстурами и материалами
4. Дождитесь завершения сканирования и индексации
5. Используйте поиск для нахождения нужных ресурсов
6. Импортируйте ресурсы в 3ds Max через плагин или напрямую

## Лицензия

AssetHub распространяется под лицензией MIT. См. файл LICENSE для подробностей.

## Контакты

По вопросам и поддержке обращайтесь к команде AssetHub по адресу [email@example.com](mailto:email@example.com)
