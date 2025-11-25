---
id: "20251110-185305"
title: "Okhttp Interceptors / Okhttp Interceptors"
aliases: ["Okhttp Interceptors"]
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
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

OkHttp Interceptors are pluggable components in the OkHttp HTTP client that can observe, modify, and short‑circuit requests and responses as they flow through the client. They are commonly used for cross‑cutting concerns such as logging, authentication headers, retries, and response rewriting without changing call-site code. In Android and Kotlin/JVM projects, interceptors are a primary mechanism to centralize networking behavior and enforce consistent policies across all HTTP calls.

*This concept file was auto-generated and has been enriched with concise technical details for interview preparation.*

# Краткое Описание (RU)

Перехватчики OkHttp (OkHttp Interceptors) — это подключаемые компоненты в HTTP-клиенте OkHttp, которые позволяют наблюдать, изменять или прерывать HTTP-запросы и ответы на различных этапах их обработки. Они используются для реализации сквозных задач, таких как логирование, добавление заголовков аутентификации, повторные попытки и модификация ответов, без изменения кода в местах вызова. В проектах на Android и Kotlin/JVM перехватчики являются основным механизмом централизации сетевой логики и единых правил для всех HTTP-запросов.

*Этот файл концепции был создан автоматически и дополнен краткими техническими деталями для подготовки к собеседованию.*

## Key Points (EN)

- Types of interceptors: OkHttp provides application interceptors and network interceptors; application interceptors operate at a higher level (before retries, redirects), while network interceptors work closer to the network layer (after caching, before the socket).
- Cross-cutting concerns: Ideal for adding common headers (e.g., Authorization), logging requests/responses, measuring latency, handling retries, and implementing custom error handling in one centralized place.
- Request/response modification: Interceptors can clone and modify Request or Response objects (e.g., change URL, add query params, normalize error bodies) before passing them along the chain.
- Ordering and chain: Interceptors are executed in the order they are added to OkHttpClient; each interceptor must call `chain.proceed(request)` (unless intentionally short-circuiting) to continue the chain.
- Short-circuiting and mocking: Interceptors can return a synthetic Response without hitting the network, which is useful for offline behavior, feature flags, and testing.

## Ключевые Моменты (RU)

- Типы перехватчиков: В OkHttp есть application interceptors и network interceptors; application работают на более высоком уровне (до повторов/редиректов), а network — ближе к сети (после кеша, перед сокетом).
- Сквозные задачи: Удобны для добавления общих заголовков (например, Authorization), логирования запросов/ответов, измерения задержек, реализации повторных попыток и централизованной обработки ошибок.
- Модификация запросов/ответов: Перехватчики могут клонировать и изменять объекты Request и Response (менять URL, добавлять query-параметры, нормализовать тело ошибок) перед передачей дальше по цепочке.
- Порядок и цепочка: Перехватчики выполняются в порядке добавления в OkHttpClient; каждый перехватчик должен вызвать `chain.proceed(request)` (если не требуется прервать цепочку), чтобы продолжить обработку.
- Прерывание и мокирование: Перехватчики могут вернуть синтетический Response без реального сетевого запроса, что полезно для офлайн-режима, фич-флагов и тестирования.

## References

- OkHttp Official Documentation — Interceptors: https://square.github.io/okhttp/interceptors/
- OkHttp GitHub Repository: https://github.com/square/okhttp
