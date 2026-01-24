---
id: sysdes-039
title: Synchronous vs Asynchronous Communication
aliases:
- Sync vs Async
- Request-Response vs Event-Driven
topic: system-design
subtopics:
- communication
- patterns
- microservices
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-message-queues--system-design--medium
- q-grpc-vs-rest--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- communication
- difficulty/medium
- patterns
- system-design
anki_cards:
- slug: sysdes-039-0-en
  language: en
  anki_id: 1769159522547
  synced_at: '2026-01-23T13:49:17.865498'
- slug: sysdes-039-0-ru
  language: ru
  anki_id: 1769159522568
  synced_at: '2026-01-23T13:49:17.866548'
---
# Question (EN)
> What is the difference between synchronous and asynchronous communication in distributed systems? When to use each?

# Vopros (RU)
> В чём разница между синхронной и асинхронной коммуникацией в распределённых системах? Когда использовать каждую?

---

## Answer (EN)

**Synchronous**: Caller waits for response. **Asynchronous**: Caller continues without waiting.

### Comparison

| Aspect | Synchronous | Asynchronous |
|--------|-------------|--------------|
| Coupling | Tight (temporal) | Loose |
| Latency | Additive | Parallel possible |
| Failure handling | Cascading failures | Isolated failures |
| Complexity | Simpler | More complex |
| Examples | REST, gRPC | Message queues, events |

### Synchronous Pattern

```
Client → Service A → Service B → Service C
         wait...     wait...     process
         wait...     wait...     ←──────
         wait...     ←──────────────────
         ←─────────────────────────────

Total latency = A + B + C
```

### Asynchronous Pattern

```
Client → Queue → Service A (processes independently)
       ↓
       → Queue → Service B (processes independently)
       ↓
       → Queue → Service C (processes independently)

Client gets immediate ACK, results delivered later
```

### When to Use Synchronous

- **User-facing requests** needing immediate response
- **Simple request-response** patterns
- **Strong consistency** requirements
- **Short operation chains** (2-3 services)

### When to Use Asynchronous

- **Long-running operations** (video processing)
- **Decoupled services** (microservices)
- **High throughput** (event streaming)
- **Resilience** (handle downstream failures)
- **Fan-out** patterns (notifications)

### Hybrid Approach

```
User Request → API Gateway (sync)
                    ↓
              Order Service → Response to user
                    ↓ (async)
              Payment Queue → Payment Service
                    ↓ (async)
              Notification Queue → Email Service
```

---

## Otvet (RU)

**Синхронная**: Вызывающий ждёт ответа. **Асинхронная**: Вызывающий продолжает без ожидания.

### Сравнение

| Аспект | Синхронная | Асинхронная |
|--------|------------|-------------|
| Связанность | Сильная (временная) | Слабая |
| Задержка | Аддитивная | Возможна параллельность |
| Обработка ошибок | Каскадные сбои | Изолированные сбои |
| Сложность | Проще | Сложнее |
| Примеры | REST, gRPC | Очереди сообщений, события |

### Синхронный паттерн

```
Клиент → Сервис A → Сервис B → Сервис C
         ждёт...    ждёт...    обработка

Общая задержка = A + B + C
```

### Асинхронный паттерн

```
Клиент → Очередь → Сервис A (обрабатывает независимо)
       ↓
       → Очередь → Сервис B (обрабатывает независимо)

Клиент получает немедленное подтверждение
```

### Когда использовать синхронную

- **Запросы пользователя** с немедленным ответом
- **Простые запрос-ответ** паттерны
- **Строгая согласованность**
- **Короткие цепочки** (2-3 сервиса)

### Когда использовать асинхронную

- **Долгие операции** (обработка видео)
- **Развязанные сервисы** (микросервисы)
- **Высокая пропускная способность**
- **Устойчивость** к сбоям downstream
- **Fan-out** паттерны (уведомления)

---

## Follow-ups

- How do you handle transactions across async services?
- What is the outbox pattern for reliable async messaging?
- How do you trace requests across async boundaries?
