---
id: be-sec-003
title: Session Management / Управление сессиями
aliases: []
topic: security
subtopics:
- authentication
- sessions
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
- c-authentication
- c-sessions
created: 2025-01-23
updated: 2025-01-23
tags:
- security
- authentication
- sessions
- difficulty/medium
- topic/security
anki_cards:
- slug: be-sec-003-0-en
  language: en
  anki_id: 1769167240506
  synced_at: '2026-01-23T15:20:42.978804'
- slug: be-sec-003-0-ru
  language: ru
  anki_id: 1769167240530
  synced_at: '2026-01-23T15:20:42.981122'
---
# Question (EN)
> What is the difference between stateful sessions and stateless (JWT) authentication?

# Vopros (RU)
> В чём разница между stateful-сессиями и stateless (JWT) аутентификацией?

---

## Answer (EN)

**Stateful Sessions (Server-side)**

How it works:
1. Server creates session, stores in database/Redis
2. Session ID sent to client as cookie
3. Each request: server looks up session by ID

```
Client -> Cookie: session_id=abc123
Server -> Redis.get("session:abc123") -> {userId, roles, ...}
```

**Pros:**
- Instant revocation (delete session)
- Session data stays on server
- Smaller cookie size

**Cons:**
- Requires centralized session store
- Adds latency (DB lookup per request)
- Harder to scale horizontally

---

**Stateless Authentication (JWT)**

How it works:
1. Server issues signed JWT with claims
2. Client stores token (cookie or localStorage)
3. Each request: server validates signature, reads claims

```
Client -> Authorization: Bearer eyJhbG...
Server -> verify(token) -> {userId, roles, exp, ...}
```

**Pros:**
- No server-side storage needed
- Scales horizontally easily
- Works across services (microservices)

**Cons:**
- Can't revoke until expiration
- Token size grows with claims
- Must handle token refresh

---

**Hybrid Approach (Best Practice):**
- Short-lived access tokens (15 min)
- Long-lived refresh tokens (server-stored)
- Revocation via refresh token invalidation

| Aspect | Stateful | Stateless |
|--------|----------|-----------|
| Storage | Server (Redis/DB) | Client |
| Revocation | Instant | On expiry only |
| Scalability | Harder | Easy |
| Microservices | Needs shared store | Works natively |

## Otvet (RU)

**Stateful-сессии (на сервере)**

Как работает:
1. Сервер создаёт сессию, хранит в базе/Redis
2. Session ID отправляется клиенту как cookie
3. Каждый запрос: сервер ищет сессию по ID

```
Client -> Cookie: session_id=abc123
Server -> Redis.get("session:abc123") -> {userId, roles, ...}
```

**Плюсы:**
- Мгновенный отзыв (удаление сессии)
- Данные сессии на сервере
- Маленький размер cookie

**Минусы:**
- Требуется централизованное хранилище
- Добавляет задержку (запрос к БД)
- Сложнее масштабировать горизонтально

---

**Stateless-аутентификация (JWT)**

Как работает:
1. Сервер выдаёт подписанный JWT с claims
2. Клиент хранит токен (cookie или localStorage)
3. Каждый запрос: сервер проверяет подпись, читает claims

```
Client -> Authorization: Bearer eyJhbG...
Server -> verify(token) -> {userId, roles, exp, ...}
```

**Плюсы:**
- Не нужно хранилище на сервере
- Легко масштабируется горизонтально
- Работает между сервисами (микросервисы)

**Минусы:**
- Нельзя отозвать до истечения срока
- Размер токена растёт с claims
- Нужна обработка обновления токена

---

**Гибридный подход (лучшая практика):**
- Краткосрочные access-токены (15 мин)
- Долгосрочные refresh-токены (на сервере)
- Отзыв через инвалидацию refresh-токена

| Аспект | Stateful | Stateless |
|--------|----------|-----------|
| Хранение | Сервер (Redis/БД) | Клиент |
| Отзыв | Мгновенный | Только по истечении |
| Масштабируемость | Сложнее | Легко |
| Микросервисы | Нужно общее хранилище | Работает нативно |

---

## Follow-ups
- How to implement session fixation protection?
- What is the sliding expiration pattern?
- How to handle concurrent sessions per user?

## Dopolnitelnye voprosy (RU)
- Как реализовать защиту от session fixation?
- Что такое паттерн sliding expiration?
- Как обрабатывать одновременные сессии пользователя?

## References
- [[c-authentication]]
- [[c-sessions]]
- [[moc-backend]]
