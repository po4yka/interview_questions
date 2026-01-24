---
id: sysdes-042
title: Distributed Tracing
aliases:
- Distributed Tracing
- Request Tracing
- Trace Context
topic: system-design
subtopics:
- observability
- debugging
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
- q-metrics-logs-traces--system-design--medium
- q-sync-async-communication--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- observability
- difficulty/medium
- debugging
- system-design
anki_cards:
- slug: sysdes-042-0-en
  language: en
  anki_id: 1769159519593
  synced_at: '2026-01-23T13:29:45.892375'
- slug: sysdes-042-0-ru
  language: ru
  anki_id: 1769159519620
  synced_at: '2026-01-23T13:29:45.893597'
---
# Question (EN)
> What is distributed tracing? How does it help debug microservices?

# Vopros (RU)
> Что такое распределённая трассировка? Как она помогает отлаживать микросервисы?

---

## Answer (EN)

**Distributed tracing** tracks requests across multiple services, creating a unified view of the request flow.

### Core Concepts

```
Trace: Complete request journey (one trace ID)
Span: Single operation within a trace
Parent-Child: Spans form a tree structure

Trace ID: abc123
├── Span 1: API Gateway (50ms)
│   └── Span 2: Auth Service (10ms)
├── Span 3: Order Service (100ms)
│   ├── Span 4: Inventory Check (30ms)
│   └── Span 5: Payment Service (60ms)
└── Span 6: Notification (async, 20ms)
```

### How It Works

```
1. Request enters → Generate trace ID
2. Each service → Creates span with trace ID
3. Calls downstream → Propagates trace ID in headers
4. Collect spans → Tracing backend (Jaeger, Zipkin)
5. Visualize → Trace timeline view
```

### Trace Context Propagation

```
Headers:
  traceparent: 00-{trace-id}-{span-id}-{flags}
  tracestate: vendor=value

Example:
  traceparent: 00-abc123-span456-01
```

### What Traces Reveal

| Problem | Trace Shows |
|---------|-------------|
| Slow request | Which service/span took longest |
| Errors | Where in the chain failure occurred |
| Bottlenecks | Services with high latency |
| Dependencies | Actual call graph (not documented) |
| Async issues | Gaps in processing |

### Sampling Strategies

```
Head-based: Decide at start (random %)
Tail-based: Decide after complete (keep errors/slow)
Adaptive: Adjust rate based on traffic

Production: 1-10% sampling (cost vs visibility)
```

### Popular Tools

| Tool | Type | Notes |
|------|------|-------|
| Jaeger | Open source | CNCF, Uber origin |
| Zipkin | Open source | Twitter origin |
| AWS X-Ray | Managed | AWS native |
| Datadog APM | Commercial | Full observability |
| OpenTelemetry | Standard | Vendor-neutral SDK |

---

## Otvet (RU)

**Распределённая трассировка** отслеживает запросы через множество сервисов, создавая единое представление потока запроса.

### Основные концепции

```
Trace: Полный путь запроса (один trace ID)
Span: Одна операция внутри trace
Parent-Child: Span'ы образуют дерево

Trace ID: abc123
├── Span 1: API Gateway (50мс)
│   └── Span 2: Auth Service (10мс)
├── Span 3: Order Service (100мс)
│   ├── Span 4: Проверка инвентаря (30мс)
│   └── Span 5: Payment Service (60мс)
└── Span 6: Уведомление (async, 20мс)
```

### Как это работает

```
1. Запрос входит → Генерируется trace ID
2. Каждый сервис → Создаёт span с trace ID
3. Вызов downstream → Передаёт trace ID в заголовках
4. Собираются span'ы → Backend трассировки (Jaeger, Zipkin)
5. Визуализация → Timeline view
```

### Что показывают трейсы

| Проблема | Трейс показывает |
|----------|------------------|
| Медленный запрос | Какой сервис/span занял больше времени |
| Ошибки | Где в цепочке произошёл сбой |
| Узкие места | Сервисы с высокой задержкой |
| Зависимости | Реальный граф вызовов |
| Проблемы async | Пробелы в обработке |

### Стратегии сэмплирования

```
Head-based: Решение в начале (случайный %)
Tail-based: Решение после завершения (сохранять ошибки/медленные)
Adaptive: Адаптация к трафику

Продакшен: 1-10% сэмплирование (стоимость vs видимость)
```

### Популярные инструменты

| Инструмент | Тип | Примечание |
|------------|-----|------------|
| Jaeger | Open source | CNCF, от Uber |
| Zipkin | Open source | От Twitter |
| AWS X-Ray | Managed | AWS нативный |
| OpenTelemetry | Стандарт | Vendor-neutral SDK |

---

## Follow-ups

- How do you trace async message queues?
- What is the overhead of distributed tracing?
- How does OpenTelemetry unify tracing standards?
