---
id: be-sec-011
title: Secrets Management / Управление секретами
aliases: []
topic: security
subtopics:
- secrets
- configuration
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Backend interview preparation
status: draft
moc: moc-backend
related:
- c-security
- c-configuration
created: 2025-01-23
updated: 2025-01-23
tags:
- security
- secrets
- configuration
- difficulty/medium
- topic/security
anki_cards:
- slug: be-sec-011-0-en
  language: en
  anki_id: 1769167242215
  synced_at: '2026-01-23T15:20:43.057247'
- slug: be-sec-011-0-ru
  language: ru
  anki_id: 1769167242237
  synced_at: '2026-01-23T15:20:43.059115'
---
# Question (EN)
> How should application secrets be managed in production?

# Vopros (RU)
> Как следует управлять секретами приложения в продакшене?

---

## Answer (EN)

**Never store secrets in:**
- Source code
- Git repository (even private)
- Unencrypted config files
- Container images

---

**Secrets Management Approaches:**

**1. Environment Variables (Basic)**
```bash
export DATABASE_URL="postgres://user:pass@host:5432/db"
export API_KEY="sk-1234..."
```
```python
import os
db_url = os.environ["DATABASE_URL"]
```
**Pros:** Simple, supported everywhere
**Cons:** Visible in process list, logs may leak them

**2. Secrets Manager Services (Recommended)**

```python
# AWS Secrets Manager
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='prod/db/credentials')

# HashiCorp Vault
import hvac
client = hvac.Client(url='https://vault.example.com')
secret = client.secrets.kv.read_secret_version(path='database')
```

| Service | Provider |
|---------|----------|
| AWS Secrets Manager | AWS |
| Azure Key Vault | Azure |
| Google Secret Manager | GCP |
| HashiCorp Vault | Self-hosted/Cloud |

**3. Kubernetes Secrets**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  username: YWRtaW4=  # base64
  password: cGFzc3dvcmQ=
```
```yaml
# Pod spec
envFrom:
  - secretRef:
      name: db-credentials
```

**4. SOPS (Secrets OPerationS)**
```yaml
# Encrypted in Git, decrypted at deploy
db_password: ENC[AES256_GCM,data:...,tag:...]
```

---

**Best Practices:**

| Practice | Description |
|----------|-------------|
| **Rotation** | Regularly rotate secrets (90 days max) |
| **Least privilege** | Apps get only needed secrets |
| **Audit logging** | Track secret access |
| **Encryption at rest** | Encrypt stored secrets |
| **Short-lived credentials** | Use temporary tokens when possible |
| **No defaults** | Fail if secret is missing |

**Secret Injection Patterns:**
```python
# Good: Fail fast if missing
DB_URL = os.environ["DATABASE_URL"]  # Raises KeyError

# Bad: Silent fallback
DB_URL = os.environ.get("DATABASE_URL", "localhost")  # May use wrong DB
```

**Defense in Depth:**
- Encrypt secrets in transit and at rest
- Network isolation for secrets services
- Regular secret scanning in CI/CD (git-secrets, truffleHog)

## Otvet (RU)

**Никогда не храните секреты в:**
- Исходном коде
- Git-репозитории (даже приватном)
- Незашифрованных конфиг-файлах
- Образах контейнеров

---

**Подходы к управлению секретами:**

**1. Переменные окружения (базовый подход)**
```bash
export DATABASE_URL="postgres://user:pass@host:5432/db"
export API_KEY="sk-1234..."
```
```python
import os
db_url = os.environ["DATABASE_URL"]
```
**Плюсы:** Просто, поддерживается везде
**Минусы:** Видны в списке процессов, могут утечь в логи

**2. Сервисы управления секретами (рекомендуется)**

```python
# AWS Secrets Manager
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='prod/db/credentials')

# HashiCorp Vault
import hvac
client = hvac.Client(url='https://vault.example.com')
secret = client.secrets.kv.read_secret_version(path='database')
```

| Сервис | Провайдер |
|--------|-----------|
| AWS Secrets Manager | AWS |
| Azure Key Vault | Azure |
| Google Secret Manager | GCP |
| HashiCorp Vault | Self-hosted/Cloud |

**3. Kubernetes Secrets**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  username: YWRtaW4=  # base64
  password: cGFzc3dvcmQ=
```
```yaml
# Спецификация пода
envFrom:
  - secretRef:
      name: db-credentials
```

**4. SOPS (Secrets OPerationS)**
```yaml
# Зашифровано в Git, расшифровывается при деплое
db_password: ENC[AES256_GCM,data:...,tag:...]
```

---

**Лучшие практики:**

| Практика | Описание |
|----------|----------|
| **Ротация** | Регулярная ротация секретов (макс. 90 дней) |
| **Минимальные права** | Приложения получают только нужные секреты |
| **Аудит логирование** | Отслеживание доступа к секретам |
| **Шифрование в покое** | Шифрование хранимых секретов |
| **Краткосрочные учётные данные** | Временные токены где возможно |
| **Без значений по умолчанию** | Падать если секрет отсутствует |

**Паттерны инъекции секретов:**
```python
# Хорошо: Падать сразу если отсутствует
DB_URL = os.environ["DATABASE_URL"]  # Вызывает KeyError

# Плохо: Тихий fallback
DB_URL = os.environ.get("DATABASE_URL", "localhost")  # Может использовать неправильную БД
```

**Эшелонированная защита:**
- Шифрование секретов при передаче и хранении
- Сетевая изоляция для сервисов секретов
- Регулярное сканирование секретов в CI/CD (git-secrets, truffleHog)

---

## Follow-ups
- How does HashiCorp Vault dynamic secrets work?
- What is the difference between secrets and configuration?
- How to handle secret rotation without downtime?

## Dopolnitelnye voprosy (RU)
- Как работают динамические секреты HashiCorp Vault?
- В чём разница между секретами и конфигурацией?
- Как обрабатывать ротацию секретов без простоя?

## References
- [[c-security]]
- [[c-configuration]]
- [[moc-backend]]
