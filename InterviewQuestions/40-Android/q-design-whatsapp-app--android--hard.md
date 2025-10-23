---
id: 20251020-200000
title: Design WhatsApp App / Проектирование приложения WhatsApp
aliases:
- Design WhatsApp App
- Проектирование приложения WhatsApp
topic: android
subtopics:
- networking-http
- files-media
- service

question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
source: https://developer.android.com/training/sync-adapters
source_note: Android sync and messaging patterns
status: reviewed
moc: moc-android
related:
- q-data-sync-unstable-network--android--hard
- q-database-encryption-android--android--medium
- q-deep-link-vs-app-link--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
- en
- ru
-
- a
- n
- d
- r
- o
- i
- d
- /
- n
- e
- t
- w
- o
- r
- k
- i
- n
- g
- -
- h
- t
- t
- p

- android/networking-http
- android/files-media
- android/service
- messaging
- realtime
- e2ee
- difficulty/hard---
# Вопрос (RU)
> Как спроектировать мессенджер WhatsApp для Android?

# Question (EN)
> How to design WhatsApp for Android?---
## Ответ (RU)

WhatsApp включает: обмен сообщениями 1-to-1/группы, медиа, статусы доставки/прочтения, E2EE (Signal Protocol), голос/видео-звонки, офлайн-персистентность, синхронизацию и масштабирование.

### Требования
**Функциональные:**
- Сообщения: текст, медиа (фото/видео/док), голосовые сообщения. Группы.
- Статусы: sent/delivered/read (двойная/синяя галочка), typing indicator.
- Безопасность: E2EE (Signal Protocol), device verification.
- Присутствие: online/offline, last seen, статусы.
- Push: FCM для оффлайн-доставки, silent push для синхронизации.
- Звонки: WebRTC для голоса/видео, STUN/TURN для NAT traversal.

**Нефункциональные:** низкая латентность (<200ms P95), высокая доступность, масштабируемость (миллиарды сообщений/день), конфиденциальность (zero-knowledge server), бережная батарея/трафик, офлайн.

### Архитектура (высокоуровнево)
Клиент Android (локальная БД, E2EE engine, WebSocket, media cache) → Load Balancer → микросервисы (Chat/Presence/Media/Call Signaling/Push) → очереди (Kafka), БД (Cassandra для messages, PostgreSQL для users), хранилище медиа (S3+CDN), кэш (Redis для presence), Signal Server для звонков.

### Клиент Android: ключевые потоки
1) Отправка сообщения: шифрование Signal Protocol (ratchet), локальная запись (pending), WebSocket send, ack от сервера → delivered, receipt от получателя → read.
2) Получение: WebSocket → расшифровка → локальная БД → UI update, отправка read receipt.
3) Медиа: сжатие (JPEG для фото, H.264/HEVC для видео), загрузка на CDN, отправка URL+thumbnail+decryption key в сообщении, ленивая подгрузка медиа.
4) Офлайн: очередь неотправленных, хранение до 30 дней, ресенд при онлайне, backoff при сетевых ошибках.
5) Группы: каждый участник имеет sender key (pairwise sessions → group sessions), рэтчет при изменении состава, forward secrecy.
6) Звонки: WebRTC SDP negotiation через Signal Server, ICE candidates, STUN/TURN fallback, адаптивный bitrate.

```kotlin
// Minimal Signal Protocol usage (conceptual)
val session = SessionBuilder(recipientAddress).buildSenderSession()
val ciphertext = SessionCipher(session).encrypt(plaintext.toByteArray())
```

```kotlin
// WebSocket send with ack
ws.send(MessageProto(id, encrypted, timestamp))
ackFlow.first { it.msgId == id } // wait for ack
```

```kotlin
// Offline queue
if (!networkAvailable) {
  db.insertPending(msg)
            } else {
  sendAndRetry(msg)
}
```

### Сервер: маршрутизация и персистентность
- Chat Service: маршрутизация сообщений по userId, хранение зашифрованных сообщений (server не видит plaintext), доставка через WebSocket или push если offline, удаление после доставки (or TTL 30 дней).
- Presence Service: heartbeat каждые 30s, кэш в Redis, pub/sub для обновлений контактов.
- Media Service: multipart upload, генерация thumbnails (без расшифровки), CDN для доставки, E2EE ключ в metadata.
- Call Signaling: relay SDP/ICE candidates, не участвует в медиа-потоке (P2P через WebRTC).
- Push Service: FCM integration, приоритизация (high priority для звонков, normal для сообщений).

### Архитектурный анализ

**Границы сервисов:**
- **Chat Service**: принимает сообщения от отправителя, проверяет rate limits, сохраняет в БД (Cassandra: partition key userId+timestamp), маршрутизирует получателю через WebSocket (если онлайн) или ставит в очередь доставки. Публикует события в Kafka для аналитики.
- **Presence Service**: обрабатывает heartbeat от клиентов (WS ping/pong), обновляет статус в Redis (TTL 45s), публикует изменения статуса подписчикам (contacts list), управляет typing indicators (ephemeral, TTL 10s).
- **Media Service**: принимает multipart uploads (chunks), генерирует thumbnails через Image Processing Pipeline (без доступа к plaintext: thumbnail создаётся клиентом или из encrypted preview), хранит в S3 с lifecycle policies (холодное хранилище через Glacier после 30 дней, удаление через 1 год). Поддерживает resumable uploads.
- **Call Signaling Service**: relay SDP offers/answers и ICE candidates между peers, не участвует в RTP/SRTP потоке (P2P). Fallback TURN server для NAT traversal (relay медиа, ~5-10% звонков). Поддерживает call queueing и call waiting.
- **Push Service**: интеграция с FCM/APNS, поддерживает message collapsing (последнее сообщение при multiple pending), priority channels, device token management, retry с backoff.
- **Group Service**: управляет членством в группах, генерирует invite links с TTL, обрабатывает admin actions, синхронизирует group keys при изменениях состава.

**Доменные модели:**
- **Message**: id (UUID), senderId, recipientId/groupId, encryptedContent (blob), timestamp, status (PENDING/SENT/DELIVERED/READ), mediaUrl (если медиа), thumbnailUrl, mediaKey (для E2EE), expiresAt (для disappearing messages).
- **Chat**: id, participants (userId[]), lastMessage, unreadCount, muteUntil, isPinned, createdAt, updatedAt.
- **User**: id, phoneNumber, publicKey (Signal Protocol identity key), deviceId[], lastSeen, status (online/offline), profilePhoto.
- **Group**: id, name, adminIds[], memberIds[], createdAt, inviteLink (UUID+TTL), settings (allowMemberInvite, onlyAdminSend).
- **Receipt**: messageId, userId, type (DELIVERED/READ), timestamp.

**Хранение данных:**
- **Cassandra (Messages)**: partition key: (userId, YYYYMM), clustering key: timestamp DESC. Хранение зашифрованных сообщений, TTL 30 дней для доставленных, индекс на messageId для receipts. Replication factor 3, eventual consistency (допустимо для messaging).
- **PostgreSQL (Users, Groups)**: strong consistency для user metadata, group membership. Индексы на phoneNumber, userId. Репликация master-slave для чтения.
- **Redis (Presence, Typing)**: keys: `presence:{userId}` (TTL 45s), `typing:{chatId}:{userId}` (TTL 10s), `online:{userId}` (set). Pub/Sub каналы для real-time updates.
- **S3 (Media)**: bucket per region, lifecycle rules (Standard → Glacier → Delete), pre-signed URLs (TTL 1h) для скачивания. CDN (CloudFront) для кэширования популярного контента.

**E2EE и Signal Protocol:**
- **Identity Keys**: долгосрочные ed25519 ключи для аутентификации устройств. Публикуются на сервер при регистрации, валидируются через QR-код safety numbers.
- **Pre-Keys**: одноразовые ECDH ключи (пачка из 100), используются для инициации сессии с оффлайн-пользователем. Пополняются при истощении.
- **Session Ratchet (Double Ratchet)**: DH ratchet для обновления session key при каждом обмене, symmetric ratchet для forward secrecy. Поддерживает out-of-order доставку.
- **Group Sessions**: каждый участник имеет sender key, распределяется через pairwise sessions. При добавлении/удалении участника — полный re-key группы.
- **Device Verification**: QR-код safety number = hash(identityKey_A || identityKey_B), сравнение для защиты от MITM. Уведомления при смене ключей устройства.

**Согласованность и доставка:**
- **At-least-once delivery**: клиент ресендит сообщение до получения ack, сервер дедуплицирует по messageId. Idempotency tokens для предотвращения двойной доставки.
- **Ordered delivery**: сервер добавляет server-side timestamp, клиент сортирует по timestamp + messageId для устранения неоднозначности. Для групп: vector clocks для causal ordering.
- **Offline queueing**: сервер хранит сообщения до 30 дней, клиент синхронизирует при онлайне через batch fetch (last_sync_timestamp). Push notification для пробуждения клиента.
- **Read receipts**: optional (пользователь может отключить), отправляется только после рендера сообщения на экране. Batch receipts для групп (не отправлять receipt на каждое сообщение).

**Медиа-пайплайн:**
- **Сжатие (клиент)**: JPEG quality 85% для фото (resize ≤1600px), H.264/HEVC для видео (~1Mbps для мобильных сетей), Opus для голосовых сообщений.
- **Chunked upload**: multipart upload (5MB chunks), resumable на уровне chunk, параллельная загрузка chunks для скорости.
- **Thumbnail generation**: клиент генерирует encrypted thumbnail (100x100), отправляется вместе с сообщением для мгновенного превью. Сервер не имеет доступа к plaintext.
- **CDN caching**: популярные медиа кэшируются в CloudFront, снижение нагрузки на S3, pre-signed URLs с ограниченным TTL (1h).
- **Progressive download**: клиент начинает воспроизведение видео до полной загрузки (streaming), range requests для seek.

**Голосовые/видео звонки:**
- **Signaling**: SDP negotiation через Chat Service (offer/answer/candidates). ICE gathering для P2P connectivity.
- **Media transport**: WebRTC с SRTP (encrypted RTP), P2P при возможности (80-90% звонков), TURN relay для NAT traversal (5-10%).
- **Adaptive bitrate**: динамическая регулировка качества на основе RTT/packet loss. Переключение с видео на голос при плохом канале.
- **Group calls**: SFU (Selective Forwarding Unit) для групповых звонков, каждый участник отправляет один поток в SFU, получает N-1 потоков. Scalable Video Coding (SVC) для адаптации quality per participant.
- **Call queueing**: missed call notification, call history persistence, callback button.

**Отказоустойчивость:**
- **WebSocket → Long polling fallback**: при disconnect клиент переключается на HTTP long polling (30s timeout), возврат к WS при восстановлении. Health check через ping/pong.
- **Multi-region deployment**: primary region для пользователя по geo (low latency), cross-region replication для DR. Automatic failover при региональном outage.
- **Message retry**: экспоненциальный backoff (1s, 2s, 4s, 8s, 16s, max 5 min), jitter для избежания sync storms. Пометка failed после 24h.
- **Circuit breaker**: к внешним сервисам (FCM, CDN), состояния CLOSED/OPEN/HALF_OPEN, timeout 30-60s в OPEN.
- **Graceful degradation**: при отказе presence service — скрыть online статусы, сообщения продолжают доставляться. При отказе media upload — показать retry UI.

**Безопасность и приватность:**
- **Zero-knowledge server**: сервер не имеет доступа к plaintext сообщений/медиа, хранит только зашифрованные blobs.
- **Sealed Sender**: скрытие метаданных отправителя от сервера через onion encryption, сервер знает только получателя.
- **Forward secrecy**: ratchet механизм обновляет session keys, compromise старого ключа не раскрывает прошлые сообщения.
- **Device attestation**: SafetyNet/Play Integrity API для валидации integrity клиента, блокировка rooted/modded устройств для защиты от tampering.
- **Rate limiting**: per user/device (100 msg/min, 50 media/min), per IP (1000 connections), distributed counter в Redis. Ban на abuse (spam/flood).

**Наблюдаемость и SLO:**
- **Метрики**: P50/P95/P99 message latency (отправка → доставка, цель <200ms P95), delivery success rate (>99.9%), WebSocket uptime (>99.95%), media upload time (<5s P95), call connection rate (>95%).
- **Distributed tracing**: OpenTelemetry для сквозной трассировки message journey: client → LB → Chat → Kafka → recipient. Span tags: userId, messageId, chatId.
- **SLO alerting**: PagerDuty/Opsgenie. Alert if message_delivery_p95 > 500ms for 5min OR delivery_success_rate < 99.5% for 10min OR websocket_uptime < 99.9%.
- **Logging**: structured JSON logs, PII masking (phone numbers → hash), retention 30 days hot, 1 year cold (Splunk/ELK).

**Масштабирование:**
- **Sharding**: Chat Service шардируется по userId hash (consistent hashing), каждый shard независимо масштабируется. Cassandra partition по userId.
- **Connection pooling**: WebSocket gateways (stateful), горизонтальное масштабирование с sticky sessions (L4/L7 LB).
- **Read replicas**: PostgreSQL master-slave для user queries, Cassandra RF=3 для чтения из ближайшего datacenter.
- **Message queue**: Kafka для асинхронной обработки (push delivery, analytics), партиции по userId, retention 7 дней.
- **CDN для медиа**: CloudFront/Cloudflare, edge caching, снижение нагрузки на origin на 90%+.
- **Auto-scaling**: Kubernetes HPA на базе connection count (WS gateways), message queue depth (Chat workers), CPU/memory для stateless services.

### Оптимизация
- Батарея: heartbeat каждые 30s, coalesce push notifications, WebSocket keep-alive с увеличенным интервалом в фоне.
- Сеть: protobuf для сжатия, batch receipts, delta sync (только новые сообщения с last_sync), предзагрузка частых контактов.
- Память: message pagination (20-50 сообщений), lazy load медиа, LRU cache для декодированных изображений.

### Офлайн
- Локальная БД (Room/SQLite) для сообщений/контактов, очередь pending sends, синхронизация при онлайне, conflict resolution (server wins для metadata, merge для messages).

## Answer (EN)

WhatsApp involves 1-to-1/group messaging, media, delivery/read statuses, E2EE (Signal Protocol), voice/video calls, offline persistence, sync, and scale.

### Requirements
**Functional:**
- Messaging: text, media (photo/video/doc), voice messages. Groups.
- Statuses: sent/delivered/read (double/blue check), typing indicator.
- Security: E2EE (Signal Protocol), device verification.
- Presence: online/offline, last seen, statuses.
- Push: FCM for offline delivery, silent push for sync.
- Calls: WebRTC for voice/video, STUN/TURN for NAT traversal.

**Non-functional:** low latency (<200ms P95), high availability, scale (billions msg/day), privacy (zero-knowledge server), battery/bandwidth efficiency, offline support.

### Architecture (high-level)
Android client (local DB, E2EE engine, WebSocket, media cache) → Load Balancer → microservices (Chat/Presence/Media/Call Signaling/Push) → queues (Kafka), DB (Cassandra for messages, PostgreSQL for users), media storage (S3+CDN), cache (Redis for presence), Signal Server for calls.

### Android client key flows
1) Send: encrypt (Signal Protocol ratchet), local store (pending), WS send, server ack → delivered, recipient receipt → read.
2) Receive: WS → decrypt → local DB → UI update, send read receipt.
3) Media: compress (JPEG, H.264/HEVC), upload to CDN, send URL+thumbnail+decryption key in message, lazy load media.
4) Offline: queue unsent, store 30 days, resend on online, backoff on network errors.
5) Groups: sender keys (pairwise → group sessions), ratchet on membership changes, forward secrecy.
6) Calls: WebRTC SDP via Signal Server, ICE candidates, STUN/TURN fallback, adaptive bitrate.

### Server routing and persistence
- Chat: route by userId, store encrypted (server blind to plaintext), deliver via WS or push if offline, delete after delivery (or TTL 30d).
- Presence: heartbeat 30s, Redis cache, pub/sub for contact updates.
- Media: multipart upload, thumbnail gen (no decryption), CDN delivery, E2EE key in metadata.
- Call Signaling: relay SDP/ICE, no media (P2P WebRTC).
- Push: FCM integration, prioritization (high for calls, normal for messages).

### Architecture analysis

**Service boundaries:**
- **Chat Service**: accepts messages, rate limit checks, stores in Cassandra (partition userId+timestamp), routes to recipient via WS (online) or queue. Publishes to Kafka for analytics.
- **Presence Service**: heartbeat from clients (WS ping/pong), updates Redis (TTL 45s), publishes status changes to subscribers (contacts), manages typing indicators (ephemeral, TTL 10s).
- **Media Service**: multipart upload (chunks), thumbnail generation via pipeline (client-created or encrypted preview), S3 storage with lifecycle (Glacier after 30d, delete after 1y). Resumable uploads.
- **Call Signaling Service**: relay SDP/ICE between peers, no RTP/SRTP (P2P). TURN fallback (relay media, ~5-10%). Call queueing/waiting support.
- **Push Service**: FCM/APNS integration, message collapsing (last msg when multiple pending), priority channels, device token management, retry with backoff.
- **Group Service**: membership management, invite links (UUID+TTL), admin actions, group key sync on membership changes.

**Domain models:**
- **Message**: id (UUID), senderId, recipientId/groupId, encryptedContent, timestamp, status (PENDING/SENT/DELIVERED/READ), mediaUrl, thumbnailUrl, mediaKey, expiresAt (disappearing).
- **Chat**: id, participants[], lastMessage, unreadCount, muteUntil, isPinned, createdAt, updatedAt.
- **User**: id, phoneNumber, publicKey (Signal identity), deviceId[], lastSeen, status, profilePhoto.
- **Group**: id, name, adminIds[], memberIds[], createdAt, inviteLink (UUID+TTL), settings.
- **Receipt**: messageId, userId, type (DELIVERED/READ), timestamp.

**Data storage:**
- **Cassandra (Messages)**: partition (userId, YYYYMM), clustering timestamp DESC. Encrypted messages, TTL 30d for delivered, messageId index for receipts. RF=3, eventual consistency.
- **PostgreSQL (Users, Groups)**: strong consistency for metadata. Indexes on phoneNumber, userId. Master-slave replication.
- **Redis (Presence, Typing)**: keys: `presence:{userId}` (TTL 45s), `typing:{chatId}:{userId}` (TTL 10s). Pub/Sub for real-time.
- **S3 (Media)**: per-region buckets, lifecycle (Standard → Glacier → Delete), pre-signed URLs (TTL 1h). CDN (CloudFront) caching.

**E2EE and Signal Protocol:**
- **Identity Keys**: long-term ed25519 for device auth. Published on registration, validated via QR safety numbers.
- **Pre-Keys**: one-time ECDH keys (batch of 100), used for offline user session init. Replenished on exhaustion.
- **Session Ratchet (Double Ratchet)**: DH ratchet for session key update per exchange, symmetric ratchet for forward secrecy. Supports out-of-order delivery.
- **Group Sessions**: sender key per participant, distributed via pairwise sessions. Full re-key on membership changes.
- **Device Verification**: QR safety number = hash(identityKey_A || identityKey_B), compare for MITM protection. Notifications on key changes.

**Consistency and delivery:**
- **At-least-once**: client resends until ack, server deduplicates by messageId. Idempotency tokens.
- **Ordered delivery**: server-side timestamp, client sorts by timestamp+messageId. For groups: vector clocks for causal ordering.
- **Offline queueing**: server stores 30d, client syncs via batch fetch (last_sync_timestamp). Push to wake client.
- **Read receipts**: optional (user can disable), sent only after screen render. Batch receipts for groups.

**Media pipeline:**
- **Compression (client)**: JPEG 85% (resize ≤1600px), H.264/HEVC (~1Mbps), Opus for voice.
- **Chunked upload**: multipart (5MB chunks), resumable, parallel chunks.
- **Thumbnail generation**: client-encrypted thumbnail (100x100), instant preview. Server blind to plaintext.
- **CDN caching**: popular media in CloudFront, reduced S3 load, pre-signed URLs (TTL 1h).
- **Progressive download**: streaming video before full download, range requests for seek.

**Voice/video calls:**
- **Signaling**: SDP via Chat Service (offer/answer/candidates). ICE gathering for P2P.
- **Media transport**: WebRTC with SRTP, P2P (80-90%), TURN relay (5-10%).
- **Adaptive bitrate**: dynamic quality based on RTT/packet loss. Video → voice on poor network.
- **Group calls**: SFU (Selective Forwarding Unit), each sends one stream, receives N-1. SVC for per-participant quality.
- **Call queueing**: missed call notification, history, callback.

**Resilience:**
- **WS → Long polling fallback**: 30s timeout, return to WS on recovery. Ping/pong health check.
- **Multi-region**: primary by geo (low latency), cross-region replication for DR. Auto-failover.
- **Message retry**: exponential backoff (1s-5min), jitter. Mark failed after 24h.
- **Circuit breaker**: to FCM/CDN, states CLOSED/OPEN/HALF_OPEN, timeout 30-60s.
- **Graceful degradation**: presence failure → hide online status, messages continue. Media failure → retry UI.

**Security and privacy:**
- **Zero-knowledge server**: blind to plaintext messages/media, stores only encrypted blobs.
- **Sealed Sender**: hide sender metadata from server via onion encryption, server knows only recipient.
- **Forward secrecy**: ratchet updates session keys, old key compromise doesn't reveal past messages.
- **Device attestation**: SafetyNet/Play Integrity for client integrity, block rooted/modded devices.
- **Rate limiting**: per user (100 msg/min, 50 media/min), per IP (1000 conn), Redis distributed counter. Ban on abuse.

**Observability and SLOs:**
- **Metrics**: P50/P95/P99 message latency (send → delivered, target <200ms P95), delivery success (>99.9%), WS uptime (>99.95%), media upload (<5s P95), call connection (>95%).
- **Distributed tracing**: OpenTelemetry for message journey: client → LB → Chat → Kafka → recipient. Span tags: userId, messageId, chatId.
- **SLO alerting**: PagerDuty/Opsgenie. Alert if latency_p95 > 500ms for 5min OR success < 99.5% for 10min OR uptime < 99.9%.
- **Logging**: structured JSON, PII masking, retention 30d hot, 1y cold (Splunk/ELK).

**Scalability:**
- **Sharding**: Chat Service by userId hash (consistent hashing), independent scaling. Cassandra partition by userId.
- **Connection pooling**: WS gateways (stateful), horizontal scale with sticky sessions (L4/L7 LB).
- **Read replicas**: PostgreSQL master-slave, Cassandra RF=3 for nearest datacenter reads.
- **Message queue**: Kafka for async (push, analytics), partition by userId, retention 7d.
- **CDN for media**: CloudFront/Cloudflare, edge caching, 90%+ origin load reduction.
- **Auto-scaling**: Kubernetes HPA on connection count (WS gateways), queue depth (Chat workers), CPU/memory (stateless).

### Optimization
- Battery: 30s heartbeat, coalesce push, increased WS keep-alive interval in background.
- Network: protobuf compression, batch receipts, delta sync (only new since last_sync), preload frequent contacts.
- Memory: message pagination (20-50), lazy load media, LRU cache for decoded images.

### Offline
- Local DB (Room/SQLite) for messages/contacts, pending sends queue, sync on online, conflict resolution (server wins metadata, merge messages).

**See also:** [[c-websockets]], [[c-message-queue]]


## Follow-ups
- How to implement disappearing messages with E2EE?
- How to handle group key distribution at scale (1000+ members)?
- How to design multi-device sync while preserving E2EE?

## References
- https://signal.org/docs/specifications/doubleratchet/
- https://developer.android.com/training/sync-adapters
- https://webrtc.org/
- https://cassandra.apache.org/doc/latest/

## Related Questions
- [[q-design-instagram-stories--android--hard]]
- [[q-data-sync-unstable-network--android--hard]]
- [[q-database-encryption-android--android--medium]]
