---
id: kotlin-kmp-005
title: "KMP Networking with Ktor / Работа с сетью в KMP через Ktor"
aliases: [Ktor KMP, Shared Networking, Cross-Platform HTTP Client]
topic: kotlin
subtopics: [kmp, multiplatform, networking, ktor]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin]
created: 2026-01-23
updated: 2026-01-23
tags: [kotlin, kmp, multiplatform, ktor, networking, difficulty/medium]
---

# Question (EN)
> How do you implement shared networking in Kotlin Multiplatform using Ktor?

# Vopros (RU)
> Как реализовать общую работу с сетью в Kotlin Multiplatform с использованием Ktor?

## Answer (EN)

**Ktor** is JetBrains' multiplatform HTTP client library, purpose-built for Kotlin Multiplatform. It provides a consistent API across Android, iOS, Desktop, and Web.

### Project Setup

```kotlin
// build.gradle.kts (shared module)
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.ktor.client.core)
            implementation(libs.ktor.client.content.negotiation)
            implementation(libs.ktor.serialization.kotlinx.json)
            implementation(libs.ktor.client.logging)
            implementation(libs.ktor.client.auth)
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
        }

        androidMain.dependencies {
            implementation(libs.ktor.client.android)  // OkHttp engine
            // OR implementation(libs.ktor.client.okhttp)
        }

        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)  // NSURLSession engine
        }

        jvmMain.dependencies {
            implementation(libs.ktor.client.cio)  // Coroutine-based engine
        }

        jsMain.dependencies {
            implementation(libs.ktor.client.js)  // Fetch API engine
        }
    }
}

// libs.versions.toml
[versions]
ktor = "3.0.0"
kotlinx-coroutines = "1.8.0"
kotlinx-serialization = "1.6.3"

[libraries]
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-client-content-negotiation = { module = "io.ktor:ktor-client-content-negotiation", version.ref = "ktor" }
ktor-serialization-kotlinx-json = { module = "io.ktor:ktor-serialization-kotlinx-json", version.ref = "ktor" }
ktor-client-android = { module = "io.ktor:ktor-client-android", version.ref = "ktor" }
ktor-client-darwin = { module = "io.ktor:ktor-client-darwin", version.ref = "ktor" }
ktor-client-logging = { module = "io.ktor:ktor-client-logging", version.ref = "ktor" }
ktor-client-auth = { module = "io.ktor:ktor-client-auth", version.ref = "ktor" }
```

### HttpClient Factory Pattern

```kotlin
// commonMain
expect fun createPlatformHttpClient(): HttpClient

fun createHttpClient(
    baseUrl: String,
    authTokenProvider: suspend () -> String?
): HttpClient {
    return createPlatformHttpClient().config {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
                encodeDefaults = true
                prettyPrint = false
            })
        }

        install(Logging) {
            logger = object : Logger {
                override fun log(message: String) {
                    co.touchlab.kermit.Logger.d { message }
                }
            }
            level = LogLevel.HEADERS
        }

        install(Auth) {
            bearer {
                loadTokens {
                    authTokenProvider()?.let { BearerTokens(it, "") }
                }
                refreshTokens {
                    // Token refresh logic
                    null
                }
            }
        }

        install(HttpTimeout) {
            requestTimeoutMillis = 30_000
            connectTimeoutMillis = 10_000
            socketTimeoutMillis = 30_000
        }

        defaultRequest {
            url(baseUrl)
            contentType(ContentType.Application.Json)
        }
    }
}

// androidMain
actual fun createPlatformHttpClient(): HttpClient {
    return HttpClient(Android) {
        engine {
            connectTimeout = 10_000
            socketTimeout = 30_000
        }
    }
}

// iosMain
actual fun createPlatformHttpClient(): HttpClient {
    return HttpClient(Darwin) {
        engine {
            configureRequest {
                setAllowsCellularAccess(true)
            }
        }
    }
}
```

### API Service Implementation

```kotlin
// commonMain
@Serializable
data class User(
    val id: String,
    val name: String,
    val email: String,
    @SerialName("avatar_url")
    val avatarUrl: String?
)

@Serializable
data class CreateUserRequest(
    val name: String,
    val email: String
)

@Serializable
data class ApiError(
    val code: String,
    val message: String
)

class UserApiService(private val httpClient: HttpClient) {

    suspend fun getUsers(): List<User> {
        return httpClient.get("/api/v1/users").body()
    }

    suspend fun getUser(id: String): User {
        return httpClient.get("/api/v1/users/$id").body()
    }

    suspend fun createUser(request: CreateUserRequest): User {
        return httpClient.post("/api/v1/users") {
            setBody(request)
        }.body()
    }

    suspend fun updateUser(id: String, request: CreateUserRequest): User {
        return httpClient.put("/api/v1/users/$id") {
            setBody(request)
        }.body()
    }

    suspend fun deleteUser(id: String) {
        httpClient.delete("/api/v1/users/$id")
    }

    suspend fun uploadAvatar(userId: String, imageData: ByteArray): User {
        return httpClient.post("/api/v1/users/$userId/avatar") {
            setBody(MultiPartFormDataContent(
                formData {
                    append("file", imageData, Headers.build {
                        append(HttpHeaders.ContentType, "image/jpeg")
                        append(HttpHeaders.ContentDisposition, "filename=\"avatar.jpg\"")
                    })
                }
            ))
        }.body()
    }
}
```

### Error Handling

```kotlin
// commonMain
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val exception: NetworkException) : NetworkResult<Nothing>()
}

sealed class NetworkException : Exception() {
    data class HttpError(
        val statusCode: Int,
        override val message: String,
        val body: String?
    ) : NetworkException()

    data class ConnectionError(override val cause: Throwable) : NetworkException()
    data class SerializationError(override val cause: Throwable) : NetworkException()
    object TimeoutError : NetworkException()
    data class UnknownError(override val cause: Throwable) : NetworkException()
}

suspend inline fun <reified T> safeApiCall(
    crossinline call: suspend () -> T
): NetworkResult<T> {
    return try {
        NetworkResult.Success(call())
    } catch (e: ClientRequestException) {
        val body = e.response.bodyAsText()
        NetworkResult.Error(
            NetworkException.HttpError(
                statusCode = e.response.status.value,
                message = e.response.status.description,
                body = body
            )
        )
    } catch (e: ServerResponseException) {
        NetworkResult.Error(
            NetworkException.HttpError(
                statusCode = e.response.status.value,
                message = e.response.status.description,
                body = null
            )
        )
    } catch (e: HttpRequestTimeoutException) {
        NetworkResult.Error(NetworkException.TimeoutError)
    } catch (e: SerializationException) {
        NetworkResult.Error(NetworkException.SerializationError(e))
    } catch (e: IOException) {
        NetworkResult.Error(NetworkException.ConnectionError(e))
    } catch (e: Exception) {
        NetworkResult.Error(NetworkException.UnknownError(e))
    }
}

// Usage
class UserRepository(private val api: UserApiService) {
    suspend fun getUser(id: String): NetworkResult<User> {
        return safeApiCall { api.getUser(id) }
    }
}
```

### WebSocket Support

```kotlin
// commonMain
class WebSocketService(private val httpClient: HttpClient) {

    suspend fun connectToChat(
        roomId: String,
        onMessage: (ChatMessage) -> Unit,
        onError: (Throwable) -> Unit
    ): WebSocketSession {
        return httpClient.webSocketSession("/ws/chat/$roomId").apply {
            launch {
                try {
                    for (frame in incoming) {
                        when (frame) {
                            is Frame.Text -> {
                                val message = Json.decodeFromString<ChatMessage>(frame.readText())
                                onMessage(message)
                            }
                            is Frame.Close -> break
                            else -> {}
                        }
                    }
                } catch (e: Exception) {
                    onError(e)
                }
            }
        }
    }

    suspend fun WebSocketSession.sendMessage(message: ChatMessage) {
        send(Frame.Text(Json.encodeToString(message)))
    }
}
```

### Testing

```kotlin
// commonTest
class UserApiServiceTest {

    private val mockEngine = MockEngine { request ->
        when (request.url.encodedPath) {
            "/api/v1/users" -> respond(
                content = """[{"id":"1","name":"John","email":"john@test.com","avatar_url":null}]""",
                headers = headersOf(HttpHeaders.ContentType, ContentType.Application.Json.toString())
            )
            "/api/v1/users/1" -> respond(
                content = """{"id":"1","name":"John","email":"john@test.com","avatar_url":null}""",
                headers = headersOf(HttpHeaders.ContentType, ContentType.Application.Json.toString())
            )
            else -> respondError(HttpStatusCode.NotFound)
        }
    }

    private val httpClient = HttpClient(mockEngine) {
        install(ContentNegotiation) {
            json()
        }
    }

    private val api = UserApiService(httpClient)

    @Test
    fun testGetUsers() = runTest {
        val users = api.getUsers()
        assertEquals(1, users.size)
        assertEquals("John", users[0].name)
    }

    @Test
    fun testGetUser() = runTest {
        val user = api.getUser("1")
        assertEquals("1", user.id)
        assertEquals("john@test.com", user.email)
    }
}
```

### Best Practices

1. **Use platform-specific engines** - Android (OkHttp), iOS (Darwin/NSURLSession)
2. **Implement proper error handling** - Wrap responses in Result types
3. **Configure timeouts appropriately** - Especially for mobile networks
4. **Use content negotiation** - Automatic JSON serialization
5. **Implement retry logic** - For transient failures
6. **Close HttpClient properly** - In cleanup/dispose methods

---

## Otvet (RU)

**Ktor** - это мультиплатформенная HTTP клиентская библиотека от JetBrains, специально созданная для Kotlin Multiplatform. Она предоставляет единый API для Android, iOS, Desktop и Web.

### Настройка проекта

```kotlin
// build.gradle.kts (shared модуль)
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.ktor.client.core)
            implementation(libs.ktor.client.content.negotiation)
            implementation(libs.ktor.serialization.kotlinx.json)
            implementation(libs.ktor.client.logging)
            implementation(libs.ktor.client.auth)
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
        }

        androidMain.dependencies {
            implementation(libs.ktor.client.android)  // OkHttp движок
        }

        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)  // NSURLSession движок
        }

        jvmMain.dependencies {
            implementation(libs.ktor.client.cio)  // Корутинный движок
        }

        jsMain.dependencies {
            implementation(libs.ktor.client.js)  // Fetch API движок
        }
    }
}
```

### Паттерн фабрики HttpClient

```kotlin
// commonMain
expect fun createPlatformHttpClient(): HttpClient

fun createHttpClient(
    baseUrl: String,
    authTokenProvider: suspend () -> String?
): HttpClient {
    return createPlatformHttpClient().config {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
                encodeDefaults = true
                prettyPrint = false
            })
        }

        install(Logging) {
            logger = object : Logger {
                override fun log(message: String) {
                    co.touchlab.kermit.Logger.d { message }
                }
            }
            level = LogLevel.HEADERS
        }

        install(Auth) {
            bearer {
                loadTokens {
                    authTokenProvider()?.let { BearerTokens(it, "") }
                }
                refreshTokens {
                    // Логика обновления токена
                    null
                }
            }
        }

        install(HttpTimeout) {
            requestTimeoutMillis = 30_000
            connectTimeoutMillis = 10_000
            socketTimeoutMillis = 30_000
        }

        defaultRequest {
            url(baseUrl)
            contentType(ContentType.Application.Json)
        }
    }
}

// androidMain
actual fun createPlatformHttpClient(): HttpClient {
    return HttpClient(Android) {
        engine {
            connectTimeout = 10_000
            socketTimeout = 30_000
        }
    }
}

// iosMain
actual fun createPlatformHttpClient(): HttpClient {
    return HttpClient(Darwin) {
        engine {
            configureRequest {
                setAllowsCellularAccess(true)
            }
        }
    }
}
```

### Реализация API сервиса

```kotlin
// commonMain
@Serializable
data class User(
    val id: String,
    val name: String,
    val email: String,
    @SerialName("avatar_url")
    val avatarUrl: String?
)

@Serializable
data class CreateUserRequest(
    val name: String,
    val email: String
)

class UserApiService(private val httpClient: HttpClient) {

    suspend fun getUsers(): List<User> {
        return httpClient.get("/api/v1/users").body()
    }

    suspend fun getUser(id: String): User {
        return httpClient.get("/api/v1/users/$id").body()
    }

    suspend fun createUser(request: CreateUserRequest): User {
        return httpClient.post("/api/v1/users") {
            setBody(request)
        }.body()
    }

    suspend fun updateUser(id: String, request: CreateUserRequest): User {
        return httpClient.put("/api/v1/users/$id") {
            setBody(request)
        }.body()
    }

    suspend fun deleteUser(id: String) {
        httpClient.delete("/api/v1/users/$id")
    }
}
```

### Обработка ошибок

```kotlin
// commonMain
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val exception: NetworkException) : NetworkResult<Nothing>()
}

sealed class NetworkException : Exception() {
    data class HttpError(
        val statusCode: Int,
        override val message: String,
        val body: String?
    ) : NetworkException()

    data class ConnectionError(override val cause: Throwable) : NetworkException()
    data class SerializationError(override val cause: Throwable) : NetworkException()
    object TimeoutError : NetworkException()
    data class UnknownError(override val cause: Throwable) : NetworkException()
}

suspend inline fun <reified T> safeApiCall(
    crossinline call: suspend () -> T
): NetworkResult<T> {
    return try {
        NetworkResult.Success(call())
    } catch (e: ClientRequestException) {
        val body = e.response.bodyAsText()
        NetworkResult.Error(
            NetworkException.HttpError(
                statusCode = e.response.status.value,
                message = e.response.status.description,
                body = body
            )
        )
    } catch (e: HttpRequestTimeoutException) {
        NetworkResult.Error(NetworkException.TimeoutError)
    } catch (e: SerializationException) {
        NetworkResult.Error(NetworkException.SerializationError(e))
    } catch (e: IOException) {
        NetworkResult.Error(NetworkException.ConnectionError(e))
    } catch (e: Exception) {
        NetworkResult.Error(NetworkException.UnknownError(e))
    }
}
```

### Поддержка WebSocket

```kotlin
// commonMain
class WebSocketService(private val httpClient: HttpClient) {

    suspend fun connectToChat(
        roomId: String,
        onMessage: (ChatMessage) -> Unit,
        onError: (Throwable) -> Unit
    ): WebSocketSession {
        return httpClient.webSocketSession("/ws/chat/$roomId").apply {
            launch {
                try {
                    for (frame in incoming) {
                        when (frame) {
                            is Frame.Text -> {
                                val message = Json.decodeFromString<ChatMessage>(frame.readText())
                                onMessage(message)
                            }
                            is Frame.Close -> break
                            else -> {}
                        }
                    }
                } catch (e: Exception) {
                    onError(e)
                }
            }
        }
    }
}
```

### Лучшие практики

1. **Используйте платформо-специфичные движки** - Android (OkHttp), iOS (Darwin/NSURLSession)
2. **Реализуйте правильную обработку ошибок** - Оборачивайте ответы в Result типы
3. **Настраивайте таймауты адекватно** - Особенно для мобильных сетей
4. **Используйте content negotiation** - Автоматическая JSON сериализация
5. **Реализуйте логику повторных попыток** - Для временных сбоев
6. **Правильно закрывайте HttpClient** - В методах очистки/dispose

---

## Follow-ups

- How do you handle certificate pinning in Ktor across platforms?
- What are the differences between Ktor engines (Android, Darwin, CIO)?
- How do you implement request/response interceptors?
- How do you handle offline-first networking in KMP?

## Dopolnitelnye Voprosy (RU)

- Как реализовать certificate pinning в Ktor на разных платформах?
- В чём различия между движками Ktor (Android, Darwin, CIO)?
- Как реализовать перехватчики запросов/ответов?
- Как реализовать offline-first работу с сетью в KMP?

## References

- [Ktor Client Documentation](https://ktor.io/docs/client.html)
- [Ktor GitHub Repository](https://github.com/ktorio/ktor)

## Ssylki (RU)

- [[c-kotlin]]
- [Документация Ktor Client](https://ktor.io/docs/client.html)

## Related Questions

- [[q-kmp-persistence--kmp--medium]]
- [[q-kmp-architecture--kmp--hard]]
