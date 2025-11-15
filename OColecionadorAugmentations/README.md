# OColecionadorAugmentations 🎨

## 📋 O que é?

O **OColecionadorAugmentations** é um serviço Python que funciona como um **processador de imagens em background**. Ele:

- 📨 **Escuta fila RabbitMQ** – Consome mensagens de novos uploads
- 📥 **Baixa imagens** do MinIO
- 🎨 **Aplica 9 transformações** (rotação, flip, brilho, contraste, crop, blur, HSV)
- 📤 **Salva variações** no MinIO (bucket: processed)
- 💾 **Registra metadados** no PostgreSQL
- 🔄 **Reprocessa falhas** com retry automático

**Propósito:** Gerar **dataset aumentado** para treinar modelos de classificação com mais robustez.

---

## 🔄 Como Funciona?

```
1. Usuário faz upload de foto no app mobile
   ↓
2. Backend publica mensagem no RabbitMQ
   ↓
3. Augmentations consome mensagem
   ↓
4. Baixa imagem original do MinIO
   ↓
5. Aplica 9 transformações (rotação, flip, brilho...)
   ↓
6. Salva 9 variações no MinIO
   ↓
7. Registra no PostgreSQL
   ↓
8. Publica para fila ModelTraining (treino da IA)
```

---

## 🏗️ Stack Tecnológico

| Tecnologia | Versão | Propósito |
|-----------|--------|----------|
| **Python** | 3.11+ | Linguagem principal |
| **RabbitMQ** | 3 | Consumo de fila |
| **MinIO** | Latest | Storage S3 |
| **PostgreSQL** | 14+ | Banco de dados |
| **OpenCV** | 4.8+ | Processamento de imagens |
| **Pillow** | 10.1+ | Manipulação de fotos |
| **NumPy** | 1.24+ | Computação numérica |
| **Docker** | Latest | Containerização |

---

## 🚀 Quick Start

### Pré-requisitos

- Python 3.11+ instalado
- RabbitMQ rodando
- MinIO rodando
- PostgreSQL rodando

### Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/PatrickCalorioCarvalho/OColecionador.git
cd OColecionador/OColecionadorAugmentations

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
psql -h localhost -U OColecionadorUser -d augmentations_db < init_db.sql

# 6. Execute o serviço
python main.py
```

**Output esperado:**
```
[*] Aguardando mensagens...
[*] Conectado a RabbitMQ
[*] Conectado a PostgreSQL
[*] Aguardando mensagens na fila 'ImageAugmentations'
```

---

### Com Docker Compose (Recomendado)

```bash
cd OColecionador/
docker compose up ocolecionadoraugmentations
```

---

## 📁 Estrutura de Projeto

```
OColecionadorAugmentations/
├── main.py                    # Ponto de entrada
├── requirements.txt           # Dependências
├── Dockerfile                 # Imagem Docker
├── init_db.sql               # Schema PostgreSQL
├── .env.example              # Exemplo de configuração
└── [módulos esperados]
    ├── config.py             # Configurações centralizadas
    ├── rabbitmq_consumer.py  # Consumer RabbitMQ
    ├── minio_handler.py      # Handler MinIO
    ├── augmentations.py      # Funções de transformação
    ├── database.py           # Conexão PostgreSQL
    └── logger.py             # Logging
```

---

## ⚙️ Configuração

### .env

```bash
# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=OColecionadorUser
RABBITMQ_PASSWORD=OColecionador@2025
RABBITMQ_QUEUE=ImageAugmentations

# MinIO
MINIO_HOST=localhost
MINIO_PORT=9000
MINIO_ACCESS_KEY=OColecionadorUser
MINIO_SECRET_KEY=OColecionador@2025
MINIO_BUCKET_ORIGINAL=ocolecionadorbucket-original
MINIO_BUCKET_PROCESSED=ocolecionadorbucket-processed

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=augmentations_db
DB_USER=OColecionadorUser
DB_PASSWORD=OColecionador@2025

# Logging
LOG_LEVEL=INFO
LOG_FILE=./augmentations.log

# Augmentations
AUGMENTATION_COUNT=9
```

---

## 🎨 Transformações Aplicadas

Cada imagem original gera **9 variações**:

| # | Tipo | Descrição |
|---|------|-----------|
| 1 | **Rotado 90°** | Rotação 90° horária |
| 2 | **Rotado 180°** | Rotação 180° |
| 3 | **Rotado 270°** | Rotação 270° horária |
| 4 | **Flip Horizontal** | Espelha eixo Y |
| 5 | **Flip Vertical** | Espelha eixo X |
| 6 | **Brilho ↑** | Aumenta intensidade 20% |
| 7 | **Brilho ↓** | Diminui intensidade 20% |
| 8 | **Blur Gaussiano** | Desfoque para robustez |
| 9 | **CLAHE** | Contraste adaptativo |

---

### Exemplo Visual

```
Original: ferrari.jpg
    ↓
├─ ferrari_rotated_90.jpg
├─ ferrari_rotated_180.jpg
├─ ferrari_rotated_270.jpg
├─ ferrari_flipped_h.jpg
├─ ferrari_flipped_v.jpg
├─ ferrari_brightness_up.jpg
├─ ferrari_brightness_down.jpg
├─ ferrari_blur.jpg
└─ ferrari_clahe.jpg
```

---

## 📨 Fluxo de Mensagens

### Consumo (Input)

**Fila:** `ImageAugmentations`

```json
{
  "itemId": 12345,
  "fotoCaminho": "item/12345/original.jpg",
  "categoria": "carros",
  "uploadedAt": "2025-11-15T10:30:00Z"
}
```

### Publicação (Output)

**Fila:** `ModelTraining`

```json
{
  "itemId": 12345,
  "categoria": "carros",
  "totalAugmentacoes": 9,
  "variações": [
    "training/carros/12345_rotated_90.jpg",
    "training/carros/12345_flipped_h.jpg",
    ...
  ],
  "status": "success",
  "processedAt": "2025-11-15T10:32:00Z"
}
```

---

## 🗄️ Banco de Dados

### Tabela: augmentation_jobs

Rastreia trabalhos de augmentação:

```sql
SELECT * FROM augmentation_jobs;

id | item_id | categoria | status    | attempts | created_at
---|---------|-----------|-----------|----------|--------------------
1  | 12345   | carros    | success   | 1        | 2025-11-15 10:30:00
2  | 12346   | moedas    | processing| 0        | 2025-11-15 10:31:00
3  | 12347   | animais   | failed    | 3        | 2025-11-15 10:32:00
```

---

### Tabela: augmentation_results

Armazena resultados de cada transformação:

```sql
SELECT * FROM augmentation_results;

id | job_id | variation_type  | output_path                          | file_size
---|--------|-----------------|--------------------------------------|----------
1  | 1      | rotated_90      | training/carros/12345_rotated_90.jpg | 45230
2  | 1      | flipped_h       | training/carros/12345_flipped_h.jpg  | 42100
3  | 1      | brightness_up   | training/carros/12345_brightness.jpg | 48900
```

---

## 📊 Monitoramento

### Logs

```bash
# Ver logs em tempo real
tail -f augmentations.log

# Exemplo de log
[2025-11-15 10:30:15] INFO    | Mensagem consumida: itemId=12345
[2025-11-15 10:30:16] INFO    | Baixando imagem de MinIO
[2025-11-15 10:30:17] INFO    | Aplicando 9 augmentations
[2025-11-15 10:30:19] INFO    | Upload de 9 variações concluído
[2025-11-15 10:30:20] INFO    | Metadados salvos no PostgreSQL
[2025-11-15 10:30:20] INFO    | ✓ Item 12345 processado com sucesso
```

---

## 🔄 Retry Logic

Se um item falhar no processamento:

```
Tentativa 1: Falha → Aguarda 5s → Requeue
Tentativa 2: Falha → Aguarda 10s → Requeue
Tentativa 3: Falha → Aguarda 20s → Requeue
Tentativa 4: Falha → Move para Dead Letter Queue
```

Monitor verifica DLQ e notifica Backend para alerta.

---

## 📈 Performance

- **Tempo por item:** 2-5 segundos
- **Tamanho saída:** 1 imagem → 9 imagens
- **Taxa:** ~1000-2000 itens/hora (1 container)
- **Escalabilidade:** Múltiplos containers consumem mesma fila

---

## 🐛 Troubleshooting

### Erro: Connection refused (RabbitMQ)

```bash
# Verifique se RabbitMQ está rodando
docker ps | grep rabbitmq

# Ou inicie com Docker Compose
docker compose up rabbitmq
```

---

### Erro: Access denied (MinIO)

```bash
# Verifique credenciais em .env
echo $MINIO_ACCESS_KEY
echo $MINIO_SECRET_KEY

# Teste conexão
python -c "from minio import Minio; Minio('localhost:9000', '...', '...')"
```

---

### Erro: PostgreSQL connection failed

```bash
# Verifique se PostgreSQL está rodando
docker ps | grep postgres

# Teste conexão
psql -h localhost -U OColecionadorUser -d augmentations_db
```

---

## 🚀 Deployment

### Docker Compose

```yaml
# docker-compose.yml
augmentations:
  build: ./OColecionadorAugmentations
  environment:
    - RABBITMQ_HOST=rabbitmq
    - MINIO_HOST=minio
    - DB_HOST=postgres
  depends_on:
    - rabbitmq
    - minio
    - postgres
  deploy:
    replicas: 3  # Escalabilidade
    resources:
      limits:
        memory: 1G
```

---

### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: augmentations
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: augmentations
        image: ocolecionador/augmentations:latest
        env:
        - name: RABBITMQ_HOST
          value: "rabbitmq-service"
        - name: MINIO_HOST
          value: "minio-service"
        resources:
          limits:
            memory: "1Gi"
          requests:
            memory: "512Mi"
```

---

## 📚 Documentação Adicional

- [RabbitMQ Tutorial Python](https://www.rabbitmq.com/tutorials/tutorial-one-python.html)
- [MinIO Python SDK](https://min.io/docs/python/API.html)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Albumentations](https://albumentations.ai/)

---

## 👨‍💻 Contribuição

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/Nova-Augmentation`)
3. Commit suas mudanças
4. Push e abra Pull Request

---

## 📄 Licença

Este projeto é open source. Veja [LICENSE](../../LICENSE) para detalhes.

---

## 👤 Autor

**Patrick Calorio Carvalho**  
📧 [Email](mailto:patrick@example.com) • 🔗 [GitHub](https://github.com/PatrickCalorioCarvalho)

---

## 📞 Suporte

- 📝 [GitHub Issues](https://github.com/PatrickCalorioCarvalho/OColecionador/issues)
- 💬 [Discussões](https://github.com/PatrickCalorioCarvalho/OColecionador/discussions)