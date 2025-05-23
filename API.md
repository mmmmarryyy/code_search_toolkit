# API Documentation v1

## 1. Создание задачи поиска

**Endpoint**  
`POST /api/search`

**Content-Type**  
`multipart/form-data`

---

### GitHub Mode

#### Обязательные параметры

| Поле          | Тип     | Описание                                                                         |
|---------------|---------|----------------------------------------------------------------------------------|
| `mode`        | string  | Должно быть `"github"`                                                           |
| `repository`  | string  | URL GitHub репозитория                                                           |
| `branch`      | string  | Название ветки (по умолчанию `"main"`)                                           |
| `snippet`     | string  | Исходный код (фрагмент) для поиска                                               |
| `methods`     | string  | JSON-массив методов                                                              |
| `combination` | string  | JSON-конфигурация стратегии объединения результатов                              |
| `language`    | string  | Язык исходного кода (например, `"java"`, `"python"`, `"cpp"`, `"c"`, `"csharp"`) |

#### combination: пример

1. Простой union

Объединяет все пары клонов из всех методов без каких-либо фильтров:

```json
{ "strategy": "union" }
```

2. threshold_union (пороговое объединение)

Включает только те пары, которые встретились в минимум N разных методах:

```json
{
  "strategy": "threshold_union",
  "min_methods": 2
}
```

3. weighted_union (взвешенное объединение)

Каждой паре начисляется сумма весов методов, в которых она встретилась. Оставляем пары, чей суммарный вес $\geq$ threshold.

```json
{
  "strategy": "weighted_union",
  "weights": {
    "NIL-fork": 0.6,
    "CCAligner": 0.3,
    "CCSTokener": 0.1
  },
  "threshold": 0.5
}
```

threshold — порог (0.0 … 1.0).

4. intersection_union (пересечение)

По умолчанию (если strategy не задана) берётся пересечение результатов всех указанных методов:

```json
{ "strategy": "intersection_union" }
```

#### Пример запроса

```bash
curl -X POST "http://api.example.com/api/search" \
  -H "Content-Type: multipart/form-data" \
  -F "mode=github" \
  -F "repository=https://github.com/user/repo" \
  -F "branch=main" \
  -F "snippet=def calculate(a, b):\n    return a + b" \
  -F 'methods=[{"name":"NIL-fork","params":{"threshold":0.75}}]' \
  -F 'combination={"strategy":"threshold_union","min_methods":2}' \
  -F "language=python"
```

---

### Local Mode

#### Обязательные параметры

| Поле         | Тип    | Описание                      |
|--------------|--------|-------------------------------|
| `mode`       | string | Должно быть `"local"`         |
| `file`       | file   | ZIP-архив проекта             |
| `snippet`    | string | Исходный код для поиска       |
| `methods`    | string | JSON-массив методов           |
| `combination`| string | JSON-конфиг комбинации        |
| `language`   | string | Язык исходного кода           |

#### Пример запроса
```bash
curl -X POST "http://api.example.com/api/search" \
  -H "Content-Type: multipart/form-data" \
  -F "mode=local" \
  -F "snippet=def calculate(a, b):\n    return a + b" \
  -F 'methods=[{"name":"NIL-fork","params":{"threshold":0.75}}]' \
  -F 'combination={"strategy":"union"}' \
  -F "language=python" \
  -F "file=@path/to/project.zip"
```

---

**Ответ для обоих режимов**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status_url": "/api/search/550e8400-e29b-41d4-a716-446655440000/status",
  "results_url": "/api/search/550e8400-e29b-41d4-a716-446655440000/results"
}
```

---

## 2. Получение статуса задачи

**Endpoint**  
`GET /api/search/{task_id}/status`

**Пример ответа**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "pending|processing|completed|error|deleted",
  "started_at": "2023-12-20T10:00:00Z",
  "processed_snippet": "def calculate(a, b):\n    return a + b"
}
```

### Status

- pending — ожидает начала обработки
- processing — сейчас обрабатывается
- completed — успешно завершена, результаты готовы
- error — обработка завершилась с ошибкой. При этом могут быть дополнительные поля:
- deleted — удалена из очереди за истекшим сроком хранения (expiration)

---

## 3. Получение результатов

**Endpoint**  
`GET /api/search/{task_id}/results`

**Пример ответа**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "results": [
    ...
  ],
  "metrics": {
    "total_files_processed": 142,
    "execution_time": 12.7
  }
}
```

Если статус задачи не completed, возвращается `HTTP 400 Bad Request` с сообщением, что задача ещё не готова.

---

## 4. Получение информации о методах

**Endpoint**  
`GET /api/methods`

**Пример ответа**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "available_methods": [
    {
      "name": "NIL-fork",
      "description": "Large-variance clone detection",
      "params": {
        "threshold": {
          "type": "float",
          "default": 0.7,
          "min": 0.1,
          "max": 1.0
        }
      }
    },
    {
      "name": "CCAligner",
      "description": "Token-based clone detection",
      "params": {
        "min_tokens": {
          "type": "integer",
          "default": 50,
          "min": 10,
          "max": 1000
        }
      }
    }
  ]
}
```

--- 

## Примечания

1. Сложные параметры (`methods`, `combination`) должны:
  - Быть сериализованы в JSON
  - Соответствовать схеме из `/api/methods`

2. Время обработки зависит от:
  - Размера репозитория (GitHub)
  - Содержимого архива (Local)
  - Выбранных методов

3. Время хранения и удаление
  - После успешного завершения задача и её результаты хранятся в течение 24 часов.
  - Как только срок хранения истекает, статус меняется на deleted, и все файлы (распакованные исходники и результаты) удаляются из файловой системы.
