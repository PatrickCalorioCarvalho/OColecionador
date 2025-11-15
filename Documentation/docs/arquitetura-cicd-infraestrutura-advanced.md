---
id: arquitetura-cicd-infraestrutura-advanced
title: Arquitetura, CI/CD e Infraestrutura - Fluxos Avançados
sidebar_label: Avançado
---

# 🏗️ Arquitetura, CI/CD e Infraestrutura - Fluxos Avançados

Documentação completa sobre como o projeto está estruturado, como funciona o CI/CD e como é feito o acesso externo.

---

## 📋 Visão Geral da Infraestrutura

```mermaid
graph TB
    subgraph External["🌍 Acesso Externo"]
        ngrok["🔗 ngrok<br/>Tunneling"]
        domain["🌐 Domain<br/>louse-model-lioness.ngrok-free.app"]
    end

    subgraph CI["🔄 CI/CD"]
        github["🐙 GitHub<br/>Repository"]
        actions["⚙️ GitHub Actions<br/>Workflows"]
        selfhosted["🖥️ Self-Hosted Runner<br/>Runner Linux"]
    end

    subgraph LocalServer["🏠 LocalServer"]
        env_file[".env<br/>Configurações"]
        nginx["🔌 Nginx<br/>Reverse Proxy"]
        glitchtip["🐛 GlitchTip<br/>Error Tracking"]
        portainer["📊 Portainer<br/>Container Mgmt"]
        metabase["📈 Metabase<br/>BI Dashboard"]
    end

    subgraph Containers["🐳 Containers Docker"]
        sqlserver["💾 SQL Server<br/>Banco Principal"]
        postgres["🗄️ PostgreSQL<br/>Augmentations DB"]
        redis["⚡ Redis<br/>Cache"]
        minio["📦 MinIO<br/>S3-Compatible"]
        rabbitmq["📨 RabbitMQ<br/>Message Broker"]
    end

    subgraph Services["🔌 Serviços Aplicação"]
        backend["🔌 Backend API<br/>.NET 8<br/>Port 5000"]
        frontend["🌐 Frontend<br/>React<br/>Port 5002"]
        mobile["📱 Mobile<br/>React Native<br/>EAS Build"]
    end

    subgraph ML["🤖 Serviços IA"]
        augmentations["🎨 Augmentations<br/>Python<br/>GPU"]
        training["🧠 Training<br/>TensorFlow<br/>GPU"]
        classifier["🤖 Classifier<br/>FastAPI<br/>Port 5001"]
    end

    External --> nginx
    CI --> selfhosted
    github --> actions
    actions --> selfhosted

    nginx --> backend
    nginx --> frontend
    
    backend --> sqlserver
    backend --> minio
    backend --> rabbitmq
    backend --> redis
    
    frontend --> backend
    mobile --> backend
    
    rabbitmq --> augmentations
    augmentations --> postgres
    augmentations --> minio
    
    rabbitmq --> training
    training --> postgres
    training --> minio
    
    classifier --> postgres
    classifier --> minio
    
    glitchtip --> postgres
    metabase --> sqlserver
    portainer --> Containers
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

```
.github/workflows/
├── BuildExpoReactNativeAPK.yml    # Build do app mobile
├── DeployDockerHub.yml             # Push de imagens
└── SelfHostedDockerCompose.yml     # Build local com Docker Compose
```

---

### Fluxo 1: Build Expo React Native APK

```mermaid
graph LR
    A["📱 Push para main/develop"] --> B["🚀 GitHub Actions<br/>BuildExpoReactNativeAPK"]
    B --> C["📥 Checkout código"]
    C --> D["⚙️ Setup Node.js"]
    D --> E["📦 npm install"]
    E --> F["🔨 eas build<br/>--platform android<br/>--build-profile preview"]
    F --> G["📱 APK gerado"]
    G --> H["📤 Upload artifact"]
    H --> I["🎉 Pronto para teste"]

    style A fill:#e1f5ff
    style B fill:#fff3e0
    style I fill:#c8e6c9
```

**Arquivo:** `.github/workflows/BuildExpoReactNativeAPK.yml`

```yaml
name: Build Expo React Native APK

on:
  push:
    branches:
      - main
      - develop
    paths:
      - 'OColecionadorMobile/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        working-directory: OColecionadorMobile
        run: npm install

      - name: Build APK with EAS
        working-directory: OColecionadorMobile
        run: |
          npm install -g eas-cli
          eas build \
            --platform android \
            --build-profile preview \
            --non-interactive

      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: app-preview.apk
          path: OColecionadorMobile/build/
```

---

### Fluxo 2: Deploy Docker Hub

```mermaid
graph LR
    A["🐳 Docker Push Trigger"] --> B["🚀 DeployDockerHub"]
    B --> C["🔐 Docker Login"]
    C --> D["🔨 Build Images"]
    D --> E["backend:latest"]
    D --> F["frontend:latest"]
    D --> G["augmentations:latest"]
    E --> H["📤 Push to Hub"]
    F --> H
    G --> H
    H --> I["🐳 patrickcaloriocarvalho/<br/>ocolecionador-*"]

    style A fill:#fce4ec
    style I fill:#e0f2f1
```

**Arquivo:** `.github/workflows/DeployDockerHub.yml`

```yaml
name: Deploy Docker Hub

on:
  push:
    branches:
      - main
    paths:
      - 'OColecionadorBackEnd/**'
      - 'OColecionadorFrontEnd/**'
      - 'OColecionadorAugmentations/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Backend
        uses: docker/build-push-action@v4
        with:
          context: OColecionadorBackEnd
          push: true
          tags: |
            patrickcaloriocarvalho/ocolecionador-backend:latest
            patrickcaloriocarvalho/ocolecionador-backend:${{ github.sha }}

      - name: Build and push Frontend
        uses: docker/build-push-action@v4
        with:
          context: OColecionadorFrontEnd
          push: true
          tags: |
            patrickcaloriocarvalho/ocolecionador-frontend:latest
            patrickcaloriocarvalho/ocolecionador-frontend:${{ github.sha }}

      - name: Build and push Augmentations
        uses: docker/build-push-action@v4
        with:
          context: OColecionadorAugmentations
          push: true
          tags: |
            patrickcaloriocarvalho/ocolecionador-augmentations:latest
            patrickcaloriocarvalho/ocolecionador-augmentations:${{ github.sha }}
```

---

### Fluxo 3: Self-Hosted Docker Compose

```mermaid
sequenceDiagram
    participant GitHub as 🐙 GitHub
    participant Actions as ⚙️ GitHub Actions
    participant Runner as 🖥️ Self-Hosted Runner
    participant Docker as 🐳 Docker Daemon
    participant Services as 🔌 Serviços

    GitHub->>Actions: Push PR detectado
    Actions->>Runner: Dispatch workflow
    Runner->>Runner: Checkout código
    Runner->>Runner: Setup variáveis .env
    Runner->>Docker: docker compose up --build
    Docker->>Services: Inicia todos os containers
    Services->>Docker: Health checks
    Docker->>Runner: ✓ Tudo pronto
    Runner->>Actions: Workflow concluído
    Actions->>GitHub: Status check ✓
```

**Arquivo:** `.github/workflows/SelfHostedDockerCompose.yml`

```yaml
name: Self Hosted Docker Compose

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  docker-compose:
    runs-on: self-hosted  # Executa na máquina local
    steps:
      - name: Checkout do código
        uses: actions/checkout@v4

      - name: Setup variáveis de ambiente
        run: |
          cat > .env << EOF
          OC_AUTH_USER=${{ secrets.OC_AUTH_USER }}
          OC_AUTH_PASSWORD=${{ secrets.OC_AUTH_PASSWORD }}
          OC_GITHUB_CLIENT_ID=${{ secrets.OC_GITHUB_CLIENT_ID }}
          OC_GITHUB_CLIENT_SECRET=${{ secrets.OC_GITHUB_CLIENT_SECRET }}
          OC_GOOGLE_CLIENT_ID=${{ secrets.OC_GOOGLE_CLIENT_ID }}
          OC_GOOGLE_CLIENT_SECRET=${{ secrets.OC_GOOGLE_CLIENT_SECRET }}
          OC_NGROK_TOKEN=${{ secrets.OC_NGROK_TOKEN }}
          EOF

      - name: Rodar Docker Compose
        run: |
          docker compose up -d --build --force-recreate

      - name: Health checks
        run: |
          sleep 10
          curl -f http://localhost:5000/api/health || exit 1
          curl -f http://localhost:5002/health || exit 1

      - name: Logs de erro
        if: failure()
        run: |
          docker compose logs --tail=100
          docker compose down
```

---

## 🌍 Acesso Externo via ngrok

### Configuração de Tunneling

```mermaid
graph LR
    A["📱 Usuário Externo<br/>Internet Pública"] --> B["🔗 ngrok Tunnel<br/>louse-model-lioness.ngrok-free.app"]
    B --> C["🔌 Nginx<br/>Reverse Proxy<br/>Port 80/443"]
    C --> D["🌐 Frontend<br/>Port 5002"]
    C --> E["🔌 Backend API<br/>Port 5000"]
    
    style A fill:#ffebee
    style B fill:#fff3cd
    style D fill:#d1ecf1
    style E fill:#d4edda
```

### Arquivo: docker-compose.yml (ngrok)

```yaml
# docker-compose.yml - Serviço ngrok
ngrok:
  image: ngrok/ngrok:latest
  container_name: ngrok
  command:
    - "start"
    - "--all"
    - "--config"
    - "/etc/ngrok.yml"
  ports:
    - "4040:4040"  # ngrok dashboard
  environment:
    NGROK_AUTHTOKEN: ${OC_NGROK_TOKEN}
  volumes:
    - ./LocalServer/ngrok.yml:/etc/ngrok.yml
  depends_on:
    - nginx
  networks:
    - ocolecionador
```

### Configuração ngrok (ngrok.yml)

```yaml
version: "3"
tunnels:
  frontend:
    proto: http
    addr: nginx:80
    domain: "louse-model-lioness.ngrok-free.app"
  
  backend:
    proto: http
    addr: ocolecionadorbackend:5000
    
  classifier:
    proto: http
    addr: ocolecionadorclassifier:5001
```

---

## 🔌 Nginx - Reverse Proxy

### Arquivo: LocalServer/nginx.conf

```nginx
upstream backend {
    server ocolecionadorbackend:5000;
}

upstream frontend {
    server ocolecionadorfrontend:5002;
}

upstream classifier {
    server ocolecionadorclassifier:5001;
}

server {
    listen 80;
    server_name louse-model-lioness.ngrok-free.app;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Classifier API
    location /classifier {
        proxy_pass http://classifier;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
```

---

## 🐳 Docker Compose - Infraestrutura Completa

### Estrutura de Serviços

```yaml
# docker-compose.yml - Overview dos serviços

services:
  # ========== BANCOS DE DADOS ==========
  sqlserver:        # SQL Server 2022 (Backend)
  postgres:         # PostgreSQL (Augmentations, Training, Classifier)
  
  # ========== INFRAESTRUTURA ==========
  redis:            # Cache distribuído
  minio:            # S3-compatible storage
  rabbitmq:         # Message broker
  
  # ========== APLICAÇÃO ==========
  ocolecionadorbackend:        # API .NET 8
  ocolecionadorfrontend:       # React app
  
  # ========== IA / ML ==========
  ocolecionadoraugmentations:  # Augmentations (GPU)
  ocolecionadorclassifier:     # Classificação (FastAPI)
  ocolecionadortraining:       # Treinamento (GPU) - Manual

  # ========== INFRAESTRUTURA LOCAL ==========
  nginx:            # Reverse Proxy
  ngrok:            # Tunneling externo
  
  # ========== MONITORAMENTO / ADMIN ==========
  portainer:        # Docker UI
  metabase:         # BI Dashboard
  glitchtip:        # Error tracking
  glitchtip-worker: # Worker para GlitchTip
```

---

### Exemplo Completo: docker-compose.yml

```yaml
version: '3.8'

services:
  # ========== BANCOS DE DADOS ==========
  
  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    container_name: sqlserver
    environment:
      MSSQL_PID: "Express"
      ACCEPT_EULA: "Y"
      MSSQL_SA_PASSWORD: ${OC_AUTH_PASSWORD}
    ports:
      - "1433:1433"
    volumes:
      - sqlserver_data:/var/opt/mssql
    healthcheck:
      test: /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P ${OC_AUTH_PASSWORD} -Q "SELECT 1"
      interval: 10s
      timeout: 3s
      retries: 10
    networks:
      - ocolecionador

  postgres:
    image: postgres:15
    container_name: postgres
    environment:
      POSTGRES_USER: ${OC_AUTH_USER}
      POSTGRES_PASSWORD: ${OC_AUTH_PASSWORD}
      POSTGRES_DB: OColecionadorAugmentationsDB
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./OColecionadorAugmentations/init_db.sql:/docker-entrypoint-initdb.d/01_init.sql
      - ./LocalServer/init_glitchtip.sql:/docker-entrypoint-initdb.d/02_glitchtip.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${OC_AUTH_USER}"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - ocolecionador

  # ========== INFRAESTRUTURA ==========

  redis:
    image: redis:7
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - ocolecionador

  minio:
    image: minio/minio
    container_name: minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: ${OC_AUTH_USER}
      MINIO_ROOT_PASSWORD: ${OC_AUTH_PASSWORD}
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - ocolecionador

  rabbitmq:
    image: rabbitmq:3-management
    container_name: rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: ${OC_AUTH_USER}
      RABBITMQ_DEFAULT_PASS: ${OC_AUTH_PASSWORD}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - ocolecionador

  # ========== APLICAÇÃO ==========

  ocolecionadorbackend:
    build:
      context: ./OColecionadorBackEnd
      dockerfile: Dockerfile
    container_name: OColecionadorBackEnd
    depends_on:
      sqlserver:
        condition: service_healthy
      minio:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    environment:
      ASPNETCORE_ENVIRONMENT: Production
      DOCKER_URI: "unix:///var/run/docker.sock"
    ports:
      - "5000:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    restart: always
    networks:
      - ocolecionador

  ocolecionadorfrontend:
    build:
      context: ./OColecionadorFrontEnd
      dockerfile: Dockerfile
      args:
        GITHUB_CLIENT_ID: ${OC_GITHUB_CLIENT_ID}
        GOOGLE_CLIENT_ID: ${OC_GOOGLE_CLIENT_ID}
    container_name: OColecionadorFrontEnd
    depends_on:
      - ocolecionadorbackend
    ports:
      - "5002:5002"
    restart: always
    networks:
      - ocolecionador

  # ========== IA / ML ==========

  ocolecionadoraugmentations:
    build: ./OColecionadorAugmentations
    container_name: OColecionadorAugmentations
    runtime: nvidia
    gpus:
      - capabilities: [gpu]
    depends_on:
      postgres:
        condition: service_healthy
      minio:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    environment:
      POSTGRES_HOST: postgres
      MINIO_HOST: minio
      RABBITMQ_HOST: rabbitmq
      CUDA_VISIBLE_DEVICES: "0"
    restart: always
    networks:
      - ocolecionador
    profiles:
      - "automatic"

  ocolecionadorclassifier:
    build: ./OColecionadorClassifier
    container_name: OColecionadorClassifier
    ports:
      - "5001:5001"
    depends_on:
      postgres:
        condition: service_healthy
      minio:
        condition: service_healthy
    environment:
      POSTGRES_HOST: postgres
      MINIO_HOST: minio
      MODEL_PATH: /app/models/v2
    restart: always
    networks:
      - ocolecionador
    profiles:
      - "automatic"

  ocolecionadortraining:
    build: ./OColecionadorTraining
    container_name: OColecionadorTraining
    runtime: nvidia
    gpus:
      - capabilities: [gpu]
    depends_on:
      postgres:
        condition: service_healthy
      minio:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    environment:
      POSTGRES_HOST: postgres
      MINIO_HOST: minio
      RABBITMQ_HOST: rabbitmq
      CUDA_VISIBLE_DEVICES: "0"
    networks:
      - ocolecionador
    profiles:
      - "manual"
    command: /bin/bash -c "while true; do sleep 1000; done"

  # ========== INFRAESTRUTURA LOCAL ==========

  nginx:
    image: nginx:alpine
    container_name: nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./LocalServer/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - ocolecionadorbackend
      - ocolecionadorfrontend
    networks:
      - ocolecionador

  ngrok:
    image: ngrok/ngrok:latest
    container_name: ngrok
    command:
      - "start"
      - "--all"
      - "--config"
      - "/etc/ngrok.yml"
    ports:
      - "4040:4040"
    environment:
      NGROK_AUTHTOKEN: ${OC_NGROK_TOKEN}
    volumes:
      - ./LocalServer/ngrok.yml:/etc/ngrok.yml:ro
    depends_on:
      - nginx
    networks:
      - ocolecionador

  # ========== MONITORAMENTO / ADMIN ==========

  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    ports:
      - "9443:9443"
      - "8000:8000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
    networks:
      - ocolecionador

  metabase:
    image: metabase/metabase:latest
    container_name: metabase
    ports:
      - "3000:3000"
    environment:
      MB_DB_TYPE: postgres
      MB_DB_DBNAME: metabase
      MB_DB_USER: ${OC_AUTH_USER}
      MB_DB_PASS: ${OC_AUTH_PASSWORD}
      MB_DB_HOST: postgres
      MB_DB_PORT: 5432
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - ocolecionador

  glitchtip:
    image: glitchtip/glitchtip:latest
    container_name: glitchtip
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgres://${OC_AUTH_USER}:${OC_AUTH_PASSWORD}@postgres:5432/glitchtip
      SECRET_KEY: ${GLITCHTIP_SECRET_KEY}
      ALLOWED_HOSTS: glitchtip
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - ocolecionador

  glitchtip_worker:
    image: glitchtip/glitchtip:latest
    container_name: glitchtip_worker
    command: celery -A glitchtip_project worker -l info
    environment:
      DATABASE_URL: postgres://${OC_AUTH_USER}:${OC_AUTH_PASSWORD}@postgres:5432/glitchtip
      SECRET_KEY: ${GLITCHTIP_SECRET_KEY}
    depends_on:
      - postgres
      - glitchtip
    networks:
      - ocolecionador

# ========== VOLUMES ==========

volumes:
  sqlserver_data:
  postgres_data:
  minio_data:
  redis_data:
  rabbitmq_data:
  portainer_data:

# ========== NETWORKS ==========

networks:
  ocolecionador:
    driver: bridge
```

---

## 🚀 Execução com Perfis

### Perfil: Automático (Produção)

```bash
# Inicia todos os serviços automáticos
docker compose --profile automatic up -d

# Inclui:
# - Todos os bancos de dados
# - Backend e Frontend
# - Augmentations
# - Classifier
# - Nginx + ngrok
# - Portainer, Metabase, GlitchTip
```

### Perfil: Manual (Desenvolvimento)

```bash
# Inicia apenas serviços base
docker compose --profile manual up -d

# Depois inicia Training manualmente
docker compose start ocolecionadortraining

# Ou executa comandos específicos
docker compose exec ocolecionadortraining python main.py
```

### Todos os Serviços

```bash
# Inicia TUDO (automático + manual)
docker compose up -d
```

---

## 🔐 Variáveis de Ambiente (.env)

```bash
# Arquivo: .env (na raiz do projeto)

# ========== AUTENTICAÇÃO ==========
OC_AUTH_USER=OColecionadorUser
OC_AUTH_PASSWORD=OColecionador@2025
OC_AUTH_EMAIL=admin@ocolecionador.local

# ========== OAUTH2 ==========
OC_GITHUB_CLIENT_ID=seu_github_id
OC_GITHUB_CLIENT_SECRET=seu_github_secret
OC_GOOGLE_CLIENT_ID=seu_google_id
OC_GOOGLE_CLIENT_SECRET=seu_google_secret

# ========== NGROK ==========
OC_NGROK_TOKEN=seu_ngrok_token

# ========== GLITCHTIP ==========
GLITCHTIP_SECRET_KEY=gerar_chave_aleatoria_aqui

# ========== SENTRY (Error Tracking) ==========
SENTRY_DSN=http://glitchtip:8000/3
```

---

## 📊 Dashboard e Ferramentas

### Acesso aos Painéis

| Ferramenta | URL | Usuário | Função |
|-----------|-----|---------|---------|
| **Frontend** | https://louse-model-lioness.ngrok-free.app | OAuth2 | App principal |
| **Backend API** | https://louse-model-lioness.ngrok-free.app/api | Token | API REST |
| **Classifier** | http://localhost:5001 | - | Classificação IA |
| **Portainer** | https://localhost:9443 | Admin | Docker UI |
| **Metabase** | http://localhost:3000 | Admin | BI Dashboard |
| **GlitchTip** | http://localhost:8000 | Admin | Error tracking |
| **pgAdmin** | http://localhost:5050 | Admin | PostgreSQL UI |
| **MinIO Console** | http://localhost:9001 | User | S3 Storage |
| **RabbitMQ** | http://localhost:15672 | User | Message Broker |

---

## 🔍 Monitoramento de Health Checks

```mermaid
graph LR
    A["Health Check"] --> B{Status}
    B -->|Healthy| C["🟢 Green"]
    B -->|Unhealthy| D["🔴 Red"]
    
    C --> E["Services rodando"]
    D --> F["Investigar logs"]
    F --> G["docker compose logs -f service"]
```

### Comando para Verificar Saúde

```bash
# Ver status de todos os containers
docker compose ps

# Ver logs de um serviço específico
docker compose logs -f ocolecionadorbackend

# Executar health check manual
docker exec ocolecionadorbackend curl -f http://localhost:8080/api/health

# Ver uso de recursos
docker stats

# Verificar volumes
docker volume ls
```

---

## 🚨 Troubleshooting

### Backend não conecta ao SQL Server

```bash
# Verifique se SQL Server está rodando
docker ps | grep sqlserver

# Teste conexão
docker exec ocolecionadorbackend curl -f http://localhost:8080/api/health

# Ver logs
docker compose logs sqlserver
```

### Ngrok não conecta

```bash
# Verifique token
echo $OC_NGROK_TOKEN

# Verifique status
curl http://localhost:4040/api/tunnels

# Reinicie ngrok
docker compose restart ngrok
```

### Augmentations não consome da fila

```bash
# Verifique RabbitMQ
docker compose logs rabbitmq

# Acesse dashboard RabbitMQ
curl http://localhost:15672 -u user:pass

# Verifique fila
docker exec rabbitmq rabbitmqctl list_queues
```

---

## 📈 Fluxo Completo de Deployment

```mermaid
sequenceDiagram
    participant Dev as 👨‍💻 Developer
    participant GitHub as 🐙 GitHub
    participant CI as ⚙️ CI/CD
    participant Runner as 🖥️ Runner
    participant DockerHub as 🐳 Docker Hub
    participant Prod as 🏠 Production

    Dev->>GitHub: Push código
    GitHub->>CI: Trigger workflows
    
    alt BuildExpo
        CI->>Runner: Build APK
        Runner->>CI: APK pronto
        CI->>GitHub: Upload artifact
    end
    
    alt DeployDockerHub
        CI->>Runner: Build Docker images
        Runner->>DockerHub: Push images
        DockerHub->>Prod: Pull latest
    end
    
    alt SelfHostedDockerCompose
        CI->>Runner: docker compose up
        Runner->>Prod: Inicia containers
        Prod->>Prod: Health checks
        Runner->>CI: ✓ Tudo OK
    end
    
    CI->>GitHub: Status check
    GitHub->>Dev: ✓ Build passou
```

---

## 🎯 Conclusão

A infraestrutura do OColecionador é:

✅ **Modular** – Cada serviço é um container independente  
✅ **Escalável** – Suporta múltiplas instâncias com load balancer  
✅ **Resiliente** – Health checks e restart policies  
✅ **Monitorado** – GlitchTip, Metabase, Portainer  
✅ **Acessível** – ngrok tunnel para acesso externo  
✅ **Automatizado** – CI/CD via GitHub Actions  
✅ **Isolado** – Redes Docker para segregação  

Todos os serviços trabalham em conjunto através de Docker Compose, com perfis específicos para desenvolvimento vs produção.