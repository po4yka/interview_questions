---
id: be-sec-001
title: OAuth 2.0 Flows / Потоки OAuth 2.0
aliases: []
topic: security
subtopics:
- authentication
- oauth
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
- c-oauth
created: 2025-01-23
updated: 2025-01-23
tags:
- security
- authentication
- oauth
- difficulty/medium
- topic/security
anki_cards:
- slug: be-sec-001-0-en
  language: en
  anki_id: 1769167240908
  synced_at: '2026-01-23T15:20:42.999492'
- slug: be-sec-001-0-ru
  language: ru
  anki_id: 1769167240933
  synced_at: '2026-01-23T15:20:43.001158'
---
# Question (EN)
> What are the main OAuth 2.0 flows and when should each be used?

# Vopros (RU)
> Какие существуют основные потоки OAuth 2.0 и когда следует использовать каждый из них?

---

## Answer (EN)

OAuth 2.0 defines four main authorization flows (grants):

**1. Authorization Code Flow**
- **Use for**: Server-side web applications
- **How it works**: User redirects to auth server, receives authorization code, server exchanges code for tokens
- **Why secure**: Tokens never exposed to browser, code is short-lived

**2. Authorization Code Flow with PKCE**
- **Use for**: Mobile apps, SPAs, public clients
- **How it works**: Same as above but adds code_verifier/code_challenge to prevent interception attacks
- **Why needed**: Public clients can't keep client_secret secure

**3. Client Credentials Flow**
- **Use for**: Machine-to-machine (M2M) communication
- **How it works**: Service authenticates directly with client_id and client_secret
- **No user involved**: Used for backend services calling APIs

**4. Implicit Flow (Deprecated)**
- **Was used for**: Browser-based apps
- **Why deprecated**: Tokens exposed in URL fragment, no refresh tokens
- **Replace with**: Authorization Code + PKCE

**Flow Selection Matrix:**

| Client Type | Flow |
|-------------|------|
| Server-side web app | Authorization Code |
| SPA / Mobile app | Authorization Code + PKCE |
| Backend service | Client Credentials |
| IoT / Limited input | Device Authorization |

## Otvet (RU)

OAuth 2.0 определяет четыре основных потока авторизации (grants):

**1. Authorization Code Flow**
- **Для**: Серверные веб-приложения
- **Как работает**: Пользователь перенаправляется на сервер авторизации, получает код авторизации, сервер обменивает код на токены
- **Почему безопасно**: Токены не попадают в браузер, код краткосрочный

**2. Authorization Code Flow с PKCE**
- **Для**: Мобильные приложения, SPA, публичные клиенты
- **Как работает**: То же самое, но добавляет code_verifier/code_challenge для защиты от перехвата
- **Зачем нужен**: Публичные клиенты не могут безопасно хранить client_secret

**3. Client Credentials Flow**
- **Для**: Межсервисное взаимодействие (M2M)
- **Как работает**: Сервис аутентифицируется напрямую с client_id и client_secret
- **Без пользователя**: Используется бэкенд-сервисами для вызова API

**4. Implicit Flow (Устарел)**
- **Использовался для**: Браузерных приложений
- **Почему устарел**: Токены в URL-фрагменте, нет refresh-токенов
- **Замена**: Authorization Code + PKCE

**Матрица выбора потока:**

| Тип клиента | Поток |
|-------------|-------|
| Серверное веб-приложение | Authorization Code |
| SPA / Мобильное приложение | Authorization Code + PKCE |
| Бэкенд-сервис | Client Credentials |
| IoT / Ограниченный ввод | Device Authorization |

---

## Follow-ups
- How does PKCE protect against authorization code interception?
- What is the difference between access tokens and refresh tokens?
- How to implement token refresh without user interaction?

## Dopolnitelnye voprosy (RU)
- Как PKCE защищает от перехвата кода авторизации?
- В чём разница между access-токенами и refresh-токенами?
- Как реализовать обновление токенов без участия пользователя?

## References
- [[c-authentication]]
- [[c-oauth]]
- [[moc-backend]]
