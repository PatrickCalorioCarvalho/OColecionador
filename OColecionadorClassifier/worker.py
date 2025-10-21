import sys
import json
import tensorflow as tf
import faiss
from PIL import Image
import numpy as np
import io
from minio import Minio
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,       
    event_level=logging.ERROR
)

sentry_sdk.init(
    "http://bb5ce3de2c2344fb92e3928b86505a71@glitchtip:8000/5",
    integrations=[sentry_logging],
    traces_sample_rate=1.0
)

logging.basicConfig(level=logging.INFO)

BUCKET_MODELS = "ocolecionadorbucket-models"
BUCKET_ORIGINAIS = "ocolecionadorbucket"

minio_client = Minio(
    "minio:9000",
    access_key="OColecionadorUser",
    secret_key="OColecionador@2025",
    secure=False
)

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize((224, 224))
    array = np.array(image) / 255.0
    return np.expand_dims(array, axis=0)

def load_latest_model_and_index():
    objects = list(minio_client.list_objects(BUCKET_MODELS, recursive=True))

    def latest_file(objects, prefix, suffix):
        files = [obj for obj in objects if obj.object_name.startswith(prefix) and obj.object_name.endswith(suffix)]
        if not files:
            raise Exception(f"Arquivo não encontrado: {prefix}*{suffix}")
        return sorted(files, key=lambda x: x.last_modified, reverse=True)[0]

    keras_obj = latest_file(objects, "classifier_", ".keras")
    json_obj = latest_file(objects, "class_indices_", ".json")
    index_obj = latest_file(objects, "index_original_", ".faiss")
    labels_obj = latest_file(objects, "labels_original_", ".npy")

    model_path = f"/tmp/{keras_obj.object_name}"
    json_path = f"/tmp/{json_obj.object_name}"
    index_path = f"/tmp/{index_obj.object_name}"
    labels_path = f"/tmp/{labels_obj.object_name}"

    minio_client.fget_object(BUCKET_MODELS, keras_obj.object_name, model_path)
    minio_client.fget_object(BUCKET_MODELS, json_obj.object_name, json_path)
    minio_client.fget_object(BUCKET_MODELS, index_obj.object_name, index_path)
    minio_client.fget_object(BUCKET_MODELS, labels_obj.object_name, labels_path)

    model = tf.keras.models.load_model(model_path)
    with open(json_path, "r") as f:
        class_indices = json.load(f)
    index_to_class = {v: k for k, v in class_indices.items()}
    index = faiss.read_index(index_path)
    labels = np.load(labels_path, allow_pickle=True)

    return model, index_to_class, index, labels

def main():
    image_bytes = sys.stdin.buffer.read()
    input_array = preprocess_image(image_bytes)

    model, index_to_class, index, labels = load_latest_model_and_index()

    prediction = model.predict(input_array)
    class_index = int(np.argmax(prediction))
    confidence = float(np.max(prediction))
    class_name = index_to_class.get(class_index, str(class_index))

    embedding_model = tf.keras.Model(
        inputs=model.input,
        outputs=model.get_layer("embedding").output
    )
    query_embedding = embedding_model.predict(input_array)[0].reshape(1, -1)

    semelhantes = []
    if index is not None and labels is not None:
        D, I = index.search(query_embedding, k=3)
        semelhantes = [
            {
                "item": f"{BUCKET_ORIGINAIS}/{labels[i]}",
                "distancia": float(D[0][j])
            }
            for j, i in enumerate(I[0])
        ]
    #distancia_minima = min([s["distancia"] for s in semelhantes]) if semelhantes else float("inf")
    #if confidence < 0.75 or distancia_minima > 75.0:
    #    class_name = "Indefinido"
    #    confidence = 0.0
    #    semelhantes = []

    print(json.dumps({
        "classe": class_name,
        "confianca": round(confidence, 4),
        "semelhantes": semelhantes
    }))

if __name__ == "__main__":
    main()