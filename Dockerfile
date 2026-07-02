# Image Python legere
FROM python:3.10-slim

# Confort / logs Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1

WORKDIR /app

# Dependances (couche mise en cache tant que requirements.txt ne change pas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code du projet
COPY . .

EXPOSE 8000

# Serveur de dev Channels/Daphne : sert HTTP + statiques + WebSocket
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
