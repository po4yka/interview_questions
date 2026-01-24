---
id: sysdes-026
title: WebSockets vs SSE vs Long Polling
aliases:
- WebSockets
- Server-Sent Events
- Long Polling
- Real-time Communication
topic: system-design
subtopics:
- communication
- real-time
- protocols
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-rest-api-design-best-practices--system-design--medium
- q-pubsub-patterns--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- communication
- difficulty/medium
- real-time
- system-design
anki_cards:
- slug: sysdes-026-0-en
  language: en
  anki_id: 1769158890641
  synced_at: '2026-01-23T13:49:17.753178'
- slug: sysdes-026-0-ru
  language: ru
  anki_id: 1769158890665
  synced_at: '2026-01-23T13:49:17.754771'
---
# Question (EN)
> What are the differences between WebSockets, Server-Sent Events, and Long Polling? When would you use each?

# Vopros (RU)
> В чем разница между WebSockets, Server-Sent Events и Long Polling? Когда использовать каждый?

---

## Answer (EN)

All three enable real-time server-to-client communication, but with different trade-offs.

### Comparison Overview

| Aspect | Long Polling | SSE | WebSocket |
|--------|--------------|-----|-----------|
| Direction | Server → Client | Server → Client | Bidirectional |
| Protocol | HTTP | HTTP | WS (TCP) |
| Connection | Repeated requests | Single persistent | Single persistent |
| Browser support | Universal | Good (no IE) | Excellent |
| Complexity | Low | Low | Medium |

### Long Polling

**How it works:**
```
Client ─ Request ─→ Server
        ← Waits... (holds connection)
        ← Response (when data available)
Client ─ New Request ─→ Server (immediately)
        ← Waits...
        ...
```

**Characteristics:**
- Client sends request, server holds until data available
- After response, client immediately sends new request
- Works everywhere (standard HTTP)
- Higher latency than WebSocket

```javascript
// Client-side long polling
async function longPoll() {
    while (true) {
        try {
            const response = await fetch('/api/events?timeout=30');
            const data = await response.json();
            handleData(data);
        } catch (error) {
            await sleep(1000); // Wait before retry
        }
    }
}
```

**Use cases:** Legacy systems, simple notifications, fallback mechanism

### Server-Sent Events (SSE)

**How it works:**
```
Client ─ Request ─→ Server
        ← Event stream (persistent connection)
        ← data: message 1
        ← data: message 2
        ← data: message 3
        ...
```

**Characteristics:**
- Unidirectional (server to client only)
- Built on HTTP (works through proxies/firewalls)
- Automatic reconnection
- Text-based (no binary)

```javascript
// Client-side SSE
const eventSource = new EventSource('/api/stream');

eventSource.onmessage = (event) => {
    console.log('Received:', event.data);
};

eventSource.onerror = (error) => {
    console.error('SSE Error:', error);
};

// Server-side (Node.js)
app.get('/api/stream', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    const sendEvent = (data) => {
        res.write(`data: ${JSON.stringify(data)}\n\n`);
    };

    // Send events...
});
```

**Use cases:** News feeds, stock tickers, notifications, live updates

### WebSockets

**How it works:**
```
Client ─ HTTP Upgrade Request ─→ Server
        ← 101 Switching Protocols
        ─ Message ─→
        ← Message ←─
        ─ Message ─→
        (full duplex)
```

**Characteristics:**
- Full duplex (bidirectional)
- Low latency (no HTTP overhead per message)
- Binary and text support
- Requires connection state management

```javascript
// Client-side WebSocket
const ws = new WebSocket('wss://example.com/socket');

ws.onopen = () => {
    ws.send(JSON.stringify({ type: 'subscribe', channel: 'updates' }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleData(data);
};

ws.onclose = () => {
    // Reconnect logic
};

// Server-side (Node.js with ws library)
wss.on('connection', (ws) => {
    ws.on('message', (message) => {
        // Handle client message
        ws.send(JSON.stringify({ response: 'ok' }));
    });
});
```

**Use cases:** Chat, gaming, collaborative editing, trading platforms

### Decision Matrix

| Requirement | Best Choice |
|-------------|-------------|
| Server → Client only | SSE |
| Bidirectional | WebSocket |
| Simple implementation | Long Polling or SSE |
| Low latency critical | WebSocket |
| Works through all proxies | Long Polling or SSE |
| Binary data | WebSocket |
| Auto-reconnect needed | SSE |
| Maximum browser support | Long Polling |

### Scaling Considerations

| Approach | Scaling Challenge | Solution |
|----------|-------------------|----------|
| Long Polling | Many pending requests | Load balancer with sticky sessions |
| SSE | Connection per client | Reverse proxy with SSE support |
| WebSocket | Stateful connections | Sticky sessions, pub/sub backend |

---

## Otvet (RU)

Все три обеспечивают real-time коммуникацию сервер-клиент, но с разными компромиссами.

### Обзор сравнения

| Аспект | Long Polling | SSE | WebSocket |
|--------|--------------|-----|-----------|
| Направление | Сервер → Клиент | Сервер → Клиент | Двунаправленное |
| Протокол | HTTP | HTTP | WS (TCP) |
| Соединение | Повторные запросы | Одно постоянное | Одно постоянное |
| Поддержка браузеров | Универсальная | Хорошая (нет IE) | Отличная |
| Сложность | Низкая | Низкая | Средняя |

### Long Polling

**Как работает:**
```
Клиент ─ Запрос ─→ Сервер
        ← Ждет... (держит соединение)
        ← Ответ (когда данные доступны)
Клиент ─ Новый запрос ─→ Сервер (немедленно)
        ← Ждет...
        ...
```

**Характеристики:**
- Клиент отправляет запрос, сервер держит до появления данных
- После ответа клиент сразу отправляет новый запрос
- Работает везде (стандартный HTTP)
- Выше задержка чем WebSocket

```javascript
// Client-side long polling
async function longPoll() {
    while (true) {
        try {
            const response = await fetch('/api/events?timeout=30');
            const data = await response.json();
            handleData(data);
        } catch (error) {
            await sleep(1000); // Ждем перед повтором
        }
    }
}
```

**Применение:** Legacy системы, простые уведомления, fallback механизм

### Server-Sent Events (SSE)

**Как работает:**
```
Клиент ─ Запрос ─→ Сервер
        ← Event stream (постоянное соединение)
        ← data: сообщение 1
        ← data: сообщение 2
        ← data: сообщение 3
        ...
```

**Характеристики:**
- Однонаправленное (только сервер к клиенту)
- Построен на HTTP (работает через прокси/файрволы)
- Автоматическое переподключение
- Текстовый (без бинарных данных)

```javascript
// Client-side SSE
const eventSource = new EventSource('/api/stream');

eventSource.onmessage = (event) => {
    console.log('Получено:', event.data);
};

eventSource.onerror = (error) => {
    console.error('SSE Ошибка:', error);
};

// Server-side (Node.js)
app.get('/api/stream', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    const sendEvent = (data) => {
        res.write(`data: ${JSON.stringify(data)}\n\n`);
    };

    // Отправка событий...
});
```

**Применение:** Новостные ленты, биржевые котировки, уведомления, live-обновления

### WebSockets

**Как работает:**
```
Клиент ─ HTTP Upgrade Request ─→ Сервер
        ← 101 Switching Protocols
        ─ Сообщение ─→
        ← Сообщение ←─
        ─ Сообщение ─→
        (full duplex)
```

**Характеристики:**
- Full duplex (двунаправленный)
- Низкая задержка (нет HTTP overhead на сообщение)
- Поддержка бинарных и текстовых данных
- Требует управления состоянием соединения

```javascript
// Client-side WebSocket
const ws = new WebSocket('wss://example.com/socket');

ws.onopen = () => {
    ws.send(JSON.stringify({ type: 'subscribe', channel: 'updates' }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleData(data);
};

ws.onclose = () => {
    // Логика переподключения
};

// Server-side (Node.js с ws библиотекой)
wss.on('connection', (ws) => {
    ws.on('message', (message) => {
        // Обработка сообщения клиента
        ws.send(JSON.stringify({ response: 'ok' }));
    });
});
```

**Применение:** Чат, игры, совместное редактирование, торговые платформы

### Матрица решений

| Требование | Лучший выбор |
|------------|--------------|
| Только сервер → клиент | SSE |
| Двунаправленное | WebSocket |
| Простая реализация | Long Polling или SSE |
| Критична низкая задержка | WebSocket |
| Работа через все прокси | Long Polling или SSE |
| Бинарные данные | WebSocket |
| Нужно авто-переподключение | SSE |
| Максимальная поддержка браузеров | Long Polling |

### Масштабирование

| Подход | Сложность масштабирования | Решение |
|--------|---------------------------|---------|
| Long Polling | Много pending запросов | Load balancer с sticky sessions |
| SSE | Соединение на клиента | Reverse proxy с поддержкой SSE |
| WebSocket | Stateful соединения | Sticky sessions, pub/sub backend |

---

## Follow-ups

- How do you handle WebSocket reconnection with state recovery?
- What is Socket.IO and how does it differ from raw WebSockets?
- How do you scale WebSocket servers horizontally?

## Related Questions

### Prerequisites (Easier)
- [[q-rest-api-design-best-practices--system-design--medium]] - REST API

### Related (Same Level)
- [[q-pubsub-patterns--system-design--medium]] - Pub/Sub
- [[q-message-queues-event-driven--system-design--medium]] - Message queues

### Advanced (Harder)
- [[q-design-twitter--system-design--hard]] - Twitter design
- [[q-design-notification-system--system-design--hard]] - Notifications
