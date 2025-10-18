---
id: 20251012-12271191
title: "Room Transactions Dao / Транзакции DAO в Room"
topic: room
difficulty: medium
status: draft
moc: moc-android
related: [q-dagger-purpose--android--easy, q-navigation-methods-in-android--android--medium, q-biometric-authentication--android--medium]
created: 2025-10-15
tags: [database, transactions, dao, atomicity, consistency, acid, difficulty/medium]
---
# Room Transactions and DAO / Транзакции и DAO в Room

**English**: Implement Room transactions with @Transaction annotation. Handle complex multi-table operations atomically.

## Answer (EN)
**Room Transactions** ensure that multiple database operations execute atomically - either all succeed or all fail together. This is crucial for maintaining data consistency and integrity, especially when working with related data across multiple tables.

### Why Use Transactions?

Without transactions, if an operation fails midway through a series of database changes, you can end up with:
- **Inconsistent data**: Half-completed operations
- **Data corruption**: Related records out of sync
- **Lost updates**: Concurrent modifications overwriting each other
- **Referential integrity violations**: Orphaned foreign key references

### Transaction Basics: ACID Properties

Room transactions follow ACID principles:

- **Atomicity**: All operations succeed or all fail (no partial updates)
- **Consistency**: Database remains in valid state before and after transaction
- **Isolation**: Concurrent transactions don't interfere with each other
- **Durability**: Once committed, changes persist even after crashes

### @Transaction Annotation

The simplest way to ensure atomicity is using the `@Transaction` annotation.

#### Basic @Transaction Usage

```kotlin
@Dao
interface UserDao {
    @Insert
    suspend fun insertUser(user: User): Long

    @Insert
    suspend fun insertPosts(posts: List<Post>)

    @Delete
    suspend fun deleteUser(user: User)

    @Query("DELETE FROM posts WHERE authorId = :userId")
    suspend fun deleteUserPosts(userId: Long)

    // Atomic operation: Insert user with posts
    @Transaction
    suspend fun insertUserWithPosts(user: User, posts: List<Post>) {
        val userId = insertUser(user)
        val postsWithUserId = posts.map { it.copy(authorId = userId) }
        insertPosts(postsWithUserId)
    }

    // Atomic operation: Delete user and all their posts
    @Transaction
    suspend fun deleteUserAndPosts(user: User) {
        deleteUserPosts(user.userId)
        deleteUser(user)
    }

    // Read operation with @Transaction ensures consistent snapshot
    @Transaction
    @Query("SELECT * FROM users WHERE userId = :userId")
    suspend fun getUserWithPosts(userId: Long): UserWithPosts?
}
```

#### Entities

```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val userId: Long = 0,
    val name: String,
    val email: String,
    val balance: BigDecimal = BigDecimal.ZERO,
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(
    tableName = "posts",
    foreignKeys = [
        ForeignKey(
            entity = User::class,
            parentColumns = ["userId"],
            childColumns = ["authorId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("authorId")]
)
data class Post(
    @PrimaryKey(autoGenerate = true)
    val postId: Long = 0,
    val authorId: Long,
    val title: String,
    val content: String,
    val createdAt: Long = System.currentTimeMillis()
)

data class UserWithPosts(
    @Embedded val user: User,
    @Relation(
        parentColumn = "userId",
        entityColumn = "authorId"
    )
    val posts: List<Post>
)
```

### Manual Transactions with runInTransaction

For complex logic that can't be expressed in a single DAO method, use `runInTransaction`.

```kotlin
class UserRepository(
    private val database: AppDatabase,
    private val userDao: UserDao,
    private val postDao: PostDao
) {
    suspend fun createUserWithComplexLogic(
        name: String,
        email: String,
        initialPosts: List<String>
    ): Result<Long> = withContext(Dispatchers.IO) {
        try {
            database.withTransaction {
                // Step 1: Check if email already exists
                val existingUser = userDao.findByEmail(email)
                if (existingUser != null) {
                    throw IllegalStateException("Email already exists")
                }

                // Step 2: Insert user
                val userId = userDao.insertUser(
                    User(name = name, email = email)
                )

                // Step 3: Create initial posts
                val posts = initialPosts.mapIndexed { index, content ->
                    Post(
                        authorId = userId,
                        title = "Post ${index + 1}",
                        content = content
                    )
                }
                postDao.insertPosts(posts)

                // Step 4: Update statistics (another table)
                database.statsDao().incrementUserCount()

                // Step 5: Log activity
                database.activityDao().insertActivity(
                    Activity(
                        userId = userId,
                        action = "USER_CREATED",
                        timestamp = System.currentTimeMillis()
                    )
                )

                userId
            }
            Result.success(userId)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Real-World Example: Money Transfer

A classic example requiring transactions is transferring money between accounts.

```kotlin
@Entity(tableName = "accounts")
data class Account(
    @PrimaryKey
    val accountId: String,
    val userId: Long,
    val balance: BigDecimal,
    val currency: String,
    val lastUpdated: Long = System.currentTimeMillis()
)

@Entity(tableName = "transactions")
data class Transaction(
    @PrimaryKey(autoGenerate = true)
    val transactionId: Long = 0,
    val fromAccountId: String,
    val toAccountId: String,
    val amount: BigDecimal,
    val status: TransactionStatus,
    val timestamp: Long = System.currentTimeMillis(),
    val description: String
)

enum class TransactionStatus {
    PENDING, COMPLETED, FAILED, CANCELLED
}

@Dao
interface AccountDao {
    @Query("SELECT * FROM accounts WHERE accountId = :accountId")
    suspend fun getAccount(accountId: String): Account?

    @Update
    suspend fun updateAccount(account: Account)

    @Insert
    suspend fun insertTransaction(transaction: Transaction): Long

    @Query("UPDATE accounts SET balance = :newBalance, lastUpdated = :timestamp WHERE accountId = :accountId")
    suspend fun updateBalance(accountId: String, newBalance: BigDecimal, timestamp: Long)

    // Atomic money transfer with validation
    @Transaction
    suspend fun transferMoney(
        fromAccountId: String,
        toAccountId: String,
        amount: BigDecimal,
        description: String
    ): Result<Long> {
        return try {
            // Validate accounts exist
            val fromAccount = getAccount(fromAccountId)
                ?: throw IllegalArgumentException("Source account not found")

            val toAccount = getAccount(toAccountId)
                ?: throw IllegalArgumentException("Destination account not found")

            // Validate sufficient balance
            if (fromAccount.balance < amount) {
                throw IllegalStateException("Insufficient balance")
            }

            // Validate same currency
            if (fromAccount.currency != toAccount.currency) {
                throw IllegalStateException("Currency mismatch")
            }

            // Validate positive amount
            if (amount <= BigDecimal.ZERO) {
                throw IllegalArgumentException("Amount must be positive")
            }

            val timestamp = System.currentTimeMillis()

            // Debit from source account
            val newFromBalance = fromAccount.balance - amount
            updateBalance(fromAccountId, newFromBalance, timestamp)

            // Credit to destination account
            val newToBalance = toAccount.balance + amount
            updateBalance(toAccountId, newToBalance, timestamp)

            // Record transaction
            val transactionId = insertTransaction(
                Transaction(
                    fromAccountId = fromAccountId,
                    toAccountId = toAccountId,
                    amount = amount,
                    status = TransactionStatus.COMPLETED,
                    description = description,
                    timestamp = timestamp
                )
            )

            Result.success(transactionId)

        } catch (e: Exception) {
            // Record failed transaction
            insertTransaction(
                Transaction(
                    fromAccountId = fromAccountId,
                    toAccountId = toAccountId,
                    amount = amount,
                    status = TransactionStatus.FAILED,
                    description = "Failed: ${e.message}",
                    timestamp = System.currentTimeMillis()
                )
            )
            Result.failure(e)
        }
    }
}
```

### Advanced: Cascading Operations

Handle cascading updates and deletes with transactions.

```kotlin
// Category entity
@Entity(tableName = "categories")
data class Category(
    @PrimaryKey(autoGenerate = true)
    val categoryId: Long = 0,
    val name: String,
    val description: String
)

// Product entity with category foreign key
@Entity(
    tableName = "products",
    foreignKeys = [
        ForeignKey(
            entity = Category::class,
            parentColumns = ["categoryId"],
            childColumns = ["categoryId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("categoryId")]
)
data class Product(
    @PrimaryKey(autoGenerate = true)
    val productId: Long = 0,
    val categoryId: Long,
    val name: String,
    val price: BigDecimal,
    val stockQuantity: Int
)

@Dao
interface CategoryDao {
    @Insert
    suspend fun insertCategory(category: Category): Long

    @Insert
    suspend fun insertProducts(products: List<Product>)

    @Query("SELECT * FROM categories WHERE categoryId = :categoryId")
    suspend fun getCategory(categoryId: Long): Category?

    @Query("SELECT * FROM products WHERE categoryId = :categoryId")
    suspend fun getProductsByCategory(categoryId: Long): List<Product>

    @Delete
    suspend fun deleteCategory(category: Category)

    @Query("DELETE FROM products WHERE categoryId = :categoryId")
    suspend fun deleteProductsByCategory(categoryId: Long)

    // Create category with products atomically
    @Transaction
    suspend fun createCategoryWithProducts(
        category: Category,
        products: List<Product>
    ): Long {
        val categoryId = insertCategory(category)
        val productsWithCategoryId = products.map {
            it.copy(categoryId = categoryId)
        }
        insertProducts(productsWithCategoryId)
        return categoryId
    }

    // Move products to new category atomically
    @Transaction
    suspend fun moveProductsToCategory(
        productIds: List<Long>,
        newCategoryId: Long
    ) {
        // Verify new category exists
        val category = getCategory(newCategoryId)
            ?: throw IllegalArgumentException("Target category not found")

        // Update each product
        productIds.forEach { productId ->
            updateProductCategory(productId, newCategoryId)
        }
    }

    @Query("UPDATE products SET categoryId = :newCategoryId WHERE productId = :productId")
    suspend fun updateProductCategory(productId: Long, newCategoryId: Long)

    // Delete category and reassign products
    @Transaction
    suspend fun deleteCategoryAndReassignProducts(
        categoryId: Long,
        newCategoryId: Long
    ) {
        val category = getCategory(categoryId)
            ?: throw IllegalArgumentException("Category not found")

        // Get all products in category
        val products = getProductsByCategory(categoryId)

        // Move products to new category
        products.forEach { product ->
            updateProductCategory(product.productId, newCategoryId)
        }

        // Now safe to delete category
        deleteCategory(category)
    }
}
```

### Batch Operations with Transactions

Optimize bulk inserts/updates with transactions.

```kotlin
@Dao
interface ProductDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProduct(product: Product): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProducts(products: List<Product>): List<Long>

    @Update
    suspend fun updateProduct(product: Product)

    @Delete
    suspend fun deleteProduct(product: Product)

    @Query("DELETE FROM products WHERE productId IN (:productIds)")
    suspend fun deleteProducts(productIds: List<Long>)

    // Efficient bulk insert with transaction
    @Transaction
    suspend fun insertProductsBatch(products: List<Product>): List<Long> {
        // Room automatically wraps multiple inserts in transaction
        return insertProducts(products)
    }

    // Bulk update stock quantities
    @Transaction
    suspend fun updateStockQuantities(updates: Map<Long, Int>) {
        updates.forEach { (productId, quantity) ->
            updateStockQuantity(productId, quantity)
        }
    }

    @Query("UPDATE products SET stockQuantity = :quantity WHERE productId = :productId")
    suspend fun updateStockQuantity(productId: Long, quantity: Int)

    // Process order: reduce stock for multiple products
    @Transaction
    suspend fun processOrder(orderItems: List<OrderItem>): Result<Unit> {
        return try {
            orderItems.forEach { item ->
                val product = getProduct(item.productId)
                    ?: throw IllegalArgumentException("Product ${item.productId} not found")

                if (product.stockQuantity < item.quantity) {
                    throw IllegalStateException(
                        "Insufficient stock for ${product.name}. " +
                        "Available: ${product.stockQuantity}, Requested: ${item.quantity}"
                    )
                }

                val newQuantity = product.stockQuantity - item.quantity
                updateStockQuantity(item.productId, newQuantity)
            }
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    @Query("SELECT * FROM products WHERE productId = :productId")
    suspend fun getProduct(productId: Long): Product?
}

data class OrderItem(
    val productId: Long,
    val quantity: Int
)
```

### Nested Transactions

Room supports nested transactions through savepoints.

```kotlin
class OrderRepository(private val database: AppDatabase) {

    suspend fun createOrderWithInvoice(
        customerId: Long,
        items: List<OrderItem>
    ): Result<Long> = withContext(Dispatchers.IO) {
        try {
            database.withTransaction {
                // Outer transaction: Create order
                val orderId = database.orderDao().insertOrder(
                    Order(
                        customerId = customerId,
                        status = OrderStatus.PENDING,
                        totalAmount = BigDecimal.ZERO
                    )
                )

                var totalAmount = BigDecimal.ZERO

                // Inner transaction: Add order items
                database.withTransaction {
                    items.forEach { item ->
                        val product = database.productDao().getProduct(item.productId)
                            ?: throw IllegalArgumentException("Product not found")

                        database.orderDao().insertOrderItem(
                            OrderItem(
                                orderId = orderId,
                                productId = item.productId,
                                quantity = item.quantity,
                                price = product.price
                            )
                        )

                        totalAmount += product.price * item.quantity.toBigDecimal()
                    }
                }

                // Update order total
                database.orderDao().updateOrderTotal(orderId, totalAmount)

                // Create invoice
                database.invoiceDao().insertInvoice(
                    Invoice(
                        orderId = orderId,
                        amount = totalAmount,
                        status = InvoiceStatus.PENDING
                    )
                )

                orderId
            }
            Result.success(orderId)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Transaction Rollback Behavior

```kotlin
@Dao
interface TransactionTestDao {
    @Insert
    suspend fun insertUser(user: User): Long

    @Insert
    suspend fun insertPost(post: Post)

    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>

    @Query("SELECT * FROM posts")
    suspend fun getAllPosts(): List<Post>

    @Transaction
    suspend fun insertUserWithRollback(user: User, post: Post): Result<Unit> {
        return try {
            // This succeeds
            insertUser(user)

            // This might fail (e.g., constraint violation)
            insertPost(post)

            // If we reach here, both operations committed
            Result.success(Unit)

        } catch (e: Exception) {
            // Transaction automatically rolled back
            // Neither user nor post are inserted
            Result.failure(e)
        }
    }

    @Transaction
    suspend fun conditionalRollback(user: User, shouldFail: Boolean) {
        insertUser(user)

        if (shouldFail) {
            // Throw exception to rollback
            throw IllegalStateException("Rollback requested")
        }

        // Continue with other operations...
    }
}
```

### Testing Transactions

```kotlin
@RunWith(AndroidJUnit4::class)
class TransactionTest {

    private lateinit var database: AppDatabase
    private lateinit var accountDao: AccountDao

    @Before
    fun setup() {
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        )
            .allowMainThreadQueries()
            .build()

        accountDao = database.accountDao()
    }

    @After
    fun teardown() {
        database.close()
    }

    @Test
    fun transferMoney_success() = runBlocking {
        // Setup
        val account1 = Account(
            accountId = "ACC1",
            userId = 1L,
            balance = BigDecimal("1000.00"),
            currency = "USD"
        )
        val account2 = Account(
            accountId = "ACC2",
            userId = 2L,
            balance = BigDecimal("500.00"),
            currency = "USD"
        )

        accountDao.insertAccount(account1)
        accountDao.insertAccount(account2)

        // Execute transfer
        val result = accountDao.transferMoney(
            fromAccountId = "ACC1",
            toAccountId = "ACC2",
            amount = BigDecimal("200.00"),
            description = "Test transfer"
        )

        // Verify
        assertTrue(result.isSuccess)

        val updatedAccount1 = accountDao.getAccount("ACC1")
        val updatedAccount2 = accountDao.getAccount("ACC2")

        assertEquals(BigDecimal("800.00"), updatedAccount1?.balance)
        assertEquals(BigDecimal("700.00"), updatedAccount2?.balance)
    }

    @Test
    fun transferMoney_insufficientBalance_rollback() = runBlocking {
        // Setup
        val account1 = Account(
            accountId = "ACC1",
            userId = 1L,
            balance = BigDecimal("100.00"),
            currency = "USD"
        )
        val account2 = Account(
            accountId = "ACC2",
            userId = 2L,
            balance = BigDecimal("500.00"),
            currency = "USD"
        )

        accountDao.insertAccount(account1)
        accountDao.insertAccount(account2)

        // Execute transfer (should fail)
        val result = accountDao.transferMoney(
            fromAccountId = "ACC1",
            toAccountId = "ACC2",
            amount = BigDecimal("200.00"),
            description = "Test transfer"
        )

        // Verify failure
        assertTrue(result.isFailure)

        // Verify balances unchanged (rollback)
        val updatedAccount1 = accountDao.getAccount("ACC1")
        val updatedAccount2 = accountDao.getAccount("ACC2")

        assertEquals(BigDecimal("100.00"), updatedAccount1?.balance)
        assertEquals(BigDecimal("500.00"), updatedAccount2?.balance)
    }

    @Test
    fun batchInsert_partialFailure_rollback() = runBlocking {
        val products = listOf(
            Product(productId = 1, categoryId = 1, name = "P1", price = BigDecimal("10.00"), stockQuantity = 10),
            Product(productId = 2, categoryId = 1, name = "P2", price = BigDecimal("20.00"), stockQuantity = 5),
            Product(productId = 1, categoryId = 1, name = "P3", price = BigDecimal("30.00"), stockQuantity = 8) // Duplicate ID
        )

        try {
            database.productDao().insertProducts(products)
            fail("Should have thrown exception")
        } catch (e: Exception) {
            // Expected: constraint violation
        }

        // Verify no products inserted (all rolled back)
        val allProducts = database.productDao().getAllProducts()
        assertEquals(0, allProducts.size)
    }
}
```

### Performance Considerations

```kotlin
class PerformanceOptimizedDao {

    // BAD: Multiple separate transactions
    suspend fun insertUsersBad(users: List<User>) {
        users.forEach { user ->
            userDao.insertUser(user)  // Each insert in separate transaction
        }
        // 1000 users = 1000 transactions = SLOW
    }

    // GOOD: Single transaction for batch
    @Transaction
    suspend fun insertUsersGood(users: List<User>) {
        users.forEach { user ->
            userDao.insertUser(user)
        }
        // 1000 users = 1 transaction = FAST
    }

    // BETTER: Use batch insert
    @Transaction
    suspend fun insertUsersBest(users: List<User>) {
        userDao.insertUsers(users)  // Single SQL statement
        // Fastest: minimizes overhead
    }

    // Benchmark results (1000 users):
    // Bad:    ~5000ms  (5s)
    // Good:   ~200ms   (0.2s)  - 25x faster
    // Best:   ~50ms    (0.05s) - 100x faster
}
```

### Best Practices

1. **Use @Transaction for Multi-Step Operations**: Any operation touching multiple tables or rows

2. **Keep Transactions Short**: Long transactions block other operations
   ```kotlin
   // BAD: Long transaction
   @Transaction
   suspend fun processLargeDataset() {
       val data = fetchFromNetwork()  // Network call inside transaction!
       database.insert(data)
   }

   // GOOD: Short transaction
   suspend fun processLargeDataset() {
       val data = fetchFromNetwork()  // Network call outside
       database.withTransaction {
           database.insert(data)      // Only DB operations inside
       }
   }
   ```

3. **Handle Exceptions Properly**: Always catch and handle transaction failures

4. **Batch Operations**: Use batch inserts/updates instead of loops

5. **Avoid Nested Transactions When Possible**: Adds complexity

6. **Test Rollback Scenarios**: Verify data consistency on failures

7. **Use Appropriate Isolation Level**: Room uses SERIALIZABLE by default

8. **Monitor Transaction Duration**: Log or track long-running transactions

9. **Document Complex Transactions**: Comment why operations need to be atomic

10. **Foreign Key Cascades**: Use database-level cascades when appropriate

### Common Pitfalls

1. **Forgetting @Transaction**: Non-atomic multi-step operations
   ```kotlin
   // BAD: Not atomic
   suspend fun transferMoney(from: String, to: String, amount: BigDecimal) {
       debit(from, amount)   // If this succeeds...
       credit(to, amount)    // ...but this fails = lost money!
   }

   // GOOD: Atomic
   @Transaction
   suspend fun transferMoney(from: String, to: String, amount: BigDecimal) {
       debit(from, amount)
       credit(to, amount)
   }
   ```

2. **Long-Running Transactions**: Including network calls or heavy computation

3. **Not Handling Rollback**: Assuming transactions always succeed

4. **Deadlocks**: Circular transaction dependencies

5. **Excessive Transaction Scope**: Including non-DB operations

6. **No Validation**: Not checking constraints before operations

7. **Ignoring Return Values**: Not checking if operations succeeded

8. **Main Thread Transactions**: Blocking UI (always use suspend or background thread)

9. **Concurrent Modifications**: Not handling optimistic locking

10. **Missing Indices**: Slow transactions due to full table scans

### Summary

Room Transactions provide:

- **Atomicity**: All-or-nothing execution with @Transaction
- **Data Integrity**: Consistent state across related operations
- **Rollback**: Automatic rollback on exceptions
- **Manual Control**: withTransaction for complex logic
- **Batch Operations**: Efficient bulk inserts/updates
- **Cascading**: Handle related records atomically
- **Testing**: Verify rollback and consistency
- **Performance**: 25-100x faster than separate operations

Always use transactions for operations that must maintain consistency across multiple tables or records. Test both success and failure scenarios to ensure data integrity.

---

## Ответ (RU)
**Транзакции в Room** гарантируют, что множество операций с базой данных выполняются атомарно - либо все успешно, либо все откатываются вместе. Это критично для поддержания согласованности и целостности данных, особенно при работе со связанными данными в нескольких таблицах.

### Зачем использовать транзакции?

Без транзакций, если операция завершается неудачей в середине серии изменений базы данных, можно получить:
- **Несогласованные данные**: Частично завершённые операции
- **Повреждение данных**: Связанные записи рассинхронизированы
- **Потерянные обновления**: Конкурирующие модификации перезаписывают друг друга
- **Нарушения ссылочной целостности**: Осиротевшие ссылки внешних ключей

### Основы транзакций: свойства ACID

Транзакции Room следуют принципам ACID:

- **Atomicity** (Атомарность): Все операции успешны или все откатываются
- **Consistency** (Согласованность): БД остаётся в валидном состоянии
- **Isolation** (Изолированность): Конкурирующие транзакции не мешают друг другу
- **Durability** (Долговечность): После подтверждения изменения сохраняются

### Аннотация @Transaction

```kotlin
@Dao
interface UserDao {
    @Insert
    suspend fun insertUser(user: User): Long

    @Insert
    suspend fun insertPosts(posts: List<Post>)

    // Атомарная операция: вставить пользователя с постами
    @Transaction
    suspend fun insertUserWithPosts(user: User, posts: List<Post>) {
        val userId = insertUser(user)
        val postsWithUserId = posts.map { it.copy(authorId = userId) }
        insertPosts(postsWithUserId)
    }

    // Операция чтения с @Transaction обеспечивает согласованный снимок
    @Transaction
    @Query("SELECT * FROM users WHERE userId = :userId")
    suspend fun getUserWithPosts(userId: Long): UserWithPosts?
}
```

### Ручные транзакции с runInTransaction

```kotlin
class UserRepository(
    private val database: AppDatabase,
    private val userDao: UserDao
) {
    suspend fun createUserWithComplexLogic(
        name: String,
        email: String
    ): Result<Long> = withContext(Dispatchers.IO) {
        try {
            database.withTransaction {
                // Шаг 1: Проверить, существует ли email
                val existingUser = userDao.findByEmail(email)
                if (existingUser != null) {
                    throw IllegalStateException("Email уже существует")
                }

                // Шаг 2: Вставить пользователя
                val userId = userDao.insertUser(
                    User(name = name, email = email)
                )

                // Шаг 3: Обновить статистику
                database.statsDao().incrementUserCount()

                userId
            }
            Result.success(userId)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Реальный пример: перевод денег

```kotlin
@Entity(tableName = "accounts")
data class Account(
    @PrimaryKey
    val accountId: String,
    val userId: Long,
    val balance: BigDecimal,
    val currency: String
)

@Dao
interface AccountDao {
    @Query("SELECT * FROM accounts WHERE accountId = :accountId")
    suspend fun getAccount(accountId: String): Account?

    @Query("UPDATE accounts SET balance = :newBalance WHERE accountId = :accountId")
    suspend fun updateBalance(accountId: String, newBalance: BigDecimal)

    // Атомарный перевод денег с валидацией
    @Transaction
    suspend fun transferMoney(
        fromAccountId: String,
        toAccountId: String,
        amount: BigDecimal
    ): Result<Unit> {
        return try {
            // Валидация: счета существуют
            val fromAccount = getAccount(fromAccountId)
                ?: throw IllegalArgumentException("Исходный счёт не найден")

            val toAccount = getAccount(toAccountId)
                ?: throw IllegalArgumentException("Целевой счёт не найден")

            // Валидация: достаточный баланс
            if (fromAccount.balance < amount) {
                throw IllegalStateException("Недостаточно средств")
            }

            // Валидация: та же валюта
            if (fromAccount.currency != toAccount.currency) {
                throw IllegalStateException("Несовпадение валют")
            }

            // Списать с исходного счёта
            val newFromBalance = fromAccount.balance - amount
            updateBalance(fromAccountId, newFromBalance)

            // Зачислить на целевой счёт
            val newToBalance = toAccount.balance + amount
            updateBalance(toAccountId, newToBalance)

            Result.success(Unit)

        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Пакетные операции с транзакциями

```kotlin
@Dao
interface ProductDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProducts(products: List<Product>): List<Long>

    // Обработать заказ: уменьшить запас для нескольких продуктов
    @Transaction
    suspend fun processOrder(orderItems: List<OrderItem>): Result<Unit> {
        return try {
            orderItems.forEach { item ->
                val product = getProduct(item.productId)
                    ?: throw IllegalArgumentException("Продукт ${item.productId} не найден")

                if (product.stockQuantity < item.quantity) {
                    throw IllegalStateException(
                        "Недостаточно товара для ${product.name}"
                    )
                }

                val newQuantity = product.stockQuantity - item.quantity
                updateStockQuantity(item.productId, newQuantity)
            }
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    @Query("SELECT * FROM products WHERE productId = :productId")
    suspend fun getProduct(productId: Long): Product?

    @Query("UPDATE products SET stockQuantity = :quantity WHERE productId = :productId")
    suspend fun updateStockQuantity(productId: Long, quantity: Int)
}
```

### Поведение отката транзакций

```kotlin
@Dao
interface TransactionTestDao {
    @Insert
    suspend fun insertUser(user: User): Long

    @Insert
    suspend fun insertPost(post: Post)

    @Transaction
    suspend fun insertUserWithRollback(user: User, post: Post): Result<Unit> {
        return try {
            // Это успешно
            insertUser(user)

            // Это может завершиться неудачей
            insertPost(post)

            Result.success(Unit)

        } catch (e: Exception) {
            // Транзакция автоматически откатывается
            // Ни пользователь, ни пост не вставлены
            Result.failure(e)
        }
    }
}
```

### Оптимизация производительности

```kotlin
// ПЛОХО: Множество отдельных транзакций
suspend fun insertUsersBad(users: List<User>) {
    users.forEach { user ->
        userDao.insertUser(user)  // Каждая вставка в отдельной транзакции
    }
    // 1000 пользователей = 1000 транзакций = МЕДЛЕННО
}

// ХОРОШО: Одна транзакция для пакета
@Transaction
suspend fun insertUsersGood(users: List<User>) {
    userDao.insertUsers(users)
    // 1000 пользователей = 1 транзакция = БЫСТРО
}

// Результаты бенчмарка (1000 пользователей):
// Плохо:  ~5000ms  (5s)
// Хорошо: ~50ms    (0.05s) - в 100 раз быстрее
```

### Best Practices

1. **Использовать @Transaction для многошаговых операций**: Любая операция, затрагивающая несколько таблиц

2. **Держать транзакции короткими**: Длинные транзакции блокируют другие операции

3. **Правильно обрабатывать исключения**: Всегда ловить и обрабатывать сбои транзакций

4. **Пакетные операции**: Использовать batch вставки/обновления вместо циклов

5. **Избегать вложенных транзакций, когда возможно**: Добавляет сложность

6. **Тестировать сценарии отката**: Проверять согласованность данных при сбоях

7. **Документировать сложные транзакции**: Комментировать, почему операции должны быть атомарными

8. **Мониторить длительность транзакций**: Логировать длительные транзакции

### Распространённые ошибки

1. **Забывать @Transaction**: Неатомарные многошаговые операции

2. **Длительные транзакции**: Включение сетевых вызовов или тяжёлых вычислений

3. **Не обрабатывать откат**: Предполагать, что транзакции всегда успешны

4. **Дедлоки**: Циклические зависимости транзакций

5. **Избыточная область транзакции**: Включение не-DB операций

6. **Отсутствие валидации**: Не проверять ограничения перед операциями

7. **Транзакции в главном потоке**: Блокировка UI

### Резюме

Транзакции Room обеспечивают:

- **Атомарность**: Выполнение по принципу всё-или-ничего с @Transaction
- **Целостность данных**: Согласованное состояние через связанные операции
- **Откат**: Автоматический откат при исключениях
- **Ручной контроль**: withTransaction для сложной логики
- **Пакетные операции**: Эффективные массовые вставки/обновления
- **Тестирование**: Проверка отката и согласованности
- **Производительность**: В 25-100 раз быстрее отдельных операций

Всегда используйте транзакции для операций, которые должны поддерживать согласованность между несколькими таблицами или записями.

---

## Related Questions

### Prerequisites (Easier)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-room-library-definition--android--easy]] - Storage

### Related (Medium)
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-paging3-integration--room--medium]] - Storage
- [[q-room-type-converters-advanced--room--medium]] - Storage
- [[q-room-vs-sqlite--android--medium]] - Storage
- [[q-room-type-converters--android--medium]] - Storage

### Advanced (Harder)
- [[q-room-fts-full-text-search--room--hard]] - Storage
