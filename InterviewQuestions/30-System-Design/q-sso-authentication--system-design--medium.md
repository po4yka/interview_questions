---
id: q-sso-authentication
title: Single Sign-On (SSO) Authentication
aliases:
- SSO
- Single Sign-On
- Federated Authentication
topic: system-design
subtopics:
- authentication
- security
- distributed-systems
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
- difficulty/medium
- security
- system-design
anki_cards:
- slug: q-sso-authentication-0-en
  anki_id: null
  synced_at: null
- slug: q-sso-authentication-0-ru
  anki_id: null
  synced_at: null
---
# Question (EN)
> How does Single Sign-On (SSO) work, and what are the main protocols used?

# Vopros (RU)
> Как работает Single Sign-On (SSO) и какие основные протоколы используются?

---

## Answer (EN)

**Single Sign-On (SSO)** is an authentication scheme that allows users to access multiple applications with one set of credentials. Login once, access everything.

### Core Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User (Browser) │     │ Identity        │     │ Service         │
│                 │     │ Provider (IdP)  │     │ Provider (SP)   │
│  - Credentials  │     │ - Auth server   │     │ - Your app      │
│  - Session      │     │ - User store    │     │ - Trusts IdP    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Identity Provider (IdP):** Authenticates users (Google, Okta, Auth0, Azure AD)
**Service Provider (SP):** Your application that trusts the IdP

### SSO Flow (Simplified)

```
1. User visits App A (SP)
   │
2. App A redirects to IdP
   │
3. User authenticates with IdP (if not already)
   │
4. IdP issues token/assertion
   │
5. User redirected back to App A with token
   │
6. App A validates token → User logged in
   │
7. User visits App B → Already authenticated via IdP
   │
8. App B gets token → User logged in (no password needed)
```

### Main Protocols

| Protocol | Use Case | Token Format |
|----------|----------|--------------|
| **SAML 2.0** | Enterprise SSO | XML assertions |
| **OAuth 2.0** | Authorization (API access) | Access tokens |
| **OpenID Connect** | Authentication + OAuth | JWT (ID token) |

### SAML 2.0 Flow

```
User → SP: Access resource
SP → User: Redirect to IdP (SAML Request)
User → IdP: Present credentials
IdP → User: SAML Response (signed XML assertion)
User → SP: POST assertion
SP: Validate signature → Create session
```

**Best for:** Enterprise applications, legacy systems

### OpenID Connect (OIDC) Flow

```
User → App: Login
App → IdP: Authorization request
IdP → User: Login page
User → IdP: Credentials
IdP → App: Authorization code
App → IdP: Exchange code for tokens
IdP → App: ID token + Access token (JWT)
App: Validate JWT → Create session
```

**Best for:** Modern web/mobile apps, consumer applications

### Session Management

**IdP Session:** Central session at identity provider
**SP Sessions:** Local sessions at each application

```
IdP Session (active)
    ├── SP1 Session (active)
    ├── SP2 Session (active)
    └── SP3 Session (expired → re-validate with IdP)
```

### Security Considerations

| Concern | Mitigation |
|---------|------------|
| Token theft | Short expiration (15 min), HTTPS only |
| Session hijacking | Secure cookies, token binding |
| Single point of failure | IdP high availability |
| Logout propagation | Single Logout (SLO) protocol |
| Token replay | Nonce, timestamp validation |

### Token Revocation

```python
# Check token validity
def validate_token(token):
    # 1. Check signature
    # 2. Check expiration
    # 3. Check revocation list (optional)
    # 4. Verify issuer and audience
    pass
```

### Real-World Examples

| Provider | Protocol | Use Case |
|----------|----------|----------|
| Google Workspace | SAML/OIDC | Enterprise apps |
| Okta | SAML/OIDC | Identity management |
| Auth0 | OIDC | Developer-friendly |
| Azure AD | SAML/OIDC | Microsoft ecosystem |
| Keycloak | SAML/OIDC | Self-hosted (open source) |

### Interview Tips

1. Explain IdP vs SP distinction clearly
2. Know the difference: SAML (enterprise) vs OIDC (modern)
3. Discuss security: token expiration, revocation, HTTPS
4. Mention trade-offs: convenience vs single point of failure

---

## Otvet (RU)

**Single Sign-On (SSO)** - схема аутентификации, позволяющая пользователям получить доступ к нескольким приложениям с одним набором учетных данных. Один вход - доступ ко всему.

### Основные компоненты

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Пользователь   │     │ Провайдер       │     │ Провайдер       │
│  (Браузер)      │     │ идентификации   │     │ сервиса (SP)    │
│                 │     │ (IdP)           │     │                 │
│  - Учетные      │     │ - Сервер        │     │ - Ваше          │
│    данные       │     │   аутентиф.     │     │   приложение    │
│  - Сессия       │     │ - Хранилище     │     │ - Доверяет IdP  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Identity Provider (IdP):** Аутентифицирует пользователей (Google, Okta, Auth0, Azure AD)
**Service Provider (SP):** Ваше приложение, которое доверяет IdP

### Поток SSO (упрощенно)

```
1. Пользователь заходит в Приложение A (SP)
   │
2. Приложение A перенаправляет на IdP
   │
3. Пользователь аутентифицируется в IdP (если еще не вошел)
   │
4. IdP выдает токен/assertion
   │
5. Пользователь перенаправлен обратно в Приложение A с токеном
   │
6. Приложение A проверяет токен → Пользователь авторизован
   │
7. Пользователь заходит в Приложение B → Уже аутентифицирован через IdP
   │
8. Приложение B получает токен → Вход без пароля
```

### Основные протоколы

| Протокол | Применение | Формат токена |
|----------|------------|---------------|
| **SAML 2.0** | Корпоративный SSO | XML assertions |
| **OAuth 2.0** | Авторизация (доступ к API) | Access tokens |
| **OpenID Connect** | Аутентификация + OAuth | JWT (ID token) |

### Поток SAML 2.0

```
Пользователь → SP: Запрос ресурса
SP → Пользователь: Редирект на IdP (SAML Request)
Пользователь → IdP: Ввод учетных данных
IdP → Пользователь: SAML Response (подписанный XML assertion)
Пользователь → SP: POST assertion
SP: Проверка подписи → Создание сессии
```

**Лучше для:** Корпоративные приложения, legacy-системы

### Поток OpenID Connect (OIDC)

```
Пользователь → Приложение: Вход
Приложение → IdP: Запрос авторизации
IdP → Пользователь: Страница входа
Пользователь → IdP: Учетные данные
IdP → Приложение: Authorization code
Приложение → IdP: Обмен кода на токены
IdP → Приложение: ID token + Access token (JWT)
Приложение: Проверка JWT → Создание сессии
```

**Лучше для:** Современные веб/мобильные приложения, потребительские сервисы

### Управление сессиями

**Сессия IdP:** Центральная сессия у провайдера идентификации
**Сессии SP:** Локальные сессии в каждом приложении

```
Сессия IdP (активна)
    ├── Сессия SP1 (активна)
    ├── Сессия SP2 (активна)
    └── Сессия SP3 (истекла → повторная проверка через IdP)
```

### Вопросы безопасности

| Проблема | Решение |
|----------|---------|
| Кража токена | Короткий срок действия (15 мин), только HTTPS |
| Перехват сессии | Secure cookies, привязка токена |
| Единая точка отказа | Высокая доступность IdP |
| Распространение выхода | Протокол Single Logout (SLO) |
| Повторное использование токена | Nonce, проверка timestamp |

### Отзыв токенов

```python
# Проверка валидности токена
def validate_token(token):
    # 1. Проверить подпись
    # 2. Проверить срок действия
    # 3. Проверить список отзыва (опционально)
    # 4. Проверить издателя и аудиторию
    pass
```

### Примеры из практики

| Провайдер | Протокол | Применение |
|-----------|----------|------------|
| Google Workspace | SAML/OIDC | Корпоративные приложения |
| Okta | SAML/OIDC | Управление идентификацией |
| Auth0 | OIDC | Удобен для разработчиков |
| Azure AD | SAML/OIDC | Экосистема Microsoft |
| Keycloak | SAML/OIDC | Self-hosted (open source) |

### Советы для собеседования

1. Четко объясните различие IdP и SP
2. Знайте разницу: SAML (корпоративный) vs OIDC (современный)
3. Обсудите безопасность: срок действия токенов, отзыв, HTTPS
4. Упомяните компромиссы: удобство vs единая точка отказа

---

## Follow-ups

- How do you implement Single Logout (SLO)?
- What is the difference between SAML and OIDC?
- How do you handle token refresh in SSO?
- What happens when the IdP goes down?

## Related Questions

### Prerequisites (Easier)
- [[q-api-gateway-patterns--system-design--medium]] - API Gateway basics

### Related (Same Level)
- [[q-dns-resolution--system-design--medium]] - Network fundamentals
- [[q-websockets-sse-long-polling--system-design--medium]] - Real-time communication

### Advanced (Harder)
- [[q-design-notification-system--system-design--hard]] - Complex system design
