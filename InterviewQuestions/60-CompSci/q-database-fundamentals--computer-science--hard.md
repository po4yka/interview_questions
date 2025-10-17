---
id: "20251013-600007"
title: "Database Fundamentals"
topic: databases
difficulty: hard
status: draft
created: "2025-10-13"
tags: ["database", "sql", "nosql", "acid", "transactions", "indexing", "normalization", "room", "sqlite", "android", "kotlin"]
description: "Comprehensive coverage of database concepts including SQL/NoSQL, ACID properties, transactions, indexing, normalization, and Android Room database with real-world Kotlin examples"
language: "en"
moc: moc-databases
related:   - "20251013-600005"  # Data Structures and Algorithms
  - "20251012-600004"  # OOP Principles
subcategory: "databases"
updated: "2025-10-13"
---
## Question

**English:**
Explain fundamental database concepts that every software engineer should know. Cover:

1. **SQL vs NoSQL:** When to use each, trade-offs
2. **ACID Properties:** Atomicity, Consistency, Isolation, Durability
3. **Transactions and Concurrency Control**
4. **Indexing and Query Optimization**
5. **Normalization (1NF, 2NF, 3NF) and Denormalization**
6. **Database Design Principles**
7. **Android Room Database** with practical examples
8. **CAP Theorem and eventual consistency**

Provide production Kotlin code with Android Room examples.

**Russian:**
Объясните фундаментальные концепции баз данных, которые должен знать каждый инженер. Охватите:

1. **SQL против NoSQL:** Когда использовать, компромиссы
2. **ACID свойства:** Атомарность, Согласованность, Изолированность, Долговечность
3. **Транзакции и управление конкурентностью**
4. **Индексирование и оптимизация запросов**
5. **Нормализация (1НФ, 2НФ, 3НФ) и Денормализация**
6. **Принципы проектирования БД**
7. **Android Room Database** с практическими примерами
8. **Теорема CAP и eventual consistency**

Предоставьте production Kotlin код с примерами Android Room.

---

## Answer

### 1. SQL vs NoSQL / SQL против NoSQL

**English:**
SQL databases are relational (tables, rows, columns) while NoSQL databases are non-relational (documents, key-value, graphs).

**Russian:**
SQL базы данных реляционные (таблицы, строки, столбцы), а NoSQL базы нереляционные (документы, ключ-значение, графы).

```kotlin
// SQL Database (Room - SQLite)
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "name") val name: String,
    @ColumnInfo(name = "email") val email: String,
    @ColumnInfo(name = "age") val age: Int
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE age > :minAge")
    suspend fun getUsersOlderThan(minAge: Int): List<User>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Query("UPDATE users SET email = :email WHERE id = :userId")
    suspend fun updateEmail(userId: String, email: String)

    @Delete
    suspend fun deleteUser(user: User)
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

// NoSQL Database (Firestore)
data class UserDocument(
    val id: String = "",
    val name: String = "",
    val email: String = "",
    val age: Int = 0,
    val metadata: Map<String, Any> = emptyMap()  // Flexible schema!
)

class FirestoreUserRepository {
    private val db = FirebaseFirestore.getInstance()
    private val usersCollection = db.collection("users")

    suspend fun getUser(userId: String): UserDocument? {
        return try {
            val doc = usersCollection.document(userId).get().await()
            doc.toObject(UserDocument::class.java)
        } catch (e: Exception) {
            null
        }
    }

    suspend fun saveUser(user: UserDocument) {
        usersCollection.document(user.id).set(user).await()
    }

    suspend fun getUsersOlderThan(minAge: Int): List<UserDocument> {
        return usersCollection
            .whereGreaterThan("age", minAge)
            .get()
            .await()
            .toObjects(UserDocument::class.java)
    }
}
```

**When to use SQL:**
```
✅ Complex queries with JOINs
✅ ACID transactions critical
✅ Fixed schema
✅ Data integrity important
✅ Relational data

Examples:
- Banking systems
- E-commerce orders
- User management with relationships
```

**When to use NoSQL:**
```
✅ Flexible schema needed
✅ Horizontal scaling required
✅ High write throughput
✅ Simple queries
✅ Denormalized data

Examples:
- Real-time chat
- IoT sensor data
- Product catalogs
- User sessions
```

**Comparison Table:**

| Feature | SQL | NoSQL |
|---------|-----|-------|
| Schema | Fixed | Flexible |
| Scaling | Vertical | Horizontal |
| Transactions | Full ACID | Eventually consistent |
| Queries | Complex JOINs | Simple lookups |
| Examples | PostgreSQL, MySQL | MongoDB, Firestore |

---

### 2. ACID Properties / ACID Свойства

**English:**
ACID ensures reliable database transactions.

**Russian:**
ACID обеспечивает надежные транзакции базы данных.

```kotlin
// ✅ ACID Properties in Room

@Database(entities = [Account::class, Transaction::class], version = 1)
abstract class BankDatabase : RoomDatabase() {
    abstract fun accountDao(): AccountDao
    abstract fun transactionDao(): TransactionDao
}

@Entity
data class Account(
    @PrimaryKey val id: String,
    val balance: Double
)

@Entity
data class Transaction(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val fromAccountId: String,
    val toAccountId: String,
    val amount: Double,
    val timestamp: Long = System.currentTimeMillis()
)

@Dao
interface AccountDao {
    @Query("SELECT * FROM Account WHERE id = :accountId")
    suspend fun getAccount(accountId: String): Account?

    @Update
    suspend fun updateAccount(account: Account)
}

@Dao
interface TransactionDao {
    @Insert
    suspend fun insertTransaction(transaction: Transaction)
}

// ATOMICITY: All or nothing
// Either both accounts are updated, or neither is
class BankRepository(private val database: BankDatabase) {

    suspend fun transfer(
        fromAccountId: String,
        toAccountId: String,
        amount: Double
    ): Result<Unit> {
        return try {
            // Transaction ensures atomicity
            database.withTransaction {
                val fromAccount = database.accountDao().getAccount(fromAccountId)
                    ?: throw Exception("From account not found")

                val toAccount = database.accountDao().getAccount(toAccountId)
                    ?: throw Exception("To account not found")

                // CONSISTENCY: Business rules enforced
                if (fromAccount.balance < amount) {
                    throw Exception("Insufficient funds")
                }

                // Update balances
                database.accountDao().updateAccount(
                    fromAccount.copy(balance = fromAccount.balance - amount)
                )

                database.accountDao().updateAccount(
                    toAccount.copy(balance = toAccount.balance + amount)
                )

                // Record transaction
                database.transactionDao().insertTransaction(
                    Transaction(
                        fromAccountId = fromAccountId,
                        toAccountId = toAccountId,
                        amount = amount
                    )
                )

                // If any step fails, entire transaction rolls back (ATOMICITY)
            }

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// ISOLATION: Transactions don't interfere
// Room uses SQLite's default isolation level (SERIALIZABLE)

@Dao
interface AccountDao {
    // ISOLATION: Read committed data only
    @Query("SELECT * FROM Account WHERE id = :accountId")
    suspend fun getAccount(accountId: String): Account?

    // DURABILITY: Once committed, changes persist
    @Update
    suspend fun updateAccount(account: Account)
}

// Example demonstrating ACID
class BankViewModel(private val repository: BankRepository) : ViewModel() {

    fun transferMoney(from: String, to: String, amount: Double) {
        viewModelScope.launch {
            repository.transfer(from, to, amount).fold(
                onSuccess = {
                    // ✅ DURABILITY: Changes persisted to disk
                    println("Transfer successful and durable")
                },
                onFailure = { error ->
                    // ❌ ATOMICITY: Transaction rolled back, no partial state
                    println("Transfer failed: ${error.message}")
                }
            )
        }
    }
}

// ACID Violations in Non-transactional code
class BadBankRepository(private val database: BankDatabase) {

    // ❌ NOT ATOMIC: Can fail halfway
    suspend fun transferBad(from: String, to: String, amount: Double) {
        val fromAccount = database.accountDao().getAccount(from)!!

        // Deduct from sender
        database.accountDao().updateAccount(
            fromAccount.copy(balance = fromAccount.balance - amount)
        )

        // ❌ If app crashes here, money disappears!

        val toAccount = database.accountDao().getAccount(to)!!

        // Add to receiver
        database.accountDao().updateAccount(
            toAccount.copy(balance = toAccount.balance + amount)
        )
    }
}
```

**ACID Summary:**
```
A - Atomicity:     All operations succeed or all fail (no partial updates)
C - Consistency:   Database moves from one valid state to another
I - Isolation:     Concurrent transactions don't interfere
D - Durability:    Committed changes survive crashes/power loss
```

---

### 3. Transactions and Concurrency / Транзакции и Конкурентность

**English:**
Transactions group multiple operations into a single atomic unit.

**Russian:**
Транзакции группируют несколько операций в одну атомарную единицу.

```kotlin
// ✅ Transaction Isolation Levels

// READ UNCOMMITTED: Dirty reads possible (not supported in SQLite)
// READ COMMITTED: No dirty reads (not supported in SQLite)
// REPEATABLE READ: No dirty/non-repeatable reads (not supported in SQLite)
// SERIALIZABLE: Full isolation (SQLite default)

@Database(entities = [Order::class, OrderItem::class], version = 1)
abstract class OrderDatabase : RoomDatabase() {
    abstract fun orderDao(): OrderDao
    abstract fun orderItemDao(): OrderItemDao
}

@Entity
data class Order(
    @PrimaryKey val id: String,
    val userId: String,
    val totalAmount: Double,
    val status: String,
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(
    foreignKeys = [
        ForeignKey(
            entity = Order::class,
            parentColumns = ["id"],
            childColumns = ["orderId"],
            onDelete = ForeignKey.CASCADE
        )
    ]
)
data class OrderItem(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val orderId: String,
    val productId: String,
    val quantity: Int,
    val price: Double
)

@Dao
interface OrderDao {
    @Insert
    suspend fun insertOrder(order: Order)

    @Query("SELECT * FROM `Order` WHERE id = :orderId")
    suspend fun getOrder(orderId: String): Order?

    @Query("UPDATE `Order` SET status = :status WHERE id = :orderId")
    suspend fun updateOrderStatus(orderId: String, status: String)
}

@Dao
interface OrderItemDao {
    @Insert
    suspend fun insertOrderItems(items: List<OrderItem>)

    @Query("SELECT * FROM OrderItem WHERE orderId = :orderId")
    suspend fun getOrderItems(orderId: String): List<OrderItem>
}

class OrderRepository(private val database: OrderDatabase) {

    // ✅ Transaction: Create order with items atomically
    suspend fun createOrder(
        orderId: String,
        userId: String,
        items: List<Pair<String, Int>>,  // (productId, quantity)
        priceMap: Map<String, Double>
    ): Result<Order> {
        return try {
            database.withTransaction {
                // Calculate total
                val totalAmount = items.sumOf { (productId, quantity) ->
                    (priceMap[productId] ?: 0.0) * quantity
                }

                // Create order
                val order = Order(
                    id = orderId,
                    userId = userId,
                    totalAmount = totalAmount,
                    status = "PENDING"
                )
                database.orderDao().insertOrder(order)

                // Create order items
                val orderItems = items.map { (productId, quantity) ->
                    OrderItem(
                        orderId = orderId,
                        productId = productId,
                        quantity = quantity,
                        price = priceMap[productId] ?: 0.0
                    )
                }
                database.orderItemDao().insertOrderItems(orderItems)

                // All succeed or all fail
                order
            }

            Result.success(
                database.orderDao().getOrder(orderId)!!
            )
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ✅ Concurrent transactions handled safely
    suspend fun processOrder(orderId: String) {
        database.withTransaction {
            val order = database.orderDao().getOrder(orderId)
                ?: throw Exception("Order not found")

            if (order.status != "PENDING") {
                throw Exception("Order already processed")
            }

            // Process payment (simulate)
            delay(1000)

            // Update status
            database.orderDao().updateOrderStatus(orderId, "COMPLETED")
        }
    }
}

// Concurrency Example: Multiple threads
class ConcurrencyDemo(private val repository: OrderRepository) {

    fun demonstrateConcurrency() = runBlocking {
        val orderId = UUID.randomUUID().toString()

        // Create order
        repository.createOrder(
            orderId = orderId,
            userId = "user123",
            items = listOf("product1" to 2, "product2" to 3),
            priceMap = mapOf("product1" to 10.0, "product2" to 15.0)
        )

        // Try to process same order concurrently
        val job1 = launch { repository.processOrder(orderId) }
        val job2 = launch { repository.processOrder(orderId) }

        job1.join()
        job2.join()

        // ✅ One succeeds, one fails (ISOLATION prevents double-processing)
    }
}

// Deadlock prevention
class DeadlockExample {
    // ❌ Bad: Can cause deadlock
    suspend fun badUpdate(db: OrderDatabase, id1: String, id2: String) {
        // Thread 1 locks id1, then id2
        // Thread 2 locks id2, then id1
        // DEADLOCK!
    }

    // ✅ Good: Lock in consistent order
    suspend fun goodUpdate(db: OrderDatabase, id1: String, id2: String) {
        val (first, second) = if (id1 < id2) id1 to id2 else id2 to id1

        db.withTransaction {
            // Always lock in same order
            db.orderDao().getOrder(first)
            db.orderDao().getOrder(second)
            // Update both
        }
    }
}
```

---

### 4. Indexing and Query Optimization / Индексирование и Оптимизация

**English:**
Indexes speed up data retrieval but slow down writes.

**Russian:**
Индексы ускоряют чтение данных, но замедляют запись.

```kotlin
// ✅ Indexing in Room

@Entity(
    tableName = "products",
    indices = [
        Index(value = ["category"]),                    // Single column index
        Index(value = ["name", "category"]),           // Composite index
        Index(value = ["price"], name = "idx_price"),  // Named index
        Index(value = ["sku"], unique = true)          // Unique index
    ]
)
data class Product(
    @PrimaryKey val id: String,
    val name: String,
    val category: String,
    val price: Double,
    val sku: String,
    val stock: Int,
    val createdAt: Long = System.currentTimeMillis()
)

@Dao
interface ProductDao {
    // ✅ Fast: Uses index on category
    @Query("SELECT * FROM products WHERE category = :category")
    suspend fun getProductsByCategory(category: String): List<Product>

    // ✅ Fast: Uses composite index (name, category)
    @Query("SELECT * FROM products WHERE name LIKE :name AND category = :category")
    suspend fun searchByNameAndCategory(name: String, category: String): List<Product>

    // ✅ Fast: Uses index on price
    @Query("SELECT * FROM products WHERE price BETWEEN :minPrice AND :maxPrice")
    suspend fun getProductsByPriceRange(minPrice: Double, maxPrice: Double): List<Product>

    // ❌ Slow: No index on stock (full table scan)
    @Query("SELECT * FROM products WHERE stock < :threshold")
    suspend fun getLowStockProducts(threshold: Int): List<Product>

    // ✅ Fast: Uses unique index on sku
    @Query("SELECT * FROM products WHERE sku = :sku")
    suspend fun getProductBySku(sku: String): Product?
}

// Query Optimization Examples

@Entity(
    indices = [
        Index(value = ["userId", "status"]),  // Composite for common query
        Index(value = ["createdAt"])          // For date range queries
    ]
)
data class Task(
    @PrimaryKey val id: String,
    val userId: String,
    val title: String,
    val status: String,
    val createdAt: Long
)

@Dao
interface TaskDao {
    // ✅ Optimized: Uses composite index
    @Query("""
        SELECT * FROM Task
        WHERE userId = :userId AND status = :status
        ORDER BY createdAt DESC
    """)
    suspend fun getUserTasksByStatus(userId: String, status: String): List<Task>

    // ❌ Not optimized: Index not used efficiently
    @Query("""
        SELECT * FROM Task
        WHERE status = :status AND userId = :userId
        ORDER BY createdAt DESC
    """)
    suspend fun getTasksWrongOrder(userId: String, status: String): List<Task>
    // Note: Index (userId, status) won't be fully utilized if status is first in WHERE

    // ✅ Optimized: Covering index (all columns in index)
    @Query("SELECT userId, status FROM Task WHERE userId = :userId")
    suspend fun getUserTaskStatusOnly(userId: String): List<TaskStatus>

    // ✅ Pagination for large results
    @Query("""
        SELECT * FROM Task
        WHERE userId = :userId
        ORDER BY createdAt DESC
        LIMIT :limit OFFSET :offset
    """)
    suspend fun getUserTasksPaged(userId: String, limit: Int, offset: Int): List<Task>
}

data class TaskStatus(val userId: String, val status: String)

// Index Trade-offs
class IndexingDemo {
    /*
    ✅ Benefits:
    - Faster SELECT queries
    - Faster WHERE, ORDER BY, JOIN operations
    - Unique constraints

    ❌ Drawbacks:
    - Slower INSERT/UPDATE/DELETE
    - Additional storage space
    - Index maintenance overhead

    Best Practices:
    1. Index columns used in WHERE clauses
    2. Index foreign keys
    3. Composite index order matters (most selective first)
    4. Don't over-index (each index has cost)
    5. Analyze query patterns before indexing
    */
}

// Full-Text Search (FTS)
@Entity
@Fts4(contentEntity = Product::class)
data class ProductFts(
    val name: String,
    val description: String
)

@Dao
interface ProductFtsDao {
    @Query("SELECT * FROM ProductFts WHERE ProductFts MATCH :query")
    suspend fun searchProducts(query: String): List<ProductFts>
}

// Usage: Fast text search
// repository.searchProducts("wireless keyboard")
```

**Index Performance:**

| Operation | Without Index | With Index |
|-----------|---------------|------------|
| SELECT (1M rows) | O(n) | O(log n) |
| INSERT | O(1) | O(log n) |
| UPDATE | O(n) | O(log n) |
| DELETE | O(n) | O(log n) |

---

### 5. Normalization and Denormalization / Нормализация и Денормализация

**English:**
Normalization reduces redundancy, denormalization improves read performance.

**Russian:**
Нормализация уменьшает избыточность, денормализация улучшает производительность чтения.

```kotlin
// ❌ Unnormalized (0NF): Data redundancy
data class OrderUnnormalized(
    val orderId: String,
    val customerName: String,
    val customerEmail: String,
    val customerPhone: String,
    val productName: String,
    val productPrice: Double,
    val quantity: Int
)
// Problem: Customer data repeated for each order item

// ✅ First Normal Form (1NF): Atomic values, no repeating groups
@Entity
data class Order1NF(
    @PrimaryKey val orderId: String,
    val customerId: String,
    val productId: String,
    val quantity: Int
)
// ✅ No repeating groups, atomic values

// ✅ Second Normal Form (2NF): 1NF + No partial dependencies
@Entity
data class Customer(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    val phone: String
)

@Entity
data class Product(
    @PrimaryKey val id: String,
    val name: String,
    val price: Double
)

@Entity(
    foreignKeys = [
        ForeignKey(entity = Customer::class, parentColumns = ["id"], childColumns = ["customerId"]),
        ForeignKey(entity = Product::class, parentColumns = ["id"], childColumns = ["productId"])
    ]
)
data class Order2NF(
    @PrimaryKey val id: String,
    val customerId: String,
    val productId: String,
    val quantity: Int
)
// ✅ No partial dependencies on composite key

// ✅ Third Normal Form (3NF): 2NF + No transitive dependencies
@Entity
data class City(
    @PrimaryKey val id: String,
    val name: String,
    val countryId: String
)

@Entity
data class Country(
    @PrimaryKey val id: String,
    val name: String
)

@Entity(
    foreignKeys = [
        ForeignKey(entity = City::class, parentColumns = ["id"], childColumns = ["cityId"])
    ]
)
data class Customer3NF(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    val cityId: String  // No countryId here (transitive dependency removed)
)
// ✅ No transitive dependencies (city -> country)

// Normalized Database (3NF)
@Database(
    entities = [Customer::class, Product::class, Order::class, OrderItem::class],
    version = 1
)
abstract class NormalizedDatabase : RoomDatabase() {
    abstract fun customerDao(): CustomerDao
    abstract fun productDao(): ProductDao
    abstract fun orderDao(): OrderDao
    abstract fun orderItemDao(): OrderItemDao
}

@Entity
data class OrderItem(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val orderId: String,
    val productId: String,
    val quantity: Int
)

// ✅ Normalized: No redundancy, easy updates
data class OrderWithDetails(
    @Embedded val order: Order,
    @Relation(
        parentColumn = "customerId",
        entityColumn = "id"
    )
    val customer: Customer,
    @Relation(
        entity = OrderItem::class,
        parentColumn = "id",
        entityColumn = "orderId"
    )
    val items: List<OrderItemWithProduct>
)

data class OrderItemWithProduct(
    @Embedded val orderItem: OrderItem,
    @Relation(
        parentColumn = "productId",
        entityColumn = "id"
    )
    val product: Product
)

@Dao
interface OrderDao {
    @Transaction
    @Query("SELECT * FROM `Order` WHERE id = :orderId")
    suspend fun getOrderWithDetails(orderId: String): OrderWithDetails
}

// ❌ Denormalized: Optimized for reads
@Entity
data class OrderDenormalized(
    @PrimaryKey val orderId: String,
    // Customer data duplicated
    val customerId: String,
    val customerName: String,
    val customerEmail: String,
    // Product data duplicated
    val productId: String,
    val productName: String,
    val productPrice: Double,
    val quantity: Int,
    val totalPrice: Double  // Calculated field
)

// ✅ Denormalized benefits:
// - Single query for all data
// - No JOINs needed
// - Faster reads

// ❌ Denormalized drawbacks:
// - Data redundancy
// - Update anomalies
// - More storage

@Dao
interface OrderDenormalizedDao {
    // ✅ Fast: No joins
    @Query("SELECT * FROM OrderDenormalized WHERE customerId = :customerId")
    suspend fun getCustomerOrders(customerId: String): List<OrderDenormalized>

    // ❌ Must update multiple rows when product price changes
    @Query("UPDATE OrderDenormalized SET productPrice = :newPrice WHERE productId = :productId")
    suspend fun updateProductPrice(productId: String, newPrice: Double)
}

// When to Denormalize:
class DenormalizationGuide {
    /*
    ✅ Denormalize when:
    - Read-heavy workload
    - Complex JOINs are slow
    - Caching calculated values
    - Reporting/analytics tables
    - Mobile apps (reduce queries)

    ❌ Keep normalized when:
    - Write-heavy workload
    - Data consistency critical
    - Storage is limited
    - Frequent updates to shared data
    */
}

// Real Android example: Message with user info (denormalized)
@Entity
data class MessageDenormalized(
    @PrimaryKey val id: String,
    val chatId: String,
    val content: String,
    // Denormalized user data for fast display
    val senderId: String,
    val senderName: String,
    val senderAvatarUrl: String,
    val timestamp: Long
)

// Single query to display messages - no joins needed!
@Dao
interface MessageDao {
    @Query("SELECT * FROM MessageDenormalized WHERE chatId = :chatId ORDER BY timestamp DESC")
    fun getMessages(chatId: String): Flow<List<MessageDenormalized>>
}
```

---

### 6. Database Design Principles / Принципы Проектирования БД

```kotlin
// ✅ Foreign Keys and Relationships

@Entity(tableName = "authors")
data class Author(
    @PrimaryKey val id: String,
    val name: String,
    val bio: String
)

@Entity(
    tableName = "books",
    foreignKeys = [
        ForeignKey(
            entity = Author::class,
            parentColumns = ["id"],
            childColumns = ["authorId"],
            onDelete = ForeignKey.CASCADE,  // Delete books when author deleted
            onUpdate = ForeignKey.CASCADE   // Update books when author ID changes
        )
    ],
    indices = [Index(value = ["authorId"])]  // Index foreign key!
)
data class Book(
    @PrimaryKey val id: String,
    val title: String,
    val authorId: String,
    val publishedYear: Int
)

// One-to-Many Relationship
data class AuthorWithBooks(
    @Embedded val author: Author,
    @Relation(
        parentColumn = "id",
        entityColumn = "authorId"
    )
    val books: List<Book>
)

@Dao
interface AuthorDao {
    @Transaction
    @Query("SELECT * FROM authors WHERE id = :authorId")
    suspend fun getAuthorWithBooks(authorId: String): AuthorWithBooks
}

// Many-to-Many Relationship
@Entity
data class Student(
    @PrimaryKey val id: String,
    val name: String
)

@Entity
data class Course(
    @PrimaryKey val id: String,
    val name: String
)

@Entity(
    primaryKeys = ["studentId", "courseId"],
    foreignKeys = [
        ForeignKey(entity = Student::class, parentColumns = ["id"], childColumns = ["studentId"]),
        ForeignKey(entity = Course::class, parentColumns = ["id"], childColumns = ["courseId"])
    ]
)
data class StudentCourseCrossRef(
    val studentId: String,
    val courseId: String,
    val enrollmentDate: Long = System.currentTimeMillis()
)

data class StudentWithCourses(
    @Embedded val student: Student,
    @Relation(
        parentColumn = "id",
        entityColumn = "id",
        associateBy = Junction(
            StudentCourseCrossRef::class,
            parentColumn = "studentId",
            entityColumn = "courseId"
        )
    )
    val courses: List<Course>
)

@Dao
interface StudentDao {
    @Transaction
    @Query("SELECT * FROM Student WHERE id = :studentId")
    suspend fun getStudentWithCourses(studentId: String): StudentWithCourses

    @Insert
    suspend fun enrollStudent(enrollment: StudentCourseCrossRef)
}

// Database Constraints
@Entity(
    tableName = "products",
    indices = [
        Index(value = ["sku"], unique = true)  // Unique constraint
    ]
)
data class ProductWithConstraints(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "name") val name: String,
    @ColumnInfo(name = "sku") val sku: String,
    @ColumnInfo(name = "price") val price: Double,
    // Check constraint (not directly supported, use validation in code)
    @ColumnInfo(name = "stock") val stock: Int
) {
    init {
        require(price > 0) { "Price must be positive" }
        require(stock >= 0) { "Stock cannot be negative" }
    }
}

// Soft Delete Pattern
@Entity
data class Task(
    @PrimaryKey val id: String,
    val title: String,
    val completed: Boolean = false,
    val deletedAt: Long? = null  // Null = not deleted
)

@Dao
interface TaskDao {
    // Only get non-deleted tasks
    @Query("SELECT * FROM Task WHERE deletedAt IS NULL")
    suspend fun getActiveTasks(): List<Task>

    // Soft delete
    @Query("UPDATE Task SET deletedAt = :timestamp WHERE id = :taskId")
    suspend fun softDelete(taskId: String, timestamp: Long = System.currentTimeMillis())

    // Restore
    @Query("UPDATE Task SET deletedAt = NULL WHERE id = :taskId")
    suspend fun restore(taskId: String)

    // Permanently delete old items
    @Query("DELETE FROM Task WHERE deletedAt < :cutoffTime")
    suspend fun permanentlyDeleteOld(cutoffTime: Long)
}

// Audit Trail Pattern
@Entity
data class AuditLog(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val entityType: String,
    val entityId: String,
    val action: String,  // CREATE, UPDATE, DELETE
    val userId: String,
    val oldValue: String?,
    val newValue: String?,
    val timestamp: Long = System.currentTimeMillis()
)

class AuditableRepository(
    private val database: AppDatabase,
    private val currentUserId: String
) {
    suspend fun updateProduct(product: Product) {
        database.withTransaction {
            val old = database.productDao().getProduct(product.id)

            database.productDao().updateProduct(product)

            database.auditLogDao().insert(
                AuditLog(
                    entityType = "Product",
                    entityId = product.id,
                    action = "UPDATE",
                    userId = currentUserId,
                    oldValue = old.toString(),
                    newValue = product.toString()
                )
            )
        }
    }
}
```

---

### 7. Android Room Database / Android Room База Данных

```kotlin
// ✅ Complete Room Setup

// 1. Entities
@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    @ColumnInfo(name = "created_at") val createdAt: Long = System.currentTimeMillis()
)

// 2. DAOs
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>  // Flow for reactive updates

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: String): User?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)

    @Query("DELETE FROM users WHERE id = :userId")
    suspend fun deleteUserById(userId: String)
}

// 3. Database
@Database(
    entities = [User::class],
    version = 1,
    exportSchema = true
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                )
                    .fallbackToDestructiveMigration()  // Dev only!
                    .build()

                INSTANCE = instance
                instance
            }
        }
    }
}

// 4. Repository
class UserRepository(private val userDao: UserDao) {

    val allUsers: Flow<List<User>> = userDao.getAllUsers()

    suspend fun getUser(userId: String): User? {
        return userDao.getUser(userId)
    }

    suspend fun insertUser(user: User) {
        userDao.insertUser(user)
    }

    suspend fun updateUser(user: User) {
        userDao.updateUser(user)
    }

    suspend fun deleteUser(user: User) {
        userDao.deleteUser(user)
    }
}

// 5. ViewModel
class UserViewModel(private val repository: UserRepository) : ViewModel() {

    val allUsers: Flow<List<User>> = repository.allUsers

    fun insertUser(user: User) = viewModelScope.launch {
        repository.insertUser(user)
    }

    fun updateUser(user: User) = viewModelScope.launch {
        repository.updateUser(user)
    }

    fun deleteUser(user: User) = viewModelScope.launch {
        repository.deleteUser(user)
    }
}

// 6. Compose UI
@Composable
fun UserListScreen(viewModel: UserViewModel) {
    val users by viewModel.allUsers.collectAsState(initial = emptyList())

    LazyColumn {
        items(users) { user ->
            UserItem(
                user = user,
                onDelete = { viewModel.deleteUser(user) }
            )
        }
    }
}

// Database Migration
@Database(
    entities = [User::class],
    version = 2,  // Incremented version
    exportSchema = true
)
abstract class AppDatabaseV2 : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        // Migration from version 1 to 2
        val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(database: SupportSQLiteDatabase) {
                // Add new column
                database.execSQL("ALTER TABLE users ADD COLUMN age INTEGER NOT NULL DEFAULT 0")
            }
        }

        fun getDatabase(context: Context): AppDatabaseV2 {
            return Room.databaseBuilder(
                context.applicationContext,
                AppDatabaseV2::class.java,
                "app_database"
            )
                .addMigrations(MIGRATION_1_2)
                .build()
        }
    }
}

// Type Converters
class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? {
        return value?.let { Date(it) }
    }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? {
        return date?.time
    }

    @TypeConverter
    fun fromStringList(value: String?): List<String>? {
        return value?.split(",")
    }

    @TypeConverter
    fun toStringList(list: List<String>?): String? {
        return list?.joinToString(",")
    }
}

@Database(
    entities = [Task::class],
    version = 1
)
@TypeConverters(Converters::class)
abstract class TaskDatabase : RoomDatabase() {
    abstract fun taskDao(): TaskDao
}

@Entity
data class Task(
    @PrimaryKey val id: String,
    val title: String,
    val dueDate: Date,  // Type converter handles Date
    val tags: List<String>  // Type converter handles List<String>
)
```

---

### 8. CAP Theorem and Consistency / Теорема CAP и Согласованность

**English:**
CAP Theorem: You can only have 2 of 3 - Consistency, Availability, Partition Tolerance.

**Russian:**
Теорема CAP: Можно иметь только 2 из 3 - Согласованность, Доступность, Устойчивость к разделению.

```kotlin
// CAP Theorem Trade-offs

/*
C - Consistency:   All nodes see same data at same time
A - Availability:  Every request receives a response
P - Partition Tolerance: System continues despite network partitions

You must choose 2:
- CP: Consistency + Partition Tolerance (sacrifice Availability)
- AP: Availability + Partition Tolerance (sacrifice Consistency)
- CA: Consistency + Availability (sacrifice Partition Tolerance - not realistic for distributed systems)
*/

// ✅ Strong Consistency (CP System)
// Example: Banking system
class BankingRepository(private val database: AppDatabase) {

    suspend fun transfer(from: String, to: String, amount: Double): Result<Unit> {
        return try {
            database.withTransaction {
                // Strong consistency: Either both accounts updated or neither
                val fromAccount = database.accountDao().getAccount(from)
                    ?: throw Exception("Account not found")

                if (fromAccount.balance < amount) {
                    throw Exception("Insufficient funds")
                }

                // ACID guarantees consistency
                database.accountDao().updateBalance(from, fromAccount.balance - amount)
                database.accountDao().updateBalance(to, amount)
            }

            Result.success(Unit)
        } catch (e: Exception) {
            // If network partition occurs, operation fails (sacrifices Availability)
            Result.failure(e)
        }
    }
}

// ✅ Eventual Consistency (AP System)
// Example: Social media likes
class LikeRepository(
    private val localDatabase: AppDatabase,
    private val remoteApi: ApiService
) {

    suspend fun likePost(postId: String, userId: String) {
        // Save locally first (Availability)
        localDatabase.likeDao().insertLike(
            Like(postId = postId, userId = userId, synced = false)
        )

        try {
            // Sync to server
            remoteApi.likePost(postId, userId)
            localDatabase.likeDao().markSynced(postId, userId)
        } catch (e: Exception) {
            // Keep local state, sync later (Eventual consistency)
            // User sees like immediately even if network fails
        }
    }

    suspend fun syncPendingLikes() {
        val pending = localDatabase.likeDao().getPendingLikes()

        pending.forEach { like ->
            try {
                remoteApi.likePost(like.postId, like.userId)
                localDatabase.likeDao().markSynced(like.postId, like.userId)
            } catch (e: Exception) {
                // Will retry later
            }
        }
    }
}

@Entity
data class Like(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val postId: String,
    val userId: String,
    val synced: Boolean = false,
    val timestamp: Long = System.currentTimeMillis()
)

// Conflict Resolution for Eventual Consistency
sealed class ConflictResolution<T> {
    data class LastWriteWins<T>(val latest: T) : ConflictResolution<T>()
    data class MergeValues<T>(val merged: T) : ConflictResolution<T>()
    data class UserChoice<T>(val options: List<T>) : ConflictResolution<T>()
}

class SyncRepository(
    private val localDb: AppDatabase,
    private val remoteApi: ApiService
) {

    suspend fun syncNotes() {
        val localNotes = localDb.noteDao().getAllNotes()
        val remoteNotes = remoteApi.getNotes()

        val conflicts = mutableListOf<Pair<Note, Note>>()

        for (local in localNotes) {
            val remote = remoteNotes.find { it.id == local.id }

            when {
                remote == null -> {
                    // Local only - upload
                    remoteApi.uploadNote(local)
                }
                local.updatedAt > remote.updatedAt -> {
                    // Local is newer - upload
                    remoteApi.uploadNote(local)
                }
                local.updatedAt < remote.updatedAt -> {
                    // Remote is newer - download
                    localDb.noteDao().updateNote(remote)
                }
                else -> {
                    // Same timestamp but different content - conflict!
                    if (local.content != remote.content) {
                        conflicts.add(local to remote)
                    }
                }
            }
        }

        // Resolve conflicts
        conflicts.forEach { (local, remote) ->
            val resolved = resolveConflict(local, remote)
            localDb.noteDao().updateNote(resolved)
            remoteApi.uploadNote(resolved)
        }
    }

    private fun resolveConflict(local: Note, remote: Note): Note {
        // Last Write Wins strategy
        return if (local.updatedAt > remote.updatedAt) local else remote

        // Or: Merge strategy
        // return Note(
        //     id = local.id,
        //     content = "${local.content}\n---\n${remote.content}",
        //     updatedAt = System.currentTimeMillis()
        // )
    }
}

@Entity
data class Note(
    @PrimaryKey val id: String,
    val content: String,
    val updatedAt: Long,
    val synced: Boolean = false
)

// Offline-First Architecture (AP System)
class OfflineFirstRepository(
    private val localDb: AppDatabase,
    private val remoteApi: ApiService
) {

    // Always read from local database (Availability)
    fun getProducts(): Flow<List<Product>> {
        return localDb.productDao().getProducts()
    }

    // Sync in background
    suspend fun syncProducts() {
        try {
            val remoteProducts = remoteApi.getProducts()
            localDb.productDao().insertAll(remoteProducts)
        } catch (e: Exception) {
            // Offline - keep using local data (Eventual consistency)
        }
    }

    // Write to local first, sync later
    suspend fun updateProduct(product: Product) {
        localDb.productDao().updateProduct(product.copy(needsSync = true))

        try {
            remoteApi.updateProduct(product)
            localDb.productDao().updateProduct(product.copy(needsSync = false))
        } catch (e: Exception) {
            // Will sync when online
        }
    }
}
```

---

## Summary / Резюме

**English:**

**Key Concepts:**

1. **SQL vs NoSQL:**
   - SQL: Structured, ACID, complex queries
   - NoSQL: Flexible schema, horizontal scaling

2. **ACID Properties:**
   - Atomicity: All or nothing
   - Consistency: Valid state transitions
   - Isolation: Concurrent transaction safety
   - Durability: Persist after commit

3. **Indexing:**
   - Speeds up reads, slows writes
   - Index foreign keys and WHERE columns
   - Composite indexes for common queries

4. **Normalization:**
   - Reduces redundancy
   - 1NF, 2NF, 3NF eliminate anomalies
   - Denormalize for read performance

5. **Room Database:**
   - @Entity, @Dao, @Database
   - Transactions with withTransaction
   - Flow for reactive queries
   - Migrations for schema changes

6. **CAP Theorem:**
   - CP: Consistency + Partition (Banking)
   - AP: Availability + Partition (Social media)
   - Eventual consistency for offline-first

**Russian:**

**Ключевые концепции:**

1. **SQL против NoSQL:**
   - SQL: Структурированная, ACID, сложные запросы
   - NoSQL: Гибкая схема, горизонтальное масштабирование

2. **ACID свойства:**
   - Атомарность: Все или ничего
   - Согласованность: Валидные переходы состояний
   - Изолированность: Безопасность конкурентных транзакций
   - Долговечность: Сохранение после коммита

3. **Индексирование:**
   - Ускоряет чтение, замедляет запись
   - Индексировать внешние ключи и WHERE столбцы
   - Композитные индексы для частых запросов

4. **Нормализация:**
   - Уменьшает избыточность
   - 1НФ, 2НФ, 3НФ устраняют аномалии
   - Денормализация для производительности чтения

5. **Room База Данных:**
   - @Entity, @Dao, @Database
   - Транзакции с withTransaction
   - Flow для реактивных запросов
   - Миграции для изменений схемы

6. **Теорема CAP:**
   - CP: Согласованность + Разделение (Банкинг)
   - AP: Доступность + Разделение (Соцсети)
   - Eventual consistency для offline-first

---

## Follow-up Questions / Вопросы для Закрепления

1. **What are ACID properties? Explain each with an example.**
   **Что такое ACID свойства? Объясните каждое с примером.**

2. **When would you choose NoSQL over SQL database?**
   **Когда бы вы выбрали NoSQL вместо SQL базы данных?**

3. **Explain database normalization. What are 1NF, 2NF, and 3NF?**
   **Объясните нормализацию БД. Что такое 1НФ, 2НФ и 3НФ?**

4. **How do indexes improve query performance? What are the trade-offs?**
   **Как индексы улучшают производительность запросов? Какие компромиссы?**

5. **What is the CAP theorem? Give examples of CP and AP systems.**
   **Что такое теорема CAP? Приведите примеры CP и AP систем.**

6. **How do you handle database migrations in Room?**
   **Как обрабатывать миграции базы данных в Room?**

7. **Explain the difference between strong and eventual consistency.**
   **Объясните разницу между сильной и итоговой согласованностью.**

8. **When should you denormalize a database? What are the risks?**
   **Когда следует денормализовать базу данных? Каковы риски?**

9. **How do transactions ensure data integrity?**
   **Как транзакции обеспечивают целостность данных?**

10. **What is the difference between @Insert, @Update, and @Upsert in Room?**
    **В чем разница между @Insert, @Update и @Upsert в Room?**
