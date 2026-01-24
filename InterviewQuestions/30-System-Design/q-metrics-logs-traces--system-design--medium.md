---
id: sysdes-043
title: Metrics vs Logs vs Traces
aliases:
- Three Pillars of Observability
- Observability Pillars
- Metrics Logs Traces
topic: system-design
subtopics:
- observability
- monitoring
- debugging
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-distributed-tracing--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- observability
- difficulty/medium
- monitoring
- system-design
anki_cards:
- slug: sysdes-043-0-en
  language: en
  anki_id: 1769159522398
  synced_at: '2026-01-23T13:49:17.857093'
- slug: sysdes-043-0-ru
  language: ru
  anki_id: 1769159522419
  synced_at: '2026-01-23T13:49:17.858080'
---
# Question (EN)
> What are the three pillars of observability? When do you use metrics, logs, or traces?

# Vopros (RU)
> Что такое три столпа observability? Когда использовать метрики, логи или трейсы?

---

## Answer (EN)

The **three pillars of observability** are **metrics**, **logs**, and **traces** - complementary signals for understanding system behavior.

### Comparison

| Aspect | Metrics | Logs | Traces |
|--------|---------|------|--------|
| What | Numeric measurements | Event records | Request flow |
| Cardinality | Low (aggregated) | High (per event) | Medium (sampled) |
| Use for | Alerting, dashboards | Debugging, audit | Request debugging |
| Cost | Lowest | Highest | Medium |
| Example | "500 errors/min" | "Error: null pointer at line 42" | "Request abc took 500ms across 5 services" |

### Metrics

```
Numeric values over time, aggregated

Types:
- Counter: Only goes up (requests_total)
- Gauge: Goes up/down (active_connections)
- Histogram: Distribution (request_duration)

Use for:
✓ Alerting (error rate > 1%)
✓ Dashboards (real-time health)
✓ SLIs/SLOs (99.9% availability)
✓ Capacity planning (trend analysis)
```

### Logs

```
Discrete events with context

Example:
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "ERROR",
  "service": "payment",
  "user_id": "123",
  "message": "Payment failed: card declined",
  "trace_id": "abc123"
}

Use for:
✓ Debugging specific errors
✓ Audit trails
✓ Security investigation
✓ Post-incident analysis
```

### Traces

```
Request path across services

        API Gateway (50ms)
            ↓
        Auth Service (10ms)
            ↓
        Order Service (200ms)  ← bottleneck!
           ├── DB Query (150ms)
           └── Cache (5ms)

Use for:
✓ Finding slow services
✓ Understanding dependencies
✓ Debugging distributed errors
✓ Latency analysis
```

### When to Use Each

| Question | Use |
|----------|-----|
| "Is the system healthy?" | Metrics |
| "Why did this request fail?" | Logs + Traces |
| "Where is the bottleneck?" | Traces |
| "What happened at 3 AM?" | Logs |
| "Should I page someone?" | Metrics (alerts) |

### Integration Pattern

```
Metrics → Alert fires (high error rate)
       ↓
Traces → Find affected requests (trace IDs)
       ↓
Logs → Get detailed error context (by trace ID)
```

---

## Otvet (RU)

**Три столпа observability** - это **метрики**, **логи** и **трейсы** - взаимодополняющие сигналы для понимания поведения системы.

### Сравнение

| Аспект | Метрики | Логи | Трейсы |
|--------|---------|------|--------|
| Что | Числовые измерения | Записи событий | Поток запроса |
| Кардинальность | Низкая (агрегированные) | Высокая (на событие) | Средняя (сэмплированные) |
| Для чего | Алертинг, дашборды | Отладка, аудит | Отладка запросов |
| Стоимость | Наименьшая | Наивысшая | Средняя |

### Метрики

```
Числовые значения во времени, агрегированные

Типы:
- Counter: Только растёт (requests_total)
- Gauge: Растёт/падает (active_connections)
- Histogram: Распределение (request_duration)

Использовать для:
✓ Алертинга (error rate > 1%)
✓ Дашбордов (состояние в реальном времени)
✓ SLI/SLO (99.9% доступность)
```

### Логи

```
Дискретные события с контекстом

Использовать для:
✓ Отладка конкретных ошибок
✓ Аудит трейлы
✓ Расследование безопасности
✓ Анализ после инцидента
```

### Трейсы

```
Путь запроса через сервисы

Использовать для:
✓ Поиск медленных сервисов
✓ Понимание зависимостей
✓ Отладка распределённых ошибок
```

### Когда использовать

| Вопрос | Использовать |
|--------|--------------|
| "Система здорова?" | Метрики |
| "Почему запрос упал?" | Логи + Трейсы |
| "Где узкое место?" | Трейсы |
| "Что случилось в 3 ночи?" | Логи |
| "Будить кого-то?" | Метрики (алерты) |

### Паттерн интеграции

```
Метрики → Алерт срабатывает (высокий error rate)
       ↓
Трейсы → Найти затронутые запросы (trace IDs)
       ↓
Логи → Получить детальный контекст ошибки (по trace ID)
```

---

## Follow-ups

- How do you correlate logs with traces?
- What is structured logging and why is it important?
- How do you manage log volume in high-traffic systems?
