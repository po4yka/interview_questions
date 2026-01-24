---
id: sysdes-048
title: Design WhatsApp
aliases:
- Design WhatsApp
- Messaging System
- Chat Application
topic: system-design
subtopics:
- design-problems
- messaging
- real-time
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
- q-message-queues--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- design-problems
- difficulty/hard
- messaging
- system-design
anki_cards:
- slug: sysdes-048-0-en
  language: en
  anki_id: 1769159522594
  synced_at: '2026-01-23T13:49:17.867620'
- slug: sysdes-048-0-ru
  language: ru
  anki_id: 1769159522619
  synced_at: '2026-01-23T13:49:17.868802'
---
# Question (EN)
> Design a messaging system like WhatsApp. Focus on 1:1 messaging, group chats, and message delivery guarantees.

# Vopros (RU)
> Спроектируйте систему сообщений типа WhatsApp. Фокус на 1:1 сообщениях, групповых чатах и гарантиях доставки.

---

## Answer (EN)

### Requirements

**Functional**: 1:1 chat, group chat (up to 256), online status, read receipts, media sharing
**Non-functional**: <100ms delivery, E2E encryption, offline support, 2B+ users

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Mobile Clients                          │
│              (Persistent WebSocket connection)              │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Connection Gateway                         │
│     (Manages WebSocket connections, routes messages)       │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Message Service                           │
│         (Handles delivery logic, fan-out)                  │
└─────────┬───────────────┬───────────────┬───────────────────┘
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  Message  │   │   User    │   │  Group    │
    │  Queue    │   │  Service  │   │  Service  │
    └───────────┘   └───────────┘   └───────────┘
```

### Message Flow (1:1)

```
Sender → Gateway → Message Service → Store in DB
                         │
                         ↓ (if recipient online)
              Recipient's Gateway → Recipient

If recipient offline:
- Message stored in "pending" queue
- On reconnect: deliver pending messages
- After delivery: message marked as delivered
```

### Message States

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   SENT   │ → │ DELIVERED│ → │   READ   │ → │ EXPIRED  │
│  (✓)     │    │  (✓✓)    │    │  (✓✓ blue)│   │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘

- SENT: Server received, stored
- DELIVERED: Recipient device received
- READ: Recipient opened conversation
```

### Group Chat Fan-out

```
Two strategies:

1. Fan-out on Write (small groups):
   - Write to each member's inbox
   - Fast reads, expensive writes
   - Good for groups < 100

2. Fan-out on Read (large groups):
   - Write once to group inbox
   - Read fetches from group
   - Good for groups > 100

WhatsApp limit: 256 members → Fan-out on Write
```

### Message Storage

```
Schema (simplified):
┌─────────────────────────────────────┐
│ messages                            │
├─────────────────────────────────────┤
│ message_id    (UUID)                │
│ conversation_id                     │
│ sender_id                           │
│ content       (encrypted)           │
│ timestamp                           │
│ status        (sent/delivered/read) │
└─────────────────────────────────────┘

Sharding: By conversation_id
Retention: Keep N days or until delivered
```

### Key Technical Decisions

| Aspect | Decision | Reason |
|--------|----------|--------|
| Connection | WebSocket | Low latency, bidirectional |
| Protocol | Custom binary | Bandwidth efficient |
| Encryption | E2E (Signal) | Privacy |
| Storage | Sharded MySQL | WhatsApp's actual choice |
| Media | CDN + presigned URLs | Offload from servers |

### Scale

```
WhatsApp numbers:
- 2B+ users
- 100B+ messages/day
- ~50 engineers (famously lean)
- Erlang backend (high concurrency)
```

---

## Otvet (RU)

### Требования

**Функциональные**: 1:1 чат, групповой чат (до 256), онлайн статус, отметки о прочтении
**Нефункциональные**: <100мс доставка, E2E шифрование, офлайн поддержка, 2B+ пользователей

### Поток сообщения (1:1)

```
Отправитель → Gateway → Message Service → Сохранить в БД
                             │
                             ↓ (если получатель онлайн)
                  Gateway получателя → Получатель

Если получатель офлайн:
- Сообщение хранится в "pending" очереди
- При reconnect: доставить pending сообщения
- После доставки: сообщение помечено как доставлено
```

### Состояния сообщения

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│   SENT   │ → │ DELIVERED│ → │   READ   │
│  (✓)     │    │  (✓✓)    │    │  (✓✓ синие)│
└──────────┘    └──────────┘    └──────────┘

- SENT: Сервер получил, сохранил
- DELIVERED: Устройство получателя получило
- READ: Получатель открыл диалог
```

### Fan-out групповых чатов

```
Две стратегии:

1. Fan-out on Write (маленькие группы):
   - Записать в inbox каждого участника
   - Быстрое чтение, дорогая запись
   - Хорошо для групп < 100

2. Fan-out on Read (большие группы):
   - Записать один раз в inbox группы
   - Чтение из группы
   - Хорошо для групп > 100

Лимит WhatsApp: 256 участников → Fan-out on Write
```

### Ключевые технические решения

| Аспект | Решение | Причина |
|--------|---------|---------|
| Соединение | WebSocket | Низкая задержка, двунаправленность |
| Протокол | Custom binary | Экономия bandwidth |
| Шифрование | E2E (Signal) | Приватность |
| Storage | Sharded MySQL | Реальный выбор WhatsApp |
| Media | CDN + presigned URLs | Разгрузить серверы |

### Масштаб

```
Числа WhatsApp:
- 2B+ пользователей
- 100B+ сообщений/день
- ~50 инженеров (знаменито lean)
- Erlang backend (высокий concurrency)
```

---

## Follow-ups

- How does end-to-end encryption work in WhatsApp?
- How do you handle message ordering in distributed systems?
- How do you design typing indicators and online status?
