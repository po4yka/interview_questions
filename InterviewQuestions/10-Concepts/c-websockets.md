---
id: "20251110-132848"
title: "Websockets / Websockets"
aliases: ["Websockets"]
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
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Summary (EN)

WebSockets is a full-duplex, persistent communication protocol over a single TCP connection, typically initiated from a web browser via an HTTP/HTTPS handshake. It enables real-time, low-latency, bidirectional data exchange between client and server without repeated HTTP requests or long polling. WebSockets are widely used for chats, live dashboards, multiplayer games, collaborative editing, and event-driven systems.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

WebSocket — это протокол постоянного двунаправленного обмена данными поверх одного TCP-соединения, обычно инициируемый из браузера через HTTP/HTTPS рукопожатие. Он обеспечивает обмен данными в реальном времени с низкими задержками между клиентом и сервером без постоянных повторных HTTP-запросов или long polling. WebSocket широко используется для чатов, живых дашбордов, онлайн-игр, совместного редактирования и событийно-ориентированных систем.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Persistent, full-duplex channel: After the initial HTTP handshake (Upgrade request), client and server keep a single open TCP connection for bidirectional communication.
- Low overhead vs HTTP polling: Avoids repeated headers and connections, reducing latency and bandwidth for frequent small messages.
- Message-based protocol: Data is sent as discrete text or binary frames, making it suitable for streaming updates and real-time events.
- Requires server support: Backend must implement the WebSocket protocol (e.g., via libraries/frameworks) and handle connection lifecycle, scaling, and backpressure.
- Security and compatibility: Commonly used as wss:// over TLS; works through most proxies but may need configuration, and is distinct from REST semantics.

## Ключевые Моменты (RU)

- Постоянный двунаправленный канал: После начального HTTP-handshake (запрос Upgrade) клиент и сервер поддерживают одно открытое TCP-соединение для обмена данными в обе стороны.
- Меньшие накладные расходы по сравнению с HTTP-polling: Нет постоянного повторения заголовков и установки соединений, что снижает задержки и трафик при частых небольших сообщениях.
- Протокол, основанный на сообщениях: Данные передаются в виде отдельных текстовых или бинарных фреймов, удобно для потоковых обновлений и событий в реальном времени.
- Требует поддержки на сервере: Бэкенд должен реализовывать протокол WebSocket, управлять жизненным циклом соединений, масштабированием и backpressure.
- Безопасность и совместимость: Обычно используется как wss:// поверх TLS; проходит через большинство прокси (иногда с настройкой) и логически отличается от REST.

## References

- RFC 6455: The WebSocket Protocol — https://datatracker.ietf.org/doc/html/rfc6455
- MDN Web Docs: WebSockets — https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API

