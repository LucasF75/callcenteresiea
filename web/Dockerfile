FROM python:3.11-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copier le code de l'app
COPY .. /app
WORKDIR /app

# Installer les dépendances Python
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

# Exposer le port Flask par défaut
EXPOSE 5000