# Python GDrive Uploader

A Python 3.12 application packaged as a multi-architecture Docker image and automatically published to Docker Hub via GitHub Actions.

---

## 🚀 Features

* Python **3.12**
* Docker multi-arch builds (`linux/amd64`, `linux/arm64`)
* Automatic Docker Hub publishing on release
* Devcontainer support for consistent local development

---

## 🧱 Tech Stack

* Python 3.12
* Docker + Buildx

---

# 🛠 Local Development

## 1️⃣ Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

---

# 🐳 Build Docker Image Locally

```bash
docker build -t <your-dockerhub-username>/<repo-name>:latest .
```

Example:

```bash
docker build -t ryuunosukeds3/hello-world-frontend:latest .
```

---

# 🐳 Multi-Arch Build (Like CI)

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t <your-dockerhub-username>/<repo-name>:latest \
  --push .
```

# 🧪 Devcontainer Support

This project supports VS Code Dev Containers with:

* Python 3.12 feature
* Node (if needed)
* Docker outside of Docker

Rebuild container:

```
Dev Containers: Rebuild Without Cache
```
