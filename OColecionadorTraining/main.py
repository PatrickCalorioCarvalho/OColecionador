import os
from minio import Minio
import tempfile, shutil
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
import tensorflow as tf
import numpy as np

BUCKET_AUG = "ocolecionadorbucket-processed"
MODEL_OUT = "models/classifier.keras"

minio_client = Minio(
    "minio:9000",
    access_key="OColecionadorUser",
    secret_key="OColecionador@2025",
    secure=False
)

def download_augmentations(tmpdir):
    for obj in minio_client.list_objects(BUCKET_AUG, recursive=True):
        print('Downloading', obj.object_name)
        outpath = os.path.join(tmpdir, obj.object_name)
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        minio_client.fget_object(BUCKET_AUG, obj.object_name, outpath)
    print('Downloaded augmentations to', tmpdir)

def train():
    tmp = tempfile.mkdtemp()
    try:
        download_augmentations(tmp)
        print('Starting training...')
        print('Using TensorFlow version', tf.__version__)
        print('Num GPUs Available:', len(tf.config.list_physical_devices('GPU')))
        print("Files in tmp:", sum(len(files) for _, _, files in os.walk(tmp)))

        # Geradores separados para treino, validação e teste
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

        print('Found', train_gen.num_classes, 'classes:', train_gen.class_indices)

        # Modelo baseado em MobileNetV2
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

        # Avaliação no conjunto de teste
        loss, acc = model.evaluate(test_gen)
        print(f"📊 Test accuracy: {acc:.4f} | Test loss: {loss:.4f}")

        os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
        model.save(MODEL_OUT)
        print('Saved model to', MODEL_OUT)

    finally:
        shutil.rmtree(tmp)

if __name__ == '__main__':
    train()
