---
id: sysdes-051
title: SLA, SLO, and SLI
aliases:
- SLA SLO SLI
- Service Level Agreement
- Service Level Objectives
topic: system-design
subtopics:
- core-concepts
- reliability
- operations
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
created: 2025-01-23
updated: 2025-01-23
tags:
- core-concepts
- difficulty/medium
- reliability
- system-design
anki_cards:
- slug: sysdes-051-0-en
  language: en
  anki_id: 1769160585828
  synced_at: '2026-01-23T13:49:17.869727'
- slug: sysdes-051-0-ru
  language: ru
  anki_id: 1769160585848
  synced_at: '2026-01-23T13:49:17.870745'
---
# Question (EN)
> What are SLA, SLO, and SLI? How do they relate to each other in defining system reliability?

# Vopros (RU)
> Что такое SLA, SLO и SLI? Как они связаны друг с другом при определении надёжности системы?

---

## Answer (EN)

**SLI** (Service Level Indicator), **SLO** (Service Level Objective), and **SLA** (Service Level Agreement) form a hierarchy for measuring and guaranteeing service reliability.

### The Hierarchy

```
SLI → SLO → SLA

SLI: What you measure
SLO: What you target internally
SLA: What you promise externally (with consequences)
```

### Definitions

| Term | Definition | Example |
|------|------------|---------|
| **SLI** | Metric that measures service behavior | Request latency, error rate, availability |
| **SLO** | Target value/range for an SLI | 99.9% availability, p99 latency < 200ms |
| **SLA** | Contract with consequences if SLO not met | 99.9% uptime or credits issued |

### Practical Example

```
SLI: Percentage of successful HTTP requests
     Formula: (successful requests / total requests) * 100

SLO: 99.9% of requests must succeed
     Internal target: 99.95% (buffer)

SLA: "We guarantee 99.9% availability.
      If we fail, you get 10% credit."
```

### Common SLIs

| Category | SLI | Measurement |
|----------|-----|-------------|
| Availability | Uptime | % of time service responds |
| Latency | Response time | p50, p95, p99 percentiles |
| Throughput | Request rate | Requests per second |
| Error rate | Failures | % of 5xx responses |
| Correctness | Data accuracy | % of correct responses |

### Error Budget

```
SLO: 99.9% availability
Error Budget: 0.1% = 43.2 minutes/month of allowed downtime

Month progress:
- Week 1: 5 min downtime → 38.2 min remaining
- Week 2: 10 min downtime → 28.2 min remaining
- Week 3: 0 min downtime → 28.2 min remaining

If budget exhausted → freeze deployments, focus on reliability
```

### Best Practices

1. **SLO < SLA**: Always set internal targets stricter than external promises
2. **Measure what matters**: Choose SLIs that reflect user experience
3. **Error budgets**: Use remaining budget to balance velocity vs reliability
4. **Review regularly**: Adjust SLOs based on actual performance

---

## Otvet (RU)

**SLI** (Service Level Indicator), **SLO** (Service Level Objective) и **SLA** (Service Level Agreement) образуют иерархию для измерения и гарантирования надёжности сервиса.

### Иерархия

```
SLI → SLO → SLA

SLI: Что вы измеряете
SLO: Какую цель ставите внутри
SLA: Что обещаете снаружи (с последствиями)
```

### Определения

| Термин | Определение | Пример |
|--------|-------------|--------|
| **SLI** | Метрика поведения сервиса | Задержка запроса, error rate, доступность |
| **SLO** | Целевое значение/диапазон для SLI | 99.9% доступность, p99 < 200мс |
| **SLA** | Контракт с последствиями при нарушении SLO | 99.9% uptime или кредиты |

### Практический пример

```
SLI: Процент успешных HTTP запросов
     Формула: (успешные запросы / всего запросов) * 100

SLO: 99.9% запросов должны быть успешны
     Внутренняя цель: 99.95% (буфер)

SLA: "Мы гарантируем 99.9% доступность.
      При нарушении - 10% кредит."
```

### Error Budget

```
SLO: 99.9% доступность
Error Budget: 0.1% = 43.2 минуты/месяц допустимого простоя

Прогресс месяца:
- Неделя 1: 5 мин простоя → осталось 38.2 мин
- Неделя 2: 10 мин простоя → осталось 28.2 мин

Если бюджет исчерпан → заморозить деплои, фокус на надёжность
```

### Лучшие практики

1. **SLO < SLA**: Внутренние цели строже внешних обещаний
2. **Измеряйте важное**: SLI должны отражать опыт пользователя
3. **Error budgets**: Баланс между скоростью и надёжностью
4. **Регулярный пересмотр**: Корректируйте SLO по реальным данным

---

## Follow-ups

- How do you choose the right SLIs for your service?
- What happens when you exhaust your error budget?
- How do SLOs differ for different user tiers?
