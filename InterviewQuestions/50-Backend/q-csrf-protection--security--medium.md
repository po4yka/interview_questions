---
id: be-sec-009
title: CSRF Protection / Защита от CSRF
aliases: []
topic: security
subtopics:
- csrf
- tokens
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
- c-csrf
created: 2025-01-23
updated: 2025-01-23
tags:
- security
- csrf
- tokens
- difficulty/medium
- topic/security
anki_cards:
- slug: be-sec-009-0-en
  language: en
  anki_id: 1769167242265
  synced_at: '2026-01-23T15:20:43.062275'
- slug: be-sec-009-0-ru
  language: ru
  anki_id: 1769167242284
  synced_at: '2026-01-23T15:20:43.063991'
---
# Question (EN)
> What is CSRF and how to protect against it?

# Vopros (RU)
> Что такое CSRF и как от него защититься?

---

## Answer (EN)

**CSRF (Cross-Site Request Forgery)** - Attack where a malicious site tricks user's browser into making unwanted requests to a site where user is authenticated.

**How Attack Works:**
1. User logs into bank.com (has session cookie)
2. User visits evil.com
3. Evil.com has: `<img src="bank.com/transfer?to=attacker&amount=1000">`
4. Browser sends request with user's session cookie
5. Bank processes transfer as legitimate request

---

**Prevention Techniques:**

**1. CSRF Tokens (Synchronizer Token Pattern)**
```html
<!-- Form includes hidden token -->
<form method="POST" action="/transfer">
    <input type="hidden" name="csrf_token" value="random-secure-token">
    ...
</form>
```

```python
# Server validates token
def transfer():
    if request.form['csrf_token'] != session['csrf_token']:
        abort(403, "CSRF validation failed")
```

**2. SameSite Cookies**
```http
Set-Cookie: session=abc; SameSite=Strict; Secure; HttpOnly
```

| Value | Behavior |
|-------|----------|
| `Strict` | Cookie never sent cross-site |
| `Lax` | Sent for top-level navigation (GET only) |
| `None` | Always sent (requires Secure) |

**3. Double Submit Cookie**
```javascript
// Cookie value also sent in header
fetch('/api/transfer', {
    headers: {
        'X-CSRF-Token': getCookie('csrf_token')
    }
})
```

**4. Origin/Referer Validation**
```python
def check_origin():
    origin = request.headers.get('Origin')
    if origin not in ALLOWED_ORIGINS:
        abort(403)
```

**5. Custom Request Headers**
```javascript
// CORS prevents cross-origin from adding custom headers
fetch('/api/transfer', {
    headers: {
        'X-Requested-With': 'XMLHttpRequest'
    }
})
```

**Best Practice Combination:**
- SameSite=Lax cookies (default protection)
- CSRF tokens for state-changing operations
- Origin validation as additional layer

## Otvet (RU)

**CSRF (Cross-Site Request Forgery)** - Атака, при которой вредоносный сайт заставляет браузер пользователя делать нежелательные запросы к сайту, где пользователь аутентифицирован.

**Как работает атака:**
1. Пользователь логинится на bank.com (получает session cookie)
2. Пользователь посещает evil.com
3. Evil.com содержит: `<img src="bank.com/transfer?to=attacker&amount=1000">`
4. Браузер отправляет запрос с session cookie пользователя
5. Банк обрабатывает перевод как легитимный запрос

---

**Методы защиты:**

**1. CSRF-токены (Synchronizer Token Pattern)**
```html
<!-- Форма включает скрытый токен -->
<form method="POST" action="/transfer">
    <input type="hidden" name="csrf_token" value="random-secure-token">
    ...
</form>
```

```python
# Сервер валидирует токен
def transfer():
    if request.form['csrf_token'] != session['csrf_token']:
        abort(403, "CSRF validation failed")
```

**2. SameSite куки**
```http
Set-Cookie: session=abc; SameSite=Strict; Secure; HttpOnly
```

| Значение | Поведение |
|----------|-----------|
| `Strict` | Cookie никогда не отправляется cross-site |
| `Lax` | Отправляется при навигации верхнего уровня (только GET) |
| `None` | Всегда отправляется (требует Secure) |

**3. Double Submit Cookie**
```javascript
// Значение cookie также отправляется в заголовке
fetch('/api/transfer', {
    headers: {
        'X-CSRF-Token': getCookie('csrf_token')
    }
})
```

**4. Валидация Origin/Referer**
```python
def check_origin():
    origin = request.headers.get('Origin')
    if origin not in ALLOWED_ORIGINS:
        abort(403)
```

**5. Кастомные заголовки запросов**
```javascript
// CORS не позволяет cross-origin добавлять кастомные заголовки
fetch('/api/transfer', {
    headers: {
        'X-Requested-With': 'XMLHttpRequest'
    }
})
```

**Лучшая комбинация:**
- SameSite=Lax куки (защита по умолчанию)
- CSRF-токены для операций, изменяющих состояние
- Валидация Origin как дополнительный слой

---

## Follow-ups
- Why doesn't CSRF work with JSON APIs?
- What is the difference between CSRF and XSS?
- How does SameSite=Lax protect against CSRF?

## Dopolnitelnye voprosy (RU)
- Почему CSRF не работает с JSON API?
- В чём разница между CSRF и XSS?
- Как SameSite=Lax защищает от CSRF?

## References
- [[c-security]]
- [[c-csrf]]
- [[moc-backend]]
