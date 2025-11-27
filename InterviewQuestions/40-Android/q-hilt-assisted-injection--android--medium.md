---
id: android-049
title: Hilt Assisted Injection
aliases: [Hilt Assisted Injection, Hilt Ассистированный инжект]
topic: android
subtopics:
  - architecture-mvvm
  - di-hilt
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-dagger
  - q-hilt-entry-points--android--medium
  - q-koin-vs-dagger-philosophy--android--hard
  - q-test-doubles-dependency-injection--android--medium
created: 2025-10-11
updated: 2025-11-10
tags: [android/architecture-mvvm, android/di-hilt, assisted-inject, dagger, dependency-injection, difficulty/medium, hilt]
sources:
  - "https://dagger.dev/hilt/assisted-injection.html"

date created: Saturday, November 1st 2025, 1:30:28 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---
# Вопрос (RU)
> Что такое Assisted Injection в Hilt/Dagger? Когда использовать `@AssistedInject` и `@AssistedFactory`?

# Question (EN)
> What is Assisted Injection in Hilt/Dagger? When and why would you use `@AssistedInject` and `@AssistedFactory`?

---

## Ответ (RU)

**Теория Assisted Injection:**
Assisted Injection позволяет смешивать зависимости, предоставляемые Dagger/Hilt, с runtime-параметрами, которые вы передаёте при создании экземпляра. Это полезно, когда нужно создавать объекты, которым одновременно требуются внедрённые зависимости (через DI-контейнер) и значения, известные только в момент вызова (например, ID, DTO, callback).

Важный момент: типы с `@AssistedInject` не могут быть напрямую внедрены Hilt/Dagger как обычные зависимости. Вместо этого вы внедряете сгенерированную `@AssistedFactory` и создаёте экземпляры через неё.

**Основные концепции:**
- Смешивает DI-зависимости с runtime-параметрами.
- Использует `@AssistedInject` для конструктора.
- Использует `@Assisted` для runtime-параметров (включая именованные варианты для устранения неоднозначности).
- Генерирует factory через `@AssistedFactory`, которую внедряют другие компоненты.
- Реализация factory автоматически генерируется Dagger/Hilt, что избавляет от ручной поддержки фабрик.

**Проблема без Assisted Injection:**
```kotlin
// Проблема: нельзя напрямую внедрить runtime-данные без явного биндинга
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val userId: String // ОШИБКА: Dagger не знает, как предоставить этот параметр!
)

// Вариант: ручная factory. Работает, но требует явной реализации
// и не использует автогенерацию и контракт Assisted Injection.
interface UserRepositoryFactory {
    fun create(userId: String): UserRepository
}

class UserRepositoryFactoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val database: Database
) : UserRepositoryFactory {
    override fun create(userId: String): UserRepository {
        return UserRepository(apiService, userId)
    }
}
```

**Решение с Assisted Injection:**
```kotlin
// Смешиваем внедрённые и runtime-зависимости
class UserRepository @AssistedInject constructor(
    // Зависимости, предоставляемые Dagger/Hilt
    private val apiService: ApiService,
    private val database: Database,
    // Runtime-параметр, предоставляемый вызывающей стороной
    @Assisted private val userId: String
) {
    suspend fun getUserData(): User {
        return apiService.getUser(userId)
    }

    suspend fun saveUser(user: User) {
        database.userDao().insert(user)
    }
}

// Factory автоматически генерируется Dagger/Hilt
@AssistedFactory
interface UserRepositoryFactory {
    fun create(userId: String): UserRepository
}

// Использование: внедряем factory, вызываем с runtime-данными
class UserViewModel @Inject constructor(
    private val userRepositoryFactory: UserRepositoryFactory,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val userId: String = savedStateHandle["userId"]!!

    // Создаём repository с внедрёнными и runtime-параметрами
    private val repository = userRepositoryFactory.create(userId)

    // В реальном коде это обычно оборачивается в LiveData/Flow, здесь упрощённый пример
    suspend fun loadUser(): User = repository.getUserData()
}
```

**Множественные @Assisted параметры:**
```kotlin
class OrderProcessor @AssistedInject constructor(
    // Внедрённые зависимости
    private val apiService: ApiService,
    private val paymentService: PaymentService,
    private val analytics: Analytics,
    // Runtime-параметры
    @Assisted private val orderId: String,
    @Assisted private val userId: String,
    @Assisted private val items: List<OrderItem>
) {
    suspend fun processOrder(): OrderResult {
        analytics.track("order_processing", mapOf("order_id" to orderId))

        val total = items.sumOf { it.price * it.quantity }
        val paymentResult = paymentService.charge(userId, total)
        val order = apiService.createOrder(orderId, userId, items)

        return OrderResult(order, paymentResult)
    }
}

@AssistedFactory
interface OrderProcessorFactory {
    fun create(orderId: String, userId: String, items: List<OrderItem>): OrderProcessor
}
```

**Именованные параметры для устранения неоднозначности:**
```kotlin
class TransferProcessor @AssistedInject constructor(
    private val apiService: ApiService,
    // Используем именованные @Assisted для различения параметров одного типа
    @Assisted("fromUserId") private val fromUserId: String,
    @Assisted("toUserId") private val toUserId: String,
    @Assisted("amount") private val amount: Double
) {
    suspend fun transfer() {
        apiService.transfer(fromUserId, toUserId, amount)
    }
}

@AssistedFactory
interface TransferProcessorFactory {
    // Имена в factory должны совпадать с именами в @Assisted
    fun create(
        @Assisted("fromUserId") fromUserId: String,
        @Assisted("toUserId") toUserId: String,
        @Assisted("amount") amount: Double
    ): TransferProcessor
}
```

**WorkManager интеграция (Hilt 2.31+):**
```kotlin
@HiltWorker
class DataSyncWorker @AssistedInject constructor(
    // При использовании Assisted Injection для Worker, Context и WorkerParameters
    // должны быть помечены @Assisted
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    // Внедрённые зависимости
    private val apiService: ApiService,
    private val database: AppDatabase,
    private val notificationManager: NotificationManager
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val syncType = inputData.getString("sync_type") ?: "full"

            notificationManager.showProgress("Синхронизация данных...")

            when (syncType) {
                "full" -> syncAll()
                "incremental" -> syncIncremental()
                else -> return Result.failure()
            }

            notificationManager.showSuccess("Синхронизация завершена")
            Result.success()
        } catch (e: Exception) {
            notificationManager.showError("Ошибка синхронизации: ${e.message}")
            Result.retry()
        }
    }

    private suspend fun syncAll() {
        val data = apiService.fetchAllData()
        database.dataDao().deleteAll()
        database.dataDao().insertAll(data)
    }

    private suspend fun syncIncremental() {
        val lastSyncTime = database.syncDao().getLastSyncTime()
        val data = apiService.fetchDataSince(lastSyncTime)
        database.dataDao().insertAll(data)
        database.syncDao().updateSyncTime(System.currentTimeMillis())
    }
}
```

Для полноты при реальной интеграции с WorkManager через Hilt необходимо использовать сгенерированный `HiltWorkerFactory` (Hilt конфигурирует его автоматически при подключении соответствующих зависимостей и аннотаций). В примере выше фокус сделан на Assisted-конструкторе worker-а.

**ViewHolder с зависимостями:**
```kotlin
class ProductViewHolder @AssistedInject constructor(
    // Внедрённые зависимости
    private val imageLoader: ImageLoader,
    private val analytics: Analytics,
    private val cartManager: CartManager,
    // Runtime-параметры
    @Assisted private val view: View,
    @Assisted private val onClickListener: (Product) -> Unit
) : RecyclerView.ViewHolder(view) {

    private val imageView: ImageView = view.findViewById(R.id.productImage)
    private val titleView: TextView = view.findViewById(R.id.productTitle)
    private val priceView: TextView = view.findViewById(R.id.productPrice)
    private val addToCartButton: Button = view.findViewById(R.id.addToCart)

    private var currentProduct: Product? = null

    init {
        addToCartButton.setOnClickListener {
            currentProduct?.let { product ->
                cartManager.addToCart(product)
                analytics.track("add_to_cart", mapOf("product_id" to product.id))
            }
        }

        view.setOnClickListener {
            currentProduct?.let { product ->
                analytics.track("product_clicked", mapOf("product_id" to product.id))
                onClickListener(product)
            }
        }
    }

    fun bind(product: Product) {
        currentProduct = product
        titleView.text = product.title
        priceView.text = "${'$'}${product.price}"
        imageLoader.load(product.imageUrl, imageView)
    }
}

@AssistedFactory
interface ProductViewHolderFactory {
    fun create(view: View, onClickListener: (Product) -> Unit): ProductViewHolder
}
```

## Answer (EN)

**Assisted Injection Theory:**
Assisted Injection allows mixing dependencies provided by Dagger/Hilt with runtime parameters that you pass when creating an instance. This is useful when you need to create objects that require both container-provided dependencies and values only known at call time (e.g., IDs, DTOs, callbacks).

Important: types with `@AssistedInject` cannot be directly injected by Hilt/Dagger like regular dependencies. Instead, you inject the generated `@AssistedFactory` and use it to create instances.

**Main concepts:**
- Mixes DI-managed dependencies with runtime parameters.
- Uses `@AssistedInject` on the constructor.
- Uses `@Assisted` for runtime parameters (including named variants for disambiguation).
- Declares a factory via `@AssistedFactory` which other components inject.
- The factory implementation is automatically generated by Dagger/Hilt, avoiding manual factory boilerplate.

**Problem without Assisted Injection:**
```kotlin
// Problem: cannot directly inject runtime data without an explicit binding
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val userId: String // ERROR: Dagger doesn't know how to provide this parameter!
)

// Option: manual factory. It works but requires a hand-written implementation
// and doesn't leverage Assisted Injection's generated factories.
interface UserRepositoryFactory {
    fun create(userId: String): UserRepository
}

class UserRepositoryFactoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val database: Database
) : UserRepositoryFactory {
    override fun create(userId: String): UserRepository {
        return UserRepository(apiService, userId)
    }
}
```

**Solution with Assisted Injection:**
```kotlin
// Mix injected and runtime dependencies
class UserRepository @AssistedInject constructor(
    // Dependencies provided by Dagger/Hilt
    private val apiService: ApiService,
    private val database: Database,
    // Runtime parameter provided by the caller
    @Assisted private val userId: String
) {
    suspend fun getUserData(): User {
        return apiService.getUser(userId)
    }

    suspend fun saveUser(user: User) {
        database.userDao().insert(user)
    }
}

// Factory is automatically generated by Dagger/Hilt
@AssistedFactory
interface UserRepositoryFactory {
    fun create(userId: String): UserRepository
}

// Usage: inject the factory and call it with runtime data
class UserViewModel @Inject constructor(
    private val userRepositoryFactory: UserRepositoryFactory,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val userId: String = savedStateHandle["userId"]!!

    // Create repository with both injected and runtime params
    private val repository = userRepositoryFactory.create(userId)

    // In real code you'd usually expose LiveData/Flow; simplified here
    suspend fun loadUser(): User = repository.getUserData()
}
```

**Multiple @Assisted parameters:**
```kotlin
class OrderProcessor @AssistedInject constructor(
    // Injected dependencies
    private val apiService: ApiService,
    private val paymentService: PaymentService,
    private val analytics: Analytics,
    // Runtime parameters
    @Assisted private val orderId: String,
    @Assisted private val userId: String,
    @Assisted private val items: List<OrderItem>
) {
    suspend fun processOrder(): OrderResult {
        analytics.track("order_processing", mapOf("order_id" to orderId))

        val total = items.sumOf { it.price * it.quantity }
        val paymentResult = paymentService.charge(userId, total)
        val order = apiService.createOrder(orderId, userId, items)

        return OrderResult(order, paymentResult)
    }
}

@AssistedFactory
interface OrderProcessorFactory {
    fun create(orderId: String, userId: String, items: List<OrderItem>): OrderProcessor
}
```

**Named parameters for disambiguation:**
```kotlin
class TransferProcessor @AssistedInject constructor(
    private val apiService: ApiService,
    // Use named @Assisted to distinguish same-type parameters
    @Assisted("fromUserId") private val fromUserId: String,
    @Assisted("toUserId") private val toUserId: String,
    @Assisted("amount") private val amount: Double
) {
    suspend fun transfer() {
        apiService.transfer(fromUserId, toUserId, amount)
    }
}

@AssistedFactory
interface TransferProcessorFactory {
    // Names in the factory must match the names in @Assisted
    fun create(
        @Assisted("fromUserId") fromUserId: String,
        @Assisted("toUserId") toUserId: String,
        @Assisted("amount") amount: Double
    ): TransferProcessor
}
```

**WorkManager integration (Hilt 2.31+):**
```kotlin
@HiltWorker
class DataSyncWorker @AssistedInject constructor(
    // When using Assisted Injection for a Worker, Context and WorkerParameters
    // must be annotated with @Assisted
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    // Injected dependencies
    private val apiService: ApiService,
    private val database: AppDatabase,
    private val notificationManager: NotificationManager
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val syncType = inputData.getString("sync_type") ?: "full"

            notificationManager.showProgress("Syncing data...")

            when (syncType) {
                "full" -> syncAll()
                "incremental" -> syncIncremental()
                else -> return Result.failure()
            }

            notificationManager.showSuccess("Sync completed")
            Result.success()
        } catch (e: Exception) {
            notificationManager.showError("Sync failed: ${e.message}")
            Result.retry()
        }
    }

    private suspend fun syncAll() {
        val data = apiService.fetchAllData()
        database.dataDao().deleteAll()
        database.dataDao().insertAll(data)
    }

    private suspend fun syncIncremental() {
        val lastSyncTime = database.syncDao().getLastSyncTime()
        val data = apiService.fetchDataSince(lastSyncTime)
        database.dataDao().insertAll(data)
        database.syncDao().updateSyncTime(System.currentTimeMillis())
    }
}
```

For full WorkManager integration in a real project, you rely on the generated `HiltWorkerFactory` (Hilt wires this when you add the appropriate dependencies and annotations). The example above focuses on the Assisted constructor pattern for the worker.

**ViewHolder with dependencies:**
```kotlin
class ProductViewHolder @AssistedInject constructor(
    // Injected dependencies
    private val imageLoader: ImageLoader,
    private val analytics: Analytics,
    private val cartManager: CartManager,
    // Runtime parameters
    @Assisted private val view: View,
    @Assisted private val onClickListener: (Product) -> Unit
) : RecyclerView.ViewHolder(view) {

    private val imageView: ImageView = view.findViewById(R.id.productImage)
    private val titleView: TextView = view.findViewById(R.id.productTitle)
    private val priceView: TextView = view.findViewById(R.id.productPrice)
    private val addToCartButton: Button = view.findViewById(R.id.addToCart)

    private var currentProduct: Product? = null

    init {
        addToCartButton.setOnClickListener {
            currentProduct?.let { product ->
                cartManager.addToCart(product)
                analytics.track("add_to_cart", mapOf("product_id" to product.id))
            }
        }

        view.setOnClickListener {
            currentProduct?.let { product ->
                analytics.track("product_clicked", mapOf("product_id" to product.id))
                onClickListener(product)
            }
        }
    }

    fun bind(product: Product) {
        currentProduct = product
        titleView.text = product.title
        priceView.text = "${'$'}${product.price}"
        imageLoader.load(product.imageUrl, imageView)
    }
}

@AssistedFactory
interface ProductViewHolderFactory {
    fun create(view: View, onClickListener: (Product) -> Unit): ProductViewHolder
}
```

---

## Дополнительные Вопросы (RU)

- Как Assisted Injection влияет на производительность по сравнению со стандартным внедрением?
- Какие стратегии тестирования Assisted Injection вы используете?
- В каких случаях следует избегать Assisted Injection?

## Follow-ups

- How does Assisted Injection affect performance compared to standard injection?
- What are the testing strategies for Assisted Injection?
- When should you avoid using Assisted Injection?

## Ссылки (RU)

- [Architecture](https://developer.android.com/topic/architecture)
- [Android Documentation](https://developer.android.com/docs)

## References

- [Architecture](https://developer.android.com/topic/architecture)
- [Android Documentation](https://developer.android.com/docs)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-dagger]]

### Предпосылки (проще)

### Похожие (того Же уровня)

- [[q-hilt-entry-points--android--medium]] - Entry Points
- [[q-kmm-dependency-injection--android--medium]] - DI паттерны

### Продвинутые (сложнее)

- [[q-dagger-multibinding--android--hard]] - Multibinding

## Related Questions

### Prerequisites / Concepts

- [[c-dagger]]

### Prerequisites (Easier)

### Related (Same Level)

- [[q-hilt-entry-points--android--medium]] - Entry Points
- [[q-kmm-dependency-injection--android--medium]] - DI patterns

### Advanced (Harder)

- [[q-dagger-multibinding--android--hard]] - Multibinding
