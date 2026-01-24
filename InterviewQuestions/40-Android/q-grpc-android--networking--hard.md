---
id: android-752
title: "gRPC on Android / gRPC на Android"
aliases: ["gRPC on Android", "gRPC на Android"]
topic: android
subtopics: [networking]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-networking, q-http-protocols-comparison--android--medium, q-retrofit-library--android--medium]
created: 2026-01-23
updated: 2026-01-23
sources: ["https://grpc.io/docs/languages/kotlin/", "https://developer.android.com/guide/topics/connectivity/grpc", "https://github.com/grpc/grpc-kotlin"]
tags: [android/networking, difficulty/hard, grpc, protobuf, http2, streaming, rpc]

---
# Вопрос (RU)

> Как использовать gRPC на Android? Объясните Protocol Buffers, типы RPC-вызовов и преимущества над REST.

# Question (EN)

> How do you use gRPC on Android? Explain Protocol Buffers, RPC call types, and advantages over REST.

---

## Ответ (RU)

**gRPC** - высокопроизводительный RPC-фреймворк от Google, использующий HTTP/2 для транспорта и Protocol Buffers (Protobuf) для сериализации. На Android gRPC обеспечивает типобезопасную коммуникацию с сервером через сгенерированные stub-классы.

### Краткий Ответ

- **gRPC** использует HTTP/2 + Protobuf для эффективной бинарной сериализации
- **4 типа вызовов**: Unary, Server Streaming, Client Streaming, Bidirectional Streaming
- **Преимущества**: меньший размер payload, строгая типизация, streaming, мультиплексирование
- На Android используйте **grpc-kotlin** с корутинами

### Подробный Ответ

### Protocol Buffers (Protobuf)

Protobuf - язык описания интерфейсов (IDL) для определения сервисов и сообщений:

```protobuf
// user_service.proto
syntax = "proto3";

package com.example.api;

option java_multiple_files = true;
option java_package = "com.example.api.grpc";

// Сообщения
message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
}

message GetUserRequest {
  string user_id = 1;
}

message GetUserResponse {
  User user = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

// Определение сервиса
service UserService {
  // Unary RPC
  rpc GetUser(GetUserRequest) returns (GetUserResponse);

  // Server streaming RPC
  rpc ListUsers(ListUsersRequest) returns (stream User);

  // Client streaming RPC
  rpc CreateUsers(stream CreateUserRequest) returns (ListUsersResponse);

  // Bidirectional streaming RPC
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message ChatMessage {
  string user_id = 1;
  string content = 2;
  int64 timestamp = 3;
}
```

### Настройка Gradle (Android)

```kotlin
// build.gradle.kts (project)
plugins {
    id("com.google.protobuf") version "0.9.4" apply false
}

// build.gradle.kts (app module)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.protobuf")
}

dependencies {
    // gRPC
    implementation("io.grpc:grpc-kotlin-stub:1.4.1")
    implementation("io.grpc:grpc-okhttp:1.62.2")
    implementation("io.grpc:grpc-protobuf-lite:1.62.2")

    // Protobuf
    implementation("com.google.protobuf:protobuf-kotlin-lite:3.25.2")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.0")
}

protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:3.25.2"
    }
    plugins {
        create("grpc") {
            artifact = "io.grpc:protoc-gen-grpc-java:1.62.2"
        }
        create("grpckt") {
            artifact = "io.grpc:protoc-gen-grpc-kotlin:1.4.1:jdk8@jar"
        }
    }
    generateProtoTasks {
        all().forEach { task ->
            task.builtins {
                create("java") {
                    option("lite")
                }
                create("kotlin") {
                    option("lite")
                }
            }
            task.plugins {
                create("grpc") {
                    option("lite")
                }
                create("grpckt")
            }
        }
    }
}
```

### Создание gRPC Channel

```kotlin
class GrpcClientProvider @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val channel: ManagedChannel by lazy {
        val builder = ManagedChannelBuilder
            .forAddress("api.example.com", 443)
            .useTransportSecurity() // TLS

        // Для Android используем OkHttp transport
        OkHttpChannelBuilder
            .forAddress("api.example.com", 443)
            .useTransportSecurity()
            .keepAliveTime(30, TimeUnit.SECONDS)
            .keepAliveTimeout(10, TimeUnit.SECONDS)
            .idleTimeout(5, TimeUnit.MINUTES)
            .build()
    }

    val userServiceStub: UserServiceGrpcKt.UserServiceCoroutineStub by lazy {
        UserServiceGrpcKt.UserServiceCoroutineStub(channel)
    }

    fun shutdown() {
        channel.shutdown().awaitTermination(5, TimeUnit.SECONDS)
    }
}
```

### Типы RPC-Вызовов

#### 1. Unary RPC (один запрос - один ответ)

```kotlin
class UserRepository @Inject constructor(
    private val userStub: UserServiceGrpcKt.UserServiceCoroutineStub
) {
    suspend fun getUser(userId: String): Result<User> {
        return try {
            val request = GetUserRequest.newBuilder()
                .setUserId(userId)
                .build()

            val response = userStub.getUser(request)
            Result.success(response.user)
        } catch (e: StatusException) {
            Result.failure(mapGrpcError(e))
        }
    }
}
```

#### 2. Server Streaming RPC (один запрос - поток ответов)

```kotlin
class UserRepository @Inject constructor(
    private val userStub: UserServiceGrpcKt.UserServiceCoroutineStub
) {
    fun listUsersStream(pageSize: Int): Flow<User> = flow {
        val request = ListUsersRequest.newBuilder()
            .setPageSize(pageSize)
            .build()

        userStub.listUsers(request).collect { user ->
            emit(user)
        }
    }.catch { e ->
        if (e is StatusException) {
            throw mapGrpcError(e)
        }
        throw e
    }
}

// Использование в ViewModel
@HiltViewModel
class UserListViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            userRepository.listUsersStream(pageSize = 20)
                .collect { user ->
                    _users.update { currentList -> currentList + user }
                }
        }
    }
}
```

#### 3. Client Streaming RPC (поток запросов - один ответ)

```kotlin
class UserRepository @Inject constructor(
    private val userStub: UserServiceGrpcKt.UserServiceCoroutineStub
) {
    suspend fun createUsersBatch(users: List<CreateUserData>): Result<List<User>> {
        return try {
            val requestFlow = flow {
                users.forEach { userData ->
                    val request = CreateUserRequest.newBuilder()
                        .setName(userData.name)
                        .setEmail(userData.email)
                        .build()
                    emit(request)
                }
            }

            val response = userStub.createUsers(requestFlow)
            Result.success(response.usersList)
        } catch (e: StatusException) {
            Result.failure(mapGrpcError(e))
        }
    }
}
```

#### 4. Bidirectional Streaming RPC (поток запросов - поток ответов)

```kotlin
class ChatRepository @Inject constructor(
    private val userStub: UserServiceGrpcKt.UserServiceCoroutineStub
) {
    fun chat(outgoingMessages: Flow<ChatMessage>): Flow<ChatMessage> {
        return userStub.chat(outgoingMessages)
    }
}

// Использование
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository
) : ViewModel() {

    private val _outgoingMessages = MutableSharedFlow<ChatMessage>()

    private val _incomingMessages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val incomingMessages: StateFlow<List<ChatMessage>> = _incomingMessages.asStateFlow()

    init {
        viewModelScope.launch {
            chatRepository.chat(_outgoingMessages)
                .catch { e -> /* handle error */ }
                .collect { message ->
                    _incomingMessages.update { it + message }
                }
        }
    }

    fun sendMessage(content: String) {
        viewModelScope.launch {
            val message = ChatMessage.newBuilder()
                .setUserId("current_user_id")
                .setContent(content)
                .setTimestamp(System.currentTimeMillis())
                .build()

            _outgoingMessages.emit(message)
        }
    }
}
```

### Обработка Ошибок

```kotlin
sealed class GrpcError : Exception() {
    data class NetworkError(override val message: String) : GrpcError()
    data class ServerError(val code: Int, override val message: String) : GrpcError()
    data class AuthenticationError(override val message: String) : GrpcError()
    data class NotFound(override val message: String) : GrpcError()
    data class Unknown(override val message: String) : GrpcError()
}

fun mapGrpcError(e: StatusException): GrpcError {
    return when (e.status.code) {
        Status.Code.UNAVAILABLE -> GrpcError.NetworkError(e.message ?: "Network unavailable")
        Status.Code.UNAUTHENTICATED -> GrpcError.AuthenticationError(e.message ?: "Unauthenticated")
        Status.Code.NOT_FOUND -> GrpcError.NotFound(e.message ?: "Not found")
        Status.Code.INTERNAL -> GrpcError.ServerError(500, e.message ?: "Internal server error")
        Status.Code.INVALID_ARGUMENT -> GrpcError.ServerError(400, e.message ?: "Invalid argument")
        else -> GrpcError.Unknown(e.message ?: "Unknown error")
    }
}
```

### Interceptors (Метаданные, Авторизация)

```kotlin
class AuthInterceptor(
    private val tokenProvider: TokenProvider
) : ClientInterceptor {

    override fun <ReqT, RespT> interceptCall(
        method: MethodDescriptor<ReqT, RespT>,
        callOptions: CallOptions,
        next: Channel
    ): ClientCall<ReqT, RespT> {
        return object : ForwardingClientCall.SimpleForwardingClientCall<ReqT, RespT>(
            next.newCall(method, callOptions)
        ) {
            override fun start(responseListener: Listener<RespT>, headers: Metadata) {
                tokenProvider.getAccessToken()?.let { token ->
                    headers.put(
                        Metadata.Key.of("Authorization", Metadata.ASCII_STRING_MARSHALLER),
                        "Bearer $token"
                    )
                }
                super.start(responseListener, headers)
            }
        }
    }
}

// Использование
val channel = OkHttpChannelBuilder
    .forAddress("api.example.com", 443)
    .useTransportSecurity()
    .intercept(AuthInterceptor(tokenProvider))
    .build()
```

### Сравнение gRPC vs REST

| Аспект | gRPC | REST |
|--------|------|------|
| **Протокол** | HTTP/2 | HTTP/1.1 или HTTP/2 |
| **Формат данных** | Protobuf (бинарный) | JSON (текст) |
| **Размер payload** | Меньше (~30-50%) | Больше |
| **Типизация** | Строгая (schema) | Слабая (опционально OpenAPI) |
| **Streaming** | Native (4 типа) | Ограниченно (SSE, WebSocket) |
| **Генерация кода** | Автоматическая | Ручная или Swagger/OpenAPI |
| **Browser support** | Ограниченно (gRPC-Web) | Полная |
| **Отладка** | Сложнее (бинарный формат) | Проще (читаемый JSON) |

### Лучшие Практики

1. **Версионирование** - включайте версию в package name proto-файла
2. **Deadline/Timeout** - всегда устанавливайте deadline для вызовов
3. **Retry с backoff** - используйте retry policy для transient errors
4. **Keep-alive** - настраивайте keep-alive для долгоживущих соединений
5. **Protobuf evolution** - используйте optional fields, не меняйте field numbers
6. **Channel reuse** - переиспользуйте один channel для всех stub'ов

---

## Answer (EN)

**gRPC** is a high-performance RPC framework from Google that uses HTTP/2 for transport and Protocol Buffers (Protobuf) for serialization. On Android, gRPC provides type-safe server communication through generated stub classes.

### Short Version

- **gRPC** uses HTTP/2 + Protobuf for efficient binary serialization
- **4 call types**: Unary, Server Streaming, Client Streaming, Bidirectional Streaming
- **Advantages**: smaller payload, strict typing, streaming, multiplexing
- On Android use **grpc-kotlin** with coroutines

### Detailed Version

### Protocol Buffers (Protobuf)

Protobuf is an Interface Definition Language (IDL) for defining services and messages:

```protobuf
// user_service.proto
syntax = "proto3";

package com.example.api;

option java_multiple_files = true;
option java_package = "com.example.api.grpc";

// Messages
message User {
  string id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;
}

message GetUserRequest {
  string user_id = 1;
}

message GetUserResponse {
  User user = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

// Service definition
service UserService {
  // Unary RPC
  rpc GetUser(GetUserRequest) returns (GetUserResponse);

  // Server streaming RPC
  rpc ListUsers(ListUsersRequest) returns (stream User);

  // Client streaming RPC
  rpc CreateUsers(stream CreateUserRequest) returns (ListUsersResponse);

  // Bidirectional streaming RPC
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message ChatMessage {
  string user_id = 1;
  string content = 2;
  int64 timestamp = 3;
}
```

### Gradle Setup (Android)

```kotlin
// build.gradle.kts (project)
plugins {
    id("com.google.protobuf") version "0.9.4" apply false
}

// build.gradle.kts (app module)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.protobuf")
}

dependencies {
    // gRPC
    implementation("io.grpc:grpc-kotlin-stub:1.4.1")
    implementation("io.grpc:grpc-okhttp:1.62.2")
    implementation("io.grpc:grpc-protobuf-lite:1.62.2")

    // Protobuf
    implementation("com.google.protobuf:protobuf-kotlin-lite:3.25.2")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.0")
}

protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:3.25.2"
    }
    plugins {
        create("grpc") {
            artifact = "io.grpc:protoc-gen-grpc-java:1.62.2"
        }
        create("grpckt") {
            artifact = "io.grpc:protoc-gen-grpc-kotlin:1.4.1:jdk8@jar"
        }
    }
    generateProtoTasks {
        all().forEach { task ->
            task.builtins {
                create("java") {
                    option("lite")
                }
                create("kotlin") {
                    option("lite")
                }
            }
            task.plugins {
                create("grpc") {
                    option("lite")
                }
                create("grpckt")
            }
        }
    }
}
```

### Creating gRPC Channel

```kotlin
class GrpcClientProvider @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val channel: ManagedChannel by lazy {
        // For Android use OkHttp transport
        OkHttpChannelBuilder
            .forAddress("api.example.com", 443)
            .useTransportSecurity()
            .keepAliveTime(30, TimeUnit.SECONDS)
            .keepAliveTimeout(10, TimeUnit.SECONDS)
            .idleTimeout(5, TimeUnit.MINUTES)
            .build()
    }

    val userServiceStub: UserServiceGrpcKt.UserServiceCoroutineStub by lazy {
        UserServiceGrpcKt.UserServiceCoroutineStub(channel)
    }

    fun shutdown() {
        channel.shutdown().awaitTermination(5, TimeUnit.SECONDS)
    }
}
```

### RPC Call Types

#### 1. Unary RPC (one request - one response)

```kotlin
class UserRepository @Inject constructor(
    private val userStub: UserServiceGrpcKt.UserServiceCoroutineStub
) {
    suspend fun getUser(userId: String): Result<User> {
        return try {
            val request = GetUserRequest.newBuilder()
                .setUserId(userId)
                .build()

            val response = userStub.getUser(request)
            Result.success(response.user)
        } catch (e: StatusException) {
            Result.failure(mapGrpcError(e))
        }
    }
}
```

#### 2. Server Streaming RPC (one request - stream of responses)

```kotlin
class UserRepository @Inject constructor(
    private val userStub: UserServiceGrpcKt.UserServiceCoroutineStub
) {
    fun listUsersStream(pageSize: Int): Flow<User> = flow {
        val request = ListUsersRequest.newBuilder()
            .setPageSize(pageSize)
            .build()

        userStub.listUsers(request).collect { user ->
            emit(user)
        }
    }.catch { e ->
        if (e is StatusException) {
            throw mapGrpcError(e)
        }
        throw e
    }
}

// Usage in ViewModel
@HiltViewModel
class UserListViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            userRepository.listUsersStream(pageSize = 20)
                .collect { user ->
                    _users.update { currentList -> currentList + user }
                }
        }
    }
}
```

#### 3. Client Streaming RPC (stream of requests - one response)

```kotlin
class UserRepository @Inject constructor(
    private val userStub: UserServiceGrpcKt.UserServiceCoroutineStub
) {
    suspend fun createUsersBatch(users: List<CreateUserData>): Result<List<User>> {
        return try {
            val requestFlow = flow {
                users.forEach { userData ->
                    val request = CreateUserRequest.newBuilder()
                        .setName(userData.name)
                        .setEmail(userData.email)
                        .build()
                    emit(request)
                }
            }

            val response = userStub.createUsers(requestFlow)
            Result.success(response.usersList)
        } catch (e: StatusException) {
            Result.failure(mapGrpcError(e))
        }
    }
}
```

#### 4. Bidirectional Streaming RPC (stream of requests - stream of responses)

```kotlin
class ChatRepository @Inject constructor(
    private val userStub: UserServiceGrpcKt.UserServiceCoroutineStub
) {
    fun chat(outgoingMessages: Flow<ChatMessage>): Flow<ChatMessage> {
        return userStub.chat(outgoingMessages)
    }
}

// Usage
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatRepository: ChatRepository
) : ViewModel() {

    private val _outgoingMessages = MutableSharedFlow<ChatMessage>()

    private val _incomingMessages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val incomingMessages: StateFlow<List<ChatMessage>> = _incomingMessages.asStateFlow()

    init {
        viewModelScope.launch {
            chatRepository.chat(_outgoingMessages)
                .catch { e -> /* handle error */ }
                .collect { message ->
                    _incomingMessages.update { it + message }
                }
        }
    }

    fun sendMessage(content: String) {
        viewModelScope.launch {
            val message = ChatMessage.newBuilder()
                .setUserId("current_user_id")
                .setContent(content)
                .setTimestamp(System.currentTimeMillis())
                .build()

            _outgoingMessages.emit(message)
        }
    }
}
```

### Error Handling

```kotlin
sealed class GrpcError : Exception() {
    data class NetworkError(override val message: String) : GrpcError()
    data class ServerError(val code: Int, override val message: String) : GrpcError()
    data class AuthenticationError(override val message: String) : GrpcError()
    data class NotFound(override val message: String) : GrpcError()
    data class Unknown(override val message: String) : GrpcError()
}

fun mapGrpcError(e: StatusException): GrpcError {
    return when (e.status.code) {
        Status.Code.UNAVAILABLE -> GrpcError.NetworkError(e.message ?: "Network unavailable")
        Status.Code.UNAUTHENTICATED -> GrpcError.AuthenticationError(e.message ?: "Unauthenticated")
        Status.Code.NOT_FOUND -> GrpcError.NotFound(e.message ?: "Not found")
        Status.Code.INTERNAL -> GrpcError.ServerError(500, e.message ?: "Internal server error")
        Status.Code.INVALID_ARGUMENT -> GrpcError.ServerError(400, e.message ?: "Invalid argument")
        else -> GrpcError.Unknown(e.message ?: "Unknown error")
    }
}
```

### Interceptors (Metadata, Authorization)

```kotlin
class AuthInterceptor(
    private val tokenProvider: TokenProvider
) : ClientInterceptor {

    override fun <ReqT, RespT> interceptCall(
        method: MethodDescriptor<ReqT, RespT>,
        callOptions: CallOptions,
        next: Channel
    ): ClientCall<ReqT, RespT> {
        return object : ForwardingClientCall.SimpleForwardingClientCall<ReqT, RespT>(
            next.newCall(method, callOptions)
        ) {
            override fun start(responseListener: Listener<RespT>, headers: Metadata) {
                tokenProvider.getAccessToken()?.let { token ->
                    headers.put(
                        Metadata.Key.of("Authorization", Metadata.ASCII_STRING_MARSHALLER),
                        "Bearer $token"
                    )
                }
                super.start(responseListener, headers)
            }
        }
    }
}

// Usage
val channel = OkHttpChannelBuilder
    .forAddress("api.example.com", 443)
    .useTransportSecurity()
    .intercept(AuthInterceptor(tokenProvider))
    .build()
```

### gRPC vs REST Comparison

| Aspect | gRPC | REST |
|--------|------|------|
| **Protocol** | HTTP/2 | HTTP/1.1 or HTTP/2 |
| **Data format** | Protobuf (binary) | JSON (text) |
| **Payload size** | Smaller (~30-50%) | Larger |
| **Typing** | Strong (schema) | Weak (optional OpenAPI) |
| **Streaming** | Native (4 types) | Limited (SSE, WebSocket) |
| **Code generation** | Automatic | Manual or Swagger/OpenAPI |
| **Browser support** | Limited (gRPC-Web) | Full |
| **Debugging** | Harder (binary format) | Easier (readable JSON) |

### Best Practices

1. **Versioning** - include version in proto package name
2. **Deadline/Timeout** - always set deadline for calls
3. **Retry with backoff** - use retry policy for transient errors
4. **Keep-alive** - configure keep-alive for long-lived connections
5. **Protobuf evolution** - use optional fields, don't change field numbers
6. **Channel reuse** - reuse one channel for all stubs

---

## Дополнительные Вопросы (RU)

1. Как версионировать gRPC API?
2. Как реализовать retry policy для gRPC вызовов?
3. В чем разница между deadline и timeout в gRPC?
4. Как тестировать gRPC сервисы на Android?
5. Когда выбирать gRPC вместо REST?

## Follow-ups

1. How do you version gRPC APIs?
2. How do you implement retry policy for gRPC calls?
3. What is the difference between deadline and timeout in gRPC?
4. How do you test gRPC services on Android?
5. When should you choose gRPC over REST?

## Ссылки (RU)

- [gRPC Kotlin](https://grpc.io/docs/languages/kotlin/)
- [gRPC Android Guide](https://developer.android.com/guide/topics/connectivity/grpc)
- [Protocol Buffers](https://protobuf.dev/)

## References

- [gRPC Kotlin](https://grpc.io/docs/languages/kotlin/)
- [gRPC Android Guide](https://developer.android.com/guide/topics/connectivity/grpc)
- [Protocol Buffers](https://protobuf.dev/)

## Связанные Вопросы (RU)

### Предпосылки

- [[q-http-protocols-comparison--android--medium]]
- [[q-retrofit-library--android--medium]]

### Похожие

- [[q-graphql-android--networking--medium]]
- [[q-websockets-android--networking--hard]]

### Продвинутое

- [[q-implement-voice-video-call--android--hard]]
- [[q-data-sync-unstable-network--android--hard]]

## Related Questions

### Prerequisites

- [[q-http-protocols-comparison--android--medium]]
- [[q-retrofit-library--android--medium]]

### Related

- [[q-graphql-android--networking--medium]]
- [[q-websockets-android--networking--hard]]

### Advanced

- [[q-implement-voice-video-call--android--hard]]
- [[q-data-sync-unstable-network--android--hard]]
