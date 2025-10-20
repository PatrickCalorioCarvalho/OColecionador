FROM tensorflow/tensorflow:2.6.0-gpu

RUN rm -f /etc/apt/sources.list.d/cuda*.list

RUN apt-get update && apt-get install -y libpq-dev

RUN ln -sf $(which python3) /usr/bin/python && \
    ln -sf $(which pip3) /usr/bin/pip && \
    python --version && pip --version

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY worker.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
