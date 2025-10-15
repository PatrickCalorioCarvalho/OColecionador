FROM tensorflow/tensorflow:2.6.0-gpu

RUN rm -f /etc/apt/sources.list.d/cuda*.list \
 && apt-get update && apt-get install -y libpq-dev

RUN ln -sf /usr/bin/python3.8 /usr/bin/python \
 && ln -sf /usr/bin/pip3 /usr/bin/pip

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

COPY main.py .
CMD ["python", "main.py"]
