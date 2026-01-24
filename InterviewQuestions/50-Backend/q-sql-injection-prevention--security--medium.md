---
id: be-sec-007
title: SQL Injection Prevention / Предотвращение SQL-инъекций
aliases: []
topic: security
subtopics:
- injection
- sql
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
- c-security
- c-sql
created: 2025-01-23
updated: 2025-01-23
tags:
- security
- sql-injection
- databases
- difficulty/medium
- topic/security
anki_cards:
- slug: be-sec-007-0-en
  language: en
  anki_id: 1769167240457
  synced_at: '2026-01-23T15:20:42.975279'
- slug: be-sec-007-0-ru
  language: ru
  anki_id: 1769167240480
  synced_at: '2026-01-23T15:20:42.977089'
---
# Question (EN)
> What is SQL injection and how to prevent it?

# Vopros (RU)
> Что такое SQL-инъекция и как её предотвратить?

---

## Answer (EN)

**SQL Injection** - An attack where malicious SQL is inserted into application queries through user input.

**Vulnerable Code:**
```python
# DANGEROUS - string concatenation
query = f"SELECT * FROM users WHERE username = '{username}'"
# Input: admin'--
# Result: SELECT * FROM users WHERE username = 'admin'--'
```

**Attack Types:**

1. **Classic (In-band)** - Results visible in response
2. **Blind** - No direct output, infer from behavior
3. **Time-based** - Use SLEEP() to detect success
4. **Union-based** - Combine results with UNION SELECT

---

**Prevention Techniques:**

**1. Parameterized Queries (Primary Defense)**
```python
# Python with psycopg2
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (username,)  # Parameter, not concatenation
)

# Java with PreparedStatement
PreparedStatement stmt = conn.prepareStatement(
    "SELECT * FROM users WHERE username = ?"
);
stmt.setString(1, username);
```

**2. ORM/Query Builders**
```python
# SQLAlchemy
User.query.filter(User.username == username).first()
```

**3. Input Validation**
```python
# Allowlist approach
if not username.isalnum():
    raise ValidationError("Invalid username")
```

**4. Escaping (Last Resort)**
```python
# Only when parameterization not possible
escaped = conn.escape_string(user_input)
```

**5. Least Privilege**
- Database user with minimal permissions
- Separate read/write accounts

**Defense-in-Depth:**
- Web Application Firewall (WAF)
- Error handling (don't expose SQL errors)
- Regular security testing

## Otvet (RU)

**SQL-инъекция** - Атака, при которой вредоносный SQL внедряется в запросы приложения через пользовательский ввод.

**Уязвимый код:**
```python
# ОПАСНО - конкатенация строк
query = f"SELECT * FROM users WHERE username = '{username}'"
# Ввод: admin'--
# Результат: SELECT * FROM users WHERE username = 'admin'--'
```

**Типы атак:**

1. **Классическая (In-band)** - Результаты видны в ответе
2. **Слепая (Blind)** - Нет прямого вывода, вывод по поведению
3. **Time-based** - Используется SLEEP() для определения успеха
4. **Union-based** - Объединение результатов через UNION SELECT

---

**Методы предотвращения:**

**1. Параметризованные запросы (основная защита)**
```python
# Python с psycopg2
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (username,)  # Параметр, не конкатенация
)

# Java с PreparedStatement
PreparedStatement stmt = conn.prepareStatement(
    "SELECT * FROM users WHERE username = ?"
);
stmt.setString(1, username);
```

**2. ORM/Query Builders**
```python
# SQLAlchemy
User.query.filter(User.username == username).first()
```

**3. Валидация ввода**
```python
# Подход allowlist
if not username.isalnum():
    raise ValidationError("Invalid username")
```

**4. Экранирование (крайняя мера)**
```python
# Только когда параметризация невозможна
escaped = conn.escape_string(user_input)
```

**5. Минимальные привилегии**
- Пользователь БД с минимальными правами
- Отдельные аккаунты для чтения/записи

**Эшелонированная защита:**
- Web Application Firewall (WAF)
- Обработка ошибок (не показывать SQL-ошибки)
- Регулярное тестирование безопасности

---

## Follow-ups
- How does prepared statement prevent SQL injection?
- What is second-order SQL injection?
- How to test for SQL injection vulnerabilities?

## Dopolnitelnye voprosy (RU)
- Как prepared statement предотвращает SQL-инъекцию?
- Что такое SQL-инъекция второго порядка?
- Как тестировать на уязвимости SQL-инъекции?

## References
- [[c-security]]
- [[c-sql]]
- [[moc-backend]]
