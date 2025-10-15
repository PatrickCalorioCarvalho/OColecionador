FROM tensorflow/tensorflow:2.6.0-gpu

# Remove repositório quebrado da NVIDIA
RUN rm -f /etc/apt/sources.list.d/cuda*.list

# Atualiza e instala libpq-dev
RUN apt-get update && apt-get install -y libpq-dev

COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
CMD ["python", "main.py"]
