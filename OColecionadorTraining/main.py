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
        outpath = os.path.join(tmpdir, obj.object_name)
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        minio_client.fget_object(BUCKET_AUG, obj.object_name, outpath)
    print('Downloaded augmentations to', tmpdir)

def train():
    tmp = tempfile.mkdtemp()
    try:
        download_augmentations(tmp)
        datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)
        train_gen = datagen.flow_from_directory(tmp, target_size=(224,224), batch_size=16, subset='train', class_mode='categorical')
        val_gen = datagen.flow_from_directory(tmp, target_size=(224,224), batch_size=16, subset='val', class_mode='categorical')
        print('Found', train_gen.num_classes, 'classes:', train_gen.class_indices)
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
        os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
        model.save(MODEL_OUT)
        print('Saved model to', MODEL_OUT)
    finally:
        shutil.rmtree(tmp)

if __name__ == '__main__':
    train()
