---
id: q-kafka-internals
title: Apache Kafka Internals / Внутреннее устройство Apache Kafka
aliases:
- Kafka Internals
- Kafka Architecture
- Внутреннее устройство Kafka
- Архитектура Kafka
topic: system-design
subtopics:
- message-queues
- distributed-systems
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
- q-message-queues-event-driven--system-design--medium
- q-cap-theorem-distributed-systems--system-design--hard
- q-pubsub-patterns--system-design--medium
created: 2026-01-26
updated: 2026-01-26
tags:
- kafka
- message-queues
- distributed-systems
- streaming
- difficulty/hard
- system-design
sources:
- https://kafka.apache.org/documentation/
- https://www.confluent.io/blog/how-kafka-is-so-fast/
anki_cards:
- slug: q-kafka-internals-0-en
  anki_id: null
  synced_at: null
- slug: q-kafka-internals-0-ru
  anki_id: null
  synced_at: null
---
# Вопрос (RU)
> Как Apache Kafka работает внутри и почему она такая быстрая?

# Question (EN)
> How does Apache Kafka work internally, and why is it so fast?

---

## Ответ (RU)

См. разделы "Краткая Версия" и "Детальная Версия" ниже для полного ответа.

## Answer (EN)

See "Short Version" and "Detailed Version" sections below for the complete answer.

## Follow-ups

- How does Kafka achieve exactly-once semantics?
- What is the difference between Kafka and RabbitMQ?
- How does log compaction work in Kafka?
- How do you tune Kafka for high throughput vs low latency?
- What happens when a broker fails in Kafka?

## References
- [[q-message-queues-event-driven--system-design--medium]]
- https://kafka.apache.org/documentation/

## Related Questions

### Base (easier)
- [[q-message-queues-event-driven--system-design--medium]] - Message queue basics
- [[q-pubsub-patterns--system-design--medium]] - Pub/Sub patterns

### Adjacent (same level)
- [[q-cap-theorem-distributed-systems--system-design--hard]] - CAP theorem tradeoffs
- [[q-consistency-models--system-design--hard]] - Consistency models

### Advanced (harder)
- [[q-consensus-algorithms--system-design--hard]] - Raft/Paxos consensus
- [[q-event-sourcing--system-design--hard]] - Event sourcing patterns

---

## Short Version

Apache Kafka is a distributed commit log designed for high-throughput, fault-tolerant streaming. Its speed comes from sequential I/O (append-only logs), zero-copy data transfer, batching, compression, and partitioned parallelism. Kafka uses a pull-based consumer model with consumer groups for horizontal scaling, manages offsets in a special `__consumer_offsets` topic, and ensures durability through ISR-based replication with configurable acknowledgment levels.

## Detailed Version

### Core Architecture

**Kafka Cluster Components:**

```
Producer(s) -----> [ Broker 1 ]  [ Broker 2 ]  [ Broker 3 ] <----- Consumer(s)
                        |             |             |
                   [ ZooKeeper / KRaft Controller ]
                   (metadata, leader election)
```

- **Broker**: A Kafka server that stores data and serves clients. Each broker handles hundreds of thousands of reads/writes per second.
- **Topic**: A logical channel for messages, similar to a database table. Topics are split into partitions.
- **Partition**: An ordered, immutable sequence of records (commit log). Each partition is an independent unit of parallelism.
- **Replica**: A copy of a partition on another broker for fault tolerance.
- **ZooKeeper/KRaft**: Manages cluster metadata, broker registration, and leader election (KRaft replaces ZooKeeper in newer versions).

**Topic and Partition Layout:**

```
Topic: orders (3 partitions, replication factor = 2)

Broker 1:          Broker 2:          Broker 3:
+-----------+      +-----------+      +-----------+
| P0 Leader |      | P0 Replica|      | P1 Leader |
| P2 Replica|      | P1 Replica|      | P2 Leader |
+-----------+      +-----------+      +-----------+
```

### Why Kafka Is So Fast

**1. Sequential I/O (Append-Only Log):**

Kafka writes messages to disk sequentially at the end of log files. Sequential writes are 100-1000x faster than random writes because:
- No disk seek time
- OS optimizes for sequential access
- SSD/HDD write amplification is minimized

```
Log file structure:
+--------+--------+--------+--------+--------+
| Msg 0  | Msg 1  | Msg 2  | Msg 3  | Msg 4  | --> (append only)
+--------+--------+--------+--------+--------+
   ^
   |
 offset 0   offset 1   offset 2   ...
```

**2. Zero-Copy Transfer:**

Kafka uses the `sendfile()` system call to transfer data directly from the page cache to the network socket, bypassing user-space copying:

```
Traditional:                    Zero-copy:
Disk -> Kernel -> App -> Kernel Disk -> Kernel -> Network
     -> Network (4 copies)            (2 copies, no app involvement)
```

This reduces CPU usage and memory bandwidth by ~50%.

**3. Batching:**

Producers batch multiple messages together before sending. Consumers fetch batches of messages. Benefits:
- Amortizes network round-trip overhead
- Enables efficient compression
- Reduces system call overhead

```kotlin
// Producer batching configuration
val props = Properties().apply {
    put(ProducerConfig.BATCH_SIZE_CONFIG, 16384)       // 16KB batch
    put(ProducerConfig.LINGER_MS_CONFIG, 5)            // Wait up to 5ms to fill batch
    put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4") // Compress entire batch
}
```

**4. Compression:**

Kafka supports compression at the batch level (gzip, snappy, lz4, zstd). Compression:
- Reduces network bandwidth
- Reduces disk storage
- Works better with batching (larger data = better compression ratio)

**5. Partitioned Parallelism:**

Each partition is an independent unit. More partitions = more parallelism:
- Multiple producers can write to different partitions concurrently
- Multiple consumers can read from different partitions concurrently
- Linear horizontal scaling

### Consumer Groups and Partition Assignment

**Consumer Group Model:**

```
Topic: orders (4 partitions)
Consumer Group: order-processor

Consumer 1 <-- P0, P1
Consumer 2 <-- P2, P3

(If Consumer 2 fails, Consumer 1 gets all 4 partitions)
```

**Key Rules:**
- Each partition is consumed by exactly one consumer in a group
- One consumer can read from multiple partitions
- Adding consumers (up to partition count) increases parallelism
- More consumers than partitions = idle consumers

**Partition Assignment Strategies:**
- **Range**: Assigns contiguous partitions to consumers
- **RoundRobin**: Distributes partitions evenly across consumers
- **Sticky**: Minimizes partition movement during rebalancing
- **CooperativeSticky**: Incremental rebalancing without stop-the-world

```kotlin
// Consumer configuration
val props = Properties().apply {
    put(ConsumerConfig.GROUP_ID_CONFIG, "order-processor")
    put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
        CooperativeStickyAssignor::class.java.name)
}
```

### Offset Management

**Offset Concept:**
Each message in a partition has a unique, monotonically increasing offset. Consumers track their position using offsets.

```
Partition 0:
+----+----+----+----+----+----+----+----+
| 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  |  <-- offsets
+----+----+----+----+----+----+----+----+
              ^                    ^
         committed            current position
```

**Offset Storage:**
Offsets are stored in a special internal topic `__consumer_offsets`:
- Key: (group_id, topic, partition)
- Value: committed offset + metadata
- Compacted topic (keeps only latest offset per key)

**Commit Strategies:**

| Strategy | Pros | Cons |
|----------|------|------|
| Auto-commit | Simple, no code | At-least-once, may duplicate |
| Sync commit | Guaranteed durability | Blocking, slower |
| Async commit | Non-blocking | May lose commits on failure |
| Manual offset control | Exactly-once possible | Complex to implement |

```kotlin
// Manual commit example
while (true) {
    val records = consumer.poll(Duration.ofMillis(100))
    for (record in records) {
        process(record)
    }
    consumer.commitSync() // Commit after processing
}
```

### Replication and Fault Tolerance

**ISR (In-Sync Replicas):**

```
Partition 0 (replication factor = 3):

Broker 1 (Leader):   [0, 1, 2, 3, 4, 5]  --> ISR
Broker 2 (Follower): [0, 1, 2, 3, 4, 5]  --> ISR
Broker 3 (Follower): [0, 1, 2, 3]        --> NOT in ISR (lagging)
```

- ISR = replicas that are fully caught up with the leader
- Followers continuously fetch from leader
- If a follower falls too far behind (`replica.lag.time.max.ms`), it's removed from ISR
- Leader election only considers ISR members

**Acks Configuration:**

| acks | Durability | Latency | Description |
|------|------------|---------|-------------|
| 0 | None | Lowest | Fire-and-forget |
| 1 | Leader only | Low | Wait for leader write |
| all (-1) | Full ISR | Highest | Wait for all ISR replicas |

```kotlin
// High durability configuration
val props = Properties().apply {
    put(ProducerConfig.ACKS_CONFIG, "all")
    put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true)
    put(ProducerConfig.MIN_INSYNC_REPLICAS_CONFIG, 2)
}
```

**Leader Election:**
1. Leader fails and is detected via heartbeat timeout
2. Controller selects new leader from ISR
3. Controller propagates new leader info to all brokers
4. Clients refresh metadata and connect to new leader

### Log Compaction

**Standard Retention vs Compaction:**

```
Standard retention (time/size based):
[msg1][msg2][msg3][msg4][msg5] --> delete old segments

Log compaction (key-based):
Before: [K1:V1][K2:V1][K1:V2][K3:V1][K2:V2]
After:  [K1:V2][K3:V1][K2:V2]  (keeps latest value per key)
```

**Use Cases:**
- Database change data capture (CDC)
- State restoration for stream processing
- Maintaining latest state without full history

**Tombstones:**
A message with a null value deletes the key after a configurable delay:
```kotlin
producer.send(ProducerRecord("users", userId, null)) // Tombstone
```

### Exactly-Once Semantics (EOS)

**Three Components:**

1. **Idempotent Producer**: Each message has a sequence number. Broker deduplicates retries.

2. **Transactional Producer**: Atomic writes across multiple partitions.

3. **Transactional Consumer**: Only reads committed messages (`isolation.level=read_committed`).

```kotlin
// Transactional producer
producer.initTransactions()
try {
    producer.beginTransaction()
    producer.send(ProducerRecord("topic1", key, value))
    producer.send(ProducerRecord("topic2", key, value))
    producer.sendOffsetsToTransaction(offsets, consumerGroupId)
    producer.commitTransaction()
} catch (e: Exception) {
    producer.abortTransaction()
}
```

### Common Interview Questions

**Q: How does Kafka guarantee message ordering?**
A: Ordering is guaranteed within a partition only. Use a consistent partition key for related messages.

**Q: What happens if all ISR replicas fail?**
A: Two options via `unclean.leader.election.enable`:
- `false` (default): Partition becomes unavailable until ISR replica recovers
- `true`: Non-ISR replica can become leader (data loss possible)

**Q: How do you handle consumer lag?**
A: Monitor via `kafka-consumer-groups.sh --describe`, scale consumers, increase partitions, or tune `max.poll.records` and `fetch.max.bytes`.

**Q: Kafka vs RabbitMQ?**
A: Kafka: high throughput, replay, streaming. RabbitMQ: flexible routing, lower latency for small messages, traditional queuing patterns.

---

## Краткая Версия

Apache Kafka - это распределённый журнал фиксации (commit log), предназначенный для высокопроизводительной, отказоустойчивой передачи потоковых данных. Её скорость обусловлена последовательным вводом-выводом (append-only логи), передачей данных без копирования (zero-copy), пакетированием, сжатием и параллелизмом на уровне партиций. Kafka использует pull-модель для потребителей с группами потребителей для горизонтального масштабирования, управляет смещениями в специальном топике `__consumer_offsets` и обеспечивает надёжность через репликацию на основе ISR с настраиваемыми уровнями подтверждения.

## Детальная Версия

### Основная Архитектура

**Компоненты кластера Kafka:**

```
Producer(ы) -----> [ Broker 1 ]  [ Broker 2 ]  [ Broker 3 ] <----- Consumer(ы)
                        |             |             |
                   [ ZooKeeper / KRaft Controller ]
                   (метаданные, выбор лидера)
```

- **Broker**: Сервер Kafka, который хранит данные и обслуживает клиентов. Каждый брокер обрабатывает сотни тысяч операций чтения/записи в секунду.
- **Topic (Топик)**: Логический канал для сообщений, аналогичный таблице базы данных. Топики разбиваются на партиции.
- **Partition (Партиция)**: Упорядоченная, неизменная последовательность записей (журнал фиксации). Каждая партиция — независимая единица параллелизма.
- **Replica (Реплика)**: Копия партиции на другом брокере для отказоустойчивости.
- **ZooKeeper/KRaft**: Управляет метаданными кластера, регистрацией брокеров и выбором лидера (KRaft заменяет ZooKeeper в новых версиях).

**Структура топиков и партиций:**

```
Топик: orders (3 партиции, фактор репликации = 2)

Broker 1:          Broker 2:          Broker 3:
+-----------+      +-----------+      +-----------+
| P0 Лидер  |      | P0 Реплика|      | P1 Лидер  |
| P2 Реплика|      | P1 Реплика|      | P2 Лидер  |
+-----------+      +-----------+      +-----------+
```

### Почему Kafka такая быстрая

**1. Последовательный ввод-вывод (Append-Only Log):**

Kafka записывает сообщения на диск последовательно в конце лог-файлов. Последовательная запись в 100-1000 раз быстрее случайной, потому что:
- Нет времени поиска на диске
- ОС оптимизирует для последовательного доступа
- Минимизирован write amplification на SSD/HDD

```
Структура лог-файла:
+--------+--------+--------+--------+--------+
| Msg 0  | Msg 1  | Msg 2  | Msg 3  | Msg 4  | --> (только добавление)
+--------+--------+--------+--------+--------+
   ^
   |
offset 0   offset 1   offset 2   ...
```

**2. Передача без копирования (Zero-Copy):**

Kafka использует системный вызов `sendfile()` для передачи данных напрямую из кэш-страницы в сетевой сокет, минуя копирование в пользовательское пространство:

```
Традиционный способ:                 Zero-copy:
Диск -> Ядро -> Приложение ->        Диск -> Ядро -> Сеть
     Ядро -> Сеть (4 копирования)          (2 копирования, без участия приложения)
```

Это снижает использование CPU и пропускную способность памяти на ~50%.

**3. Пакетирование (Batching):**

Producer-ы группируют несколько сообщений перед отправкой. Consumer-ы извлекают пакеты сообщений. Преимущества:
- Амортизация затрат на сетевой обмен
- Эффективное сжатие
- Снижение накладных расходов на системные вызовы

```kotlin
// Конфигурация пакетирования producer-а
val props = Properties().apply {
    put(ProducerConfig.BATCH_SIZE_CONFIG, 16384)       // 16KB пакет
    put(ProducerConfig.LINGER_MS_CONFIG, 5)            // Ждать до 5мс для заполнения пакета
    put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4") // Сжать весь пакет
}
```

**4. Сжатие (Compression):**

Kafka поддерживает сжатие на уровне пакета (gzip, snappy, lz4, zstd). Сжатие:
- Снижает использование сетевой полосы
- Уменьшает потребление дискового пространства
- Лучше работает с пакетированием (больше данных = лучший коэффициент сжатия)

**5. Параллелизм на уровне партиций:**

Каждая партиция — независимая единица. Больше партиций = больше параллелизма:
- Несколько producer-ов могут писать в разные партиции одновременно
- Несколько consumer-ов могут читать из разных партиций одновременно
- Линейное горизонтальное масштабирование

### Группы потребителей и назначение партиций

**Модель группы потребителей:**

```
Топик: orders (4 партиции)
Группа потребителей: order-processor

Consumer 1 <-- P0, P1
Consumer 2 <-- P2, P3

(Если Consumer 2 откажет, Consumer 1 получит все 4 партиции)
```

**Основные правила:**
- Каждая партиция обрабатывается ровно одним consumer-ом в группе
- Один consumer может читать из нескольких партиций
- Добавление consumer-ов (до количества партиций) увеличивает параллелизм
- Больше consumer-ов чем партиций = простаивающие consumer-ы

**Стратегии назначения партиций:**
- **Range**: Назначает смежные партиции consumer-ам
- **RoundRobin**: Распределяет партиции равномерно между consumer-ами
- **Sticky**: Минимизирует перемещение партиций при ребалансинге
- **CooperativeSticky**: Инкрементальный ребалансинг без остановки всех consumer-ов

```kotlin
// Конфигурация consumer-а
val props = Properties().apply {
    put(ConsumerConfig.GROUP_ID_CONFIG, "order-processor")
    put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
        CooperativeStickyAssignor::class.java.name)
}
```

### Управление смещениями (Offset Management)

**Концепция смещения:**
Каждое сообщение в партиции имеет уникальную, монотонно возрастающую позицию (offset). Consumer-ы отслеживают свою позицию с помощью смещений.

```
Партиция 0:
+----+----+----+----+----+----+----+----+
| 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  |  <-- смещения
+----+----+----+----+----+----+----+----+
              ^                    ^
       подтверждённый        текущая позиция
```

**Хранение смещений:**
Смещения хранятся в специальном внутреннем топике `__consumer_offsets`:
- Ключ: (group_id, topic, partition)
- Значение: подтверждённое смещение + метаданные
- Компактируемый топик (хранит только последнее смещение для каждого ключа)

**Стратегии подтверждения:**

| Стратегия | Преимущества | Недостатки |
|-----------|--------------|------------|
| Авто-commit | Просто, без кода | At-least-once, возможны дубликаты |
| Синхронный commit | Гарантированная надёжность | Блокирующий, медленнее |
| Асинхронный commit | Неблокирующий | Может потерять commit-ы при сбое |
| Ручное управление | Возможна exactly-once семантика | Сложная реализация |

```kotlin
// Пример ручного подтверждения
while (true) {
    val records = consumer.poll(Duration.ofMillis(100))
    for (record in records) {
        process(record)
    }
    consumer.commitSync() // Подтвердить после обработки
}
```

### Репликация и отказоустойчивость

**ISR (In-Sync Реплики):**

```
Партиция 0 (фактор репликации = 3):

Broker 1 (Лидер):    [0, 1, 2, 3, 4, 5]  --> ISR
Broker 2 (Follower): [0, 1, 2, 3, 4, 5]  --> ISR
Broker 3 (Follower): [0, 1, 2, 3]        --> НЕ в ISR (отстаёт)
```

- ISR = реплики, которые полностью синхронизированы с лидером
- Follower-ы непрерывно запрашивают данные у лидера
- Если follower слишком сильно отстаёт (`replica.lag.time.max.ms`), он удаляется из ISR
- Выбор лидера учитывает только участников ISR

**Конфигурация acks:**

| acks | Надёжность | Задержка | Описание |
|------|------------|----------|----------|
| 0 | Нет | Минимальная | Отправил и забыл |
| 1 | Только лидер | Низкая | Ждать записи лидера |
| all (-1) | Весь ISR | Максимальная | Ждать всех ISR реплик |

```kotlin
// Конфигурация высокой надёжности
val props = Properties().apply {
    put(ProducerConfig.ACKS_CONFIG, "all")
    put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true)
    put(ProducerConfig.MIN_INSYNC_REPLICAS_CONFIG, 2)
}
```

**Выбор лидера:**
1. Лидер отказывает, обнаруживается по таймауту heartbeat
2. Controller выбирает нового лидера из ISR
3. Controller рассылает информацию о новом лидере всем брокерам
4. Клиенты обновляют метаданные и подключаются к новому лидеру

### Компактация лога (Log Compaction)

**Стандартное удаление vs компактация:**

```
Стандартное удаление (по времени/размеру):
[msg1][msg2][msg3][msg4][msg5] --> удалить старые сегменты

Компактация лога (по ключу):
До:    [K1:V1][K2:V1][K1:V2][K3:V1][K2:V2]
После: [K1:V2][K3:V1][K2:V2]  (хранит последнее значение для каждого ключа)
```

**Сценарии использования:**
- Change Data Capture (CDC) из баз данных
- Восстановление состояния для потоковой обработки
- Хранение текущего состояния без полной истории

**Tombstones (надгробные камни):**
Сообщение со значением null удаляет ключ после настраиваемой задержки:
```kotlin
producer.send(ProducerRecord("users", userId, null)) // Tombstone
```

### Семантика ровно-один-раз (Exactly-Once Semantics)

**Три компонента:**

1. **Идемпотентный Producer**: Каждое сообщение имеет порядковый номер. Broker дедуплицирует повторные отправки.

2. **Транзакционный Producer**: Атомарные записи в несколько партиций.

3. **Транзакционный Consumer**: Читает только подтверждённые сообщения (`isolation.level=read_committed`).

```kotlin
// Транзакционный producer
producer.initTransactions()
try {
    producer.beginTransaction()
    producer.send(ProducerRecord("topic1", key, value))
    producer.send(ProducerRecord("topic2", key, value))
    producer.sendOffsetsToTransaction(offsets, consumerGroupId)
    producer.commitTransaction()
} catch (e: Exception) {
    producer.abortTransaction()
}
```

### Типичные вопросы на собеседованиях

**В: Как Kafka гарантирует порядок сообщений?**
О: Порядок гарантирован только в рамках одной партиции. Используйте постоянный ключ партиции для связанных сообщений.

**В: Что происходит, если все ISR реплики откажут?**
О: Два варианта через `unclean.leader.election.enable`:
- `false` (по умолчанию): Партиция становится недоступной до восстановления ISR реплики
- `true`: Не-ISR реплика может стать лидером (возможна потеря данных)

**В: Как обрабатывать отсталость consumer-а (lag)?**
О: Мониторить через `kafka-consumer-groups.sh --describe`, масштабировать consumer-ов, увеличить количество партиций или настроить `max.poll.records` и `fetch.max.bytes`.

**В: Kafka vs RabbitMQ?**
О: Kafka: высокая пропускная способность, повторное чтение, streaming. RabbitMQ: гибкая маршрутизация, меньше задержка для маленьких сообщений, традиционные паттерны очереди.
