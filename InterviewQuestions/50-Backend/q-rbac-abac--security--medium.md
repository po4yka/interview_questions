---
id: be-sec-005
title: RBAC vs ABAC Authorization / Авторизация RBAC vs ABAC
aliases: []
topic: security
subtopics:
- authorization
- access-control
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
- c-authorization
- c-access-control
created: 2025-01-23
updated: 2025-01-23
tags:
- security
- authorization
- rbac
- abac
- difficulty/medium
- topic/security
anki_cards:
- slug: be-sec-005-0-en
  language: en
  anki_id: 1769167239529
  synced_at: '2026-01-23T15:20:42.930400'
- slug: be-sec-005-0-ru
  language: ru
  anki_id: 1769167239555
  synced_at: '2026-01-23T15:20:42.932070'
---
# Question (EN)
> What is the difference between RBAC and ABAC authorization models?

# Vopros (RU)
> В чём разница между моделями авторизации RBAC и ABAC?

---

## Answer (EN)

**RBAC (Role-Based Access Control)**

Access is granted based on user's **role** in the organization.

```
User -> Role -> Permissions

Example:
  user: alice -> role: editor -> permissions: [read, write, publish]
```

**Implementation:**
```python
# Check role
if user.role == "admin":
    allow_action()

# Check permission via role
if "delete" in user.role.permissions:
    allow_delete()
```

**Pros:** Simple, easy to audit, works well for static hierarchies
**Cons:** Role explosion in complex systems, no context-awareness

---

**ABAC (Attribute-Based Access Control)**

Access is granted based on **attributes** of user, resource, action, and environment.

```
Policy: "Allow if user.department == resource.department
         AND time is business_hours"
```

**Implementation:**
```python
# Policy engine evaluates attributes
policy_decision = evaluate_policy(
    subject={"role": "doctor", "department": "cardiology"},
    resource={"type": "patient_record", "department": "cardiology"},
    action="read",
    environment={"time": "14:00", "location": "hospital"}
)
```

**Pros:** Fine-grained, context-aware, scales to complex requirements
**Cons:** Complex to implement, harder to audit, performance overhead

---

**Comparison:**

| Aspect | RBAC | ABAC |
|--------|------|------|
| Complexity | Simple | Complex |
| Granularity | Coarse (role-level) | Fine (attribute-level) |
| Context | Static | Dynamic |
| Use case | Corporate apps | Healthcare, finance, multi-tenant |
| Audit | Easy | Harder |

**Hybrid approach:** Start with RBAC, add ABAC for specific requirements.

## Otvet (RU)

**RBAC (Role-Based Access Control)**

Доступ предоставляется на основе **роли** пользователя в организации.

```
User -> Role -> Permissions

Пример:
  user: alice -> role: editor -> permissions: [read, write, publish]
```

**Реализация:**
```python
# Проверка роли
if user.role == "admin":
    allow_action()

# Проверка разрешения через роль
if "delete" in user.role.permissions:
    allow_delete()
```

**Плюсы:** Простота, лёгкость аудита, подходит для статических иерархий
**Минусы:** Взрывной рост ролей в сложных системах, нет учёта контекста

---

**ABAC (Attribute-Based Access Control)**

Доступ предоставляется на основе **атрибутов** пользователя, ресурса, действия и окружения.

```
Policy: "Разрешить если user.department == resource.department
         И время рабочее"
```

**Реализация:**
```python
# Policy engine оценивает атрибуты
policy_decision = evaluate_policy(
    subject={"role": "doctor", "department": "cardiology"},
    resource={"type": "patient_record", "department": "cardiology"},
    action="read",
    environment={"time": "14:00", "location": "hospital"}
)
```

**Плюсы:** Детальный контроль, учёт контекста, масштабируется для сложных требований
**Минусы:** Сложность реализации, труднее аудит, накладные расходы на производительность

---

**Сравнение:**

| Аспект | RBAC | ABAC |
|--------|------|------|
| Сложность | Простая | Высокая |
| Детализация | Грубая (на уровне роли) | Тонкая (на уровне атрибутов) |
| Контекст | Статический | Динамический |
| Применение | Корпоративные приложения | Медицина, финансы, multi-tenant |
| Аудит | Простой | Сложнее |

**Гибридный подход:** Начните с RBAC, добавьте ABAC для специфических требований.

---

## Follow-ups
- What is ReBAC (Relationship-Based Access Control)?
- How to implement RBAC in a microservices architecture?
- What is the Open Policy Agent (OPA)?

## Dopolnitelnye voprosy (RU)
- Что такое ReBAC (Relationship-Based Access Control)?
- Как реализовать RBAC в микросервисной архитектуре?
- Что такое Open Policy Agent (OPA)?

## References
- [[c-authorization]]
- [[c-access-control]]
- [[moc-backend]]
