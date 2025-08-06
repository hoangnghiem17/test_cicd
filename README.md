# CI/CD Pipeline Implementation with GitHub Actions

A complete CI/CD pipeline implementation using GitHub Actions, simulating real-world AI-based service deployment with Git-Flow branching model.

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Project Structure](#2-project-structure)
3. [CI Pipeline (Pull Request Validation)](#3-ci-pipeline-pull-request-validation)
4. [CD-Test Pipeline (Develop Branch Deployment)](#4-cd-test-pipeline-develop-branch-deployment)
5. [CD-Prod Pipeline (Production Deployment)](#5-cd-prod-pipeline-production-deployment)
6. [Git-Flow and SHA Management](#6-git-flow-and-sha-management)
7. [Docker Configuration](#7-docker-configuration)
8. [GitHub Container Registry Setup](#8-github-container-registry-setup)
9. [Manual Approval Gates](#9-manual-approval-gates)
10. [Testing and Validation](#10-testing-and-validation)

---

## 1. Architecture Overview

### Pipeline Flow
```
Feature Branch → PR to develop → CI Pipeline → Merge → CD-Test Pipeline → CD-Prod Pipeline (with approval)
```

### Key Components
- **CI Pipeline**: Code validation, linting, testing, Docker build verification
- **CD-Test Pipeline**: Build, tag, and push Docker images to registry
- **CD-Prod Pipeline**: Pull tested images and deploy to production with manual approval
- **Git-Flow**: Feature branches → develop → main
- **SHA-based Versioning**: Ensures exact image traceability across environments

### Technology Stack
- **Platform**: GitHub.com with GitHub Actions
- **Runtime**: GitHub-hosted Ubuntu runners
- **Language**: Python 3.9 with Poetry dependency management
- **Containerization**: Docker with multi-platform support (linux/amd64)
- **Registry**: GitHub Container Registry (GHCR)
- **Quality Tools**: flake8 (linting), pytest (testing)

---

## 2. Project Structure

```
test_cicd/
├── .github/workflows/
│   ├── ci.yml              # CI Pipeline (PR validation)
│   ├── cd_test.yml         # CD-Test Pipeline (develop deployment)
│   └── cd_prod.yml         # CD-Prod Pipeline (production deployment)
├── tests/
│   └── test_app.py         # Unit tests
├── app.py                  # Main application
├── Dockerfile              # Container configuration
├── pyproject.toml          # Poetry project configuration
├── poetry.lock             # Dependency lock file
└── README.md               # This documentation
```

### Application Components

**app.py**: Minimal Python application simulating an AI service
- HTTP client using `requests` library
- Persistent execution with 60-second intervals
- Demonstrates dependency management and container persistence

**tests/test_app.py**: Unit tests validating application logic
- Tests the `fetch_greeting()` function
- Ensures CI pipeline validates actual code functionality

---

## 3. CI Pipeline (Pull Request Validation)

### Trigger
```yaml
on:
  pull_request:
    branches: [develop]
    types: [opened, synchronize, reopened]
```

### Pipeline Steps

1. **Code Checkout**: Retrieve PR code using `actions/checkout@v2`
2. **Python Setup**: Install Python 3.9 using `actions/setup-python@v2`
3. **Poetry Installation**: Install Poetry dependency manager
4. **Dependency Installation**: `poetry install --no-root`
5. **Code Linting**: Two-stage flake8 validation
   - Critical errors: `E9,F63,F7,F82` (syntax errors, undefined names)
   - Style warnings: complexity and line length checks
6. **Unit Testing**: Execute pytest with proper PYTHONPATH configuration
7. **Docker Build Verification**: Build Docker image for linux/amd64 platform

### Quality Gates
- **Linting**: Must pass critical error checks (E9, F63, F7, F82)
- **Testing**: All pytest tests must pass
- **Docker Build**: Image must build successfully for target platform

### Key Features
- **Non-blocking warnings**: Style issues don't fail the pipeline
- **Platform-specific builds**: Ensures compatibility with deployment environment
- **Dependency validation**: Verifies all requirements can be installed

---

## 4. CD-Test Pipeline (Develop Branch Deployment)

### Trigger
```yaml
on:
  push:
    branches: [develop]
```

### Pipeline Steps

1. **Code Checkout**: Retrieve merged develop branch code
2. **Docker Setup**: Configure Buildx for multi-platform builds
3. **Registry Login**: Authenticate with GitHub Container Registry
4. **SHA Generation**: Extract 7-character commit SHA using `git rev-parse --short HEAD`
5. **Docker Build**: Create linux/amd64 image with `docker buildx build`
6. **Image Tagging**: Tag image with commit SHA: `ghcr.io/REPO/myapp:SHA`
7. **Registry Push**: Upload tagged image to GHCR

### Image Versioning Strategy
- **Format**: `ghcr.io/hoangnghiem17/test_cicd/myapp:SHA`
- **SHA Source**: Commit SHA from develop branch
- **Example**: `ghcr.io/hoangnghiem17/test_cicd/myapp:082866e`

### Key Features
- **Immutable versioning**: Each commit gets unique image tag
- **Platform optimization**: Built specifically for linux/amd64
- **Registry integration**: Automatic push to private GHCR

---

## 5. CD-Prod Pipeline (Production Deployment)

### Trigger
```yaml
on:
  workflow_run:
    workflows: ["CD-Test Pipeline"]
    types: [completed]
```

### Pipeline Steps

1. **Trigger Validation**: Only proceed if CD-Test succeeded on develop branch
2. **Code Checkout**: Retrieve main branch code for deployment context
3. **Docker Setup**: Configure Buildx and login to GHCR
4. **SHA Extraction**: Extract commit SHA from triggering workflow
   ```bash
   GIT_SHA=$(echo "${{ github.event.workflow_run.head_sha }}" | cut -c1-7)
   ```
5. **Image Pull**: Download exact image built and tested in CD-Test
6. **Manual Approval**: Wait for production environment approval
7. **Deployment**: Deploy container with `docker run -d -p 80:80`

### Critical SHA Management
The pipeline uses `github.event.workflow_run.head_sha` to ensure:
- **Same Image**: Pulls exact image that passed CD-Test
- **Traceability**: Deployment uses tested develop branch commit
- **Consistency**: No rebuild, just deployment of verified artifact

### Manual Approval Gate
- **Environment**: `production` with required reviewers
- **Process**: Pipeline pauses before deployment step
- **Security**: Human validation before production changes

---

## 6. Git-Flow and SHA Management

### Branching Strategy
```
feature/xyz → develop → main
     ↓           ↓       ↓
    CI      CD-Test  CD-Prod
```

### SHA Flow Across Pipelines

1. **Developer pushes to develop**: Commit SHA `abc1234`
2. **CD-Test builds image**: Tagged as `myapp:abc1234`
3. **CD-Prod triggers**: Extracts SHA `abc1234` from workflow event
4. **Production deployment**: Pulls and deploys `myapp:abc1234`

### Key Innovation: Cross-Pipeline SHA Passing
```yaml
# CD-Prod extracts SHA from triggering workflow
GIT_SHA=$(echo "${{ github.event.workflow_run.head_sha }}" | cut -c1-7)
```

This ensures CD-Prod deploys the exact image built in CD-Test, maintaining complete traceability.

---

## 7. Docker Configuration

### Dockerfile Structure
```dockerfile
FROM python:3.9-slim
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y curl

# Poetry installation
RUN pip install poetry==1.8.3

# Dependency installation
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

# Application code
COPY . .
EXPOSE 80
CMD ["poetry", "run", "python", "app.py"]
```

### Key Features
- **Multi-stage optimization**: Separate dependency and code layers
- **Poetry integration**: Modern Python dependency management
- **Slim base image**: Minimal attack surface
- **Persistent execution**: Application runs continuously
- **Port exposure**: Ready for production deployment

### Platform Targeting
All builds use `--platform linux/amd64` to ensure consistency across development and production environments.

---

## 8. GitHub Container Registry Setup

### Authentication
- **Token**: Personal Access Token (PAT) with `write:packages` permission
- **Storage**: GitHub secret `CR_PAT`
- **Usage**: All pipelines authenticate using `${{ secrets.CR_PAT }}`

### Repository Configuration
- **Registry**: `ghcr.io`
- **Namespace**: `ghcr.io/hoangnghiem17/test_cicd/myapp`
- **Visibility**: Private (default for personal repositories)

### Image Management
- **Tagging**: SHA-based for immutable versioning
- **Retention**: Images persist for audit and rollback
- **Access**: Controlled via GitHub repository permissions

---

## 9. Manual Approval Gates

### GitHub Environments Configuration
1. **Environment Name**: `production`
2. **Protection Rules**: Required reviewers
3. **Integration**: CD-Prod pipeline references environment
4. **Behavior**: Pipeline pauses at deployment step

### Approval Process
```yaml
environment:
  name: production  # Triggers approval gate
```

When CD-Prod reaches the deployment job:
1. GitHub pauses execution
2. Configured reviewers receive notification
3. Manual approval required to proceed
4. Pipeline resumes after approval

### Security Benefits
- **Human oversight**: Critical production changes require approval
- **Audit trail**: All approvals logged in GitHub
- **Access control**: Only designated reviewers can approve

---

## 10. Testing and Validation

### Local Development Testing
```bash
# Build and test locally
poetry install
poetry run pytest tests
poetry run flake8 .

# Test Docker build
docker build -t myapp:test .
docker run -d -p 8080:80 myapp:test
```

### Pipeline Testing Strategy
1. **Feature branch**: Create PR to trigger CI validation
2. **Develop deployment**: Merge PR to test CD-Test pipeline
3. **Production simulation**: Manual trigger of CD-Prod for validation

### Monitoring and Verification
- **Pipeline logs**: Detailed execution logs in GitHub Actions
- **Image registry**: Verify images in GHCR
- **Container status**: Check running containers in deployment environment

### Quality Assurance
- **Linting**: flake8 ensures code quality standards
- **Testing**: pytest validates application functionality
- **Build verification**: Docker build confirms deployment readiness
- **Manual review**: Production approval gate ensures human oversight

---

## Pipeline Status and Usage

✅ **CI Pipeline**: Validates all PRs to develop branch  
✅ **CD-Test Pipeline**: Builds and pushes images on develop commits  
✅ **CD-Prod Pipeline**: Deploys to production with manual approval  
✅ **SHA Management**: Ensures exact image traceability  
✅ **Docker Integration**: Containerized deployment ready  
✅ **Manual Approval**: Production safety gates implemented  

This implementation successfully demonstrates a production-ready CI/CD pipeline with proper quality gates, security controls, and deployment automation suitable for enterprise environments.