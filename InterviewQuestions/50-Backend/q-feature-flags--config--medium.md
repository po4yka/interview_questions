---
id: be-cfg-002
title: Feature Flags / Флаги функций
aliases: []
topic: config
subtopics:
- feature-flags
- deployment
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Backend interview preparation
status: draft
moc: moc-backend
related:
- c-configuration
- c-deployment
created: 2025-01-23
updated: 2025-01-23
tags:
- config
- feature-flags
- deployment
- difficulty/medium
- topic/config
anki_cards:
- slug: be-cfg-002-0-en
  language: en
  anki_id: 1769167239579
  synced_at: '2026-01-23T15:20:42.933361'
- slug: be-cfg-002-0-ru
  language: ru
  anki_id: 1769167239603
  synced_at: '2026-01-23T15:20:42.935478'
---
# Question (EN)
> What are feature flags and how to implement them?

# Vopros (RU)
> Что такое feature flags и как их реализовать?

---

## Answer (EN)

**Feature Flags (Feature Toggles)** - Configuration that allows enabling/disabling features at runtime without deploying new code.

**Use Cases:**
- Gradual rollouts (canary releases)
- A/B testing
- Kill switches for problematic features
- Beta features for specific users
- Trunk-based development

---

**Implementation Levels:**

**1. Simple Boolean Flag:**
```python
# config.py
FEATURES = {
    "new_checkout": False,
    "dark_mode": True,
}

# usage
if FEATURES["new_checkout"]:
    return new_checkout_flow()
else:
    return old_checkout_flow()
```

**2. User-Based Targeting:**
```python
def is_feature_enabled(feature: str, user: User) -> bool:
    flag = get_flag(feature)

    if flag.enabled_for_all:
        return True

    if user.id in flag.allowed_user_ids:
        return True

    if user.email.endswith("@company.com"):
        return True  # Internal users

    return False
```

**3. Percentage Rollout:**
```python
import hashlib

def is_enabled_for_percentage(feature: str, user_id: int, percentage: int) -> bool:
    # Consistent hashing - same user always gets same result
    hash_input = f"{feature}:{user_id}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
    bucket = hash_value % 100

    return bucket < percentage
```

---

**Feature Flag Service:**

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class FeatureFlag:
    name: str
    enabled: bool = False
    percentage: int = 0  # 0-100
    allowed_users: List[int] = None
    allowed_groups: List[str] = None

class FeatureFlagService:
    def __init__(self, flags_repo: FlagsRepository):
        self.repo = flags_repo
        self._cache = {}

    def is_enabled(
        self,
        feature: str,
        user_id: Optional[int] = None,
        context: dict = None
    ) -> bool:
        flag = self._get_flag(feature)

        if not flag or not flag.enabled:
            return False

        # Check user allowlist
        if user_id and flag.allowed_users:
            if user_id in flag.allowed_users:
                return True

        # Check percentage rollout
        if flag.percentage > 0 and user_id:
            return is_enabled_for_percentage(feature, user_id, flag.percentage)

        return flag.enabled and flag.percentage == 100
```

---

**Feature Flag Patterns:**

| Pattern | Use Case |
|---------|----------|
| **Release Toggle** | Deploy dark, enable later |
| **Experiment Toggle** | A/B testing |
| **Ops Toggle** | Kill switch |
| **Permission Toggle** | Premium features |

**Best Practices:**
- Remove flags after full rollout
- Document flag purpose and owner
- Set expiration dates
- Use feature flag service (LaunchDarkly, Unleash)
- Test both flag states

**Anti-patterns:**
- Long-lived flags (technical debt)
- Nested flags (complexity)
- No cleanup process

## Otvet (RU)

**Feature Flags (Feature Toggles)** - Конфигурация, позволяющая включать/выключать функции во время выполнения без деплоя нового кода.

**Сценарии использования:**
- Постепенные выкатки (canary releases)
- A/B-тестирование
- Kill switches для проблемных функций
- Бета-функции для определённых пользователей
- Trunk-based development

---

**Уровни реализации:**

**1. Простой булевый флаг:**
```python
# config.py
FEATURES = {
    "new_checkout": False,
    "dark_mode": True,
}

# использование
if FEATURES["new_checkout"]:
    return new_checkout_flow()
else:
    return old_checkout_flow()
```

**2. Таргетинг по пользователю:**
```python
def is_feature_enabled(feature: str, user: User) -> bool:
    flag = get_flag(feature)

    if flag.enabled_for_all:
        return True

    if user.id in flag.allowed_user_ids:
        return True

    if user.email.endswith("@company.com"):
        return True  # Внутренние пользователи

    return False
```

**3. Процентный выкат:**
```python
import hashlib

def is_enabled_for_percentage(feature: str, user_id: int, percentage: int) -> bool:
    # Консистентное хеширование - один пользователь всегда получает одинаковый результат
    hash_input = f"{feature}:{user_id}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
    bucket = hash_value % 100

    return bucket < percentage
```

---

**Сервис Feature Flag:**

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class FeatureFlag:
    name: str
    enabled: bool = False
    percentage: int = 0  # 0-100
    allowed_users: List[int] = None
    allowed_groups: List[str] = None

class FeatureFlagService:
    def __init__(self, flags_repo: FlagsRepository):
        self.repo = flags_repo
        self._cache = {}

    def is_enabled(
        self,
        feature: str,
        user_id: Optional[int] = None,
        context: dict = None
    ) -> bool:
        flag = self._get_flag(feature)

        if not flag or not flag.enabled:
            return False

        # Проверка allowlist пользователей
        if user_id and flag.allowed_users:
            if user_id in flag.allowed_users:
                return True

        # Проверка процентного выката
        if flag.percentage > 0 and user_id:
            return is_enabled_for_percentage(feature, user_id, flag.percentage)

        return flag.enabled and flag.percentage == 100
```

---

**Паттерны Feature Flag:**

| Паттерн | Сценарий |
|---------|----------|
| **Release Toggle** | Деплой скрыто, включить позже |
| **Experiment Toggle** | A/B-тестирование |
| **Ops Toggle** | Kill switch |
| **Permission Toggle** | Премиум-функции |

**Лучшие практики:**
- Удалять флаги после полного выката
- Документировать цель и владельца флага
- Устанавливать даты истечения
- Использовать сервис флагов (LaunchDarkly, Unleash)
- Тестировать оба состояния флага

**Антипаттерны:**
- Долгоживущие флаги (технический долг)
- Вложенные флаги (сложность)
- Отсутствие процесса очистки

---

## Follow-ups
- How to implement A/B testing with feature flags?
- What is trunk-based development?
- How to handle database migrations with feature flags?

## Dopolnitelnye voprosy (RU)
- Как реализовать A/B-тестирование с feature flags?
- Что такое trunk-based development?
- Как обрабатывать миграции БД с feature flags?

## References
- [[c-configuration]]
- [[c-deployment]]
- [[moc-backend]]
