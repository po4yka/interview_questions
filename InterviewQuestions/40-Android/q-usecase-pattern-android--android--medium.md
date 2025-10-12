---
id: 20251006-016
title: "UseCase Pattern in Android / Паттерн UseCase в Android"
aliases: []

# Classification
topic: android
subtopics: [architecture, usecase, clean-architecture, domain-layer]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-android
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android, architecture, usecase, clean-architecture, domain-layer, difficulty/medium]
---
# Question (EN)
> What is the UseCase pattern in Android? When and how to implement it?
# Вопрос (RU)
> Что такое паттерн UseCase в Android? Когда и как его реализовать?

---

## Answer (EN)

**UseCase** (or Interactor) encapsulates a single business operation, making business logic reusable and testable.

### Basic Implementation

```kotlin
class GetUserUseCase(
    private val repository: UserRepository
) {
    suspend operator fun invoke(userId: String): Result<User> {
        return repository.getUser(userId)
    }
}

// Usage in ViewModel
class UserViewModel(
    private val getUserUseCase: GetUserUseCase
) : ViewModel() {

    fun loadUser(userId: String) {
        viewModelScope.launch {
            getUserUseCase(userId)
                .onSuccess { user ->
                    _uiState.value = UiState.Success(user)
                }
                .onFailure { error ->
                    _uiState.value = UiState.Error(error.message)
                }
        }
    }
}
```

### UseCase with Parameters

```kotlin
data class LoginParams(
    val email: String,
    val password: String
)

class LoginUseCase(
    private val authRepository: AuthRepository,
    private val userRepository: UserRepository,
    private val analytics: Analytics
) {
    suspend operator fun invoke(params: LoginParams): Result<User> {
        return try {
            // 1. Validate
            if (!isValidEmail(params.email)) {
                return Result.failure(InvalidEmailException())
            }

            // 2. Authenticate
            val token = authRepository.login(params.email, params.password)

            // 3. Fetch user data
            val user = userRepository.getCurrentUser(token)

            // 4. Log event
            analytics.logEvent("user_logged_in", mapOf("userId" to user.id))

            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun isValidEmail(email: String): Boolean {
        return email.contains("@")
    }
}
```

### UseCase with Flow

```kotlin
class ObserveUserUseCase(
    private val repository: UserRepository
) {
    operator fun invoke(userId: String): Flow<User> {
        return repository.observeUser(userId)
    }
}

// Usage
class ProfileViewModel(
    observeUserUseCase: ObserveUserUseCase
) : ViewModel() {

    val user: StateFlow<User?> = observeUserUseCase("user123")
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = null
        )
}
```

### When to Use UseCases

**- Use when:**
- Complex business logic
- Multiple repositories involved
- Logic reused across ViewModels
- Need clear separation of concerns

**- Don't use when:**
- Simple repository calls
- One-to-one mapping to repository
- Adds unnecessary layer

```kotlin
// - BAD - Unnecessary UseCase
class GetProductsUseCase(private val repo: ProductRepository) {
    suspend operator fun invoke() = repo.getProducts()
}
// Better: Call repository directly from ViewModel

// - GOOD - Complex logic
class PurchaseProductUseCase(
    private val productRepo: ProductRepository,
    private val paymentRepo: PaymentRepository,
    private val analyticsRepo: AnalyticsRepository
) {
    suspend operator fun invoke(productId: String): Result<Purchase> {
        // Multiple steps, multiple repositories
        val product = productRepo.getProduct(productId)
        val payment = paymentRepo.processPayment(product.price)
        analyticsRepo.logPurchase(productId)
        return Result.success(Purchase(product, payment))
    }
}
```

**English Summary**: UseCase encapsulates single business operation. Benefits: reusable logic, testability, separation of concerns. Implement with `operator fun invoke()`. Use for: complex logic, multiple repositories. Don't use for simple repository calls. Can return Flow for reactive data.

## Ответ (RU)

**UseCase** (или Interactor) инкапсулирует одну бизнес-операцию, делая бизнес-логику переиспользуемой и тестируемой.

### Базовая реализация

```kotlin
class GetUserUseCase(
    private val repository: UserRepository
) {
    suspend operator fun invoke(userId: String): Result<User> {
        return repository.getUser(userId)
    }
}

// Использование в ViewModel
class UserViewModel(
    private val getUserUseCase: GetUserUseCase
) : ViewModel() {
    fun loadUser(userId: String) {
        viewModelScope.launch {
            getUserUseCase(userId)
                .onSuccess { user ->
                    _uiState.value = UiState.Success(user)
                }
        }
    }
}
```

### Когда использовать UseCases

**- Использовать когда:**
- Сложная бизнес-логика
- Задействовано несколько repositories
- Логика переиспользуется между ViewModels
- Нужно четкое разделение обязанностей

**- Не использовать когда:**
- Простые вызовы repository
- Один к одному с repository
- Добавляет ненужный слой

**Краткое содержание**: UseCase инкапсулирует одну бизнес-операцию. Преимущества: переиспользуемая логика, тестируемость, разделение обязанностей. Реализация с `operator fun invoke()`. Использовать для: сложной логики, нескольких repositories. Не использовать для простых вызовов repository.

---

## References
- [Domain layer - Android](https://developer.android.com/topic/architecture/domain-layer)

## Related Questions
- [[q-clean-architecture-android--android--hard]]
