FROM tensorflow/tensorflow:2.6.0-gpu

# Remove repositórios quebrados da NVIDIA
RUN rm -f /etc/apt/sources.list.d/cuda*.list

# Instala libpq-dev
RUN apt-get update && apt-get install -y libpq-dev

# Corrige o alias para usar Python 3.8 e pip3
RUN ln -sf $(which python3) /usr/bin/python \
 && ln -sf $(which pip3) /usr/bin/pip

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

COPY main.py .
CMD ["python", "main.py"]
