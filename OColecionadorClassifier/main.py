from fastapi import FastAPI, File, UploadFile
from minio import Minio
import tensorflow as tf
from tensorflow.keras import backend as K
from PIL import Image
import numpy as np
import io
import os
import json
import gc
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

app = FastAPI()

sentry_logging = LoggingIntegration(
    level=logging.INFO,       
    event_level=logging.ERROR
)

sentry_sdk.init(
    "http://8fae73ef8af543b8898e7883f9877a97@glitchtip:8000/4",
    integrations=[sentry_logging],
    traces_sample_rate=1.0
)

logging.basicConfig(level=logging.INFO)

gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        logging.warning(f"Erro ao configurar GPU: {e}")

BUCKET_MODELS = "ocolecionadorbucket-models"

minio_client = Minio(
    "minio:9000",
    access_key="OColecionadorUser",
    secret_key="OColecionador@2025",
    secure=False
)

def load_latest_model_and_classes():
    objects = list(minio_client.list_objects(BUCKET_MODELS, recursive=True))
    keras_files = [obj for obj in objects if obj.object_name.endswith(".keras")]
    if not keras_files:
        raise Exception("Nenhum modelo .keras encontrado no MinIO.")
    latest = sorted(keras_files, key=lambda x: x.last_modified, reverse=True)[0]
    model_path = f"/tmp/{latest.object_name}"
    minio_client.fget_object(BUCKET_MODELS, latest.object_name, model_path)
    model = tf.keras.models.load_model(model_path)
    json_name = latest.object_name.replace(".keras", ".json")
    json_path = f"/tmp/{json_name}"
    minio_client.fget_object(BUCKET_MODELS, json_name, json_path)
    with open(json_path, "r") as f:
        class_indices = json.load(f)
    index_to_class = {v: k for k, v in class_indices.items()}

    return model, index_to_class

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize((224, 224))
    array = np.array(image) / 255.0
    return np.expand_dims(array, axis=0)

@app.post("/api/classify")
async def classify(file: UploadFile = File(...)):
    image_bytes = await file.read()
    input_array = preprocess_image(image_bytes)
    model, index_to_class = load_latest_model_and_classes()
    prediction = model.predict(input_array)
    class_index = int(np.argmax(prediction))
    confidence = float(np.max(prediction))
    class_name = index_to_class.get(class_index, str(class_index))
    del model
    K.clear_session()
    gc.collect()
    return {"classe": class_name, "confianca": round(confidence, 4)}
