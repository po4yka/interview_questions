---
id: q-design-google-docs
title: Design Google Docs
difficulty: hard
subtopics:
- real-time-collaboration
- crdt
- operational-transformation
- distributed-systems
- websockets
- conflict-resolution
anki_cards:
- slug: q-design-google-docs-0-en
  anki_id: null
  synced_at: null
- slug: q-design-google-docs-0-ru
  anki_id: null
  synced_at: null
---

# Question (EN)
> How would you design a real-time collaborative document editor like Google Docs?

## Answer (EN)

### 1. Requirements Clarification

**Functional Requirements:**
- Real-time collaborative editing (multiple users simultaneously)
- Document creation, editing, and deletion
- Rich text formatting (bold, italic, headers, lists)
- Cursor and selection synchronization
- Version history and rollback
- Offline editing with sync on reconnect
- Sharing and access control (view/edit/comment)
- Comments and suggestions

**Non-Functional Requirements:**
- Low latency (<100ms for local changes)
- Strong eventual consistency
- High availability (99.9%+)
- Support for millions of concurrent documents
- Conflict-free merging of concurrent edits

**Scale Estimates:**
- 100M daily active users
- 10M concurrent editing sessions
- Average document: 50KB, up to 10MB
- 1000 operations/second per popular document

---

### 2. High-Level Architecture

```
+------------------+     +------------------+     +------------------+
|    Client App    |<--->|   API Gateway    |<--->|  Auth Service    |
|  (Browser/Mobile)|     |  (Load Balancer) |     +------------------+
+------------------+     +------------------+
         |                        |
         | WebSocket              | REST
         v                        v
+------------------+     +------------------+     +------------------+
| Collaboration    |<--->|  Document        |<--->|  Storage         |
| Service          |     |  Service         |     |  (S3/GCS)        |
| (OT/CRDT Engine) |     +------------------+     +------------------+
+------------------+              |
         |                        v
         v               +------------------+
+------------------+     |  Search Service  |
| Presence Service |     |  (Elasticsearch) |
| (Redis Pub/Sub)  |     +------------------+
+------------------+
         |
         v
+------------------+
| Operations Log   |
| (Kafka/Spanner)  |
+------------------+
```

---

### 3. Core Algorithm: OT vs CRDT

#### Operational Transformation (OT)
**Used by:** Google Docs, Microsoft Office Online

**How it works:**
1. Each edit is an **operation** (insert, delete, retain)
2. When concurrent operations arrive, **transform** them against each other
3. Server maintains authoritative document state

**Operation Types:**
```
Insert(position, text)   - Insert text at position
Delete(position, length) - Delete characters
Retain(count)            - Skip characters (for formatting)
```

**Transformation Example:**
```
Initial: "Hello"
User A: Insert(5, " World") -> "Hello World"
User B: Delete(0, 1)        -> "ello" (intended)

Without transformation: conflicts!
With OT:
- Transform B's operation against A's: Delete(0, 1)
- Transform A's operation against B's: Insert(4, " World")
- Result: "ello World" - consistent for both
```

**Pros:** Proven at scale (Google Docs), efficient for text
**Cons:** Complex transformation functions, centralized server required

#### CRDT (Conflict-free Replicated Data Type)
**Used by:** Figma, Apple Notes, some modern editors

**How it works:**
1. Each character has a **unique ID** (fractional positioning)
2. Operations are **commutative** - order doesn't matter
3. Merge automatically without transformation

**Types:**
- **RGA (Replicated Growable Array):** Uses linked list with unique IDs
- **YATA (Yet Another Transformation Approach):** Optimized for text
- **Automerge/Yjs:** Popular CRDT libraries

**Fractional Indexing Example:**
```
Initial positions: A=0.0, B=1.0
Insert between A and B: new position = 0.5
Insert between A and 0.5: new position = 0.25
```

**Pros:** Decentralized, works offline, mathematically proven correct
**Cons:** Higher memory (IDs for each character), tombstones for deletions

---

### 4. Real-Time Communication

#### WebSocket Connection
```
Client                    Server
   |                         |
   |---- Connect ----------->|
   |<--- Ack + Doc State ----|
   |                         |
   |---- Operation --------->|
   |<--- Ack + Transform ----|
   |<--- Broadcast Ops ------|
   |                         |
```

**Connection Management:**
- Sticky sessions via load balancer (user ID hash)
- Heartbeat every 30 seconds
- Automatic reconnection with exponential backoff
- Operation queue during disconnection

#### Presence Service (Cursor Sync)
```json
{
  "userId": "user123",
  "documentId": "doc456",
  "cursor": { "position": 42, "selectionEnd": 50 },
  "color": "#FF5733",
  "lastSeen": "2024-01-15T10:30:00Z"
}
```
- Redis Pub/Sub for real-time cursor updates
- Throttle cursor updates (10-20ms debounce)
- Show user avatars at cursor positions

---

### 5. Document Storage

#### Data Model
```sql
-- Documents metadata
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    owner_id UUID,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Document content (versioned)
CREATE TABLE document_versions (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    version INT,
    content_snapshot TEXT,  -- Periodic full snapshot
    created_at TIMESTAMP,
    created_by UUID
);

-- Operations log (fine-grained)
CREATE TABLE operations (
    id BIGSERIAL PRIMARY KEY,
    document_id UUID,
    version INT,
    operation JSONB,  -- {type, position, text, ...}
    user_id UUID,
    timestamp TIMESTAMP,
    INDEX (document_id, version)
);
```

#### Storage Strategy
- **Hot storage:** Recent operations in Redis/Memcached
- **Warm storage:** Last 30 days in PostgreSQL/Spanner
- **Cold storage:** Full snapshots in S3/GCS (every 100 ops or 5 min)
- **Compaction:** Merge operations into snapshots periodically

---

### 6. Conflict Resolution Flow

```
1. User types "Hello"
   |
   v
2. Client generates operation: Insert(0, "Hello")
   |
   v
3. Send via WebSocket with local version number
   |
   v
4. Server receives, checks version
   |
   +-- Version matches? Apply and broadcast
   |
   +-- Version mismatch? Transform against missed operations
       |
       v
5. Server broadcasts transformed operation to all clients
   |
   v
6. Clients apply operation, update local state
```

---

### 7. Offline Support

**Strategy: Optimistic Local-First**

1. **Local-first editing:** Changes apply immediately to local state
2. **Operation queue:** Store pending operations in IndexedDB
3. **Sync on reconnect:**
   - Send queued operations with last known version
   - Server transforms against concurrent operations
   - Receive transformed operations from others

**Conflict Resolution:**
```
Offline changes: [Op1, Op2, Op3]
Server state: [ServerOp1, ServerOp2]

On reconnect:
1. Transform Op1 against ServerOp1, ServerOp2 -> Op1'
2. Transform Op2 against ServerOp1, ServerOp2, Op1' -> Op2'
3. Apply transformed operations
4. Merge result is consistent
```

---

### 8. Access Control

**Permission Model:**
```
Owner    -> Full control (delete, share, transfer)
Editor   -> Edit content, add comments
Commenter -> Add comments only
Viewer   -> Read-only access
```

**Sharing Options:**
- Direct user share (email)
- Link sharing (anyone with link)
- Domain-restricted (organization only)
- Public (searchable)

**Implementation:**
```sql
CREATE TABLE document_permissions (
    document_id UUID,
    principal_type ENUM('user', 'group', 'domain', 'anyone'),
    principal_id VARCHAR(255),  -- user email, group id, or '*'
    role ENUM('owner', 'editor', 'commenter', 'viewer'),
    created_at TIMESTAMP,
    PRIMARY KEY (document_id, principal_type, principal_id)
);
```

---

### 9. Performance Optimizations

**Client-side:**
- Virtual rendering (only visible content in DOM)
- Debounce operations (batch keystrokes)
- Local operation cache for undo/redo
- Lazy load images and embeds

**Server-side:**
- Sticky sessions to reduce state sync
- Operation batching (group small operations)
- Snapshot caching (avoid replaying full history)
- Read replicas for document loading

**At Scale:**
- Shard documents by ID
- Separate hot documents to dedicated servers
- Rate limit operations per user (100 ops/sec)

---

### 10. Monitoring and Observability

**Key Metrics:**
- Operation latency (P50, P95, P99)
- Conflict rate per document
- Active WebSocket connections
- Sync lag (client vs server version)
- Document load time

**Alerts:**
- Latency > 500ms
- Conflict rate > 5%
- WebSocket disconnection spike
- Storage write failures

---

### 11. Trade-offs Summary

| Aspect | OT Choice | CRDT Choice |
|--------|-----------|-------------|
| Complexity | Higher server logic | Higher memory usage |
| Offline | Requires careful sync | Native support |
| Scalability | Central server bottleneck | Peer-to-peer possible |
| Proven at scale | Google Docs | Figma, newer systems |

**Recommendation:** For a Google Docs clone, OT with a central server is battle-tested. For modern greenfield projects, consider CRDT (Yjs/Automerge) for simpler offline support.

---

# Vopros (RU)
> Как бы вы спроектировали редактор документов с совместным редактированием в реальном времени, как Google Docs?

## Otvet (RU)

### 1. Уточнение требований

**Функциональные требования:**
- Совместное редактирование в реальном времени (несколько пользователей одновременно)
- Создание, редактирование и удаление документов
- Форматирование текста (жирный, курсив, заголовки, списки)
- Синхронизация курсоров и выделений
- История версий и откат изменений
- Офлайн-редактирование с синхронизацией при подключении
- Настройки доступа (просмотр/редактирование/комментирование)
- Комментарии и предложения

**Нефункциональные требования:**
- Низкая задержка (<100мс для локальных изменений)
- Строгая согласованность в конечном счёте (strong eventual consistency)
- Высокая доступность (99.9%+)
- Поддержка миллионов одновременных документов
- Бесконфликтное слияние параллельных правок

**Оценки масштаба:**
- 100 млн активных пользователей в день
- 10 млн одновременных сессий редактирования
- Средний документ: 50КБ, до 10МБ
- 1000 операций/секунду для популярных документов

---

### 2. Высокоуровневая архитектура

```
+------------------+     +------------------+     +------------------+
|    Клиент        |<--->|   API Gateway    |<--->|  Сервис          |
|  (Браузер/Моб.)  |     |  (Балансировщик) |     |  авторизации     |
+------------------+     +------------------+     +------------------+
         |                        |
         | WebSocket              | REST
         v                        v
+------------------+     +------------------+     +------------------+
| Сервис           |<--->|  Сервис          |<--->|  Хранилище       |
| коллаборации     |     |  документов      |     |  (S3/GCS)        |
| (OT/CRDT движок) |     +------------------+     +------------------+
+------------------+              |
         |                        v
         v               +------------------+
+------------------+     |  Поисковый       |
| Сервис           |     |  сервис          |
| присутствия      |     |  (Elasticsearch) |
| (Redis Pub/Sub)  |     +------------------+
+------------------+
         |
         v
+------------------+
| Лог операций     |
| (Kafka/Spanner)  |
+------------------+
```

---

### 3. Основной алгоритм: OT против CRDT

#### Операционная трансформация (OT)
**Используется:** Google Docs, Microsoft Office Online

**Принцип работы:**
1. Каждая правка - это **операция** (вставка, удаление, пропуск)
2. При получении конкурентных операций выполняется их **трансформация**
3. Сервер поддерживает авторитетное состояние документа

**Типы операций:**
```
Insert(позиция, текст)   - Вставить текст в позицию
Delete(позиция, длина)   - Удалить символы
Retain(количество)       - Пропустить символы (для форматирования)
```

**Пример трансформации:**
```
Исходный текст: "Привет"
Пользователь А: Insert(6, " мир") -> "Привет мир"
Пользователь Б: Delete(0, 1)      -> "ривет" (намерение)

Без трансформации: конфликт!
С OT:
- Трансформируем операцию Б относительно А: Delete(0, 1)
- Трансформируем операцию А относительно Б: Insert(5, " мир")
- Результат: "ривет мир" - согласованный для обоих
```

**Плюсы:** Проверено на масштабе (Google Docs), эффективно для текста
**Минусы:** Сложные функции трансформации, требуется центральный сервер

#### CRDT (Бесконфликтные реплицируемые типы данных)
**Используется:** Figma, Apple Notes, современные редакторы

**Принцип работы:**
1. Каждый символ имеет **уникальный ID** (дробное позиционирование)
2. Операции **коммутативны** - порядок не важен
3. Автоматическое слияние без трансформации

**Типы:**
- **RGA (Replicated Growable Array):** Связный список с уникальными ID
- **YATA:** Оптимизирован для текста
- **Automerge/Yjs:** Популярные CRDT-библиотеки

**Пример дробного индексирования:**
```
Начальные позиции: A=0.0, B=1.0
Вставка между A и B: новая позиция = 0.5
Вставка между A и 0.5: новая позиция = 0.25
```

**Плюсы:** Децентрализованность, работа офлайн, математически доказанная корректность
**Минусы:** Больше памяти (ID для каждого символа), надгробия для удалений

---

### 4. Коммуникация в реальном времени

#### WebSocket-соединение
```
Клиент                    Сервер
   |                         |
   |---- Подключение ------->|
   |<--- Подтв. + Состояние -|
   |                         |
   |---- Операция ---------->|
   |<--- Подтв. + Трансф. ---|
   |<--- Трансляция опер. ---|
   |                         |
```

**Управление соединениями:**
- Липкие сессии через балансировщик (хеш ID пользователя)
- Heartbeat каждые 30 секунд
- Автоматическое переподключение с экспоненциальной задержкой
- Очередь операций при разрыве соединения

#### Сервис присутствия (синхронизация курсоров)
```json
{
  "userId": "user123",
  "documentId": "doc456",
  "cursor": { "position": 42, "selectionEnd": 50 },
  "color": "#FF5733",
  "lastSeen": "2024-01-15T10:30:00Z"
}
```
- Redis Pub/Sub для обновлений курсоров в реальном времени
- Троттлинг обновлений курсора (дебаунс 10-20мс)
- Отображение аватаров пользователей у курсоров

---

### 5. Хранение документов

#### Модель данных
```sql
-- Метаданные документов
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    owner_id UUID,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Содержимое документа (версионированное)
CREATE TABLE document_versions (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    version INT,
    content_snapshot TEXT,  -- Периодический полный снапшот
    created_at TIMESTAMP,
    created_by UUID
);

-- Лог операций (детальный)
CREATE TABLE operations (
    id BIGSERIAL PRIMARY KEY,
    document_id UUID,
    version INT,
    operation JSONB,  -- {type, position, text, ...}
    user_id UUID,
    timestamp TIMESTAMP,
    INDEX (document_id, version)
);
```

#### Стратегия хранения
- **Горячее хранилище:** Недавние операции в Redis/Memcached
- **Тёплое хранилище:** Последние 30 дней в PostgreSQL/Spanner
- **Холодное хранилище:** Полные снапшоты в S3/GCS (каждые 100 операций или 5 минут)
- **Компактификация:** Периодическое слияние операций в снапшоты

---

### 6. Процесс разрешения конфликтов

```
1. Пользователь набирает "Привет"
   |
   v
2. Клиент генерирует операцию: Insert(0, "Привет")
   |
   v
3. Отправка через WebSocket с локальным номером версии
   |
   v
4. Сервер получает, проверяет версию
   |
   +-- Версия совпадает? Применить и транслировать
   |
   +-- Версия не совпадает? Трансформировать относительно
       пропущенных операций
       |
       v
5. Сервер транслирует трансформированную операцию всем клиентам
   |
   v
6. Клиенты применяют операцию, обновляют локальное состояние
```

---

### 7. Поддержка офлайн-режима

**Стратегия: Оптимистичный локальный приоритет**

1. **Локальный приоритет:** Изменения сразу применяются к локальному состоянию
2. **Очередь операций:** Хранение ожидающих операций в IndexedDB
3. **Синхронизация при подключении:**
   - Отправка операций из очереди с последней известной версией
   - Сервер трансформирует относительно конкурентных операций
   - Получение трансформированных операций от других

**Разрешение конфликтов:**
```
Офлайн-изменения: [Op1, Op2, Op3]
Состояние сервера: [ServerOp1, ServerOp2]

При подключении:
1. Трансформируем Op1 относительно ServerOp1, ServerOp2 -> Op1'
2. Трансформируем Op2 относительно ServerOp1, ServerOp2, Op1' -> Op2'
3. Применяем трансформированные операции
4. Результат слияния согласован
```

---

### 8. Контроль доступа

**Модель прав:**
```
Владелец     -> Полный контроль (удаление, публикация, передача)
Редактор     -> Редактирование содержимого, добавление комментариев
Комментатор  -> Только добавление комментариев
Читатель     -> Только просмотр
```

**Варианты предоставления доступа:**
- Прямой доступ пользователю (по email)
- Доступ по ссылке (любой с ссылкой)
- Ограничение по домену (только организация)
- Публичный (индексируется поиском)

**Реализация:**
```sql
CREATE TABLE document_permissions (
    document_id UUID,
    principal_type ENUM('user', 'group', 'domain', 'anyone'),
    principal_id VARCHAR(255),  -- email, group id или '*'
    role ENUM('owner', 'editor', 'commenter', 'viewer'),
    created_at TIMESTAMP,
    PRIMARY KEY (document_id, principal_type, principal_id)
);
```

---

### 9. Оптимизации производительности

**На стороне клиента:**
- Виртуальный рендеринг (только видимый контент в DOM)
- Дебаунс операций (группировка нажатий клавиш)
- Локальный кеш операций для отмены/повтора
- Ленивая загрузка изображений и вложений

**На стороне сервера:**
- Липкие сессии для уменьшения синхронизации состояния
- Пакетирование операций (группировка мелких операций)
- Кеширование снапшотов (без воспроизведения полной истории)
- Реплики для чтения при загрузке документов

**На масштабе:**
- Шардирование документов по ID
- Выделенные серверы для популярных документов
- Ограничение частоты операций на пользователя (100 оп/сек)

---

### 10. Мониторинг и наблюдаемость

**Ключевые метрики:**
- Задержка операций (P50, P95, P99)
- Частота конфликтов на документ
- Активные WebSocket-соединения
- Отставание синхронизации (версия клиента vs сервера)
- Время загрузки документа

**Алерты:**
- Задержка > 500мс
- Частота конфликтов > 5%
- Всплеск разрывов WebSocket
- Ошибки записи в хранилище

---

### 11. Сравнение подходов

| Аспект | Выбор OT | Выбор CRDT |
|--------|----------|------------|
| Сложность | Выше логика сервера | Выше потребление памяти |
| Офлайн | Требует аккуратной синхронизации | Нативная поддержка |
| Масштабируемость | Центральный сервер - узкое место | Возможен P2P |
| Проверено на масштабе | Google Docs | Figma, новые системы |

**Рекомендация:** Для клона Google Docs OT с центральным сервером - проверенное решение. Для новых проектов с нуля стоит рассмотреть CRDT (Yjs/Automerge) для простой поддержки офлайн-режима.
