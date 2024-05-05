# Utilisez une image de base Python 3.12
FROM python:3.12

# Définissez l'environnement de travail dans le conteneur
WORKDIR /app

# Copiez les fichiers de dépendances dans le conteneur
COPY requirements.txt .

# Installez les dépendances
RUN pip install -r requirements.txt

# Copiez le reste du code de l'application dans le conteneur
COPY . .

# Copiez le script entrypoint.sh et rendez-le exécutable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


# Exposez le port sur lequel votre application s'exécute (par exemple, 8000 si votre application Django s'exécute sur ce port)
EXPOSE 8000

# Définissez la commande pour exécuter votre application
ENTRYPOINT ["/entrypoint.sh"]