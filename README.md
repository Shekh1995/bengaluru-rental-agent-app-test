# 🏢 Bengaluru Rental Property AI Agent — Pipeline Deployable Web App

A production-ready, cloud-native web application and microservice for automated rental property research, deal calculations, and commute intelligence across Bengaluru.

---

## 🚀 Key Features

* **⚡ Interactive UI Dashboard:** Real-time property search, filtering by budget, BHK, locality, and tech hub commute times.
* **💰 Financial Move-In Calculator:** Instant calculation of initial move-in outlay, deposit-to-rent multiplier, and annual savings projection vs. tech corridor market rates.
* **🛡️ Pre-Token Verification System:** Direct verification flags and checks for water source, municipal electricity sub-meter, and direct owner listings.
* **🐳 Docker Multi-Stage Build:** Minimal, non-root `python:3.11-slim` image equipped with healthcheck probes.
* **⚙️ GitHub Actions CI/CD Pipeline:** Fully automated workflow running linting (`flake8`), unit & integration tests (`pytest`), container build & push (`ghcr.io` / Docker Hub), and Kubernetes manifest linting.
* **☸️ Kubernetes Ready:** Out-of-the-box manifests for `Deployment`, `Service`, and `Ingress` with liveness and readiness probes.

---

## 📂 Project Structure

```
bengaluru-rental-agent-app/
├── .github/
│   └── workflows/
│       └── ci-cd.yml             # GitHub Actions CI/CD pipeline
├── app/
│   ├── main.py                   # FastAPI REST API & static file serving
│   ├── models.py                 # Pydantic schemas
│   ├── services/
│   │   ├── property_service.py   # Property catalog & filtering logic
│   │   └── calculator_service.py # Move-in & deposit financial algorithms
│   └── static/
│       ├── index.html            # Single-page application UI
│       ├── app.js                # Frontend state & async API client
│       └── styles.css            # Responsive dark/modern styles
├── k8s/
│   ├── deployment.yaml           # Kubernetes Deployment manifest
│   ├── service.yaml              # Kubernetes Service manifest
│   └── ingress.yaml              # Kubernetes Ingress manifest
├── tests/
│   ├── test_api.py               # API endpoint integration tests
│   └── test_calculator.py        # Calculator business logic unit tests
├── Dockerfile                    # Multi-stage production container build
├── docker-compose.yml            # Local orchestration
├── requirements.txt              # Production runtime dependencies
└── requirements-dev.txt          # Testing & linting dependencies
```

---

## 🛠️ Local Development & Testing

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Run Test Suite
```bash
pytest -v tests/
```

### 3. Run Web App Locally
```bash
uvicorn app.main:app --reload --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🐳 Docker Deployment

### Run via Docker Compose:
```bash
docker compose up --build -d
```

### Inspect Container Logs:
```bash
docker compose logs -f
```

---

## 🚀 CI/CD Pipeline (GitHub Actions)

When pushed to a GitHub repository, the pipeline automatically triggers:

1. **Test & Lint:** Executes `flake8` and runs `pytest` test suite.
2. **Build & Push:** Builds multi-stage Docker container and publishes it to GitHub Container Registry (`ghcr.io`).
3. **Security Scan:** Runs `Trivy` to audit the container against CVE vulnerabilities.
4. **Deploy Staging:** Validates Kubernetes manifests and triggers target cluster rolling update.
