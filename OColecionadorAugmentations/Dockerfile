FROM tensorflow/tensorflow:2.6.0-gpu

# Remove repositórios quebrados da NVIDIA
RUN rm -f /etc/apt/sources.list.d/cuda*.list

# Instala libpq-dev
RUN apt-get update && apt-get install -y libpq-dev

# Verifica e força o uso do Python 3.8
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1 \
 && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Confirma versão correta
RUN python --version && pip --version

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

COPY main.py .
CMD ["python", "main.py"]
