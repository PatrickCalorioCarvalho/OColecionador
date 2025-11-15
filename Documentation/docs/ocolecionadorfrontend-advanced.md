---
id: ocolecionadorfrontend-advanced
title: OColecionadorFrontEnd - Fluxos Avançados
sidebar_label: Avançado
---

# OColecionadorFrontEnd - Fluxos Avançados

Documentação detalhada dos fluxos complexos e padrões avançados da aplicação React.

---

## 🔄 Fluxo 1: Autenticação OAuth2 Completa

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 Usuário
    participant Frontend as 🌐 Frontend React
    participant Login as 📄 Login.tsx
    participant AuthService as 🔐 AuthService
    participant Backend as 🔌 Backend API
    participant GoogleOAuth as 🔑 Google OAuth
    participant Dashboard as 📊 Dashboard.tsx

    User->>Frontend: Acessa http://localhost:3000
    Frontend->>Frontend: Verifica token em localStorage
    alt Token não existe
        Frontend->>Login: Renderiza tela de login
        Login-->>User: Exibe botões "Google" e "GitHub"
    end

    User->>Login: Clica "Entrar com Google"
    Login->>AuthService: startOAuth('google')
    AuthService->>GoogleOAuth: window.location = Google Auth URL
    GoogleOAuth->>User: Apresenta formulário
    User->>GoogleOAuth: Credenciais
    GoogleOAuth->>Frontend: Redireciona com ?code=... &state=...
    
    Frontend->>Frontend: Detecta URL com code (AuthRedirect.tsx)
    Frontend->>AuthService: handleCallback(code, state)
    AuthService->>Backend: POST /api/auth/callback { code, state }
    
    Backend->>GoogleOAuth: Valida code com secret
    GoogleOAuth-->>Backend: ID Token + Access Token
    Backend->>Backend: Decodifica JWT de Google
    Backend->>Backend: Gera JWT próprio com claims do usuário
    Backend-->>AuthService: { token: 'eyJ...', provider: 'google' }
    
    AuthService->>AuthService: localStorage.setItem('token_ocolecionador', token)
    AuthService->>AuthService: Adiciona na session storage também
    Frontend->>Dashboard: Redireciona para /dashboard
    Dashboard->>Dashboard: Carrega dados de usuário
    Dashboard-->>User: ✓ Dashboard carregado com sucesso
```

---

## 📸 Fluxo 2: Upload Multi-Foto com Validação

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 Usuário
    participant UI as 🎨 Upload UI
    participant Validator as ✅ Validator
    participant Frontend as 🌐 Frontend
    participant Backend as 🔌 Backend
    participant MinIO as 📦 MinIO
    participant SQLServer as 💾 SQL Server

    User->>UI: Seleciona múltiplas fotos (drag & drop)
    UI->>UI: Agrupa em FormData
    UI->>Validator: Valida cada arquivo
    
    loop Para cada arquivo
        Validator->>Validator: Tipo (jpeg, png, webp)
        Validator->>Validator: Tamanho (< 10MB)
        Validator->>Validator: Dimensões (min 300x300)
        alt Falha validação
            Validator-->>UI: ❌ Erro
            UI-->>User: "Formato inválido"
        else Passa
            Validator-->>UI: ✓ OK
        end
    end

    UI->>UI: Cria preview local em <img>
    User->>UI: Insere nome do item
    User->>UI: Seleciona categoria
    User->>UI: Clica "Upload"

    UI->>Frontend: FormData { nome, categoriaId, fotos[] }
    Frontend->>Frontend: setLoading(true)
    Frontend->>Backend: POST /api/Items { FormData }
    
    Backend->>Backend: Valida token
    Backend->>Backend: Valida FormData (tamanho total)
    Backend->>MinIO: UploadFile (bucket: original, path: item/{id}/original.jpg)
    MinIO-->>Backend: { url, etag }
    
    Backend->>SQLServer: INSERT INTO Items (nome, categoriaId)
    Backend->>SQLServer: INSERT INTO Fotos (ItemId, Caminho)
    
    Backend->>Backend: Publica mensagem RabbitMQ (Augmentations)
    Backend-->>Frontend: { itemId, fotoIds[], urls[] }
    
    Frontend->>Frontend: setLoading(false)
    Frontend->>UI: Limpa formulário
    Frontend-->>User: "✓ Fotos enviadas com sucesso!"
```

---

## 🤖 Fluxo 3: Classificação com IA e Busca de Similaridade

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 Usuário
    participant ClassifyTab as 🤖 Classify Tab
    participant Frontend as 🌐 Frontend
    participant Backend as 🔌 Backend
    participant MinIO as 📦 MinIO
    participant Classifier as 🧠 Classifier API
    participant FAISS as 🔍 FAISS

    User->>ClassifyTab: Seleciona foto para classificar
    ClassifyTab->>ClassifyTab: Preview da imagem
    User->>ClassifyTab: Clica "Classificar"
    
    ClassifyTab->>ClassifyTab: setLoading(true), progress=0
    ClassifyTab->>Frontend: Inicia upload
    Frontend->>Backend: POST /api/Clasificar { foto }
    Backend->>Backend: 1. Valida imagem
    Backend->>MinIO: 2. Upload temporário
    MinIO-->>Backend: { path: 'temp/uploads/xyz.jpg' }
    Backend->>Backend: 3. Registra em banco
    
    Backend->>Classifier: 4. POST /classify { image_path }
    Classifier->>MinIO: Download imagem
    MinIO-->>Classifier: Bytes
    
    Classifier->>Classifier: 5. Pré-processamento
    Classifier->>Classifier: - Redimensiona para 224x224
    Classifier->>Classifier: - Normaliza pixel values
    Classifier->>Classifier: - Converte para tensor
    
    Classifier->>Classifier: 6. Forward pass TensorFlow
    Classifier->>Classifier: - MobileNetV2 layers
    Classifier->>Classifier: - Output softmax (10 classes)
    Classifier->>Classifier: - Extrai embeddings (1280 dims)
    
    Classifier->>Classifier: 7. Pós-processamento
    Classifier->>Classifier: - Classe = argmax(softmax)
    Classifier->>Classifier: - Confiança = max(softmax)
    Classifier->>FAISS: 8. LoadIndex + Search(embedding, k=5)
    FAISS-->>Classifier: { distances, indices }
    
    Classifier-->>Backend: {<br/>  classe: 'carro',<br/>  confianca: 0.95,<br/>  semelhantes: [<br/>    { itemId: 1, distancia: 0.08 },<br/>    { itemId: 2, distancia: 0.12 }<br/>  ]<br/>}
    
    Backend->>SQLServer: Salva classificação
    Backend-->>Frontend: JSON com resultado
    
    Frontend->>Frontend: Parse resultado
    Frontend->>ClassifyTab: Exibe resultado
    ClassifyTab->>ClassifyTab: - Classe principal em grande
    ClassifyTab->>ClassifyTab: - Barra de confiança animada
    ClassifyTab->>ClassifyTab: - Lista de similares com imagens
    Frontend-->>User: "🎯 Resultado: Carro com 95% de confiança"
```

---

## 🐳 Fluxo 4: Dashboard Docker com Polling e Real-time Updates

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 Admin
    participant DockerTab as 🐳 Docker Tab
    participant Frontend as 🌐 Frontend
    participant useDocker as 🔄 useDocker Hook
    participant Backend as 🔌 Backend
    participant DockerAPI as 🐳 Docker API

    User->>DockerTab: Acessa aba "Containers"
    DockerTab->>Frontend: useDocker()
    Frontend->>useDocker: Inicializa hook
    useDocker->>useDocker: useState({ containers: [], loading: true })
    useDocker->>useDocker: useEffect(() => { fetchContainers() }, [])
    
    useDocker->>Frontend: Requisição GET /api/Docker
    Frontend->>Backend: Com token de autenticação
    Backend->>Backend: Valida token (admin?)
    Backend->>DockerAPI: docker.Containers.ListContainersAsync()
    DockerAPI-->>Backend: [{<br/>  Id: 'abc123...',<br/>  Names: ['/ocolecionadortraining'],<br/>  State: 'exited',<br/>  Status: 'Exited (0)',<br/>  Image: 'ocolecionadortraining:latest'<br/>}]
    
    Backend-->>Frontend: Transforma para ContainerDTO[]
    Frontend-->>useDocker: [{ id, names, state, status, image }]
    useDocker->>useDocker: setContainers(data)
    useDocker->>useDocker: setLoading(false)
    
    Frontend->>DockerTab: Re-renders com containers
    DockerTab->>DockerTab: Renderiza ContainerCard para cada
    DockerTab-->>User: Exibe cards com status
    
    alt Usuário clica "Iniciar"
        User->>DockerTab: Clica "Iniciar" em card
        DockerTab->>useDocker: startContainer(id)
        useDocker->>Frontend: POST /api/Docker/start/{id}
        Frontend->>Backend: Com token
        Backend->>DockerAPI: docker.Containers.StartContainerAsync(id)
        DockerAPI->>DockerAPI: SIGTERM+SIGKILL → docker run
        DockerAPI-->>Backend: { StatusCode: 204 }
        Backend-->>Frontend: { success: true }
        Frontend-->>useDocker: Atualiza container state
        useDocker->>useDocker: setContainers(updated)
        DockerTab-->>User: "✓ Container iniciado"
    end
    
    alt Polling automático a cada 5s
        useDocker->>useDocker: setInterval(() => fetchContainers(), 5000)
        useDocker->>Frontend: GET /api/Docker
        Frontend->>Backend: Fetch atualizado
        Backend->>DockerAPI: ListContainersAsync()
        Backend-->>Frontend: Novo estado
        Frontend-->>useDocker: Data atualizada
        useDocker->>useDocker: setContainers(data)
        DockerTab->>DockerTab: Re-renders automaticamente
    end
```

---

## 🎨 Fluxo 5: Renderização da Galeria com Imagens do MinIO

```mermaid
sequenceDiagram
    autonumber
    participant User as 👤 Usuário
    participant CollectionTab as 📦 Collection Tab
    participant Frontend as 🌐 Frontend
    participant useItems as 🔄 useItems Hook
    participant Backend as 🔌 Backend
    participant SQLServer as 💾 SQL Server
    participant MinIO as 📦 MinIO
    participant Browser as 🌍 Browser

    User->>CollectionTab: Acessa aba "Minha Coleção"
    CollectionTab->>Frontend: useItems()
    Frontend->>useItems: Inicializa hook
    useItems->>useItems: useState({ items: [], loading: true })
    useItems->>useItems: useEffect(() => { fetchItems() }, [])
    
    useItems->>Frontend: GET /api/Items (com token)
    Frontend->>Backend: Requisição autenticada
    Backend->>Backend: Valida token
    Backend->>SQLServer: SELECT * FROM Items<br/>INCLUDE(Fotos)<br/>INCLUDE(Categoria)
    
    SQLServer-->>Backend: [{<br/>  id: 1,<br/>  nome: 'Ferrari 250',<br/>  categoriaId: 1,<br/>  fotos: [<br/>    { id: 101, caminho: 'item/1/original.jpg' }<br/>  ]<br/>}]
    
    loop Para cada Item e Foto
        Backend->>MinIO: GetPresignedUrlAsync(bucket, path)
        MinIO-->>Backend: URL assinada:<br/>https://minio:9000/ocolecionadorbucket-original/<br/>item/1/original.jpg?<br/>X-Amz-Algorithm=AWS4-HMAC-SHA256&<br/>X-Amz-Credential=...&<br/>X-Amz-Date=20251115T100000Z&<br/>X-Amz-Expires=3600&<br/>X-Amz-Signature=...
    end
    
    Backend-->>Frontend: [{<br/>  id: 1,<br/>  nome: 'Ferrari 250',<br/>  fotos: [<br/>    'https://minio.../item/1/original.jpg?X-Amz-...'<br/>  ]<br/>}]
    
    Frontend-->>useItems: Data com presigned URLs
    useItems->>useItems: setItems(data)
    useItems->>useItems: setLoading(false)
    
    Frontend->>CollectionTab: Re-renders
    CollectionTab->>CollectionTab: Map items para grid
    loop Para cada item
        CollectionTab->>CollectionTab: <ItemCard<br/>  id={item.id}<br/>  nome={item.nome}<br/>  fotos={item.fotos}<br/>/>
        ItemCard->>ItemCard: <img src={presigned_url} />
    end
    
    CollectionTab-->>User: Grid renderizado
    Browser->>Browser: Carrega imagens em paralelo
    Browser->>MinIO: GET presigned_urls (conexões paralelas)
    MinIO-->>Browser: Bytes de imagem
    Browser->>Browser: Renderiza em <img>
    Browser-->>User: "✓ Galeria carregada com 150 fotos"
```

---

## 🔌 Interceptor de Requisições com Error Handling

```typescript
// Detalhes do arquivo services/API.ts

// Interceptor de Request
API.interceptors.request.use(
  (config) => {
    // 1. Adiciona token
    const token = localStorage.getItem('token_ocolecionador')
    if (token && !isTokenExpired(token)) {
      config.headers.Authorization = `Bearer ${token}`
    } else if (token && isTokenExpired(token)) {
      // Token expirado - logout
      clearToken()
      window.location.href = '/login'
    }
    
    // 2. Adiciona headers customizados
    config.headers['X-Requested-With'] = 'XMLHttpRequest'
    config.headers['Content-Type'] = 'application/json'
    
    // 3. Timeout por tipo de request
    if (config.url?.includes('/Clasificar')) {
      config.timeout = 30000 // 30s para classificação
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Interceptor de Response
API.interceptors.response.use(
  (response) => {
    // 2xx: Sucesso
    return response
  },
  (error) => {
    // Trata diferentes status codes
    if (error.response?.status === 401) {
      // Unauthorized - logout
      clearToken()
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      // Forbidden - sem permissão
      console.error('Sem permissão para esta ação')
    } else if (error.response?.status === 404) {
      // Not found
      console.error('Recurso não encontrado')
    } else if (error.response?.status === 500) {
      // Server error
      console.error('Erro interno do servidor')
    } else if (error.code === 'ECONNABORTED') {
      // Timeout
      console.error('Requisição expirou')
    }
    return Promise.reject(error)
  }
)
```

---

## 🎯 Performance: Lazy Loading de Imagens

```typescript
// Componente com lazy loading implementado

interface ItemCardProps {
  item: Item
}

export function ItemCard({ item }: ItemCardProps) {
  const [loaded, setLoaded] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    // Intersection Observer para lazy loading
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && imgRef.current) {
            imgRef.current.src = item.fotos[0]
            observer.unobserve(entry.target)
          }
        })
      },
      { rootMargin: '50px' }
    )

    if (imgRef.current) {
      observer.observe(imgRef.current)
    }

    return () => observer.disconnect()
  }, [item.fotos])

  return (
    <div className="item-card">
      <div className="image-container">
        {!loaded && <div className="skeleton" />}
        <img
          ref={imgRef}
          src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3C/svg%3E"
          alt={item.nome}
          onLoad={() => setLoaded(true)}
          className={loaded ? 'loaded' : ''}
        />
      </div>
      <h3>{item.nome}</h3>
    </div>
  )
}
```

---

## 📊 Conclusão

Os fluxos avançados do OColecionadorFrontEnd demonstram:

✅ **Segurança** – Token management, CORS, autenticação  
✅ **Performance** – Lazy loading, presigned URLs, polling  
✅ **UX** – Error handling, loading states, real-time updates  
✅ **Escalabilidade** – Hooks customizados, interceptadores, composição  
