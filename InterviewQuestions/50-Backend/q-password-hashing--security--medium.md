---
id: be-sec-010
title: Password Hashing / Хеширование паролей
aliases: []
topic: security
subtopics:
- passwords
- hashing
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
- c-passwords
created: 2025-01-23
updated: 2025-01-23
tags:
- security
- passwords
- hashing
- difficulty/medium
- topic/security
anki_cards:
- slug: be-sec-010-0-en
  language: en
  anki_id: 1769167242310
  synced_at: '2026-01-23T15:20:43.065220'
- slug: be-sec-010-0-ru
  language: ru
  anki_id: 1769167242346
  synced_at: '2026-01-23T15:20:43.066553'
---
# Question (EN)
> How should passwords be securely stored and what hashing algorithms are recommended?

# Vopros (RU)
> Как следует безопасно хранить пароли и какие алгоритмы хеширования рекомендуются?

---

## Answer (EN)

**Never store plaintext passwords.** Use password hashing functions with salt.

**Why Not Regular Hash (MD5, SHA-256)?**
- Too fast (can hash billions per second)
- Vulnerable to rainbow tables
- No protection against brute force

---

**Recommended Algorithms (in order of preference):**

**1. Argon2 (Winner of PHC 2015)**
```python
from argon2 import PasswordHasher
ph = PasswordHasher()

# Hash password
hash = ph.hash("user_password")
# $argon2id$v=19$m=65536,t=3,p=4$salt$hash

# Verify
try:
    ph.verify(hash, "user_password")
except VerifyMismatchError:
    print("Invalid password")
```
- Memory-hard (resists GPU attacks)
- Variants: argon2id (recommended), argon2i, argon2d

**2. bcrypt**
```python
import bcrypt

# Hash with auto-generated salt
hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
# $2b$12$salt-here...hash-here

# Verify
bcrypt.checkpw(password.encode(), hash)
```
- Proven track record (since 1999)
- Cost factor (rounds) makes it slow

**3. scrypt**
```python
import hashlib
hash = hashlib.scrypt(
    password.encode(),
    salt=os.urandom(16),
    n=2**14,  # CPU cost
    r=8,      # Memory cost
    p=1       # Parallelization
)
```
- Memory-hard
- Used in cryptocurrency

---

**Key Concepts:**

**Salt** - Random data added to password before hashing
```
hash(password + salt) = unique_hash
```
Prevents rainbow table attacks. Each user has unique salt.

**Work Factor** - Computational cost
```python
# bcrypt: rounds (10-14 typical)
bcrypt.gensalt(rounds=12)  # 2^12 iterations

# argon2: time, memory, parallelism
PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
```
Increase over time as hardware improves.

**Storage Format:**
```
$algorithm$version$params$salt$hash
Example: $2b$12$Qz8qM2x...$hF9Kl3...
```

**Best Practices:**
- Use library defaults (well-tested)
- Hash on server, never client
- Enforce minimum password length (12+)
- Check against breached password lists

## Otvet (RU)

**Никогда не храните пароли открытым текстом.** Используйте функции хеширования паролей с солью.

**Почему не обычный хеш (MD5, SHA-256)?**
- Слишком быстрые (миллиарды хешей в секунду)
- Уязвимы к rainbow-таблицам
- Нет защиты от перебора

---

**Рекомендуемые алгоритмы (в порядке предпочтения):**

**1. Argon2 (Победитель PHC 2015)**
```python
from argon2 import PasswordHasher
ph = PasswordHasher()

# Хеширование пароля
hash = ph.hash("user_password")
# $argon2id$v=19$m=65536,t=3,p=4$salt$hash

# Проверка
try:
    ph.verify(hash, "user_password")
except VerifyMismatchError:
    print("Неверный пароль")
```
- Memory-hard (устойчив к GPU-атакам)
- Варианты: argon2id (рекомендуется), argon2i, argon2d

**2. bcrypt**
```python
import bcrypt

# Хеширование с автогенерируемой солью
hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
# $2b$12$salt-here...hash-here

# Проверка
bcrypt.checkpw(password.encode(), hash)
```
- Проверенный временем (с 1999 года)
- Cost factor (rounds) делает его медленным

**3. scrypt**
```python
import hashlib
hash = hashlib.scrypt(
    password.encode(),
    salt=os.urandom(16),
    n=2**14,  # Нагрузка на CPU
    r=8,      # Нагрузка на память
    p=1       # Параллелизм
)
```
- Memory-hard
- Используется в криптовалютах

---

**Ключевые концепции:**

**Соль (Salt)** - Случайные данные, добавляемые к паролю перед хешированием
```
hash(password + salt) = unique_hash
```
Предотвращает атаки rainbow-таблицами. У каждого пользователя уникальная соль.

**Work Factor** - Вычислительная сложность
```python
# bcrypt: раунды (типично 10-14)
bcrypt.gensalt(rounds=12)  # 2^12 итераций

# argon2: время, память, параллелизм
PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
```
Увеличивайте со временем по мере роста производительности оборудования.

**Формат хранения:**
```
$algorithm$version$params$salt$hash
Пример: $2b$12$Qz8qM2x...$hF9Kl3...
```

**Лучшие практики:**
- Используйте настройки библиотек по умолчанию (хорошо протестированы)
- Хешируйте на сервере, никогда на клиенте
- Требуйте минимальную длину пароля (12+)
- Проверяйте по спискам утекших паролей

---

## Follow-ups
- How to upgrade from MD5/SHA to bcrypt without resetting passwords?
- What is pepper and how is it different from salt?
- How to implement secure password reset flow?

## Dopolnitelnye voprosy (RU)
- Как перейти с MD5/SHA на bcrypt без сброса паролей?
- Что такое pepper и чем он отличается от соли?
- Как реализовать безопасный поток сброса пароля?

## References
- [[c-security]]
- [[c-passwords]]
- [[moc-backend]]
