import pika
import json
import os
import io
import datetime
import psycopg2
import numpy as np
import tensorflow as tf
from minio import Minio
from PIL import Image
import random
import sentry_sdk
import logging
import gc
from tensorflow.keras import backend as K

# Configura logging
logging.basicConfig(level=logging.INFO)

# Configura Sentry
sentry_sdk.init(
    dsn="http://4a08936b06c7360828a68f7810d04423@sentry:9000/2",
    send_default_pii=True,
)
sentry_sdk.capture_message("🚨 Teste manual de erro no Sentry!")

# Configura TensorFlow para alocar memória sob demanda
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        logging.warning(f"Erro ao configurar GPU: {e}")

# Conexão com PostgreSQL
conn = psycopg2.connect(
    host="postgres",
    dbname="OColecionadorAugmentationsDB",
    user="OColecionadorUser",
    password="OColecionador@2025",
    port=5432
)

# Conexão com MinIO
minio_client = Minio(
    "minio:9000",
    access_key="OColecionadorUser",
    secret_key="OColecionador@2025",
    secure=False
)

def salvar_metadata(item_id, categoria, original, variacao, split, bucket, caminho):
    logging.info(f"💾 Salvando metadata: {item_id}, {variacao}, {split}")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO imagens (item_id, categoria, original, variacao, dataset_split, bucket, caminho, criado_em) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (item_id, categoria, original, variacao, split, bucket, caminho, datetime.datetime.now().isoformat())
    )
    conn.commit()
    cur.close()

def buscar_split(item_id):
    cur = conn.cursor()
    cur.execute("SELECT dataset_split FROM imagens WHERE item_id = %s LIMIT 1", (item_id,))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None

def escolher_split():
    r = random.random()
    return "train" if r < 0.7 else "val" if r < 0.9 else "test"

def tf_augmentations(image_tensor):
    augmentations = {
        "orig": image_tensor,
        "rot90": tf.image.rot90(image_tensor, k=1),
        "rot180": tf.image.rot90(image_tensor, k=2),
        "flip_lr": tf.image.flip_left_right(image_tensor),
        "flip_ud": tf.image.flip_up_down(image_tensor),
        "bright": tf.image.adjust_brightness(image_tensor, 0.2),
        "contrast": tf.image.adjust_contrast(image_tensor, 2),
        "hue": tf.image.adjust_hue(image_tensor, 0.1),
        "saturation": tf.image.adjust_saturation(image_tensor, 2),
        "crop": tf.image.central_crop(image_tensor, 0.7)
    }
    return augmentations

def aplicar_augmentations_e_salvar(img_tensor, bucket, filename, categoria, item_id, split):
    variacoes = tf_augmentations(img_tensor)
    novo_bucket = f"{bucket}-processed"
    if not minio_client.bucket_exists(novo_bucket):
        minio_client.make_bucket(novo_bucket)

    for nome, tensor in variacoes.items():
        np_img = tensor.numpy()
        img_pil = Image.fromarray(np_img)
        buffer = io.BytesIO()
        img_pil.save(buffer, format="JPEG")
        buffer.seek(0)

        novo_nome = f"{os.path.splitext(os.path.basename(filename))[0]}_{nome}.jpg"
        caminho_final = f"{split}/{categoria}/{novo_nome}"
        logging.info(f"💾 Salvando variação {nome} em {caminho_final}")
        minio_client.put_object(
            novo_bucket,
            caminho_final,
            buffer,
            len(buffer.getvalue()),
            content_type="image/jpeg"
        )
        salvar_metadata(item_id, categoria, filename, novo_nome, split, novo_bucket, f"{novo_bucket}/{caminho_final}")

def processar_imagem(bucket, filename, categoria, item_id):
    try:
        response = minio_client.get_object(bucket, filename)
        image = Image.open(io.BytesIO(response.read())).convert("RGB")
        response.close()
        response.release_conn()

        img_array = np.array(image)
        img_tensor = tf.convert_to_tensor(img_array, dtype=tf.uint8)

        split = buscar_split(item_id) or escolher_split()
        aplicar_augmentations_e_salvar(img_tensor, bucket, filename, categoria, item_id, split)

        logging.info(f"✅ {filename} (item_id={item_id}) salvo em {split}/ com variações")
    except Exception as e:
        logging.exception("Erro ao processar imagem")
        sentry_sdk.capture_exception(e)
    finally:
        K.clear_session()
        del img_tensor, img_array
        gc.collect()

def callback(ch, method, properties, body):
    try:
        msg = json.loads(body)
        caminho = msg.get("Caminho")
        categoria = msg.get("Categoria")
        item_id = msg.get("ItemId")

        if caminho and categoria and item_id:
            bucket, filename = caminho.split("//", 1)
            logging.info(f"🔍 Processando {filename} do bucket {bucket}")
            processar_imagem(bucket, filename, categoria, item_id)
    except Exception as e:
        logging.exception("Erro no callback do RabbitMQ")
        sentry_sdk.capture_exception(e)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host="rabbitmq",
        port=5672,
        credentials=pika.PlainCredentials("OColecionadorUser", "OColecionador@2025"),
        connection_attempts=5,
        retry_delay=5
    ))
    channel = connection.channel()
    channel.queue_declare(queue="ImageAugmentations", durable=True)
    channel.basic_consume(queue="ImageAugmentations", on_message_callback=callback, auto_ack=True)

    logging.info(" [*] Aguardando mensagens do RabbitMQ...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
