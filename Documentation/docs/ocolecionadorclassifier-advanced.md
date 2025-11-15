---
id: ocolecionadorclassifier-advanced
title: OColecionadorClassifier - Fluxos Avançados
sidebar_label: Avançado
---

# OColecionadorClassifier - Fluxos Avançados

Documentação detalhada dos fluxos complexos de inferência e otimizações.

---

## 🔄 Fluxo 1: Pipeline Completo de Classificação com Embedding Extraction

```mermaid
sequenceDiagram
    participant Request as 🌐 HTTP Request
    participant Validation as ✓ Validator
    participant Preprocessing as 🖼️ Preprocessor
    participant TensorFlow as 🧠 TensorFlow
    participant Embeddings as 🔗 Embeddings
    participant FAISS as 🔍 FAISS
    participant Database as 💾 PostgreSQL
    participant Response as 📤 Response

    Request->>Validation: POST /classify (image)
    Validation->>Validation: Valida MIME type
    Validation->>Validation: Valida tamanho lt 10MB
    Validation->>Validation: Calcula hash SHA256
    
    Validation->>Preprocessing: Imagem válida
    Preprocessing->>Preprocessing: Abre com Pillow
    Preprocessing->>Preprocessing: Redimensiona 224x224
    Preprocessing->>Preprocessing: Converte RGB
    Preprocessing->>Preprocessing: Normaliza div 255
    Preprocessing->>Preprocessing: Converte NumPy array
    Preprocessing->>Preprocessing: Batch dimension 1,224,224,3
    
    Preprocessing->>TensorFlow: Array normalizado
    TensorFlow->>TensorFlow: Conv2D layers x N
    TensorFlow->>TensorFlow: BatchNorm x N
    TensorFlow->>TensorFlow: ReLU activation x N
    TensorFlow->>TensorFlow: Global Average Pooling → 1280D
    TensorFlow->>TensorFlow: Dense 512 relu → 512D
    TensorFlow->>TensorFlow: Dropout 0.5
    TensorFlow->>TensorFlow: Dense num_classes softmax
    
    TensorFlow-->>Embeddings: Softmax output + 512D layer
    Embeddings->>Embeddings: L2 Normalization
    Embeddings->>Embeddings: Converte float32
    Embeddings->>FAISS: Query vector 512D
    
    FAISS->>FAISS: IVF clustering nprobe=10
    FAISS->>FAISS: L2 distance calculation
    FAISS-->>Embeddings: distances, indices
    
    Embeddings->>Database: SELECT items WHERE embedding_id IN indices
    Database-->>Embeddings: item_id, nome, categoria
    
    Embeddings->>Database: INSERT INTO predictions
    Database-->>Embeddings: Saved OK
    
    Embeddings-->>Response: Classification result
    Response->>Response: classe, confianca, embedding, similar_items
    Response-->>Request: 200 OK with JSON
```

---

## ⚡ Fluxo 2: Batch Inference com Processing Paralelo

```mermaid
graph LR
    A["📨 Batch Request<br/>N imagens"] -->|Split| B["🔀 Task Queue"]
    B -->|Task 1-4| C["🧠 TF Session 1"]
    B -->|Task 5-8| D["🧠 TF Session 2"]
    B -->|Task 9-12| E["🧠 TF Session 3"]
    
    C -->|Preprocess| C1["Normaliza + Resize"]
    D -->|Preprocess| D1["Normaliza + Resize"]
    E -->|Preprocess| E1["Normaliza + Resize"]
    
    C1 -->|Batch forward| C2["Softmax outputs"]
    D1 -->|Batch forward| D2["Softmax outputs"]
    E1 -->|Batch forward| E2["Softmax outputs"]
    
    C2 -->|Extract embeddings| C3["512D vectors"]
    D2 -->|Extract embeddings| D3["512D vectors"]
    E2 -->|Extract embeddings| E3["512D vectors"]
    
    C3 -->|Batch insert| F["💾 PostgreSQL"]
    D3 -->|Batch insert| F
    E3 -->|Batch insert| F
    
    F -->|Return| G["📤 Aggregated Response"]
    
    style A fill:#fff3e0
    style B fill:#e1f5ff
    style C fill:#f3e5f5
    style D fill:#f3e5f5
    style E fill:#f3e5f5
    style F fill:#e8f5e9
```

---

## 🎯 Fluxo 3: FAISS Search com Diferentes Estratégias

```mermaid
graph TD
    A["🔗 Embedding (512D)"] -->|Strategy| B{Índice Type}
    
    B -->|Flat| C["Linear search<br/>O(n) complexity"]
    B -->|IVFFlat| D["Clustering + search<br/>O(log n) + nprobe"]
    B -->|HNSW| E["Hierarchical search<br/>O(log log n)"]
    
    C -->|Compute| C1["L2 distance"]
    C1 -->|Sort| C2["Top-K distances"]
    C2 -->|Return| F["🔍 Results"]
    
    D -->|Cluster| D1["Assign to cluster"]
    D1 -->|Search cluster| D2["nprobe=10 clusters"]
    D2 -->|Compute| D3["L2 distance"]
    D3 -->|Sort| D4["Top-K distances"]
    D4 -->|Return| F
    
    E -->|Graph| E1["Traverse hierarchy"]
    E1 -->|Find neighbors| E2["K-NN in graph"]
    E2 -->|Return| F
    
    F -->|Threshold| G{Confiança}
    G -->|< 0.7| H["❌ Reject"]
    G -->|>= 0.7| I["✓ Accept"]
```

---

## 🔄 Fluxo 4: Model Versioning e A/B Testing

```mermaid
sequenceDiagram
    participant Request as 🌐 Request
    participant Router as 🔀 Router
    participant ModelV1 as 🧠 Model v1
    participant ModelV2 as 🧠 Model v2
    participant Database as 💾 Database

    Request->>Router: Incoming request
    Router->>Router: Random split 50/50
    
    alt Route to V1 (50%)
        Router->>ModelV1: Forward request
        ModelV1->>ModelV1: Inference
        ModelV1-->>Router: Result + metadata
    else Route to V2 (50%)
        Router->>ModelV2: Forward request
        ModelV2->>ModelV2: Inference
        ModelV2-->>Router: Result + metadata
    end
    
    Router->>Database: INSERT INTO ab_test_results
    Database->>Database: Store:<br/>- model_version<br/>- prediction<br/>- confidence<br/>- timestamp
    
    Router-->>Request: Response
    
    par Continuous Monitoring
        Database->>Database: Calculate metrics (v1 vs v2)
        Database->>Database: Accuracy, latency, error rate
    end
```

---

## 💾 Fluxo 5: Caching e Cache Invalidation

```mermaid
sequenceDiagram
    participant Request as 🌐 Request
    participant Cache as 💾 Redis Cache
    participant Model as 🧠 Model
    participant Database as 💾 PostgreSQL

    Request->>Request: Calcula hash SHA256 da imagem
    Request->>Cache: Verifica cache (hash key)
    
    alt Cache HIT (existe)
        Cache-->>Request: Return cached result
        Request->>Database: Log cache_hit
    else Cache MISS (não existe)
        Cache-->>Request: null
        Request->>Model: Execute inference
        Model-->>Request: Predictions + embeddings
        Request->>Cache: SET cache[hash] = result (TTL: 24h)
        Request->>Database: Log inference_performed
    end
```

---

## 📊 Fluxo 6: Monitoramento e Alertas em Tempo Real

```mermaid
graph LR
    A["🤖 Classifier"] -->|Emit| B["📊 Metrics"]
    
    B -->|Inference time| C["⏱️ Latency"]
    B -->|Confidence| D["📈 Confidence"]
    B -->|Error rate| E["❌ Errors"]
    
    C -->|Scrape| F["Prometheus"]
    D -->|Scrape| F
    E -->|Scrape| F
    
    F -->|Query| G["📊 Grafana"]
    F -->|Alert| H["🚨 AlertManager"]
    
    H -->|Latency > 500ms| I["🔔 Slack Alert"]
    H -->|Error rate > 5%| I
    H -->|Confidence < 0.6| I
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style F fill:#f3e5f5
    style G fill:#e8f5e9
    style H fill:#fce4ec
```

---

## 🔐 Fluxo 7: Validação e Adversarial Detection

```mermaid
sequenceDiagram
    participant Image as 🖼️ Input Image
    participant QualityCheck as ✓ Quality Check
    participant BirtBoxCheck as 📦 BBox Check
    participant AdversarialCheck as 🛡️ Adversarial Check
    participant Inference as 🧠 Inference
    participant Response as 📤 Response

    Image->>QualityCheck: Blur detection (Laplacian)
    QualityCheck->>QualityCheck: Var < 100 → blurry
    
    Image->>BirtBoxCheck: Object detection (YOLOv8)
    BirtBoxCheck->>BirtBoxCheck: Detecta bounding box
    BirtBoxCheck->>BirtBoxCheck: Crop central 80%
    
    Image->>AdversarialCheck: FGSM attack detection
    AdversarialCheck->>AdversarialCheck: Perturbações adversariais?
    
    alt Quality/Detection falha
        QualityCheck-->>Response: ⚠️ Low quality
        BirtBoxCheck-->>Response: ⚠️ Object not detected
        AdversarialCheck-->>Response: ⚠️ Adversarial detected
    else Tudo OK
        Inference->>Inference: Execute normal inference
        Inference-->>Response: ✓ Result
    end
```

---

## 🚀 Fluxo 8: Escalabilidade com Horizontal Load Balancing

```mermaid
graph TB
    subgraph Users["👥 Users"]
        U1["User 1"]
        U2["User 2"]
        U3["User 3"]
        U4["User 4"]
    end
    
    subgraph LoadBalancer["⚖️ Load Balancer"]
        LB["Nginx / HAProxy"]
    end
    
    subgraph Classifiers["🤖 Classifier Instances"]
        C1["Classifier-1<br/>Port 5001"]
        C2["Classifier-2<br/>Port 5002"]
        C3["Classifier-3<br/>Port 5003"]
    end
    
    subgraph SharedResources["📦 Shared Resources"]
        Model["Model Cache<br/>(shared memory)"]
        FAISS["FAISS Index<br/>(shared memory)"]
        DB["PostgreSQL<br/>Connection Pool"]
    end
    
    U1 -->|Request| LB
    U2 -->|Request| LB
    U3 -->|Request| LB
    U4 -->|Request| LB
    
    LB -->|Round-robin| C1
    LB -->|Round-robin| C2
    LB -->|Round-robin| C3
    
    C1 -->|Load| Model
    C2 -->|Load| Model
    C3 -->|Load| Model
    
    C1 -->|Query| FAISS
    C2 -->|Query| FAISS
    C3 -->|Query| FAISS
    
    C1 -->|INSERT| DB
    C2 -->|INSERT| DB
    C3 -->|INSERT| DB
```

---

## 📈 Fluxo 9: Benchmark - Tempo de Processamento

```mermaid
graph LR
    A["Input<br/>1 image<br/>4MB"] 
    -->|Download<br/>50ms| B["Load em RAM"]
    -->|Validation<br/>10ms| C["Check MIME/Size"]
    -->|Preprocessing<br/>50ms| D["Resize 224x224<br/>Normalize"]
    -->|Inference<br/>100-150ms| E["Forward Pass<br/>TensorFlow"]
    -->|Embedding<br/>20ms| F["Extract 512D"]
    -->|FAISS Search<br/>30ms| G["Find k=5 similar"]
    -->|Database<br/>20ms| H["Query items"]
    -->|Response<br/>10ms| I["JSON encode"]
    -->|Total<br/>~290-340ms| J["✓ Complete"]
```

---

## 🔍 Fluxo 10: Debugging com Observabilidade Completa

```mermaid
sequenceDiagram
    participant Code as 🤖 Code
    participant Logging as 📝 Logger
    participant APM as 📊 APM (DataDog)
    participant Tracing as 🔎 Distributed Tracing
    participant Dashboard as 📊 Dashboard

    Code->>Logging: log.info("Starting inference")
    Code->>Tracing: span_start("preprocess")
    Code->>Code: Preprocessa imagem
    Code->>Tracing: span_end("preprocess", duration=50ms)
    
    Code->>Tracing: span_start("inference")
    Code->>Code: Forward pass
    Code->>Tracing: span_end("inference", duration=145ms)
    
    Code->>Tracing: span_start("faiss_search")
    Code->>Code: Search similar
    Code->>Tracing: span_end("faiss_search", duration=35ms)
    
    Tracing->>APM: Send trace
    APM->>APM: Correlate with request ID
    APM->>APM: Calculate service map
    
    APM->>Dashboard: Push metrics
    Dashboard->>Dashboard: Display latency graph
    Dashboard->>Dashboard: Show error rates
    Dashboard->>Dashboard: Highlight bottlenecks
    
    alt Latency > threshold
        APM->>APM: Trigger alert
        APM->>Logging: log.warning("High latency")
    end
```

---

## 🎯 Conclusão

O **OColecionadorClassifier** oferece:

✅ **Inferência Rápida** – 100-200ms (TensorFlow)  
✅ **Busca Escalável** – FAISS para milhares de itens  
✅ **Versioning** – A/B testing entre modelos  
✅ **Observabilidade** – Métricas, logs, tracing  
✅ **Validação Robusta** – Detecção de qualidade e adversarial  
✅ **Caching** – Redis para reduzir latência  
✅ **Escalabilidade** – Múltiplas instâncias com load balancer  

**Tempo médio: 290-340ms por requisição**  
**Throughput: ~5-10 requisições/seg por instância**