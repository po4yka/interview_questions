---
id: be-sec-002
title: JWT Structure and Validation / Структура и валидация JWT
aliases: []
topic: security
subtopics:
- authentication
- jwt
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
- c-jwt
created: 2025-01-23
updated: 2025-01-23
tags:
- security
- authentication
- jwt
- difficulty/medium
- topic/security
anki_cards:
- slug: be-sec-002-0-en
  language: en
  anki_id: 1769167242680
  synced_at: '2026-01-23T15:20:43.073838'
- slug: be-sec-002-0-ru
  language: ru
  anki_id: 1769167242708
  synced_at: '2026-01-23T15:20:43.075281'
---
# Question (EN)
> What is the structure of a JWT and how should it be validated?

# Vopros (RU)
> Какова структура JWT и как его следует валидировать?

---

## Answer (EN)

**JWT Structure** (three Base64URL-encoded parts separated by dots):

```
header.payload.signature
```

**1. Header** - Algorithm and token type:
```json
{
  "alg": "RS256",
  "typ": "JWT"
}
```

**2. Payload** - Claims (data):
```json
{
  "sub": "user123",
  "iss": "auth.example.com",
  "aud": "api.example.com",
  "exp": 1735689600,
  "iat": 1735686000,
  "roles": ["admin"]
}
```

**3. Signature** - Cryptographic verification:
```
RSASHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), privateKey)
```

**Validation Steps (MUST follow all):**

1. **Verify signature** - Use public key to validate signature
2. **Check `exp`** - Token not expired
3. **Check `iat`** - Issued-at not in future
4. **Check `iss`** - Issuer matches expected value
5. **Check `aud`** - Audience includes your service
6. **Check `nbf`** - Not-before time passed (if present)

**Common Vulnerabilities:**
- `alg: none` attack - Always validate algorithm
- Key confusion - Don't accept HS256 when expecting RS256
- Missing expiration - Always require `exp`

## Otvet (RU)

**Структура JWT** (три части в Base64URL, разделённые точками):

```
header.payload.signature
```

**1. Header** - Алгоритм и тип токена:
```json
{
  "alg": "RS256",
  "typ": "JWT"
}
```

**2. Payload** - Claims (данные):
```json
{
  "sub": "user123",
  "iss": "auth.example.com",
  "aud": "api.example.com",
  "exp": 1735689600,
  "iat": 1735686000,
  "roles": ["admin"]
}
```

**3. Signature** - Криптографическая подпись:
```
RSASHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), privateKey)
```

**Шаги валидации (ОБЯЗАТЕЛЬНО все):**

1. **Проверить подпись** - Использовать публичный ключ
2. **Проверить `exp`** - Токен не истёк
3. **Проверить `iat`** - Время выпуска не в будущем
4. **Проверить `iss`** - Издатель совпадает с ожидаемым
5. **Проверить `aud`** - Аудитория включает ваш сервис
6. **Проверить `nbf`** - Время "не раньше" прошло (если есть)

**Распространённые уязвимости:**
- Атака `alg: none` - Всегда проверять алгоритм
- Путаница ключей - Не принимать HS256, если ожидается RS256
- Отсутствие срока - Всегда требовать `exp`

---

## Follow-ups
- What is the difference between HS256 and RS256?
- How to implement JWT refresh token rotation?
- Where should JWTs be stored on the client side?

## Dopolnitelnye voprosy (RU)
- В чём разница между HS256 и RS256?
- Как реализовать ротацию refresh-токенов JWT?
- Где следует хранить JWT на стороне клиента?

## References
- [[c-authentication]]
- [[c-jwt]]
- [[moc-backend]]
