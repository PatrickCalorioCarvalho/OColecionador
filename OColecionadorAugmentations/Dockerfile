FROM nvidia/cudagl:10.1-devel-ubuntu18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN rm -f /etc/apt/sources.list.d/cuda*.list \
    && rm -f /etc/apt/sources.list.d/nvidia-ml.list

RUN apt-get update && apt-get install -y tzdata \
 && ln -fs /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata

RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    wget \
    build-essential \
    libpq-dev \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    git \
    gpg \
    ca-certificates

RUN curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub | gpg --dearmor -o /usr/share/keyrings/cuda-keyring.gpg \
 && echo "deb [signed-by=/usr/share/keyrings/cuda-keyring.gpg] https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64 /" > /etc/apt/sources.list.d/cuda.list

WORKDIR /opt
RUN wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz \
 && tar -xvf Python-3.13.0.tgz \
 && cd Python-3.13.0 \
 && ./configure --enable-optimizations \
 && make -j$(nproc) \
 && make altinstall

RUN ln -s /usr/local/bin/python3.13 /usr/bin/python \
 && ln -s /usr/local/bin/pip3.13 /usr/bin/pip

RUN pip install --upgrade pip setuptools wheel

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
CMD ["python", "main.py"]
