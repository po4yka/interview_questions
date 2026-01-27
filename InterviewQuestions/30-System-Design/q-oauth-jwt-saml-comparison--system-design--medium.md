---
id: q-oauth-jwt-saml-comparison
title: OAuth vs JWT vs SAML Comparison
aliases:
- OAuth 2.0
- JWT Tokens
- SAML Authentication
- SSO Protocols
topic: system-design
subtopics:
- authentication
- authorization
- security
- protocols
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-api-gateway-patterns--system-design--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- authentication
- security
- difficulty/medium
- system-design
anki_cards:
- slug: q-oauth-jwt-saml-comparison-0-en
  anki_id: null
  synced_at: null
- slug: q-oauth-jwt-saml-comparison-0-ru
  anki_id: null
  synced_at: null
---
# Question (EN)
> What are the differences between OAuth, JWT, and SAML? When should you use each?

# Vopros (RU)
> В чём разница между OAuth, JWT и SAML? Когда следует использовать каждый из них?

---

## Answer (EN)

These three technologies serve different purposes in authentication and authorization:

| Aspect | OAuth 2.0 | JWT | SAML |
|--------|-----------|-----|------|
| **Type** | Authorization framework | Token format | Authentication protocol |
| **Format** | N/A (protocol) | JSON (Base64) | XML |
| **Primary Use** | Delegated authorization | Stateless auth tokens | Enterprise SSO |
| **Token Size** | Varies | Compact (~500 bytes) | Large (XML verbose) |
| **Best For** | APIs, mobile apps | Microservices, SPAs | Enterprise, legacy systems |

### OAuth 2.0

**OAuth 2.0** is an authorization framework that allows third-party applications to access user resources without exposing credentials.

```
User → Client App → Authorization Server → Resource Server
         │                  │
         │    1. Redirect   │
         ├─────────────────→│
         │    2. Login      │
         │←─────────────────┤
         │    3. Auth Code  │
         │←─────────────────┤
         │    4. Exchange   │
         ├─────────────────→│
         │    5. Token      │
         │←─────────────────┤
```

**Key Flows:**

| Flow | Use Case |
|------|----------|
| Authorization Code | Web apps with backend |
| Authorization Code + PKCE | Mobile/SPA (no client secret) |
| Client Credentials | Service-to-service |
| Implicit (deprecated) | Legacy SPAs |

**Example: Authorization Code Flow**

```
1. GET /authorize?response_type=code&client_id=app&redirect_uri=...
2. User logs in, consents
3. Redirect to: callback?code=AUTH_CODE
4. POST /token (exchange code for access token)
5. Use access token to call APIs
```

### JWT (JSON Web Token)

**JWT** is a token format (not a protocol). It's a compact, self-contained way to transmit information.

**Structure:** `header.payload.signature`

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4ifQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Decoded:**
```json
// Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// Payload
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022,
  "exp": 1516242622
}

// Signature
HMACSHA256(base64(header) + "." + base64(payload), secret)
```

**Key Properties:**

- **Stateless:** No server-side session needed
- **Self-contained:** Contains all user claims
- **Verifiable:** Signature ensures integrity

**Common Claims:**

| Claim | Purpose |
|-------|---------|
| `sub` | Subject (user ID) |
| `iat` | Issued at |
| `exp` | Expiration time |
| `iss` | Issuer |
| `aud` | Audience |

### SAML (Security Assertion Markup Language)

**SAML** is an XML-based protocol for enterprise Single Sign-On (SSO).

**Actors:**
- **IdP (Identity Provider):** Authenticates users (e.g., Okta, ADFS)
- **SP (Service Provider):** Application requesting authentication

```
User → SP → IdP → SP
 │      │    │    │
 │  1. Access resource
 ├──────→    │    │
 │  2. SAML Request (redirect to IdP)
 │      ├────→    │
 │  3. User authenticates
 │      │    │    │
 │  4. SAML Response (assertion)
 │      │←───┤    │
 │  5. Validate, create session
 │      │    │────→
```

**SAML Assertion Example:**
```xml
<saml:Assertion>
  <saml:Issuer>https://idp.example.com</saml:Issuer>
  <saml:Subject>
    <saml:NameID>user@example.com</saml:NameID>
  </saml:Subject>
  <saml:Conditions NotBefore="..." NotOnOrAfter="..."/>
  <saml:AttributeStatement>
    <saml:Attribute Name="role">
      <saml:AttributeValue>admin</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

### When to Use Each

| Scenario | Recommendation |
|----------|----------------|
| Mobile app accessing API | OAuth 2.0 + PKCE |
| Microservices communication | JWT (or OAuth + JWT) |
| Enterprise SSO with legacy systems | SAML |
| Modern web SSO | OAuth 2.0 / OIDC |
| Third-party API access | OAuth 2.0 |
| Stateless API authentication | JWT |

### OAuth 2.0 + JWT Combination

Modern systems often combine OAuth 2.0 with JWT:

```
Client → Auth Server → API (Resource Server)
           │
           │ Issues JWT as access token
           ↓
  Access Token = JWT containing claims
           │
           ↓
  API validates JWT signature (stateless)
```

### Security Considerations

| Technology | Concern | Mitigation |
|------------|---------|------------|
| OAuth 2.0 | Token theft | Short expiry, refresh tokens, HTTPS |
| JWT | No revocation | Short expiry, token blacklist, refresh tokens |
| JWT | Payload visible | Don't store secrets, use encryption (JWE) |
| SAML | XML vulnerabilities | Signature validation, secure parsing |
| All | Man-in-the-middle | Always use HTTPS |

### Common Interview Questions

1. **Can JWT be revoked?** Not directly (stateless). Use short expiry + refresh tokens or maintain a blacklist.

2. **OAuth vs OpenID Connect?** OIDC adds authentication layer on top of OAuth 2.0, returns ID token (JWT).

3. **Why not use JWT for sessions?** Can't invalidate on logout; consider server-side sessions for sensitive apps.

---

## Otvet (RU)

Эти три технологии служат разным целям в аутентификации и авторизации:

| Аспект | OAuth 2.0 | JWT | SAML |
|--------|-----------|-----|------|
| **Тип** | Фреймворк авторизации | Формат токена | Протокол аутентификации |
| **Формат** | Н/Д (протокол) | JSON (Base64) | XML |
| **Основное применение** | Делегированная авторизация | Stateless токены | Enterprise SSO |
| **Размер токена** | Варьируется | Компактный (~500 байт) | Большой (XML многословен) |
| **Лучше всего для** | API, мобильные приложения | Микросервисы, SPA | Enterprise, legacy системы |

### OAuth 2.0

**OAuth 2.0** - фреймворк авторизации, позволяющий сторонним приложениям получать доступ к ресурсам пользователя без раскрытия учётных данных.

```
Пользователь → Клиент → Сервер авторизации → Сервер ресурсов
                  │              │
                  │  1. Редирект │
                  ├─────────────→│
                  │  2. Логин    │
                  │←─────────────┤
                  │  3. Код      │
                  │←─────────────┤
                  │  4. Обмен    │
                  ├─────────────→│
                  │  5. Токен    │
                  │←─────────────┤
```

**Основные потоки:**

| Поток | Применение |
|-------|------------|
| Authorization Code | Веб-приложения с бэкендом |
| Authorization Code + PKCE | Мобильные/SPA (без client secret) |
| Client Credentials | Сервис-к-сервису |
| Implicit (устарел) | Legacy SPA |

**Пример: Authorization Code Flow**

```
1. GET /authorize?response_type=code&client_id=app&redirect_uri=...
2. Пользователь логинится, даёт согласие
3. Редирект на: callback?code=AUTH_CODE
4. POST /token (обмен кода на access token)
5. Использование access token для вызова API
```

### JWT (JSON Web Token)

**JWT** - это формат токена (не протокол). Компактный, самодостаточный способ передачи информации.

**Структура:** `заголовок.полезная_нагрузка.подпись`

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4ifQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Декодированный:**
```json
// Заголовок
{
  "alg": "HS256",
  "typ": "JWT"
}

// Полезная нагрузка
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022,
  "exp": 1516242622
}

// Подпись
HMACSHA256(base64(header) + "." + base64(payload), secret)
```

**Ключевые свойства:**

- **Stateless:** Не требуется серверная сессия
- **Самодостаточный:** Содержит все claims пользователя
- **Верифицируемый:** Подпись гарантирует целостность

**Распространённые claims:**

| Claim | Назначение |
|-------|------------|
| `sub` | Субъект (ID пользователя) |
| `iat` | Время выпуска |
| `exp` | Время истечения |
| `iss` | Издатель |
| `aud` | Аудитория |

### SAML (Security Assertion Markup Language)

**SAML** - XML-протокол для корпоративного Single Sign-On (SSO).

**Участники:**
- **IdP (Identity Provider):** Аутентифицирует пользователей (например, Okta, ADFS)
- **SP (Service Provider):** Приложение, запрашивающее аутентификацию

```
Пользователь → SP → IdP → SP
      │         │    │    │
      │  1. Запрос доступа
      ├─────────→    │    │
      │  2. SAML Request (редирект на IdP)
      │         ├────→    │
      │  3. Пользователь аутентифицируется
      │         │    │    │
      │  4. SAML Response (assertion)
      │         │←───┤    │
      │  5. Валидация, создание сессии
      │         │    │────→
```

**Пример SAML Assertion:**
```xml
<saml:Assertion>
  <saml:Issuer>https://idp.example.com</saml:Issuer>
  <saml:Subject>
    <saml:NameID>user@example.com</saml:NameID>
  </saml:Subject>
  <saml:Conditions NotBefore="..." NotOnOrAfter="..."/>
  <saml:AttributeStatement>
    <saml:Attribute Name="role">
      <saml:AttributeValue>admin</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

### Когда использовать каждый

| Сценарий | Рекомендация |
|----------|--------------|
| Мобильное приложение с API | OAuth 2.0 + PKCE |
| Коммуникация микросервисов | JWT (или OAuth + JWT) |
| Enterprise SSO с legacy системами | SAML |
| Современный веб SSO | OAuth 2.0 / OIDC |
| Доступ к сторонним API | OAuth 2.0 |
| Stateless аутентификация API | JWT |

### Комбинация OAuth 2.0 + JWT

Современные системы часто комбинируют OAuth 2.0 с JWT:

```
Клиент → Сервер авторизации → API (Сервер ресурсов)
              │
              │ Выпускает JWT как access token
              ↓
  Access Token = JWT с claims
              │
              ↓
  API валидирует подпись JWT (stateless)
```

### Соображения безопасности

| Технология | Проблема | Решение |
|------------|----------|---------|
| OAuth 2.0 | Кража токена | Короткий срок, refresh tokens, HTTPS |
| JWT | Нет отзыва | Короткий срок, blacklist токенов, refresh tokens |
| JWT | Payload виден | Не хранить секреты, использовать шифрование (JWE) |
| SAML | XML уязвимости | Валидация подписи, безопасный парсинг |
| Все | Man-in-the-middle | Всегда использовать HTTPS |

### Частые вопросы на интервью

1. **Можно ли отозвать JWT?** Напрямую нет (stateless). Используйте короткий срок + refresh tokens или ведите blacklist.

2. **OAuth vs OpenID Connect?** OIDC добавляет слой аутентификации поверх OAuth 2.0, возвращает ID token (JWT).

3. **Почему не использовать JWT для сессий?** Нельзя инвалидировать при logout; для чувствительных приложений лучше серверные сессии.

---

## Follow-ups

- What is OpenID Connect (OIDC) and how does it relate to OAuth 2.0?
- How do you implement token refresh securely?
- What are the security implications of storing JWTs in localStorage vs cookies?
- How does PKCE protect against authorization code interception?

## Related Questions

### Prerequisites (Easier)
- [[q-api-gateway-patterns--system-design--medium]] - API Gateway handles auth

### Related (Same Level)
- [[q-grpc-vs-rest--system-design--medium]] - API protocols
- [[q-microservices-vs-monolith--system-design--hard]] - Where auth fits

### Advanced (Harder)
- [[q-design-rate-limiter--system-design--hard]] - Auth rate limiting
