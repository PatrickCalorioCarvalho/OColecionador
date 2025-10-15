FROM tensorflow/tensorflow:2.4.1-gpu

RUN apt-get update && apt-get install -y libpq-dev

COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
CMD ["python", "main.py"]