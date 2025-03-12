# Code Search Toolkit

REST-сервис для точечного поиска фрагментов программного кода в GitHub-репозиториях на основе методов обнаружения дубликатов

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
