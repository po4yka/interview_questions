---
id: kotlin-kmp-003
title: "KMP Shared Code Strategy / Стратегия разделения кода в KMP"
aliases: [What to Share KMP, KMP Code Sharing Strategy, Platform vs Shared Code]
topic: kotlin
subtopics: [kmp, multiplatform, architecture, code-sharing]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin]
created: 2026-01-23
updated: 2026-01-23
tags: [kotlin, kmp, multiplatform, architecture, code-sharing, difficulty/hard]
---

# Question (EN)
> What code should you share in KMP vs keep platform-specific? How do you decide?

# Vopros (RU)
> Какой код следует выносить в общую часть KMP, а какой оставлять платформо-специфичным? Как принять решение?

## Answer (EN)

Deciding what to share in Kotlin Multiplatform requires balancing code reuse benefits against platform-specific UX, performance, and maintenance costs.

### The Sharing Spectrum

```
100% Shared          Balanced              100% Native
    |-------------------|-------------------|
    |                   |                   |
Business Logic    Data Layer           UI Layer
Data Models       Networking        Platform APIs
Algorithms        Storage           Native Features
```

### Code to SHARE (High ROI)

#### 1. Business Logic / Domain Layer
```kotlin
// commonMain - Pure business rules, always shareable
class PaymentValidator {
    fun validateCard(cardNumber: String): ValidationResult {
        return when {
            cardNumber.length !in 13..19 -> ValidationResult.InvalidLength
            !passesLuhnCheck(cardNumber) -> ValidationResult.InvalidChecksum
            else -> ValidationResult.Valid
        }
    }
}

class PriceCalculator {
    fun calculateTotal(
        items: List<CartItem>,
        discount: Discount?,
        taxRate: Double
    ): Money {
        val subtotal = items.sumOf { it.price * it.quantity }
        val discounted = discount?.apply(subtotal) ?: subtotal
        return Money(discounted * (1 + taxRate))
    }
}
```

#### 2. Data Models
```kotlin
// commonMain - Data classes work everywhere
@Serializable
data class User(
    val id: String,
    val email: String,
    val profile: UserProfile,
    val createdAt: Instant
)

@Serializable
sealed class ApiResponse<T> {
    data class Success<T>(val data: T) : ApiResponse<T>()
    data class Error<T>(val code: Int, val message: String) : ApiResponse<T>()
}
```

#### 3. Networking Layer
```kotlin
// commonMain - Ktor works on all platforms
class ApiClient(private val httpClient: HttpClient) {
    suspend fun getUser(id: String): User {
        return httpClient.get("$BASE_URL/users/$id").body()
    }

    suspend fun updateProfile(profile: UserProfile): ApiResponse<User> {
        return httpClient.put("$BASE_URL/profile") {
            contentType(ContentType.Application.Json)
            setBody(profile)
        }.body()
    }
}
```

#### 4. State Management
```kotlin
// commonMain - Shared state containers
class UserStore {
    private val _state = MutableStateFlow(UserState.Initial)
    val state: StateFlow<UserState> = _state.asStateFlow()

    fun dispatch(action: UserAction) {
        _state.update { currentState ->
            reduce(currentState, action)
        }
    }

    private fun reduce(state: UserState, action: UserAction): UserState {
        return when (action) {
            is UserAction.LoadUser -> state.copy(isLoading = true)
            is UserAction.UserLoaded -> state.copy(
                isLoading = false,
                user = action.user
            )
            is UserAction.Error -> state.copy(
                isLoading = false,
                error = action.message
            )
        }
    }
}
```

### Code to Keep PLATFORM-SPECIFIC

#### 1. UI Layer (Usually)
```kotlin
// Android - Jetpack Compose
@Composable
fun UserProfileScreen(viewModel: UserViewModel) {
    val state by viewModel.state.collectAsState()
    // Native Android UI with Material Design
}

// iOS - SwiftUI
struct UserProfileView: View {
    @ObservedObject var viewModel: UserViewModel
    var body: some View {
        // Native iOS UI with iOS design patterns
    }
}
```

#### 2. Platform-Specific APIs
```kotlin
// Platform biometrics - can't be shared
// androidMain
actual class BiometricAuth actual constructor() {
    actual suspend fun authenticate(): AuthResult {
        // Use AndroidX Biometric library
    }
}

// iosMain
actual class BiometricAuth actual constructor() {
    actual suspend fun authenticate(): AuthResult {
        // Use LocalAuthentication framework (Face ID/Touch ID)
    }
}
```

#### 3. Performance-Critical Code
```kotlin
// When native implementation significantly outperforms shared
// androidMain
actual class ImageProcessor {
    actual fun processImage(bitmap: ByteArray): ByteArray {
        // Use Android RenderScript or Vulkan
    }
}

// iosMain
actual class ImageProcessor {
    actual fun processImage(bitmap: ByteArray): ByteArray {
        // Use Metal or Accelerate framework
    }
}
```

### Decision Framework

| Question | Share | Platform-Specific |
|----------|-------|-------------------|
| Does it have business rules? | Yes | - |
| Is it pure data transformation? | Yes | - |
| Does it need platform APIs? | - | Yes |
| Is platform UX important here? | - | Yes |
| Is performance critical? | Evaluate | Evaluate |
| Does library exist for KMP? | Yes | - |
| Single-platform feature? | - | Yes |

### Architecture Patterns for Sharing

#### Clean Architecture Approach
```
                    Platform Layer (UI)
                           |
                    expect/actual
                           |
                   Presentation Layer (shared ViewModels)
                           |
                    Domain Layer (100% shared)
                           |
                     Data Layer (mostly shared)
                           |
                    expect/actual
                           |
                  Platform Data Sources
```

#### Recommended Sharing Levels

| Layer | Sharing Level | Notes |
|-------|---------------|-------|
| **Domain** | 100% | Business logic, use cases |
| **Data** | 90%+ | Repositories, API clients, models |
| **Presentation** | 70-90% | ViewModels, state management |
| **UI** | 0-30%* | Native by default, Compose Multiplatform optional |

*With Compose Multiplatform, UI sharing can reach 80-100%

### Practical Example: E-Commerce App

```kotlin
// SHARED (commonMain)
- CartRepository, OrderRepository
- Product, Order, User data classes
- PriceCalculator, InventoryChecker
- CartViewModel, CheckoutViewModel
- PaymentValidator, AddressValidator
- ApiClient, all networking

// PLATFORM-SPECIFIC
- Push notification handling
- Payment SDK integration (Stripe Android vs iOS)
- Deep link handling
- App widgets (Android) / Widgets (iOS)
- Platform-specific analytics (if not using shared SDK)
```

### Migration Strategy

1. **Start with domain layer** - easiest to share, highest ROI
2. **Move to data layer** - networking, storage abstractions
3. **Share ViewModels** - if using shared state management
4. **Evaluate UI sharing** - Compose Multiplatform if appropriate

---

## Otvet (RU)

Решение о том, что выносить в общую часть в Kotlin Multiplatform, требует баланса между преимуществами переиспользования кода и платформо-специфичным UX, производительностью и затратами на поддержку.

### Спектр разделения

```
100% Общий           Сбалансированный      100% Нативный
    |-------------------|-------------------|
    |                   |                   |
Бизнес-логика     Слой данных          UI слой
Модели данных     Сеть                 Платформенные API
Алгоритмы         Хранилище            Нативные функции
```

### Код для РАЗДЕЛЕНИЯ (Высокий ROI)

#### 1. Бизнес-логика / Domain слой
```kotlin
// commonMain - Чистые бизнес-правила, всегда можно разделить
class PaymentValidator {
    fun validateCard(cardNumber: String): ValidationResult {
        return when {
            cardNumber.length !in 13..19 -> ValidationResult.InvalidLength
            !passesLuhnCheck(cardNumber) -> ValidationResult.InvalidChecksum
            else -> ValidationResult.Valid
        }
    }
}

class PriceCalculator {
    fun calculateTotal(
        items: List<CartItem>,
        discount: Discount?,
        taxRate: Double
    ): Money {
        val subtotal = items.sumOf { it.price * it.quantity }
        val discounted = discount?.apply(subtotal) ?: subtotal
        return Money(discounted * (1 + taxRate))
    }
}
```

#### 2. Модели данных
```kotlin
// commonMain - Data классы работают везде
@Serializable
data class User(
    val id: String,
    val email: String,
    val profile: UserProfile,
    val createdAt: Instant
)

@Serializable
sealed class ApiResponse<T> {
    data class Success<T>(val data: T) : ApiResponse<T>()
    data class Error<T>(val code: Int, val message: String) : ApiResponse<T>()
}
```

#### 3. Сетевой слой
```kotlin
// commonMain - Ktor работает на всех платформах
class ApiClient(private val httpClient: HttpClient) {
    suspend fun getUser(id: String): User {
        return httpClient.get("$BASE_URL/users/$id").body()
    }

    suspend fun updateProfile(profile: UserProfile): ApiResponse<User> {
        return httpClient.put("$BASE_URL/profile") {
            contentType(ContentType.Application.Json)
            setBody(profile)
        }.body()
    }
}
```

#### 4. Управление состоянием
```kotlin
// commonMain - Общие контейнеры состояния
class UserStore {
    private val _state = MutableStateFlow(UserState.Initial)
    val state: StateFlow<UserState> = _state.asStateFlow()

    fun dispatch(action: UserAction) {
        _state.update { currentState ->
            reduce(currentState, action)
        }
    }

    private fun reduce(state: UserState, action: UserAction): UserState {
        return when (action) {
            is UserAction.LoadUser -> state.copy(isLoading = true)
            is UserAction.UserLoaded -> state.copy(
                isLoading = false,
                user = action.user
            )
            is UserAction.Error -> state.copy(
                isLoading = false,
                error = action.message
            )
        }
    }
}
```

### Код для ПЛАТФОРМО-СПЕЦИФИЧНОЙ реализации

#### 1. UI слой (обычно)
```kotlin
// Android - Jetpack Compose
@Composable
fun UserProfileScreen(viewModel: UserViewModel) {
    val state by viewModel.state.collectAsState()
    // Нативный Android UI с Material Design
}

// iOS - SwiftUI
struct UserProfileView: View {
    @ObservedObject var viewModel: UserViewModel
    var body: some View {
        // Нативный iOS UI с iOS паттернами дизайна
    }
}
```

#### 2. Платформо-специфичные API
```kotlin
// Платформенная биометрия - нельзя разделить
// androidMain
actual class BiometricAuth actual constructor() {
    actual suspend fun authenticate(): AuthResult {
        // Использовать AndroidX Biometric библиотеку
    }
}

// iosMain
actual class BiometricAuth actual constructor() {
    actual suspend fun authenticate(): AuthResult {
        // Использовать LocalAuthentication framework (Face ID/Touch ID)
    }
}
```

#### 3. Критичный к производительности код
```kotlin
// Когда нативная реализация значительно превосходит общую
// androidMain
actual class ImageProcessor {
    actual fun processImage(bitmap: ByteArray): ByteArray {
        // Использовать Android RenderScript или Vulkan
    }
}

// iosMain
actual class ImageProcessor {
    actual fun processImage(bitmap: ByteArray): ByteArray {
        // Использовать Metal или Accelerate framework
    }
}
```

### Фреймворк принятия решений

| Вопрос | Разделить | Платформо-специфично |
|--------|-----------|---------------------|
| Есть бизнес-правила? | Да | - |
| Чистая трансформация данных? | Да | - |
| Нужны платформенные API? | - | Да |
| Важен платформенный UX здесь? | - | Да |
| Критична производительность? | Оценить | Оценить |
| Существует KMP библиотека? | Да | - |
| Фича только для одной платформы? | - | Да |

### Архитектурные паттерны для разделения

#### Подход Clean Architecture
```
                    Platform Layer (UI)
                           |
                    expect/actual
                           |
                   Presentation Layer (общие ViewModels)
                           |
                    Domain Layer (100% общий)
                           |
                     Data Layer (в основном общий)
                           |
                    expect/actual
                           |
                  Platform Data Sources
```

#### Рекомендуемые уровни разделения

| Слой | Уровень разделения | Примечания |
|------|-------------------|------------|
| **Domain** | 100% | Бизнес-логика, use cases |
| **Data** | 90%+ | Репозитории, API клиенты, модели |
| **Presentation** | 70-90% | ViewModels, управление состоянием |
| **UI** | 0-30%* | Нативный по умолчанию, Compose Multiplatform опционально |

*С Compose Multiplatform разделение UI может достигать 80-100%

### Практический пример: E-Commerce приложение

```kotlin
// ОБЩЕЕ (commonMain)
- CartRepository, OrderRepository
- Product, Order, User data классы
- PriceCalculator, InventoryChecker
- CartViewModel, CheckoutViewModel
- PaymentValidator, AddressValidator
- ApiClient, вся работа с сетью

// ПЛАТФОРМО-СПЕЦИФИЧНОЕ
- Обработка push-уведомлений
- Интеграция платёжного SDK (Stripe Android vs iOS)
- Обработка deep links
- App widgets (Android) / Widgets (iOS)
- Платформо-специфичная аналитика (если не используется общий SDK)
```

### Стратегия миграции

1. **Начните с domain слоя** - проще всего разделить, высший ROI
2. **Переходите к data слою** - сеть, абстракции хранилища
3. **Разделяйте ViewModels** - если используете общее управление состоянием
4. **Оцените разделение UI** - Compose Multiplatform если подходит

---

## Follow-ups

- How do you measure code sharing percentage in KMP?
- What are the trade-offs of sharing ViewModels?
- When should you use Compose Multiplatform for UI sharing?
- How do you handle platform-specific edge cases in shared code?

## Dopolnitelnye Voprosy (RU)

- Как измерить процент разделения кода в KMP?
- Какие компромиссы при разделении ViewModels?
- Когда стоит использовать Compose Multiplatform для разделения UI?
- Как обрабатывать платформо-специфичные краевые случаи в общем коде?

## References

- [KMP Code Sharing Best Practices](https://kotlinlang.org/docs/multiplatform-share-on-platforms.html)
- [Touchlab KMP Best Practices](https://touchlab.co/kotlin-multiplatform-libraries)

## Ssylki (RU)

- [[c-kotlin]]
- [Лучшие практики разделения кода KMP](https://kotlinlang.org/docs/multiplatform-share-on-platforms.html)

## Related Questions

- [[q-kmp-architecture--kmp--hard]]
- [[q-kmp-expect-actual--kmp--medium]]
- [[q-compose-multiplatform--kmp--medium]]
