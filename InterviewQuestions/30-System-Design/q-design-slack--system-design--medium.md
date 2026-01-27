---
id: q-design-slack
title: Design Slack (Team Messaging)
aliases:
- Design Slack
- Team Messaging Platform
- Workplace Chat
topic: system-design
subtopics:
- design-problems
- messaging
- real-time
- collaboration
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-whatsapp--system-design--hard
- q-websockets-sse-long-polling--system-design--medium
- q-message-queues-event-driven--system-design--medium
- q-pubsub-patterns--system-design--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- design-problems
- difficulty/medium
- messaging
- real-time
- system-design
anki_cards:
- slug: q-design-slack-0-en
  anki_id: null
  synced_at: null
- slug: q-design-slack-0-ru
  anki_id: null
  synced_at: null
---
# Question (EN)
> How would you design a team messaging platform like Slack?

# Vopros (RU)
> Как бы вы спроектировали платформу командного обмена сообщениями, подобную Slack?

---

## Answer (EN)

### Requirements

**Functional**:
- Channels (public/private) and direct messages
- Real-time message delivery
- Message threads and replies
- Presence indicators (online/away/DND)
- File sharing and media preview
- @mentions and notifications
- Message search and history
- Workspace and organization hierarchy
- Integrations and bots (Slack Apps)

**Non-functional**:
- <200ms message delivery latency
- 99.99% availability
- Support millions of concurrent users
- Messages must be persistent and searchable
- Cross-device sync

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Web / Mobile / Desktop Clients             │
│                (Persistent WebSocket connection)            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    API Gateway / Load Balancer              │
│              (Authentication, Rate limiting)                │
└─────────────────────────┬───────────────────────────────────┘
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
│  WebSocket  │    │    REST     │    │   Search    │
│   Service   │    │   Service   │    │   Service   │
│ (Real-time) │    │   (CRUD)    │    │(Elasticsearch)│
└──────┬──────┘    └──────┬──────┘    └─────────────┘
       │                  │
       └────────┬─────────┘
                │
┌───────────────▼─────────────────────────────────────────────┐
│                     Message Service                          │
│        (Routing, fan-out, delivery guarantees)              │
└───────┬───────────────┬───────────────┬─────────────────────┘
        │               │               │
  ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
  │  Channel  │   │   User    │   │   File    │
  │  Service  │   │  Service  │   │  Service  │
  └───────────┘   └───────────┘   └───────────┘
```

### Data Models

```
Workspace:
┌─────────────────────────────────────┐
│ workspace_id (UUID)                 │
│ name, domain                        │
│ settings (JSON)                     │
│ created_at                          │
└─────────────────────────────────────┘

Channel:
┌─────────────────────────────────────┐
│ channel_id (UUID)                   │
│ workspace_id                        │
│ name, description                   │
│ type (public/private/dm)            │
│ created_by                          │
│ created_at                          │
└─────────────────────────────────────┘

Message:
┌─────────────────────────────────────┐
│ message_id (UUID)                   │
│ channel_id                          │
│ user_id                             │
│ content (text)                      │
│ thread_ts (parent message ID)       │
│ attachments (JSON)                  │
│ reactions (JSON)                    │
│ edited_at                           │
│ created_at                          │
└─────────────────────────────────────┘

Sharding: By workspace_id or channel_id
```

### Real-Time Message Delivery

```
WebSocket Connection Flow:
1. Client connects → Authenticate via token
2. Subscribe to channels user belongs to
3. Server pushes messages to subscribed connections

Message Send Flow:
┌────────┐   POST    ┌────────┐   Queue   ┌─────────┐
│ Client │ ───────→  │  API   │ ───────→  │ Message │
└────────┘           └────────┘           │ Service │
                                          └────┬────┘
                                               │
                     ┌─────────────────────────┼─────────────────────┐
                     │                         │                     │
               ┌─────▼─────┐            ┌──────▼──────┐       ┌──────▼──────┐
               │   Store   │            │  Pub/Sub    │       │   Index     │
               │  in DB    │            │  (Redis)    │       │(Elasticsearch)│
               └───────────┘            └──────┬──────┘       └─────────────┘
                                               │
                                    ┌──────────┼──────────┐
                                    │          │          │
                              ┌─────▼────┐ ┌───▼────┐ ┌───▼────┐
                              │ WS Node 1│ │ WS Node 2│ │ WS Node N│
                              └─────┬────┘ └────┬───┘ └────┬───┘
                                    │          │          │
                                    ▼          ▼          ▼
                                 Clients    Clients    Clients
```

### Channel Membership & Fan-out

```
Two approaches for message delivery:

1. Small channels (<1000 members):
   - Fan-out on write: Push to all member connections
   - Use Redis Pub/Sub per channel
   - Low latency, higher memory

2. Large channels (>1000 members):
   - Fan-out on read: Store once, clients poll/fetch
   - Pagination for history
   - Lower memory, slightly higher latency

Slack hybrid: Most channels < 100 members → Fan-out on write
```

### Presence System

```
┌─────────────────────────────────────────────────────────────┐
│                   Presence Service                          │
│  (Tracks online/away/DND status per user per workspace)    │
└─────────────────────────────────────────────────────────────┘

Heartbeat mechanism:
- Client sends heartbeat every 30s
- No heartbeat for 60s → Mark as away
- No heartbeat for 5min → Mark as offline

Status storage:
- Redis HSET: presence:{workspace_id} → {user_id: status, last_seen}
- Expire keys after 10 minutes

Presence updates:
- Broadcast to channel members via Pub/Sub
- Batch updates to reduce traffic
```

### Threading Model

```
Thread structure:
┌─────────────────────────────────┐
│ Parent Message (thread_ts=null) │
│ message_id: "1706234567.001234" │
│ reply_count: 5                  │
│ last_reply: "1706234890.001238" │
└───────────────┬─────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼───────────────┐  ┌────▼──────────────┐
│ Reply 1           │  │ Reply 2           │
│ thread_ts=parent  │  │ thread_ts=parent  │
└───────────────────┘  └───────────────────┘

- Threads are identified by parent message timestamp
- Replies stored with thread_ts pointing to parent
- Channel shows only parent messages + unread thread indicator
```

### Search Architecture

```
┌────────────┐      ┌────────────────────────────────────────┐
│   Client   │ ──→  │          Search Service                │
└────────────┘      └──────────────┬─────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │     Elasticsearch Cluster    │
                    │   (Sharded by workspace_id) │
                    └──────────────────────────────┘

Indexed fields:
- message content (full-text)
- sender name, channel name
- file names, file content (for docs)
- timestamp (range queries)

Features:
- Autocomplete for channels/users
- Filters: from:, in:, before:, after:
- Highlighting matched terms
```

### File Sharing

```
Upload flow:
1. Client requests upload URL → Presigned S3 URL
2. Client uploads directly to S3
3. S3 triggers Lambda for processing
4. Lambda: thumbnail, virus scan, index
5. File metadata stored in DB
6. Message with attachment created

Storage:
- S3 for files (with lifecycle policies)
- CDN for delivery (CloudFront)
- Metadata in PostgreSQL
- Thumbnails cached in Redis
```

### Notifications

```
┌─────────────────────────────────────────────────────────────┐
│                  Notification Service                        │
└───────────────┬───────────────────────────────┬─────────────┘
                │                               │
        ┌───────▼───────┐               ┌───────▼───────┐
        │  Push (FCM/   │               │    Email      │
        │    APNs)      │               │   Service     │
        └───────────────┘               └───────────────┘

Logic:
- @mention → Always notify
- Channel message → Notify if preferences allow
- DM → Notify unless muted
- User online in channel → Skip push, show in-app only
- Batch notifications after 5 minutes if multiple

Delivery modes:
1. In-app: WebSocket push
2. Push: Mobile (FCM/APNs)
3. Email: Digest for missed messages
```

### Key Technical Decisions

| Aspect | Decision | Reason |
|--------|----------|--------|
| Real-time | WebSocket + Redis Pub/Sub | Low latency, scalable |
| Database | PostgreSQL (sharded) | ACID, JSON support |
| Search | Elasticsearch | Full-text, faceted search |
| Cache | Redis | Presence, channel metadata |
| Queue | Kafka | Message ordering, replay |
| Files | S3 + CDN | Scalable, cost-effective |
| API | REST + WebSocket | CRUD + real-time |

### Scale Considerations

```
Slack numbers (approximate):
- 20M+ daily active users
- 750K+ organizations
- 1.5B+ messages/week
- Petabytes of files

Scaling strategies:
- Shard by workspace_id (isolation)
- Connection servers: horizontal scale
- Message fanout: async via Kafka
- Search: separate Elasticsearch cluster
- Files: S3 with tiered storage
```

---

## Otvet (RU)

### Требования

**Функциональные**:
- Каналы (публичные/приватные) и личные сообщения
- Доставка сообщений в реальном времени
- Треды и ответы на сообщения
- Индикаторы присутствия (онлайн/отошёл/не беспокоить)
- Обмен файлами и превью медиа
- @упоминания и уведомления
- Поиск и история сообщений
- Иерархия рабочих пространств и организаций
- Интеграции и боты (Slack Apps)

**Нефункциональные**:
- <200мс задержка доставки сообщений
- 99.99% доступность
- Поддержка миллионов одновременных пользователей
- Сообщения должны быть постоянными и доступными для поиска
- Синхронизация между устройствами

### Высокоуровневая архитектура

```
┌─────────────────────────────────────────────────────────────┐
│              Web / Mobile / Desktop клиенты                 │
│              (Постоянное WebSocket соединение)              │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                API Gateway / Load Balancer                   │
│              (Аутентификация, Rate limiting)                │
└─────────────────────────┬───────────────────────────────────┘
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
│  WebSocket  │    │    REST     │    │   Search    │
│   Service   │    │   Service   │    │   Service   │
│(Real-time)  │    │   (CRUD)    │    │(Elasticsearch)│
└─────────────┘    └─────────────┘    └─────────────┘
```

### Модели данных

```
Workspace:
┌─────────────────────────────────────┐
│ workspace_id (UUID)                 │
│ name, domain                        │
│ settings (JSON)                     │
│ created_at                          │
└─────────────────────────────────────┘

Channel:
┌─────────────────────────────────────┐
│ channel_id (UUID)                   │
│ workspace_id                        │
│ name, description                   │
│ type (public/private/dm)            │
│ created_by, created_at              │
└─────────────────────────────────────┘

Message:
┌─────────────────────────────────────┐
│ message_id (UUID)                   │
│ channel_id, user_id                 │
│ content (text)                      │
│ thread_ts (ID родительского сообщения)│
│ attachments, reactions (JSON)       │
│ created_at                          │
└─────────────────────────────────────┘

Шардинг: По workspace_id или channel_id
```

### Доставка сообщений в реальном времени

```
Поток WebSocket соединения:
1. Клиент подключается → Аутентификация по токену
2. Подписка на каналы пользователя
3. Сервер пушит сообщения подписанным соединениям

Поток отправки сообщения:
Клиент → API → Message Service → {DB + Pub/Sub + Search}
                                        │
                              WS ноды → Клиенты
```

### Система присутствия

```
Механизм heartbeat:
- Клиент отправляет heartbeat каждые 30с
- Нет heartbeat 60с → Пометить как "отошёл"
- Нет heartbeat 5мин → Пометить как оффлайн

Хранение статуса:
- Redis HSET: presence:{workspace_id} → {user_id: status}
- Expire ключей через 10 минут

Обновления присутствия:
- Broadcast участникам канала через Pub/Sub
- Batch обновления для снижения трафика
```

### Модель тредов

```
Структура треда:
┌─────────────────────────────────┐
│ Родительское сообщение          │
│ (thread_ts=null)                │
│ reply_count: 5                  │
└───────────────┬─────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼────────────┐    ┌─────▼──────────┐
│ Ответ 1        │    │ Ответ 2        │
│ thread_ts=parent│   │ thread_ts=parent│
└────────────────┘    └────────────────┘

- Треды идентифицируются по timestamp родителя
- Ответы хранятся с thread_ts, указывающим на родителя
- Канал показывает только родительские сообщения
```

### Архитектура поиска

```
┌────────────┐      ┌────────────────────────────────────────┐
│   Клиент   │ ──→  │           Search Service               │
└────────────┘      └──────────────┬─────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Elasticsearch Cluster     │
                    │  (Шардинг по workspace_id)  │
                    └──────────────────────────────┘

Индексируемые поля:
- Контент сообщения (полнотекстовый)
- Имя отправителя, название канала
- Имена файлов, содержимое документов
- Timestamp (range запросы)

Фильтры: from:, in:, before:, after:
```

### Обмен файлами

```
Поток загрузки:
1. Клиент запрашивает URL → Presigned S3 URL
2. Клиент загружает напрямую в S3
3. S3 триггерит Lambda для обработки
4. Lambda: превью, антивирус, индексация
5. Метаданные файла сохраняются в БД
6. Создаётся сообщение с вложением

Хранение:
- S3 для файлов (с lifecycle policies)
- CDN для доставки (CloudFront)
- Метаданные в PostgreSQL
```

### Уведомления

```
Логика:
- @упоминание → Всегда уведомлять
- Сообщение в канале → Уведомлять по настройкам
- Личное сообщение → Уведомлять если не muted
- Пользователь онлайн в канале → Только in-app

Режимы доставки:
1. In-app: WebSocket push
2. Push: Мобильные (FCM/APNs)
3. Email: Дайджест пропущенных сообщений
```

### Ключевые технические решения

| Аспект | Решение | Причина |
|--------|---------|---------|
| Real-time | WebSocket + Redis Pub/Sub | Низкая задержка, масштабируемость |
| База данных | PostgreSQL (шардированный) | ACID, поддержка JSON |
| Поиск | Elasticsearch | Полнотекстовый поиск, фасеты |
| Кэш | Redis | Присутствие, метаданные каналов |
| Очередь | Kafka | Ordering сообщений, replay |
| Файлы | S3 + CDN | Масштабируемость, экономичность |

### Масштабирование

```
Числа Slack (приблизительно):
- 20M+ ежедневных активных пользователей
- 750K+ организаций
- 1.5B+ сообщений/неделя
- Петабайты файлов

Стратегии масштабирования:
- Шардинг по workspace_id (изоляция)
- Connection серверы: горизонтальное масштабирование
- Message fanout: асинхронно через Kafka
- Поиск: отдельный Elasticsearch кластер
- Файлы: S3 с tiered storage
```

---

## Follow-ups

- How do you handle message ordering across distributed WebSocket servers?
- How would you design Slack's real-time collaborative editing (like Slack Canvas)?
- How do you implement efficient unread message counters per channel?
- How would you design the integration/bot platform (Slack Apps)?
- How do you handle workspace data isolation for enterprise customers?
