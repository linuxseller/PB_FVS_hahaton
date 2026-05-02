# Tools

## submit_solution.py

Скрипт для простой отправки решения без ручной упаковки ZIP.

Установка зависимости:

```bash
pip install requests
```

Запуск:

```bash
python submit_solution.py \
  --server http://SERVER_IP:8000 \
  --team team-sonic \
  --task 04-arena-scheduler \
  --path ./my-solution
```

Скрипт:

1. Проверит, что в папке есть `Dockerfile`.
2. Сам создаст ZIP.
3. Отправит ZIP на judge-сервер.
4. Покажет результат.
