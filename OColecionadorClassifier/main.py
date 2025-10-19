from fastapi import FastAPI, File, UploadFile
from minio import Minio
import tensorflow as tf
from PIL import Image
import numpy as np
import io
import os

app = FastAPI()

BUCKET_MODELS = "ocolecionadorbucket-models"

minio_client = Minio(
    "minio:9000",
    access_key="OColecionadorUser",
    secret_key="OColecionador@2025",
    secure=False
)

def load_latest_model():
    objects = list(minio_client.list_objects(BUCKET_MODELS, recursive=True))
    if not objects:
        raise Exception("Nenhum modelo encontrado no MinIO.")
    latest = sorted(objects, key=lambda x: x.last_modified, reverse=True)[0]
    model_path = f"/tmp/{latest.object_name}"
    minio_client.fget_object(BUCKET_MODELS, latest.object_name, model_path)
    model = tf.keras.models.load_model(model_path)
    return model

model = load_latest_model()

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize((224, 224))
    array = np.array(image) / 255.0
    return np.expand_dims(array, axis=0)

@app.post("/api/analisar-imagem")
async def analisar_imagem(file: UploadFile = File(...)):
    image_bytes = await file.read()
    input_array = preprocess_image(image_bytes)
    prediction = model.predict(input_array)
    class_index = int(np.argmax(prediction))
    confidence = float(np.max(prediction))
    class_name = str(class_index)
    return {"classe": class_name, "confianca": round(confidence, 4)}
