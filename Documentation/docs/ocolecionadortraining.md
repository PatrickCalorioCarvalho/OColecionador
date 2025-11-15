---
id: ocolecionadortraining
title: OColecionadorTraining
sidebar_label: Introdução
---

# OColecionadorTraining 🎓

## 📋 Visão Geral

O **OColecionadorTraining** é um serviço Python de **treinamento de modelos de Deep Learning** que funciona como um **orquestrador de pipelines de IA**. Ele:

- 📨 **Consome mensagens** do RabbitMQ (fila: ModelTraining)
- 📥 **Baixa dataset aumentado** do MinIO (bucket: processed)
- 🎯 **Treina modelos** TensorFlow/Keras (MobileNetV2)
- 📊 **Calcula métricas** (Accuracy, Precision, Recall, F1)
- 💾 **Registra histórico** no PostgreSQL
- 📤 **Salva modelos** no MinIO e filesystem
- 🎲 **Gerencia versões** de modelos (v1, v2, v3...)
- ⚡ **Suporta GPU** para acelerar treinamento
- 📈 **Monitora progresso** com callbacks

### Responsabilidades Principais

- 🔔 **Consumo de Fila** – Escuta mensagens de novos datasets
- 📥 **Data Loading** – Carrega e valida imagens do MinIO
- 🔀 **Data Augmentation** – Aplicações em tempo de treinamento
- 🧠 **Transfer Learning** – Fine-tuning de MobileNetV2
- 📊 **Validação** – Avalia modelo em validation set
- 🎯 **Hyperparameter Tuning** – Grid search/random search
- 💾 **Model Versioning** – Salva checkpoints e best model
- 📈 **Logging de Métricas** – TensorBoard, WandB, custom
- 🔄 **Retry Logic** – Reprocessa falhas com backoff

---

## 🏗️ Arquitetura

### Estrutura de Pastas

```
OColecionadorTraining/
├── main.py                          # Ponto de entrada
├── requirements.txt                 # Dependências Python
├── Dockerfile                       # Imagem Docker
├── init_db.sql                     # Schema PostgreSQL
├── config.yaml                     # Configuração de treinamento
├── models/
│   ├── v1/
│   │   ├── model.h5               # Modelo treinado
│   │   ├── weights.h5             # Pesos
│   │   ├── training_log.csv       # Histórico
│   │   └── metadata.json
│   └── v2/
│       ├── model.h5
│       ├── weights.h5
│       └── metadata.json
├── datasets/
│   ├── train/
│   │   ├── carros/
│   │   ├── moedas/
│   │   └── animais/
│   ├── val/
│   └── test/
├── logs/
│   ├── tensorboard/
│   ├── training.log
│   └── metrics.json
└── [módulos Python esperados]
    ├── config.py                   # Configurações
    ├── rabbitmq_consumer.py        # Consumer RabbitMQ
    ├── data_loader.py              # Data pipeline
    ├── minio_handler.py            # Handler MinIO
    ├── model_builder.py            # Construção de modelos
    ├── training_engine.py          # Motor de treinamento
    ├── validators.py               # Validação
    ├── database.py                 # Conexão PostgreSQL
    ├── callbacks.py                # Custom callbacks
    └── logger.py                   # Logging centralizado
```

---

## 📦 Dependências Principais

```txt
Python 3.11+
├── tensorflow                  # Deep learning framework
├── keras                       # Neural network API
├── numpy                       # Computação numérica
├── pandas                      # Data manipulation
├── pillow                      # Processamento de imagens
├── opencv-python              # Visão computacional
├── scikit-learn               # ML utilities
├── pika                       # RabbitMQ Client
├── minio                      # MinIO/S3 Client
├── psycopg2-binary            # PostgreSQL Client
├── python-dotenv              # Variáveis de ambiente
├── tensorboard                # Visualization
├── wandb                      # Experiment tracking
├── matplotlib                 # Plotting
└── requests                   # HTTP client
```

---

## 🔌 Fluxo Principal

```mermaid
graph LR
    A["📨 RabbitMQ<br/>fila: ModelTraining"] -->|Mensagem| B["🎓 Training Service"]
    B -->|Download| C["📦 MinIO<br/>bucket: processed"]
    B -->|Load| D["📊 Data Pipeline"]
    D -->|Train/Val split| E["🔀 Generators"]
    E -->|Batch processing| F["🧠 TensorFlow Model"]
    F -->|Callbacks| G["📈 TensorBoard"]
    F -->|Save| H["💾 Best Checkpoint"]
    H -->|Upload| I["📦 MinIO<br/>bucket: models"]
    F -->|Metrics| J["💾 PostgreSQL"]
    J -->|Query| K["📊 Dashboard"]
```

---

## 🧠 Arquitetura do Modelo de Treinamento

### Transfer Learning com MobileNetV2

```
Input: 224x224x3 (RGB)
    ↓
[MobileNetV2 - Weights pré-treinados (ImageNet)]
    ├─ Depthwise Separable Convolutions
    ├─ BatchNormalization
    ├─ Linear Bottleneck
    └─ Inverted Residual blocks
    ↓
Global Average Pooling (1280D)
    ↓
Dense(512, activation='relu') [Fine-tune]
    ↓
Dropout(0.5) [Regularização]
    ↓
Dense(num_classes, activation='softmax') [Fine-tune]
    ↓
Output: [prob_classe1, prob_classe2, ..., prob_classeN]
```

### Estratégias de Treinamento

**Phase 1: Feature Extraction (Congelado)**
```
MobileNetV2 base: frozen=True
Top layers: trainable
Learning rate: 1e-3
Epochs: 10
```

**Phase 2: Fine-tuning (Descongelado)**
```
MobileNetV2 base: frozen=False (últimas 50 layers)
Top layers: trainable
Learning rate: 1e-5
Epochs: 20
```

---

## 📨 Formato de Mensagem RabbitMQ

### Input (Consumo)

**Fila:** `ModelTraining`

```json
{
  "batchId": "batch_20251115_001",
  "totalImages": 450,
  "categories": ["carros", "moedas", "animais"],
  "augmentationCount": 9,
  "datasetPath": "training/carros/",
  "targetClasses": 50,
  "priority": "high",
  "createdAt": "2025-11-15T10:00:00Z"
}
```

### Output (Publicação após sucesso)

**Fila:** `ModelEvaluation`

```json
{
  "modelVersion": "v3_20251115_143022",
  "trainingStatus": "success",
  "metrics": {
    "accuracy": 0.9412,
    "precision": 0.9387,
    "recall": 0.9301,
    "f1_score": 0.9344,
    "loss": 0.1823
  },
  "trainingTime": 3600,
  "epochsCompleted": 30,
  "bestEpoch": 28,
  "modelPath": "models/v3_20251115_143022/model.h5",
  "metricsPath": "models/v3_20251115_143022/metrics.json",
  "embeddingsPath": "models/v3_20251115_143022/embeddings.faiss",
  "completedAt": "2025-11-15T11:00:00Z"
}
```

---

## 🗄️ Estrutura de Dados PostgreSQL

### Tabela: training_jobs

```sql
CREATE TABLE training_jobs (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) UNIQUE NOT NULL,
    model_version VARCHAR(50) UNIQUE,
    status VARCHAR(20), -- pending, training, validating, success, failed
    total_images INT,
    total_categories INT,
    augmentation_count INT,
    target_accuracy DECIMAL(5, 4),
    achieved_accuracy DECIMAL(5, 4),
    achieved_precision DECIMAL(5, 4),
    achieved_recall DECIMAL(5, 4),
    achieved_f1 DECIMAL(5, 4),
    training_time_seconds INT,
    epochs_completed INT,
    best_epoch INT,
    early_stopping_patience INT DEFAULT 5,
    stopped_reason VARCHAR(100),
    error_message TEXT,
    attempts INT DEFAULT 0,
    max_attempts INT DEFAULT 2,
    model_path VARCHAR(255),
    metrics_path VARCHAR(255),
    embeddings_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: training_metrics

```sql
CREATE TABLE training_metrics (
    id SERIAL PRIMARY KEY,
    job_id INT REFERENCES training_jobs(id),
    epoch INT,
    loss DECIMAL(8, 6),
    accuracy DECIMAL(5, 4),
    val_loss DECIMAL(8, 6),
    val_accuracy DECIMAL(5, 4),
    precision DECIMAL(5, 4),
    recall DECIMAL(5, 4),
    f1_score DECIMAL(5, 4),
    learning_rate DECIMAL(10, 8),
    duration_seconds INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: model_versions

```sql
CREATE TABLE model_versions (
    id SERIAL PRIMARY KEY,
    model_version VARCHAR(50) UNIQUE,
    accuracy DECIMAL(5, 4),
    precision DECIMAL(5, 4),
    recall DECIMAL(5, 4),
    f1_score DECIMAL(5, 4),
    is_production BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,
    deployment_date TIMESTAMP,
    model_path VARCHAR(255),
    total_parameters INT,
    inference_time_ms DECIMAL(6, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: hyperparameters

```sql
CREATE TABLE hyperparameters (
    id SERIAL PRIMARY KEY,
    job_id INT REFERENCES training_jobs(id),
    batch_size INT,
    learning_rate DECIMAL(10, 8),
    optimizer VARCHAR(50), -- adam, sgd, rmsprop
    loss_function VARCHAR(50), -- categorical_crossentropy
    epochs INT,
    early_stopping_patience INT,
    dropout_rate DECIMAL(3, 2),
    l1_regularization DECIMAL(10, 8),
    l2_regularization DECIMAL(10, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```bash
# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=OColecionadorUser
RABBITMQ_PASSWORD=OColecionador@2025
RABBITMQ_QUEUE=ModelTraining
RABBITMQ_OUTPUT_QUEUE=ModelEvaluation

# MinIO
MINIO_HOST=minio
MINIO_PORT=9000
MINIO_ACCESS_KEY=OColecionadorUser
MINIO_SECRET_KEY=OColecionador@2025
MINIO_BUCKET_PROCESSED=ocolecionadorbucket-processed
MINIO_BUCKET_MODELS=ocolecionadorbucket-models

# PostgreSQL
DB_HOST=postgres
DB_PORT=5432
DB_NAME=training_db
DB_USER=OColecionadorUser
DB_PASSWORD=OColecionador@2025

# TensorFlow
TF_CPP_MIN_LOG_LEVEL=2
CUDA_VISIBLE_DEVICES=0  # GPU device
TF_FORCE_GPU_ALLOW_GROWTH=true

# Treinamento
BATCH_SIZE=32
EPOCHS=30
LEARNING_RATE=0.001
EARLY_STOPPING_PATIENCE=5
VALIDATION_SPLIT=0.2
TEST_SPLIT=0.1

# Logging
LOG_LEVEL=INFO
LOG_FILE=/logs/training.log
TENSORBOARD_LOG_DIR=/logs/tensorboard
WANDB_ENABLED=true
WANDB_PROJECT=ocolecionador
WANDB_API_KEY=<sua_chave_wandb>
```

### config.yaml

```yaml
# config.yaml - Configuração de treinamento

model:
  name: MobileNetV2
  input_size: 224
  pooling: global_average
  weights: imagenet  # pré-treinado

training:
  phase1:
    epochs: 10
    learning_rate: 0.001
    freeze_base: true
    
  phase2:
    epochs: 20
    learning_rate: 0.00001
    freeze_base: false
    freeze_until_layer: 100

optimizer:
  name: adam
  beta_1: 0.9
  beta_2: 0.999
  epsilon: 1e-7

loss:
  function: categorical_crossentropy
  
regularization:
  dropout: 0.5
  l1: 0.0001
  l2: 0.0001

data:
  batch_size: 32
  validation_split: 0.2
  test_split: 0.1
  shuffle: true
  augmentation:
    rotation_range: 20
    width_shift_range: 0.2
    height_shift_range: 0.2
    horizontal_flip: true
    zoom_range: 0.2
    
callbacks:
  early_stopping:
    monitor: val_loss
    patience: 5
    restore_best: true
    
  model_checkpoint:
    monitor: val_accuracy
    save_best_only: true
    
  reduce_lr:
    monitor: val_loss
    factor: 0.1
    patience: 3
    min_lr: 1e-7
    
tensorboard:
  enabled: true
  histogram_freq: 1
```

---

## 🚀 Estrutura de Código (main.py)

```python
# main.py - Ponto de entrada

import pika
import json
import logging
import tensorflow as tf
from tensorflow import keras
import numpy as np
import psycopg2
from datetime import datetime
import time

# Configuração
RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
INPUT_QUEUE = "ModelTraining"
OUTPUT_QUEUE = "ModelEvaluation"

# Conexões
db_connection = psycopg2.connect(...)

def process_training_message(ch, method, properties, body):
    """Callback para processar mensagem de treinamento"""
    job_id = None
    try:
        message = json.loads(body)
        batch_id = message['batchId']
        total_images = message['totalImages']
        categories = message['categories']
        
        # 1. Criar registro no banco
        job_id = create_training_job(batch_id, total_images, len(categories))
        
        # 2. Baixar dataset do MinIO
        dataset_path = download_dataset_from_minio(batch_id)
        
        # 3. Carregar e preparar dados
        train_gen, val_gen, num_classes = prepare_data_generators(
            dataset_path,
            batch_size=32,
            validation_split=0.2
        )
        
        # 4. Construir modelo
        model = build_model(num_classes=num_classes)
        
        # 5. Compilar modelo
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        # 6. Definir callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.1,
                patience=3,
                min_lr=1e-7
            ),
            keras.callbacks.TensorBoard(
                log_dir='./logs/tensorboard',
                histogram_freq=1
            ),
            CustomMetricsCallback(job_id)
        ]
        
        # 7. Treinar modelo
        start_time = time.time()
        
        history = model.fit(
            train_gen,
            epochs=30,
            validation_data=val_gen,
            callbacks=callbacks,
            verbose=1
        )
        
        training_time = time.time() - start_time
        
        # 8. Avaliar no test set
        test_metrics = evaluate_model(model, job_id)
        
        # 9. Salvar modelo
        model_version = f"v{get_version_number()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = save_model(model, model_version)
        
        # 10. Upload para MinIO
        minio_path = upload_model_to_minio(model_path, model_version)
        
        # 11. Registrar sucesso no banco
        update_training_job_success(
            job_id,
            model_version,
            test_metrics,
            training_time
        )
        
        # 12. Publicar resultado
        publish_training_result(
            model_version,
            test_metrics,
            minio_path,
            'success'
        )
        
        # 13. ACK da mensagem
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logging.info(f"✓ Treinamento {batch_id} concluído: {model_version}")
        
    except Exception as e:
        logging.error(f"Erro no treinamento: {str(e)}")
        
        if job_id:
            update_training_job_error(job_id, str(e))
        
        # NACK com requeue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def build_model(num_classes):
    """Constrói modelo MobileNetV2 com transfer learning"""
    
    # Carregar base pré-treinada
    base_model = keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Congelar base inicialmente
    base_model.trainable = False
    
    # Adicionar top layers
    model = keras.Sequential([
        keras.layers.Input(shape=(224, 224, 3)),
        base_model,
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.Dense(512, activation='relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    return model


def prepare_data_generators(dataset_path, batch_size=32, validation_split=0.2):
    """Prepara data generators com augmentação"""
    
    train_datagen = keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        fill_mode='nearest'
    )
    
    val_datagen = keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255
    )
    
    train_gen = train_datagen.flow_from_directory(
        dataset_path,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset='training'
    )
    
    val_gen = val_datagen.flow_from_directory(
        dataset_path,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation'
    )
    
    return train_gen, val_gen, train_gen.num_classes


class CustomMetricsCallback(keras.callbacks.Callback):
    """Callback customizado para registrar métricas"""
    
    def __init__(self, job_id):
        super().__init__()
        self.job_id = job_id
    
    def on_epoch_end(self, epoch, logs=None):
        # Salvar métrica no banco
        save_epoch_metrics(
            self.job_id,
            epoch,
            logs
        )


def main():
    """Função principal - inicia consumer"""
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    
    channel.queue_declare(queue=INPUT_QUEUE, durable=True)
    channel.basic_consume(
        queue=INPUT_QUEUE,
        on_message_callback=process_training_message,
        auto_ack=False
    )
    
    logging.info("[*] Aguardando mensagens de treinamento...")
    channel.start_consuming()


if __name__ == '__main__':
    main()
```

---

## 🐳 Docker

### Dockerfile

```dockerfile
FROM tensorflow/tensorflow:latest-gpu

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=10s --retries=3 \
    CMD python -c "import tensorflow; print('OK')" || exit 1

# Executar
CMD ["python", "main.py"]
```

### requirements.txt

```txt
tensorflow==2.14.0
keras==2.14.0
numpy==1.24.3
pandas==2.1.0
pillow==10.1.0
opencv-python==4.8.1.78
scikit-learn==1.3.2
pika==1.3.1
minio==7.1.15
psycopg2-binary==2.9.9
python-dotenv==1.0.0
tensorboard==2.14.0
wandb==0.15.12
matplotlib==3.8.1
requests==2.31.0
```

---

## 📊 Exemplo de Fluxo Completo

```mermaid
sequenceDiagram
    participant Augmentations as 🎨 Augmentations Service
    participant RabbitMQ as 📨 RabbitMQ
    participant Training as 🎓 Training Service
    participant MinIO as 📦 MinIO
    participant PostgreSQL as 💾 PostgreSQL
    participant TensorBoard as 📊 TensorBoard

    Augmentations->>RabbitMQ: Publish (9000 imagens aumentadas)
    RabbitMQ->>Training: Delivery (batchId, totalImages)
    
    Training->>PostgreSQL: INSERT training_jobs (status: training)
    Training->>MinIO: Download dataset (9000 imagens)
    MinIO-->>Training: Stream de imagens
    
    Training->>Training: Split train 80% val 20%
    Training->>Training: Constrói MobileNetV2
    
    loop 30 epochs
        Training->>Training: Phase 1: Feature extraction (10 ep)
        Training->>Training: Phase 2: Fine-tuning (20 ep)
        Training->>PostgreSQL: INSERT training_metrics (epoch, loss, accuracy)
        Training->>TensorBoard: Log scalars
    end
    
    Training->>Training: Avaliar no test set
    Training->>Training: Calcula métricas finais
    Training->>Training: Salva model.h5
    
    Training->>MinIO: Upload model (v3_20251115)
    MinIO-->>Training: Uploaded OK
    
    Training->>PostgreSQL: UPDATE training_jobs (status: success, accuracy: 0.94)
    Training->>RabbitMQ: Publish (ModelEvaluation fila)
    Training->>RabbitMQ: ACK
```

---

## ⚡ Performance

| Métrica | Valor |
|---------|-------|
| **Tempo de treinamento** | 60-120 minutos |
| **Memória necessária** | 4-8GB (GPU) |
| **Throughput** | 1 modelo/hora |
| **Acurácia final** | 92-96% |
| **Tamanho do modelo** | 50-100MB |
| **Tempo de inferência** | 100-200ms |

---

## 🎯 Conclusão

O **OColecionadorTraining** é um serviço robusto e eficiente que:

✅ **Consome mensagens** de forma assíncrona  
✅ **Treina modelos** com Transfer Learning  
✅ **Gerencia versões** de modelos  
✅ **Registra métricas** detalhadas  
✅ **Suporta GPU** para acelerar treinamento  
✅ **Integra com TensorBoard** para visualização  
✅ **Publica resultados** para fila de avaliação  

**Tempo médio: 60-120 minutos por modelo**