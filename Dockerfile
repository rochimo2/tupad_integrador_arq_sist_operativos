FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Entrypoint: comando que se ejecuta en el contenedor
CMD ["python", "run.py"]