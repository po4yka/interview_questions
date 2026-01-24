---
id: sysdes-041
title: Graceful Degradation
aliases:
- Graceful Degradation
- Fallback Strategies
- Partial Functionality
topic: system-design
subtopics:
- resilience
- availability
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
- q-bulkhead-pattern--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- resilience
- difficulty/medium
- availability
- system-design
anki_cards:
- slug: sysdes-041-0-en
  language: en
  anki_id: 1769159519694
  synced_at: '2026-01-23T13:29:45.898498'
- slug: sysdes-041-0-ru
  language: ru
  anki_id: 1769159519719
  synced_at: '2026-01-23T13:29:45.899565'
---
# Question (EN)
> What is graceful degradation? How do you implement fallback strategies in distributed systems?

# Vopros (RU)
> Что такое плавная деградация? Как реализовать стратегии fallback в распределённых системах?

---

## Answer (EN)

**Graceful degradation** maintains partial functionality when components fail, rather than complete system failure.

### Core Principle

```
Full functionality:  🟢 Search + Recommendations + Reviews + Personalization

Degraded (recs down): 🟡 Search + Generic Items + Reviews (still usable)

Degraded (DB slow):   🟡 Search + Cached Results (stale but fast)

Critical failure:     🔴 Static page "Service unavailable"
```

### Fallback Strategies

| Strategy | Use Case | Example |
|----------|----------|---------|
| Cache fallback | DB unavailable | Serve stale cached data |
| Default values | Service timeout | Show generic recommendations |
| Feature toggle | Partial outage | Disable non-critical features |
| Static content | Major outage | Show cached static page |
| Alternative service | Primary down | Switch to backup provider |

### Implementation Example

```python
async def get_recommendations(user_id):
    try:
        # Primary: personalized recommendations
        return await recommendation_service.get(user_id, timeout=500)
    except TimeoutError:
        # Fallback 1: cached recommendations
        cached = await cache.get(f"recs:{user_id}")
        if cached:
            return cached
        # Fallback 2: popular items
        return await get_popular_items()
    except ServiceUnavailable:
        # Fallback 3: static defaults
        return DEFAULT_RECOMMENDATIONS

def get_product_page(product_id):
    product = get_product(product_id)  # Required

    # Optional components with fallbacks
    reviews = safe_get(lambda: get_reviews(product_id), default=[])
    related = safe_get(lambda: get_related(product_id), default=[])
    inventory = safe_get(lambda: get_inventory(product_id), default="Check in store")

    return render(product, reviews, related, inventory)
```

### Degradation Levels

```
Level 0: Full functionality
         ↓ (Non-critical service fails)
Level 1: Core features work, extras disabled
         ↓ (Database slow)
Level 2: Read-only mode with cached data
         ↓ (Major outage)
Level 3: Static fallback page
```

### Design Principles

1. **Identify critical path**: What MUST work?
2. **Define fallbacks**: What happens when X fails?
3. **Set timeouts**: Fast failure enables fallback
4. **Monitor degradation**: Alert on fallback usage
5. **Test failures**: Chaos engineering

---

## Otvet (RU)

**Плавная деградация** сохраняет частичную функциональность при отказе компонентов вместо полного падения системы.

### Основной принцип

```
Полная функциональность:  🟢 Поиск + Рекомендации + Отзывы + Персонализация

Деградация (рекомендации): 🟡 Поиск + Общие товары + Отзывы (всё ещё работает)

Деградация (БД медленная): 🟡 Поиск + Кешированные результаты (устаревшие, но быстрые)

Критический сбой:         🔴 Статическая страница "Сервис недоступен"
```

### Стратегии Fallback

| Стратегия | Случай | Пример |
|-----------|--------|--------|
| Fallback на кеш | БД недоступна | Отдавать устаревшие данные |
| Значения по умолчанию | Таймаут сервиса | Общие рекомендации |
| Feature toggle | Частичный сбой | Отключить некритичные фичи |
| Статический контент | Крупный сбой | Кешированная статическая страница |
| Альтернативный сервис | Primary упал | Переключиться на backup |

### Уровни деградации

```
Уровень 0: Полная функциональность
           ↓ (Некритичный сервис падает)
Уровень 1: Основные фичи работают, дополнительные отключены
           ↓ (БД медленная)
Уровень 2: Режим только чтения с кешированными данными
           ↓ (Крупный сбой)
Уровень 3: Статическая fallback страница
```

### Принципы проектирования

1. **Определить критический путь**: Что ДОЛЖНО работать?
2. **Определить fallback**: Что происходит при отказе X?
3. **Установить таймауты**: Быстрый отказ включает fallback
4. **Мониторить деградацию**: Алерт при использовании fallback
5. **Тестировать отказы**: Chaos engineering

---

## Follow-ups

- How do you decide what's critical vs optional?
- What is the difference between graceful degradation and circuit breaker?
- How do you test graceful degradation in production?
