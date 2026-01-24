---
id: be-sec-004
title: CORS and Preflight Requests / CORS и предварительные запросы
aliases: []
topic: security
subtopics:
- cors
- http
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
- c-cors
- c-http
created: 2025-01-23
updated: 2025-01-23
tags:
- security
- cors
- http
- difficulty/medium
- topic/security
anki_cards:
- slug: be-sec-004-0-en
  language: en
  anki_id: 1769167241382
  synced_at: '2026-01-23T15:20:43.014905'
- slug: be-sec-004-0-ru
  language: ru
  anki_id: 1769167241406
  synced_at: '2026-01-23T15:20:43.016807'
---
# Question (EN)
> What is CORS and when does the browser send a preflight request?

# Vopros (RU)
> Что такое CORS и когда браузер отправляет предварительный запрос?

---

## Answer (EN)

**CORS (Cross-Origin Resource Sharing)** is a browser security mechanism that restricts web pages from making requests to a different origin (domain, protocol, or port) than the one that served the page.

**Same Origin:**
```
https://example.com/page -> https://example.com/api  (allowed)
```

**Cross Origin:**
```
https://app.com -> https://api.example.com  (blocked by default)
```

---

**Preflight Request** - Browser sends OPTIONS request before the actual request to check if CORS is allowed.

**Preflight is triggered when:**
- HTTP method is not GET, HEAD, or POST
- Custom headers are used (e.g., `Authorization`, `X-Custom-Header`)
- POST with Content-Type other than:
  - `application/x-www-form-urlencoded`
  - `multipart/form-data`
  - `text/plain`

**Preflight Request/Response:**
```http
OPTIONS /api/data HTTP/1.1
Origin: https://app.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Authorization, Content-Type

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.com
Access-Control-Allow-Methods: GET, POST, PUT
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400
```

**Key Response Headers:**
| Header | Purpose |
|--------|---------|
| `Access-Control-Allow-Origin` | Allowed origins (`*` or specific) |
| `Access-Control-Allow-Credentials` | Allow cookies (can't use with `*`) |
| `Access-Control-Allow-Methods` | Allowed HTTP methods |
| `Access-Control-Allow-Headers` | Allowed custom headers |
| `Access-Control-Max-Age` | Cache preflight (seconds) |

## Otvet (RU)

**CORS (Cross-Origin Resource Sharing)** - механизм безопасности браузера, который ограничивает веб-страницы в выполнении запросов к другому origin (домен, протокол или порт), отличному от того, который обслужил страницу.

**Same Origin:**
```
https://example.com/page -> https://example.com/api  (разрешено)
```

**Cross Origin:**
```
https://app.com -> https://api.example.com  (заблокировано по умолчанию)
```

---

**Preflight-запрос** - Браузер отправляет OPTIONS-запрос перед основным, чтобы проверить, разрешён ли CORS.

**Preflight срабатывает когда:**
- HTTP-метод не GET, HEAD или POST
- Используются кастомные заголовки (`Authorization`, `X-Custom-Header`)
- POST с Content-Type, отличным от:
  - `application/x-www-form-urlencoded`
  - `multipart/form-data`
  - `text/plain`

**Preflight запрос/ответ:**
```http
OPTIONS /api/data HTTP/1.1
Origin: https://app.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Authorization, Content-Type

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.com
Access-Control-Allow-Methods: GET, POST, PUT
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400
```

**Ключевые заголовки ответа:**
| Заголовок | Назначение |
|-----------|------------|
| `Access-Control-Allow-Origin` | Разрешённые origins (`*` или конкретный) |
| `Access-Control-Allow-Credentials` | Разрешить cookies (нельзя с `*`) |
| `Access-Control-Allow-Methods` | Разрешённые HTTP-методы |
| `Access-Control-Allow-Headers` | Разрешённые кастомные заголовки |
| `Access-Control-Max-Age` | Кэш preflight (секунды) |

---

## Follow-ups
- Why can't you use `Access-Control-Allow-Origin: *` with credentials?
- How to debug CORS errors?
- What is the difference between simple and preflighted requests?

## Dopolnitelnye voprosy (RU)
- Почему нельзя использовать `Access-Control-Allow-Origin: *` с credentials?
- Как отлаживать ошибки CORS?
- В чём разница между простыми и preflighted-запросами?

## References
- [[c-cors]]
- [[c-http]]
- [[moc-backend]]
