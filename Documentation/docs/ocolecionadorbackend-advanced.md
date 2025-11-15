---
id: ocolecionadorbackend-advanced
title: OColecionadorBackEnd - Fluxos Avançados
sidebar_label: Avançado
---

# OColecionadorBackEnd - Fluxos Avançados

Este documento detalha os fluxos mais complexos envolvendo múltiplos serviços, bancos de dados e fila de mensagens.

---

## 🔄 Fluxo 1: Pipeline Completo Upload → Augmentations → Training

```mermaid
sequenceDiagram
    autonumber
    participant Mobile as 📱 App Mobile
    participant Backend as 🔌 Backend API
    participant MinIO as 📦 MinIO Storage
    participant SQLServer as 💾 SQL Server
    participant RabbitMQ as 📨 RabbitMQ
    participant Augmentations as 🎨 Augmentations
    participant PostgreSQL as 🗄️ PostgreSQL
    participant Training as 🧠 Training Service

    Mobile->>Backend: POST /api/Items (FormData com foto)
    Backend->>Backend: Valida token OAuth
    Backend->>MinIO: UploadFile(bucket: original, path: item/{itemId}/original.jpg)
    MinIO-->>Backend: { url, etag }
    Backend->>SQLServer: INSERT INTO Fotos (ItemId, Caminho, CreatedAt)
    SQLServer-->>Backend: { fotoId }
    Backend->>RabbitMQ: PublishMessage('ImageAugmentations', { itemId, fotoCaminho, categoria })
    Backend-->>Mobile: { success: true, itemId, fotoId }

    RabbitMQ->>Augmentations: ConsumeMessage('ImageAugmentations')
    Augmentations->>Augmentations: Conecta ao PostgreSQL
    Augmentations->>MinIO: DownloadFile(bucket: original, path: item/{itemId}/original.jpg)
    MinIO-->>Augmentations: Stream de imagem
    
    Augmentations->>Augmentations: Aplica augmentations:<br/>- Rotação (90°, 180°, 270°)<br/>- Flip horizontal/vertical<br/>- Ajuste de brilho/contraste<br/>- Crop central<br/>- Mudança de cor/saturação

    loop Para cada variação
        Augmentations->>Augmentations: Gera nova imagem
        Augmentations->>MinIO: UploadFile(bucket: processed, path: training/{categoria}/{variacao}.jpg)
        Augmentations->>PostgreSQL: INSERT INTO AugmentationMetadata
    end

    Augmentations->>RabbitMQ: PublishMessage('ModelTraining', { batchId, totalImages })
    
    RabbitMQ->>Training: ConsumeMessage('ModelTraining')
    Training->>Training: Conecta ao PostgreSQL
    Training->>Training: Consulta todas as imagens processadas
    Training->>MinIO: DownloadFile(bucket: processed, path: training/{categoria}/*.jpg)
    MinIO-->>Training: Stream de múltiplas imagens
    
    Training->>Training: Pré-processamento:<br/>- Redimensiona para 224x224<br/>- Normaliza valores de pixel<br/>- Cria splits train/val/test<br/>- Calcula augmentation stats

    Training->>Training: Treina modelo TensorFlow:<br/>- Transfer Learning (MobileNetV2)<br/>- Otimizador Adam<br/>- Loss: categorical_crossentropy<br/>- Epochs: 100<br/>- Early stopping

    Training->>Training: Gera embeddings com FAISS:<br/>- Extrai features de layer penúltimo<br/>- Cria índice FAISS<br/>- Salva para busca de similaridade

    Training->>MinIO: UploadFile(bucket: models, path: models/v{timestamp}/model.h5)
    Training->>MinIO: UploadFile(bucket: models, path: models/v{timestamp}/embeddings.faiss)
    Training->>PostgreSQL: INSERT INTO ModelMetrics<br/>(accuracy, loss, val_accuracy, timestamp)
    Training->>Backend: POST /api/UpdateModelVersion { modelPath, embeddings }
    Backend->>SQLServer: UPDATE Models SET CurrentVersion = v{timestamp}
```

---

## 🎯 Fluxo 2: Classificação com Busca de Similaridade

```mermaid
sequenceDiagram
    autonumber
    participant Mobile as 📱 App Mobile
    participant Backend as 🔌 Backend API
    participant MinIO as 📦 MinIO Storage
    participant SQLServer as 💾 SQL Server
    participant Classifier as 🤖 Classifier API
    participant FAISS as 🔍 FAISS Index

    Mobile->>Backend: POST /api/Clasificar (FormData com foto)
    Backend->>Backend: Valida token OAuth
    Backend->>MinIO: UploadFile(bucket: temp, path: uploads/{timestamp}.jpg)
    MinIO-->>Backend: { path }
    Backend->>SQLServer: INSERT INTO TemporaryUpload (Path, Timestamp)
    
    Backend->>Classifier: POST /classify { imagePath: 'uploads/{timestamp}.jpg' }
    Classifier->>MinIO: DownloadFile(bucket: temp, path: uploads/{timestamp}.jpg)
    MinIO-->>Classifier: Imagem bytes
    
    Classifier->>Classifier: Pré-processamento:<br/>- Redimensiona para 224x224<br/>- Normaliza pixel values<br/>- Converte para tensor

    Classifier->>Classifier: Forward pass TensorFlow:<br/>- MobileNetV2 layers<br/>- Output softmax<br/>- Extract embeddings

    Classifier->>Classifier: Classificação:<br/>- Classe: argmax(softmax)<br/>- Confiança: max(softmax)<br/>- Threshold: 0.75

    Classifier->>FAISS: LoadIndex(embeddings.faiss)
    Classifier->>FAISS: Search(query_embedding, k=5)
    FAISS-->>Classifier: { distances, indices }
    
    Classifier->>SQLServer: SELECT TOP 5 Items WHERE Index IN (indices)
    SQLServer-->>Classifier: [{ id, nome, categoria, distancia }]

    Classifier-->>Backend: {<br/>  classe: 'carro',<br/>  confianca: 0.92,<br/>  embedding: [...],<br/>  semelhantes: [<br/>    { itemId: 1, nome: 'Ferrari', distancia: 0.08 },<br/>    { itemId: 2, nome: 'Lamborghini', distancia: 0.12 }<br/>  ]<br/>}

    Backend->>SQLServer: INSERT INTO Classifications<br/>(ImagePath, Classe, Confianca, Timestamp)
    Backend->>SQLServer: UPDATE TemporaryUpload SET Classified = 1
    Backend-->>Mobile: {<br/>  classe: 'carro',<br/>  confianca: '92%',<br/>  itemsSemelhantes: [<br/>    { id: 1, nome: 'Ferrari', foto: 'https://...' },<br/>    { id: 2, nome: 'Lamborghini', foto: 'https://...' }<br/>  ]<br/>}
```

---

## 🐳 Fluxo 3: Orquestração de Containers Docker

```mermaid
sequenceDiagram
    autonumber
    participant Frontend as 🌐 Frontend React
    participant Backend as 🔌 Backend API
    participant DockerSocket as 🔌 Docker Socket
    participant DockerDaemon as 🐳 Docker Daemon
    participant Container as 🎯 Container Process

    Frontend->>Frontend: Admin clica em "Start Training"
    Frontend->>Backend: GET /api/Docker (listar containers)
    Backend->>DockerSocket: docker.Containers.ListContainersAsync()
    DockerSocket->>DockerDaemon: GET /containers/json?all=true
    DockerDaemon-->>DockerSocket: [{ Id, Names, State, Status, Image }]
    DockerSocket-->>Backend: ContainerListResponse[]
    Backend-->>Frontend: [{<br/>  id: 'abc123...',<br/>  names: ['/ocolecionadortraining'],<br/>  state: 'exited',<br/>  status: 'Exited (0)',<br/>  image: 'ocolecionadortraining:latest'<br/>}]

    Frontend->>Frontend: Renderiza botão "Start"
    Frontend->>Backend: POST /api/Docker/start/abc123
    Backend->>Backend: Valida token OAuth
    Backend->>DockerSocket: docker.Containers.StartContainerAsync(containerId)
    DockerSocket->>DockerDaemon: POST /containers/{id}/start
    DockerDaemon->>Container: SIGTERM+SIGKILL → docker run
    Container->>Container: Inicializa processo Python
    
    DockerDaemon-->>DockerSocket: { StatusCode: 204 } ✓
    DockerSocket-->>Backend: { Status: 204 }
    Backend-->>Frontend: { success: true, status: 'running' }
    
    Frontend->>Frontend: Atualiza UI → "Running"

    Container->>Container: python main.py (Training)
    Container->>Container: [*] Aguardando mensagens RabbitMQ...
    Container->>RabbitMQ: Conecta ao broker
    Container->>Container: Consome filas ImageAugmentations

    alt Container recebe sinal
        Frontend->>Backend: POST /api/Docker/stop/abc123
        Backend->>DockerSocket: docker.Containers.StopContainerAsync(containerId)
        DockerSocket->>DockerDaemon: POST /containers/{id}/stop?t=10
        DockerDaemon->>Container: SIGTERM (10s timeout)
        Container->>Container: Cleanup (salva modelo)
        DockerDaemon->>Container: SIGKILL
        Container->>Container: ❌ Encerrado
    else
        Container->>Container: Completa treinamento com sucesso
        Container->>MinIO: Salva modelo
        Container->>PostgreSQL: Salva métricas
        Container->>Container: exit(0)
    end
```

---

## 📊 Fluxo 4: Get Items com Presigned URLs do MinIO

```mermaid
sequenceDiagram
    autonumber
    participant Frontend as 🌐 Frontend React
    participant Backend as 🔌 Backend API
    participant SQLServer as 💾 SQL Server
    participant MinIO as 📦 MinIO

    Frontend->>Backend: GET /api/Items
    Backend->>Backend: Valida token OAuth
    Backend->>SQLServer: SELECT * FROM Items<br/>INCLUDE(Fotos)<br/>INCLUDE(Categoria)

    SQLServer-->>Backend: [{<br/>  id: 1,<br/>  nome: 'Ferrari 250',<br/>  categoriaId: 1,<br/>  fotos: [{<br/>    id: 1,<br/>    caminho: 'item/1/original.jpg'<br/>  }]<br/>}]

    Backend->>Backend: Para cada item:
    Backend->>Backend: Para cada foto:

    loop Para cada Foto
        Backend->>MinIO: GetPresignedUrlAsync(bucket: original, path: item/1/original.jpg)
        MinIO-->>Backend: URL com assinatura temporária:<br/>https://minio:9000/original/item/1/original.jpg?<br/>X-Amz-Algorithm=...&<br/>X-Amz-Credential=...&<br/>X-Amz-Date=...&<br/>X-Amz-Expires=3600&<br/>X-Amz-Signature=...
    end

    Backend-->>Frontend: [{<br/>  id: 1,<br/>  nome: 'Ferrari 250',<br/>  categoriaId: 1,<br/>  fotos: [<br/>    'https://minio.../item/1/original.jpg?X-Amz-...'<br/>  ]<br/>}]

    Frontend->>Frontend: Renderiza lista de itens
    Frontend->>MinIO: GET presigned_url (download automático)
    MinIO-->>Frontend: Imagem JPEG/PNG
    Frontend->>Frontend: Exibe miniatura
```

---

## 🔐 Fluxo 5: Autenticação OAuth2 com Token Validation

```mermaid
sequenceDiagram
    autonumber
    participant Mobile as 📱 App Mobile
    participant Frontend as 🌐 Frontend React
    participant Backend as 🔌 Backend API
    participant GoogleOAuth as 🔑 Google OAuth
    participant GitHubOAuth as 🔑 GitHub OAuth

    Mobile->>GoogleOAuth: 1️⃣ Abre Google Login
    GoogleOAuth->>Mobile: Formulário de login
    Mobile->>GoogleOAuth: Credenciais do usuário
    GoogleOAuth-->>Mobile: authorization_code
    Mobile->>Backend: POST /api/auth/callback?code=...&provider=google
    
    Backend->>Backend: Valida state (CSRF)
    Backend->>GoogleOAuth: POST /token { code, client_id, client_secret }
    GoogleOAuth-->>Backend: {<br/>  access_token: 'ya29...',<br/>  token_type: 'Bearer',<br/>  expires_in: 3600<br/>}
    
    Backend->>GoogleOAuth: GET /userinfo (using access_token)
    GoogleOAuth-->>Backend: {<br/>  id: '123456789',<br/>  email: 'user@gmail.com',<br/>  name: 'João Silva',<br/>  picture: 'https://...'<br/>}

    Backend->>SQLServer: SELECT * FROM Users WHERE ExternalId = '123456789'
    alt User não existe
        SQLServer-->>Backend: null
        Backend->>SQLServer: INSERT INTO Users (ExternalId, Email, Name, Provider)
    else User existe
        SQLServer-->>Backend: User record
    end

    Backend->>Backend: Gera JWT token:<br/>- Header: { typ: 'JWT', alg: 'HS256' }<br/>- Payload: { sub: userId, email, provider }<br/>- Signature: HMAC-SHA256(secret)

    Backend-->>Mobile: {<br/>  token: 'eyJhbGciOiJIUzI1NiIs...',<br/>  provider: 'google',<br/>  user: { name, email, picture }<br/>}

    Mobile->>Mobile: localStorage.setItem('token', 'google_OC_eyJ...')
    Mobile->>Mobile: Redireciona para Dashboard

    alt Próxima requisição
        Mobile->>Backend: GET /api/Items<br/>Header: Authorization: Bearer eyJ...
        Backend->>OAuthMiddleware: Valida token
        OAuthMiddleware->>OAuthMiddleware: Decodifica JWT<br/>- Verifica assinatura<br/>- Valida expiration<br/>- Extrai claims
        OAuthMiddleware-->>Backend: { userId, provider, claims }
        Backend->>SQLServer: SELECT * FROM Users WHERE Id = userId
        Backend->>Backend: Executa operação autorizada
    end
```

---

## ⚠️ Tratamento de Erros e Retry Logic

```mermaid
sequenceDiagram
    autonumber
    participant Backend as 🔌 Backend API
    participant RabbitMQ as 📨 RabbitMQ
    participant Augmentations as 🎨 Augmentations
    participant MinIO as 📦 MinIO

    Backend->>RabbitMQ: PublishMessage('ImageAugmentations', msg)
    RabbitMQ-->>Backend: Message enqueued
    
    RabbitMQ->>Augmentations: Delivery 1
    Augmentations->>MinIO: DownloadFile (Tentativa 1)
    MinIO-->>Augmentations: ❌ Connection timeout
    Augmentations->>Augmentations: Log erro: "MinIO timeout"
    Augmentations->>RabbitMQ: NACK (requeue=true)
    
    RabbitMQ->>RabbitMQ: Aguarda 5s
    RabbitMQ->>Augmentations: Delivery 2 (Tentativa 2)
    Augmentations->>MinIO: DownloadFile (Tentativa 2)
    MinIO-->>Augmentations: ❌ Access denied (credenciais)
    Augmentations->>Augmentations: Log erro: "MinIO auth failed"
    Augmentations->>RabbitMQ: NACK (requeue=false)
    
    RabbitMQ->>RabbitMQ: Move para Dead Letter Queue
    Backend->>RabbitMQ: Monitora DLQ
    Backend->>Backend: Alert: Message failed 3x
    Backend->>SQLServer: INSERT INTO ErrorLog (msg, reason, timestamp)
    Backend->>Monitoring: Sentry.captureException()
```

---

## 📈 Diagram de Carga: Múltiplas Requisições Simultâneas

```mermaid
graph TB
    subgraph Users["👥 Múltiplos Usuários"]
        U1["User 1"]
        U2["User 2"]
        U3["User 3"]
        U4["User 4"]
    end

    subgraph LoadBalancer["⚖️ Load Balancer / Reverse Proxy"]
        LB["Nginx"]
    end

    subgraph BackendPool["🔌 Backend Pool"]
        BE1["Instance 1<br/>Port 5000"]
        BE2["Instance 2<br/>Port 5001"]
        BE3["Instance 3<br/>Port 5002"]
    end

    subgraph Database["💾 Data Layer"]
        SQLServer["SQL Server<br/>Connection Pool"]
        Cache["Redis<br/>Cache"]
    end

    subgraph Services["📦 External Services"]
        MinIO["MinIO"]
        RabbitMQ["RabbitMQ"]
    end

    U1 -->|POST /Items| LB
    U2 -->|GET /Items| LB
    U3 -->|POST /Clasificar| LB
    U4 -->|GET /Docker| LB

    LB -->|Round Robin| BE1
    LB -->|Round Robin| BE2
    LB -->|Round Robin| BE3

    BE1 -->|Query| SQLServer
    BE2 -->|Query| SQLServer
    BE3 -->|Query| SQLServer

    BE1 -->|GET/SET| Cache
    BE2 -->|GET/SET| Cache
    BE3 -->|GET/SET| Cache

    BE1 -->|Upload/Download| MinIO
    BE2 -->|Upload/Download| MinIO
    BE3 -->|Upload/Download| MinIO

    BE1 -->|Publish| RabbitMQ
    BE2 -->|Publish| RabbitMQ
    BE3 -->|Publish| RabbitMQ

    style Users fill:#e1f5ff
    style LoadBalancer fill:#fff3e0
    style BackendPool fill:#f3e5f5
    style Database fill:#e8f5e9
    style Services fill:#fce4ec
```

---

## 🎯 Conclusão

Os fluxos acima ilustram a complexidade da orquestração entre:

✅ **Frontend/Mobile** – Interfaces do usuário  
✅ **Backend .NET** – Lógica central  
✅ **SQL Server + PostgreSQL** – Persistência  
✅ **MinIO** – Storage distribuído  
✅ **RabbitMQ** – Fila assíncrona  
✅ **Serviços de IA** – Classificação e treinamento  
✅ **Docker API** – Orquestração de containers  

O sistema foi projetado com **resiliência, escalabilidade e observabilidade** em mente.