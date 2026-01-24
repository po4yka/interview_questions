---
id: cs-eng-cicd
title: Software Engineering - CI/CD
topic: software_engineering
difficulty: medium
tags:
- cs_testing
- devops
anki_cards:
- slug: cs-eng-cicd-0-en
  language: en
  anki_id: 1769160675624
  synced_at: '2026-01-23T13:31:18.884011'
- slug: cs-eng-cicd-0-ru
  language: ru
  anki_id: 1769160675650
  synced_at: '2026-01-23T13:31:18.885408'
- slug: cs-eng-cicd-1-en
  language: en
  anki_id: 1769160675675
  synced_at: '2026-01-23T13:31:18.886730'
- slug: cs-eng-cicd-1-ru
  language: ru
  anki_id: 1769160675700
  synced_at: '2026-01-23T13:31:18.888468'
---
# Continuous Integration and Delivery

## CI/CD Overview

### Continuous Integration (CI)

Frequently merge code to main branch with automated testing.

```
Developer -> Commit -> Build -> Test -> Integrate
    |                                      |
    +<---- Fast feedback on failures <-----+
```

**Key practices**:
- Commit frequently (at least daily)
- Automated build and test
- Fix broken builds immediately
- Keep build fast (<10 min)

### Continuous Delivery (CD)

Every commit is potentially deployable.

```
CI -> Staging Deploy -> Integration Tests -> Manual Approval -> Production
```

### Continuous Deployment

Every commit that passes tests deploys automatically.

```
CI -> Staging -> Tests -> Production (automatic)
```

## CI/CD Pipeline

```yaml
# GitHub Actions example
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run linter
        run: ruff check .

  deploy:
    needs: [build, lint]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: ./deploy.sh
```

## Pipeline Stages

### 1. Build

Compile code, create artifacts.

```yaml
- name: Build
  run: |
    npm install
    npm run build
```

### 2. Test

Run automated tests.

```yaml
- name: Unit Tests
  run: pytest tests/unit

- name: Integration Tests
  run: pytest tests/integration

- name: E2E Tests
  run: cypress run
```

### 3. Security Scan

Check for vulnerabilities.

```yaml
- name: Security Scan
  run: |
    npm audit
    snyk test
```

### 4. Quality Gate

Code quality checks.

```yaml
- name: Code Coverage
  run: pytest --cov --cov-fail-under=80

- name: Static Analysis
  run: sonar-scanner
```

### 5. Deploy

Push to environment.

```yaml
- name: Deploy to Staging
  run: kubectl apply -f k8s/staging/

- name: Deploy to Production
  run: kubectl apply -f k8s/production/
```

## Deployment Strategies

### Rolling Deployment

Gradually replace old instances with new.

```
Old:  [v1][v1][v1][v1]
Step1: [v1][v1][v1][v2]
Step2: [v1][v1][v2][v2]
Step3: [v1][v2][v2][v2]
Done:  [v2][v2][v2][v2]
```

**Pros**: Zero downtime, gradual rollout.
**Cons**: Multiple versions running simultaneously.

### Blue-Green Deployment

Two identical environments, switch traffic.

```
      Load Balancer
           |
    +------+------+
    |             |
[Blue v1]    [Green v2]
   100%         0%

Switch:
[Blue v1]    [Green v2]
    0%         100%
```

**Pros**: Instant rollback, clean cutover.
**Cons**: Double infrastructure cost.

### Canary Deployment

Route small % of traffic to new version.

```
Load Balancer
      |
   +--+--+
   |     |
[v1]   [v2]
95%    5% (canary)

If successful, increase to 100%
```

**Pros**: Low risk, test in production.
**Cons**: Complex routing, monitoring needed.

### Feature Flags

Deploy code, control activation separately.

```python
if feature_flags.is_enabled("new_checkout"):
    return new_checkout_flow()
else:
    return old_checkout_flow()
```

**Benefits**:
- Decouple deployment from release
- A/B testing
- Kill switch for problems

## Infrastructure as Code (IaC)

### Terraform Example

```hcl
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"

  tags = {
    Name = "web-server"
  }
}

resource "aws_security_group" "web_sg" {
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "app.py"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    spec:
      containers:
      - name: web
        image: myapp:v1.2.3
        ports:
        - containerPort: 8080
```

## Version Control Best Practices

### Branching Strategies

**GitHub Flow**:
```
main ----o----o----o----o----
           \     /
feature     o--o
```

**GitFlow**:
```
main     ----o---------o----
              \       /
develop ----o--o----o-----
              \   /
feature       o-o
```

**Trunk-Based**:
```
main ----o--o--o--o--o----
         (short-lived branches)
```

### Commit Messages

```
type(scope): description

feat(auth): add OAuth2 login
fix(api): handle null response
docs(readme): update installation
refactor(db): optimize queries
test(user): add edge cases
```

## Monitoring and Observability

### Logs

```python
import logging

logger = logging.getLogger(__name__)

def process_order(order):
    logger.info(f"Processing order {order.id}")
    try:
        result = payment_service.charge(order)
        logger.info(f"Payment successful for order {order.id}")
        return result
    except PaymentError as e:
        logger.error(f"Payment failed for order {order.id}: {e}")
        raise
```

### Metrics

```python
from prometheus_client import Counter, Histogram

requests_total = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@request_duration.time()
def handle_request():
    requests_total.inc()
    # Handle request
```

### Alerting

```yaml
# Prometheus alert rule
groups:
- name: app
  rules:
  - alert: HighErrorRate
    expr: rate(http_errors_total[5m]) > 0.1
    for: 5m
    annotations:
      summary: "High error rate detected"
```

## Best Practices

1. **Automate everything**: Build, test, deploy
2. **Fail fast**: Quick feedback on problems
3. **Test in production-like environments**
4. **Monitor deployments**: Detect issues quickly
5. **Enable quick rollbacks**: Blue-green, feature flags
6. **Security scanning**: Part of pipeline
7. **Keep pipeline fast**: Parallel jobs, caching

## Interview Questions

1. **What is CI/CD?**
   - CI: Frequent integration with automated testing
   - CD: Every commit is deployable
   - Enables fast, reliable releases

2. **Blue-green vs canary deployment?**
   - Blue-green: Full switch between environments
   - Canary: Gradual rollout to subset
   - Canary is lower risk, blue-green simpler

3. **How to handle failed deployments?**
   - Automatic rollback on health check failure
   - Feature flags to disable problematic code
   - Blue-green allows instant switch back

4. **Why use infrastructure as code?**
   - Reproducible environments
   - Version controlled
   - Review changes before apply
   - Disaster recovery
