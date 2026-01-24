---
id: sysdes-054
title: Service Mesh
aliases:
- Service Mesh
- Istio
- Linkerd
- Sidecar Proxy
topic: system-design
subtopics:
- infrastructure
- microservices
- networking
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-api-gateway--system-design--medium
- q-microservices-vs-monolith--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- infrastructure
- difficulty/medium
- microservices
- system-design
anki_cards:
- slug: sysdes-054-0-en
  language: en
  anki_id: 1769160585274
  synced_at: '2026-01-23T13:49:17.855223'
- slug: sysdes-054-0-ru
  language: ru
  anki_id: 1769160585299
  synced_at: '2026-01-23T13:49:17.856104'
---
# Question (EN)
> What is a service mesh? How does it differ from an API gateway, and when would you use one?

# Vopros (RU)
> Что такое service mesh? Чем он отличается от API gateway и когда его использовать?

---

## Answer (EN)

**Service mesh** is a dedicated infrastructure layer for handling service-to-service communication, typically implemented as sidecar proxies.

### Architecture

```
Without Service Mesh:
┌─────────┐        ┌─────────┐
│Service A│───────►│Service B│
└─────────┘        └─────────┘
  (handles retries, TLS, tracing itself)

With Service Mesh:
┌─────────┬───────┐        ┌───────┬─────────┐
│Service A│ Proxy │───────►│ Proxy │Service B│
└─────────┴───────┘        └───────┴─────────┘
              ↑                  ↑
              └───── Control Plane ─────┘
                  (Istiod, Linkerd)
```

### Components

| Component | Function | Example |
|-----------|----------|---------|
| Data Plane | Sidecar proxies handling traffic | Envoy, Linkerd-proxy |
| Control Plane | Configuration, policy management | Istiod, Linkerd |

### Key Features

```
1. Traffic Management
   - Load balancing
   - Traffic splitting (canary, A/B)
   - Retries, timeouts, circuit breaking

2. Security
   - mTLS between services (automatic)
   - Authorization policies
   - Certificate management

3. Observability
   - Distributed tracing
   - Metrics collection
   - Access logging

4. Policy
   - Rate limiting
   - Access control
   - Quota management
```

### Service Mesh vs API Gateway

| Aspect | API Gateway | Service Mesh |
|--------|-------------|--------------|
| Position | Edge (north-south) | Internal (east-west) |
| Traffic | External → Internal | Service → Service |
| Focus | API management | Service communication |
| Auth | External clients | Service identity |
| Deployment | Centralized | Distributed (sidecars) |

```
                    Internet
                        │
                   ┌────▼────┐
                   │   API   │ ← North-South traffic
                   │ Gateway │
                   └────┬────┘
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
┌───▼───┐          ┌───▼───┐          ┌───▼───┐
│Svc A  │◄────────►│Svc B  │◄────────►│Svc C  │
└───────┘          └───────┘          └───────┘
         ↑ East-West traffic (Service Mesh) ↑
```

### Popular Service Meshes

| Mesh | Proxy | Notes |
|------|-------|-------|
| Istio | Envoy | Feature-rich, complex |
| Linkerd | linkerd2-proxy | Lightweight, simple |
| Consul Connect | Envoy | HashiCorp ecosystem |
| AWS App Mesh | Envoy | AWS native |

### When to Use

**Use Service Mesh when:**
- Many microservices (50+)
- Need mTLS everywhere
- Complex traffic routing needs
- Consistent observability required

**Avoid when:**
- Few services (< 10)
- Simple communication patterns
- Resource constraints (sidecars add overhead)

---

## Otvet (RU)

**Service mesh** - выделенный инфраструктурный слой для обработки коммуникации между сервисами, обычно реализуемый через sidecar прокси.

### Архитектура

```
Без Service Mesh:
┌─────────┐        ┌─────────┐
│Сервис A │───────►│Сервис B │
└─────────┘        └─────────┘
  (сам обрабатывает retries, TLS, tracing)

С Service Mesh:
┌─────────┬───────┐        ┌───────┬─────────┐
│Сервис A │ Proxy │───────►│ Proxy │Сервис B │
└─────────┴───────┘        └───────┴─────────┘
              ↑                  ↑
              └───── Control Plane ─────┘
```

### Ключевые возможности

```
1. Управление трафиком
   - Балансировка нагрузки
   - Разделение трафика (canary, A/B)
   - Retries, таймауты, circuit breaking

2. Безопасность
   - mTLS между сервисами (автоматически)
   - Политики авторизации
   - Управление сертификатами

3. Observability
   - Распределённая трассировка
   - Сбор метрик
   - Логирование доступа
```

### Service Mesh vs API Gateway

| Аспект | API Gateway | Service Mesh |
|--------|-------------|--------------|
| Позиция | Edge (north-south) | Внутренний (east-west) |
| Трафик | Внешний → Внутренний | Сервис → Сервис |
| Фокус | API management | Коммуникация сервисов |
| Деплой | Централизованный | Распределённый (sidecars) |

### Популярные Service Mesh

| Mesh | Proxy | Примечания |
|------|-------|------------|
| Istio | Envoy | Богатый функционал, сложный |
| Linkerd | linkerd2-proxy | Лёгкий, простой |
| Consul Connect | Envoy | Экосистема HashiCorp |

### Когда использовать

**Используйте Service Mesh когда:**
- Много микросервисов (50+)
- Нужен mTLS везде
- Сложные требования к роутингу
- Требуется единообразная observability

**Избегайте когда:**
- Мало сервисов (< 10)
- Простые паттерны коммуникации
- Ограничения по ресурсам

---

## Follow-ups

- What is the overhead of running a service mesh?
- How does Istio implement mTLS?
- What is the difference between Istio and Linkerd?
