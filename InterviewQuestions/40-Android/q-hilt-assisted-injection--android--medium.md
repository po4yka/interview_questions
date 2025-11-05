---
id: android-049
title: "Hilt Assisted Injection / Hilt Assisted Injection"
aliases: ["Hilt Assisted Injection"]
topic: android
subtopics: [architecture-mvvm, di-hilt]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-assisted-injection, q-hilt-entry-points--android--medium]
created: 2025-10-11
updated: 2025-10-31
tags: [android/architecture-mvvm, android/di-hilt, assisted-inject, dagger, dependency-injection, difficulty/medium, hilt]
sources: [https://dagger.dev/hilt/assisted-injection.html]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)
> Что такое Assisted Injection в Hilt/Dagger? Когда использовать `@AssistedInject` и `@AssistedFactory`?

# Question (EN)
> What is Assisted Injection in Hilt/Dagger? When and why would you use `@AssistedInject` and `@AssistedFactory`?

---

## Ответ (RU)

**Теория Assisted Injection:**
Assisted Injection позволяет смешивать зависимости, предоставляемые Dagger, с runtime-параметрами, которые вы предоставляете при создании экземпляра. Это полезно когда нужно создать объекты, требующие как внедрённые зависимости, так и пользовательские данные.

**Основные концепции:**
- Смешивает DI-зависимости с runtime-параметрами
- Использует `@AssistedInject` для конструктора
- Использует `@Assisted` для runtime-параметров
- Генерирует factory через `@AssistedFactory`
- Автоматически создаёт реализацию factory

**Проблема без Assisted Injection:**
```kotlin
// Проблема: нельзя внедрить runtime-данные
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val userId: String // ОШИБКА: Dagger не знает это!
)

// Проблема: ручная factory теряет DI преимущества
interface UserRepositoryFactory {
    fun create(userId: String): UserRepository
}

class UserRepositoryFactoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val database: Database
) : UserRepositoryFactory {
    override fun create(userId: String): UserRepository {
        return UserRepository(apiService, database, userId)
    }
}
```

**Решение с Assisted Injection:**
```kotlin
// Смешиваем внедрённые и runtime-зависимости
class UserRepository @AssistedInject constructor(
    // Зависимости, предоставляемые Dagger
    private val apiService: ApiService,
    private val database: Database,
    // Runtime-параметр, предоставляемый вами
    @Assisted private val userId: String
) {
    suspend fun getUserData(): User {
        return apiService.getUser(userId)
    }

    suspend fun saveUser(user: User) {
        database.userDao().insert(user)
    }
}

// Factory автоматически генерируется Dagger
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

    val userData = repository.getUserData()
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
    // Имена параметров в factory должны совпадать с именами @Assisted
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
    // Assisted-параметры от WorkManager
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
                else -> Result.failure()
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
        priceView.text = "$${product.price}"
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
Assisted Injection allows mixing dependencies provided by Dagger with runtime parameters that you provide when creating an instance. This is useful when you need to create objects that require both injected dependencies and user-provided data.

**Main concepts:**
- Mixes DI dependencies with runtime parameters
- Uses `@AssistedInject` for constructor
- Uses `@Assisted` for runtime parameters
- Generates factory through `@AssistedFactory`
- Automatically creates factory implementation

**Problem without Assisted Injection:**
```kotlin
// Problem: can't inject runtime data
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val userId: String // ERROR: Dagger doesn't know this!
)

// Problem: manual factory loses DI benefits
interface UserRepositoryFactory {
    fun create(userId: String): UserRepository
}

class UserRepositoryFactoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val database: Database
) : UserRepositoryFactory {
    override fun create(userId: String): UserRepository {
        return UserRepository(apiService, database, userId)
    }
}
```

**Solution with Assisted Injection:**
```kotlin
// Mix injected and runtime dependencies
class UserRepository @AssistedInject constructor(
    // Dependencies provided by Dagger
    private val apiService: ApiService,
    private val database: Database,
    // Runtime parameter provided by you
    @Assisted private val userId: String
) {
    suspend fun getUserData(): User {
        return apiService.getUser(userId)
    }

    suspend fun saveUser(user: User) {
        database.userDao().insert(user)
    }
}

// Factory is automatically generated by Dagger
@AssistedFactory
interface UserRepositoryFactory {
    fun create(userId: String): UserRepository
}

// Usage: inject factory, call with runtime data
class UserViewModel @Inject constructor(
    private val userRepositoryFactory: UserRepositoryFactory,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val userId: String = savedStateHandle["userId"]!!

    // Create repository with both injected and runtime params
    private val repository = userRepositoryFactory.create(userId)

    val userData = repository.getUserData()
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
    // Parameter names in factory must match @Assisted names
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
    // Assisted parameters from WorkManager
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
                else -> Result.failure()
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
        priceView.text = "$${product.price}"
        imageLoader.load(product.imageUrl, imageView)
    }
}

@AssistedFactory
interface ProductViewHolderFactory {
    fun create(view: View, onClickListener: (Product) -> Unit): ProductViewHolder
}
```

---

## Follow-ups

- How does Assisted Injection affect performance compared to standard injection?
- What are the testing strategies for Assisted Injection?
- When should you avoid using Assisted Injection?


## References

- [Architecture](https://developer.android.com/topic/architecture)
- [Android Documentation](https://developer.android.com/docs)


## Related Questions

### Prerequisites (Easier)

### Related (Same Level)
- [[q-hilt-entry-points--android--medium]] - Entry Points
- [[q-hilt-viewmodel-injection--android--medium]] - ViewModel injection
- [[q-kmm-dependency-injection--android--medium]] - DI patterns

### Advanced (Harder)
- [[q-dagger-multibinding--android--hard]] - Multibinding
- [[q-hilt-testing--android--hard]] - Hilt testing
