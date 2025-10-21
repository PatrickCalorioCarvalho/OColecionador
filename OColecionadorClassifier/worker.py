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

def load_latest_model_and_classes():
    objects = list(minio_client.list_objects(BUCKET_MODELS, recursive=True))

    keras_files = [obj for obj in objects if obj.object_name.endswith(".keras")]
    json_files = [obj for obj in objects if obj.object_name.endswith(".json") and obj.object_name.startswith("classifier_")]

    def extract_timestamp(name):
        parts = name.replace(".keras", "").replace(".json", "").split("_")
        return "_".join(parts[1:]) if len(parts) > 1 else ""

    keras_by_ts = {extract_timestamp(obj.object_name): obj for obj in keras_files}
    json_by_ts = {extract_timestamp(obj.object_name): obj for obj in json_files}

    common_ts = sorted(set(keras_by_ts.keys()) & set(json_by_ts.keys()), reverse=True)
    if not common_ts:
        raise Exception("Nenhum par de arquivos .keras e .json encontrado com o mesmo timestamp.")

    ts = common_ts[0]
    keras_obj = keras_by_ts[ts]
    json_obj = json_by_ts[ts]

    model_path = f"/tmp/{keras_obj.object_name}"
    json_path = f"/tmp/{json_obj.object_name}"
    minio_client.fget_object(BUCKET_MODELS, keras_obj.object_name, model_path)
    minio_client.fget_object(BUCKET_MODELS, json_obj.object_name, json_path)

    model = tf.keras.models.load_model(model_path)
    with open(json_path, "r") as f:
        class_indices = json.load(f)
    index_to_class = {v: k for k, v in class_indices.items()}
    return model, index_to_class

def load_latest_index_and_labels():
    objects = list(minio_client.list_objects(BUCKET_MODELS, recursive=True))
    index_files = [obj for obj in objects if obj.object_name.startswith("index_original_") and obj.object_name.endswith(".faiss")]
    labels_files = [obj for obj in objects if obj.object_name.startswith("labels_original_") and obj.object_name.endswith(".npy")]

    if not index_files or not labels_files:
        return None, None

    latest_index = sorted(index_files, key=lambda x: x.last_modified, reverse=True)[0]
    latest_labels = sorted(labels_files, key=lambda x: x.last_modified, reverse=True)[0]

    index_path = f"/tmp/{latest_index.object_name}"
    labels_path = f"/tmp/{latest_labels.object_name}"

    minio_client.fget_object(BUCKET_MODELS, latest_index.object_name, index_path)
    minio_client.fget_object(BUCKET_MODELS, latest_labels.object_name, labels_path)

    index = faiss.read_index(index_path)
    labels = np.load(labels_path, allow_pickle=True)
    return index, labels

def main():
    image_bytes = sys.stdin.buffer.read()
    input_array = preprocess_image(image_bytes)

    model, index_to_class = load_latest_model_and_classes()
    prediction = model.predict(input_array)
    class_index = int(np.argmax(prediction))
    confidence = float(np.max(prediction))
    class_name = index_to_class.get(class_index, str(class_index))

    embedding_model = tf.keras.Model(inputs=model.input, outputs=model.get_layer("dense").output)
    query_embedding = embedding_model.predict(input_array)[0].reshape(1, -1)

    index, labels = load_latest_index_and_labels()
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

    print(json.dumps({
        "classe": class_name,
        "confianca": round(confidence, 4),
        "semelhantes": semelhantes
    }))

if __name__ == "__main__":
    main()