---
id: ocolecionadoraugmentations-advanced
title: OColecionadorAugmentations - Fluxos Avançados
sidebar_label: Avançado
---

# OColecionadorAugmentations - Fluxos Avançados

Documentação detalhada dos fluxos complexos e otimizações do serviço de augmentação.

---

## 🔄 Fluxo 1: Pipeline Completo com Processamento Paralelo

```mermaid
sequenceDiagram
    participant RabbitMQ as 📨 RabbitMQ
    participant Augmentations as 🎨 Augmentations
    participant MinIO as 📦 MinIO
    participant PostgreSQL as 💾 PostgreSQL
    participant Workers as ⚙️ Thread Pool

    RabbitMQ->>Augmentations: Delivery (consumer)
    Augmentations->>PostgreSQL: INSERT job (status: processing)
    
    Augmentations->>MinIO: DownloadFile (original)
    MinIO-->>Augmentations: Imagem bytes
    
    Augmentations->>Augmentations: Carrega em memória (NumPy)
    
    Augmentations->>Workers: Dispatch 9 tasks em paralelo
    
    par Task 1 - Rotação
        Workers->>Workers: Rotado 90°
        Workers->>MinIO: Upload
    and Task 2 - Flip H
        Workers->>Workers: Flip Horizontal
        Workers->>MinIO: Upload
    and Task 3 - Brilho ↑
        Workers->>Workers: Brightness Up
        Workers->>MinIO: Upload
    and Task 4-9
        Workers->>Workers: Outras transformações
        Workers->>MinIO: Upload
    end
    
    Workers->>PostgreSQL: Batch INSERT (9 rows)
    Augmentations->>PostgreSQL: UPDATE job (status: success)
    Augmentations->>RabbitMQ: PublishMessage (fila: ModelTraining)
    Augmentations->>RabbitMQ: ACK
```

---

## 🎨 Fluxo 2: Augmentations com Detecção de Qualidade

```mermaid
sequenceDiagram
    participant Consumer as 📨 Consumer
    participant QualityCheck as ✓ Quality Detector
    participant Transform as 🎨 Transform Engine
    participant Validation as 🔍 Validation
    participant MinIO as 📦 MinIO

    Consumer->>Consumer: Recebe mensagem
    Consumer->>Consumer: Download imagem
    
    Consumer->>QualityCheck: Analisa qualidade original
    QualityCheck->>QualityCheck: Blur detection (Laplacian variance)
    QualityCheck->>QualityCheck: Brightness check (histogram)
    QualityCheck->>QualityCheck: Contrast analysis (std dev)
    
    alt Qualidade baixa (< threshold)
        QualityCheck-->>Consumer: ⚠️ Low quality
        Consumer->>PostgreSQL: Flag bad_quality = true
        Consumer->>Consumer: Skip para augmentations avançadas
    else Qualidade OK
        QualityCheck-->>Consumer: ✓ OK
    end
    
    Consumer->>Transform: Aplicar 9 transformações
    
    par Para cada variação
        Transform->>Validation: Valida transformação
        Validation->>Validation: Verifica integridade
        alt Variação inválida
            Validation-->>Transform: ✗ Skip
        else Válida
            Validation-->>Transform: ✓ Salva
            Transform->>MinIO: Upload
        end
    end
```

---

## ⚡ Fluxo 3: Batch Processing com Multi-Threading

```mermaid
graph LR
    A["📨 RabbitMQ<br/>Queue"] -->|Batch=10| B["🔀 Load Balancer"]
    B -->|Task 1-10| C["⚙️ Worker Pool<br/>Thread-1"]
    B -->|Task 11-20| D["⚙️ Worker Pool<br/>Thread-2"]
    B -->|Task 21-30| E["⚙️ Worker Pool<br/>Thread-3"]
    
    C -->|Upload| F["📦 MinIO<br/>Connection Pool"]
    D -->|Upload| F
    E -->|Upload| F
    
    F -->|Batch INSERT| G["💾 PostgreSQL<br/>Async I/O"]
    
    C -->|Metrics| H["📊 Monitoring"]
    D -->|Metrics| H
    E -->|Metrics| H
```

---

## 🔁 Fluxo 4: Retry com Exponential Backoff

```mermaid
sequenceDiagram
    participant Queue as 📨 Queue
    participant Consumer as 🎨 Consumer
    participant Storage as 📦 Storage
    participant DB as 💾 Database
    participant DLQ as ☠️ Dead Letter Queue

    Queue->>Consumer: Delivery (Attempt 1)
    Consumer->>Storage: Download
    Storage-->>Consumer: ❌ Timeout
    Consumer->>DB: attempts++
    Consumer->>Queue: NACK + requeue
    
    activate Queue
    Note over Queue: Wait 5s * 2^0 = 5s
    deactivate Queue
    
    Queue->>Consumer: Redelivery (Attempt 2)
    Consumer->>Storage: Download
    Storage-->>Consumer: ❌ 403 Forbidden
    Consumer->>DB: attempts++
    Consumer->>Queue: NACK + requeue
    
    activate Queue
    Note over Queue: Wait 5s * 2^1 = 10s
    deactivate Queue
    
    Queue->>Consumer: Redelivery (Attempt 3)
    Consumer->>Storage: Download
    Storage-->>Consumer: ✓ OK
    Consumer->>Consumer: Process
    Consumer->>Queue: ACK
    
    alt Mais de 3 tentativas
        Consumer->>DLQ: Send message
        DLQ->>DLQ: Alert Backend
    end
```

---

## 🎯 Fluxo 5: Augmentations Adaptativas Baseadas em Categoria

```mermaid
graph TB
    A["📨 Mensagem<br/>itemId, categoria"] -->|Categoria?| B{Classifica}
    
    B -->|carros| C["🚗 Car-specific<br/>Augmentations"]
    B -->|moedas| D["🪙 Coin-specific<br/>Augmentations"]
    B -->|animais| E["🦁 Animal-specific<br/>Augmentations"]
    B -->|arte| F["🎨 Art-specific<br/>Augmentations"]
    
    C -->|Rotação 360°<br/>Perspective warp| C1["Simula<br/>diferentes ângulos"]
    D -->|Rotação granular<br/>Zoom in/out| D1["Simula<br/>macro photography"]
    E -->|Rotação natural<br/>Color jitter| E1["Simula<br/>pose variation"]
    F -->|Elastic deform<br/>Color shift| F1["Simula<br/>lighting variation"]
    
    C1 -->|Upload| G["📦 MinIO<br/>training/{categoria}"]
    D1 -->|Upload| G
    E1 -->|Upload| G
    F1 -->|Upload| G
```

---

## 💾 Fluxo 6: Persistência com Transações PostgreSQL

```mermaid
sequenceDiagram
    participant Consumer as 🎨 Consumer
    participant DB as 💾 PostgreSQL
    participant Transaction as 🔒 Transaction

    Consumer->>Transaction: BEGIN
    Transaction->>DB: Lock table augmentation_jobs
    
    Consumer->>DB: INSERT INTO augmentation_jobs (status: processing)
    DB-->>Consumer: job_id = 101
    
    loop Para cada variação (9x)
        Consumer->>Consumer: Gera transformação
        Consumer->>DB: INSERT INTO augmentation_results
        DB->>DB: Add to transaction buffer
    end
    
    Consumer->>DB: INSERT INTO augmentation_metrics (tempo, file_size)
    
    alt Sucesso
        Consumer->>Transaction: COMMIT
        Transaction->>DB: Persiste todas as 11 inserts
        DB->>DB: Unlock table
        DB-->>Consumer: ✓ Confirmado
    else Erro
        Consumer->>Transaction: ROLLBACK
        Transaction->>DB: Desfaz todas as inserts
        DB->>DB: Unlock table
        DB-->>Consumer: ❌ Revertido
    end
```

---

## 📊 Fluxo 7: Monitoramento e Métricas

```mermaid
graph LR
    A["🎨 Processing"] -->|Emit| B["📊 Metrics"]
    
    B -->|Scrape| C["📈 Prometheus"]
    C -->|Query| D["📊 Grafana"]
    
    B -->|Events| E["🔔 Alert Manager"]
    E -->|Trigger| F["🚨 Slack Notification"]
    
    C -->|Store| G["⏱️ Time Series DB"]
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e8f5e9
    style E fill:#fce4ec
```

**Métricas coletadas:**
- Tempo de processamento por item
- Taxa de sucesso/falha
- Tamanho de arquivo processado
- Latência de RabbitMQ/MinIO/PostgreSQL
- Memória utilizada por worker

---

## 🔐 Fluxo 8: Validação de Integridade de Arquivo

```mermaid
sequenceDiagram
    participant Consumer as 🎨 Consumer
    participant Transform as 🔄 Transform
    participant Validation as ✓ Validator
    participant MinIO as 📦 MinIO

    Consumer->>Transform: Gera augmentação
    Transform-->>Validation: Imagem processada (bytes)
    
    Validation->>Validation: Calcula MD5 hash
    Validation->>Validation: Verifica dimensões
    Validation->>Validation: Valida formato (JPEG/PNG)
    Validation->>Validation: Verifica se não está corrompida
    
    alt Validação falha
        Validation-->>Consumer: ❌ Invalid
        Consumer->>PostgreSQL: Flag error_type = 'invalid_format'
        Consumer->>Consumer: Skip upload
    else Válida
        Validation-->>MinIO: Upload
        MinIO->>MinIO: Calcula ETag S3
        MinIO-->>Validation: ETag retornado
        
        Validation->>Validation: Compara ETag com hash local
        alt ETag mismatch
            Validation-->>Consumer: ⚠️ Integrity check failed
        else Match
            Validation-->>Consumer: ✓ Confirmed
        end
    end
```

---

## 🚀 Fluxo 9: Escalabilidade com Consumidores Múltiplos

```mermaid
graph TB
    subgraph Queue["📨 RabbitMQ<br/>ImageAugmentations"]
        Q1["Message 1"]
        Q2["Message 2"]
        Q3["Message 3"]
        Q4["Message 4"]
        Q5["Message 5"]
    end
    
    subgraph Consumers["🎨 Consumers (Particionamento)"]
        C1["Consumer-1<br/>itemId: 1-1000"]
        C2["Consumer-2<br/>itemId: 1001-2000"]
        C3["Consumer-3<br/>itemId: 2001-3000"]
    end
    
    subgraph Storage["📦 Shared Resources"]
        MinIO["MinIO<br/>Connection Pool (10)"]
        DB["PostgreSQL<br/>Connection Pool (20)"]
    end
    
    Q1 -->|Auto dispatch| C1
    Q2 -->|Auto dispatch| C2
    Q3 -->|Auto dispatch| C3
    Q4 -->|Auto dispatch| C1
    Q5 -->|Auto dispatch| C2
    
    C1 -->|Concorre| MinIO
    C2 -->|Concorre| MinIO
    C3 -->|Concorre| MinIO
    
    C1 -->|Concorre| DB
    C2 -->|Concorre| DB
    C3 -->|Concorre| DB
    
    style Queue fill:#fff3e0
    style Consumers fill:#e1f5ff
    style Storage fill:#e8f5e9
```

---

## 📈 Benchmark: Tempo de Processamento

```mermaid
graph LR
    A["Input<br/>1 imagem<br/>4MB"] -->|Download<br/>200ms| B["Load em RAM<br/>400ms"]
    B -->|Transform 1<br/>100ms| C["Rotated 90°"]
    B -->|Transform 2<br/>100ms| D["Rotated 180°"]
    B -->|Transform 3<br/>100ms| E["Rotated 270°"]
    B -->|Transform 4<br/>80ms| F["Flip H"]
    B -->|Transform 5<br/>80ms| G["Flip V"]
    B -->|Transform 6<br/>120ms| H["Brightness"]
    B -->|Transform 7<br/>120ms| I["Contrast"]
    B -->|Transform 8<br/>150ms| J["Blur"]
    B -->|Transform 9<br/>200ms| K["CLAHE"]
    
    C -->|Upload<br/>300ms| L["MinIO"]
    D -->|Upload<br/>300ms| L
    E -->|Upload<br/>300ms| L
    F -->|Upload<br/>300ms| L
    G -->|Upload<br/>300ms| L
    H -->|Upload<br/>300ms| L
    I -->|Upload<br/>300ms| L
    J -->|Upload<br/>300ms| L
    K -->|Upload<br/>300ms| L
    
    L -->|Batch INSERT<br/>150ms| M["PostgreSQL"]
    M -->|Total<br/>~3.5s| N["✓ Completo"]
```

**Breakdown:**
- Download: 200ms
- Transform paralelo: ~200ms (9 tasks em paralelo)
- Upload paralelo: ~300ms (9 uploads em paralelo com connection pooling)
- Database: 150ms
- **Total: ~2.8-3.5 segundos por item**

---

## 🔍 Fluxo 10: Debugging e Observabilidade

```mermaid
sequenceDiagram
    participant Code as 🎨 Code
    participant Logger as 📝 Logger
    participant Sentry as 🚨 Sentry
    participant DataDog as 📊 DataDog

    Code->>Logger: log.info("Starting processing itemId=123")
    Code->>Code: Download imagem
    Code->>Logger: log.debug("Downloaded 4.2MB in 215ms")
    
    Code->>Code: Processa transformação
    Code->>Logger: log.info("Generated 9 variations")
    Code->>DataDog: Emit metric: augmentations_count=9
    
    alt Erro durante upload
        Code-->>Logger: log.error("MinIO upload failed")
        Code->>Logger: log.exception(traceback)
        Code->>Sentry: captureException(err, context={itemId, attempt})
        Code->>DataDog: Emit error metric: uploads_failed_count++
    else Sucesso
        Code->>Logger: log.info("✓ Item processed successfully")
        Code->>DataDog: Emit timing: processing_time_ms=2850
    end
```

---

## 🎯 Conclusão

O **OColecionadorAugmentations** oferece:

✅ **Processamento Paralelo** – 9 transformações simultâneas  
✅ **Retry Automático** – Com exponential backoff  
✅ **Validação Rigorosa** – Integridade de arquivo  
✅ **Observabilidade** – Métricas, logs, alertas  
✅ **Escalabilidade** – Múltiplos consumers  
✅ **Resiliência** – Tratamento de erros robusto  

Tempo médio: **2.8-3.5 segundos por item**  
Throughput: **~1000-2000 itens/hora**