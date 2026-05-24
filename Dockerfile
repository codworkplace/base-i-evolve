FROM python:3.14-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY ./app ./app
COPY ./data ./data

# Открываем порты
EXPOSE 8000
EXPOSE 8501

# Запускаем сервисы
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run app/ui.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"]
