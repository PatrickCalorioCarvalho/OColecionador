---
id: arquitetura-cicd-infraestrutura
title: Arquitetura, CI/CD e Infraestrutura
sidebar_label: Introdução
---

# ⚡ Arquitetura, CI/CD e Infraestrutura

Referência rápida para operações comuns.

---

## 🚀 Iniciar Ambiente

```bash
# Tudo (automático + manual)
docker compose up -d

# Apenas automático (produção)
docker compose --profile automatic up -d

# Apenas manual (desenvolvimento)
docker compose --profile manual up -d
```

---

## 🔌 URLs de Acesso

| Serviço | URL | Status |
|---------|-----|--------|
| **Frontend** | https://louse-model-lioness.ngrok-free.app | 🟢 Externo |
| **Backend** | http://localhost:5000 | 🔵 Local |
| **Classifier** | http://localhost:5001 | 🔵 Local |
| **Portainer** | https://localhost:9443 | 🟢 Admin |
| **Metabase** | http://localhost:3000 | 🟢 BI |
| **GlitchTip** | http://localhost:8000 | 🔴 Erro |
| **MinIO** | http://localhost:9001 | 🟡 Storage |
| **RabbitMQ** | http://localhost:15672 | 🟡 Queue |

---

## 📊 Status dos Containers

```bash
# Listar todos
docker compose ps

# Ver logs em tempo real
docker compose logs -f backend

# Ver uso de CPU/memória
docker stats
```

---

## 🔄 CI/CD Workflows

### Build Mobile (APK)
- **Trigger:** Push em `OColecionadorMobile/**`
- **Ação:** Build APK com EAS
- **Resultado:** Download em artifacts

### Deploy Docker Hub
- **Trigger:** Push em `main` (múltiplos paths)
- **Ação:** Build e push de imagens
- **Resultado:** Disponível no Docker Hub

### Self-Hosted Compose
- **Trigger:** Pull Request aberto
- **Ação:** `docker compose up --build`
- **Resultado:** Status check no PR

---

## 🐛 Troubleshooting

```bash
# Backend com erro?
docker compose logs backend | tail -50

# Banco não inicia?
docker compose logs sqlserver

# RabbitMQ não conecta?
docker compose logs rabbitmq

# Reiniciar serviço
docker compose restart backend

# Remover volumes (CUIDADO!)
docker compose down -v
```

---

## 🔐 Credenciais Padrão

```
Usuário: OColecionadorUser
Senha: OColecionador@2025
Email: admin@ocolecionador.local
```

---

## 📱 Mobile App

```bash
cd OColecionadorMobile
npm start          # Inicia Expo dev
eas build          # Build APK/IPA
eas submit         # Submete stores
```

---

## 💾 Backup de Dados

```bash
# SQL Server
docker exec sqlserver /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P PASSWORD \
  -Q "BACKUP DATABASE OColecionadorDataBase TO DISK='/backup/db.bak'"

# PostgreSQL
docker exec postgres pg_dump -U user dbname > backup.sql

# MinIO (S3)
docker exec minio mc mirror minio/bucket ./backup
```

---

## 🚫 Parar Ambiente

```bash
# Parar containers
docker compose stop

# Parar e remover
docker compose down

# Parar e remover tudo (incl. volumes)
docker compose down -v
```

---

## 📞 Contato / Suporte

- 📖 [Documentação Completa](.)
- 🐙 [GitHub Issues](https://github.com/PatrickCalorioCarvalho/OColecionador/issues)
- 📧 Email: patrick@example.com