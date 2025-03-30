# Code Search Toolkit

REST-сервис для точечного поиска фрагментов программного кода в GitHub-репозиториях на основе методов обнаружения дубликатов:
- CCSTokener
- NIL-fork
- CCAligner

## Некоторые компоненты системы

### Модифицированные реализации алгоритмов

1. **NIL-fork**  
Адаптированная для задачи code search версия NIL: `https://github.com/mmmmarryyy/NIL-fork.git`  
*Основные изменения:*
- Переориентация с обнаружения всех клонов на точечный поиск
- Оптимизация для работы с единичным фрагментом кода

2. **CCStokener-fork**  
Собственная реализация CCSTokener на основе оригинальной статьи: `https://github.com/mmmmarryyy/CCStokener-fork.git`

### Интеграция с существующими методами

1. **DockerizedCloneDetectionTools**  
Оригинальные реализации алгоритмов обнаружения клонов в Docker-контейнерах: `https://github.com/mmmmarryyy/DockerizedCloneDetectionTools`

## Описание

Сервис предоставляет API для:
- Создания задачи поиска по GitHub-репозиторию
- Получения статуса задачи и результатов
- Получения информации о доступных методах

Swagger-документация доступна по адресу: `/docs`

## Запуск

### Локально
1. Установите зависимости:
```
pip install -r requirements.txt
```
2. Соберите контейнеры для методов, которые вы хотите использовать
3. Запустите сервер:
```
python3 -m app.main
```

## Сборка Docker-контейнеров

В проекте лежат Dockerfile для CCAligner и CCSTokener, а также bash‑скрипты для их сборки и запуска:
- **CCAligner:**  
  - Сборка: `tools/build_CCAligner.sh`
  
- **CCSTokener:**  
  - Сборка: `tools/build_CCSTokener.sh`

- **NIL-fork:**  
  - Сборка: `tools/build_NIL_fork.sh`
