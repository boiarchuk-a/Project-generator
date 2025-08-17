FROM python:3.9-slim

WORKDIR /app

# скопировать зависимости и поставить
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# скопировать весь проект
COPY . .

# слушаем 80 порт
EXPOSE 80

# запускаем uvicorn
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]
