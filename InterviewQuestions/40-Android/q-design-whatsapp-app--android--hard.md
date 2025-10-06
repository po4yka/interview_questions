---
id: 20251006-000001
title: "How to design a WhatsApp-like app? / Как спроектировать приложение подобное WhatsApp?"
aliases: []

# Classification
topic: system-design
subtopics: [messaging, real-time, architecture, scalability, mobile-app-design]
question_kind: design
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: [real-time-updates, websocket, database-design, offline-first]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [system-design, whatsapp, messaging, real-time, architecture, scalability, android, difficulty/hard]
---

# Question (EN)
> How would you design a WhatsApp-like messaging application for Android?

# Вопрос (RU)
> Как бы вы спроектировали мессенджер, подобный WhatsApp, для Android?

---

## Answer (EN)

Designing a WhatsApp-like messaging application involves multiple components working together to provide real-time, reliable, and scalable messaging capabilities. Here's a comprehensive breakdown:

### 1. Core Requirements

**Functional Requirements:**
- One-to-one messaging
- Group messaging
- Media sharing (images, videos, documents)
- Message delivery status (sent, delivered, read)
- End-to-end encryption
- Online/offline status
- Last seen timestamp
- Push notifications
- Voice and video calls
- Message persistence (offline mode)

**Non-Functional Requirements:**
- Low latency for message delivery
- High availability (99.9%+)
- Scalability to millions of users
- Data privacy and security
- Efficient bandwidth usage
- Battery optimization

### 2. High-Level Architecture

```
┌─────────────────┐
│  Android Client │
└────────┬────────┘
         │
         ├─── WebSocket (Real-time messaging)
         ├─── REST API (User profile, media upload)
         └─── Push Notifications (FCM)
         │
┌────────▼────────┐
│  Load Balancer  │
└────────┬────────┘
         │
┌────────▼────────┐
│  Application    │
│  Servers        │ ← Message Queue (Kafka/RabbitMQ)
└────────┬────────┘
         │
         ├─── User Database (PostgreSQL/MySQL)
         ├─── Message Database (Cassandra/MongoDB)
         ├─── Cache Layer (Redis)
         └─── File Storage (S3/CDN)
```

### 3. Android App Architecture

#### Layer Structure

```kotlin
// Domain Layer - Use Cases
class SendMessageUseCase @Inject constructor(
    private val messageRepository: MessageRepository,
    private val encryptionService: EncryptionService
) {
    suspend operator fun invoke(
        chatId: String,
        content: String,
        recipientId: String
    ): Result<Message> {
        return try {
            // Encrypt message
            val encryptedContent = encryptionService.encrypt(content, recipientId)

            // Create message entity
            val message = Message(
                id = UUID.randomUUID().toString(),
                chatId = chatId,
                senderId = getCurrentUserId(),
                content = encryptedContent,
                timestamp = System.currentTimeMillis(),
                status = MessageStatus.SENDING
            )

            // Save to local DB first (offline-first)
            messageRepository.saveMessageLocally(message)

            // Send to server
            messageRepository.sendMessage(message)

            Result.Success(message)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
}

// Data Layer - Repository
class MessageRepositoryImpl @Inject constructor(
    private val localDataSource: MessageLocalDataSource,
    private val remoteDataSource: MessageRemoteDataSource,
    private val websocketManager: WebSocketManager
) : MessageRepository {

    override suspend fun sendMessage(message: Message): Result<Message> {
        return try {
            // Try to send via WebSocket for real-time delivery
            if (websocketManager.isConnected()) {
                websocketManager.sendMessage(message)
            } else {
                // Fallback to REST API
                remoteDataSource.sendMessage(message)
            }

            // Update local status
            localDataSource.updateMessageStatus(message.id, MessageStatus.SENT)

            Result.Success(message)
        } catch (e: Exception) {
            // Mark for retry
            localDataSource.updateMessageStatus(message.id, MessageStatus.FAILED)
            Result.Error(e)
        }
    }

    override fun observeMessages(chatId: String): Flow<List<Message>> {
        return localDataSource.observeMessages(chatId)
            .map { messages ->
                messages.map { decryptMessage(it) }
            }
    }
}
```

#### WebSocket Implementation

```kotlin
class WebSocketManager @Inject constructor(
    private val okHttpClient: OkHttpClient,
    private val messageHandler: MessageHandler
) {
    private var webSocket: WebSocket? = null
    private val reconnectDelay = 5000L

    fun connect(userId: String) {
        val request = Request.Builder()
            .url("wss://api.example.com/ws?userId=$userId")
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Log.d("WebSocket", "Connection opened")
                // Send authentication
                authenticate(userId)
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                // Handle incoming message
                val message = Json.decodeFromString<Message>(text)
                messageHandler.handleIncomingMessage(message)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e("WebSocket", "Connection failed", t)
                // Implement exponential backoff
                scheduleReconnect()
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                Log.d("WebSocket", "Connection closed: $reason")
                scheduleReconnect()
            }
        })
    }

    fun sendMessage(message: Message) {
        val json = Json.encodeToString(message)
        webSocket?.send(json) ?: run {
            // Queue message for sending when connection is restored
            messageHandler.queueMessage(message)
        }
    }

    private fun scheduleReconnect() {
        Handler(Looper.getMainLooper()).postDelayed({
            connect(getCurrentUserId())
        }, reconnectDelay)
    }
}
```

#### Local Database (Room)

```kotlin
@Entity(tableName = "messages")
data class MessageEntity(
    @PrimaryKey val id: String,
    val chatId: String,
    val senderId: String,
    val content: String,
    val timestamp: Long,
    val status: MessageStatus,
    val mediaUrl: String? = null,
    val mediaType: MediaType? = null,
    val isEncrypted: Boolean = true
)

@Dao
interface MessageDao {
    @Query("SELECT * FROM messages WHERE chatId = :chatId ORDER BY timestamp ASC")
    fun observeMessages(chatId: String): Flow<List<MessageEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMessage(message: MessageEntity)

    @Query("UPDATE messages SET status = :status WHERE id = :messageId")
    suspend fun updateMessageStatus(messageId: String, status: MessageStatus)

    @Query("SELECT * FROM messages WHERE status = :status")
    suspend fun getPendingMessages(status: MessageStatus = MessageStatus.FAILED): List<MessageEntity>
}

@Database(
    entities = [MessageEntity::class, ChatEntity::class, UserEntity::class],
    version = 1
)
abstract class MessagingDatabase : RoomDatabase() {
    abstract fun messageDao(): MessageDao
    abstract fun chatDao(): ChatDao
    abstract fun userDao(): UserDao
}
```

### 4. Key Features Implementation

#### End-to-End Encryption

```kotlin
class E2EEncryptionService @Inject constructor(
    private val keyStore: KeyStoreManager
) {
    // Signal Protocol or similar
    fun encrypt(message: String, recipientPublicKey: String): String {
        val cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding")
        val publicKey = keyStore.getPublicKey(recipientPublicKey)
        cipher.init(Cipher.ENCRYPT_MODE, publicKey)
        val encryptedBytes = cipher.doFinal(message.toByteArray())
        return Base64.encodeToString(encryptedBytes, Base64.DEFAULT)
    }

    fun decrypt(encryptedMessage: String): String {
        val cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding")
        val privateKey = keyStore.getPrivateKey()
        cipher.init(Cipher.DECRYPT_MODE, privateKey)
        val decryptedBytes = cipher.doFinal(
            Base64.decode(encryptedMessage, Base64.DEFAULT)
        )
        return String(decryptedBytes)
    }
}
```

#### Message Status Tracking

```kotlin
class MessageStatusTracker @Inject constructor(
    private val messageRepository: MessageRepository
) {
    fun trackDeliveryStatus(messageId: String) {
        viewModelScope.launch {
            messageRepository.observeMessageStatus(messageId)
                .collect { status ->
                    when (status) {
                        MessageStatus.SENDING -> updateUI(messageId, "Sending...")
                        MessageStatus.SENT -> updateUI(messageId, "✓")
                        MessageStatus.DELIVERED -> updateUI(messageId, "✓✓")
                        MessageStatus.READ -> updateUI(messageId, "✓✓ (blue)")
                        MessageStatus.FAILED -> updateUI(messageId, "❌")
                    }
                }
        }
    }
}
```

#### Offline Support

```kotlin
class OfflineMessageSync @Inject constructor(
    private val messageDao: MessageDao,
    private val networkMonitor: NetworkMonitor,
    private val messageRepository: MessageRepository
) {
    init {
        observeNetworkChanges()
    }

    private fun observeNetworkChanges() {
        viewModelScope.launch {
            networkMonitor.isOnline.collect { isOnline ->
                if (isOnline) {
                    syncPendingMessages()
                }
            }
        }
    }

    private suspend fun syncPendingMessages() {
        val pendingMessages = messageDao.getPendingMessages()
        pendingMessages.forEach { message ->
            try {
                messageRepository.sendMessage(message.toDomainModel())
            } catch (e: Exception) {
                Log.e("Sync", "Failed to sync message ${message.id}", e)
            }
        }
    }
}
```

#### Push Notifications

```kotlin
class MessagingFirebaseService : FirebaseMessagingService() {
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        val data = remoteMessage.data
        val messageId = data["messageId"] ?: return
        val senderId = data["senderId"] ?: return
        val content = data["content"] ?: return

        // Decrypt message
        val decryptedContent = encryptionService.decrypt(content)

        // Save to local DB
        saveMessageToDb(messageId, senderId, decryptedContent)

        // Show notification if app is in background
        if (!isAppInForeground()) {
            showNotification(senderId, decryptedContent)
        }
    }

    private fun showNotification(senderId: String, content: String) {
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_message)
            .setContentTitle(getUserName(senderId))
            .setContentText(content)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(messageId.hashCode(), notification)
    }
}
```

### 5. Scalability Considerations

#### Message Pagination

```kotlin
class MessagePagingSource(
    private val chatId: String,
    private val messageDao: MessageDao,
    private val apiService: ApiService
) : PagingSource<Int, Message>() {

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Message> {
        return try {
            val page = params.key ?: 0
            val pageSize = params.loadSize

            // Try local first
            val localMessages = messageDao.getMessagesPaged(chatId, page, pageSize)

            if (localMessages.isEmpty() && networkMonitor.isOnline()) {
                // Fetch from server
                val response = apiService.getMessages(chatId, page, pageSize)
                messageDao.insertAll(response.messages)

                LoadResult.Page(
                    data = response.messages,
                    prevKey = if (page == 0) null else page - 1,
                    nextKey = if (response.messages.isEmpty()) null else page + 1
                )
            } else {
                LoadResult.Page(
                    data = localMessages,
                    prevKey = if (page == 0) null else page - 1,
                    nextKey = if (localMessages.size < pageSize) null else page + 1
                )
            }
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }
}
```

### 6. Performance Optimizations

**Battery Optimization:**
- Use WorkManager for background sync instead of continuous services
- Implement doze mode handling
- Batch network requests
- Use FCM for push notifications instead of polling

**Network Optimization:**
- Compress media before upload
- Use Protocol Buffers instead of JSON for WebSocket
- Implement message batching for sending multiple messages
- Cache media files locally

**Memory Optimization:**
- Paginate message lists
- Use Glide/Coil for image loading with caching
- Implement proper message recycling in RecyclerView
- Clear old messages from memory

### 7. Security Best Practices

- Use SSL/TLS for all network communication
- Implement certificate pinning
- Store encryption keys in Android Keystore
- Use Signal Protocol for E2E encryption
- Implement secure file deletion
- Add tamper detection
- Use biometric authentication for app access

### Best Practices

1. **Offline-First Architecture**: Always save to local DB first, then sync
2. **Optimistic UI Updates**: Show messages immediately, update status asynchronously
3. **Message Queue**: Implement retry mechanism for failed messages
4. **Connection Management**: Handle reconnection with exponential backoff
5. **Data Consistency**: Use idempotent message IDs to prevent duplicates
6. **Testing**: Unit test business logic, integration test WebSocket, UI test messaging flow

### Common Pitfalls

1. Not handling network failures gracefully
2. Ignoring battery optimization
3. Poor database indexing leading to slow queries
4. Not implementing proper encryption
5. Hardcoding server URLs
6. Not handling edge cases (airplane mode, force quit, etc.)

## Ответ (RU)

Проектирование приложения для обмена сообщениями, подобного WhatsApp, включает несколько компонентов, работающих вместе для обеспечения обмена сообщениями в реальном времени с высокой надежностью и масштабируемостью.

### 1. Основные требования

**Функциональные требования:**
- Личные сообщения (один на один)
- Групповые сообщения
- Обмен медиафайлами (изображения, видео, документы)
- Статус доставки сообщений (отправлено, доставлено, прочитано)
- Сквозное шифрование
- Статус онлайн/офлайн
- Временная метка последнего посещения
- Push-уведомления
- Голосовые и видеозвонки
- Сохранение сообщений (офлайн режим)

**Нефункциональные требования:**
- Низкая задержка доставки сообщений
- Высокая доступность (99.9%+)
- Масштабируемость для миллионов пользователей
- Конфиденциальность и безопасность данных
- Эффективное использование пропускной способности
- Оптимизация батареи

### 2. Архитектура высокого уровня

Система состоит из:
- Android-клиента
- WebSocket для обмена сообщениями в реальном времени
- REST API для профилей пользователей и загрузки медиа
- Push-уведомлений (FCM)
- Балансировщика нагрузки
- Серверов приложений
- Очереди сообщений (Kafka/RabbitMQ)
- Базы данных пользователей (PostgreSQL/MySQL)
- Базы данных сообщений (Cassandra/MongoDB)
- Слоя кэширования (Redis)
- Файлового хранилища (S3/CDN)

### 3. Архитектура Android-приложения

#### Структура слоев

Приложение использует Clean Architecture с тремя основными слоями:

**Domain Layer (Слой бизнес-логики)**: Содержит use cases и бизнес-правила. Пример - `SendMessageUseCase`, который обрабатывает отправку сообщения с шифрованием.

**Data Layer (Слой данных)**: Управляет источниками данных (локальными и удаленными). `MessageRepository` координирует сохранение в локальной БД и отправку на сервер.

**Presentation Layer (Слой представления)**: ViewModel и UI компоненты.

#### Реализация WebSocket

WebSocket Manager управляет постоянным подключением к серверу для обмена сообщениями в реальном времени:
- Автоматическое переподключение при разрыве соединения
- Экспоненциальная задержка для повторных попыток
- Очередь сообщений при отсутствии подключения

#### Локальная база данных (Room)

Room Database хранит:
- Сообщения с метаданными
- Чаты и их участники
- Информацию о пользователях
- Статусы доставки

Используется паттерн "offline-first" - все данные сначала сохраняются локально, затем синхронизируются с сервером.

### 4. Реализация ключевых функций

#### Сквозное шифрование (E2E)

Используется асимметричное шифрование (RSA) или Signal Protocol:
- Каждый пользователь имеет пару ключей (публичный/приватный)
- Сообщения шифруются публичным ключом получателя
- Только получатель может расшифровать своим приватным ключом
- Ключи хранятся в Android Keystore

#### Отслеживание статуса сообщений

Система отслеживает пять состояний:
- SENDING (отправка)
- SENT (отправлено на сервер)
- DELIVERED (доставлено получателю)
- READ (прочитано)
- FAILED (ошибка отправки)

#### Офлайн-поддержка

Приложение полностью функционально в офлайн режиме:
- Сообщения сохраняются локально
- При восстановлении подключения происходит автоматическая синхронизация
- Мониторинг состояния сети через NetworkMonitor
- Повторная отправка неудачных сообщений

#### Push-уведомления

Firebase Cloud Messaging (FCM) доставляет уведомления:
- Получение сообщений в фоновом режиме
- Дешифрование контента
- Отображение уведомлений
- Обновление локальной БД

### 5. Масштабируемость

#### Пагинация сообщений

Используется Paging 3 библиотека:
- Загрузка сообщений порциями
- Сначала из локальной БД, затем с сервера
- Эффективное использование памяти

### 6. Оптимизация производительности

**Батарея:**
- WorkManager для фоновой синхронизации
- Обработка Doze режима
- Пакетная отправка запросов
- FCM вместо polling

**Сеть:**
- Сжатие медиафайлов перед загрузкой
- Protocol Buffers вместо JSON для WebSocket
- Пакетная отправка сообщений
- Кэширование медиафайлов

**Память:**
- Пагинация списков сообщений
- Glide/Coil для загрузки изображений с кэшированием
- Переработка элементов в RecyclerView
- Очистка старых сообщений

### 7. Безопасность

- SSL/TLS для всех сетевых соединений
- Certificate pinning
- Хранение ключей шифрования в Android Keystore
- Signal Protocol для E2E шифрования
- Безопасное удаление файлов
- Детектирование взлома
- Биометрическая аутентификация

### Лучшие практики

1. **Offline-First архитектура**: Всегда сохранять локально, затем синхронизировать
2. **Оптимистичные UI обновления**: Показывать сообщения немедленно, обновлять статус асинхронно
3. **Очередь сообщений**: Механизм повторных попыток для неудачных сообщений
4. **Управление подключением**: Переподключение с экспоненциальной задержкой
5. **Согласованность данных**: Идемпотентные ID сообщений для предотвращения дубликатов

### Частые ошибки

1. Некорректная обработка сетевых сбоев
2. Игнорирование оптимизации батареи
3. Плохая индексация БД, приводящая к медленным запросам
4. Отсутствие правильного шифрования
5. Жестко заданные URL серверов
6. Необработка граничных случаев (режим полета, принудительное закрытие и т.д.)

---

## References
- [Building a Messaging App](https://www.scalablepath.com/back-end/messaging-app-architecture)
- [Signal Protocol Documentation](https://signal.org/docs/)
- [Android Offline-First Architecture](https://developer.android.com/topic/architecture/data-layer/offline-first)
- [WebSocket with OkHttp](https://square.github.io/okhttp/features/websockets/)
- [Room Database Guide](https://developer.android.com/training/data-storage/room)

## Related Questions
- How to implement WebSocket in Android?
- What is offline-first architecture?
- How to implement end-to-end encryption?
- How to optimize battery usage in messaging apps?
- What is the Signal Protocol?
