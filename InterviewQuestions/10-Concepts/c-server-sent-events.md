---
id: "20251110-170045"
title: "Server Sent Events / Server Sent Events"
aliases: ["Server Sent Events"]
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

Server-Sent Events (SSE) is an HTTP-based mechanism that allows a server to push a continuous stream of text/event data to the client over a single long-lived, one-way connection. It is commonly used for real-time updates such as notifications, live feeds, and monitoring dashboards without requiring the client to constantly poll. SSE is built on standard HTTP, works well with proxies and browsers, and provides an event-driven API via `EventSource` in JavaScript.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Server-Sent Events (SSE) — это механизм поверх HTTP, позволяющий серверу отправлять непрерывный поток текстовых/событийных данных клиенту через одно долгоживущее одностороннее соединение. Чаще всего используется для реального времени: уведомления, живые ленты, мониторинг без постоянного опроса серверa со стороны клиента. SSE основан на стандартном HTTP, хорошо работает с прокси и браузерами и предоставляет событийный API через `EventSource` в JavaScript.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- One-way streaming: Server can continuously push events to the client; the client cannot send data back over the same SSE channel.
- Standard HTTP protocol: Uses a persistent HTTP connection (`Content-Type: text/event-stream`), simplifying deployment with existing infrastructure.
- EventSource API: In browsers, `EventSource` automatically handles connection setup, reconnection, and message dispatching with minimal code.
- Auto-reconnect and last-event-id: SSE supports built-in reconnection and resuming from the last received event ID, improving reliability.
- Compared to WebSockets: SSE is simpler and well-suited for server→client updates; WebSockets are preferred for full-duplex, high-frequency, or binary communication.

## Ключевые Моменты (RU)

- Односторонний стриминг: Сервер может непрерывно отправлять события клиенту; клиент не посылает данные обратно по тому же SSE-каналу.
- Стандартный HTTP-протокол: Используется постоянное HTTP-соединение (`Content-Type: text/event-stream`), что упрощает работу с существующей инфраструктурой.
- API EventSource: В браузерах `EventSource` автоматически настраивает соединение, переподключения и доставку сообщений при минимуме кода.
- Автопереподключение и last-event-id: SSE поддерживает восстановление соединения и продолжение с последнего полученного ID события, повышая надежность.
- Сравнение с WebSockets: SSE проще и оптимален для обновлений сервер→клиент; WebSockets подходят для двустороннего, высокочастотного или бинарного обмена.

## References

- WHATWG HTML Living Standard – Server-sent events section
- MDN Web Docs – Server-sent events (EventSource)
