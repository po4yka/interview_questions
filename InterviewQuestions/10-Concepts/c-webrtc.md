---
id: "20251110-132908"
title: "Webrtc / Webrtc"
aliases: ["Webrtc"]
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

WebRTC (Web Real-Time Communication) is an open standard and set of browser APIs enabling real-time audio, video, and arbitrary data transfer directly between peers without requiring intermediate media servers. It matters because it allows building low-latency applications such as video conferencing, voice calls, screen sharing, and realtime collaboration directly in the browser or mobile apps. WebRTC is widely used in modern communication platforms and is supported by major browsers and native SDKs.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

WebRTC (Web Real-Time Communication) — это открытый стандарт и набор API браузера для организации обмена аудио, видео и произвольными данными между клиентами в реальном времени без обязательного использования промежуточных медиасерверов. Он важен тем, что позволяет создавать низколатентные приложения — видеозвонки, голосовую связь, шаринг экрана и совместную работу — прямо в браузере и мобильных приложениях. WebRTC широко поддерживается современными браузерами и нативными SDK и используется во многих коммуникационных сервисах.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Peer-to-peer communication: Establishes direct connections between clients using ICE (Interactive Connectivity Establishment), STUN, and TURN to traverse NATs and firewalls.
- Media and data channels: Provides high-level APIs for audio/video streams (getUserMedia, RTCPeerConnection) and low-latency bidirectional data channels (RTCDataChannel).
- Built-in codecs and encryption: Uses standardized media codecs (e.g., Opus, VP8/VP9/AV1 where supported) and mandatory end-to-end encryption over DTLS-SRTP for secure communication.
- Signaling is external: Does not define how peers discover each other; applications must implement their own signaling (e.g., via WebSocket, HTTP, or other channels).
- Typical use cases: Video conferencing, voice chat in apps/games, screen sharing, file transfer, and collaborative tools (e.g., whiteboards, remote assistance).

## Ключевые Моменты (RU)

- P2P-взаимодействие: Устанавливает прямые соединения между клиентами с помощью ICE, STUN и TURN для обхода NAT и файрволов.
- Медиа- и дата-каналы: Предоставляет высокоуровневые API для работы с аудио/видео-потоками (getUserMedia, RTCPeerConnection) и низколатентными двунаправленными дата-каналами (RTCDataChannel).
- Встроенные кодеки и шифрование: Использует стандартные медиакодеки (например, Opus, VP8/VP9/AV1 при поддержке) и обязательное шифрование трафика через DTLS-SRTP для безопасности.
- Внешний сигналинг: Не регламентирует механизм сигналинга и поиска пиров; приложение должно реализовать его само (например, через WebSocket или HTTP).
- Типичные сценарии: Видеоконференции, голосовой чат в приложениях и играх, шаринг экрана, передача файлов и инструменты совместной работы.

## References

- https://webrtc.org
- https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API
