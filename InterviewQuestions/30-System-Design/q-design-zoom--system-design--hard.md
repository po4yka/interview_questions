---
id: q-design-zoom
title: Design Zoom (Video Conferencing)
aliases:
- Design Zoom
- Video Conferencing System
- WebRTC Architecture
topic: system-design
subtopics:
- design-problems
- webrtc
- real-time
- streaming
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-websockets-sse-long-polling--system-design--medium
- q-design-whatsapp--system-design--hard
created: 2025-01-26
updated: 2025-01-26
tags:
- design-problems
- difficulty/hard
- real-time
- system-design
- webrtc
anki_cards:
- slug: q-design-zoom-0-en
  anki_id: null
  synced_at: null
- slug: q-design-zoom-0-ru
  anki_id: null
  synced_at: null
---
# Question (EN)
> How would you design a video conferencing system like Zoom? Focus on low latency, multi-participant calls, and screen sharing.

# Vopros (RU)
> Как бы вы спроектировали систему видеоконференций, подобную Zoom? Фокус на низкой задержке, многопользовательских звонках и демонстрации экрана.

---

## Answer (EN)

### Requirements

**Functional**: 1:1 video calls, group calls (up to 1000), screen sharing, chat, recording, virtual backgrounds
**Non-functional**: <150ms latency, 99.99% availability, adaptive quality, E2E encryption option, global reach

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Clients                                │
│    (Web/Desktop/Mobile with WebRTC + Custom Protocols)      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Signaling Server                           │
│    (WebSocket - session setup, SDP exchange, ICE candidates)│
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Media Server (SFU)                         │
│    (Selective Forwarding Unit - routes media streams)       │
└─────────┬───────────────┬───────────────┬───────────────────┘
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  TURN/    │   │ Recording │   │  Transcod-│
    │  STUN     │   │  Service  │   │  ing      │
    └───────────┘   └───────────┘   └───────────┘
```

### WebRTC Fundamentals

```
Connection establishment (ICE):

1. STUN (Session Traversal Utilities for NAT):
   - Discover public IP address
   - Works for ~80% of NAT types

2. TURN (Traversal Using Relays around NAT):
   - Relay server for symmetric NAT
   - Fallback when direct P2P fails
   - Higher latency, more bandwidth cost

3. ICE (Interactive Connectivity Establishment):
   - Gathers candidates (host, srflx, relay)
   - Tests connectivity, selects best path
   - Handles network changes (ICE restart)
```

### SFU vs MCU Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  MCU (Multipoint Control Unit)                              │
├─────────────────────────────────────────────────────────────┤
│  - Server decodes ALL streams                               │
│  - Mixes into single composite stream                       │
│  - Client receives 1 stream                                 │
│  - CPU intensive on server                                  │
│  - Fixed layout                                             │
│  - Legacy approach                                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  SFU (Selective Forwarding Unit) ← Zoom uses this          │
├─────────────────────────────────────────────────────────────┤
│  - Server forwards streams without decoding                 │
│  - Client selects which streams to receive                  │
│  - Client decodes multiple streams                          │
│  - Much more scalable                                       │
│  - Flexible layout (client-side)                            │
│  - Modern approach                                          │
└─────────────────────────────────────────────────────────────┘

For N participants:
- MCU: Server CPU = O(N), Client receives 1 stream
- SFU: Server CPU = O(1), Client receives N-1 streams
```

### Bandwidth Adaptation

```
Simulcast (multiple resolutions):
┌─────────────────────────────────────────────┐
│  Sender encodes 3 layers simultaneously:    │
│                                             │
│  ┌──────────┐  High:   1080p @ 2.5 Mbps    │
│  │  Camera  │─→ Mid:    720p @ 1.0 Mbps    │
│  └──────────┘  Low:    360p @ 0.3 Mbps     │
│                                             │
│  SFU forwards appropriate layer per viewer  │
│  based on their bandwidth/screen size       │
└─────────────────────────────────────────────┘

SVC (Scalable Video Coding):
┌─────────────────────────────────────────────┐
│  Single stream with embedded layers:        │
│                                             │
│  ┌─────────────────────────────────┐        │
│  │ Base Layer (always sent)        │        │
│  ├─────────────────────────────────┤        │
│  │ Enhancement Layer 1 (optional)  │        │
│  ├─────────────────────────────────┤        │
│  │ Enhancement Layer 2 (optional)  │        │
│  └─────────────────────────────────┘        │
│                                             │
│  Receiver drops layers as needed            │
└─────────────────────────────────────────────┘
```

### Signaling Server

```
Signaling flow (WebSocket):

1. Create Meeting:
   Client A → Server: createMeeting()
   Server → Client A: meetingId, token

2. Join Meeting:
   Client B → Server: join(meetingId)
   Server → Client A: participantJoined(B)

3. SDP Exchange (Session Description Protocol):
   Client A → Server → Client B: offer (codecs, capabilities)
   Client B → Server → Client A: answer (accepted params)

4. ICE Candidates:
   Both clients exchange connectivity info via server

5. Media Flows Directly (P2P) or via SFU
```

### Audio/Video Codecs

| Codec | Type | Bandwidth | Use Case |
|-------|------|-----------|----------|
| VP8 | Video | Medium | Good compatibility |
| VP9 | Video | 30% less | Better quality |
| H.264 | Video | Variable | Hardware acceleration |
| AV1 | Video | 50% less | Future, CPU intensive |
| Opus | Audio | 6-510 kbps | Adaptive, low latency |
| G.711 | Audio | 64 kbps | PSTN compatibility |

### Screen Sharing

```
Implementation options:

1. getDisplayMedia() API:
   - Browser native screen capture
   - User selects window/screen
   - Separate video track from camera

2. Encoding considerations:
   - High resolution (1080p-4K)
   - Low frame rate (5-15 fps)
   - Text optimization (sharp edges)
   - Content-type hints (motion vs static)

3. Architecture:
   ┌─────────┐     ┌─────────┐
   │ Camera  │────→│         │
   │ Stream  │     │   SFU   │────→ Participants
   ├─────────┤     │         │
   │ Screen  │────→│         │
   │ Stream  │     └─────────┘
   └─────────┘

   Two separate tracks, viewers choose layout
```

### Recording

```
Recording architecture:

┌─────────────────────────────────────────────────────────────┐
│                     Recording Options                        │
├─────────────────────────────────────────────────────────────┤
│  1. Server-side (Zoom's approach):                          │
│     - SFU sends streams to recording service                │
│     - Composite into single video                           │
│     - Store in S3/cloud storage                             │
│     - Requires server CPU                                   │
│                                                             │
│  2. Client-side:                                            │
│     - Each participant records locally                      │
│     - Higher quality, uses client resources                 │
│     - Sync issues possible                                  │
│                                                             │
│  3. Hybrid (Zoom does this):                                │
│     - Cloud recording (server-side)                         │
│     - Local recording option                                │
└─────────────────────────────────────────────────────────────┘

Cloud recording pipeline:
Stream → Transcoder → MP4 → S3 → CDN for playback
```

### End-to-End Encryption

```
E2E Encryption (optional in Zoom):

┌─────────────────────────────────────────────────────────────┐
│  Without E2E (default):                                     │
│  - SRTP encrypts media in transit                           │
│  - Server can decrypt (for recording, transcription)        │
│                                                             │
│  With E2E:                                                  │
│  - Client encrypts before sending                           │
│  - Server forwards encrypted blobs (can't decrypt)          │
│  - Disables server features (cloud recording, live transcr.)│
│                                                             │
│  Key exchange:                                              │
│  - Per-meeting symmetric key                                │
│  - Distributed via asymmetric encryption                    │
│  - Security code verification                               │
└─────────────────────────────────────────────────────────────┘
```

### Handling Network Issues

```
1. Jitter Buffer:
   - Buffer incoming packets (50-200ms)
   - Smooth out arrival time variations
   - Tradeoff: latency vs smoothness

2. Forward Error Correction (FEC):
   - Send redundant data
   - Recover from packet loss without retransmission
   - ~10-20% overhead

3. Packet Loss Concealment:
   - Audio: interpolate from adjacent frames
   - Video: freeze frame, gradual decode

4. Congestion Control:
   - GCC (Google Congestion Control)
   - Adjust bitrate based on packet loss/delay
   - Switch simulcast layers dynamically

5. ICE Restart:
   - Handle network changes (WiFi → LTE)
   - Re-establish connection transparently
```

### Scale Considerations

```
Zoom-scale numbers:
- 300M+ daily meeting participants
- Meetings up to 1000 participants
- Global presence (data centers worldwide)

Scaling strategies:
1. Geographic distribution:
   - Route to nearest media server
   - Edge servers for TURN/STUN

2. Meeting sharding:
   - Large meetings split across SFU clusters
   - Cascading: SFU-to-SFU connections

3. Compute:
   - SFU is mostly I/O bound (forwarding)
   - Recording/transcoding needs GPU
```

### Key Technical Decisions

| Aspect | Decision | Reason |
|--------|----------|--------|
| Architecture | SFU | Scalable, flexible |
| Transport | SRTP/DTLS over UDP | Low latency |
| Signaling | WebSocket | Real-time, bidirectional |
| Video | VP9 + Simulcast | Quality + adaptability |
| Audio | Opus | Adaptive bitrate, low latency |
| NAT Traversal | ICE (STUN+TURN) | Works through firewalls |

---

## Otvet (RU)

### Требования

**Функциональные**: 1:1 видеозвонки, групповые звонки (до 1000), демонстрация экрана, чат, запись, виртуальные фоны
**Нефункциональные**: <150мс задержка, 99.99% доступность, адаптивное качество, опция E2E шифрования, глобальный охват

### Основы WebRTC

```
Установление соединения (ICE):

1. STUN (Session Traversal Utilities for NAT):
   - Определить публичный IP адрес
   - Работает для ~80% типов NAT

2. TURN (Traversal Using Relays around NAT):
   - Relay-сервер для симметричного NAT
   - Fallback когда P2P не работает
   - Выше задержка, больше трафика

3. ICE (Interactive Connectivity Establishment):
   - Собирает кандидатов (host, srflx, relay)
   - Тестирует связность, выбирает лучший путь
   - Обрабатывает смену сети (ICE restart)
```

### Архитектура SFU vs MCU

```
┌─────────────────────────────────────────────────────────────┐
│  MCU (Multipoint Control Unit)                              │
├─────────────────────────────────────────────────────────────┤
│  - Сервер декодирует ВСЕ потоки                             │
│  - Смешивает в один композитный поток                       │
│  - Клиент получает 1 поток                                  │
│  - Высокая нагрузка на CPU сервера                          │
│  - Устаревший подход                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  SFU (Selective Forwarding Unit) ← Zoom использует это      │
├─────────────────────────────────────────────────────────────┤
│  - Сервер пересылает потоки без декодирования               │
│  - Клиент выбирает какие потоки получать                    │
│  - Клиент декодирует несколько потоков                      │
│  - Гораздо масштабируемее                                   │
│  - Гибкий layout (на стороне клиента)                       │
│  - Современный подход                                       │
└─────────────────────────────────────────────────────────────┘

Для N участников:
- MCU: CPU сервера = O(N), Клиент получает 1 поток
- SFU: CPU сервера = O(1), Клиент получает N-1 потоков
```

### Адаптация полосы пропускания

```
Simulcast (несколько разрешений):
┌─────────────────────────────────────────────┐
│  Отправитель кодирует 3 слоя одновременно: │
│                                             │
│  ┌──────────┐  High:   1080p @ 2.5 Mbps    │
│  │  Камера  │─→ Mid:    720p @ 1.0 Mbps    │
│  └──────────┘  Low:    360p @ 0.3 Mbps     │
│                                             │
│  SFU пересылает подходящий слой каждому    │
│  зрителю на основе bandwidth/размера экрана│
└─────────────────────────────────────────────┘

SVC (Scalable Video Coding):
┌─────────────────────────────────────────────┐
│  Один поток со встроенными слоями:         │
│                                             │
│  ┌─────────────────────────────────┐        │
│  │ Базовый слой (всегда отправляется)│      │
│  ├─────────────────────────────────┤        │
│  │ Улучшающий слой 1 (опционально) │        │
│  ├─────────────────────────────────┤        │
│  │ Улучшающий слой 2 (опционально) │        │
│  └─────────────────────────────────┘        │
│                                             │
│  Получатель отбрасывает слои по необходимости│
└─────────────────────────────────────────────┘
```

### Демонстрация экрана

```
Варианты реализации:

1. getDisplayMedia() API:
   - Нативный захват экрана браузером
   - Пользователь выбирает окно/экран
   - Отдельный видеотрек от камеры

2. Особенности кодирования:
   - Высокое разрешение (1080p-4K)
   - Низкий framerate (5-15 fps)
   - Оптимизация для текста (четкие края)
   - Подсказки типа контента (движение vs статика)
```

### Запись

```
Архитектура записи:

1. Серверная (подход Zoom):
   - SFU отправляет потоки в сервис записи
   - Композит в одно видео
   - Хранение в S3/облаке
   - Требует CPU сервера

2. Клиентская:
   - Каждый участник записывает локально
   - Выше качество, использует ресурсы клиента
   - Возможны проблемы синхронизации

3. Гибридная (Zoom делает так):
   - Облачная запись (серверная)
   - Опция локальной записи
```

### Обработка сетевых проблем

```
1. Jitter Buffer:
   - Буферизировать входящие пакеты (50-200мс)
   - Сглаживать вариации времени прихода
   - Компромисс: задержка vs плавность

2. Forward Error Correction (FEC):
   - Отправлять избыточные данные
   - Восстановление без ретрансмиссии
   - ~10-20% overhead

3. Packet Loss Concealment:
   - Аудио: интерполяция из соседних кадров
   - Видео: заморозка кадра, постепенное декодирование

4. Congestion Control:
   - GCC (Google Congestion Control)
   - Регулировать bitrate по потерям/задержкам
   - Динамическое переключение simulcast слоёв
```

### Ключевые технические решения

| Аспект | Решение | Причина |
|--------|---------|---------|
| Архитектура | SFU | Масштабируемость, гибкость |
| Транспорт | SRTP/DTLS через UDP | Низкая задержка |
| Сигналинг | WebSocket | Real-time, двунаправленный |
| Видео | VP9 + Simulcast | Качество + адаптивность |
| Аудио | Opus | Адаптивный bitrate, низкая задержка |
| NAT Traversal | ICE (STUN+TURN) | Работает через firewall |

### Масштаб

```
Числа уровня Zoom:
- 300M+ ежедневных участников митингов
- Митинги до 1000 участников
- Глобальное присутствие (датацентры по всему миру)

Стратегии масштабирования:
1. Географическое распределение:
   - Маршрутизация на ближайший media сервер
   - Edge серверы для TURN/STUN

2. Шардирование митингов:
   - Большие митинги разделяются между кластерами SFU
   - Каскадирование: SFU-to-SFU соединения
```

---

## Follow-ups

- How would you implement the breakout rooms feature?
- How does Zoom handle audio echo cancellation and noise suppression?
- How would you design the waiting room and host controls?
- How would you implement live transcription and closed captions?
- How does bandwidth estimation work in WebRTC?
