# OColecionadorClassifier 🤖

## 📋 O que é?

O **OColecionadorClassifier** é um serviço Python de **inferência de IA** que classifica imagens de colecionáveis. Ele:

- 🔍 **Recebe imagens** via HTTP POST
- 🧠 **Executa Deep Learning** (TensorFlow + MobileNetV2)
- 🎯 **Retorna classe e confiança**
- 🔗 **Encontra itens similares** usando FAISS
- 💾 **Registra predições** no PostgreSQL
- ⚡ **Processa rápido** (150-350ms por imagem)

**Propósito:** Classificar automaticamente colecionáveis e sugerir itens similares no catálogo.

---

## 🔄 Como Funciona?

```
1. Usuário seleciona foto no app
   ↓
2. Backend envia para Classifier API
   ↓
3. Classifier redimensiona para 224x224
   ↓
4. TensorFlow faz forward pass (MobileNetV2)
   ↓
5. Retorna: classe + confiança + embedding 512D
   ↓
6. FAISS busca 5 itens similares no índice
   ↓
7. Backend retorna resultado com sugestões
```

---

## 🏗️ Stack Tecnológico

| Tecnologia | Versão | Propósito |
|-----------|--------|----------|
| **Python** | 3.11+ | Linguagem principal |
| **TensorFlow** | 2.14+ | Deep Learning framework |
| **MobileNetV2** | - | Modelo pré-treinado |
| **FAISS** | 1.7.4 | Busca de similaridade |
| **Flask** | 3.0+ | Web API |
| **NumPy** | 1.24+ | Computação numérica |
| **Pillow** | 10.1+ | Processamento de imagens |
| **PostgreSQL** | 14+ | Banco de dados |
| **Docker** | Latest | Containerização |

---

## 🚀 Quick Start

### Pré-requisitos

- Python 3.11+ instalado
- PostgreSQL rodando
- MinIO rodando (opcional para download de imagens)

### Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/PatrickCalorioCarvalho/OColecionador.git
cd OColecionador/OColecionadorClassifier

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
psql -h localhost -U OColecionadorUser -d classifier_db < init_db.sql

# 6. Baixe/prepare os modelos
# Coloque model.h5 e embeddings.faiss em ./models/v2/

# 7. Execute o serviço
python app.py
```

**Output esperado:**
```
 * Running on http://0.0.0.0:5001
 * Model loaded: v2_20251115
 * FAISS index loaded: 5000 items
 * PostgreSQL connected
```

---

### Com Docker Compose (Recomendado)

```bash
cd OColecionador/
docker compose up ocolecionadorclassifier
```

---

## 📁 Estrutura de Projeto

```
OColecionadorClassifier/
├── app.py                      # Ponto de entrada Flask
├── requirements.txt            # Dependências
├── Dockerfile                  # Imagem Docker
├── init_db.sql                # Schema PostgreSQL
├── .env.example               # Exemplo de configuração
├── models/
│   ├── v1/
│   │   ├── model.h5          # Modelo TensorFlow
│   │   ├── embeddings.faiss  # Índice FAISS
│   │   └── metadata.json
│   └── v2/
│       ├── model.h5
│       ├── embeddings.faiss
│       └── metadata.json
└── [módulos esperados]
    ├── config.py
    ├── model_loader.py
    ├── inference_engine.py
    ├── minio_handler.py
    ├── database.py
    ├── validators.py
    └── logger.py
```

---

## ⚙️ Configuração

### .env

```bash
# Flask/API
FLASK_ENV=production
FLASK_PORT=5001
WORKERS=4

# Modelos
MODEL_PATH=./models/v2/model.h5
EMBEDDINGS_PATH=./models/v2/embeddings.faiss
MODEL_VERSION=v2_20251115
INPUT_SIZE=224

# MinIO (para download de imagens)
MINIO_HOST=minio
MINIO_PORT=9000
MINIO_ACCESS_KEY=OColecionadorUser
MINIO_SECRET_KEY=OColecionador@2025

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=classifier_db
DB_USER=OColecionadorUser
DB_PASSWORD=OColecionador@2025

# FAISS
FAISS_METRIC=L2

# Logging
LOG_LEVEL=INFO
```

---

## 🔌 Endpoints Principais

### 1. **POST /api/classify**

Classifica uma imagem.

**Request:**
```bash
curl -X POST -F "image=@foto.jpg" http://localhost:5001/api/classify?top_k=3
```

**Response:**
```json
{
  "classe": "carro",
  "confianca": 0.92,
  "top_k_predictions": [
    { "classe": "carro", "confianca": 0.92 },
    { "classe": "lamborghini", "confianca": 0.07 },
    { "classe": "veiculo", "confianca": 0.01 }
  ],
  "embedding": [0.12, -0.34, ...],
  "inference_time_ms": 145,
  "model_version": "v2_20251115"
}
```

---

### 2. **POST /api/classify/batch**

Classifica múltiplas imagens.

**Request:**
```bash
curl -X POST -F "images=@foto1.jpg" -F "images=@foto2.jpg" \
  http://localhost:5001/api/classify/batch
```

**Response:**
```json
{
  "results": [
    {
      "image_id": "1",
      "classe": "carro",
      "confianca": 0.92
    },
    {
      "image_id": "2",
      "classe": "moeda",
      "confianca": 0.88
    }
  ],
  "total_time_ms": 420
}
```

---

### 3. **POST /api/classify/similarity**

Encontra itens similares.

**Request:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"embedding": [0.12, -0.34, ...], "k": 5}' \
  http://localhost:5001/api/classify/similarity
```

**Response:**
```json
{
  "similar_items": [
    {
      "item_id": 101,
      "nome": "Ferrari 250",
      "distancia": 0.08,
      "confianca_similaridade": 0.92,
      "foto_url": "https://minio.../item/101.jpg"
    }
  ],
  "total_found": 5
}
```

---

### 4. **GET /api/model/status**

Status do modelo.

```bash
curl http://localhost:5001/api/model/status
```

**Response:**
```json
{
  "model_version": "v2_20251115",
  "status": "loaded",
  "accuracy": 0.94,
  "total_classes": 50,
  "faiss_index_size": 5000
}
```

---

### 5. **GET /api/model/classes**

Lista todas as classes.

```bash
curl http://localhost:5001/api/model/classes
```

**Response:**
```json
{
  "total_classes": 50,
  "classes": [
    { "id": 0, "name": "carro" },
    { "id": 1, "name": "lamborghini" },
    ...
  ]
}
```

---

## 🗄️ Banco de Dados

### Tabela: predictions

Armazena todas as predições feitas:

```sql
SELECT * FROM predictions;

id | image_path | classe | confianca | inference_time_ms | created_at
---|------------|--------|-----------|-------------------|--------------------
1  | temp/1.jpg | carro  | 0.92      | 145               | 2025-11-15 10:30:00
2  | temp/2.jpg | moeda  | 0.88      | 152               | 2025-11-15 10:31:00
```

---

### Tabela: model_metrics

Métricas dos modelos treinados:

```sql
SELECT * FROM model_metrics;

id | model_version | accuracy | precision | recall | total_classes
---|---------------|----------|-----------|--------|---------------
1  | v2_20251115   | 0.94     | 0.92      | 0.93   | 50
```

---

## 📊 Performance

| Métrica | Valor |
|---------|-------|
| Tempo de inferência | 100-200ms |
| Tempo de busca FAISS (k=5) | 20-50ms |
| **Tempo total** | **150-350ms** |
| Throughput | ~5-10 requisições/seg |
| Memória modelo | 200-300MB |
| Memória FAISS | 100-200MB |

---

## 🐛 Troubleshooting

### Erro: Model not found

```bash
# Verifique se os arquivos existem
ls -la models/v2/

# Baixe do MinIO
python -c "from minio_handler import download_model; download_model()"
```

---

### Erro: PostgreSQL connection failed

```bash
# Verifique credenciais
psql -h localhost -U OColecionadorUser -d classifier_db

# Ou execute migrações
psql -h localhost -U OColecionadorUser -d classifier_db < init_db.sql
```

---

### Erro: Out of memory

```bash
# Reduza batch size em .env
BATCH_SIZE=16

# Ou execute com GPU
# Instale tensorflow-gpu e configure CUDA
```

---

## 🚀 Deployment

### Docker Compose

```yaml
classifier:
  build: ./OColecionadorClassifier
  ports:
    - "5001:5001"
  environment:
    - MODEL_PATH=./models/v2/model.h5
    - DB_HOST=postgres
  volumes:
    - ./models:/app/models
  depends_on:
    - postgres
```

---

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: classifier
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: classifier
        image: ocolecionador/classifier:latest
        ports:
        - containerPort: 5001
        env:
        - name: MODEL_VERSION
          value: "v2_20251115"
        resources:
          limits:
            memory: "2Gi"
          requests:
            memory: "1Gi"
```

---

## 📚 Documentação Adicional

- [TensorFlow Documentation](https://www.tensorflow.org/api_docs)
- [MobileNetV2 Paper](https://arxiv.org/abs/1801.04381)
- [FAISS Documentation](https://faiss.ai/)
- [Flask API](https://flask.palletsprojects.com/)

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