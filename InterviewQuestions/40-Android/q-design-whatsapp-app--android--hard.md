---
id: 20251020-200000
title: Design WhatsApp App / Проектирование приложения WhatsApp
aliases: [Design WhatsApp App, Проектирование приложения WhatsApp, WhatsApp Architecture, Архитектура WhatsApp]
topic: android
subtopics: [files-media, networking-http, service]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-data-sync-unstable-network--android--hard, q-database-encryption-android--android--medium]
sources: [https://signal.org/docs/specifications/doubleratchet/]
created: 2025-10-20
updated: 2025-10-28
tags: [android/files-media, android/networking-http, android/service, difficulty/hard, e2ee, messaging, realtime, websocket]
---
# Вопрос (RU)
> Как спроектировать мессенджер WhatsApp для Android?

# Question (EN)
> How to design WhatsApp for Android?

---

## Ответ (RU)

WhatsApp включает обмен сообщениями 1-to-1/группы, медиа, статусы доставки/прочтения, E2EE (Signal Protocol), голос/видео-звонки, офлайн-персистентность.

### Требования
**Функциональные:** сообщения (текст, медиа, голосовые), группы, статусы (sent/delivered/read), безопасность (E2EE, device verification), присутствие (online/offline, last seen), push (FCM), звонки (WebRTC, STUN/TURN).

**Нефункциональные:** низкая латентность (<200ms P95), высокая доступность, масштабируемость (миллиарды msg/день), конфиденциальность (zero-knowledge server), бережная батарея/трафик, офлайн.

### Архитектура (высокоуровнево)
Android клиент (Room DB, E2EE engine, WebSocket, media cache) → Load Balancer → микросервисы (Chat/Presence/Media/Call Signaling/Push) → Kafka, Cassandra (messages), PostgreSQL (users), S3+CDN (media), Redis (presence).

### Клиент Android: Ключевые Потоки
1. **Отправка:** шифрование Signal Protocol (ratchet) → локальная запись (pending) → WebSocket send → ack от сервера (delivered) → receipt от получателя (read).
2. **Получение:** WebSocket → расшифровка → Room DB → UI update → отправка read receipt.
3. **Медиа:** сжатие (JPEG/H.264) → upload на CDN → отправка URL+thumbnail+decryption key → ленивая загрузка.
4. **Офлайн:** очередь unsent → хранение до 30 дней → ресенд при онлайне → backoff при ошибках.
5. **Группы:** sender keys (pairwise sessions → group sessions) → рэтчет при изменении состава → forward secrecy.
6. **Звонки:** WebRTC SDP negotiation через Signal Server → ICE candidates → STUN/TURN fallback → адаптивный bitrate.

```kotlin
// ✅ Signal Protocol usage
val session = SessionBuilder(recipientAddress).buildSenderSession()
val ciphertext = SessionCipher(session).encrypt(plaintext.toByteArray())

// ✅ WebSocket send with ack
ws.send(MessageProto(id, encrypted, timestamp))
ackFlow.first { it.msgId == id }

// ✅ Offline queue
if (!networkAvailable) {
    db.insertPending(msg)
} else {
    sendAndRetry(msg)
}
```

### Сервер: Маршрутизация
- **Chat Service:** маршрутизация по userId, хранение зашифрованных сообщений (server не видит plaintext), доставка через WebSocket или push, удаление после доставки (TTL 30 дней).
- **Presence Service:** heartbeat каждые 30s, кэш в Redis, pub/sub для обновлений контактов.
- **Media Service:** multipart upload, генерация thumbnails, CDN доставка, E2EE ключ в metadata.
- **Call Signaling:** relay SDP/ICE candidates, не участвует в медиа-потоке (P2P через WebRTC).
- **Push Service:** FCM integration, приоритизация (high для звонков, normal для сообщений).

### E2EE и Signal Protocol
- **Identity Keys:** долгосрочные ed25519 ключи для аутентификации устройств, валидация через QR-код safety numbers.
- **Pre-Keys:** одноразовые ECDH ключи (пачка из 100), инициация сессии с оффлайн-пользователем.
- **Double Ratchet:** DH ratchet для обновления session key, symmetric ratchet для forward secrecy, поддержка out-of-order доставки.
- **Group Sessions:** каждый участник имеет sender key, распределяется через pairwise sessions, полный re-key при изменении состава.

### Хранение данных
- **Cassandra (Messages):** partition (userId, YYYYMM), clustering timestamp DESC, зашифрованные сообщения, TTL 30d, RF=3, eventual consistency.
- **PostgreSQL (Users, Groups):** strong consistency для metadata, индексы на phoneNumber/userId, master-slave replication.
- **Redis (Presence):** `presence:{userId}` (TTL 45s), `typing:{chatId}:{userId}` (TTL 10s), Pub/Sub для real-time.
- **S3 (Media):** lifecycle (Standard → Glacier → Delete), pre-signed URLs (TTL 1h), CloudFront CDN caching.

### Доставка
- **At-least-once:** клиент ресендит до ack, сервер дедуплицирует по messageId, idempotency tokens.
- **Ordered delivery:** server-side timestamp, клиент сортирует по timestamp+messageId, для групп: vector clocks для causal ordering.
- **Offline queueing:** сервер хранит 30d, клиент синхронизирует batch fetch (last_sync_timestamp), push notification для пробуждения.

### Масштабирование
- **Sharding:** Chat Service по userId hash (consistent hashing), Cassandra partition по userId.
- **Connection pooling:** WebSocket gateways (stateful), горизонтальное масштабирование со sticky sessions.
- **Read replicas:** PostgreSQL master-slave, Cassandra RF=3 для чтения из nearest datacenter.
- **Message queue:** Kafka для async (push, analytics), partition по userId, retention 7d.
- **Auto-scaling:** Kubernetes HPA на базе connection count (WS gateways), queue depth (Chat workers).

### Оптимизация
- **Батарея:** heartbeat каждые 30s, coalesce push, WebSocket keep-alive с увеличенным интервалом в фоне.
- **Сеть:** protobuf для сжатия, batch receipts, delta sync (только новые сообщения с last_sync), предзагрузка частых контактов.
- **Память:** message pagination (20-50 сообщений), lazy load медиа, LRU cache для декодированных изображений.

### Офлайн
Room/SQLite для сообщений/контактов, очередь pending sends, синхронизация при онлайне, conflict resolution (server wins для metadata, merge для messages).

## Answer (EN)

WhatsApp involves 1-to-1/group messaging, media, delivery/read statuses, E2EE (Signal Protocol), voice/video calls, offline persistence.

### Requirements
**Functional:** messaging (text, media, voice), groups, statuses (sent/delivered/read), security (E2EE, device verification), presence (online/offline, last seen), push (FCM), calls (WebRTC, STUN/TURN).

**Non-functional:** low latency (<200ms P95), high availability, scale (billions msg/day), privacy (zero-knowledge server), battery/bandwidth efficiency, offline support.

### Architecture (high-level)
Android client (Room DB, E2EE engine, WebSocket, media cache) → Load Balancer → microservices (Chat/Presence/Media/Call Signaling/Push) → Kafka, Cassandra (messages), PostgreSQL (users), S3+CDN (media), Redis (presence).

### Android Client Key Flows
1. **Send:** encrypt Signal Protocol (ratchet) → local store (pending) → WS send → server ack (delivered) → recipient receipt (read).
2. **Receive:** WS → decrypt → Room DB → UI update → send read receipt.
3. **Media:** compress (JPEG/H.264) → upload to CDN → send URL+thumbnail+decryption key → lazy load.
4. **Offline:** queue unsent → store 30 days → resend on online → backoff on errors.
5. **Groups:** sender keys (pairwise → group sessions) → ratchet on membership changes → forward secrecy.
6. **Calls:** WebRTC SDP via Signal Server → ICE candidates → STUN/TURN fallback → adaptive bitrate.

### Server Routing
- **Chat Service:** route by userId, store encrypted (server blind to plaintext), deliver via WS or push if offline, delete after delivery (TTL 30d).
- **Presence Service:** heartbeat 30s, Redis cache, pub/sub for contact updates.
- **Media Service:** multipart upload, thumbnail gen, CDN delivery, E2EE key in metadata.
- **Call Signaling:** relay SDP/ICE, no media (P2P WebRTC).
- **Push Service:** FCM integration, prioritization (high for calls, normal for messages).

### E2EE and Signal Protocol
- **Identity Keys:** long-term ed25519 for device auth, validated via QR safety numbers.
- **Pre-Keys:** one-time ECDH keys (batch of 100), used for offline user session init.
- **Double Ratchet:** DH ratchet for session key update, symmetric ratchet for forward secrecy, supports out-of-order delivery.
- **Group Sessions:** sender key per participant, distributed via pairwise sessions, full re-key on membership changes.

### Data Storage
- **Cassandra (Messages):** partition (userId, YYYYMM), clustering timestamp DESC, encrypted messages, TTL 30d, RF=3, eventual consistency.
- **PostgreSQL (Users, Groups):** strong consistency for metadata, indexes on phoneNumber/userId, master-slave replication.
- **Redis (Presence):** `presence:{userId}` (TTL 45s), `typing:{chatId}:{userId}` (TTL 10s), Pub/Sub for real-time.
- **S3 (Media):** lifecycle (Standard → Glacier → Delete), pre-signed URLs (TTL 1h), CloudFront CDN caching.

### Delivery
- **At-least-once:** client resends until ack, server deduplicates by messageId, idempotency tokens.
- **Ordered delivery:** server-side timestamp, client sorts by timestamp+messageId, for groups: vector clocks for causal ordering.
- **Offline queueing:** server stores 30d, client syncs via batch fetch (last_sync_timestamp), push to wake client.

### Scalability
- **Sharding:** Chat Service by userId hash (consistent hashing), Cassandra partition by userId.
- **Connection pooling:** WS gateways (stateful), horizontal scale with sticky sessions.
- **Read replicas:** PostgreSQL master-slave, Cassandra RF=3 for nearest datacenter reads.
- **Message queue:** Kafka for async (push, analytics), partition by userId, retention 7d.
- **Auto-scaling:** Kubernetes HPA on connection count (WS gateways), queue depth (Chat workers).

### Optimization
- **Battery:** 30s heartbeat, coalesce push, increased WS keep-alive interval in background.
- **Network:** protobuf compression, batch receipts, delta sync (only new since last_sync), preload frequent contacts.
- **Memory:** message pagination (20-50), lazy load media, LRU cache for decoded images.

### Offline
Room/SQLite for messages/contacts, pending sends queue, sync on online, conflict resolution (server wins metadata, merge messages).

---

## Follow-ups
- How to implement disappearing messages with E2EE?
- How to handle group key distribution at scale (1000+ members)?
- How to design multi-device sync while preserving E2EE?
- How to optimize battery consumption for background WebSocket connections?
- How to implement message search with E2EE (encrypted at rest)?

## References
- [Signal Protocol - Double Ratchet](https://signal.org/docs/specifications/doubleratchet/)
- [WebRTC Documentation](https://webrtc.org/)
- [Cassandra Documentation](https://cassandra.apache.org/doc/latest/)
- [Android Sync Adapters](https://developer.android.com/training/sync-adapters)

## Related Questions

### Prerequisites (Easier)
- [[q-database-encryption-android--android--medium]]
- [[q-deep-link-vs-app-link--android--medium]]

### Related (Same Level)
- [[q-data-sync-unstable-network--android--hard]]
- [[q-design-instagram-stories--android--hard]]

### Advanced (Harder)
- [[q-design-instagram-stories--android--hard]]
