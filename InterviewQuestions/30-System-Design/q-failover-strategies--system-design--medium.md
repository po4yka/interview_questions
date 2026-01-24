---
id: sysdes-024
title: Failover Strategies
aliases:
- Failover
- Active-Passive
- Active-Active
topic: system-design
subtopics:
- resilience
- high-availability
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
- q-replication-strategies--system-design--medium
- q-circuit-breaker-pattern--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- resilience
- difficulty/medium
- high-availability
- system-design
anki_cards:
- slug: sysdes-024-0-en
  language: en
  anki_id: 1769158891291
  synced_at: '2026-01-23T13:49:17.823833'
- slug: sysdes-024-0-ru
  language: ru
  anki_id: 1769158891316
  synced_at: '2026-01-23T13:49:17.825353'
---
# Question (EN)
> What are the main failover strategies? Explain active-passive vs active-active and their trade-offs.

# Vopros (RU)
> Какие основные стратегии failover существуют? Объясните active-passive vs active-active и их компромиссы.

---

## Answer (EN)

**Failover** is the process of automatically switching to a redundant system when the primary system fails.

### Failover Types

**1. Active-Passive (Hot Standby)**
```
Normal operation:
[Active] ←── Traffic
[Passive]    (idle, synchronized)

After failover:
[Failed]
[Active] ←── Traffic (promoted)
```

**Characteristics:**
- Passive server is idle, only receives updates
- Failover requires promotion time
- Lower resource utilization
- Simpler to implement

**2. Active-Active (Hot-Hot)**
```
Normal operation:
[Active 1] ←── Traffic (50%)
[Active 2] ←── Traffic (50%)

After failover:
[Failed]
[Active 2] ←── Traffic (100%)
```

**Characteristics:**
- Both servers handle traffic
- Immediate failover (already serving)
- Better resource utilization
- More complex (conflict handling)

### Comparison Table

| Aspect | Active-Passive | Active-Active |
|--------|----------------|---------------|
| Resource usage | 50% idle | 100% utilized |
| Failover speed | Slower (promotion) | Faster (already active) |
| Complexity | Lower | Higher |
| Cost efficiency | Lower | Higher |
| Data conflicts | None | Possible |
| Use case | Databases | Stateless services |

### Failover Process

**1. Failure Detection**
```
Health Checks:
- Heartbeat (ping every N seconds)
- TCP/HTTP health endpoints
- Application-level checks

Timeout example:
- 3 missed heartbeats = failure detected
- Typical: 5-30 seconds to detect
```

**2. Failover Decision**
```
Manual:  Operator triggers failover
Automatic: System detects and switches
Semi-auto: System detects, operator confirms
```

**3. Traffic Redirection**
```
Methods:
- DNS update (slow propagation)
- Load balancer reconfiguration (fast)
- Virtual IP (VIP) migration (fast)
- Service discovery update
```

### Challenges

**Split-Brain Problem**
```
Network partition:
[Server A] ←┐              ┌─→ [Server B]
            │   Partition  │
[Clients]───┴──────────────┴───[Clients]

Both think they are primary → data divergence
```

**Solutions:**
- Quorum-based decisions (majority)
- STONITH (Shoot The Other Node In The Head)
- Fencing (block old primary's I/O)

### Failover Levels

| Level | What fails over | Example |
|-------|-----------------|---------|
| Application | App instances | Web servers |
| Database | DB primary | PostgreSQL, MySQL |
| Storage | Storage nodes | SAN, NAS |
| Network | Network paths | BGP, OSPF |
| Datacenter | Entire DC | DR site |

### Best Practices

1. **Test failover regularly** (chaos engineering)
2. **Automate failover** but have manual override
3. **Monitor failover events** and alert
4. **Plan for failback** (returning to primary)
5. **Document runbooks** for manual intervention

---

## Otvet (RU)

**Failover** - процесс автоматического переключения на резервную систему при отказе основной.

### Типы Failover

**1. Active-Passive (Hot Standby)**
```
Нормальная работа:
[Active] ←── Трафик
[Passive]    (простаивает, синхронизирован)

После failover:
[Failed]
[Active] ←── Трафик (повышен)
```

**Характеристики:**
- Passive сервер простаивает, только получает обновления
- Failover требует времени на промоушен
- Низкая утилизация ресурсов
- Проще в реализации

**2. Active-Active (Hot-Hot)**
```
Нормальная работа:
[Active 1] ←── Трафик (50%)
[Active 2] ←── Трафик (50%)

После failover:
[Failed]
[Active 2] ←── Трафик (100%)
```

**Характеристики:**
- Оба сервера обрабатывают трафик
- Мгновенный failover (уже обслуживает)
- Лучшая утилизация ресурсов
- Сложнее (обработка конфликтов)

### Сравнительная таблица

| Аспект | Active-Passive | Active-Active |
|--------|----------------|---------------|
| Использование ресурсов | 50% простаивает | 100% используется |
| Скорость failover | Медленнее (промоушен) | Быстрее (уже активен) |
| Сложность | Ниже | Выше |
| Эффективность затрат | Ниже | Выше |
| Конфликты данных | Нет | Возможны |
| Применение | Базы данных | Stateless сервисы |

### Процесс Failover

**1. Обнаружение сбоя**
```
Health Checks:
- Heartbeat (ping каждые N секунд)
- TCP/HTTP health endpoints
- Application-level проверки

Пример таймаута:
- 3 пропущенных heartbeat = сбой обнаружен
- Типично: 5-30 секунд на обнаружение
```

**2. Решение о Failover**
```
Ручной:       Оператор запускает failover
Автоматический: Система обнаруживает и переключает
Полуавтомат:  Система обнаруживает, оператор подтверждает
```

**3. Перенаправление трафика**
```
Методы:
- DNS обновление (медленное распространение)
- Реконфигурация load balancer (быстро)
- Миграция Virtual IP (VIP) (быстро)
- Обновление service discovery
```

### Сложности

**Проблема Split-Brain**
```
Сетевое разделение:
[Сервер A] ←┐              ┌─→ [Сервер B]
            │   Partition  │
[Клиенты]───┴──────────────┴───[Клиенты]

Оба считают себя primary → расхождение данных
```

**Решения:**
- Quorum-based решения (большинство)
- STONITH (Shoot The Other Node In The Head)
- Fencing (блокировка I/O старого primary)

### Уровни Failover

| Уровень | Что переключается | Пример |
|---------|-------------------|--------|
| Приложение | Инстансы приложения | Web серверы |
| База данных | DB primary | PostgreSQL, MySQL |
| Хранилище | Узлы хранения | SAN, NAS |
| Сеть | Сетевые пути | BGP, OSPF |
| Датацентр | Весь DC | DR сайт |

### Лучшие практики

1. **Тестируйте failover регулярно** (chaos engineering)
2. **Автоматизируйте failover** но имейте ручной override
3. **Мониторьте события failover** и алертите
4. **Планируйте failback** (возврат на primary)
5. **Документируйте runbooks** для ручного вмешательства

---

## Follow-ups

- How do you implement zero-downtime failover?
- What is the difference between failover and switchover?
- How do you handle long-running transactions during failover?

## Related Questions

### Prerequisites (Easier)
- [[q-replication-strategies--system-design--medium]] - Replication

### Related (Same Level)
- [[q-circuit-breaker-pattern--system-design--medium]] - Circuit breaker
- [[q-master-slave-master-master--system-design--medium]] - Master patterns

### Advanced (Harder)
- [[q-design-notification-system--system-design--hard]] - System design
