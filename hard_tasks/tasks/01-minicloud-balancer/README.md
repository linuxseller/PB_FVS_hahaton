# 01. MiniCloud Balancer


## Суть

Нужно написать HTTP-сервис-балансировщик. Judge будет отправлять ему запросы, а сервис должен перенаправлять их на worker-сервисы.

Worker-сервисы нестабильны: часть отвечает медленно, часть иногда падает, часть возвращает ошибки.

## Контракт решения

Ваш контейнер должен слушать порт `8080`.

### Healthcheck

```http
GET /health
```

Ответ:

```json
{"status":"ok"}
```

### Конфигурация workers

```http
POST /config
```

Тело:

```json
{
  "workers": [
    {"id": "w1", "url": "http://host:port"},
    {"id": "w2", "url": "http://host:port"}
  ]
}
```

### Обработка запроса

```http
POST /handle
```

Тело:

```json
{
  "request_id": "r1",
  "payload": "hello",
  "timeout_ms": 800
}
```

Ваш сервис должен вызвать одного из workers:

```http
POST {worker_url}/work
```

и вернуть:

```json
{
  "request_id": "r1",
  "status": "ok",
  "worker": "w1",
  "result": "..."
}
```

Если все workers недоступны, можно вернуть:

```json
{
  "request_id": "r1",
  "status": "failed",
  "worker": null,
  "result": null
}
```

## Что будет в скрытых тестах

- worker с высоким latency;
- worker, который периодически падает;
- worker со скрытым rate limit;
- волнообразная нагрузка;
- проверка retry;
- проверка, что мёртвый worker не используется постоянно.
