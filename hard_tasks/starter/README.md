# Starter templates

В каждой папке есть минимальный Python-шаблон, который запускается на порту 8080.

Это не финальное решение, а точка старта.

Локальная проверка:

```bash
cd starter/04-arena-scheduler/python
docker build -t arena-starter .
docker run --rm -p 8080:8080 arena-starter
```
