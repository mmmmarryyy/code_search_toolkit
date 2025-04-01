# API Documentation v1

## 1. Создание задачи поиска

**Endpoint**  
`POST /api/search`

**Content-Type**  
`multipart/form-data`

---

### GitHub Mode

#### Обязательные параметры

| Поле          | Тип    | Описание                                |
|---------------|--------|-----------------------------------------|
| `mode`        | string | Должно быть `"github"`                  |
| `repository`  | string | URL GitHub репозитория                  |
| `branch`      | string | Название ветки                          |
| `snippet`     | string | Исходный код для поиска                 |
| `methods`     | string | JSON-массив методов                     |
| `combination` | string | JSON-конфиг комбинации                  |
| `language`    | string | Язык исходного кода (например, `"java"`)|

#### Пример запроса

```bash
curl -X POST "http://api.example.com/api/search" \
  -H "Content-Type: multipart/form-data" \
  -F "mode=github" \
  -F "repository=https://github.com/user/repo" \
  -F "branch=main" \
  -F "snippet=def calculate(a, b):\n    return a + b" \
  -F "methods=[{\"name\":\"NIL\",\"params\":{\"threshold\":0.75}}]" \
  -F "combination={\"strategy\":\"weighted_union\",\"weights\":{\"NIL\":0.6,\"CCAligner\":0.4}}" \
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
  -F "methods=[{\"name\":\"NIL\",\"params\":{\"threshold\":0.75}}]" \
  -F "combination={\"strategy\":\"union\"}" \
  -F "language=python" \
  -F "file=@project.zip"
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
      "name": "NIL",
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
