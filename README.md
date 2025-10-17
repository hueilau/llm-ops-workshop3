# LLMOps Pipeline - End-to-End FastAPI Deployment

This project demonstrates a complete LLMOps pipeline using FastAPI, Docker, Kubernetes, and GitHub Actions.

## 🚀 Features

- **FastAPI Application**: Question-answering service using Hugging Face transformers
- **Docker Containerization**: Production-ready Docker setup
- **Kubernetes Deployment**: Scalable container orchestration
- **Security Scanning**: Trivy vulnerability scanning
- **CI/CD Pipeline**: Automated GitHub Actions workflow

## 📋 Prerequisites

- Docker Hub account
- Kubernetes cluster (local or cloud)
- GitHub repository with secrets configured

## 🔧 Setup Instructions

### 1. Configure GitHub Secrets

In your GitHub repository, go to Settings > Secrets and variables > Actions, and add:

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_TOKEN`: Your Docker Hub access token (recommended) or personal access token
- `KUBECONFIG`: Base64 encoded kubeconfig file for your Kubernetes cluster

#### How to create a Docker Hub Access Token:
1. Log in to [Docker Hub](https://hub.docker.com/)
2. Go to Account Settings > Security
3. Click "New Access Token"
4. Give it a name (e.g., "GitHub Actions")
5. Select permissions: Read, Write, Delete
6. Copy the generated token and add it as `DOCKER_TOKEN` secret in GitHub

### 2. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Test the API
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is FastAPI?",
    "context": "FastAPI is a modern, fast web framework for building APIs with Python 3.6+."
  }'
```

### 3. Docker Build and Run

```bash
# Build the image
docker build -t fastapi-app .

# Run the container
docker run -p 8000:8000 fastapi-app

# Health check
curl http://localhost:8000/health
```

### 4. Kubernetes Deployment

```bash
# Apply the manifests
kubectl apply -f deployment.yml
kubectl apply -f service.yml

# Check deployment status
kubectl rollout status deployment/gpt-huggingface
kubectl get services gpt-hf-service
```

## 🧪 AI Safety & Testing

### Comprehensive Testing Strategy
- **Unit Tests**: API functionality, error handling, performance
- **Hallucination Detection**: Prevents false information generation
- **Bias Testing**: Detects gender, cultural, and demographic biases
- **Context Grounding**: Ensures answers align with provided context

### Running Tests Locally
```bash
# Unit tests
pytest test_main.py -v --cov=main

# AI Safety tests (requires service running)
python main.py &
./run-promptfoo-tests.sh
```

See [TESTING.md](TESTING.md) for detailed testing documentation.

## 🔄 CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **Test**: Unit tests and AI safety validation (Promptfoo)
2. **Build & Push**: Creates Docker image and pushes to Docker Hub  
3. **Security Scan**: Scans image with Trivy for vulnerabilities
4. **Deploy**: Deploys to Kubernetes cluster
5. **Validate**: Post-deployment safety and health checks

## 📊 API Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check endpoint
- `POST /chat`: Question-answering endpoint

## 🛡️ Security Features

- Non-root container execution
- Resource limits and requests
- Security context configurations
- Automated vulnerability scanning
- No privilege escalation

## 🏗️ Architecture

```
GitHub Repository
    ↓
GitHub Actions Pipeline
    ↓
Docker Hub Registry
    ↓
Kubernetes Cluster
    ↓
FastAPI Application
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass
5. Submit a pull request