---
id: android-025
title: UseCase Pattern in Android / Паттерн UseCase в Android
aliases:
- UseCase Pattern in Android
- Паттерн UseCase в Android
topic: android
subtopics:
- architecture-clean
- architecture-mvvm
- di-hilt
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
sources: []
status: draft
moc: moc-android
related:
- c-clean-architecture
- c-repository-pattern
- c-usecase-pattern
created: 2025-10-06
updated: 2025-10-28
tags:
- android/architecture-clean
- android/architecture-mvvm
- android/di-hilt
- difficulty/medium
---

# Вопрос (RU)
> Что такое паттерн UseCase в Android? Когда и как его реализовать?

# Question (EN)
> What is the UseCase pattern in Android? When and how to implement it?

---

## Ответ (RU)

**UseCase** (или Interactor) — компонент domain-слоя, инкапсулирующий одну бизнес-операцию. Делает логику переиспользуемой, тестируемой и изолирует `ViewModel` от деталей repository.

### Базовая Реализация

```kotlin
// ✅ Простой UseCase для одного репозитория
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
                .onSuccess { user -> _uiState.value = UiState.Success(user) }
                .onFailure { error -> _uiState.value = UiState.Error(error.message) }
        }
    }
}
```

### Когда Использовать

**✅ Использовать:**
- Сложная бизнес-логика (валидация, трансформации, вычисления)
- Задействовано несколько repositories/data sources
- Логика переиспользуется между несколькими ViewModels
- Нужна изоляция и тестируемость бизнес-правил

**❌ НЕ использовать:**
- Простой вызов одного метода repository без логики
- Соотношение 1:1 с repository методом
- Добавляет ненужный слой абстракции

```kotlin
// ❌ BAD - Бесполезный UseCase без бизнес-логики
class GetProductsUseCase(private val repo: ProductRepository) {
    suspend operator fun invoke() = repo.getProducts() // Просто проксирует
}
// Лучше: вызвать repository напрямую из ViewModel

// ✅ GOOD - UseCase с реальной бизнес-логикой
class PurchaseProductUseCase(
    private val productRepo: ProductRepository,
    private val paymentRepo: PaymentRepository,
    private val analytics: Analytics
) {
    suspend operator fun invoke(productId: String): Result<Purchase> {
        val product = productRepo.getProduct(productId)
        val payment = paymentRepo.processPayment(product.price)
        analytics.logPurchase(productId, product.price)
        return Result.success(Purchase(product, payment))
    }
}
```

### UseCase С Реактивными Данными

```kotlin
// ✅ UseCase возвращающий Flow для реактивных обновлений
class ObserveCartItemsUseCase(
    private val cartRepo: CartRepository
) {
    operator fun invoke(): Flow<List<CartItem>> {
        return cartRepo.observeCart()
            .map { items -> items.filter { it.isAvailable } } // Фильтрация
    }
}

// Использование
val cartItems: StateFlow<List<CartItem>> = observeCartItemsUseCase()
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
```

**Краткое содержание**: UseCase инкапсулирует бизнес-операцию domain-слоя. Использовать для: сложной логики, нескольких data sources, переиспользования. НЕ использовать для простых вызовов repository. Реализация: `operator fun invoke()`, может возвращать `Flow` для реактивности.

## Answer (EN)

**UseCase** (or Interactor) is a domain layer component that encapsulates a single business operation. Makes logic reusable, testable, and isolates `ViewModel` from repository details.

### Basic Implementation

```kotlin
// ✅ Simple UseCase for single repository
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
                .onSuccess { user -> _uiState.value = UiState.Success(user) }
                .onFailure { error -> _uiState.value = UiState.Error(error.message) }
        }
    }
}
```

### When to Use

**✅ Use when:**
- Complex business logic (validation, transformations, calculations)
- Multiple repositories/data sources involved
- Logic reused across multiple ViewModels
- Need isolation and testability of business rules

**❌ Don't use when:**
- Simple single repository method call without logic
- One-to-one mapping to repository method
- Adds unnecessary abstraction layer

```kotlin
// ❌ BAD - Useless UseCase without business logic
class GetProductsUseCase(private val repo: ProductRepository) {
    suspend operator fun invoke() = repo.getProducts() // Just proxies
}
// Better: call repository directly from ViewModel

// ✅ GOOD - UseCase with real business logic
class PurchaseProductUseCase(
    private val productRepo: ProductRepository,
    private val paymentRepo: PaymentRepository,
    private val analytics: Analytics
) {
    suspend operator fun invoke(productId: String): Result<Purchase> {
        val product = productRepo.getProduct(productId)
        val payment = paymentRepo.processPayment(product.price)
        analytics.logPurchase(productId, product.price)
        return Result.success(Purchase(product, payment))
    }
}
```

### UseCase with Reactive Data

```kotlin
// ✅ UseCase returning Flow for reactive updates
class ObserveCartItemsUseCase(
    private val cartRepo: CartRepository
) {
    operator fun invoke(): Flow<List<CartItem>> {
        return cartRepo.observeCart()
            .map { items -> items.filter { it.isAvailable } } // Filtering
    }
}

// Usage
val cartItems: StateFlow<List<CartItem>> = observeCartItemsUseCase()
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
```

**Summary**: UseCase encapsulates domain layer business operation. Use for: complex logic, multiple data sources, reusability. Don't use for simple repository calls. Implementation: `operator fun invoke()`, can return `Flow` for reactivity.

---

## Follow-ups

1. How to test UseCases in isolation from repositories?
2. Should UseCases handle threading or rely on repositories?
3. How to handle multiple parameters in UseCases (data class vs varargs)?
4. When to use `suspend fun invoke()` vs `fun invoke(): `Flow`<T>`?
5. How do UseCases fit in multi-module architecture?

## References

- [Domain layer - Android](https://developer.android.com/topic/architecture/domain-layer)
- [Guide to app architecture - Android](https://developer.android.com/topic/architecture)

## Related Questions

### Prerequisites / Concepts

- [[c-clean-architecture]]
- [[c-repository-pattern]]
- [[c-usecase-pattern]]


### Prerequisites (Easier)
- [[q-repository-pattern--android--medium]] - `Repository` pattern basics

### Related (Same Level)
- [[q-viewmodel-livedata--android--medium]] - `ViewModel` basics
- [[q-kmm-dependency-injection--android--medium]] - DI fundamentals

### Advanced (Harder)
- [[q-clean-architecture-android--android--hard]] - Full Clean Architecture
- [[q-multi-module-best-practices--android--hard]] - Multi-module organization
