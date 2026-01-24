---
id: sysdes-063
title: Chaos Engineering
aliases:
- Chaos Engineering
- Chaos Monkey
- Fault Injection
- GameDay
topic: system-design
subtopics:
- resilience
- testing
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
- q-circuit-breaker--system-design--medium
- q-graceful-degradation--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- resilience
- difficulty/medium
- testing
- system-design
anki_cards:
- slug: sysdes-063-0-en
  language: en
  anki_id: 1769160583577
  synced_at: '2026-01-23T13:49:17.797545'
- slug: sysdes-063-0-ru
  language: ru
  anki_id: 1769160583599
  synced_at: '2026-01-23T13:49:17.799787'
---
# Question (EN)
> What is chaos engineering? How does it help improve system reliability?

# Vopros (RU)
> Что такое хаос-инжиниринг? Как он помогает улучшить надёжность системы?

---

## Answer (EN)

**Chaos engineering** is the discipline of experimenting on a system to build confidence in its ability to withstand turbulent conditions in production.

### Core Principles

```
1. Build a hypothesis around steady state
   "Our system maintains 99.9% availability"

2. Vary real-world events
   Kill instances, inject latency, corrupt network

3. Run experiments in production
   Real conditions reveal real weaknesses

4. Automate experiments to run continuously
   Continuous validation, not one-time tests

5. Minimize blast radius
   Start small, expand gradually
```

### Types of Failures to Inject

| Category | Examples |
|----------|----------|
| Infrastructure | Kill instances, AZ failure |
| Network | Latency, packet loss, partition |
| Application | Memory pressure, CPU spike, disk full |
| Dependencies | Slow database, unavailable service |
| Data | Corrupt cache, invalid responses |

### Chaos Experiments

```
Experiment: Kill random production instance

Hypothesis: System auto-scales and maintains latency SLO

Steps:
1. Verify steady state (latency < 200ms, error rate < 0.1%)
2. Kill one instance in production
3. Monitor: Auto-scaling triggers? Latency spike?
4. Verify return to steady state within 5 minutes

Result:
- Pass: System recovered as expected
- Fail: Discovered auto-scaling delay, fixed configuration
```

### Netflix Chaos Tools

| Tool | Purpose |
|------|---------|
| Chaos Monkey | Kill random instances |
| Latency Monkey | Inject network delays |
| Chaos Kong | Simulate region failure |
| Chaos Gorilla | Simulate AZ failure |
| Conformity Monkey | Find non-compliant instances |

### GameDay

```
Planned chaos event:

1. Planning
   - Define scope and objectives
   - Identify participants
   - Prepare rollback procedures

2. Execution
   - Inject failures
   - Observe system behavior
   - Document findings

3. Analysis
   - What broke?
   - What worked well?
   - Action items for improvement

4. Follow-up
   - Fix identified issues
   - Update runbooks
   - Schedule next GameDay
```

### Best Practices

```
Start small:
1. Begin in staging/test environments
2. Run during business hours (team available)
3. Have rollback ready
4. Gradually increase blast radius

Progress:
Dev → Staging → Canary → Small % prod → Full prod
```

### Tools

| Tool | Provider | Features |
|------|----------|----------|
| Chaos Monkey | Netflix OSS | Random instance termination |
| Gremlin | Commercial | Comprehensive chaos platform |
| LitmusChaos | CNCF | Kubernetes-native |
| AWS FIS | AWS | Fault Injection Simulator |
| Chaos Mesh | PingCAP | Kubernetes chaos |

---

## Otvet (RU)

**Хаос-инжиниринг** - дисциплина экспериментирования над системой для повышения уверенности в её способности выдерживать турбулентные условия в production.

### Основные принципы

```
1. Построить гипотезу о steady state
   "Наша система поддерживает 99.9% доступность"

2. Варьировать реальные события
   Убивать инстансы, инжектить задержку, нарушать сеть

3. Запускать эксперименты в production
   Реальные условия выявляют реальные слабости

4. Автоматизировать непрерывное выполнение
   Постоянная валидация, не разовые тесты

5. Минимизировать blast radius
   Начинать с малого, расширять постепенно
```

### Типы инжектируемых сбоев

| Категория | Примеры |
|-----------|---------|
| Инфраструктура | Убить инстансы, сбой AZ |
| Сеть | Задержка, потеря пакетов, partition |
| Приложение | Давление на память, CPU spike, диск полон |
| Зависимости | Медленная БД, недоступный сервис |

### Chaos эксперименты

```
Эксперимент: Убить случайный production инстанс

Гипотеза: Система auto-scales и поддерживает latency SLO

Шаги:
1. Проверить steady state (latency < 200мс, error rate < 0.1%)
2. Убить один инстанс в production
3. Мониторить: Auto-scaling срабатывает? Всплеск latency?
4. Проверить возврат к steady state в течение 5 минут

Результат:
- Pass: Система восстановилась как ожидалось
- Fail: Обнаружена задержка auto-scaling, исправлена конфигурация
```

### GameDay

```
Запланированное chaos событие:

1. Планирование
   - Определить scope и цели
   - Идентифицировать участников
   - Подготовить процедуры отката

2. Выполнение
   - Инжектировать сбои
   - Наблюдать поведение системы
   - Документировать находки

3. Анализ
   - Что сломалось?
   - Что сработало хорошо?
   - Action items для улучшения
```

### Лучшие практики

```
Начинать с малого:
1. Сначала в staging/test окружениях
2. Запускать в рабочие часы (команда доступна)
3. Иметь готовый rollback
4. Постепенно увеличивать blast radius
```

---

## Follow-ups

- How do you measure the success of chaos experiments?
- What is the difference between chaos engineering and load testing?
- How do you get buy-in for chaos engineering from management?
