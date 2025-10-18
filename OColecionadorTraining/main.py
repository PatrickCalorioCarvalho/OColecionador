import os
from minio import Minio
import tempfile, shutil
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
import tensorflow as tf
import numpy as np
from datetime import datetime
import psycopg2
from collections import Counter

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,       
    event_level=logging.ERROR
)

sentry_sdk.init(
    "http://44f733a0f9384fb9a9272cb83fe5f358@glitchtip:8000/3",
    integrations=[sentry_logging],
    traces_sample_rate=1.0
)

logging.basicConfig(level=logging.INFO)


BUCKET_AUG = "ocolecionadorbucket-processed"
BUCKET_MODELS = "ocolecionadorbucket-models"
MODEL_VOLUME = "/mnt/modelos"

minio_client = Minio(
    "minio:9000",
    access_key="OColecionadorUser",
    secret_key="OColecionador@2025",
    secure=False
)

def download_augmentations(tmpdir):
    for obj in minio_client.list_objects(BUCKET_AUG, recursive=True):
        outpath = os.path.join(tmpdir, obj.object_name)
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        minio_client.fget_object(BUCKET_AUG, obj.object_name, outpath)
    logging.info('✅ Imagens baixadas para', tmpdir)

def count_classes_by_subset(generator):
    counts = Counter(generator.classes)
    index_to_class = {v: k for k, v in generator.class_indices.items()}
    return {index_to_class[i]: count for i, count in counts.items()}

def save_metrics_to_db(train_count, val_count, test_count, acc, loss, model_path):
    conn = psycopg2.connect(
        host="postgres",
        database="OColecionadorAugmentationsDB",
        user="OColecionadorUser",
        password="OColecionador@2025"
    )
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO modelo_resultado (
            data_geracao, imagens_treino, imagens_validacao, imagens_teste,
            acuracia_teste, perda_teste, caminho_modelo
        ) VALUES (NOW(), %s, %s, %s, %s, %s, %s) RETURNING id
    """, (train_count, val_count, test_count, acc, loss, model_path))
    model_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    logging.info("✅ Métricas salvas no PostgreSQL")
    return model_id

# Função para salvar distribuição por categoria
def save_distribution_to_db(model_id, subset_name, class_counts):
    conn = psycopg2.connect(
        host="postgres",
        database="OColecionadorAugmentationsDB",
        user="OColecionadorUser",
        password="OColecionador@2025"
    )
    cur = conn.cursor()
    for categoria, quantidade in class_counts.items():
        cur.execute("""
            INSERT INTO modelo_distribuicao (modelo_id, conjunto, categoria, quantidade)
            VALUES (%s, %s, %s, %s)
        """, (model_id, subset_name, categoria, quantidade))
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f"✅ Distribuição '{subset_name}' salva no banco")

# Função principal
def train():
    tmp = tempfile.mkdtemp()
    try:
        download_augmentations(tmp)

        train_gen = ImageDataGenerator(rescale=1./255).flow_from_directory(
            os.path.join(tmp, "training"),
            target_size=(224, 224),
            batch_size=16,
            class_mode='categorical'
        )

        val_gen = ImageDataGenerator(rescale=1./255).flow_from_directory(
            os.path.join(tmp, "validation"),
            target_size=(224, 224),
            batch_size=16,
            class_mode='categorical'
        )

        test_gen = ImageDataGenerator(rescale=1./255).flow_from_directory(
            os.path.join(tmp, "test"),
            target_size=(224, 224),
            batch_size=16,
            class_mode='categorical',
            shuffle=False
        )

        base = tf.keras.applications.MobileNetV2(weights='imagenet', include_top=False, input_shape=(224,224,3))
        base.trainable = False

        model = models.Sequential([
            base,
            layers.GlobalAveragePooling2D(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(train_gen.num_classes, activation='softmax')
        ])

        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        model.fit(train_gen, validation_data=val_gen, epochs=3)

        loss, acc = model.evaluate(test_gen)
        acc = float(f"{acc:.4f}")
        loss = float(f"{loss:.4f}")
        logging.info(f"📊 Test accuracy: {str(acc)} | Test loss: {str(loss)}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"classifier_{timestamp}.keras"
        model_path = os.path.join(MODEL_VOLUME, model_filename)
        os.makedirs(MODEL_VOLUME, exist_ok=True)
        model.save(model_path)
        logging.info(f"✅ Modelo salvo localmente: {model_path}")

        if not minio_client.bucket_exists(BUCKET_MODELS):
            minio_client.make_bucket(BUCKET_MODELS)
        minio_client.fput_object(BUCKET_MODELS, model_filename, model_path)
        logging.info(f"✅ Modelo salvo no MinIO: {BUCKET_MODELS}/{model_filename}")

        model_id = save_metrics_to_db(
            train_gen.samples,
            val_gen.samples,
            test_gen.samples,
            acc,
            loss,
            f"{BUCKET_MODELS}/{model_filename}"
        )

        save_distribution_to_db(model_id, "training", count_classes_by_subset(train_gen))
        save_distribution_to_db(model_id, "validation", count_classes_by_subset(val_gen))
        save_distribution_to_db(model_id, "test", count_classes_by_subset(test_gen))
        
    finally:
        shutil.rmtree(tmp)
        logging.info("🧹 Diretório temporário removido")

if __name__ == '__main__':
    train()
