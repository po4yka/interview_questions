---
id: android-468
title: Design WhatsApp App / Проектирование приложения WhatsApp
aliases:
- Design WhatsApp App
- Проектирование приложения WhatsApp
topic: android
subtopics:
- media
- networking-http
- service
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- c-service
- c-retrofit
- c-media3
- q-data-sync-unstable-network--android--hard
- q-database-encryption-android--android--medium
- q-design-instagram-stories--android--hard
created: 2025-10-20
updated: 2025-11-02
tags:
- android/media
- android/networking-http
- android/service
- architecture
- cryptography
- difficulty/hard
- e2ee
- messaging
- networking
- performance
- realtime
- system-design
- websocket
sources:
- https://signal.org/docs/specifications/doubleratchet/
---

# Вопрос (RU)

> Как спроектировать мессенджер WhatsApp для Android?

## Краткая Версия

Спроектируйте E2E‑зашифрованный Android‑чат для обмена сообщениями 1-to-1 и в малых группах. Система должна обеспечивать низкую латентность отправки, устойчивость офлайн‑доставки и синхронизацию между несколькими устройствами одного пользователя.

## Подробная Версия

Спроектируйте полноценный E2E‑зашифрованный мессенджер WhatsApp для Android со следующими требованиями:

**Производительность:**
- Онлайн‑латентность отправки: <200мс (p95)
- Поддержка миллиардов сообщений в день
- Бережное потребление батареи и трафика

**Функциональность:**
- Обмен сообщениями 1-to-1 и в малых группах (текст, медиа, голосовые)
- E2E шифрование (`Signal Protocol`) с forward secrecy
- Статусы доставки/прочтения (sent/delivered/read)
- Синхронизация между 2+ устройствами одного пользователя
- Устойчивая офлайн‑доставка с очередью неотправленных сообщений

**Безопасность:**
- E2E шифрование с zero-knowledge server (сервер не видит plaintext)
- Управление ключами и безопасный бэкап
- Анти‑спам и защита от злоупотреблений

**Технические детали (для обсуждения):**
- Локальная модель данных и индексы (`Room` database)
- Генерация ID и упорядочивание сообщений
- Статусы доставки/прочтения (sent/received/read)
- Пайплайн вложений: шифрование → чанки → возобновляемая загрузка
- Стратегия уведомлений (Android 13–15, `FCM`, группировка)
- Управление ключами и бэкап с восстановлением
- Наблюдаемость (метрики latency, доставки, синхронизации)
- План поэтапного релиза (staged rollout)

# Question (EN)

> How to design WhatsApp for Android?

## `Short` Version

Design an E2E‑encrypted Android chat for 1-to-1 and small group messaging. The system should ensure low send latency, durable offline delivery, and synchronization across multiple devices for the same user.

## Detailed Version

Design a complete E2E‑encrypted WhatsApp messenger for Android with the following requirements:

**Performance:**
- Online send latency: <200ms (p95)
- Support billions of messages per day
- Battery and bandwidth efficient

**Functionality:**
- 1-to-1 and small group messaging (text, media, voice)
- E2E encryption (`Signal Protocol`) with forward secrecy
- Delivery/read statuses (sent/delivered/read)
- Sync across 2+ devices for same user
- Durable offline delivery with unsent message queue

**Security:**
- E2E encryption with zero-knowledge server (server blind to plaintext)
- Key management and secure backup
- Anti‑spam and abuse protection

**Technical details (for discussion):**
- Local data model and indexes (`Room` database)
- `Message` ID generation and ordering
- Delivery/ack states (sent/received/read)
- Attachment pipeline: encrypt → chunk → resumable upload
- Notification strategy (Android 13–15, `FCM`, grouping)
- Key management and backup with recovery
- Observability (latency, delivery, sync metrics)
- Staged rollout plan

## Ответ (RU)

`WhatsApp` — E2E‑зашифрованный мессенджер, включающий: обмен сообщениями 1-to-1 и в группах, медиафайлы (изображения, видео, аудио), статусы доставки/прочтения, E2E шифрование через `Signal Protocol` с forward secrecy, голос/видео-звонки через `WebRTC`, и офлайн-персистентность с синхронизацией при восстановлении сети.

### Требования

**Функциональные:**

**Обмен сообщениями:**
-   Текстовые сообщения с поддержкой форматирования (жирный, курсив, моноширинный)
-   Медиафайлы: изображения (`JPEG`, `PNG`, `WEBP`), видео (`H.264`, `H.265`), аудио (`Opus`, `AAC`), документы
-   Голосовые сообщения с записью в реальном времени и сжатием

**Группы:**
-   Создание групп до 256 участников (для малых групп — до 32 для оптимизации)
-   Управление участниками (добавление/удаление), изменение названия/аватара
-   Групповые настройки (кто может отправлять сообщения, админы)

**Статусы доставки:**
-   `sent` — сообщение отправлено с клиента
-   `delivered` — сообщение доставлено на сервер и на устройство получателя
-   `read` — сообщение прочитано получателем (double checkmark)

**Безопасность:**
-   E2E шифрование через `Signal Protocol` с forward secrecy (каждое сообщение имеет уникальный ключ)
-   Device verification через QR-код safety numbers для предотвращения MITM атак
-   Блокировка и репортинг пользователей

**Присутствие:**
-   Статусы `online`/`offline` в реальном времени
-   `last seen` — время последнего посещения (с настройками приватности)

**Push уведомления:**
-   Интеграция с `FCM` (Firebase Cloud Messaging) для фоновых уведомлений
-   Группировка уведомлений по чатам (Android 13+)

**Звонки:**
-   Голосовые и видеозвонки через `WebRTC`
-   `STUN`/`TURN` серверы для NAT traversal
-   Адаптивный битрейт для оптимизации качества при плохом соединении

**Нефункциональные:**

-   **Низкая латентность**: <200ms (P95) от нажатия "Отправить" до доставки на сервер — критично для ощущения real-time общения
-   **Высокая доступность**: >99.9% uptime для критичных операций (отправка/получение сообщений)
-   **Масштабируемость**: поддержка миллиардов сообщений в день через горизонтальное масштабирование
-   **Конфиденциальность**: zero-knowledge server — сервер не видит plaintext сообщений, только зашифрованные данные
-   **Бережная батарея/трафик**: оптимизация частоты heartbeat, batch отправка, компрессия данных
-   **Офлайн поддержка**: очередь неотправленных сообщений, синхронизация при восстановлении сети

### Архитектура

**Android клиент:**

Модульная архитектура с четким разделением ответственности:
-   **`Room` database**: локальное хранилище для сообщений, контактов, групп с индексами для быстрого поиска и пагинации
-   **E2EE engine**: движок шифрования `Signal Protocol` для encrypt/decrypt сообщений, управление ключами
-   **WebSocket**: realtime канал для получения сообщений, обновлений статусов, presence
-   **Media cache**: многоуровневый кеш (`Memory` → `Disk`) для медиафайлов с LRU eviction policy

**Backend:**

Архитектура микросервисов с горизонтальным масштабированием:
-   **Load Balancer**: распределение нагрузки между инстансами, sticky sessions для `WebSocket` connections
-   **Микросервисы**: `Chat Service` (маршрутизация сообщений), `Presence Service` (онлайн статусы), `Media Service` (загрузка/доставка медиа), `Call Signaling Service` (`WebRTC` signaling), `Push Service` (`FCM` интеграция)
-   **Хранилище данных**: `Kafka` для async обработки событий, `Cassandra` для сообщений (партиционирование, TTL), `PostgreSQL` для пользователей/групп (strong consistency), `S3`+`CDN` для медиа (lifecycle policies), `Redis` для presence кеша (TTL-based)

### Клиент Android: Ключевые Потоки

**1. Отправка сообщения**

Многоэтапный процесс отправки с гарантией доставки и шифрованием:

**Этапы:**
1.   **Шифрование**: применение `Signal Protocol` `Double` Ratchet для шифрования plaintext — каждый сеанс имеет уникальные ключи для forward secrecy
2.   **Локальная запись**: сохранение сообщения в `Room` database со статусом `pending` — позволяет отображать сообщение в UI до подтверждения доставки (optimistic UI)
3.   **WebSocket отправка**: отправка зашифрованного сообщения через `WebSocket` для минимальной латентности
4.   **Server ack**: получение подтверждения от сервера и обновление статуса до `delivered` — гарантия доставки на сервер
5.   **Recipient receipt**: получение read receipt от получателя и обновление статуса до `read` — индикация прочтения

**2. Получение сообщения**

Обработка входящих сообщений с расшифровкой и синхронизацией:

**Этапы:**
1.   **WebSocket получение**: получение зашифрованного сообщения через `WebSocket`
2.   **Расшифровка**: применение `Signal Protocol` для расшифровки ciphertext в plaintext
3.   **Room DB сохранение**: запись расшифрованного сообщения в `Room` database с индексами для быстрого поиска
4.   **UI update**: обновление UI через `Flow`/`LiveData` для реактивного отображения новых сообщений
5.   **Read receipt**: автоматическая отправка read receipt при открытии чата или прочтении сообщения

**3. Обработка медиа**

Загрузка медиафайлов с шифрованием и оптимизацией:

**Этапы:**
1.   **Сжатие**: компрессия медиа (изображения: `JPEG`/`WEBP`, видео: `H.264` с битрейтом 2-4 Mbps для экономии трафика)
2.   **Шифрование**: `AES-GCM` шифрование медиафайла с ключом для E2E защиты
3.   **Upload на CDN**: загрузка зашифрованного файла на `S3` с последующей доставкой через `CDN` для глобальной доступности
4.   **Отправка metadata**: отправка `URL` медиа, `thumbnail` для превью, и `decryption key` (зашифрованного через `Signal Protocol`) получателю
5.   **Ленивая загрузка**: загрузка медиа только при открытии/просмотре для экономии трафика и батареи

**4. Офлайн режим**

Очередь неотправленных сообщений с автоматической синхронизацией:

**Механизм:**
-   **Очередь unsent**: сохранение неотправленных сообщений в `Room` database с статусом `pending`
-   **Хранение**: персистентное хранение до 30 дней для гарантии доставки даже при длительном отсутствии сети
-   **Автоматический resend**: автоматическая отправка при восстановлении сети через `WorkManager` с constraints
-   **Exponential backoff**: увеличение интервала между retry при ошибках (1s, 2s, 4s, 8s) для предотвращения перегрузки сервера

**5. Групповые сообщения**

Эффективная доставка сообщений в группы с E2E шифрованием:

**Механизм:**
-   **Sender keys**: каждый участник группы имеет sender key для отправки сообщений группе
-   **Pairwise → Group sessions**: распределение sender key через pairwise сессии для безопасности
-   **Ratchet при изменении состава**: полный re-key при добавлении/удалении участников для поддержки forward secrecy
-   **Forward secrecy**: каждый участник имеет уникальный ключ для группы, предотвращающий чтение старых сообщений при компрометации ключа

**6. Звонки (WebRTC)**

Установление голосовых/видеозвонков с NAT traversal:

**Процесс:**
-   **SDP negotiation**: обмен `SDP` (Session Description Protocol) через `Signal Server` для согласования параметров медиа
-   **ICE candidates**: обмен `ICE` (Interactive Connectivity Establishment) candidates для обнаружения оптимального пути соединения
-   **STUN/TURN fallback**: использование `STUN` для обнаружения публичного IP, `TURN` для relay при невозможности P2P соединения
-   **Адаптивный bitrate**: автоматическая адаптация битрейта на основе качества сети для плавного разговора

**Примеры реализации:**

```kotlin
// ✅ Signal Protocol usage with Double Ratchet
val session = SessionBuilder(recipientAddress)
    .buildSenderSession()  // Создание или получение сессии
val ciphertext = SessionCipher(session)
    .encrypt(plaintext.toByteArray())  // Шифрование с forward secrecy

// ✅ WebSocket send with ack confirmation
ws.send(MessageProto(id, encrypted, timestamp))
// Ожидание подтверждения от сервера
ackFlow.first { it.msgId == id }  // Блокирующее ожидание ack

// ✅ Offline queue with retry logic
if (!networkAvailable) {
    db.insertPending(msg)  // Сохранение в локальную очередь
} else {
    sendAndRetry(msg)  // Отправка с exponential backoff
}
```

### Сервер: Маршрутизация

**Границы сервисов:**

-   **`Chat Service`**: маршрутизация сообщений по `userId` получателя, хранение зашифрованных сообщений в `Cassandra` (server не видит plaintext — zero-knowledge architecture), доставка через `WebSocket` для онлайн пользователей или `push` для офлайн, автоматическое удаление после доставки (TTL 30 дней) для оптимизации хранилища
-   **`Presence Service`**: обработка heartbeat каждые 30 секунд для отслеживания онлайн статусов, кэширование в `Redis` с TTL 45 секунд для быстрого доступа, `pub/sub` для realtime обновлений статусов контактов
-   **`Media Service`**: обработка `multipart upload` для больших файлов (чанки 4-8MB), автоматическая генерация `thumbnails` для превью, доставка через `CDN` (`CloudFront`/`Cloudflare`) для глобальной доступности, хранение E2EE ключа в metadata для расшифровки получателем
-   **`Call Signaling Service`**: ретрансляция `SDP`/`ICE` candidates между участниками звонка, не участвует в медиа-потоке (P2P соединение через `WebRTC` для минимальной латентности)
-   **`Push Service`**: интеграция с `FCM` для фоновых уведомлений, приоритизация (`high` для звонков для немедленного пробуждения, `normal` для сообщений), группировка уведомлений по чатам (Android 13+)

### E2E Шифрование И Signal Protocol

**Архитектура шифрования:**

`Signal Protocol` — криптографический протокол для E2E шифрования с гарантиями forward secrecy и защиты от MITM атак.

**Identity Keys:**

-   **Долгосрочные ключи**: `ed25519` ключи для аутентификации устройств — каждый пользователь имеет уникальный identity key pair, публичный ключ используется для проверки подлинности
-   **Валидация**: проверка через QR-код safety numbers — визуальное сравнение числовых отпечатков для предотвращения MITM атак при первой установке сессии
-   **Хранение**: безопасное хранение private key в `Android Keystore` с `StrongBox` support для защиты от физических атак

**Pre-Keys:**

-   **Одноразовые ключи**: пачка из 100 одноразовых `ECDH` ключей, загружаемых на сервер для инициации сессии с оффлайн пользователем
-   **Использование**: когда пользователь офлайн, отправитель использует pre-key для установки сессии без необходимости интерактивного обмена ключами
-   **Обновление**: автоматическая загрузка новых pre-keys при исчерпании запаса для непрерывной доступности

**`Double` Ratchet:**

Механизм обновления ключей для обеспечения forward secrecy:

-   **DH Ratchet**: обновление session key через `Diffie-Hellman` key exchange при каждом отправленном сообщении — новый ключ для каждого сообщения
-   **Symmetric Ratchet**: обновление ключа шифрования через одностороннюю функцию (KDF) для обеспечения forward secrecy даже без получения ответа
-   **Out-of-order доставка**: поддержка расшифровки сообщений при неупорядоченной доставке через счетчик сообщений и хранение промежуточных ключей

**Group Sessions:**

-   **Sender keys**: каждый участник группы имеет свой sender key для эффективной отправки сообщений всей группе
-   **Распределение**: sender key распределяется через pairwise сессии (1-to-1) для безопасности — каждый участник получает ключ отдельно
-   **Re-key при изменении состава**: полный re-key при добавлении/удалении участников — старые участники не могут читать новые сообщения, новые не могут читать старые (forward и backward secrecy)

### Хранение Данных

**Cassandra (Messages):**

Оптимизировано для высоконагруженных запросов чтения с партиционированием:

-   **Партиционирование**: партиционирование по `(userId, YYYYMM)` для изоляции данных пользователя и временных периодов — оптимизация запросов по пользователю и месяцу
-   **Clustering**: сортировка по `timestamp DESC` для быстрого получения последних сообщений без дополнительных сортировок
-   **Зашифрованные данные**: хранение только зашифрованных сообщений (server не видит plaintext) — zero-knowledge architecture
-   **TTL**: автоматическое удаление через 30 дней для оптимизации хранилища и соответствия политике хранения
-   **Replication Factor**: RF=3 для надежности и возможности чтения из nearest datacenter
-   **Eventual consistency**: eventual consistency модели для высокой производительности при миллиардах сообщений в день

**PostgreSQL (Users, Groups):**

Strong consistency для метаданных пользователей и групп:

-   **Strong consistency**: гарантия консистентности для критичных операций (регистрация, изменение профиля, управление группами)
-   **Индексы**: индексы на `phoneNumber` и `userId` для быстрого поиска пользователей
-   **Replication**: master-slave replication для масштабирования чтений без нагрузки на master

**Redis (Presence):**

Быстрый кеш для presence данных с TTL-based eviction:

-   **Presence кеш**: `presence:{userId}` с TTL 45 секунд — автоматическое удаление при отсутствии heartbeat
-   **Typing индикаторы**: `typing:{chatId}:{userId}` с TTL 10 секунд — индикация набора текста в реальном времени
-   **Pub/Sub**: использование `Pub/Sub` для realtime распространения обновлений статусов контактов

**S3 (Media):**

`Lifecycle` management для оптимизации стоимости хранилища:

-   **`Lifecycle` policies**: автоматический переход `Standard` → `Glacier` → `Delete` для экономии на неиспользуемых медиа
-   **Pre-signed URLs**: временные подписанные URL с TTL 1 час для безопасного доступа к медиафайлам без раскрытия прямых ссылок
-   **CDN caching**: кэширование на `CloudFront` edge серверах для глобальной доставки с низкой латентностью

### Доставка Сообщений

**At-least-once гарантия доставки:**

-   **Client retry**: клиент автоматически ресендит сообщение до получения ack от сервера — гарантия доставки даже при временных сетевых сбоях
-   **Server deduplication**: сервер дедуплицирует дубликаты по `messageId` и `idempotency tokens` — предотвращение дублирования при retry
-   **Idempotency tokens**: уникальный токен для каждого запроса отправки, позволяющий безопасно повторять отправку без создания дубликатов

**Ordered delivery (упорядоченная доставка):**

-   **Server-side timestamp**: сервер присваивает timestamp при получении сообщения для единообразного упорядочивания — предотвращение расхождений из-за различий в локальном времени клиентов
-   **Client sorting**: клиент сортирует сообщения по `timestamp` + `messageId` для разрешения конфликтов при одинаковом timestamp — детерминированное упорядочивание
-   **Vector clocks для групп**: использование vector clocks для causal ordering в группах — корректное упорядочивание при параллельных сообщениях от разных участников

**Offline queueing (офлайн очередь):**

-   **Server storage**: сервер хранит неотправленные сообщения до 30 дней для доставки при восстановлении соединения получателя
-   **Batch sync**: клиент синхронизирует пропущенные сообщения через batch fetch с `last_sync_timestamp` для эффективной загрузки — загрузка только новых сообщений с последней синхронизации
-   **Push notification**: `FCM` push notification для пробуждения клиента при получении нового сообщения в офлайне — минимизация задержки доставки

### Масштабирование

**Шардирование (Sharding):**

-   **Chat `Service`**: партиционирование по hash от `userId` через consistent hashing — равномерное распределение нагрузки между инстансами сервиса
-   **Cassandra partitioning**: партиционирование сообщений по `userId` для изоляции данных пользователей и горизонтального масштабирования

**Connection pooling:**

-   **WebSocket gateways**: stateful `WebSocket` gateways для поддержки persistent connections — низкая латентность для realtime обновлений
-   **Horizontal scaling**: горизонтальное масштабирование со sticky sessions через load balancer — обеспечение того, что клиент всегда подключается к тому же gateway инстансу

**Read replicas:**

-   **PostgreSQL**: master-slave replication для масштабирования чтений без нагрузки на master — распределение read-only запросов на replicas
-   **Cassandra**: RF=3 (Replication Factor) для чтения из nearest datacenter — снижение latency для глобальной аудитории через географическое распределение

**`Message` queue:**

-   **Kafka**: async обработка для `push` уведомлений и analytics событий — неблокирующая обработка для улучшения latency отправки сообщений
-   **Partitioning**: партиционирование по `userId` для гарантии порядка обработки сообщений одного пользователя
-   **Retention**: хранение событий 7 дней для аналитики и отладки

**Auto-scaling:**

-   **Kubernetes HPA**: автоматическое масштабирование на основе connection count для `WebSocket` gateways — добавление инстансов при росте количества подключений
-   **`Queue` depth**: масштабирование `Chat Service` workers на основе глубины очереди сообщений — обеспечение обработки пиковых нагрузок

### Оптимизация Производительности

**Батарея:**

-   **Heartbeat frequency**: heartbeat каждые 30 секунд для поддержания `WebSocket` соединения — баланс между надежностью соединения и расходом батареи
-   **Push coalescing**: объединение нескольких push-уведомлений в одно для снижения частоты пробуждения устройства — экономия батареи
-   **WebSocket keep-alive**: увеличение интервала keep-alive в фоне (с 30s до 60-90s) для снижения активности при неактивном использовании

**Сеть:**

-   **Protobuf compression**: использование `Protocol Buffers` для сжатия данных вместо JSON — снижение размера payload на 30-50%
-   **Batch receipts**: отправка read receipts батчами (раз в 5-10 секунд) вместо каждого сообщения — снижение количества HTTP-запросов
-   **Delta sync**: синхронизация только новых сообщений с `last_sync_timestamp` — загрузка только изменений, не полного состояния
-   **Prefetch частых контактов**: предзагрузка сообщений и метаданных для часто используемых контактов — улучшение UX при открытии чата

**Память:**

-   **`Message` pagination**: загрузка только 20-50 сообщений за раз в UI с lazy loading при скролле — предотвращение перегрузки памяти большими чатами
-   **Lazy load медиа**: загрузка медиафайлов только при открытии/просмотре, не при загрузке списка чатов
-   **LRU cache**: кеширование декодированных изображений в памяти с LRU eviction policy (~50MB limit) — быстрый доступ к превью без повторного декодирования

### Офлайн Режим

**Локальное хранилище:**

-   **`Room`/SQLite**: персистентное хранилище для сообщений, контактов, групп в локальной `Room` database — доступ к данным даже без сети
-   **Индексы**: оптимизированные индексы для быстрого поиска по тексту сообщений (`FTS`), контактам, группам

**Очередь отправки:**

-   **Pending sends queue**: сохранение неотправленных сообщений в `Room` database со статусом `pending` для автоматической отправки при восстановлении сети
-   **Retry логика**: автоматический retry с exponential backoff при ошибках сети для надежной доставки

**Синхронизация при онлайне:**

-   **Batch sync**: автоматическая синхронизация пропущенных сообщений при восстановлении сети через batch fetch с `last_sync_timestamp`
-   **WorkManager**: использование `WorkManager` для фоновой синхронизации с constraints (сеть, зарядка) — продолжает работу даже при закрытом приложении

**Conflict resolution:**

-   **Server wins для metadata**: при конфликтах метаданных (имя контакта, аватар группы) — приоритет серверной версии для консистентности
-   **Merge для messages**: при конфликтах сообщений — объединение с сортировкой по timestamp для сохранения всех сообщений

### Детальная Реализация (Staff-level)

**Архитектура модулей:**

Модульная структура для независимой разработки и тестирования:
-   **feature-chat**: модуль чата — UI, отправка/получение сообщений, список чатов
-   **feature-media**: модуль медиа — обработка изображений, видео, аудио, загрузка/загрузка
-   **crypto**: модуль криптографии — `Signal Protocol` implementation, управление ключами
-   **sync**: модуль синхронизации — синхронизация между устройствами, offline queue
-   **notifications**: модуль уведомлений — `FCM` интеграция, группировка, приоритизация
-   **flags**: feature flags — динамическое управление функциональностью
-   **analytics**: модуль аналитики — метрики производительности, ошибки

**Хранилище:**

-   **`Room` database**: локальное хранилище с `protobuf` сущностями для эволюции схемы — позволяет добавлять новые поля без миграций БД через расширение protobuf messages

**Модель данных:**

**`Thread` (чат):**
-   `threadId`: уникальный идентификатор чата (1-to-1 или группа)
-   `participants`: список участников чата
-   `lastMessageId`: ID последнего сообщения для быстрого доступа
-   `unreadCount`: количество непрочитанных сообщений для badge
-   `lastActivityAt`: timestamp последней активности для сортировки списка чатов

**`Message` (сообщение):**
-   `localId`: локальный `ULID` для упорядочивания до получения `globalId` от сервера
-   `globalId`: уникальный ID от сервера для синхронизации между устройствами
-   `threadId`: связь с чатом
-   `senderId`: ID отправителя
-   `createdAt`: timestamp создания
-   `sendState`: состояние отправки (`QUEUED`, `ENCRYPTED`, `UPLOADING`, `SENT`, `DELIVERED`)
-   `receiptState`: состояние прочтения (`SENT`, `DELIVERED`, `READ`)
-   `body`: текст сообщения (зашифрованный)
-   `mediaRef`: ссылка на медиафайл (если есть)

**Attachment (вложение):**
-   `id`: уникальный ID вложения
-   `messageLocalId`: связь с сообщением
-   `status`: статус загрузки (`PENDING`, `UPLOADING`, `UPLOADED`, `FAILED`)
-   `mediaKey`: ключ расшифровки (зашифрованный через `Signal Protocol`)
-   `size`: размер файла
-   `chunkCount`: количество чанков для возобновляемой загрузки
-   `thumbRef`: ссылка на thumbnail

**ID и упорядочивание:**

-   **ULID локально**: использование `ULID` для генерации локальных ID до получения `globalId` от сервера — обеспечивает упорядочивание даже до синхронизации
-   **GlobalId от сервера**: сервер присваивает `globalId` при получении сообщения для синхронизации между устройствами
-   **Reconcile по clientTag**: разрешение конфликтов при синхронизации через `clientTag` для идентификации локальных сообщений

**Криптография:**

-   **`Double` Ratchet/Noise**: использование `Double Ratchet` алгоритма для 1-to-1 сообщений, `Noise Protocol` для групп
-   **Sender-key для групп**: эффективное групповое шифрование через sender keys вместо pairwise сессий
-   **Per-device identity**: каждый пользователь имеет уникальный identity key на каждом устройстве для безопасности
-   **Хранение ключей**: `SQLCipher` для зашифрованной БД, `EncryptedFile` для медиафайлов на диске — защита ключей от физического доступа
-   **Бэкап**: бэкап с клиентским ключом шифрования и восстановлением через пользовательский секрет/`Android Keystore` — безопасное резервное копирование

**Пайплайн отправки:**

OUTBOX state machine для надежной доставки:
-   **`QUEUED`**: сообщение добавлено в очередь отправки
-   **`ENCRYPTED`**: сообщение зашифровано через `Signal Protocol`
-   **`UPLOADING`**: медиа (если есть) загружается на сервер
-   **`SENT`**: сообщение отправлено на сервер и получен ack
-   **`DELIVERED`**: сообщение доставлено на устройство получателя
-   **`READ`**: сообщение прочитано получателем

**Транспорт:**

-   **Foreground**: активный `WebSocket`/`MQTT` сокет для realtime обновлений и минимальной латентности
-   **Background**: `FCM` data payload для пробуждения + короткий fetch для синхронизации — экономия батареи в фоне
-   **Адаптивный heartbeat**: увеличение интервала heartbeat в фоне (30s → 60-90s) для снижения расхода батареи

**Упорядочивание:**

-   **Приоритет globalId**: использование `globalId` от сервера для упорядочивания если доступен
-   **Fallback**: использование `ULID` + server timestamp для упорядочивания до получения `globalId`

**Вложения (Attachments):**

-   **Шифрование**: `AES-GCM` шифрование медиафайла перед загрузкой для E2E защиты
-   **Чанковая загрузка**: разбиение файла на чанки 4-8MB для возобновляемости при обрыве сети
-   **Resumable upload**: возобновление загрузки по индексу чанка — сервер сообщает последний успешно загруженный чанк
-   **Превью/thumbnail**: генерация и шифрование thumbnail для быстрого превью (также зашифровано через `AES-GCM`)
-   **Exponential backoff**: увеличение интервала retry при ошибках загрузки (1s, 2s, 4s, 8s)

**Уведомления (Android 13-15):**

-   **FCM data payload**: отправка минимального payload через `FCM` для пробуждения приложения
-   **Notification metadata**: уведомление с минимумом данных (имя отправителя, preview текста) для конфиденциальности
-   **Разрешение на уведомления**: обработка нового flow разрешений на уведомления в Android 13+
-   **Группировка**: группировка уведомлений по `threadId` для удобства (Android 13+)
-   **Read-sync**: синхронизация read status при открытии приложения для обновления уведомлений

**Фоновая работа:**

-   **WorkManager**: использование `WorkManager` для background sync и backfill с constraints
-   **Constraints**: ограничения (unmetered network или user-allowed) для экономии мобильного трафика
-   **Doze Mode**: уважение `Doze Mode` и `App Standby` — выполнение только в maintenance windows

**Поиск и гигиена:**

-   **FTS (Full-Text Search)**: полнотекстовый поиск по сообщениям с политиками безопасности (не индексировать E2E зашифрованный контент, только локально расшифрованные)
-   **LRU/age eviction**: автоматическое удаление больших медиафайлов по LRU или возрасту для освобождения места
-   **Настройки автоскачивания**: пользовательские настройки для автоматической загрузки медиа (Wi-Fi only, всегда, никогда)

**Анти‑спам и защита от злоупотреблений:**

-   **Локальные лимиты**: ограничение частоты отправки сообщений на клиенте для предотвращения spam
-   **Списки блокировок**: локальное хранение списков блокировок с синхронизацией между устройствами
-   **Серверные сигналы**: получение сигналов от сервера о потенциально опасных сообщениях (ML-based detection)
-   **Предупреждающий UX**: отображение предупреждений пользователю при подозрительных сообщениях, задержка preview для проверки

**Наблюдаемость и релиз:**

**Метрики производительности:**
-   **p95 отправки**: 95-й перцентиль времени отправки сообщения — должен быть <200ms
-   **tap-to-open**: время от tap на уведомление до открытия чата — индикатор UX
-   **Reconnect rate**: частота переподключений `WebSocket` — индикатор стабильности соединения
-   **Задержки ack**: время от отправки до получения ack от сервера — индикатор сетевой latency
-   **Crash/ANR**: мониторинг крэшей и `ANR` для стабильности

**Стратегия релиза:**
-   **Staged rollout**: поэтапный запуск новых фич (1% → 5% → 25% → 100%) с мониторингом метрик на каждом этапе
-   **Kill-switch для сокета**: feature flag для экстренного отключения `WebSocket` и перехода на fallback (long-polling) при проблемах

## Answer (EN)

`WhatsApp` is an E2E‑encrypted messenger involving: 1-to-1 and group messaging, media files (images, video, audio), delivery/read statuses, E2E encryption via `Signal Protocol` with forward secrecy, voice/video calls via `WebRTC`, and offline persistence with sync on network recovery.

### Requirements

**Functional:**

**Messaging:**
-   Text messages with formatting support (bold, italic, monospace)
-   Media files: images (`JPEG`, `PNG`, `WEBP`), video (`H.264`, `H.265`), audio (`Opus`, `AAC`), documents
-   Voice messages with real-time recording and compression

**Groups:**
-   Create groups up to 256 participants (for small groups — up to 32 for optimization)
-   Participant management (add/remove), change name/avatar
-   Group settings (who can send messages, admins)

**Delivery statuses:**
-   `sent` — message sent from client
-   `delivered` — message delivered to server and recipient device
-   `read` — message read by recipient (double checkmark)

**Security:**
-   E2E encryption via `Signal Protocol` with forward secrecy (each message has unique key)
-   Device verification via QR code safety numbers to prevent MITM attacks
-   Block and report users

**Presence:**
-   Real-time `online`/`offline` statuses
-   `last seen` — last visit time (with privacy settings)

**Push notifications:**
-   `FCM` (Firebase Cloud Messaging) integration for background notifications
-   Notification grouping by chats (Android 13+)

**Calls:**
-   Voice and video calls via `WebRTC`
-   `STUN`/`TURN` servers for NAT traversal
-   Adaptive bitrate for quality optimization on poor connections

**Non-functional:**

-   **Low latency**: <200ms (P95) from "Send" tap to server delivery — critical for real-time feel
-   **High availability**: >99.9% uptime for critical operations (send/receive messages)
-   **Scale**: support billions of messages per day via horizontal scaling
-   **Privacy**: zero-knowledge server — server blind to plaintext, only encrypted data
-   **Battery/bandwidth efficiency**: optimize heartbeat frequency, batch sending, data compression
-   **Offline support**: unsent message queue, sync on network recovery

### Architecture

**Android client:**

Modular architecture with clear separation of responsibility:
-   **`Room` database**: local storage for messages, contacts, groups with indexes for fast search and pagination
-   **E2EE engine**: `Signal Protocol` encryption engine for encrypt/decrypt messages, key management
-   **WebSocket**: realtime channel for receiving messages, status updates, presence
-   **Media cache**: multi-level cache (`Memory` → `Disk`) for media files with LRU eviction policy

**Backend:**

Microservices architecture with horizontal scaling:
-   **Load Balancer**: load distribution across instances, sticky sessions for `WebSocket` connections
-   **Microservices**: `Chat Service` (message routing), `Presence Service` (online statuses), `Media Service` (upload/delivery), `Call Signaling Service` (`WebRTC` signaling), `Push Service` (`FCM` integration)
-   **Data storage**: `Kafka` for async event processing, `Cassandra` for messages (partitioning, TTL), `PostgreSQL` for users/groups (strong consistency), `S3`+`CDN` for media (lifecycle policies), `Redis` for presence cache (TTL-based)

### Android Client: Key Flows

**1. Send `Message`**

Multi-step sending process with delivery guarantee and encryption:

**Steps:**
1.   **Encryption**: apply `Signal Protocol` `Double` Ratchet to encrypt plaintext — each session has unique keys for forward secrecy
2.   **Local store**: save message to `Room` database with `pending` status — enables displaying message in UI before delivery confirmation (optimistic UI)
3.   **WebSocket send**: send encrypted message via `WebSocket` for minimal latency
4.   **Server ack**: receive server confirmation and update status to `delivered` — guarantee server delivery
5.   **Recipient receipt**: receive read receipt from recipient and update status to `read` — indicates message read

**2. Receive `Message`**

Incoming message processing with decryption and synchronization:

**Steps:**
1.   **WebSocket receive**: receive encrypted message via `WebSocket`
2.   **Decrypt**: apply `Signal Protocol` to decrypt ciphertext to plaintext
3.   **Room DB save**: write decrypted message to `Room` database with indexes for fast search
4.   **UI update**: update UI via `Flow`/`LiveData` for reactive new message display
5.   **Read receipt**: automatically send read receipt on chat open or message read

**3. Media Processing**

Media file upload with encryption and optimization:

**Steps:**
1.   **Compression**: compress media (images: `JPEG`/`WEBP`, video: `H.264` with 2-4 Mbps bitrate for bandwidth savings)
2.   **Encryption**: `AES-GCM` encrypt media file with key for E2E protection
3.   **Upload to CDN**: upload encrypted file to `S3` with subsequent delivery via `CDN` for global availability
4.   **Send metadata**: send media `URL`, `thumbnail` for preview, and `decryption key` (encrypted via `Signal Protocol`) to recipient
5.   **Lazy load**: load media only on open/view for bandwidth and battery savings

**4. Offline Mode**

Unsent message queue with automatic synchronization:

**Mechanism:**
-   **Unsent queue**: save unsent messages to `Room` database with `pending` status
-   **Storage**: persistent storage up to 30 days to guarantee delivery even on prolonged network absence
-   **Automatic resend**: automatic sending on network recovery via `WorkManager` with constraints
-   **Exponential backoff**: increase retry interval on errors (1s, 2s, 4s, 8s) to prevent server overload

**5. Group Messages**

Efficient group message delivery with E2E encryption:

**Mechanism:**
-   **Sender keys**: each group participant has sender key for sending group messages
-   **Pairwise → Group sessions**: distribute sender key via pairwise sessions for security
-   **Ratchet on membership changes**: full re-key on add/remove participants to maintain forward secrecy
-   **Forward secrecy**: each participant has unique group key preventing old message reading on key compromise

**6. Calls (WebRTC)**

Voice/video call establishment with NAT traversal:

**Process:**
-   **SDP negotiation**: exchange `SDP` (Session Description Protocol) via `Signal Server` to agree media parameters
-   **ICE candidates**: exchange `ICE` (Interactive Connectivity Establishment) candidates to discover optimal connection path
-   **STUN/TURN fallback**: use `STUN` to discover public IP, `TURN` for relay when P2P connection impossible
-   **Adaptive bitrate**: automatically adapt bitrate based on network quality for smooth conversation

### Server: Routing

**`Service` boundaries:**

-   **`Chat Service`**: route messages by recipient `userId`, store encrypted messages in `Cassandra` (server blind to plaintext — zero-knowledge architecture), deliver via `WebSocket` for online users or `push` for offline, automatic deletion after delivery (TTL 30 days) for storage optimization
-   **`Presence Service`**: process heartbeat every 30 seconds to track online statuses, cache in `Redis` with 45 second TTL for fast access, `pub/sub` for realtime contact status updates
-   **`Media Service`**: handle `multipart upload` for large files (4-8MB chunks), automatic `thumbnail` generation for preview, delivery via `CDN` (`CloudFront`/`Cloudflare`) for global availability, store E2EE key in metadata for recipient decryption
-   **`Call Signaling Service`**: relay `SDP`/`ICE` candidates between call participants, does not participate in media stream (P2P connection via `WebRTC` for minimal latency)
-   **`Push Service`**: `FCM` integration for background notifications, prioritization (`high` for calls for immediate wake, `normal` for messages), notification grouping by chats (Android 13+)

### E2E Encryption and Signal Protocol

**Encryption architecture:**

`Signal Protocol` — cryptographic protocol for E2E encryption with forward secrecy guarantees and MITM attack protection.

**Identity Keys:**

-   **`Long`-term keys**: `ed25519` keys for device authentication — each user has unique identity key pair, public key used for authenticity verification
-   **Validation**: verification via QR code safety numbers — visual comparison of numeric fingerprints to prevent MITM attacks on first session setup
-   **Storage**: secure private key storage in `Android Keystore` with `StrongBox` support for protection against physical attacks

**Pre-Keys:**

-   **One-time keys**: batch of 100 one-time `ECDH` keys uploaded to server for initiating session with offline user
-   **Usage**: when user offline, sender uses pre-key to establish session without need for interactive key exchange
-   **Refresh**: automatic upload of new pre-keys when supply exhausted for continuous availability

**`Double` Ratchet:**

Key update mechanism to ensure forward secrecy:

-   **DH Ratchet**: session key update via `Diffie-Hellman` key exchange on each sent message — new key per message
-   **Symmetric Ratchet**: encryption key update via one-way function (KDF) to ensure forward secrecy even without receiving response
-   **Out-of-order delivery**: support decryption of messages on out-of-order delivery via message counter and intermediate key storage

**Group Sessions:**

-   **Sender keys**: each group participant has sender key for efficient group message sending
-   **Distribution**: sender key distributed via pairwise sessions (1-to-1) for security — each participant receives key separately
-   **Re-key on membership changes**: full re-key on add/remove participants — old participants cannot read new messages, new cannot read old (forward and backward secrecy)

### Data Storage

**Cassandra (Messages):**

Optimized for high-throughput read queries with partitioning:

-   **Partitioning**: partition by `(userId, YYYYMM)` to isolate user data and time periods — optimize queries by user and month
-   **Clustering**: sort by `timestamp DESC` for fast last message retrieval without additional sorting
-   **Encrypted data**: store only encrypted messages (server blind to plaintext) — zero-knowledge architecture
-   **TTL**: automatic deletion after 30 days for storage optimization and retention policy compliance
-   **Replication Factor**: RF=3 for reliability and ability to read from nearest datacenter
-   **Eventual consistency**: eventual consistency model for high performance with billions of messages per day

**PostgreSQL (Users, Groups):**

Strong consistency for user and group metadata:

-   **Strong consistency**: guarantee consistency for critical operations (registration, profile changes, group management)
-   **Indexes**: indexes on `phoneNumber` and `userId` for fast user search
-   **Replication**: master-slave replication to scale reads without master load

**Redis (Presence):**

Fast cache for presence data with TTL-based eviction:

-   **Presence cache**: `presence:{userId}` with 45 second TTL — automatic deletion on missing heartbeat
-   **Typing indicators**: `typing:{chatId}:{userId}` with 10 second TTL — real-time typing indication
-   **Pub/Sub**: use `Pub/Sub` for realtime distribution of contact status updates

**S3 (Media):**

`Lifecycle` management for storage cost optimization:

-   **`Lifecycle` policies**: automatic transition `Standard` → `Glacier` → `Delete` for savings on unused media
-   **Pre-signed URLs**: temporary signed URLs with 1 hour TTL for secure media access without exposing direct links
-   **CDN caching**: caching on `CloudFront` edge servers for global delivery with low latency

### `Message` Delivery

**At-least-once delivery guarantee:**

-   **Client retry**: client automatically resends message until server ack received — guarantees delivery even on temporary network failures
-   **Server deduplication**: server deduplicates duplicates by `messageId` and `idempotency tokens` — prevents duplication on retry
-   **Idempotency tokens**: unique token per send request, allowing safe retry without creating duplicates

**Ordered delivery:**

-   **Server-side timestamp**: server assigns timestamp on message receipt for uniform ordering — prevents discrepancies from client time differences
-   **Client sorting**: client sorts messages by `timestamp` + `messageId` to resolve conflicts on same timestamp — deterministic ordering
-   **Vector clocks for groups**: use vector clocks for causal ordering in groups — correct ordering on parallel messages from different participants

**Offline queueing:**

-   **Server storage**: server stores undelivered messages up to 30 days for delivery on recipient connection recovery
-   **Batch sync**: client syncs missed messages via batch fetch with `last_sync_timestamp` for efficient loading — load only new messages since last sync
-   **Push notification**: `FCM` push notification to wake client on new message received offline — minimizes delivery delay

### Scalability

**Sharding:**

-   **Chat `Service`**: partition by `userId` hash via consistent hashing — even load distribution across service instances
-   **Cassandra partitioning**: partition messages by `userId` to isolate user data and enable horizontal scaling

**Connection pooling:**

-   **WebSocket gateways**: stateful `WebSocket` gateways to support persistent connections — low latency for realtime updates
-   **Horizontal scaling**: horizontal scaling with sticky sessions via load balancer — ensure client always connects to same gateway instance

**Read replicas:**

-   **PostgreSQL**: master-slave replication to scale reads without master load — distribute read-only queries to replicas
-   **Cassandra**: RF=3 (Replication Factor) to read from nearest datacenter — reduce latency for global audience via geographic distribution

**`Message` queue:**

-   **Kafka**: async processing for `push` notifications and analytics events — non-blocking processing to improve message send latency
-   **Partitioning**: partition by `userId` to guarantee message ordering for same user
-   **Retention**: store events 7 days for analytics and debugging

**Auto-scaling:**

-   **Kubernetes HPA**: auto-scale based on connection count for `WebSocket` gateways — add instances on connection growth
-   **`Queue` depth**: scale `Chat Service` workers based on message queue depth — handle peak loads

### Performance Optimization

**Battery:**

-   **Heartbeat frequency**: heartbeat every 30 seconds to maintain `WebSocket` connection — balance connection reliability and battery usage
-   **Push coalescing**: combine multiple push notifications into one to reduce device wake frequency — battery savings
-   **WebSocket keep-alive**: increase keep-alive interval in background (from 30s to 60-90s) to reduce activity on inactive usage

**Network:**

-   **Protobuf compression**: use `Protocol Buffers` for data compression instead of JSON — reduce payload size by 30-50%
-   **Batch receipts**: send read receipts in batches (every 5-10 seconds) instead of per message — reduce HTTP request count
-   **Delta sync**: sync only new messages with `last_sync_timestamp` — load only changes, not full state
-   **Prefetch frequent contacts**: preload messages and metadata for frequently used contacts — improve UX on chat open

**Memory:**

-   **`Message` pagination**: load only 20-50 messages at a time in UI with lazy loading on scroll — prevent memory overload on large chats
-   **Lazy load media**: load media files only on open/view, not on chat list load
-   **LRU cache**: cache decoded images in memory with LRU eviction policy (~50MB limit) — fast preview access without re-decoding

### Offline Mode

**Local storage:**

-   **`Room`/SQLite**: persistent storage for messages, contacts, groups in local `Room` database — access data even without network
-   **Indexes**: optimized indexes for fast search by message text (`FTS`), contacts, groups

**Send queue:**

-   **Pending sends queue**: save unsent messages to `Room` database with `pending` status for automatic sending on network recovery
-   **Retry logic**: automatic retry with exponential backoff on network errors for reliable delivery

**Sync on online:**

-   **Batch sync**: automatic synchronization of missed messages on network recovery via batch fetch with `last_sync_timestamp`
-   **WorkManager**: use `WorkManager` for background sync with constraints (network, charging) — continues even when app closed

**Conflict resolution:**

-   **Server wins for metadata**: on metadata conflicts (contact name, group avatar) — prioritize server version for consistency
-   **Merge for messages**: on message conflicts — merge with timestamp sorting to preserve all messages

### Detailed Implementation (Staff-level)

**Module architecture:**

Modular structure for independent development and testing:
-   **feature-chat**: chat module — UI, send/receive messages, chat list
-   **feature-media**: media module — image, video, audio processing, upload/download
-   **crypto**: cryptography module — `Signal Protocol` implementation, key management
-   **sync**: sync module — synchronization across devices, offline queue
-   **notifications**: notifications module — `FCM` integration, grouping, prioritization
-   **flags**: feature flags — dynamic functionality control
-   **analytics**: analytics module — performance metrics, errors

**Storage:**

-   **`Room` database**: local storage with `protobuf` entities for schema evolution — allows adding new fields without DB migrations via protobuf message extension

**Data model:**

**`Thread` (chat):**
-   `threadId`: unique chat identifier (1-to-1 or group)
-   `participants`: chat participants list
-   `lastMessageId`: last message ID for fast access
-   `unreadCount`: unread message count for badge
-   `lastActivityAt`: last activity timestamp for chat list sorting

**`Message`:**
-   `localId`: local `ULID` for ordering before receiving server `globalId`
-   `globalId`: unique server ID for synchronization across devices
-   `threadId`: link to chat
-   `senderId`: sender ID
-   `createdAt`: creation timestamp
-   `sendState`: send state (`QUEUED`, `ENCRYPTED`, `UPLOADING`, `SENT`, `DELIVERED`)
-   `receiptState`: receipt state (`SENT`, `DELIVERED`, `READ`)
-   `body`: message text (encrypted)
-   `mediaRef`: media file reference (if present)

**Attachment:**
-   `id`: unique attachment ID
-   `messageLocalId`: link to message
-   `status`: upload status (`PENDING`, `UPLOADING`, `UPLOADED`, `FAILED`)
-   `mediaKey`: decryption key (encrypted via `Signal Protocol`)
-   `size`: file size
-   `chunkCount`: chunk count for resumable upload
-   `thumbRef`: thumbnail reference

**ID and ordering:**

-   **Local ULID**: use `ULID` to generate local IDs before receiving server `globalId` — ensures ordering even before sync
-   **GlobalId from server**: server assigns `globalId` on message receipt for cross-device synchronization
-   **Reconcile by clientTag**: resolve conflicts on sync via `clientTag` to identify local messages

**Cryptography:**

-   **`Double` Ratchet/Noise**: use `Double Ratchet` algorithm for 1-to-1 messages, `Noise Protocol` for groups
-   **Sender-key for groups**: efficient group encryption via sender keys instead of pairwise sessions
-   **Per-device identity**: each user has unique identity key per device for security
-   **Key storage**: `SQLCipher` for encrypted DB, `EncryptedFile` for media files on disk — protect keys from physical access
-   **Backup**: backup with client-held encryption key and restore via user secret/`Android Keystore` — secure backup

**Send pipeline:**

OUTBOX state machine for reliable delivery:
-   **`QUEUED`**: message added to send queue
-   **`ENCRYPTED`**: message encrypted via `Signal Protocol`
-   **`UPLOADING`**: media (if present) uploading to server
-   **`SENT`**: message sent to server and ack received
-   **`DELIVERED`**: message delivered to recipient device
-   **`READ`**: message read by recipient

**Transport:**

-   **Foreground**: active `WebSocket`/`MQTT` socket for realtime updates and minimal latency
-   **Background**: `FCM` data payload to wake + short fetch for sync — battery savings in background
-   **Adaptive heartbeat**: increase heartbeat interval in background (30s → 60-90s) to reduce battery drain

**Ordering:**

-   **Priority globalId**: use server `globalId` for ordering if available
-   **Fallback**: use `ULID` + server timestamp for ordering before receiving `globalId`

**Attachments:**

-   **Encryption**: `AES-GCM` encrypt media file before upload for E2E protection
-   **Chunked upload**: split file into 4-8MB chunks for resumability on network interruption
-   **Resumable upload**: resume upload by chunk index — server reports last successfully uploaded chunk
-   **Preview/thumbnail**: generate and encrypt thumbnail for fast preview (also encrypted via `AES-GCM`)
-   **Exponential backoff**: increase retry interval on upload errors (1s, 2s, 4s, 8s)

**Notifications (Android 13-15):**

-   **FCM data payload**: send minimal payload via `FCM` to wake application
-   **Notification metadata**: notification with minimal data (sender name, text preview) for privacy
-   **Notification permission**: handle new notification permission flow in Android 13+
-   **Grouping**: group notifications by `threadId` for convenience (Android 13+)
-   **Read-sync**: sync read status on app open to update notifications

**Background work:**

-   **WorkManager**: use `WorkManager` for background sync and backfill with constraints
-   **Constraints**: constraints (unmetered network or user-allowed) to save mobile data
-   **Doze Mode**: respect `Doze Mode` and `App Standby` — execute only in maintenance windows

**Search and hygiene:**

-   **FTS (Full-Text Search)**: full-text search on messages with security policies (do not index E2E encrypted content, only locally decrypted)
-   **LRU/age eviction**: automatic deletion of large media files by LRU or age to free space
-   **Auto-download settings**: user settings for automatic media download (Wi-Fi only, always, never)

**Anti‑spam and abuse protection:**

-   **Local limits**: rate limiting message sending on client to prevent spam
-   **Block lists**: local storage of block lists with sync across devices
-   **Server signals**: receive server signals about potentially dangerous messages (ML-based detection)
-   **Warning UX**: display warnings to user on suspicious messages, delay preview for verification

**Observability and release:**

**Performance metrics:**
-   **Send p95**: 95th percentile message send time — should be <200ms
-   **tap-to-open**: time from notification tap to chat open — UX indicator
-   **Reconnect rate**: `WebSocket` reconnection frequency — connection stability indicator
-   **Ack delays**: time from send to server ack — network latency indicator
-   **Crash/ANR**: monitor crashes and `ANR` for stability

**Release strategy:**
-   **Staged rollout**: gradual new feature launch (1% → 5% → 25% → 100%) with metrics monitoring at each stage
-   **Kill-switch for socket**: feature flag to emergency disable `WebSocket` and switch to fallback (long-polling) on issues

---

## Follow-ups

-   How to implement disappearing messages with E2EE?
-   How to handle group key distribution at scale (1000+ members)?
-   How to design multi-device sync while preserving E2EE?
-   How to optimize battery consumption for background WebSocket connections?
-   How to implement message search with E2EE (encrypted at rest)?

## References

-   [Signal Protocol - `Double` Ratchet](https://signal.org/docs/specifications/doubleratchet/)
-   [WebRTC Documentation](https://webrtc.org/)
-   [Cassandra Documentation](https://cassandra.apache.org/doc/latest/)
-   [Android WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)
-   [Room Database](https://developer.android.com/training/data-storage/room)
-   [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)

## Related Questions

### Prerequisites / Concepts

- [[c-service]]
- [[c-retrofit]]
- [[c-media3]]


### Prerequisites (Easier)

-   [[q-database-encryption-android--android--medium]]
-   [[q-deep-link-vs-app-link--android--medium]]

### Related (Same Level)

-   [[q-data-sync-unstable-network--android--hard]]
-   [[q-design-instagram-stories--android--hard]]

### Advanced (Harder)

-   [[q-design-uber-app--android--hard]]
