---
id: sysdes-038
title: gRPC vs REST
aliases:
- gRPC
- Protocol Buffers
- RPC vs REST
topic: system-design
subtopics:
- communication
- api
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
- q-websockets-sse-long-polling--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- communication
- difficulty/medium
- api
- system-design
anki_cards:
- slug: sysdes-038-0-en
  language: en
  anki_id: 1769159521497
  synced_at: '2026-01-23T13:49:17.811681'
- slug: sysdes-038-0-ru
  language: ru
  anki_id: 1769159521519
  synced_at: '2026-01-23T13:49:17.812973'
---
# Question (EN)
> What are the differences between gRPC and REST? When would you choose one over the other?

# Vopros (RU)
> В чем разница между gRPC и REST? Когда выбирать один вместо другого?

---

## Answer (EN)

**gRPC** is a high-performance RPC framework using Protocol Buffers and HTTP/2. **REST** is an architectural style using JSON over HTTP.

### Key Differences

| Aspect | REST | gRPC |
|--------|------|------|
| Protocol | HTTP/1.1 (usually) | HTTP/2 |
| Format | JSON (text) | Protocol Buffers (binary) |
| Contract | OpenAPI/Swagger (optional) | Proto files (required) |
| Streaming | Limited (SSE, WebSocket) | Native bidirectional |
| Browser support | Excellent | Limited (needs proxy) |
| Code generation | Optional | Built-in |

### Performance Comparison

```
JSON (REST):
{"user_id": 123, "name": "John", "email": "john@example.com"}
~65 bytes, human-readable

Protocol Buffers (gRPC):
0x08 0x7B 0x12 0x04 0x4A 0x6F 0x68 0x6E...
~25 bytes, binary, faster to parse
```

### gRPC Streaming Modes

```
1. Unary: Request → Response (like REST)

2. Server streaming: Request → Stream of responses
   client.ListUsers(request) → [user1, user2, user3...]

3. Client streaming: Stream of requests → Response
   client.UploadChunks([chunk1, chunk2...]) → result

4. Bidirectional: Stream ↔ Stream
   chat.Connect() → send/receive messages
```

### When to Use REST

- Public APIs (broad compatibility)
- Browser-based clients
- Simple CRUD operations
- When human readability matters
- Caching important (HTTP caching)

### When to Use gRPC

- Microservices communication (internal)
- Low latency requirements
- Streaming data (real-time)
- Polyglot environments (code generation)
- Mobile clients (bandwidth sensitive)

### Proto File Example

```protobuf
syntax = "proto3";

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (stream User);
}

message GetUserRequest {
  int32 user_id = 1;
}

message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
}
```

---

## Otvet (RU)

**gRPC** - высокопроизводительный RPC-фреймворк на Protocol Buffers и HTTP/2. **REST** - архитектурный стиль с JSON через HTTP.

### Ключевые различия

| Аспект | REST | gRPC |
|--------|------|------|
| Протокол | HTTP/1.1 (обычно) | HTTP/2 |
| Формат | JSON (текст) | Protocol Buffers (бинарный) |
| Контракт | OpenAPI/Swagger (опционально) | Proto файлы (обязательно) |
| Стриминг | Ограниченный (SSE, WebSocket) | Нативный двунаправленный |
| Поддержка браузеров | Отличная | Ограниченная (нужен прокси) |
| Кодогенерация | Опциональная | Встроенная |

### Сравнение производительности

```
JSON (REST):
{"user_id": 123, "name": "John", "email": "john@example.com"}
~65 байт, читаемый человеком

Protocol Buffers (gRPC):
0x08 0x7B 0x12 0x04 0x4A 0x6F 0x68 0x6E...
~25 байт, бинарный, быстрее парсить
```

### Режимы стриминга gRPC

```
1. Unary: Запрос → Ответ (как REST)

2. Server streaming: Запрос → Поток ответов
   client.ListUsers(request) → [user1, user2, user3...]

3. Client streaming: Поток запросов → Ответ
   client.UploadChunks([chunk1, chunk2...]) → result

4. Bidirectional: Поток ↔ Поток
   chat.Connect() → отправка/получение сообщений
```

### Когда использовать REST

- Публичные API (широкая совместимость)
- Браузерные клиенты
- Простые CRUD операции
- Когда важна читаемость человеком
- Важно кеширование (HTTP caching)

### Когда использовать gRPC

- Коммуникация микросервисов (внутренняя)
- Требования низкой задержки
- Потоковые данные (real-time)
- Полиглотные среды (кодогенерация)
- Мобильные клиенты (важна пропускная способность)

---

## Follow-ups

- How does gRPC handle errors compared to REST?
- What is gRPC-Web and when do you need it?
- How does HTTP/2 multiplexing benefit gRPC?
