---
id: sysdes-060
title: Protocol Buffers vs JSON
aliases:
- Protocol Buffers
- Protobuf
- JSON vs Protobuf
- Binary Serialization
topic: system-design
subtopics:
- communication
- serialization
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
- q-grpc-vs-rest--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- communication
- difficulty/medium
- serialization
- system-design
anki_cards:
- slug: sysdes-060-0-en
  language: en
  anki_id: 1769160582776
  synced_at: '2026-01-23T13:49:17.765200'
- slug: sysdes-060-0-ru
  language: ru
  anki_id: 1769160582800
  synced_at: '2026-01-23T13:49:17.766647'
---
# Question (EN)
> What are Protocol Buffers? How do they compare to JSON for data serialization?

# Vopros (RU)
> Что такое Protocol Buffers? Как они сравниваются с JSON для сериализации данных?

---

## Answer (EN)

**Protocol Buffers (Protobuf)** is Google's binary serialization format that is smaller, faster, and type-safe compared to JSON.

### Comparison

| Aspect | JSON | Protocol Buffers |
|--------|------|------------------|
| Format | Text (human-readable) | Binary |
| Size | Larger | 3-10x smaller |
| Parse speed | Slower | 10-100x faster |
| Schema | Optional | Required (.proto) |
| Type safety | None | Strong typing |
| Language support | Universal | Code generation |
| Debugging | Easy (readable) | Hard (binary) |

### Size Comparison

```
JSON (65 bytes):
{"user_id":123,"name":"John","email":"john@example.com"}

Protobuf (~25 bytes):
0x08 0x7B 0x12 0x04 0x4A 0x6F 0x68 0x6E 0x1A 0x10...

Field encoding:
- Field number + wire type (1 byte)
- Varint for integers (1-10 bytes)
- Length-prefixed for strings
- No field names in payload
```

### Proto File Definition

```protobuf
syntax = "proto3";

message User {
  int32 user_id = 1;     // Field number 1
  string name = 2;        // Field number 2
  string email = 3;       // Field number 3
  repeated string tags = 4;  // Repeated = array
  Address address = 5;    // Nested message

  enum Status {
    UNKNOWN = 0;
    ACTIVE = 1;
    INACTIVE = 2;
  }
  Status status = 6;
}

message Address {
  string street = 1;
  string city = 2;
}
```

### Wire Types

| Type | Meaning | Used For |
|------|---------|----------|
| 0 | Varint | int32, int64, bool, enum |
| 1 | 64-bit | fixed64, double |
| 2 | Length-delimited | string, bytes, messages |
| 5 | 32-bit | fixed32, float |

### When to Use Each

**Use JSON when:**
- Human readability important
- Browser clients (native support)
- Public APIs (broad compatibility)
- Debugging/logging
- Schema flexibility needed

**Use Protobuf when:**
- Performance critical (latency/bandwidth)
- Internal microservices
- Mobile (bandwidth limited)
- Strict contracts needed
- Large data volumes

### Code Generation

```bash
# Generate code from .proto file
protoc --python_out=. user.proto
protoc --go_out=. user.proto
protoc --java_out=. user.proto

# Usage in Python
from user_pb2 import User
user = User(user_id=123, name="John")
bytes_data = user.SerializeToString()
parsed = User.FromString(bytes_data)
```

---

## Otvet (RU)

**Protocol Buffers (Protobuf)** - бинарный формат сериализации от Google, который меньше, быстрее и типобезопасен по сравнению с JSON.

### Сравнение

| Аспект | JSON | Protocol Buffers |
|--------|------|------------------|
| Формат | Текст (читаемый) | Бинарный |
| Размер | Больше | В 3-10x меньше |
| Скорость парсинга | Медленнее | В 10-100x быстрее |
| Схема | Опциональная | Обязательная (.proto) |
| Типобезопасность | Нет | Строгая типизация |
| Поддержка языков | Универсальная | Генерация кода |
| Отладка | Легко (читаемый) | Сложно (бинарный) |

### Сравнение размера

```
JSON (65 байт):
{"user_id":123,"name":"John","email":"john@example.com"}

Protobuf (~25 байт):
0x08 0x7B 0x12 0x04 0x4A 0x6F 0x68 0x6E 0x1A 0x10...

Кодирование полей:
- Номер поля + wire type (1 байт)
- Varint для целых (1-10 байт)
- Length-prefixed для строк
- Нет имён полей в payload
```

### Определение Proto файла

```protobuf
syntax = "proto3";

message User {
  int32 user_id = 1;     // Номер поля 1
  string name = 2;        // Номер поля 2
  string email = 3;       // Номер поля 3
  repeated string tags = 4;  // Repeated = массив
}
```

### Когда использовать каждый

**Используйте JSON когда:**
- Важна читаемость человеком
- Браузерные клиенты (нативная поддержка)
- Публичные API (широкая совместимость)
- Отладка/логирование
- Нужна гибкость схемы

**Используйте Protobuf когда:**
- Критична производительность (latency/bandwidth)
- Внутренние микросервисы
- Мобильные (ограничен bandwidth)
- Нужны строгие контракты
- Большие объёмы данных

### Генерация кода

```bash
# Генерация кода из .proto файла
protoc --python_out=. user.proto
protoc --go_out=. user.proto

# Использование в Python
from user_pb2 import User
user = User(user_id=123, name="John")
bytes_data = user.SerializeToString()
```

---

## Follow-ups

- What is backward/forward compatibility in Protobuf?
- How does Protobuf compare to other binary formats (Avro, Thrift)?
- What are the limitations of Protocol Buffers?
