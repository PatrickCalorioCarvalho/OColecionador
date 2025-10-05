# Guia de Instalação do Servidor Local para Desenvolvimento

## Informações de Sistema e Hardware

- **Sistema Operacional:** [Ubuntu Server 24.04.3](https://ubuntu.com/download/server/thank-you?version=24.04.3&architecture=amd64&lts=true)
- **CPU:** Intel i5-3330 3.00GHz
- **Memória:** 2x 8GB DDR3 1333 MHz  
- **Armazenamento:** SSD M.2 240GB
- **GPU:** GeForce GTX 750 Ti

---

## 1. Atualização dos Pacotes do Sistema

```shell
sudo apt update && sudo apt upgrade -y
```

---

## 2. Instalação do Docker

```shell
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER
newgrp docker
```

### Teste do Docker

```shell
sudo docker run hello-world
```

---

## 3. Instalação do Driver NVIDIA para GTX 750 Ti

```shell
sudo apt purge -y nvidia-*
sudo add-apt-repository ppa:graphics-drivers/ppa -y
sudo apt update
sudo apt install -y nvidia-driver-470
sudo reboot
```

---

## 4. Instalação do NVIDIA Container Toolkit

```shell
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit.gpg

distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit.gpg] https://#' | \
  sudo tee /etc/apt/sources.list.d/libnvidia-container.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

---

## 5. Teste do Docker com GPU

```shell
docker run --rm --gpus all nvidia/cuda:11.4.3-base-ubuntu20.04 nvidia-smi
```

---

## 6. Teste do TensorFlow com GPU

```shell
docker run -it --gpus all tensorflow/tensorflow:2.4.1-gpu python
```

No terminal Python, execute:

```python
import tensorflow as tf

print("TensorFlow versão:", tf.__version__)
print("GPUs disponíveis:", tf.config.list_physical_devices('GPU'))
print(tf.test.is_gpu_available())
print(tf.test.is_built_with_cuda())
```

---

## 7. Instalação do GitHub Actions Runner

```shell
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.328.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.328.0/actions-runner-linux-x64-2.328.0.tar.gz

echo "01066fad3a2893e63e6ca880ae3a1fad5bf9329d60e77ee15f2b97c148c3cd4e  actions-runner-linux-x64-2.328.0.tar.gz" | shasum -a 256 -c
tar xzf ./actions-runner-linux-x64-2.328.0.tar.gz

./config.sh --url https://github.com/PatrickCalorioCarvalho/OColecionador --token SEU_TOKEN

sudo ./svc.sh install
sudo ./svc.sh start
```

---

## Observações

- Substitua `SEU_TOKEN` pelo token gerado no GitHub Actions.
- Reinicie o sistema após instalar o driver NVIDIA.
- Certifique-se de que o usuário atual está no grupo `docker` para evitar problemas de permissão.
- Criar usuario sentry docker compose run --rm sentry createuser --superuser
---

**Referências:**
- [Documentação Oficial Docker](https://docs.docker.com/engine/install/ubuntu/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- [GitHub Actions Runner](https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners)