# OColecionadorTraining 🎓

## 📋 O que é?

O **OColecionadorTraining** é um serviço Python de **treinamento automático de modelos de IA**. Ele:

- 📨 **Escuta fila RabbitMQ** para novos datasets aumentados
- 📥 **Baixa imagens** do MinIO
- 🧠 **Treina modelos** TensorFlow com Transfer Learning (MobileNetV2)
- 📊 **Calcula métricas** (Accuracy, Precision, Recall, F1)
- 💾 **Salva modelos** versionados
- 📈 **Monitora progresso** com TensorBoard
- ⚡ **Suporta GPU** para acelerar
- 🔄 **Gerencia checkpoints** e early stopping

**Propósito:** Treinar automaticamente novos modelos quando há novos dados aumentados disponíveis.

---

## 🔄 Como Funciona?

```
1. Augmentations Service publica mensagem
   ↓
2. Training Service consome e valida
   ↓
3. Download dataset do MinIO (9000+ imagens)
   ↓
4. Split: train 80% / val 20%
   ↓
5. Phase 1: Feature Extraction (10 epochs, congelado)
   ↓
6. Phase 2: Fine-tuning (20 epochs, descongelado)
   ↓
7. Avaliar em test set
   ↓
8. Salvar modelo + métricas
   ↓
9. Upload para MinIO
   ↓
10. Publicar resultado na fila ModelEvaluation
```

---

## 🏗️ Stack Tecnológico

| Tecnologia | Versão | Propósito |
|-----------|--------|----------|
| **Python** | 3.11+ | Linguagem principal |
| **TensorFlow** | 2.14+ | Deep Learning |
| **Keras** | 2.14+ | Neural Networks API |
| **MobileNetV2** | - | Modelo base |
| **CUDA/cuDNN** | 12/9+ | GPU acceleration |
| **RabbitMQ** | 3+ | Fila de mensagens |
| **MinIO** | Latest | Storage S3 |
| **PostgreSQL** | 14+ | Banco de dados |
| **TensorBoard** | 2.14+ | Visualização |
| **WandB** | 0.15+ | Experiment tracking |
| **Docker** | Latest | Containerização |

---

## 🚀 Quick Start

### Pré-requisitos

- Python 3.11+ instalado
- CUDA 12+ e cuDNN 9+ (para GPU)
- RabbitMQ rodando
- MinIO rodando
- PostgreSQL rodando
- GPU com 6GB+ de memória (recomendado)

### Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/PatrickCalorioCarvalho/OColecionador.git
cd OColecionador/OColecionadorTraining

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
nano .env  # Edite com suas credenciais

# 5. Execute migrações PostgreSQL
psql -h localhost -U OColecionadorUser -d training_db < init_db.sql

# 6. Execute o serviço
python main.py
```

**Output esperado:**
```
[*] Aguardando mensagens de treinamento...
[*] Conectado a RabbitMQ
[*] Conectado a PostgreSQL
[*] TensorFlow GPU disponível: True
[*] Aguardando mensagens na fila 'ModelTraining'
```

---

### Com Docker Compose (Recomendado com GPU)

```bash
cd OColecionador/
docker compose up ocolecionadortraining
```

---

## 📁 Estrutura de Projeto

```
OColecionadorTraining/
├── main.py                      # Ponto de entrada
├── requirements.txt             # Dependências
├── Dockerfile                   # Imagem Docker
├── init_db.sql                 # Schema PostgreSQL
├── config.yaml                 # Configuração
├── .env.example                # Exemplo .env
├── models/
│   ├── v1/
│   │   ├── model.h5
│   │   ├── weights.h5
│   │   └── metadata.json
│   └── v2/
└── [módulos esperados]
    ├── config.py
    ├── rabbitmq_consumer.py
    ├── data_loader.py
    ├── model_builder.py
    ├── training_engine.py
    ├── callbacks.py
    ├── database.py
    └── logger.py
```

---

## ⚙️ Configuração

### .env

```bash
# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=OColecionadorUser
RABBITMQ_PASSWORD=OColecionador@2025
RABBITMQ_QUEUE=ModelTraining

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
CUDA_VISIBLE_DEVICES=0
TF_FORCE_GPU_ALLOW_GROWTH=true

# Treinamento
BATCH_SIZE=32
EPOCHS=30
LEARNING_RATE=0.001
EARLY_STOPPING_PATIENCE=5

# Logging
LOG_LEVEL=INFO
WANDB_ENABLED=true
```

### config.yaml

```yaml
model:
  name: MobileNetV2
  input_size: 224
  weights: imagenet

training:
  phase1:
    epochs: 10
    learning_rate: 0.001
    freeze_base: true
  phase2:
    epochs: 20
    learning_rate: 0.00001
    freeze_base: false

data:
  batch_size: 32
  validation_split: 0.2
  augmentation:
    rotation_range: 20
    horizontal_flip: true
    zoom_range: 0.2
```

---

## 📊 Pipeline de Treinamento

### Phase 1: Feature Extraction (10 epochs)

```
MobileNetV2 base: CONGELADO
Top layers: TREINÁVEIS
Learning rate: 0.001 (mais alto)
Epochs: 10
Objetivo: Adaptar camadas superiores ao nosso dataset
```

### Phase 2: Fine-tuning (20 epochs)

```
MobileNetV2 base: DESCONGELADO (últimas 50 layers)
Top layers: TREINÁVEIS
Learning rate: 0.00001 (muito mais baixo)
Epochs: 20
Objetivo: Ajustar pesos pré-treinados para nosso domínio
```

---

## 📊 Fluxo de Mensagens

### Consumo (Input)

**Fila:** `ModelTraining`

```json
{
  "batchId": "batch_20251115_001",
  "totalImages": 9000,
  "categories": ["carros", "moedas", "animais"],
  "augmentationCount": 9,
  "datasetPath": "training/carros/",
  "targetClasses": 50,
  "createdAt": "2025-11-15T10:00:00Z"
}
```

---

### Publicação (Output)

**Fila:** `ModelEvaluation`

```json
{
  "modelVersion": "v3_20251115_143022",
  "trainingStatus": "success",
  "metrics": {
    "accuracy": 0.9412,
    "precision": 0.9387,
    "recall": 0.9301,
    "f1_score": 0.9344
  },
  "trainingTime": 3600,
  "epochsCompleted": 30,
  "bestEpoch": 28,
  "modelPath": "models/v3_20251115_143022/model.h5",
  "completedAt": "2025-11-15T11:00:00Z"
}
```

---

## 🗄️ Banco de Dados

### Tabela: training_jobs

Rastreia todos os trabalhos de treinamento:

```sql
SELECT * FROM training_jobs;

id | batch_id | model_version | status | accuracy | training_time_seconds
---|----------|---------------|--------|----------|---------------------
1  | batch_001| v2_20251115   | success| 0.94     | 3600
2  | batch_002| v3_20251115   | training| null    | null
```

---

### Tabela: training_metrics

Métrica por epoch:

```sql
SELECT * FROM training_metrics WHERE job_id = 1;

epoch | loss   | accuracy | val_loss | val_accuracy | learning_rate
------|--------|----------|----------|--------------|---------------
0     | 2.1456 | 0.34     | 2.0987   | 0.38         | 0.001
1     | 1.8234 | 0.52     | 1.7654   | 0.55         | 0.001
...
29    | 0.1823 | 0.9412   | 0.2134   | 0.9301       | 0.00001
```

---

## 📊 Monitoramento

### TensorBoard em Tempo Real

```bash
# Iniciar TensorBoard
tensorboard --logdir=./logs/tensorboard --port=6006

# Acessar em http://localhost:6006
```

**Visualizações:**
- Loss e Accuracy por epoch
- Distribuição de pesos
- Histogramas de ativações
- Grafos do modelo

---

### Logs

```bash
# Ver logs em tempo real
tail -f training.log

# Exemplo
[2025-11-15 10:00:15] INFO    | Job 1 iniciado: batch_001
[2025-11-15 10:00:20] INFO    | Dataset carregado: 9000 imagens
[2025-11-15 10:00:30] INFO    | Model built: 2.3M parameters
[2025-11-15 10:01:00] INFO    | Epoch 1/30 - loss: 2.1456, acc: 0.34
[2025-11-15 10:02:00] INFO    | Epoch 2/30 - loss: 1.8234, acc: 0.52
...
[2025-11-15 11:00:00] INFO    | ✓ Training completed: accuracy=0.9412
```

---

## ⚡ Performance

| Métrica | Valor (GPU) | Valor (CPU) |
|---------|-------------|------------|
| **Tempo/epoch** | 2-3min | 15-20min |
| **Tempo total** | 60-90min | 8-10h |
| **Memória usada** | 4-6GB | 8-16GB |
| **Throughput** | 1000+ img/s | 50-100 img/s |
| **Acurácia final** | 92-96% | 92-96% |

---

## 🐛 Troubleshooting

### Erro: GPU not found

```bash
# Verifique CUDA
nvidia-smi

# Ou use CPU
export CUDA_VISIBLE_DEVICES=""
```

---

### Erro: Out of memory

```bash
# Reduza batch size em .env
BATCH_SIZE=16

# Ou limpe cache TensorFlow
python -c "import tensorflow as tf; tf.keras.backend.clear_session()"
```

---

### Erro: RabbitMQ connection failed

```bash
# Verifique credenciais
docker logs rabbitmq

# Ou reinicie
docker restart rabbitmq
```

---

## 🚀 Deployment

### Docker Compose com GPU

```yaml
training:
  build:
    context: ./OColecionadorTraining
    dockerfile: Dockerfile
  environment:
    - CUDA_VISIBLE_DEVICES=0
    - TF_FORCE_GPU_ALLOW_GROWTH=true
  volumes:
    - /usr/local/cuda:/usr/local/cuda:ro  # CUDA libraries
    - ./models:/app/models
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

---

### Kubernetes com GPU

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: training
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: training
        image: ocolecionador/training:latest
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        resources:
          limits:
            nvidia.com/gpu: "1"
            memory: "8Gi"
          requests:
            nvidia.com/gpu: "1"
            memory: "4Gi"
```

---

## 📚 Documentação Adicional

- [TensorFlow Training Guide](https://www.tensorflow.org/guide/keras/training_and_evaluation)
- [MobileNetV2 Paper](https://arxiv.org/abs/1801.04381)
- [Transfer Learning](https://cs231n.github.io/transfer-learning/)
- [TensorBoard](https://www.tensorflow.org/tensorboard)

---

## 👨‍💻 Contribuição

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/Melhoria`)
3. Commit suas mudanças
4. Push e abra Pull Request

---

## 📄 Licença

Open source. Veja [LICENSE](../../LICENSE) para detalhes.

---

## 👤 Autor

**Patrick Calorio Carvalho**  
📧 [Email](mailto:patrick@example.com) • 🔗 [GitHub](https://github.com/PatrickCalorioCarvalho)

---

## 📞 Suporte

- 📝 [GitHub Issues](https://github.com/PatrickCalorioCarvalho/OColecionador/issues)
- 💬 [Discussões](https://github.com/PatrickCalorioCarvalho/OColecionador/discussions)