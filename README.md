````markdown
# 🎬 Movie Sentiment Classification — End-to-End MLOps

An end-to-end Machine Learning and MLOps project that classifies movie reviews as **positive or negative** and demonstrates the complete journey from ML development to **automated CI/CD and production deployment on Amazon EKS**.

The project integrates **DVC, MLflow, DagsHub, Flask, Docker, GitHub Actions, Amazon ECR, Kubernetes, and Amazon EKS** into a reproducible production-style ML workflow.

---

## 🎥 Project Demo

> **Live production API deployed on Amazon EKS**

<!-- Add your screen recording/video/GIF here -->

📺 **Demo:** `Coming soon`

The demo shows:

- ML pipeline execution with DVC
- Experiment/model tracking with MLflow and DagsHub
- Flask API
- Docker containerization
- GitHub Actions CI/CD
- Amazon ECR
- Amazon EKS
- Kubernetes deployment
- AWS Load Balancer
- Live sentiment prediction

---

## 🚀 Live API

The application is deployed on **Amazon EKS** and exposed through an AWS Load Balancer.

### Prediction endpoint

```text
POST /predict
````

Example:

```json
{
  "text": "This movie was absolutely fantastic and I loved it"
}
```

The request travels through:

```text
Internet
   ↓
AWS Load Balancer
   ↓
Kubernetes Service
   ↓
EKS Pod
   ↓
Flask API
   ↓
MLflow Model
   ↓
Sentiment Prediction
```

> ⚠️ The live endpoint may change when the AWS infrastructure is recreated.

---

# 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │       GitHub         │
                         │  Source Code + Git   │
                         └──────────┬───────────┘
                                    │
                                  Push
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   GitHub Actions     │
                         │      CI / CD         │
                         └──────────┬───────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
         DVC Pipeline          Unit Tests         Docker Build
                │                                       │
                ▼                                       ▼
         MLflow / DagsHub                           Amazon ECR
                │                                       │
                │                                       ▼
                │                                  Docker Image
                │                                       │
                └───────────────────────┐               │
                                        │               │
                                        ▼               ▼
                                  ┌─────────────────────────┐
                                  │       Amazon EKS        │
                                  │                         │
                                  │   ┌───────┐ ┌───────┐  │
                                  │   │ Pod 1 │ │ Pod 2 │  │
                                  │   └───┬───┘ └───┬───┘  │
                                  │       │         │      │
                                  │       └────┬────┘      │
                                  │            │           │
                                  │     Kubernetes Service │
                                  └────────────┬────────────┘
                                               │
                                               ▼
                                      AWS Load Balancer
                                               │
                                               ▼
                                        Public REST API
                                               │
                                               ▼
                                      Sentiment Prediction
```

---

# 🎯 Project Objectives

This project demonstrates how to take a machine learning model beyond a notebook and deploy it as a production-style application.

The main objectives are:

* Build a reproducible ML pipeline
* Version datasets and pipeline stages with DVC
* Track experiments with MLflow
* Register and manage ML models
* Serve the model through Flask
* Containerize the application with Docker
* Automate testing and deployment with GitHub Actions
* Store Docker images in Amazon ECR
* Deploy the application to Amazon EKS
* Run multiple Kubernetes replicas
* Expose the application through an AWS Load Balancer
* Serve real-time sentiment predictions through a REST API

---

# 🧠 Machine Learning Pipeline

The ML workflow is organized into reproducible DVC stages.

```text
Data Ingestion
      ↓
Data Preprocessing
      ↓
Feature Engineering
      ↓
Model Building
      ↓
Model Evaluation
      ↓
Model Registration
```

DVC allows the pipeline to be reproduced using:

```bash
dvc repro
```

The pipeline can also be visualized using:

```bash
dvc dag
```

---

# 📊 Experiment Tracking & Model Registry

The project uses **MLflow with DagsHub** for experiment tracking and model management.

MLflow is used for:

* Experiment tracking
* Metrics
* Model artifacts
* Model registration
* Production model management

The application loads the production model using the MLflow model registry.

Example model URI:

```text
models:/my_model@champion
```

This allows the Flask application to retrieve the model designated as the production/champion model rather than hard-coding a local model file.

---

# 🌐 Flask ML API

The trained model is served through a Flask REST API.

### Prediction endpoint

```text
POST /predict
```

Example request:

```json
{
  "text": "This movie was fantastic and entertaining"
}
```

Example negative review:

```json
{
  "text": "This movie was boring and disappointing"
}
```

The API performs the required text preprocessing before passing the processed input to the trained model.

The preprocessing pipeline includes operations such as:

* Lowercasing
* Stop-word removal
* Number removal
* Punctuation removal
* URL removal
* Lemmatization

---

# 🐳 Docker

The Flask application is containerized using Docker.

The Docker image contains:

* Python runtime
* ML dependencies
* Flask
* Gunicorn
* NLTK resources
* MLflow dependencies
* Application source code

The application runs on:

```text
Port: 5000
```

The container starts the Flask application using Gunicorn.

---

# 🔄 CI/CD Pipeline

GitHub Actions automates the build, test, and deployment workflow.

The pipeline performs the following steps:

```text
Git Push
   ↓
Checkout Repository
   ↓
Install Python / uv
   ↓
Install Dependencies
   ↓
Run DVC Pipeline
   ↓
Run Tests
   ↓
Register / Promote Model
   ↓
Build Docker Image
   ↓
Push Image to Amazon ECR
   ↓
Configure kubectl
   ↓
Connect to Amazon EKS
   ↓
Create / Update Kubernetes Secrets
   ↓
Deploy Application
   ↓
Rolling Deployment
   ↓
Verify Deployment
```

This allows application changes to move automatically from source control to the Kubernetes environment.

---

# ☁️ AWS Infrastructure

The application is deployed using AWS services.

## Amazon ECR

Amazon Elastic Container Registry stores the Docker image.

Repository:

```text
movie-sentiment-classification
```

Image:

```text
movie-sentiment-classification:latest
```

---

## Amazon EKS

The application runs on an Amazon EKS cluster.

Cluster:

```text
flask-app-cluster
```

Managed node group:

```text
flask-app-nodes
```

The application is deployed with multiple replicas.

Current deployment configuration:

```text
Replicas: 2
```

---

# ☸️ Kubernetes

The application is deployed using Kubernetes resources.

### Deployment

```text
flask-app
```

The Deployment maintains two application replicas.

### Service

```text
flask-app-service
```

Service type:

```text
LoadBalancer
```

The Service exposes the Flask application externally through an AWS Load Balancer.

### Kubernetes architecture

```text
                 AWS Load Balancer
                         │
                         ▼
               flask-app-service
                         │
                ┌────────┴────────┐
                ▼                 ▼
             Pod 1             Pod 2
                │                 │
                └────────┬────────┘
                         ▼
                    Flask API
```

---

# 🔐 Secrets & Security

Sensitive credentials are not stored directly in the source code.

The project uses environment variables and Kubernetes Secrets for sensitive values such as:

```text
DAGSHUB_TOKEN
```

The Kubernetes application retrieves the token through:

```yaml
env:
  - name: DAGSHUB_TOKEN
    valueFrom:
      secretKeyRef:
        name: dagshub-secret
        key: DAGSHUB_TOKEN
```

AWS credentials used by CI/CD are stored as GitHub Actions secrets.

> Never commit credentials, API keys, AWS access keys, or DagsHub tokens to the repository.

---

# 📁 Project Structure

```text
Movie-Sentiment-Classification/
│
├── .github/
│   └── workflows/
│       └── ci.yaml
│
├── data/
│
├── flask_app/
│   └── app.py
│
├── models/
│   └── vectorizer.pkl
│
├── notebooks/
│
├── scripts/
│   └── promote_model.py
│
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── ...
│
├── tests/
│   ├── test_model.py
│   └── test_flask_app.py
│
├── Dockerfile
├── deployment.yaml
├── dvc.yaml
├── dvc.lock
├── params.yaml
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

---

# 🛠️ Technology Stack

| Category                | Technology        |
| ----------------------- | ----------------- |
| Programming Language    | Python            |
| Machine Learning        | Scikit-learn      |
| API                     | Flask             |
| Application Server      | Gunicorn          |
| Data Versioning         | DVC               |
| Experiment Tracking     | MLflow            |
| ML Platform             | DagsHub           |
| Dependency Management   | uv                |
| Containerization        | Docker            |
| CI/CD                   | GitHub Actions    |
| Container Registry      | Amazon ECR        |
| Cloud                   | AWS               |
| Container Orchestration | Kubernetes        |
| Kubernetes Platform     | Amazon EKS        |
| Load Balancing          | AWS Load Balancer |
| Testing                 | Python unittest   |

---

# ⚙️ Local Setup

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Movie-Sentiment-Classification
```

## 2. Install dependencies

Using `uv`:

```bash
uv sync
```

## 3. Configure DagsHub credentials

Set:

```text
DAGSHUB_TOKEN
```

as an environment variable.

Do not put the token directly in the source code.

## 4. Run the DVC pipeline

```bash
uv run dvc repro
```

## 5. Run tests

```bash
uv run python -m unittest discover
```

## 6. Run the Flask application

```bash
uv run gunicorn --bind 0.0.0.0:5000 flask_app.app:app
```

The API will be available at:

```text
http://localhost:5000
```

---

# 🐳 Run with Docker

Build the image:

```bash
docker build -t movie-sentiment-classification .
```

Run the container:

```bash
docker run -p 5000:5000 \
  -e DAGSHUB_TOKEN=<YOUR_TOKEN> \
  movie-sentiment-classification
```

The API will be available at:

```text
http://localhost:5000
```

---

# ☸️ Kubernetes Deployment

Configure AWS credentials and connect to the EKS cluster:

```bash
aws eks update-kubeconfig \
  --region us-east-1 \
  --name flask-app-cluster
```

Create the Kubernetes secret:

```bash
kubectl create secret generic dagshub-secret \
  --from-literal=DAGSHUB_TOKEN=<YOUR_TOKEN> \
  --dry-run=client -o yaml | kubectl apply -f -
```

Deploy:

```bash
kubectl apply -f deployment.yaml
```

Check Pods:

```bash
kubectl get pods
```

Check Deployment:

```bash
kubectl get deployment
```

Check Service:

```bash
kubectl get service
```

Check rollout:

```bash
kubectl rollout status deployment/flask-app
```

---

# 🧪 API Testing

Example request:

```bash
curl -X POST http://<LOAD_BALANCER_DNS>:5000/predict \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"This movie was fantastic and I loved it\"}"
```

Example PowerShell:

```powershell
Invoke-RestMethod `
  -Uri "http://<LOAD_BALANCER_DNS>:5000/predict" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"text":"This movie was fantastic and I loved it"}'
```

---

# 📈 Monitoring

The Flask application exposes Prometheus metrics through:

```text
/metrics
```

This provides a foundation for integrating Prometheus and Grafana for application monitoring.

Future monitoring improvements include:

* Request rate
* Request latency
* Error rate
* CPU utilization
* Memory utilization
* Pod availability
* Model prediction monitoring
* Data/model drift monitoring

---

# 🔮 Future Improvements

The current system can be further improved with:

* [ ] Kubernetes readiness probes
* [ ] Kubernetes liveness probes
* [ ] Horizontal Pod Autoscaler
* [ ] Prometheus
* [ ] Grafana
* [ ] HTTPS/TLS
* [ ] Custom domain
* [ ] AWS Application Load Balancer configuration
* [ ] Immutable Docker image tags using Git commit SHA
* [ ] GitHub Actions → AWS OIDC authentication
* [ ] Model drift detection
* [ ] Data drift monitoring
* [ ] Automated model retraining
* [ ] Canary / blue-green deployments
* [ ] Centralized logging
* [ ] Distributed tracing

---

# 📚 Key MLOps Concepts Demonstrated

This project demonstrates practical experience with:

### Machine Learning

* NLP preprocessing
* Feature engineering
* Model training
* Model evaluation
* Model registration

### MLOps

* Reproducible pipelines
* Data versioning
* Experiment tracking
* Model registry
* Model serving
* CI/CD
* Containerization
* Model deployment

### Cloud & DevOps

* Docker
* Amazon ECR
* Amazon EKS
* Kubernetes
* IAM
* AWS Load Balancer
* GitHub Actions

---

# 💡 What This Project Demonstrates

This project goes beyond training a machine learning model in a notebook.

It demonstrates how to take an ML model through the complete lifecycle:

```text
Development
     ↓
Data Pipeline
     ↓
Experiment Tracking
     ↓
Model Registry
     ↓
Model Serving
     ↓
Containerization
     ↓
CI/CD
     ↓
Cloud Deployment
     ↓
Kubernetes
     ↓
Public ML API
```

The final result is a **containerized machine learning API running on Amazon EKS and accessible through an AWS Load Balancer**.

---

# 👨‍💻 Author

**Bapun Suna**

MSc Computer Science | Machine Learning | MLOps | AI

Interested in:

* Machine Learning
* Deep Learning
* MLOps
* LLMOps
* Agentic AI
* Cloud Computing
* Kubernetes
* Production AI Systems

---

## ⭐ If you found this project useful

Consider giving the repository a ⭐ and exploring the implementation.

```text
Machine Learning → MLOps → Cloud → Kubernetes → Production
```
