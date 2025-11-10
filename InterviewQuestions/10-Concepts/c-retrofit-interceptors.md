---
id: "20251110-162411"
title: "Retrofit Interceptors / Retrofit Interceptors"
aliases: ["Retrofit Interceptors"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: []
created: "2025-11-10"
updated: "2025-11-10"
tags: ["programming-languages", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Retrofit interceptors are OkHttp interceptors used within Retrofit clients to observe, modify, and handle HTTP requests and responses at a central point. They enable cross-cutting concerns such as logging, authentication headers (e.g., tokens), retries, offline caching, and error handling without duplicating code in each API call. Commonly used in Android/Kotlin and Java projects, they are key for debugging, security, and consistent network behavior.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Interceptors в Retrofit — это перехватчики OkHttp, используемые внутри клиента Retrofit для наблюдения, изменения и обработки HTTP-запросов и ответов в одном месте. Они позволяют реализовать сквозные задачи, такие как логирование, добавление токенов авторизации, повтор запросов, офлайн-кеширование и обработка ошибок без дублирования логики в каждом методе API. Широко применяются в Android/Kotlin и Java-проектах для отладки, безопасности и единообразного сетевого поведения.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Two main types: application interceptors (added to OkHttpClient) and network interceptors (closer to network layer); both can be used with Retrofit.
- Ideal for adding common headers (Authorization, User-Agent), signing requests, handling tokens (e.g., refresh on 401), and centralized error mapping.
- Useful for logging requests/responses (URL, headers, body) for debugging while keeping this concern outside business logic.
- Can implement retry, backoff, and offline/Cache-Control strategies consistently across all API calls.
- Must be used carefully to avoid infinite loops, leaking sensitive data in logs, or unexpectedly modifying idempotency of requests.

## Ключевые Моменты (RU)

- Два основных типа: application interceptors (добавляются в OkHttpClient) и network interceptors (ближе к сетевому уровню); оба используются совместно с Retrofit.
- Подходят для добавления общих заголовков (Authorization, User-Agent), подписания запросов, обработки токенов (например, обновление при 401) и централизованного маппинга ошибок.
- Удобны для логирования запросов/ответов (URL, заголовки, тело) для отладки, вынося эту логику из бизнес-кода.
- Позволяют единообразно реализовать retry, backoff и офлайн/Cache-Control стратегии для всех запросов API.
- Требуют осторожности, чтобы избежать бесконечных циклов, утечек чувствительных данных в логах и нежелательного изменения идемпотентности запросов.

## References

- https://square.github.io/okhttp/interceptors/
- https://square.github.io/retrofit/
