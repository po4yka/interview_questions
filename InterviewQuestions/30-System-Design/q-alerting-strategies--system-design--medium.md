---
id: sysdes-062
title: Alerting Strategies
aliases:
- Alerting
- Incident Management
- On-Call
- PagerDuty
topic: system-design
subtopics:
- observability
- operations
- reliability
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-sla-slo-sli--system-design--medium
- q-metrics-logs-traces--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- observability
- difficulty/medium
- operations
- system-design
anki_cards:
- slug: sysdes-062-0-en
  language: en
  anki_id: 1769160583726
  synced_at: '2026-01-23T13:49:17.805501'
- slug: sysdes-062-0-ru
  language: ru
  anki_id: 1769160583749
  synced_at: '2026-01-23T13:49:17.807153'
---
# Question (EN)
> What are best practices for alerting in production systems? How do you avoid alert fatigue?

# Vopros (RU)
> Каковы лучшие практики алертинга в продакшен системах? Как избежать усталости от алертов?

---

## Answer (EN)

Effective alerting notifies the right people about actionable problems while minimizing noise and alert fatigue.

### Alert Quality Principles

```
Good alert:
✓ Actionable (someone needs to do something)
✓ Urgent (needs attention now)
✓ Symptom-based (user impact, not cause)
✓ Has runbook link

Bad alert:
✗ CPU at 80% (so what?)
✗ Fires constantly (alert fatigue)
✗ No clear action
✗ Cause-based (disk full vs "service degraded")
```

### Alert Severity Levels

| Level | Response | Example | Action |
|-------|----------|---------|--------|
| P1/Critical | Immediate (page) | Service down | Wake someone up |
| P2/High | Within 1 hour | Degraded performance | During work hours |
| P3/Medium | Within 24 hours | Non-critical failure | Next business day |
| P4/Low | When convenient | Warning threshold | Backlog item |

### Symptom vs Cause Alerting

```
Cause-based (BAD):
- Alert: "Database CPU > 90%"
- Problem: May not affect users
- Result: Alert fatigue

Symptom-based (GOOD):
- Alert: "API error rate > 1%"
- Why: Users are experiencing errors
- Result: Actionable, clear impact
```

### Alert Configuration

```yaml
# Good alert example
alert: HighErrorRate
expr: |
  (
    sum(rate(http_requests_total{status=~"5.."}[5m]))
    /
    sum(rate(http_requests_total[5m]))
  ) > 0.01
for: 5m  # Must persist for 5 minutes
labels:
  severity: critical
  team: platform
annotations:
  summary: "High error rate detected"
  description: "Error rate is {{ $value | humanizePercentage }}"
  runbook: "https://wiki/runbooks/high-error-rate"
  dashboard: "https://grafana/d/api-errors"
```

### Reducing Alert Fatigue

| Strategy | Implementation |
|----------|----------------|
| Alert on symptoms | User-facing metrics, not internal |
| Set proper thresholds | Based on actual impact |
| Use "for" duration | Avoid flapping alerts |
| Aggregate related alerts | One alert for related issues |
| Regular review | Delete alerts that don't page |
| Silence during maintenance | Scheduled silences |

### On-Call Best Practices

```
1. Rotation schedule
   - 1-week rotations
   - Primary + secondary on-call
   - Follow-the-sun for global teams

2. Escalation policy
   Primary (5 min) → Secondary (10 min) → Manager (15 min)

3. Incident response
   - Acknowledge within 5 minutes
   - Communicate status updates
   - Postmortem for P1/P2

4. On-call compensation
   - Extra pay or time off
   - Reasonable alert volume target
```

### Alert Routing

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ Prometheus  │───►│ Alertmanager │───►│ PagerDuty   │
│   (fire)    │    │  (routing)   │    │ (notify)    │
└─────────────┘    └──────────────┘    └─────────────┘
                          │
                          ├──► Slack (P3/P4)
                          └──► Email (reports)
```

---

## Otvet (RU)

Эффективный алертинг уведомляет нужных людей о проблемах, требующих действий, минимизируя шум и усталость от алертов.

### Принципы качества алертов

```
Хороший алерт:
✓ Actionable (кто-то должен что-то сделать)
✓ Urgent (требует внимания сейчас)
✓ На основе симптомов (влияние на пользователя)
✓ Есть ссылка на runbook

Плохой алерт:
✗ CPU на 80% (и что?)
✗ Срабатывает постоянно (усталость)
✗ Нет чёткого действия
✗ На основе причины (диск полон vs "сервис деградирует")
```

### Уровни серьёзности

| Уровень | Реакция | Пример | Действие |
|---------|---------|--------|----------|
| P1/Critical | Немедленно (page) | Сервис упал | Разбудить кого-то |
| P2/High | В течение 1 часа | Деградация | В рабочие часы |
| P3/Medium | В течение 24 часов | Некритичный сбой | Следующий рабочий день |
| P4/Low | Когда удобно | Warning threshold | В бэклог |

### Симптомы vs Причины

```
На основе причины (ПЛОХО):
- Алерт: "Database CPU > 90%"
- Проблема: Может не влиять на пользователей
- Результат: Усталость от алертов

На основе симптомов (ХОРОШО):
- Алерт: "API error rate > 1%"
- Почему: Пользователи испытывают ошибки
- Результат: Actionable, ясное влияние
```

### Снижение усталости от алертов

| Стратегия | Реализация |
|-----------|------------|
| Алерты на симптомы | User-facing метрики |
| Правильные пороги | На основе реального влияния |
| Использовать "for" | Избегать flapping |
| Агрегировать связанные | Один алерт на связанные проблемы |
| Регулярный пересмотр | Удалять неработающие алерты |
| Silence при maintenance | Запланированные silences |

### Best practices On-Call

```
1. Расписание ротации
   - 1-недельные ротации
   - Primary + secondary on-call

2. Политика эскалации
   Primary (5 мин) → Secondary (10 мин) → Manager (15 мин)

3. Реагирование на инциденты
   - Acknowledge в течение 5 минут
   - Коммуникация статуса
   - Postmortem для P1/P2
```

---

## Follow-ups

- How do you write effective runbooks?
- What is the difference between alerting and logging?
- How do you handle alert storms?
