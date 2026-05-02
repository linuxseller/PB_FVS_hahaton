# 02. Distributed Cache Challenge


## Суть

Нужно написать кэширующий HTTP-сервис перед медленным backend.

Backend умеет хранить значения по ключам, но он медленный и нестабильный. Ваш сервис должен ускорять чтение и сохранять корректность.

## Контракт решения

Контейнер слушает порт `8080`.

### Healthcheck

```http
GET /health
```

### Конфигурация backend

```http
POST /config
```

```json
{
  "backend_url": "http://host:port",
  "ttl_ms": 1000,
  "max_items": 100
}
```

### Получить значение

```http
GET /value/{key}
```

Ответ:

```json
{
  "key": "a",
  "value": "123",
  "source": "cache"
}
```

`source` может быть `cache` или `backend`.

### Записать значение

```http
POST /value/{key}
```

```json
{"value":"new value"}
```

### Удалить значение

```http
DELETE /value/{key}
```

## Что будет в скрытых тестах

- много конкурентных чтений одного ключа;
- backend временно падает;
- проверка TTL;
- проверка invalidation после POST/DELETE;
- ограничение размера кэша.
