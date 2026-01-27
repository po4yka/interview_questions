---
id: android-750
title: Ktor Client for Android / Ktor Client для Android
aliases:
- Ktor Client for Android
- Ktor Client для Android
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
- q-retrofit-library--android--medium
- q-kmm-ktor-networking--android--medium
created: 2026-01-23
updated: 2026-01-23
sources:
- https://ktor.io/docs/client-overview.html
- https://ktor.io/docs/client-engines.html
- https://ktor.io/docs/client-multiplatform.html
tags:
- android/networking
- difficulty/medium
- http-client
- ktor
- kotlin-multiplatform
- coroutines
anki_cards:
- slug: android-750-0-en
  language: en
- slug: android-750-0-ru
  language: ru
---
# Vopros (RU)

> Kak ispol'zovat' Ktor Client na Android? Ob"yasnite multiplatformennuyu nastrojku, vybor engine i osnovnye preimushchestva pered Retrofit.

# Question (EN)

> How do you use Ktor Client on Android? Explain multiplatform setup, engine selection, and key advantages over Retrofit.

---

## Otvet (RU)

**Ktor Client** - eto asinkhronnyy HTTP-klient ot JetBrains, polnost'yu napisannyy na Kotlin i gluboko integrirovannyy s koroutinami. Glavnoe preimushchestvo - podderzhka Kotlin Multiplatform (KMP), pozvolyayushchaya ispol'zovat' odin kod dlya Android, iOS, Desktop i Backend.

### Kratkiy Otvet

- **Ktor Client** - chistyy Kotlin HTTP-klient s native podderzhkoy koroutin
- Na Android ispol'zuyte **OkHttp engine** dlya luchshey sovmestimosti i HTTP/2
- **Multiplatform**: odin interfeys - raznye engine dlya kazhdoy platformy (OkHttp na Android, Darwin na iOS)
- **Preimushchestva pered Retrofit**: KMP podderzhka, DSL-konfiguratsiya, native suspend funktsii

### Podrobnyy Otvet

### Engine Selection dlya Android

| Engine | Kogda ispol'zovat' | Osobennosti |
|--------|-------------------|-------------|
| **OkHttp** | Production Android | HTTP/2, interceptory, certificate pinning |
| **CIO** | KMP bez platform-spetsifik | Chistyy Kotlin, minimal'nye zavisimosti |
| **Android** | Ustarevshiy | Ne rekomenduetsya, ogranichennye vozmozhnosti |

**Rekomendatsiya dlya Android**: OkHttp engine obespechet maksimal'nuyu sovmestimost' i proizvoditel'nost'.

### Nastroyka Zavisimostey (Ktor 3.0+)

```kotlin
// build.gradle.kts (shared module dlya KMP)
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("io.ktor:ktor-client-core:3.0.3")
            implementation("io.ktor:ktor-client-content-negotiation:3.0.3")
            implementation("io.ktor:ktor-serialization-kotlinx-json:3.0.3")
            implementation("io.ktor:ktor-client-logging:3.0.3")
        }

        androidMain.dependencies {
            implementation("io.ktor:ktor-client-okhttp:3.0.3")
        }

        iosMain.dependencies {
            implementation("io.ktor:ktor-client-darwin:3.0.3")
        }
    }
}
```

### Bazovaya Konfiguratsiya Klienta

```kotlin
// commonMain - obshchiy kod
expect fun createPlatformEngine(): HttpClientEngine

class ApiClient {
    val httpClient = HttpClient(createPlatformEngine()) {
        // Content Negotiation dlya JSON
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = false
                isLenient = true
                ignoreUnknownKeys = true
                coerceInputValues = true
            })
        }

        // Logging
        install(Logging) {
            level = LogLevel.HEADERS
            logger = object : Logger {
                override fun log(message: String) {
                    println("Ktor: $message")
                }
            }
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
            url("https://api.example.com/")
        }
    }
}

// androidMain
actual fun createPlatformEngine(): HttpClientEngine = OkHttp.create {
    config {
        followRedirects(true)
        connectTimeout(10, TimeUnit.SECONDS)
    }
}

// iosMain
actual fun createPlatformEngine(): HttpClientEngine = Darwin.create()
```

### Vypolnenie Zaprosov (Suspend Funktsii)

```kotlin
@Serializable
data class User(val id: Int, val name: String, val email: String)

@Serializable
data class CreateUserRequest(val name: String, val email: String)

class UserRepository(private val client: HttpClient) {

    // GET zapros
    suspend fun getUser(id: Int): User {
        return client.get("users/$id").body()
    }

    // POST zapros
    suspend fun createUser(request: CreateUserRequest): User {
        return client.post("users") {
            contentType(ContentType.Application.Json)
            setBody(request)
        }.body()
    }

    // GET s query parametrami
    suspend fun searchUsers(query: String, page: Int = 1): List<User> {
        return client.get("users/search") {
            parameter("q", query)
            parameter("page", page)
            parameter("limit", 20)
        }.body()
    }

    // DELETE zapros
    suspend fun deleteUser(id: Int): Boolean {
        val response = client.delete("users/$id")
        return response.status.isSuccess()
    }
}
```

### Obrabotka Oshibok

```kotlin
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val code: Int, val message: String) : NetworkResult<Nothing>()
    data class NetworkError(val exception: Throwable) : NetworkResult<Nothing>()
}

suspend inline fun <reified T> HttpClient.safeRequest(
    block: HttpRequestBuilder.() -> Unit
): NetworkResult<T> {
    return try {
        val response = request(block)
        if (response.status.isSuccess()) {
            NetworkResult.Success(response.body<T>())
        } else {
            NetworkResult.Error(response.status.value, response.status.description)
        }
    } catch (e: ClientRequestException) {
        NetworkResult.Error(e.response.status.value, e.message ?: "Client error")
    } catch (e: ServerResponseException) {
        NetworkResult.Error(e.response.status.value, e.message ?: "Server error")
    } catch (e: IOException) {
        NetworkResult.NetworkError(e)
    }
}

// Ispol'zovanie
val result = client.safeRequest<User> {
    method = HttpMethod.Get
    url("users/1")
}

when (result) {
    is NetworkResult.Success -> println("User: ${result.data}")
    is NetworkResult.Error -> println("Error ${result.code}: ${result.message}")
    is NetworkResult.NetworkError -> println("Network error: ${result.exception}")
}
```

### Avtorizatsiya s Bearer Token

```kotlin
val client = HttpClient(OkHttp) {
    install(Auth) {
        bearer {
            loadTokens {
                BearerTokens(
                    accessToken = tokenStorage.getAccessToken() ?: "",
                    refreshToken = tokenStorage.getRefreshToken() ?: ""
                )
            }

            refreshTokens {
                val response = client.post("auth/refresh") {
                    setBody(RefreshRequest(oldTokens?.refreshToken ?: ""))
                }
                val tokens: TokenResponse = response.body()
                tokenStorage.saveTokens(tokens.accessToken, tokens.refreshToken)
                BearerTokens(tokens.accessToken, tokens.refreshToken)
            }

            sendWithoutRequest { request ->
                request.url.host == "api.example.com"
            }
        }
    }
}
```

### Sravnenie s Retrofit

| Aspekt | Ktor Client | Retrofit |
|--------|-------------|----------|
| **KMP podderzhka** | Native | Net (tol'ko JVM) |
| **Koroutiny** | Native suspend | Cherez adapter |
| **Konfiguratsiya** | DSL | Annotatsii + Builder |
| **Razmer** | Men'she (bez OkHttp) | Bol'she |
| **Ekosistema** | Rastet | Zrelaya |
| **Learning curve** | Srednyaya | Nizkaya |

**Kogda vybrat' Ktor**:
- Kotlin Multiplatform proekt
- Nuzhna maksimal'naya integratsiya s koroutinami
- Predpochtitaete DSL konfiguratsiyu

**Kogda vybrat' Retrofit**:
- Tol'ko Android proekt
- Bol'shaya komanda s opytom Retrofit
- Nuzhna zrelaya ekosistema i mnozhhestvo adapterov

### Luchshie Praktiki

1. **Singleton HttpClient** - sozdavat' odin klient na prilozheniye
2. **Zakryvat' klient** - vyzyvat' `client.close()` pri zavershenii
3. **ignoreUnknownKeys = true** - ustoychivost' k izmeneniyam API
4. **Strukturirovannye timeout'y** - razdelyat' connect/request/socket
5. **Loginrovanie tol'ko v debug** - ne logirovvat' body v production

---

## Answer (EN)

**Ktor Client** is an asynchronous HTTP client from JetBrains, written entirely in Kotlin with deep coroutine integration. The main advantage is Kotlin Multiplatform (KMP) support, allowing shared networking code across Android, iOS, Desktop, and Backend.

### Short Version

- **Ktor Client** - pure Kotlin HTTP client with native coroutine support
- On Android use **OkHttp engine** for best compatibility and HTTP/2
- **Multiplatform**: single interface - different engines per platform (OkHttp on Android, Darwin on iOS)
- **Advantages over Retrofit**: KMP support, DSL configuration, native suspend functions

### Detailed Version

### Engine Selection for Android

| Engine | When to Use | Features |
|--------|-------------|----------|
| **OkHttp** | Production Android | HTTP/2, interceptors, certificate pinning |
| **CIO** | KMP without platform specifics | Pure Kotlin, minimal dependencies |
| **Android** | Legacy | Not recommended, limited features |

**Recommendation for Android**: OkHttp engine provides maximum compatibility and performance.

### Dependency Setup (Ktor 3.0+)

```kotlin
// build.gradle.kts (shared module for KMP)
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("io.ktor:ktor-client-core:3.0.3")
            implementation("io.ktor:ktor-client-content-negotiation:3.0.3")
            implementation("io.ktor:ktor-serialization-kotlinx-json:3.0.3")
            implementation("io.ktor:ktor-client-logging:3.0.3")
        }

        androidMain.dependencies {
            implementation("io.ktor:ktor-client-okhttp:3.0.3")
        }

        iosMain.dependencies {
            implementation("io.ktor:ktor-client-darwin:3.0.3")
        }
    }
}
```

### Basic Client Configuration

```kotlin
// commonMain - shared code
expect fun createPlatformEngine(): HttpClientEngine

class ApiClient {
    val httpClient = HttpClient(createPlatformEngine()) {
        // Content Negotiation for JSON
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = false
                isLenient = true
                ignoreUnknownKeys = true
                coerceInputValues = true
            })
        }

        // Logging
        install(Logging) {
            level = LogLevel.HEADERS
            logger = object : Logger {
                override fun log(message: String) {
                    println("Ktor: $message")
                }
            }
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
            url("https://api.example.com/")
        }
    }
}

// androidMain
actual fun createPlatformEngine(): HttpClientEngine = OkHttp.create {
    config {
        followRedirects(true)
        connectTimeout(10, TimeUnit.SECONDS)
    }
}

// iosMain
actual fun createPlatformEngine(): HttpClientEngine = Darwin.create()
```

### Making Requests (Suspend Functions)

```kotlin
@Serializable
data class User(val id: Int, val name: String, val email: String)

@Serializable
data class CreateUserRequest(val name: String, val email: String)

class UserRepository(private val client: HttpClient) {

    // GET request
    suspend fun getUser(id: Int): User {
        return client.get("users/$id").body()
    }

    // POST request
    suspend fun createUser(request: CreateUserRequest): User {
        return client.post("users") {
            contentType(ContentType.Application.Json)
            setBody(request)
        }.body()
    }

    // GET with query parameters
    suspend fun searchUsers(query: String, page: Int = 1): List<User> {
        return client.get("users/search") {
            parameter("q", query)
            parameter("page", page)
            parameter("limit", 20)
        }.body()
    }

    // DELETE request
    suspend fun deleteUser(id: Int): Boolean {
        val response = client.delete("users/$id")
        return response.status.isSuccess()
    }
}
```

### Error Handling

```kotlin
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val code: Int, val message: String) : NetworkResult<Nothing>()
    data class NetworkError(val exception: Throwable) : NetworkResult<Nothing>()
}

suspend inline fun <reified T> HttpClient.safeRequest(
    block: HttpRequestBuilder.() -> Unit
): NetworkResult<T> {
    return try {
        val response = request(block)
        if (response.status.isSuccess()) {
            NetworkResult.Success(response.body<T>())
        } else {
            NetworkResult.Error(response.status.value, response.status.description)
        }
    } catch (e: ClientRequestException) {
        NetworkResult.Error(e.response.status.value, e.message ?: "Client error")
    } catch (e: ServerResponseException) {
        NetworkResult.Error(e.response.status.value, e.message ?: "Server error")
    } catch (e: IOException) {
        NetworkResult.NetworkError(e)
    }
}

// Usage
val result = client.safeRequest<User> {
    method = HttpMethod.Get
    url("users/1")
}

when (result) {
    is NetworkResult.Success -> println("User: ${result.data}")
    is NetworkResult.Error -> println("Error ${result.code}: ${result.message}")
    is NetworkResult.NetworkError -> println("Network error: ${result.exception}")
}
```

### Authentication with Bearer Token

```kotlin
val client = HttpClient(OkHttp) {
    install(Auth) {
        bearer {
            loadTokens {
                BearerTokens(
                    accessToken = tokenStorage.getAccessToken() ?: "",
                    refreshToken = tokenStorage.getRefreshToken() ?: ""
                )
            }

            refreshTokens {
                val response = client.post("auth/refresh") {
                    setBody(RefreshRequest(oldTokens?.refreshToken ?: ""))
                }
                val tokens: TokenResponse = response.body()
                tokenStorage.saveTokens(tokens.accessToken, tokens.refreshToken)
                BearerTokens(tokens.accessToken, tokens.refreshToken)
            }

            sendWithoutRequest { request ->
                request.url.host == "api.example.com"
            }
        }
    }
}
```

### Comparison with Retrofit

| Aspect | Ktor Client | Retrofit |
|--------|-------------|----------|
| **KMP support** | Native | No (JVM only) |
| **Coroutines** | Native suspend | Via adapter |
| **Configuration** | DSL | Annotations + Builder |
| **Size** | Smaller (without OkHttp) | Larger |
| **Ecosystem** | Growing | Mature |
| **Learning curve** | Medium | Low |

**When to choose Ktor**:
- Kotlin Multiplatform project
- Need maximum coroutine integration
- Prefer DSL configuration

**When to choose Retrofit**:
- Android-only project
- Large team with Retrofit experience
- Need mature ecosystem and many adapters

### Best Practices

1. **Singleton HttpClient** - create one client per application
2. **Close the client** - call `client.close()` on termination
3. **ignoreUnknownKeys = true** - resilience to API changes
4. **Structured timeouts** - separate connect/request/socket
5. **Log only in debug** - don't log body in production

---

## Dopolnitel'nye Voprosy (RU)

1. Kak nastroit' certificate pinning s Ktor na Android?
2. Kak testirovat' Ktor Client s MockEngine?
3. Kak realizovat' retry-logiku s eksponentsial'noy zaderzhkoy?
4. V chem raznitsa mezhdu CIO i OkHttp engine?
5. Kak ispol'zovat' Ktor WebSocket dlya real-time kommunikatsii?

## Follow-ups

1. How do you configure certificate pinning with Ktor on Android?
2. How do you test Ktor Client with MockEngine?
3. How do you implement retry logic with exponential backoff?
4. What are the differences between CIO and OkHttp engines?
5. How do you use Ktor WebSocket for real-time communication?

## Ssylki (RU)

- [Dokumentatsiya Ktor Client](https://ktor.io/docs/client-overview.html)
- [Ktor Engines](https://ktor.io/docs/client-engines.html)
- [Ktor Multiplatform](https://ktor.io/docs/client-multiplatform.html)

## References

- [Ktor Client Documentation](https://ktor.io/docs/client-overview.html)
- [Ktor Engines](https://ktor.io/docs/client-engines.html)
- [Ktor Multiplatform](https://ktor.io/docs/client-multiplatform.html)

## Svyazannye Voprosy (RU)

### Predposylki

- [[q-retrofit-library--android--medium]]
- [[q-kotlinx-serialization--kotlin--medium]]

### Pokhozhie

- [[q-kmm-ktor-networking--android--medium]]
- [[q-http-protocols-comparison--android--medium]]

### Prodvinutoe

- [[q-websockets-android--networking--hard]]
- [[q-grpc-android--networking--hard]]

## Related Questions

### Prerequisites

- [[q-retrofit-library--android--medium]]
- [[q-kotlinx-serialization--kotlin--medium]]

### Related

- [[q-kmm-ktor-networking--android--medium]]
- [[q-http-protocols-comparison--android--medium]]

### Advanced

- [[q-websockets-android--networking--hard]]
- [[q-grpc-android--networking--hard]]
