FROM tensorflow/tensorflow:2.6.0-gpu

# Remove repositórios quebrados da NVIDIA
RUN rm -f /etc/apt/sources.list.d/cuda*.list

# Instala libpq-dev
RUN apt-get update && apt-get install -y libpq-dev

# Força o uso do Python 3.8 e pip3
RUN ln -sf $(which python3) /usr/bin/python && \
    ln -sf $(which pip3) /usr/bin/pip && \
    python --version && pip --version

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir -r requirements.txt

COPY main.py .
CMD ["python", "main.py"]
