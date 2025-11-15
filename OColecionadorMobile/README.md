# OColecionadorMobile 📱

## 📋 O que é?

O **OColecionadorMobile** é o **aplicativo nativo para iOS e Android** do projeto OColecionador. Uma experiência móvel completa para colecionadores:

- ✅ **Login OAuth2** – Autenticação segura com Google e GitHub
- ✅ **Galeria da Coleção** – Visualizar itens em grid
- ✅ **Criar Novo Item** – Upload de múltiplas fotos com câmera/galeria
- ✅ **Classificação em Tempo Real** – IA integrada no dispositivo
- ✅ **Gerenciamento de Categorias** – Organizar itens
- ✅ **Perfil do Usuário** – Visualizar dados e logout
- ✅ **Interface Intuitiva** – Bottom tabs navigation

---

## 🏗️ Stack Tecnológico

| Tecnologia | Versão | Propósito |
|-----------|--------|----------|
| **React Native** | 0.81.4 | Framework mobile |
| **Expo** | ~54.0.10 | Managed service |
| **TypeScript** | ~5.9.2 | Type-safe development |
| **Expo Router** | ~6.0.8 | Navegação nativa |
| **Axios** | ^1.12.2 | Cliente HTTP |
| **Expo Secure Store** | ~15.0.7 | Armazenamento seguro |
| **Expo Image Picker** | ~17.0.8 | Câmera e galeria |

---

## 🚀 Quick Start

### Pré-requisitos

- Node.js 20+ instalado
- Expo CLI: `npm install -g expo-cli`
- EAS CLI: `npm install -g eas-cli`
- Emulador Android ou simulador iOS (opcional)

### Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/PatrickCalorioCarvalho/OColecionador.git
cd OColecionador/OColecionadorMobile

# 2. Instale as dependências
npm install

# 3. Configure variáveis de ambiente
cat > .env << EOF
EXPO_PUBLIC_API_URL=https://seu-backend.com/api
EOF

# 4. Inicie o servidor Expo
npm start

# 5. Abra no seu device/emulador
# Pressione:
# - "a" para Android
# - "i" para iOS
# - "w" para Web
```

A aplicação abrirá via **Expo Go** no seu dispositivo.

---

## 📱 Estrutura do Projeto

```
OColecionadorMobile/
├── app/
│   ├── _layout.tsx              # RootLayout (verificação de token)
│   ├── index.tsx                # Redirect para /home
│   │
│   ├── (auth)/
│   │   ├── _layout.tsx          # Layout de autenticação
│   │   └── login.tsx            # Tela de login OAuth2
│   │
│   └── (tabs)/
│       ├── _layout.tsx          # Bottom tab navigator
│       ├── home.tsx             # Galeria de itens (FlatList 2 cols)
│       ├── newItem.tsx          # Criar novo item
│       ├── classify.tsx         # Classificar imagem
│       └── account.tsx          # Perfil do usuário
│
├── assets/
│   └── images/
│       ├── icon.png
│       ├── splash-icon.png
│       └── ...
│
├── models/
│   ├── Items.ts                 # Interface Item + CRUD
│   ├── Categorias.ts            # Interface Categoria + GET
│   └── Clasificar.ts            # Interface Classification
│
├── services/
│   └── API.ts                   # Cliente HTTP com interceptors
│
├── app.json                     # Configuração Expo
├── eas.json                     # Configuração EAS Build
├── package.json
├── tsconfig.json
└── README.md
```

---

## 🧩 Componentes Principais

### 1. **Login Screen**

Tela inicial com OAuth2 e deep linking:

```tsx
<WebBrowser.openAuthSessionAsync(
  'https://backend/login?mobile=true',
  redirectUri
)>
  // Retorna token via deep link
  ocolecionadormobile://auth?token=google_OC_ya29...
</WebBrowser>
```

---

### 2. **Home Screen**

Grid 2 colunas com pull-to-refresh:

```tsx
<FlatList
  data={items}
  numColumns={2}
  renderItem={({ item }) => (
    <View style={styles.card}>
      <Image source={{ uri: item.fotos[0] }} />
      <Text>{item.nome}</Text>
    </View>
  )}
  refreshControl={<RefreshControl />}
/>
```

---

### 3. **New Item Screen**

Formulário completo com:
- Input de nome
- Picker de categorias
- Seletor de múltiplas fotos (câmera + galeria)
- Preview das fotos
- Botão salvar

---

### 4. **Classify Screen**

Captura foto e envia para classificação:
- Seletor de imagem (câmera/galeria)
- Preview
- Botão "Analisar"
- Resultado com classe + confiança + similares

---

### 5. **Account Screen**

Exibe perfil do usuário:
- Avatar do Google/GitHub
- Nome
- Botão de logout

---

## 📡 Endpoints Consumidos

```bash
# Autenticação (Deep Linking)
GET /login?mobile=true
  → Redireciona para: ocolecionadormobile://auth?token=...

# Itens
GET /api/Items
  Response: [{ id, nome, categoriaId, fotos: [url1, url2, ...] }]

POST /api/Items (FormData)
  Body: { nome, categoriaId, fotos: [File, File, ...] }
  Response: { itemId, success }

# Categorias
GET /api/Categorias
  Response: [{ id, descricao }, ...]

# Classificação
POST /api/Clasificar (FormData)
  Body: { Foto: File }
  Response: {
    classe: "carro",
    confianca: 0.92,
    items: [{ nome, fotos, distancia }, ...]
  }
```

---

## 🔐 Autenticação e Segurança

### Token Storage

```typescript
// Usa Expo Secure Store (encriptado no device)
await SecureStore.setItemAsync('token', 'google_OC_ya29...');
```

### Deep Linking

```json
// app.json
{
  "scheme": "ocolecionadormobile",
  "plugins": [
    [
      "expo-router",
      {
        "origin": "https://seu-backend.com"
      }
    ]
  ]
}
```

### Interceptor Automático

```typescript
// Adiciona Authorization header em todas as requisições
api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## 🎨 Design System

### Cores

```typescript
const colors = {
  bg_dark: '#1E2A38',
  bg_card: '#2c3e50',
  text_primary: '#fff',
  text_secondary: '#aaa',
  primary: '#24afb9',
  danger: '#e74c3c',
  success: '#2ecc71',
};
```

### Bottom Tabs

```
┌─────────────────────────────┐
│  Item                       │
├─────────────────────────────┤
│  Item    │    Item          │
├─────────────────────────────┤
│ 🏠 Início │ ➕ Novo │ 🔍 Classificar │ 👤 Conta │
└─────────────────────────────┘
```

---

## 🔄 Fluxos Principais

### 1️⃣ Login com OAuth2

```
Abre app
  ↓
Verifica token em Secure Store
  ↓
Sem token? → Abre WebBrowser
  ↓
Google/GitHub login
  ↓
Backend retorna token
  ↓
Deep link: ocolecionadormobile://auth?token=...
  ↓
Salva em Secure Store
  ↓
Redireciona para /home
```

---

### 2️⃣ Upload de Múltiplas Fotos

```
Home → Aba "Novo"
  ↓
Preenche nome
  ↓
Seleciona categoria
  ↓
Clica "Selecionar Fotos"
  ↓
Câmera/Galeria → Seleciona X fotos
  ↓
Preview em FlatList horizontal
  ↓
Clica "Salvar"
  ↓
Monta FormData com blobs
  ↓
POST /api/Items
  ↓
✓ Sucesso → Limpa form
```

---

### 3️⃣ Classificação em Tempo Real

```
Aba "Classificar"
  ↓
Seleciona foto
  ↓
Preview
  ↓
"Analisar Foto"
  ↓
Envia ao backend
  ↓
Classifier executa TensorFlow
  ↓
FAISS busca similares
  ↓
Retorna classe + confiança + items similares
  ↓
Renderiza resultado
```

---

## 📸 Recursos Específicos

### Câmera

```typescript
// Captura foto
const result = await ImagePicker.launchCameraAsync({
  mediaTypes: ImagePicker.MediaTypeOptions.Images,
  quality: 1,  // 0-1
  allowsEditing: false,
});

if (!result.canceled) {
  const uri = result.assets[0].uri;  // file://...
}
```

### Galeria

```typescript
// Seleciona da galeria
const result = await ImagePicker.launchImageLibraryAsync({
  mediaTypes: ImagePicker.MediaTypeOptions.Images,
  quality: 1,
  allowsMultiple: false,
});
```

### FormData com Fotos

```typescript
const formData = new FormData();

photos.forEach((photo, index) => {
  formData.append('fotos', {
    uri: photo,               // file://...
    type: 'image/jpeg',
    name: `photo_${index}.jpg`,
  } as any);
});

formData.append('nome', 'Meu Item');
formData.append('categoriaId', 1);
```

---

## 🚀 Build e Distribuição

### Desenvolvimento

```bash
# Inicia Expo dev server
npm start

# Em outro terminal, build Android
npm run android

# Ou iOS
npm run ios
```

---

### Build com EAS (Produção)

```bash
# Login na conta Expo
expo login

# Build Android APK
eas build --platform android --profile preview

# Build iOS
eas build --platform ios --profile preview

# Distribuir para Play Store/App Store
eas build --platform android --profile production
eas submit --platform android
```

---

### APK Local

```bash
# Build APK local (requer Android Studio)
npx eas-cli build --platform android \
  --profile preview \
  --local \
  --output app-production-release.apk
```

---

## 🧪 Testes

```bash
# Testes unitários
npm test

# Com coverage
npm test -- --coverage
```

---

## 📊 Performance

### Otimizações Implementadas

✅ **FlatList virtualizado** – Renderiza apenas itens visíveis  
✅ **Lazy loading de imagens** – Carrega sob demanda  
✅ **Memoization** – Evita re-renders  
✅ **Cache local** – AsyncStorage para dados  
✅ **Compressão** – Fotos comprimidas antes de upload  

---

## 🐛 Troubleshooting

### Erro: "Failed to fetch from API"

```bash
# Verifique se backend está acessível
curl https://seu-backend.com/api/Items

# Verifique CORS
# Backend deve ter CORS habilitado para mobile
```

---

### Erro: "Token inválido"

```bash
# Limpe o app
npm start -- --clear

# Verifique Secure Store
// Pode estar criptografado com fingerprint diferente
```

---

### Câmera não funciona

```bash
# Verifique permissões no app.json
{
  "plugins": [
    [
      "expo-image-picker",
      {
        "photosPermission": "A aplicação acessa sua câmera e galeria.",
        "cameraPermission": "A aplicação acessa sua câmera."
      }
    ]
  ]
}
```

---

## 📚 Documentação Adicional

- [Expo Documentation](https://docs.expo.dev)
- [Expo Router](https://docs.expo.dev/routing/introduction/)
- [React Native](https://reactnative.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

## 👨‍💻 Contribuição

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/MinhaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona feature'`)
4. Push para a branch (`git push origin feature/MinhaFuncionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é open source. Veja [LICENSE](../../LICENSE) para detalhes.

---

## 👤 Autor

**Patrick Calorio Carvalho**  
📧 [Email](mailto:patrick@example.com)  
🔗 [GitHub](https://github.com/PatrickCalorioCarvalho)  
🔗 [LinkedIn](https://linkedin.com/in/patrickcaloriocarvalho)

---

## 📞 Suporte

Para reportar bugs ou sugerir melhorias:
- 📝 [GitHub Issues](https://github.com/PatrickCalorioCarvalho/OColecionador/issues)
- 💬 [Discussões](https://github.com/PatrickCalorioCarvalho/OColecionador/discussions)

---

## 🔗 Links Úteis

- 🌐 [Dashboard Web](https://louse-model-lioness.ngrok-free.app)
- 🔌 [Backend API](http://localhost:5000)
- 📚 [Documentação Completa](../Documentation/docs)
- 🐳 [Docker Hub](https://hub.docker.com/u/patrickcaloriocarvalho)
- 🎯 [Expo Dashboard](https://expo.dev/dashboard)