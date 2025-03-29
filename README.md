# OColecionador - Projeto de Classificação de Imagens com MinIO e TensorFlow

## Descrição
O **OColecionador** tem como objetivo capturar imagens pelo aplicativo mobile (React Native), enviá-las para um backend em Node.js, armazená-las em um bucket no MinIO e gerar automaticamente variações dessas imagens (rotação e mudança de coloração) para treinamento de um modelo de classificação com Python e TensorFlow. O modelo treinado pode ser utilizado posteriormente pelo backend ou por outro serviço para classificação automática de imagens.

## Tecnologias Utilizadas
- **Frontend**: React Native
- **Backend**: Node.js
- **Armazenamento**: MinIO
- **Processamento e Treinamento**: Python, TensorFlow

## Fluxo do Sistema
1. O usuário captura uma imagem pelo aplicativo React Native.
2. A imagem é enviada para o backend Node.js.
3. O backend salva a imagem original em um bucket no MinIO.
4. O backend gera variações da imagem (rotação e coloração) e as armazena em outro bucket no MinIO.
5. Um processo de treinamento em Python e TensorFlow consome essas imagens para gerar um modelo de classificação.
6. O modelo treinado pode ser utilizado pelo backend ou outro serviço para classificação automática de novas imagens enviadas.

## Diagrama do Fluxo do Sistema

```mermaid
graph TD;
    A[Usuário captura imagem no app] --> B[Envio para Backend Node.js]
    B --> C[Salvamento no MinIO - Bucket Original]
    B --> D[Geração de variações]
    D --> E[Salvamento no MinIO - Bucket Processado]
    E --> F[Treinamento do modelo com TensorFlow]
    F --> G[Modelo de Classificação Treinado]
    G --> H[Uso do modelo para classificação automática]
```

## Conclusão
O **OColecionador** fornece um pipeline completo para captura, armazenamento, processamento, treinamento e classificação de imagens. Com a automação da geração de variações das imagens, garantimos um conjunto de dados mais robusto para o treinamento do modelo de classificação.
