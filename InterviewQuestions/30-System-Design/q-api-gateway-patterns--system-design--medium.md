---
id: sysdes-018
title: API Gateway Patterns
aliases:
- API Gateway
- Gateway Pattern
topic: system-design
subtopics:
- microservices
- infrastructure
- api
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-reverse-proxy-forward-proxy--system-design--medium
- q-microservices-vs-monolith--system-design--hard
created: 2025-01-23
updated: 2025-01-23
tags:
- microservices
- difficulty/medium
- infrastructure
- system-design
anki_cards:
- slug: sysdes-018-0-en
  language: en
  anki_id: 1769158889242
  synced_at: '2026-01-23T13:29:45.878176'
- slug: sysdes-018-0-ru
  language: ru
  anki_id: 1769158889266
  synced_at: '2026-01-23T13:29:45.880810'
---
# Question (EN)
> What is an API Gateway? What patterns and responsibilities does it handle in a microservices architecture?

# Vopros (RU)
> Что такое API Gateway? Какие паттерны и обязанности он выполняет в микросервисной архитектуре?

---

## Answer (EN)

**API Gateway** is a single entry point for all client requests that routes them to appropriate microservices.

### Why API Gateway?

```
Without Gateway:
Client → Service A
Client → Service B
Client → Service C
(Client knows all services, complex client logic)

With Gateway:
Client → API Gateway → Service A
                    → Service B
                    → Service C
(Single entry point, simplified client)
```

### Core Responsibilities

**1. Request Routing**
```yaml
routes:
  - path: /users/**
    service: user-service
  - path: /orders/**
    service: order-service
  - path: /products/**
    service: product-service
```

**2. Authentication & Authorization**
```
Request → Gateway → Validate JWT → Route to service
                 ↓
         Reject if invalid
```

**3. Rate Limiting**
```
Per-user: 100 requests/minute
Per-IP: 1000 requests/minute
Per-endpoint: configurable
```

**4. Request/Response Transformation**
```
Client sends: JSON
Gateway transforms to: Protocol Buffers for internal service
```

**5. Load Balancing**
- Round robin
- Least connections
- Weighted routing

**6. Circuit Breaking**
```
Service unhealthy → Gateway stops routing → Returns cached/fallback
```

### API Gateway Patterns

**1. Backend for Frontend (BFF)**
```
Mobile App → Mobile BFF Gateway → Services
Web App   → Web BFF Gateway    → Services
(Optimized responses for each client type)
```

**2. API Composition/Aggregation**
```
Client: GET /user-dashboard

Gateway calls:
  - GET /users/123      → User Service
  - GET /orders?user=123 → Order Service
  - GET /notifications   → Notification Service

Gateway combines: Returns single aggregated response
```

**3. Protocol Translation**
```
External: REST/HTTP
Internal: gRPC, Message Queues
Gateway translates between protocols
```

### Popular API Gateways

| Gateway | Strengths |
|---------|-----------|
| Kong | Plugin ecosystem, Lua extensibility |
| AWS API Gateway | Serverless, AWS integration |
| Nginx Plus | Performance, familiar to ops |
| Traefik | Cloud-native, auto-discovery |
| Apigee | Enterprise features, analytics |

### Trade-offs

| Pros | Cons |
|------|------|
| Single entry point | Single point of failure |
| Centralized cross-cutting concerns | Additional latency |
| Simplified clients | Deployment bottleneck |
| Protocol translation | Complexity |

### Best Practices

1. Keep gateway stateless (scale horizontally)
2. Don't put business logic in gateway
3. Implement health checks for backends
4. Use caching strategically
5. Monitor and log all requests

---

## Otvet (RU)

**API Gateway** - единая точка входа для всех клиентских запросов, которая маршрутизирует их к соответствующим микросервисам.

### Зачем API Gateway?

```
Без Gateway:
Клиент → Сервис A
Клиент → Сервис B
Клиент → Сервис C
(Клиент знает все сервисы, сложная логика на клиенте)

С Gateway:
Клиент → API Gateway → Сервис A
                    → Сервис B
                    → Сервис C
(Единая точка входа, упрощенный клиент)
```

### Основные обязанности

**1. Маршрутизация запросов**
```yaml
routes:
  - path: /users/**
    service: user-service
  - path: /orders/**
    service: order-service
  - path: /products/**
    service: product-service
```

**2. Аутентификация и авторизация**
```
Запрос → Gateway → Валидация JWT → Маршрут к сервису
                ↓
        Отклонить если невалидный
```

**3. Rate Limiting**
```
На пользователя: 100 запросов/минуту
На IP: 1000 запросов/минуту
На endpoint: настраиваемо
```

**4. Трансформация запросов/ответов**
```
Клиент отправляет: JSON
Gateway преобразует в: Protocol Buffers для внутреннего сервиса
```

**5. Балансировка нагрузки**
- Round robin
- Least connections
- Взвешенная маршрутизация

**6. Circuit Breaking**
```
Сервис недоступен → Gateway прекращает маршрутизацию → Возвращает кеш/fallback
```

### Паттерны API Gateway

**1. Backend for Frontend (BFF)**
```
Мобильное приложение → Mobile BFF Gateway → Сервисы
Веб-приложение      → Web BFF Gateway    → Сервисы
(Оптимизированные ответы для каждого типа клиента)
```

**2. API Composition/Aggregation**
```
Клиент: GET /user-dashboard

Gateway вызывает:
  - GET /users/123      → User Service
  - GET /orders?user=123 → Order Service
  - GET /notifications   → Notification Service

Gateway объединяет: Возвращает единый агрегированный ответ
```

**3. Трансляция протоколов**
```
Внешние: REST/HTTP
Внутренние: gRPC, Message Queues
Gateway транслирует между протоколами
```

### Популярные API Gateway

| Gateway | Преимущества |
|---------|--------------|
| Kong | Экосистема плагинов, расширяемость на Lua |
| AWS API Gateway | Serverless, интеграция с AWS |
| Nginx Plus | Производительность, знакомо ops |
| Traefik | Cloud-native, авто-обнаружение |
| Apigee | Enterprise функции, аналитика |

### Компромиссы

| Плюсы | Минусы |
|-------|--------|
| Единая точка входа | Единая точка отказа |
| Централизованные cross-cutting concerns | Дополнительная задержка |
| Упрощенные клиенты | Узкое место при деплое |
| Трансляция протоколов | Сложность |

### Лучшие практики

1. Держите gateway stateless (горизонтальное масштабирование)
2. Не размещайте бизнес-логику в gateway
3. Реализуйте health checks для backends
4. Используйте кеширование стратегически
5. Мониторьте и логируйте все запросы

---

## Follow-ups

- How do you handle API versioning at the gateway level?
- What is the difference between API Gateway and Service Mesh?
- How do you implement canary deployments with API Gateway?

## Related Questions

### Prerequisites (Easier)
- [[q-reverse-proxy-forward-proxy--system-design--medium]] - Proxies
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing

### Related (Same Level)
- [[q-circuit-breaker-pattern--system-design--medium]] - Circuit breaker
- [[q-rate-limiting-algorithms--system-design--medium]] - Rate limiting

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - Microservices
