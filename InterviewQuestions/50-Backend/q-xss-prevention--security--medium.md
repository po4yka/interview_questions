---
id: be-sec-008
title: XSS Prevention / Предотвращение XSS
aliases: []
topic: security
subtopics:
- xss
- injection
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
- c-xss
created: 2025-01-23
updated: 2025-01-23
tags:
- security
- xss
- injection
- difficulty/medium
- topic/security
anki_cards:
- slug: be-sec-008-0-en
  language: en
  anki_id: 1769167239881
  synced_at: '2026-01-23T15:20:42.948337'
- slug: be-sec-008-0-ru
  language: ru
  anki_id: 1769167239906
  synced_at: '2026-01-23T15:20:42.950514'
---
# Question (EN)
> What are the types of XSS attacks and how to prevent them?

# Vopros (RU)
> Какие существуют типы XSS-атак и как их предотвратить?

---

## Answer (EN)

**XSS (Cross-Site Scripting)** - Attacker injects malicious scripts into web pages viewed by other users.

**Types of XSS:**

**1. Stored XSS (Persistent)**
- Malicious script saved in database
- Executes when other users view the content
- Example: Comment with `<script>` tag

**2. Reflected XSS**
- Script in URL parameter reflected back in response
- Requires victim to click malicious link
- Example: `search?q=<script>alert(1)</script>`

**3. DOM-based XSS**
- Vulnerability in client-side JavaScript
- Never reaches server
- Example: `document.write(location.hash)`

---

**Prevention Techniques:**

**1. Output Encoding (Primary Defense)**
```python
# HTML context
from html import escape
safe_html = escape(user_input)  # < becomes &lt;

# JavaScript context
import json
safe_js = json.dumps(user_input)

# URL context
from urllib.parse import quote
safe_url = quote(user_input)
```

**2. Content Security Policy (CSP)**
```http
Content-Security-Policy: default-src 'self'; script-src 'self'
```
Prevents inline scripts and limits script sources.

**3. Input Validation**
```python
# Sanitize HTML (if HTML is allowed)
import bleach
clean = bleach.clean(user_input, tags=['b', 'i', 'u'])
```

**4. HTTP-Only Cookies**
```http
Set-Cookie: session=abc; HttpOnly; Secure
```
Prevents JavaScript from accessing session cookies.

**5. Framework Auto-Escaping**
```html
<!-- Django -->
{{ user_input }}  <!-- Auto-escaped -->
{{ user_input|safe }}  <!-- DANGEROUS - not escaped -->
```

**Context-Specific Encoding:**
| Context | Encoding |
|---------|----------|
| HTML body | HTML entity encode |
| HTML attribute | Attribute encode |
| JavaScript | JavaScript encode |
| URL | URL encode |
| CSS | CSS encode |

## Otvet (RU)

**XSS (Cross-Site Scripting)** - Атакующий внедряет вредоносные скрипты на веб-страницы, просматриваемые другими пользователями.

**Типы XSS:**

**1. Хранимый XSS (Stored/Persistent)**
- Вредоносный скрипт сохраняется в базе данных
- Выполняется когда другие пользователи просматривают контент
- Пример: Комментарий с тегом `<script>`

**2. Отражённый XSS (Reflected)**
- Скрипт в URL-параметре отражается обратно в ответе
- Требует от жертвы перехода по вредоносной ссылке
- Пример: `search?q=<script>alert(1)</script>`

**3. DOM-based XSS**
- Уязвимость в клиентском JavaScript
- Никогда не достигает сервера
- Пример: `document.write(location.hash)`

---

**Методы предотвращения:**

**1. Кодирование вывода (основная защита)**
```python
# HTML-контекст
from html import escape
safe_html = escape(user_input)  # < становится &lt;

# JavaScript-контекст
import json
safe_js = json.dumps(user_input)

# URL-контекст
from urllib.parse import quote
safe_url = quote(user_input)
```

**2. Content Security Policy (CSP)**
```http
Content-Security-Policy: default-src 'self'; script-src 'self'
```
Запрещает inline-скрипты и ограничивает источники скриптов.

**3. Валидация ввода**
```python
# Санитизация HTML (если HTML разрешён)
import bleach
clean = bleach.clean(user_input, tags=['b', 'i', 'u'])
```

**4. HTTP-Only куки**
```http
Set-Cookie: session=abc; HttpOnly; Secure
```
Запрещает JavaScript доступ к сессионным кукам.

**5. Автоэкранирование фреймворков**
```html
<!-- Django -->
{{ user_input }}  <!-- Автоматически экранируется -->
{{ user_input|safe }}  <!-- ОПАСНО - не экранируется -->
```

**Контекстно-зависимое кодирование:**
| Контекст | Кодирование |
|----------|-------------|
| HTML body | HTML entity encode |
| HTML attribute | Attribute encode |
| JavaScript | JavaScript encode |
| URL | URL encode |
| CSS | CSS encode |

---

## Follow-ups
- How does CSP prevent XSS attacks?
- What is the difference between encoding and sanitization?
- How to test for XSS vulnerabilities?

## Dopolnitelnye voprosy (RU)
- Как CSP предотвращает XSS-атаки?
- В чём разница между кодированием и санитизацией?
- Как тестировать на уязвимости XSS?

## References
- [[c-security]]
- [[c-xss]]
- [[moc-backend]]
