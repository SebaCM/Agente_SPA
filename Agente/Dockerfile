# Usa una imagen oficial de Python como base
FROM python:3.12-slim

# Establece el directorio de trabajo en /app dentro del contenedor
WORKDIR /app

# Copia los archivos de requerimientos e instálalos
# Usar una copia separada del requirements.txt ayuda a la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto en el que correrá la API
EXPOSE 8000

# Define el comando para ejecutar la aplicación con Uvicorn
# La opción --host 0.0.0.0 permite que la API sea accesible desde fuera del contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
