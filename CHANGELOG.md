# 🧾 CHANGELOG – OColecionador

## 📅 Período: Setembro a Novembro de 2025

Histórico consolidado dos principais commits realizados no branch `main`.

---

## 🚀 **Novidades e Funcionalidades Adicionadas**

### Novembro de 2025

* **DashBoardFrontEnd (#77)** – Implementação do painel visual principal do sistema, com visualização dos colecionáveis e status dos módulos.
* **Integração Classifier com BackEnd e Mobile (#76)** – Unificação dos módulos de classificação e comunicação entre backend e app mobile.
* **OColecionadorFrontEnd (#75)** – Estrutura consolidada do front-end web, integrando o dashboard e a API principal.

### Outubro de 2025

* **OColecionadorClassifier (#71)** – Inclusão do módulo de classificação automatizada de imagens.
* **OColecionadorTraining (#70)** – Adição do módulo de treinamento de modelos de IA para reconhecimento de itens colecionáveis.
* **Estrutura Mobile (#67)** – Criação da base do aplicativo mobile em React Native/Expo, conectado à API principal.
* **CI/CD BackEnd and Augmentations (#66)** – Configuração dos pipelines de integração e entrega contínua para backend e serviços de augmentations.

### Setembro de 2025

* **AddAugmentations / EstruturaInicialProcessoDeAugmentations** – Adição do pipeline de “image augmentation” para treinar e aumentar a base de dados de imagens.
* **Merge: EstruturaAugmentations (#65)** – Integração final da estrutura de augmentations ao projeto principal.
* **Merge: EstruturaAPI (#64)** – Estrutura inicial da API backend consolidada.
* **Merge: LocalServer (#63)** – Adição do ambiente local com Docker Compose para desenvolvimento e testes integrados.

---

## 🛠️ **Melhorias e Alterações**

### Outubro de 2025

* **Personalizar Release / GH_PAT / Deploy (#73)** – Configuração de publicações automatizadas e deploy contínuo.
* **Atualizar ReadMe** – Atualização da documentação principal do projeto com novas instruções e dependências.
* **CorrigirDiagrama** – Correção do diagrama de arquitetura e fluxos entre módulos.

### Setembro de 2025

* **DockerFilePythonVersion / RemoverServiceosDocker / removerDoker** – Ajustes na configuração Docker e simplificação da estrutura de serviços.

---

## 🧩 **Monitoramento e Observabilidade**

### Outubro de 2025

* **ConfigSentry (#69)** – Configuração inicial do Sentry para rastreamento de erros e logs.
* **MonitoramentoSentry (#68)** – Implementação do monitoramento ativo com envio de eventos e métricas.

---

## 📘 **Documentação**

* **Atualizações em README.md** (Março, Agosto, Outubro) – Revisões e melhorias nas instruções de instalação, execução e arquitetura do projeto.

---

## 🧹 **Correções e Refatorações Gerais**

* Ajustes em scripts de CI/CD.
* Correções de inconsistências em módulos de Docker e serviços auxiliares.
* Padronização de nomes de commits e módulos.

---

## 🎯 **Resumo Final do Estado do Projeto (Novembro 2025)**

* Projeto consolidado em **arquitetura modular**, com os seguintes componentes principais:

  * `OColecionadorBackEnd` (API em .NET 8)
  * `OColecionadorFrontEnd` (Dashboard em React)
  * `OColecionadorMobile` (App mobile em React Native)
  * `OColecionadorClassifier` e `OColecionadorTraining` (módulos de IA)
  * `OColecionadorAugmentations` (pré-processamento e aumento de dataset)
  * `LocalServer` (ambiente Docker completo)
* Sistema de **monitoramento ativo (Sentry)** e pipelines de **CI/CD configurados**.
* Base pronta para **releases automatizadas** via GitHub Actions.
* Projeto atingiu um estado de **funcionalidade completa**, com integração ponta-a-ponta entre backend, mobile e IA.

---

✍️ **Autor principal:** [@PatrickCalorioCarvalho](https://github.com/PatrickCalorioCarvalho)
📦 **Último commit relevante:** `DashBoardFrontEnd (#77)` – *04 de novembro de 2025*
