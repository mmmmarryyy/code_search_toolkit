# API v1

1. Создание задачи поиска

```
POST /api/search
Content-Type: application/json
```

Пример запроса для GitHub:
```
{
  "mode": "github",
  "repository": "https://github.com/user/repo",
  "branch": "main",
  "snippet": "def calculate(a, b):\n    return a + b",
  "methods": [
    {
      "name": "NIL",
      "params": {
        "threshold": 0.75,
        ...
      }
    },
    {
      "name": "CCAligner",
      "params": {
        "min_tokens": 50,
        ...
      }
    }
  ],
  "combination": {
    "strategy": "weighted_union",
    "weights": {
      "NIL": 0.6,
      "CCAligner": 0.4
    }
  }
}
```

Пример запроса для локального файла:
```
POST /api/search
Content-Type: multipart/form-data

{
  "mode": "local",
  "snippet": "def calculate(a, b):\n    return a + b",
  "methods": [...],
  "combination": {...}
}
file=@project.zip
```

Ответ:
```
201 Created
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status_url": "/api/search/550e8400-e29b-41d4-a716-446655440000/status",
  "results_url": "/api/search/550e8400-e29b-41d4-a716-446655440000/results"
}
```

2. Получение статуса задачи

```
GET /api/search/{task_id}/status
```

Ответ:
```
200 OK
{
  "status": "pending|processing|completed|failed",
  "started_at": "2023-12-20T10:00:00Z",
  "processed_snippet": ...,
  // TODO: add some progress status if possible 
}
```

3. Получение результатов
```
GET /api/search/{task_id}/results
```

Ответ (упрощенный):
```
200 OK
{
  "results": [
    ??? // TODO: think about format (maybe file)
  ],
  "metrics": {
    "total_files_processed": 142,
    "execution_time": 12.7
  }
}
```

4. Получение информации о методах

```
GET /api/methods
```

Ответ:
```
200 OK
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
        },
        ...
      }
    },
    ...
  ]
}
```