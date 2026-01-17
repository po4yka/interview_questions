---
id: android-025
title: UseCase Pattern in Android / Паттерн UseCase в Android
aliases: [UseCase Pattern in Android, Паттерн UseCase в Android]
topic: android
subtopics: [architecture-clean, architecture-mvvm, di-hilt]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
sources: []
status: draft
moc: moc-android
related: [c-clean-architecture, q-android-architectural-patterns--android--medium, q-android-lint-tool--android--medium, q-factory-pattern-android--android--medium, q-repository-pattern--android--medium]
created: 2025-10-06
updated: 2025-11-10
tags: [android/architecture-clean, android/architecture-mvvm, android/di-hilt, difficulty/medium]
anki_cards:
  - slug: android-025-0-en
    front: "What is the UseCase pattern in Android and when to use it?"
    back: |
      **UseCase** (Interactor) = domain layer component encapsulating one business operation.

      **When to use**:
      - Complex business logic (validation, transformations)
      - Multiple repositories/data sources
      - Reusable logic across ViewModels
      - Need isolation and testability

      ```kotlin
      class GetUserUseCase(private val repo: UserRepository) {
          suspend operator fun invoke(id: String) = repo.getUser(id)
      }
      ```

      **Avoid**: mechanical proxies without real logic.
    tags:
      - android_architecture
      - difficulty::medium
  - slug: android-025-0-ru
    front: "Что такое паттерн UseCase в Android и когда его использовать?"
    back: |
      **UseCase** (Interactor) = компонент domain-слоя, инкапсулирующий одну бизнес-операцию.

      **Когда использовать**:
      - Сложная бизнес-логика (валидация, трансформации)
      - Несколько репозиториев/источников данных
      - Переиспользуемая логика между ViewModel
      - Нужна изоляция и тестируемость

      ```kotlin
      class GetUserUseCase(private val repo: UserRepository) {
          suspend operator fun invoke(id: String) = repo.getUser(id)
      }
      ```

      **Избегать**: механических прокси без реальной логики.
    tags:
      - android_architecture
      - difficulty::medium

---
# Вопрос (RU)
> Что такое паттерн UseCase в Android? Когда и как его реализовать?

# Question (EN)
> What is the UseCase pattern in Android? When and how to implement it?

---

## Ответ (RU)

**UseCase** (или Interactor) — компонент domain-слоя, инкапсулирующий одну законченную бизнес-операцию или сценарий. Делает логику переиспользуемой, тестируемой и изолирует `ViewModel` от деталей repository и data sources.

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

**✅ Использовать (особенно оправдано), когда:**
- Есть сложная бизнес-логика (валидация, трансформации, вычисления)
- Задействовано несколько repositories/data sources
- Логика переиспользуется между несколькими ViewModels или модулями
- Нужна изоляция и тестируемость бизнес-правил
- Хотим стабильный контракт domain-слоя между UI и данными

**⚠️ Замечание:**
- Допустимы "тонкие" UseCase'ы, которые сейчас лишь делегируют один вызов repository, если они обеспечивают единообразный подход, помогают тестировать UI независимо от data layer и могут эволюционировать вместе с бизнес-логикой.

**❌ Избегать, если:**
- Вводится дополнительный слой только "ради паттерна", без пользы для читаемости, тестируемости или изоляции
- Для каждого метода репозитория механически создаётся UseCase без осмысленных границ или сценариев

```kotlin
// ❌ BAD - Бесполезный UseCase, добавленный механически без границ сценария
class GetProductsUseCase(private val repo: ProductRepository) {
    suspend operator fun invoke() = repo.getProducts() // Просто проксирует и не даёт дополнительных преимуществ
}
// В таком случае можно вызывать repository напрямую из ViewModel,
// либо осмысленно оформить это как часть конкретного сценария.

// ✅ GOOD - UseCase с реальной бизнес-логикой/сценарием
class PurchaseProductUseCase(
    private val productRepo: ProductRepository,
    private val paymentRepo: PaymentRepository,
    private val analytics: Analytics
) {
    suspend operator fun invoke(productId: String): Result<Purchase> {
        // Упрощённый пример: в реальном коде нужно обрабатывать ошибки
        val product = productRepo.getProduct(productId)
        val payment = paymentRepo.processPayment(product.price)
        analytics.logPurchase(productId, product.price)
        return Result.success(Purchase(product, payment))
    }
}
```

### UseCase С Реактивными Данными

```kotlin
// ✅ UseCase, возвращающий Flow для реактивных обновлений
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

**Краткое содержание**: UseCase инкапсулирует бизнес-операцию domain-слоя и служит стабильным контрактом между UI и бизнес-логикой. Использовать для: сложной логики, нескольких data sources, переиспользования и изоляции. Избегать бессмысленных слоёв без ценности. Реализация: `operator fun invoke()`, возможен `Flow` для реактивности.

## Answer (EN)

A **UseCase** (or Interactor) is a domain layer component that encapsulates a single cohesive business operation or scenario. It makes logic reusable, testable, and isolates the `ViewModel` from repository and data source details.

### Basic Implementation

```kotlin
// ✅ Simple UseCase for a single repository
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

**✅ Use (especially justified) when:**
- There is complex business logic (validation, transformations, calculations)
- Multiple repositories/data sources are involved
- Logic is reused across multiple ViewModels or modules
- You need isolation and testability of business rules
- You want a stable domain-layer contract between UI and data

**⚠️ Note:**
- "Thin" UseCases that currently delegate to a single repository call can be acceptable if they provide a consistent approach, allow UI to be tested independently of the data layer, and are expected to evolve with business rules.

**❌ Avoid when:**
- You add another layer only "for the sake of the pattern" without benefits for readability, testability, or isolation
- You mechanically create a UseCase per repository method without meaningful boundaries or scenarios

```kotlin
// ❌ BAD - Useless UseCase added mechanically without a clear scenario boundary
class GetProductsUseCase(private val repo: ProductRepository) {
    suspend operator fun invoke() = repo.getProducts() // Just proxies and adds no real value
}
// In such a case, you can call the repository directly from the ViewModel,
// or refactor this into a more meaningful scenario-specific UseCase.

// ✅ GOOD - UseCase with real business logic / scenario
class PurchaseProductUseCase(
    private val productRepo: ProductRepository,
    private val paymentRepo: PaymentRepository,
    private val analytics: Analytics
) {
    suspend operator fun invoke(productId: String): Result<Purchase> {
        // Simplified example: in real code, handle errors from product/payment operations
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

**Summary**: A UseCase encapsulates a domain-layer business operation and acts as a stable contract between UI and business logic. Use it for complex logic, multiple data sources, and reuse/isolated testing. Avoid meaningless layers without value. Implementation: `operator fun invoke()`, may return a `Flow` for reactive scenarios.

---

## Дополнительные Вопросы (RU)

1. Как тестировать UseCase в изоляции от репозиториев?
2. Должен ли UseCase управлять потоками выполнения или полагаться на репозитории?
3. Как обрабатывать несколько параметров в UseCase (data class vs отдельные аргументы)?
4. Когда использовать `suspend fun invoke()` против `fun invoke(): Flow<T>`?
5. Как UseCase вписывается в многомодульную архитектуру?

## Follow-ups

1. How to test UseCases in isolation from repositories?
2. Should UseCases handle threading or rely on repositories?
3. How to handle multiple parameters in UseCases (data class vs separate arguments)?
4. When to use `suspend fun invoke()` vs `fun invoke(): Flow<T>`?
5. How do UseCases fit in multi-module architecture?

## References

- [Domain layer - Android](https://developer.android.com/topic/architecture/domain-layer)
- [Guide to app architecture - Android](https://developer.android.com/topic/architecture)

## Related Questions

### Prerequisites / Concepts

- [[c-clean-architecture]]

### Prerequisites (Easier)
- [[q-repository-pattern--android--medium]] - Repository pattern basics

### Related (Same Level)
- [[q-kmm-dependency-injection--android--medium]] - DI fundamentals

### Advanced (Harder)
- [[q-clean-architecture-android--android--hard]] - Full Clean Architecture
- [[q-multi-module-best-practices--android--hard]] - Multi-module organization