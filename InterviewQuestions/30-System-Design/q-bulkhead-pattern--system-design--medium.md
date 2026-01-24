---
id: sysdes-040
title: Bulkhead Pattern
aliases:
- Bulkhead
- Resource Isolation
- Fault Isolation
topic: system-design
subtopics:
- resilience
- patterns
- fault-tolerance
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
- patterns
- system-design
anki_cards:
- slug: sysdes-040-0-en
  language: en
  anki_id: 1769159519644
  synced_at: '2026-01-23T13:29:45.895824'
- slug: sysdes-040-0-ru
  language: ru
  anki_id: 1769159519668
  synced_at: '2026-01-23T13:29:45.897278'
---
# Question (EN)
> What is the Bulkhead pattern? How does it improve system resilience?

# Vopros (RU)
> Что такое паттерн Bulkhead? Как он улучшает устойчивость системы?

---

## Answer (EN)

**Bulkhead pattern** isolates resources to prevent failures from cascading across the system. Named after ship compartments that prevent flooding from sinking the entire vessel.

### Core Concept

```
Without Bulkhead:
┌─────────────────────────────────┐
│  Shared Thread Pool (100)       │
│  Service A ████████████████████ │ ← A uses all threads
│  Service B (blocked)            │ ← B cannot work
│  Service C (blocked)            │ ← C cannot work
└─────────────────────────────────┘

With Bulkhead:
┌──────────┬──────────┬──────────┐
│ Pool A   │ Pool B   │ Pool C   │
│ (30)     │ (40)     │ (30)     │
│ ████████ │ ░░░░░░░░ │ ░░░░░░░░ │
│ A overload│ B works │ C works  │
└──────────┴──────────┴──────────┘
```

### Types of Bulkheads

| Type | Isolation | Use Case |
|------|-----------|----------|
| Thread pool | Threads | Sync calls |
| Semaphore | Concurrent requests | Async calls |
| Connection pool | DB connections | Database access |
| Process | Memory/CPU | Critical services |
| Container | Full isolation | Microservices |

### Implementation Example

```python
# Thread pool bulkhead
class BulkheadExecutor:
    def __init__(self, max_concurrent=10):
        self.semaphore = Semaphore(max_concurrent)

    def execute(self, task):
        if not self.semaphore.acquire(timeout=1):
            raise BulkheadFullException()
        try:
            return task()
        finally:
            self.semaphore.release()

# Separate bulkheads per service
payment_bulkhead = BulkheadExecutor(max_concurrent=20)
inventory_bulkhead = BulkheadExecutor(max_concurrent=30)
```

### Benefits

- **Fault isolation**: One slow service doesn't block others
- **Resource guarantee**: Critical services get reserved resources
- **Graceful degradation**: System partially works under load
- **Predictable capacity**: Known limits per component

### Sizing Guidelines

- Reserve 20-30% extra capacity per pool
- Base size on historical usage + peak load
- Monitor and adjust based on metrics
- Consider priority (critical services get more)

---

## Otvet (RU)

**Паттерн Bulkhead** изолирует ресурсы для предотвращения каскадных сбоев. Назван по аналогии с переборками корабля.

### Основная концепция

```
Без Bulkhead:
┌─────────────────────────────────┐
│  Общий пул потоков (100)        │
│  Сервис A ██████████████████████ │ ← A использует все
│  Сервис B (заблокирован)        │
│  Сервис C (заблокирован)        │
└─────────────────────────────────┘

С Bulkhead:
┌──────────┬──────────┬──────────┐
│ Пул A    │ Пул B    │ Пул C    │
│ (30)     │ (40)     │ (30)     │
│ ████████ │ ░░░░░░░░ │ ░░░░░░░░ │
│ A перегруз│ B работает│ C работает│
└──────────┴──────────┴──────────┘
```

### Типы Bulkhead

| Тип | Изоляция | Применение |
|-----|----------|------------|
| Пул потоков | Потоки | Синхронные вызовы |
| Семафор | Параллельные запросы | Асинхронные вызовы |
| Пул соединений | Соединения БД | Доступ к БД |
| Процесс | Память/CPU | Критичные сервисы |
| Контейнер | Полная изоляция | Микросервисы |

### Преимущества

- **Изоляция сбоев**: Один медленный сервис не блокирует другие
- **Гарантия ресурсов**: Критичные сервисы получают зарезервированные ресурсы
- **Плавная деградация**: Система частично работает под нагрузкой
- **Предсказуемая ёмкость**: Известные лимиты на компонент

### Рекомендации по размеру

- Резервируйте 20-30% дополнительной ёмкости на пул
- Базируйте размер на исторических данных + пиковая нагрузка
- Мониторьте и корректируйте по метрикам

---

## Follow-ups

- How do bulkheads work with circuit breakers?
- What is the difference between bulkhead and rate limiting?
- How do you size bulkhead pools dynamically?
