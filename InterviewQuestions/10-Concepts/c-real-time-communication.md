---
id: "20251110-170831"
title: "Real Time Communication / Real Time Communication"
aliases: ["Real Time Communication"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: ["c-websockets", "c-webrtc", "c-server-sent-events", "c-networking", "c-rest-api"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---

# Summary (EN)

Real Time Communication (RTC) is a communication model where data (audio, video, messages, events) is transmitted with minimal latency so participants can interact almost instantly, without relying on traditional request-response polling. It is widely used in video conferencing, voice calls, live chat, multiplayer gaming, collaboration tools, and IoT monitoring. In programming, RTC typically relies on persistent or long-lived connections (e.g., WebRTC, WebSockets, RTMP, MQTT) and requires careful handling of latency, synchronization, scalability, and network reliability.

*This concept file was auto-generated. Content enriched for concise interview-focused understanding.*

# Краткое Описание (RU)

Real Time Communication (RTC) — это модель обмена данными (аудио, видео, сообщения, события) с минимальной задержкой, позволяющая участникам взаимодействовать практически мгновенно, без классического опроса по схеме запрос-ответ. Широко используется в видеоконференциях, голосовой связи, онлайн‑чатах, мультиплеерных играх, инструментах совместной работы и мониторинге IoT. В разработке RTC опирается на постоянные или длительно живущие соединения (например, WebRTC, WebSockets, RTMP, MQTT) и требует особого внимания к задержкам, синхронизации, масштабированию и устойчивости к сетевым сбоям.

*Этот файл концепции был создан автоматически. Содержимое дополнено для краткого интервью-ориентированного объяснения.*

## Key Points (EN)

- Low latency: Focuses on end-to-end delay small enough for interactive use (typically milliseconds to low hundreds of ms), unlike batch or offline communication.
- Persistent connections: Often uses long-lived channels (WebSockets, WebRTC peer connections, real-time messaging protocols) instead of repeated HTTP polling.
- Bidirectional and event-driven: Enables both client and server (or peers) to push updates instantly; fits publish/subscribe and streaming patterns.
- Network challenges: Must handle jitter, packet loss, NAT traversal, congestion control, and device/network heterogeneity while preserving user experience.
- Scalability and reliability: Real-time systems often require media servers, signaling services, and horizontal scaling strategies to support many concurrent users.

## Ключевые Моменты (RU)

- Низкая задержка: Ориентирована на сквозную задержку, достаточную для интерактивности (миллисекунды или сотни миллисекунд), в отличие от пакетной или офлайн-коммуникации.
- Постоянные соединения: Обычно использует длительные соединения (WebSockets, WebRTC, протоколы для real-time сообщений), а не повторяющийся HTTP polling.
- Двунаправленность и событийная модель: Клиент и сервер (или пиры) могут моментально отправлять события друг другу; хорошо сочетается с pub/sub и стриминг-паттернами.
- Сетевые сложности: Нужно учитывать джиттер, потерю пакетов, обход NAT, контроль перегрузки и различия в устройствах/сетях, сохраняя приемлемое качество.
- Масштабирование и надежность: Часто требуются медиа-серверы, сигнальные сервисы и горизонтальное масштабирование для поддержки большого числа одновременных пользователей.

## References

- WebRTC Overview (MDN): https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API
- WebSockets (MDN): https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API
- Real-time communication concepts (webrtc.org): https://webrtc.org

