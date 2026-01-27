---
id: android-746
title: Ktor Client on Android / Ktor Client на Android
aliases:
- Ktor Client on Android
- Ktor Client на Android
topic: android
subtopics:
- networking
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-networking
- q-network-resilience--networking--medium
- q-http-caching--networking--medium
created: 2026-01-23
updated: 2026-01-23
sources:
- https://ktor.io/docs/client-overview.html
- https://ktor.io/docs/client-engines.html
tags:
- android/networking
- difficulty/medium
- http-client
- ktor
- kotlin-multiplatform
- serialization
anki_cards:
- slug: android-746-0-en
  language: en
- slug: android-746-0-ru
  language: ru
---
# Vopros (RU)

> Kak nastroit' Ktor Client na Android? Ob"yasnite vybor engine, podklyuchenie plaginov i serializatsiyu.

# Question (EN)

> How do you set up Ktor Client on Android? Explain engine selection, plugin configuration, and serialization.

---

## Otvet (RU)

**Ktor Client** - eto asinkhronnyy HTTP-klient ot JetBrains, ideal'no integrirovannyy s koroutinami i podderzhivayushchiy Kotlin Multiplatform. Na Android rekomenduetsya ispol'zovat' **OkHttp** ili **CIO** engine v zavisimosti ot potrebnostey.

### Kratkiy Otvet

- Dobav'te zavisimosti dlya **ktor-client-core**, **engine** (OkHttp/CIO) i **content-negotiation** s **kotlinx-serialization**
- **OkHttp engine** rekomenduetsya dlya Android - luchshaya sovmestimost', HTTP/2, interceptory
- Konfiguriruyte plaginy cherez blok `install {}` pri sozdanii klienta
- Ispol'zuyte `ContentNegotiation` s `Json` dlya avtomaticheskoy serializatsii/deserializatsii

### Podrobnyy Otvet

### Vybor Engine

| Engine | Preimushchestva | Nedostatki |
|--------|-----------------|------------|
| **OkHttp** | HTTP/2, interceptory, otlichnaya Android-podderzhka | Dopolnitel'naya zavisimost' |
| **CIO** | Chistyy Kotlin, minimal'nye zavisimosti | Net HTTP/2 (v Ktor 3.0) |
| **Android** (ustarevshiy) | Vstroennyy | Ogranichennye vozmozhnosti, ustarevshiy |

**Rekomendatsiya**: Ispol'zovat' **OkHttp** dlya production Android-prilozheniy.

### Nastroyka Zavisimostey (Ktor 3.0+)

```kotlin
// build.gradle.kts
dependencies {
    // Core
    implementation("io.ktor:ktor-client-core:3.0.3")

    // Engine (vybrat' odin)
    implementation("io.ktor:ktor-client-okhttp:3.0.3")
    // ili
    // implementation("io.ktor:ktor-client-cio:3.0.3")

    // Serialization
    implementation("io.ktor:ktor-client-content-negotiation:3.0.3")
    implementation("io.ktor:ktor-serialization-kotlinx-json:3.0.3")

    // Logging (optsional'no)
    implementation("io.ktor:ktor-client-logging:3.0.3")

    // Resources (typed routes, optsional'no)
    implementation("io.ktor:ktor-client-resources:3.0.3")
}
```

### Bazovaya Konfiguratsiya Klienta

```kotlin
@Serializable
data class User(val id: Int, val name: String, val email: String)

val httpClient = HttpClient(OkHttp) {
    // Content Negotiation dlya JSON
    install(ContentNegotiation) {
        json(Json {
            prettyPrint = true
            isLenient = true
            ignoreUnknownKeys = true // Vazhno dlya evolyutsii API
            coerceInputValues = true // null -> default value
        })
    }

    // Logging
    install(Logging) {
        logger = Logger.ANDROID
        level = LogLevel.HEADERS // BODY dlya otladki
        sanitizeHeader { header -> header == HttpHeaders.Authorization }
    }

    // Timeout
    install(HttpTimeout) {
        requestTimeoutMillis = 30_000
        connectTimeoutMillis = 10_000
        socketTimeoutMillis = 30_000
    }

    // Default headers
    defaultRequest {
        header(HttpHeaders.ContentType, ContentType.Application.Json)
        header("X-Api-Version", "2")
    }

    // OkHttp-spetsifichnaya konfiguratsiya
    engine {
        config {
            followRedirects(true)
            // Dobavlenie OkHttp interceptorov
            addInterceptor(AuthInterceptor())
        }
    }
}
```

### Vypolnenie Zaprosov

```kotlin
class UserRepository(private val client: HttpClient) {

    suspend fun getUser(id: Int): User {
        return client.get("https://api.example.com/users/$id").body()
    }

    suspend fun createUser(user: User): User {
        return client.post("https://api.example.com/users") {
            contentType(ContentType.Application.Json)
            setBody(user)
        }.body()
    }

    suspend fun updateUser(id: Int, user: User): User {
        return client.put("https://api.example.com/users/$id") {
            setBody(user)
        }.body()
    }

    suspend fun deleteUser(id: Int): Boolean {
        val response = client.delete("https://api.example.com/users/$id")
        return response.status.isSuccess()
    }

    // Zapros s query-parametrami
    suspend fun searchUsers(query: String, page: Int): List<User> {
        return client.get("https://api.example.com/users") {
            parameter("q", query)
            parameter("page", page)
            parameter("limit", 20)
        }.body()
    }
}
```

### Typed Resources (Ktor 3.0)

```kotlin
// Opredelenie resursov
@Resource("/users")
class Users {
    @Resource("{id}")
    class ById(val parent: Users = Users(), val id: Int)

    @Resource("search")
    class Search(val parent: Users = Users(), val query: String, val page: Int = 1)
}

// Klient s Resources
val client = HttpClient(OkHttp) {
    install(Resources)
    install(ContentNegotiation) { json() }
    defaultRequest {
        url("https://api.example.com")
    }
}

// Ispol'zovanie
suspend fun getUser(id: Int): User {
    return client.get(Users.ById(id = id)).body()
}

suspend fun searchUsers(query: String): List<User> {
    return client.get(Users.Search(query = query, page = 1)).body()
}
```

### Obrabotka Oshibok

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
    data class NetworkError(val exception: Throwable) : ApiResult<Nothing>()
}

suspend inline fun <reified T> HttpClient.safeRequest(
    block: HttpRequestBuilder.() -> Unit
): ApiResult<T> {
    return try {
        val response = request(block)
        if (response.status.isSuccess()) {
            ApiResult.Success(response.body<T>())
        } else {
            ApiResult.Error(response.status.value, response.status.description)
        }
    } catch (e: ClientRequestException) {
        ApiResult.Error(e.response.status.value, e.message ?: "Client error")
    } catch (e: ServerResponseException) {
        ApiResult.Error(e.response.status.value, e.message ?: "Server error")
    } catch (e: IOException) {
        ApiResult.NetworkError(e)
    }
}

// Ispol'zovanie
val result = client.safeRequest<User> {
    method = HttpMethod.Get
    url("https://api.example.com/users/1")
}

when (result) {
    is ApiResult.Success -> println("User: ${result.data}")
    is ApiResult.Error -> println("Error ${result.code}: ${result.message}")
    is ApiResult.NetworkError -> println("Network error: ${result.exception}")
}
```

### Interceptory i Avtorizatsiya

```kotlin
val client = HttpClient(OkHttp) {
    install(Auth) {
        bearer {
            loadTokens {
                BearerTokens(
                    accessToken = tokenRepository.getAccessToken(),
                    refreshToken = tokenRepository.getRefreshToken()
                )
            }
            refreshTokens {
                val response = client.post("https://api.example.com/auth/refresh") {
                    setBody(RefreshRequest(oldTokens?.refreshToken ?: ""))
                }
                val tokens: TokenResponse = response.body()
                tokenRepository.saveTokens(tokens)
                BearerTokens(tokens.accessToken, tokens.refreshToken)
            }
            sendWithoutRequest { request ->
                request.url.host == "api.example.com"
            }
        }
    }
}
```

### Lifecycle Management

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {

    // Klient dolzhen byt' singleton ili scope'd k zhiznennomu tsiklu
    // Zakryvat' pri unichtozhenii
}

// V Hilt module
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideHttpClient(): HttpClient {
        return HttpClient(OkHttp) {
            // konfiguratsiya
        }
    }

    // Zakrytie pri unichtozhenii prilozheniya
    // Ktor client dolzhen byt' zakryt yavno
}
```

### Luchshie Praktiki

1. **Pereispol'zuyte klient** - sozdavayte odin `HttpClient` na prilozheniye
2. **Zakryvayte klient** - vyzyvay `client.close()` pri zavershenii
3. **Ispol'zuyte `ignoreUnknownKeys`** - dlya ustoychivosti k izmeneniyam API
4. **Nastroyte timeout'y** - predotvratite zavisaniye
5. **Logiruyte v debug, ne v release** - bezopasnost'

---

## Answer (EN)

**Ktor Client** is an asynchronous HTTP client from JetBrains, seamlessly integrated with coroutines and supporting Kotlin Multiplatform. On Android, the recommended engines are **OkHttp** or **CIO** depending on your requirements.

### Short Version

- Add dependencies for **ktor-client-core**, **engine** (OkHttp/CIO), and **content-negotiation** with **kotlinx-serialization**
- **OkHttp engine** is recommended for Android - best compatibility, HTTP/2, interceptors
- Configure plugins via `install {}` block when creating the client
- Use `ContentNegotiation` with `Json` for automatic serialization/deserialization

### Detailed Version

### Engine Selection

| Engine | Pros | Cons |
|--------|------|------|
| **OkHttp** | HTTP/2, interceptors, excellent Android support | Additional dependency |
| **CIO** | Pure Kotlin, minimal dependencies | No HTTP/2 (in Ktor 3.0) |
| **Android** (legacy) | Built-in | Limited features, deprecated |

**Recommendation**: Use **OkHttp** for production Android apps.

### Dependency Setup (Ktor 3.0+)

```kotlin
// build.gradle.kts
dependencies {
    // Core
    implementation("io.ktor:ktor-client-core:3.0.3")

    // Engine (choose one)
    implementation("io.ktor:ktor-client-okhttp:3.0.3")
    // or
    // implementation("io.ktor:ktor-client-cio:3.0.3")

    // Serialization
    implementation("io.ktor:ktor-client-content-negotiation:3.0.3")
    implementation("io.ktor:ktor-serialization-kotlinx-json:3.0.3")

    // Logging (optional)
    implementation("io.ktor:ktor-client-logging:3.0.3")

    // Resources (typed routes, optional)
    implementation("io.ktor:ktor-client-resources:3.0.3")
}
```

### Basic Client Configuration

```kotlin
@Serializable
data class User(val id: Int, val name: String, val email: String)

val httpClient = HttpClient(OkHttp) {
    // Content Negotiation for JSON
    install(ContentNegotiation) {
        json(Json {
            prettyPrint = true
            isLenient = true
            ignoreUnknownKeys = true // Important for API evolution
            coerceInputValues = true // null -> default value
        })
    }

    // Logging
    install(Logging) {
        logger = Logger.ANDROID
        level = LogLevel.HEADERS // BODY for debugging
        sanitizeHeader { header -> header == HttpHeaders.Authorization }
    }

    // Timeout
    install(HttpTimeout) {
        requestTimeoutMillis = 30_000
        connectTimeoutMillis = 10_000
        socketTimeoutMillis = 30_000
    }

    // Default headers
    defaultRequest {
        header(HttpHeaders.ContentType, ContentType.Application.Json)
        header("X-Api-Version", "2")
    }

    // OkHttp-specific configuration
    engine {
        config {
            followRedirects(true)
            // Add OkHttp interceptors
            addInterceptor(AuthInterceptor())
        }
    }
}
```

### Making Requests

```kotlin
class UserRepository(private val client: HttpClient) {

    suspend fun getUser(id: Int): User {
        return client.get("https://api.example.com/users/$id").body()
    }

    suspend fun createUser(user: User): User {
        return client.post("https://api.example.com/users") {
            contentType(ContentType.Application.Json)
            setBody(user)
        }.body()
    }

    suspend fun updateUser(id: Int, user: User): User {
        return client.put("https://api.example.com/users/$id") {
            setBody(user)
        }.body()
    }

    suspend fun deleteUser(id: Int): Boolean {
        val response = client.delete("https://api.example.com/users/$id")
        return response.status.isSuccess()
    }

    // Request with query parameters
    suspend fun searchUsers(query: String, page: Int): List<User> {
        return client.get("https://api.example.com/users") {
            parameter("q", query)
            parameter("page", page)
            parameter("limit", 20)
        }.body()
    }
}
```

### Typed Resources (Ktor 3.0)

```kotlin
// Define resources
@Resource("/users")
class Users {
    @Resource("{id}")
    class ById(val parent: Users = Users(), val id: Int)

    @Resource("search")
    class Search(val parent: Users = Users(), val query: String, val page: Int = 1)
}

// Client with Resources
val client = HttpClient(OkHttp) {
    install(Resources)
    install(ContentNegotiation) { json() }
    defaultRequest {
        url("https://api.example.com")
    }
}

// Usage
suspend fun getUser(id: Int): User {
    return client.get(Users.ById(id = id)).body()
}

suspend fun searchUsers(query: String): List<User> {
    return client.get(Users.Search(query = query, page = 1)).body()
}
```

### Error Handling

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
    data class NetworkError(val exception: Throwable) : ApiResult<Nothing>()
}

suspend inline fun <reified T> HttpClient.safeRequest(
    block: HttpRequestBuilder.() -> Unit
): ApiResult<T> {
    return try {
        val response = request(block)
        if (response.status.isSuccess()) {
            ApiResult.Success(response.body<T>())
        } else {
            ApiResult.Error(response.status.value, response.status.description)
        }
    } catch (e: ClientRequestException) {
        ApiResult.Error(e.response.status.value, e.message ?: "Client error")
    } catch (e: ServerResponseException) {
        ApiResult.Error(e.response.status.value, e.message ?: "Server error")
    } catch (e: IOException) {
        ApiResult.NetworkError(e)
    }
}

// Usage
val result = client.safeRequest<User> {
    method = HttpMethod.Get
    url("https://api.example.com/users/1")
}

when (result) {
    is ApiResult.Success -> println("User: ${result.data}")
    is ApiResult.Error -> println("Error ${result.code}: ${result.message}")
    is ApiResult.NetworkError -> println("Network error: ${result.exception}")
}
```

### Interceptors and Authentication

```kotlin
val client = HttpClient(OkHttp) {
    install(Auth) {
        bearer {
            loadTokens {
                BearerTokens(
                    accessToken = tokenRepository.getAccessToken(),
                    refreshToken = tokenRepository.getRefreshToken()
                )
            }
            refreshTokens {
                val response = client.post("https://api.example.com/auth/refresh") {
                    setBody(RefreshRequest(oldTokens?.refreshToken ?: ""))
                }
                val tokens: TokenResponse = response.body()
                tokenRepository.saveTokens(tokens)
                BearerTokens(tokens.accessToken, tokens.refreshToken)
            }
            sendWithoutRequest { request ->
                request.url.host == "api.example.com"
            }
        }
    }
}
```

### Lifecycle Management

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {

    // Client should be singleton or scoped to lifecycle
    // Close on destruction
}

// In Hilt module
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideHttpClient(): HttpClient {
        return HttpClient(OkHttp) {
            // configuration
        }
    }

    // Close on app destruction
    // Ktor client should be closed explicitly
}
```

### Best Practices

1. **Reuse the client** - create one `HttpClient` per application
2. **Close the client** - call `client.close()` on termination
3. **Use `ignoreUnknownKeys`** - for resilience to API changes
4. **Configure timeouts** - prevent hanging
5. **Log in debug, not release** - security

---

## Dopolnitel'nye Voprosy (RU)

1. Kak realizovat' retry-logiku s Ktor Client?
2. V chem raznitsa mezhdu OkHttp i CIO engine?
3. Kak nastroit' certificate pinning s Ktor?
4. Kak testirovat' Ktor Client s MockEngine?
5. Kak ispol'zovat' Ktor Client v Kotlin Multiplatform proekte?

## Follow-ups

1. How do you implement retry logic with Ktor Client?
2. What are the differences between OkHttp and CIO engines?
3. How do you configure certificate pinning with Ktor?
4. How do you test Ktor Client with MockEngine?
5. How do you use Ktor Client in a Kotlin Multiplatform project?

## Ssylki (RU)

- [Dokumentatsiya Ktor Client](https://ktor.io/docs/client-overview.html)
- [Ktor Engines](https://ktor.io/docs/client-engines.html)
- [Ktor Serialization](https://ktor.io/docs/serialization-client.html)

## References

- [Ktor Client Documentation](https://ktor.io/docs/client-overview.html)
- [Ktor Engines](https://ktor.io/docs/client-engines.html)
- [Ktor Serialization](https://ktor.io/docs/serialization-client.html)

## Svyazannye Voprosy (RU)

### Predposylki

- [[q-retrofit-vs-ktor--networking--easy]]
- [[q-kotlinx-serialization--kotlin--medium]]

### Pokhozhie

- [[q-network-resilience--networking--medium]]
- [[q-http-caching--networking--medium]]

### Prodvinutoe

- [[q-websocket-handling--networking--hard]]
- [[q-grpc-android--networking--hard]]

## Related Questions

### Prerequisites

- [[q-retrofit-vs-ktor--networking--easy]]
- [[q-kotlinx-serialization--kotlin--medium]]

### Related

- [[q-network-resilience--networking--medium]]
- [[q-http-caching--networking--medium]]

### Advanced

- [[q-websocket-handling--networking--hard]]
- [[q-grpc-android--networking--hard]]
