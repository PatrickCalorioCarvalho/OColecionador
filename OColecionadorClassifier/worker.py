import sys
import json
import tensorflow as tf
from PIL import Image
import numpy as np
import io
from minio import Minio

BUCKET_MODELS = "ocolecionadorbucket-models"

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize((224, 224))
    array = np.array(image) / 255.0
    return np.expand_dims(array, axis=0)

def load_model_and_classes():
    minio_client = Minio(
        "minio:9000",
        access_key="OColecionadorUser",
        secret_key="OColecionador@2025",
        secure=False
    )
    objects = list(minio_client.list_objects(BUCKET_MODELS, recursive=True))
    keras_files = [obj for obj in objects if obj.object_name.endswith(".keras")]
    latest = sorted(keras_files, key=lambda x: x.last_modified, reverse=True)[0]
    model_path = f"/tmp/{latest.object_name}"
    minio_client.fget_object(BUCKET_MODELS, latest.object_name, model_path)
    model = tf.keras.models.load_model(model_path)

    json_name = latest.object_name.replace("classifier_", "class_indices_").replace(".keras", ".json")
    json_path = f"/tmp/{json_name}"
    minio_client.fget_object(BUCKET_MODELS, json_name, json_path)
    with open(json_path, "r") as f:
        class_indices = json.load(f)
    index_to_class = {v: k for k, v in class_indices.items()}
    return model, index_to_class

def main():
    image_bytes = sys.stdin.buffer.read()
    input_array = preprocess_image(image_bytes)
    model, index_to_class = load_model_and_classes()
    prediction = model.predict(input_array)
    class_index = int(np.argmax(prediction))
    confidence = float(np.max(prediction))
    class_name = index_to_class.get(class_index, str(class_index))
    print(json.dumps({"classe": class_name, "confianca": round(confidence, 4)}))

if __name__ == "__main__":
    main()
