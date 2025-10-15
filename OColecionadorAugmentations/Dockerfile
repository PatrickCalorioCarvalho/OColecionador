FROM nvidia/cuda:11.4.3-cudnn8-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y tzdata \
 && ln -fs /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata

RUN apt-get install -y \
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
