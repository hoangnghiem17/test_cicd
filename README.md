# CI/CD Pipeline Implementation with GitHub Actions!!!

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
- **CD-Test Pipeline**: Automated testing, build, tag, and push Docker images to registry
- **CD-Prod Pipeline**: Pull tested images and deploy to production with manual approval
- **Automated Testing**: Binary pass/fail validation before Docker operations
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
├── scripts/
│   └── run_automated_tests.py  # Automated testing script
├── test_data/
│   ├── input_data.json     # Test scenarios (URLs, descriptions)
│   └── reference_data.json # Expected results for each test
├── tests/
│   └── test_app.py         # Unit tests
├── app.py                  # Main application
├── Dockerfile              # Container configuration
├── pyproject.toml          # Poetry project configuration
├── poetry.lock             # Dependency lock file
├── AUTOMATED_TESTING.md    # Detailed testing documentation
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

**scripts/run_automated_tests.py**: Automated testing for CD-Test pipeline
- Loads test scenarios and compares app output with expected results
- Generates binary results (1/0) per test case
- Blocks pipeline if any test fails

**test_data/**: Fixed test data for automated validation
- `input_data.json`: Test scenarios with different HTTP endpoints
- `reference_data.json`: Expected application responses for each scenario

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

1. **Code Checkout**: Retrieve merged develop branch code with full Git history
2. **Python Setup**: Install Python 3.9 and Poetry dependency manager
3. **Automated Testing**: Run test suite comparing app output against reference data
   - Tests 5 scenarios: GitHub API, HTTP 200/404/500, network timeout
   - Generates binary results (1/0) per test case
   - **Pipeline blocked if any test fails**
4. **Test Results Upload**: Save binary and detailed results as GitHub artifacts
5. **Docker Setup**: Configure Buildx for multi-platform builds (only if tests pass)
6. **Registry Login**: Authenticate with GitHub Container Registry
7. **Docker Build**: Create linux/amd64 image with `docker buildx build`
8. **Image Tagging**: Tag image with full commit SHA: `ghcr.io/REPO/myapp:${{ github.sha }}`
9. **Registry Push**: Upload tagged image to GHCR
10. **Git Tag Creation**: Create/update `latest-tested` tag pointing to current commit
   ```bash
   git tag -f latest-tested ${{ github.sha }}
   git push origin --force --tags
   ```

### Image Versioning Strategy
- **Format**: `ghcr.io/hoangnghiem17/test_cicd/myapp:FULL_SHA`
- **SHA Source**: Full 40-character commit SHA from develop branch
- **Tag Communication**: `latest-tested` Git tag points to the tested commit
- **Example**: `ghcr.io/hoangnghiem17/test_cicd/myapp:abc123def456...`

### Key Features
- **Automated Quality Gates**: Tests application functionality before Docker operations
- **Binary Test Results**: 1/0 output per test case for clear pass/fail tracking
- **Pipeline Blocking**: Failed tests prevent untested code from reaching registry
- **Immutable versioning**: Each commit gets unique image tag
- **Platform optimization**: Built specifically for linux/amd64
- **Registry integration**: Automatic push to private GHCR

---

## 5. CD-Prod Pipeline (Production Deployment)

### Trigger
```yaml
on:
  push:
    branches: [main]
```

### Design Challenge and Evolution

**Original Goal**: Create separate pipelines for test and production with proper SHA traceability and manual approval gates.

**Core Problems Encountered**:
1. **SHA Mismatch**: CD-Test used develop branch SHA, but CD-Prod referenced main branch SHA
2. **No Manual Approval**: GitHub Actions doesn't support Environment approval gates with `workflow_run` triggers

### Approaches Comparison Table

| Approach | SHA Access | Manual Approval | Complexity | Repository Impact | Status |
|----------|------------|-----------------|------------|-------------------|---------|
| `workflow_run` + `head_sha` | ✅ Works | ❌ Not supported | Low | None | ❌ Failed |
| GitHub Artifacts | ❌ Limited | ❌ Not supported | Medium | None | ❌ Failed |
| Workflow Outputs | ❌ Unreliable | ❌ Not supported | Medium | None | ❌ Failed |
| File Commit | ✅ Works | ✅ Works | High | Commits pollution | ❌ Failed |
| **Git Tags** | ✅ Works | ✅ Works | Low | Clean tags only | ✅ **Success** |

### Alternative Approaches Tested

#### ❌ Approach 1: `workflow_run` with `head_sha`
```yaml
# Initial CD-Prod implementation
on:
  workflow_run:
    workflows: ["CD-Test Pipeline"]
    types: [completed]

# SHA extraction attempt
GIT_SHA=$(echo "${{ github.event.workflow_run.head_sha }}" | cut -c1-7)
```

**Why it Failed**:
- ✅ **SHA Extraction**: Successfully got develop branch SHA
- ❌ **Manual Approval**: Environment approval gates don't work with `workflow_run` triggers
- ❌ **Production Safety**: No human oversight before deployment

#### ❌ Approach 2: GitHub Actions Artifacts
```yaml
# CD-Test: Upload SHA as artifact
- name: Upload Git SHA Artifact
  uses: actions/upload-artifact@v4
  with:
    name: git-sha
    path: git_sha.txt

# CD-Prod: Download SHA artifact
- name: Download Git SHA Artifact
  uses: actions/download-artifact@v4
  with:
    name: git-sha
```

**Why it Failed**:
- ❌ **Cross-Workflow Access**: Artifacts are workflow-local by default
- ❌ **Complex Sharing**: No direct cross-workflow artifact access
- ❌ **Still Manual Approval Issue**: Would still require `workflow_run` trigger

#### ❌ Approach 3: Workflow Outputs with `workflow_run`
```yaml
# CD-Test: Set output
outputs:
  git_sha: ${{ steps.git_sha.outputs.sha }}

# CD-Prod: Access output
run: |
  GIT_SHA=${{ github.event.workflow_run.outputs.git_sha }}
```

**Why it Failed**:
- ❌ **Workflow Outputs**: `workflow_run.outputs` not reliably accessible
- ❌ **GitHub Actions Limitation**: Outputs don't propagate across `workflow_run` triggers
- ❌ **Manual Approval Issue**: Still can't use Environment gates

#### ❌ Approach 4: File-Based Communication
```yaml
# Store SHA in repository file
echo "${{ github.sha }}" > .github/last-tested-sha.txt
git add .github/last-tested-sha.txt
git commit -m "Update tested SHA"
```

**Why it Failed**:
- ❌ **Repository Pollution**: Creates unnecessary commits
- ❌ **Complexity**: Requires additional Git operations
- ❌ **Race Conditions**: Multiple concurrent builds could conflict

### ✅ Final Solution: Git Tag-Based Communication

**Why Git Tags Work**:
- ✅ **Repository-Wide Visibility**: Tags are accessible across all workflows
- ✅ **No Commit Pollution**: Tags don't create additional commits
- ✅ **Force Update**: `-f` flag allows overwriting existing tags
- ✅ **Manual Approval Compatible**: Works with `push` trigger (not `workflow_run`)
- ✅ **Git-Native**: Uses standard Git mechanisms
- ✅ **Audit Trail**: Tag history provides deployment tracking

```bash
# CD-Test: Create tag pointing to tested commit
git tag -f latest-tested ${{ github.sha }}
git push origin --force --tags

# CD-Prod: Resolve tag to get tested SHA
GIT_SHA=$(git rev-parse latest-tested)
```

### Pipeline Steps

1. **Manual Approval**: Pipeline blocked immediately by `environment: production` requirement
   - Configured reviewers receive notification
   - Complete pipeline paused until manual approval
   - Human oversight before any production activities
2. **Code Checkout**: Retrieve main branch code with full Git history (`fetch-depth: 0`) (after approval)
3. **SHA Resolution**: Extract commit SHA from `latest-tested` tag
   ```bash
   GIT_SHA=$(git rev-parse latest-tested)
   ```
4. **Docker Setup**: Configure Buildx and login to GHCR
5. **Image Pull**: Download exact image built and tested in CD-Test
6. **Deployment**: Deploy container with `docker run -d -p 80:80`

### Git Tag-Based SHA Management
The pipeline uses Git tags to ensure cross-pipeline communication:
- **Tag Creation**: CD-Test creates `latest-tested` tag on successful image push
- **Tag Resolution**: CD-Prod resolves tag to get tested commit SHA
- **Consistency**: Guarantees deployment of verified artifact from develop branch

### Manual Approval Gate
- **Environment**: `production` with required reviewers
- **Process**: Complete pipeline blocked at job start until approval
- **Security**: Human validation before any production activities
- **Compatibility**: Works with `push` trigger (unlike `workflow_run`)

---

## 6. Git-Flow and SHA Management

### Branching Strategy
```
feature/xyz → develop → main
     ↓           ↓       ↓
    CI      CD-Test  CD-Prod
```

### Git Tag-Based SHA Flow

1. **Developer pushes to develop**: Commit SHA `abc123def456...`
2. **CD-Test builds image**: Tagged as `myapp:abc123def456...`
3. **CD-Test creates Git tag**: `latest-tested` → `abc123def456...`
4. **Developer merges to main**: Triggers CD-Prod pipeline
5. **CD-Prod resolves tag**: `git rev-parse latest-tested` → `abc123def456...`
6. **Production deployment**: Pulls and deploys exact tested image

### Key Innovation: Git Tag Communication
```bash
# CD-Test: Create tag pointing to tested commit
git tag -f latest-tested ${{ github.sha }}
git push origin --force --tags

# CD-Prod: Resolve tag to get tested SHA
GIT_SHA=$(git rev-parse latest-tested)
```

**Benefits of this approach:**
- ✅ **Solves SHA mismatch**: CD-Prod gets develop branch SHA (not main branch SHA)
- ✅ **Enables manual approval**: Works with `push` trigger (not `workflow_run`)
- ✅ **Git-native solution**: Uses standard Git tagging mechanism
- ✅ **Complete traceability**: Exact image from develop branch deployed to production

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

## 11. GitHub Actions UI Configuration

### Environment: `production`

| Setting | Configuration Path | Purpose |
|---------|-------------------|----------|
| Create Environment | Repository > Settings > Environments > New environment | Controls manual approval for production deployments |
| Required Reviewers | Inside `production` environment → Add reviewers | Only authorized personnel can approve prod deployments |
| Deployment Protection Rule | Optional, if using API/external approval logic | Enhanced security, often not needed with GitHub internal approval |

### GitHub Secrets: `CR_PAT`

| Setting | Configuration Path | Purpose |
|---------|-------------------|----------|
| Secret `CR_PAT` | Repository > Settings > Secrets and variables > Actions → New repository secret | Authenticates Docker Push/Pull with GitHub Container Registry |
| Token Creation | GitHub > Settings > Developer Settings > Personal Access Tokens | Token requires: `read:packages`, `write:packages`, `repo` scopes |

### GitHub Actions Permissions

| Setting | Configuration Path | Purpose |
|---------|-------------------|----------|
| Workflow Permissions | Repository > Settings > Actions > General > Workflow permissions | Follows principle of least privilege |
| Read Access | Enable "Read access to contents and metadata" | Allows workflow checkout, SHA access, tag reading |
| Optional PR Creation | "Allow GitHub Actions to create and approve pull requests" | Only if using Actions for automated PRs/tags |

⚠️ Note: Workflows can also set specific permissions as shown in `cd_prod.yml`:
```yaml
permissions:
  contents: read
  actions: read
```

### Branch Protection: `develop`

| Setting | Configuration Path | Purpose |
|---------|-------------------|----------|
| Branch Protection Rule | Repository > Settings > Branches > Add rule → Branch: `develop` | Prevents direct pushes to develop |
| Status Checks | Enable "Require status checks to pass before merging" | Blocks merges if CI/CD fails |
| Required Checks | Select `CI Build`, `CD-Test deploy` | Ensures only validated code proceeds |
| Optional Reviews | "Require pull request reviews before merging" | If code review enforcement needed |

### Optional Tag Protection

| Setting | Configuration Path | Purpose |
|---------|-------------------|----------|
| Tag Environment | Optional for deployment on tags | Enhanced control over tested commits |
| Tag Protection Rules | Settings > Branches > Tag protection rules | Prevents `latest-tested` manipulation |

### Configuration Checklist

| Component | Required | Purpose |
|-----------|----------|----------|
| `production` Environment | ✅ | Guards production deployments |
| `CR_PAT` Secret | ✅ | Container Registry authentication |
| Actions Permissions | ✅ | Security and integrity |
| Branch Protection | ✅ | Ensures CI/CD quality |

---

## Pipeline Status and Usage

✅ **CI Pipeline**: Validates all PRs to develop branch  
✅ **CD-Test Pipeline**: Builds and pushes images on develop commits  
✅ **CD-Prod Pipeline**: Deploys to production with manual approval  
✅ **SHA Management**: Ensures exact image traceability  
✅ **Docker Integration**: Containerized deployment ready  
✅ **Manual Approval**: Production safety gates implemented  

This implementation successfully demonstrates a production-ready CI/CD pipeline with proper quality gates, security controls, and deployment automation suitable for enterprise environments.
