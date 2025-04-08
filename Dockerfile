FROM python:3.9-slim

WORKDIR /app

RUN mkdir -p /app/logs

COPY requirements.txt .

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ .scripts/

# Запуск сервисов
CMD ["python", "scripts/main.py"]
