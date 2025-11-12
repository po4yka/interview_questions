---
id: android-468
title: Design WhatsApp App / Проектирование приложения WhatsApp
aliases:
- Design WhatsApp App
- Проектирование приложения WhatsApp
topic: android
subtopics:
- networking-http
- service
- media
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-service
- q-data-sync-unstable-network--android--hard
- q-database-encryption-android--android--medium
- q-design-instagram-stories--android--hard
created: 2025-10-20
updated: 2025-11-10
tags:
- android/networking-http
- android/service
- android/media
- difficulty/hard
- messaging
- networking
- performance
- realtime
- system-design
sources:
- "https://signal.org/docs/specifications/doubleratchet/"

---

# Вопрос (RU)

> Как спроектировать мессенджер WhatsApp для Android?

## Краткая Версия

Спроектируйте E2E‑зашифрованный Android‑чат для обмена сообщениями 1-to-1 и в малых группах. Система должна обеспечивать низкую латентность отправки, устойчивость офлайн‑доставки и синхронизацию между несколькими устройствами одного пользователя.

## Подробная Версия

Спроектируйте полноценный E2E‑зашифрованный мессенджер WhatsApp для Android со следующими требованиями:

**Производительность:**
- Онлайн‑латентность отправки: <200мс (p95) до подтверждения сервером (server ack)
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
- Анти‑спам и защита от злоупотреблений (на основе метаданных, сигналов и репортов, без доступа к содержимому сообщений)

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
- Online send latency: <200ms (p95) to server acknowledgment (server ack)
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
- Anti‑spam and abuse protection (based on metadata, signals, and reports, without plaintext access)

**Technical details (for discussion):**
- Local data model and indexes (`Room` database)
- Message ID generation and ordering
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
-   Медиафайлы: изображения (`JPEG`, `PNG`, `WEBP`), видео (например, `H.264`, `H.265`), аудио (например, `Opus`, `AAC`), документы — конкретные кодеки выбираются продуктом и не жёстко заданы протоколом
-   Голосовые сообщения с записью в реальном времени и сжатием

**Группы:**
-   Создание групп (типично до 256 участников; для "малых" групп можно оптимизировать UX/поведение под 32+ участников в зависимости от требований продукта)
-   Управление участниками (добавление/удаление), изменение названия/аватара
-   Групповые настройки (кто может отправлять сообщения, админы)

**Статусы доставки:**
-   `sent` — сообщение доставлено на сервер (подтверждено server ack)
-   `delivered` — сообщение доставлено на устройство получателя (сервер получил ack от клиента-получателя)
-   `read` — сообщение прочитано получателем (double checkmark)

**Безопасность:**
-   E2E шифрование через `Signal Protocol` с forward secrecy (каждое сообщение защищено ключом из ратчет-цепочки)
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

-   **Низкая латентность**: <200ms (P95) от нажатия "Отправить" до подтверждения сервером — критично для ощущения real-time общения
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
-   **Хранилище данных**: `Kafka` для async обработки событий, `Cassandra` для сообщений (партиционирование, TTL по политике хранения), `PostgreSQL` для пользователей/групп (strong consistency), `S3`+`CDN` для медиа (lifecycle policies), `Redis` для presence кеша (TTL-based)

### Клиент Android: Ключевые Потоки

**1. Отправка сообщения**

Многоэтапный процесс отправки с гарантией доставки и шифрованием:

**Этапы:**
1.   **Шифрование**: применение `Signal Protocol` (X3DH + `Double` Ratchet) для установки/использования сессии и шифрования plaintext — forward secrecy достигается за счет комбинации DH- и симметрических ратчетов
2.   **Локальная запись**: сохранение сообщения в `Room` database со статусом `pending` — позволяет отображать сообщение в UI до подтверждения доставки (optimistic UI)
3.   **WebSocket отправка**: отправка зашифрованного сообщения через `WebSocket` для минимальной латентности
4.   **Server ack**: получение подтверждения от сервера (доставка на сервер) и обновление статуса до `sent`
5.   **Device delivery**: получение подтверждения доставки на устройство получателя и обновление статуса до `delivered`
6.   **Recipient read**: получение read receipt от получателя и обновление статуса до `read`

**2. Получение сообщения**

Обработка входящих сообщений с расшифровкой и синхронизацией:

**Этапы:**
1.   **WebSocket получение**: получение зашифрованного сообщения через `WebSocket`
2.   **Расшифровка**: применение `Signal Protocol` `Double` Ratchet для расшифровки ciphertext в plaintext
3.   **Room DB сохранение**: запись расшифрованного сообщения в `Room` database с индексами для быстрого поиска
4.   **UI update**: обновление UI через `Flow`/`LiveData` для реактивного отображения новых сообщений
5.   **Read receipt**: отправка read receipt при открытии чата или прочтении сообщения

**3. Обработка медиа**

Загрузка медиафайлов с шифрованием и оптимизацией:

**Этапы:**
1.   **Сжатие**: компрессия медиа (изображения: `JPEG`/`WEBP`, видео: например, `H.264` с целевым битрейтом в несколько Mbps — конкретные значения выбираются продуктом)
2.   **Шифрование**: `AES-GCM` шифрование медиафайла с уникальным симметричным ключом (per-media key) для E2E защиты
3.   **Upload на CDN**: загрузка зашифрованного файла на `S3` с последующей доставкой через `CDN` для глобальной доступности
4.   **Отправка metadata**: отправка `URL` медиа и `thumbnail` для превью, а также `decryption key` (зашифрованного через `Signal Protocol`) получателю; серверы хранения медиа не имеют доступа к незашифрованному ключу
5.   **Ленивая загрузка**: загрузка медиа только при открытии/просмотре для экономии трафика и батареи

**4. Офлайн режим**

Очередь неотправленных сообщений с автоматической синхронизацией:

**Механизм:**
-   **Очередь unsent**: сохранение неотправленных сообщений в `Room` database со статусом `pending`
-   **Хранение**: персистентное хранение в рамках заданной политики ретенции (например, до 30 дней — конкретное значение определяется продуктом)
-   **Автоматический resend**: автоматическая отправка при восстановлении сети через `WorkManager` с constraints
-   **Exponential backoff**: увеличение интервала между retry при ошибках (1s, 2s, 4s, 8s) для предотвращения перегрузки сервера

**5. Групповые сообщения**

Эффективная доставка сообщений в группы с E2E шифрованием (Signal-style sender keys):

**Механизм:**
-   **Sender keys**: клиент генерирует sender key для группы и использует его для шифрования сообщений, отправляемых в эту группу
-   **Pairwise распространение**: sender key доставляется каждому участнику через E2E 1-to-1 сессии (pairwise), сервер видит только зашифрованные ключи
-   **Re-key при изменении состава**: при добавлении/удалении участников выполняется переинициализация групповых ключей (минимум для новых сообщений), чтобы старые участники не читали новые сообщения, а новые — старые

**6. Звонки (WebRTC)**

Установление голосовых/видеозвонков с NAT traversal:

**Процесс:**
-   **SDP negotiation**: обмен `SDP` (Session Description Protocol) через сигнальный сервис для согласования параметров медиа
-   **ICE candidates**: обмен `ICE` (Interactive Connectivity Establishment) candidates для обнаружения оптимального пути соединения
-   **STUN/TURN fallback**: использование `STUN` для обнаружения публичного IP, `TURN` для relay при невозможности P2P соединения
-   **Адаптивный bitrate**: автоматическая адаптация битрейта на основе качества сети для плавного разговора

**Примеры реализации:**

```kotlin
// ⛔ Псевдокод: иллюстрирует идею использования Signal Protocol, не готовый prod-код
val session = buildOrLoadSignalSession(recipientAddress)
val ciphertext = encryptWithSession(session, plaintext.toByteArray())

// ✅ WebSocket send with ack confirmation (упрощено)
ws.send(MessageProto(id, ciphertext, timestamp))
// Ожидание подтверждения от сервера
ackFlow.first { it.msgId == id }

// ✅ Offline queue with retry logic (упрощено)
if (!networkAvailable) {
    db.insertPending(msg)
} else {
    sendWithRetry(msg)
}
```

### Сервер: Маршрутизация

**Границы сервисов:**

-   **`Chat Service`**: маршрутизация сообщений по `userId`/`threadId` получателя, хранение зашифрованных сообщений в `Cassandra` (server не видит plaintext — zero-knowledge architecture), доставка через `WebSocket` для онлайн пользователей или `push` для офлайн, TTL и политики ретенции настраиваются продуктом
-   **`Presence Service`**: обработка heartbeat (например, каждые ~30 секунд) для отслеживания онлайн статусов, кэширование в `Redis` с небольшим TTL для быстрого доступа, `pub/sub` для realtime обновлений статусов контактов
-   **`Media Service`**: обработка `multipart upload` для больших файлов (чанки 4-8MB), автоматическая генерация `thumbnails` (также шифруются на клиенте), доставка через `CDN` (`CloudFront`/`Cloudflare`) для глобальной доступности; сервис не хранит незашифрованные медиа-ключи
-   **`Call Signaling Service`**: ретрансляция `SDP`/`ICE` candidates между участниками звонка, не участвует в медиа-потоке (P2P соединение через `WebRTC` при возможности)
-   **`Push Service`**: интеграция с `FCM` для фоновых уведомлений, приоритизация (`high` для звонков для немедленного пробуждения, `normal` для сообщений), группировка уведомлений по чатам (Android 13+)

### E2E Шифрование И Signal Protocol

**Архитектура шифрования:**

`Signal Protocol` — криптографический протокол для E2E шифрования с гарантиями forward secrecy и защиты от MITM атак.

**Identity Keys:**

-   **Долгосрочные ключи**: `ed25519` ключи для аутентификации устройств — каждый пользователь/устройство имеет identity key pair, публичный ключ используется для проверки подлинности
-   **Валидация**: проверка через QR-код safety numbers — визуальное сравнение числовых отпечатков для предотвращения MITM атак при первой установке сессии
-   **Хранение**: безопасное хранение private key в `Android Keystore` с `StrongBox` support (где доступно)

**Pre-Keys:**

-   **Одноразовые ключи**: пачка одноразовых `ECDH` ключей, загружаемых на сервер для инициации сессии с оффлайн пользователем
-   **Использование**: когда пользователь офлайн, отправитель использует pre-key для установки сессии без интерактивного обмена ключами
-   **Обновление**: автоматическая загрузка новых pre-keys при исчерпании запаса

**`Double` Ratchet:**

Механизм обновления ключей для обеспечения forward secrecy:

-   **DH Ratchet**: обновление части состояния сессии при получении нового DH публичного ключа от собеседника (происходит периодически, а не строго на каждое сообщение)
-   **Symmetric Ratchet**: обновление ключа шифрования через KDF для каждого сообщения в соответствующей цепочке
-   **Out-of-order доставка**: поддержка расшифровки сообщений при неупорядоченной доставке через счетчики и хранение нужных промежуточных ключей

**Group Sessions (Sender Keys):**

-   **Sender keys**: каждый участник использует выделенный sender key для шифрования своих сообщений группе
-   **Распределение**: sender key распределяется через pairwise E2E сессии (1-to-1) с каждым участником
-   **Re-key при изменении состава**: переинициализация ключей для новых сообщений при изменении состава группы, достигая forward/backward secrecy для истории

### Хранение Данных

**Cassandra (Messages):**

Оптимизировано для высоконагруженных операций чтения/записи с партиционированием:

-   **Партиционирование**: практично партиционировать по `threadId` (или по пользователю+чату) и диапазонам времени/идентификаторов, чтобы эффективно читать историю конкретного чата; конкретная схема зависит от требований, пример с `(userId, YYYYMM)` следует рассматривать как один из возможных вариантов.
-   **Clustering**: сортировка по `timestamp` или `messageId` для быстрого получения последних сообщений
-   **Зашифрованные данные**: хранение только зашифрованных сообщений (server не видит plaintext)
-   **TTL/retention**: политики TTL и ретенции настраиваются продуктом; для полноценного WhatsApp-like опыта история обычно не ограничивается 30 днями
-   **Replication Factor**: RF=3 для надежности
-   **Eventual consistency**: eventual consistency для высокой производительности при больших объемах

**PostgreSQL (Users, Groups):**

Strong consistency для метаданных пользователей и групп:

-   **Strong consistency**: гарантия консистентности для критичных операций (регистрация, изменение профиля, управление группами)
-   **Индексы**: индексы на `phoneNumber` и `userId` для быстрого поиска
-   **Replication**: репликация для масштабирования чтений

**Redis (Presence):**

Быстрый кеш для presence данных с TTL-based eviction:

-   **Presence кеш**: `presence:{userId}` с коротким TTL — автоматическое удаление при отсутствии heartbeat
-   **Typing индикаторы**: `typing:{chatId}:{userId}` с малым TTL — индикация набора текста
-   **Pub/Sub**: использование `Pub/Sub` для realtime обновлений

**S3 (Media):**

Lifecycle management для оптимизации стоимости хранилища:

-   **Lifecycle policies**: автоматический переход `Standard` → `Glacier` → `Delete` по политике ретенции
-   **Pre-signed URLs**: временные подписанные URL для доступа к зашифрованным объектам
-   **CDN caching**: кэширование на edge-серверах для низкой латентности

### Доставка Сообщений

**At-least-once гарантия доставки:**

-   **Client retry**: клиент автоматически ресендит сообщение до получения ack от сервера
-   **Server deduplication**: сервер дедуплицирует по `messageId`/idempotency-токенам
-   **Idempotency tokens**: уникальный токен для безопасных повторов

**Ordered delivery (упорядоченная доставка):**

-   **Server-side timestamp/globalId**: сервер присваивает timestamp и/или монотонный `globalId` при получении
-   **Client sorting**: клиент сортирует по `globalId` или по (`timestamp`, `messageId`) для детерминированного порядка
-   **Vector clocks для групп (опционально)**: могут использоваться для causal ordering в сложных сценариях; в простом дизайне достаточно server-ordered id

**Offline queueing (офлайн очередь):**

-   **Server storage**: сервер хранит недоставленные сообщения в соответствии с политикой ретенции (например, до N дней)
-   **Batch sync**: клиент синхронизирует пропущенные сообщения через batch fetch с `last_sync_timestamp`
-   **Push notification**: `FCM` для пробуждения клиента при появлении новых сообщений

### Масштабирование

**Шардирование (Sharding):**

-   **Chat `Service`**: партиционирование по hash от `userId` или `threadId` через consistent hashing
-   **Cassandra**: схема партиционирования согласована с ключами доступа (по чатам/пользователям и времени)

**Connection pooling:**

-   **WebSocket gateways**: stateful `WebSocket` gateways для persistent connections
-   **Horizontal scaling**: горизонтальное масштабирование со sticky sessions через load balancer

**Read replicas:**

-   **PostgreSQL**: реплики для масштабирования чтений
-   **Cassandra**: RF и multi-DC для чтения из ближайшего DC

**Message queue:**

-   **Kafka**: async обработка для `push` и analytics
-   **Partitioning**: по `userId`/`threadId` для локального порядка
-   **Retention**: хранение событий для аналитики/отладки

**Auto-scaling:**

-   **Kubernetes HPA**: масштабирование по числу подключений/нагрузке
-   **`Queue` depth**: масштабирование воркеров по глубине очереди

### Оптимизация Производительности

**Батарея:**

-   **Heartbeat frequency**: баланс для поддержки соединения и экономии
-   **Push coalescing**: объединение уведомлений
-   **WebSocket keep-alive**: увеличение интервалов в фоне

**Сеть:**

-   **Protobuf**: компактное бинарное кодирование вместо JSON
-   **Batch receipts**: батчинг read receipts
-   **Delta sync**: синхронизация только новых данных
-   **Prefetch частых контактов**: предзагрузка для UX (опционально)

**Память:**

-   **Message pagination**: ленивый скролл
-   **Lazy load медиа**: загрузка по требованию
-   **LRU cache**: ограниченный кеш превью

### Офлайн Режим

**Локальное хранилище:**

-   **`Room`/SQLite**: локальное хранилище сообщений/контактов/групп
-   **Индексы**: FTS и индексы по ключевым полям

**Очередь отправки:**

-   **Pending sends queue**: сообщения со статусом `pending`
-   **Retry логика**: exponential backoff

**Синхронизация при онлайне:**

-   **Batch sync**: по `last_sync_timestamp`
-   **WorkManager**: надёжная фонова синхронизация

**Conflict resolution:**

-   **Server wins для metadata**
-   **Merge для messages**: с сортировкой по `globalId`/timestamp

### Детальная Реализация (Staff-level)

**Архитектура модулей:**

Модульная структура для независимой разработки и тестирования:
-   **feature-chat**
-   **feature-media**
-   **crypto**
-   **sync**
-   **notifications**
-   **flags**
-   **analytics**

**Хранилище:**

-   **`Room` database**: локальное хранилище; при использовании `protobuf`/binary payloads для сообщений DB миграции всё равно должны быть явными — protobuf упрощает эволюцию формата, но не заменяет схемы БД

**Модель данных:**

**Thread (чат):**
-   `threadId`
-   `participants`
-   `lastMessageId`
-   `unreadCount`
-   `lastActivityAt`

**Message (сообщение):**
-   `localId`: локальный `ULID` до получения `globalId`
-   `globalId`: уникальный ID от сервера
-   `threadId`
-   `senderId`
-   `createdAt`
-   `sendState`: (`QUEUED`, `ENCRYPTED`, `UPLOADING`, `SENT`, `DELIVERED`)
-   `receiptState`: (`SENT`, `DELIVERED`, `READ`)
-   `body`: зашифрованный payload
-   `mediaRef`

**Attachment (вложение):**
-   `id`
-   `messageLocalId`
-   `status`: (`PENDING`, `UPLOADING`, `UPLOADED`, `FAILED`)
-   `mediaKey`: ключ расшифровки (зашифрованный через `Signal Protocol`)
-   `size`
-   `chunkCount`
-   `thumbRef`

**ID и упорядочивание:**

-   **ULID локально**
-   **GlobalId от сервера**
-   **Reconcile по clientTag**

**Криптография:**

-   **`Double` Ratchet** для 1-to-1
-   **Sender keys** для групп
-   **Per-device identity**
-   **Хранение ключей**: `SQLCipher` для БД, `EncryptedFile` для медиа
-   **Бэкап**: ключ шифрования у клиента, восстановление через секрет/`Android Keystore`

**Пайплайн отправки:**

OUTBOX state machine:
-   `QUEUED` → `ENCRYPTED` → `UPLOADING` → `SENT` (server ack) → `DELIVERED` (device receipt) → `READ`

**Транспорт:**

-   **Foreground**: `WebSocket`/`MQTT`
-   **Background**: `FCM` + короткий sync
-   **Адаптивный heartbeat**

**Упорядочивание:**

-   **Приоритет globalId**
-   **Fallback**: `ULID` + server timestamp

**Вложения (Attachments):**

-   **Шифрование**: `AES-GCM` per-media key
-   **Чанковая загрузка**: 4-8MB чанки
-   **Resumable upload**
-   **Зашифрованный thumbnail**
-   **Exponential backoff**

**Уведомления (Android 13-15):**

-   **FCM data payload**
-   **Минимальный metadata**
-   **Runtime permission**
-   **Группировка по `threadId`**
-   **Read-sync**

**Фоновая работа:**

-   **WorkManager**
-   **Constraints**
-   **Doze Mode**

**Поиск и гигиена:**

-   **FTS** только по локально доступному расфшифрованному тексту
-   **LRU/age eviction** медиа
-   **Настройки автоскачивания**

**Анти‑спам и защита от злоупотреблений:**

-   **Локальные лимиты**
-   **Списки блокировок** (E2E совместимый: решения принимаются на клиенте и сервере по метаданным)
-   **Серверные сигналы**: только на основе метаданных, паттернов, репортов и, при необходимости, анализа медиа, отправленных как спам/репорты; содержимое обычных E2E сообщений не анализируется сервером
-   **Предупреждающий UX**

**Наблюдаемость и релиз:**

**Метрики производительности:**
-   **p95 отправки до server ack** <200ms
-   **tap-to-open**
-   **Reconnect rate**
-   **Ack delays**
-   **Crash/ANR**

**Стратегия релиза:**
-   **Staged rollout**
-   **Kill-switch для сокета** (fallback на long-polling)

## Answer (EN)

`WhatsApp` is an E2E‑encrypted messenger involving: 1-to-1 and group messaging, media files (images, video, audio), delivery/read statuses, E2E encryption via `Signal Protocol` with forward secrecy, voice/video calls via `WebRTC`, and offline persistence with sync on network recovery.

### Requirements

**Functional:**

**Messaging:**
-   Text messages with formatting support (bold, italic, monospace)
-   Media files: images (`JPEG`, `PNG`, `WEBP`), video (e.g., `H.264`, `H.265`), audio (e.g., `Opus`, `AAC`), documents — concrete codecs are product choices, not protocol constraints
-   Voice messages with real-time recording and compression

**Groups:**
-   Create groups (commonly up to 256 participants; for "small" groups you may optimize UX/behavior around 32+ members depending on product requirements)
-   Participant management (add/remove), change name/avatar
-   Group settings (who can send messages, admins)

**Delivery statuses:**
-   `sent` — message delivered to server (server ack received)
-   `delivered` — message delivered to recipient device (server receives device ack)
-   `read` — message read by recipient (double checkmark)

**Security:**
-   E2E encryption via `Signal Protocol` with forward secrecy (each message protected by a ratcheted key)
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

-   **Low latency**: <200ms (P95) from "Send" tap to server acknowledgment — critical for real-time feel
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
-   **Data storage**: `Kafka` for async event processing, `Cassandra` for messages (partitioning, retention policies), `PostgreSQL` for users/groups (strong consistency), `S3`+`CDN` for media (lifecycle policies), `Redis` for presence cache (TTL-based)

### Android Client: Key Flows

**1. Send Message**

Multi-step sending process with delivery guarantee and encryption:

**Steps:**
1.   **Encryption**: use `Signal Protocol` (X3DH + `Double` Ratchet) to establish/use a session and encrypt plaintext — forward secrecy via DH and symmetric ratchets
2.   **Local store**: save message to `Room` database with `pending` status — enables displaying in UI before confirmation (optimistic UI)
3.   **WebSocket send**: send encrypted message via `WebSocket` for minimal latency
4.   **Server ack**: on ack from server, update status to `sent` (delivered to server)
5.   **Device delivery**: on delivery receipt from recipient device, update status to `delivered`
6.   **Recipient read**: on read receipt from recipient, update status to `read`

**2. Receive Message**

Incoming message processing with decryption and synchronization:

**Steps:**
1.   **WebSocket receive**: receive encrypted message via `WebSocket`
2.   **Decrypt**: apply `Signal Protocol` `Double` Ratchet to decrypt ciphertext
3.   **Room DB save**: write decrypted message to `Room` database with indexes for fast search
4.   **UI update**: update UI via `Flow`/`LiveData` for reactive new message display
5.   **Read receipt**: send read receipt on chat open or message read

**3. Media Processing**

Media file upload with encryption and optimization:

**Steps:**
1.   **Compression**: compress media (images: `JPEG`/`WEBP`, video: e.g., `H.264` with target bitrate in a few Mbps — concrete values are product choices)
2.   **Encryption**: `AES-GCM` encrypt media file with a unique per-media key for E2E protection
3.   **Upload to CDN**: upload encrypted file to `S3` with delivery via `CDN` for global availability
4.   **Send metadata**: send media `URL`, `thumbnail`, and `decryption key` (encrypted via `Signal Protocol`) to recipient; media service never sees plaintext key
5.   **Lazy load**: load media only on open/view for bandwidth and battery savings

**4. Offline Mode**

Unsent message queue with automatic synchronization:

**Mechanism:**
-   **Unsent queue**: save unsent messages to `Room` database with `pending` status
-   **Storage**: persist according to retention policy (e.g., up to 30 days — concrete value is a product choice)
-   **Automatic resend**: resend on network recovery via `WorkManager` with constraints
-   **Exponential backoff**: increase retry intervals on errors to avoid overload

**5. Group Messages**

Efficient group message delivery with E2E encryption (Signal-style sender keys):

**Mechanism:**
-   **Sender keys**: client uses a sender key for its messages to the group
-   **Pairwise distribution**: distribute sender key via 1-to-1 E2E sessions to each member
-   **Re-key on membership changes**: re-key for new messages when membership changes to maintain forward/backward secrecy

**6. Calls (WebRTC)**

Voice/video call establishment with NAT traversal:

**Process:**
-   **SDP negotiation**: exchange `SDP` via signaling service
-   **ICE candidates**: exchange `ICE` candidates
-   **STUN/TURN fallback**: use `STUN`/`TURN` as needed
-   **Adaptive bitrate**: adapt bitrate based on network

### Server: Routing

**`Service` boundaries:**

-   **`Chat Service`**: route messages by recipient `userId`/`threadId`, store encrypted messages in `Cassandra`, deliver via `WebSocket` or `push`, retention via configurable TTL
-   **`Presence Service`**: track heartbeat, cache in `Redis` with short TTL, `pub/sub` for updates
-   **`Media Service`**: handle chunked uploads, generate thumbnails client-encrypted, deliver via `CDN`; never store plaintext media keys
-   **`Call Signaling Service`**: relay `SDP`/`ICE` candidates, not in media path
-   **`Push Service`**: `FCM` integration with priority and grouping

### E2E Encryption and Signal Protocol

**Encryption architecture:** `Signal Protocol` for E2E encryption with forward secrecy and MITM protection.

**Identity Keys:**
-   `Long`-term `ed25519` keys per device
-   QR code safety numbers for verification
-   Secure storage in `Android Keystore` (with `StrongBox` when available)

**Pre-Keys:**
-   One-time `ECDH` pre-keys uploaded in batches
-   Used to start sessions with offline users
-   Periodically replenished

**`Double` Ratchet:**
-   DH ratchet on receipt of new DH public key (not literally every single message)
-   Symmetric ratchet per message
-   Supports out-of-order decryption via stored skipped keys

**Group Sessions (Sender Keys):**
-   Sender keys per participant for efficient group messaging
-   Distributed via pairwise sessions
-   Re-key on membership changes

### Data Storage

**Cassandra (Messages):**
-   Partitioning keyed to chat/user access patterns (e.g., by `threadId` plus time buckets)
-   Clustered by `timestamp`/`messageId`
-   Only encrypted payload stored
-   Retention configurable; long-term history allowed
-   RF tuned (e.g., 3) for reliability
-   Eventual consistency for throughput

**PostgreSQL (Users, Groups):**
-   Strong consistency for critical metadata
-   Indexed by identifiers
-   Replication for reads

**Redis (Presence):**
-   TTL-based presence and typing indicators
-   Pub/Sub for fanout

**S3 (Media):**
-   Lifecycle policies
-   Pre-signed URLs
-   CDN caching

### Message Delivery

**At-least-once delivery:**
-   Client retries until ack
-   Server deduplicates via `messageId`/idempotency

**Ordered delivery:**
-   Server-assigned timestamp/globalId
-   Client-side deterministic sorting
-   Vector clocks optional for advanced causal ordering

**Offline queueing:**
-   Server stores undelivered messages per retention
-   Client batch sync from `last_sync_timestamp`
-   `FCM` wakeups

### Scalability

**Sharding:** by `userId`/`threadId` via consistent hashing

**Connection pooling:** WebSocket gateways + sticky sessions

**Read replicas:** PostgreSQL + Cassandra multi-DC

**Message queue:** Kafka for async processing

**Auto-scaling:** HPA and queue-based scaling

### Performance Optimization

**Battery:** tune heartbeats, coalesce pushes, adjust keep-alives

**Network:** use Protobuf, batch receipts, delta sync, optional prefetch

**Memory:** pagination, lazy media load, LRU caches

### Offline Mode

Local DB, send queue with retries, batch sync, WorkManager, conflict resolution with server-preferred metadata and merged messages.

### Detailed Implementation (Staff-level)

Module decomposition, robust storage, clear data models, Signal-based crypto, OUTBOX state machine, WebSocket/FCM transport, consistent ordering, encrypted attachments, Android 13-15 notifications, background work compliant with Doze, local-only full-text search, storage hygiene, E2EE-compatible anti-abuse, strong observability, and staged rollout with kill-switch.

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

### Prerequisites (Easier)

-   [[q-database-encryption-android--android--medium]]

### Related (Same Level)

-   [[q-data-sync-unstable-network--android--hard]]
-   [[q-design-instagram-stories--android--hard]]

### Advanced (Harder)

-   [[q-design-uber-app--android--hard]]
