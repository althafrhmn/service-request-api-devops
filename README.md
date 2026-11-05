# Service Request Management API

A DevOps portfolio project: a REST API that is tested, containerized, security-scanned and deployed to Kubernetes through an automated pipeline.

## Tech Stack

- Python and FastAPI
- pytest
- Docker
- GitHub Actions (CI)
- GitHub Container Registry (GHCR)
- Trivy (image vulnerability scanning)
- Kubernetes (Minikube)

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/requests` | Create a service request |
| GET | `/requests` | List all requests |
| GET | `/requests/{request_id}` | Get one request |
| PATCH | `/requests/{request_id}/status` | Update request status |
| DELETE | `/requests/{request_id}` | Delete a request |

Interactive docs are available at `/docs`. No database is used yet.

## Run Locally

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python -m pytest -v
    uvicorn app.main:app --reload

## Run with Docker

    docker build -t service-request-api .
    docker run -p 8000:8000 service-request-api

## CI Pipeline (GitHub Actions)

On every push to `main`:

1. Run pytest
2. Build the Docker image
3. Scan the image with Trivy
4. Push the image to GHCR (only if the scan passes)

## Deploy to Kubernetes (Minikube)

    kubectl apply -f k8s/
    kubectl port-forward service/service-request-api 8080:80

Open http://localhost:8080/docs

The Deployment uses readiness and liveness probes on `/health`, plus CPU and memory limits.

## Security Scanning

The pipeline fails only on fixable HIGH/CRITICAL vulnerabilities
(`--ignore-unfixed --severity HIGH,CRITICAL`).

- **Fixed:** pip 26.3 and setuptools 84.2.1 upgrades, and Debian package updates through `apt-get upgrade`.
- **False positive:** Trivy reports setuptools 70.3.0 from pip's bundled SBOM (`pip/_vendor/bom.cdx.json`). The installed setuptools is 84.2.1, and the flagged code is not in the image. This one file is excluded with `skip-files`.
- **Accepted risk:** Debian findings with no upstream fix yet. The pipeline will start failing on them once a fix is published.

## Project Structure

    app/                FastAPI application
    tests/              pytest tests
    k8s/                Kubernetes manifests
    .github/workflows/  CI pipeline
    Dockerfile          Container image

## Roadmap

- [ ] Prometheus and Grafana monitoring
- [ ] Deploy to Kubernetes from the pipeline
- [ ] Persistent storage (database) before scaling beyond 1 replica
- [ ] Separate dev dependencies (pytest) from the runtime image