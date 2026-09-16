# Bengaluru Rental Property AI Agent

A FastAPI web application for searching Bengaluru rental listings, comparing commute estimates, and calculating move-in costs.

## Features

- Filter sample listings by BHK, rent, locality, furnishing, and work location.
- View commute, metro, parking, water reliability, and verification details.
- Calculate monthly costs, initial move-in cost, deposit ratio, annual projection, and estimated savings.
- Serve the web UI and API from one FastAPI service.
- Run locally with Python, Docker Compose, or Kubernetes manifests.

## Requirements

- Python 3.11 or newer
- Git
- Docker Desktop, only if using Docker
- A Kubernetes cluster and `kubectl`, only if deploying to Kubernetes

## 1. Get the code

```bash
git clone https://github.com/Shekh1995/bengaluru-rental-agent-app-test.git
cd bengaluru-rental-agent-app-test
```

On Windows PowerShell, use the same commands from the directory where you want to store the project.

## 2. Create a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If PowerShell blocks activation, run this once in the current PowerShell session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 3. Install dependencies

Install runtime and development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## 4. Run the tests

Run all tests from the repository root:

```bash
python -m pytest -q
```

The test suite covers health/readiness endpoints, the web UI, property filtering, the calculation API, and calculator business rules.

## 5. Start the application locally

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

After the server starts, open these links on the same computer:

- [Web UI](http://127.0.0.1:8000/)
- [Interactive API documentation](http://127.0.0.1:8000/docs)
- [Health check](http://127.0.0.1:8000/health)
- [Readiness check](http://127.0.0.1:8000/ready)

Stop the development server with `Ctrl+C`.

## 6. Run with Docker Compose

Make sure Docker Desktop is running, then execute:

```bash
docker compose up --build -d
```

After the container starts, open the [Docker web UI](http://127.0.0.1:8000/) and check the container health:

```bash
docker compose ps
docker compose logs -f rental-agent
```

Stop and remove the container:

```bash
docker compose down
```

## 7. Deploy to Kubernetes

The CI workflow publishes the image using this repository-based name:

```text
ghcr.io/shekh1995/bengaluru-rental-agent-app-test/bengaluru-rental-agent:latest
```

Update the `image` value in [`k8s/deployment.yaml`](k8s/deployment.yaml) to the published image before deploying. The GitHub Container Registry package must be public, or your cluster must have an image pull secret.

Apply the manifests from the repository root:

```bash
kubectl apply -f ./k8s/deployment.yaml
kubectl apply -f ./k8s/service.yaml
kubectl apply -f ./k8s/ingress.yaml
```

Check the rollout and service:

```bash
kubectl rollout status deployment/bengaluru-rental-agent
kubectl get pods,service,ingress
```

The deployment exposes port `8000` inside the container. The Kubernetes service exposes it on port `80`.

## API examples

List properties after starting the application:

[GET /api/properties](http://127.0.0.1:8000/api/properties)

Filter by BHK and maximum rent:

[Filter properties by BHK and rent](http://127.0.0.1:8000/api/properties?bhk=2&max_rent=35000)

Calculate move-in costs:

```bash
curl -X POST http://127.0.0.1:8000/api/calculate \
	-H "Content-Type: application/json" \
	-d '{"rent_monthly":28000,"deposit":120000,"maintenance":2000}'
```

## Project structure

- [`app/main.py`](app/main.py): FastAPI application and routes
- [`app/models.py`](app/models.py): Pydantic request and response models
- [`app/services/property_service.py`](app/services/property_service.py): Listing data and filtering
- [`app/services/calculator_service.py`](app/services/calculator_service.py): Move-in cost calculations
- [`app/static/`](app/static/): HTML, CSS, and browser JavaScript
- [`tests/`](tests/): API and business-logic tests
- [`k8s/`](k8s/): Kubernetes manifests
- [`Dockerfile`](Dockerfile): Multi-stage production image
- [`docker-compose.yml`](docker-compose.yml): Local container orchestration

## Continuous integration

The workflow in `.github/workflows/ci-cd.yml` runs on pushes and pull requests targeting `main` or `master`. It:

1. Installs Python dependencies.
2. Runs Flake8 checks and the Pytest suite with coverage.
3. Builds and, for non-pull-request pushes, publishes a Docker image to GitHub Container Registry.
4. Runs a Trivy filesystem security scan.
5. Counts and validates the Kubernetes manifest files for the staging verification job.

The workflow does not configure cluster credentials or perform a live Kubernetes rollout. Kubernetes deployment remains a separate step using the manifests above.
