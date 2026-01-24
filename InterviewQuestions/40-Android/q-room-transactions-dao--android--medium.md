---
id: android-279
anki_cards:
- slug: android-279-0-en
  language: en
  anki_id: 1768420261015
  synced_at: '2026-01-23T16:45:06.004172'
- slug: android-279-0-ru
  language: ru
  anki_id: 1768420261057
  synced_at: '2026-01-23T16:45:06.005711'
title: Room Transactions Dao / Транзакции DAO в Room
aliases:
- Room Transactions Dao
- Транзакции DAO в Room
topic: android
subtopics:
- coroutines
- room
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-room
- q-room-library-definition--android--easy
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/coroutines
- android/room
- dao
- database
- difficulty/medium
- transactions
---
# Вопрос (RU)

> Как обеспечить атомарность операций с несколькими таблицами в `Room`? Покажите использование @Transaction для критических операций.

# Question (EN)

> How do you ensure atomicity for multi-table operations in `Room`? Show @Transaction usage for critical operations.

---

## Ответ (RU)

**Транзакции `Room`** гарантируют атомарность набора операций с базой данных через аннотацию `@Transaction` в DAO-методах и метод `withTransaction` у `RoomDatabase`. Это критично для поддержания целостности связанных данных.

Важно: транзакция будет откатена только если из аннотированного `@Transaction` метода или блока `withTransaction` выйдет неперехваченное исключение. Простое возвращение `Result.failure(...)` или логирование ошибки без выброса исключения не приводит к откату.

### Зачем Нужны Транзакции?

Без транзакций при сбое в середине серии операций возникают:
- **Несогласованность**: частично завершённые операции
- **Потерянные обновления**: конкурентные модификации
- **Нарушение ссылочной целостности**: осиротевшие foreign keys

### Использование @Transaction

```kotlin
@Dao
interface UserDao {
    @Insert
    suspend fun insertUser(user: User): Long

    @Insert
    suspend fun insertPosts(posts: List<Post>)

    // ✅ Атомарная операция - либо все изменения будут зафиксированы, либо при исключении всё откатится
    @Transaction
    suspend fun insertUserWithPosts(user: User, posts: List<Post>) {
        val userId = insertUser(user)
        val postsWithUserId = posts.map { it.copy(authorId = userId) }
        insertPosts(postsWithUserId)
        // Если здесь или выше будет выброшено исключение, транзакция откатится
    }

    // ✅ Используется для комплексных чтений (например, с @Relation), чтобы все связанные запросы
    // были выполнены в одной транзакции и дали согласованное состояние.
    // Для одного простого SELECT наличие @Transaction обычно не меняет семантику.
    @Transaction
    @Query("SELECT * FROM users WHERE userId = :userId")
    suspend fun getUserWithPosts(userId: Long): UserWithPosts?
}
```

### Ручные Транзакции Через withTransaction

Для сложной логики, выходящей за пределы одного метода DAO, используйте `RoomDatabase.withTransaction` и возвращайте результат из блока. Не перехватывайте исключения внутри блока, если хотите откатить транзакцию.

```kotlin
class UserRepository(
    private val database: AppDatabase,
    private val userDao: UserDao
) {
    suspend fun createUserWithComplexLogic(
        name: String,
        email: String
    ): Result<Long> = withContext(Dispatchers.IO) {
        runCatching {
            database.withTransaction {
                // ✅ Многошаговая логика в ручной транзакции
                val existingUser = userDao.findByEmail(email)
                if (existingUser != null) {
                    throw IllegalStateException("Email exists")
                }
                val newUserId = userDao.insertUser(User(name, email))
                database.statsDao().incrementUserCount()
                newUserId
            }
        }
    }
}
```

### Пример: Перевод Денег

```kotlin
@Dao
interface AccountDao {
    @Query("SELECT * FROM accounts WHERE accountId = :accountId")
    suspend fun getAccount(accountId: String): Account?

    @Query("UPDATE accounts SET balance = :newBalance WHERE accountId = :accountId")
    suspend fun updateBalance(accountId: String, newBalance: BigDecimal)

    // ✅ Атомарный перевод денег: при исключении все изменения откатываются
    @Transaction
    suspend fun transferMoney(
        fromAccountId: String,
        toAccountId: String,
        amount: BigDecimal
    ) {
        val fromAccount = getAccount(fromAccountId)
            ?: throw IllegalArgumentException("Исходный счёт не найден")
        val toAccount = getAccount(toAccountId)
            ?: throw IllegalArgumentException("Целевой счёт не найден")

        if (fromAccount.balance < amount) {
            throw IllegalStateException("Недостаточно средств")
        }

        // Оба обновления выполняются в пределах одной транзакции
        updateBalance(fromAccountId, fromAccount.balance - amount)
        updateBalance(toAccountId, toAccount.balance + amount)
        // Если исключение выброшено до конца метода, транзакция откатится
    }
}
```

Если требуется вернуть `Result`, оборачивайте вызов `transferMoney` снаружи в `runCatching { ... }`, а не глушите исключения внутри `@Transaction` метода.

### Оптимизация Производительности

```kotlin
// ❌ Плохо: множество отдельных транзакций
suspend fun insertUsersBad(users: List<User>) {
    users.forEach { user ->
        userDao.insertUser(user)  // 1000 users = до 1000 отдельных транзакций
    }
}

// ✅ Хорошо: одна транзакция для пакета
@Transaction
suspend fun insertUsersGood(users: List<User>) {
    userDao.insertUsers(users)  // 1000 users = 1 транзакция
    // Существенно снижает накладные расходы на открытие/закрытие транзакций
}
```

### Best Practices

1. **Держать транзакции короткими** - не включать сетевые вызовы и долгие операции
2. **Использовать batch-операции** вместо циклов с отдельными вызовами DAO
3. **Понимать модель отката** - исключение внутри `@Transaction`/`withTransaction` приводит к откату; если вы перехватываете исключение и не пробрасываете его, транзакция будет зафиксирована
4. **Тестировать сценарии отката** - проверять согласованность данных после ошибок

### Распространённые Ошибки

```kotlin
// ❌ Забыли @Transaction - неатомарная операция
suspend fun transferMoney(from: String, to: String, amount: BigDecimal) {
    debit(from, amount)   // Если успешно...
    credit(to, amount)    // ...но это упало = потеря денег!
}

// ✅ Атомарная операция
@Transaction
suspend fun transferMoney(from: String, to: String, amount: BigDecimal) {
    debit(from, amount)
    credit(to, amount)  // Либо обе успешны, либо при исключении всё откатится
}
```

---

## Answer (EN)

**`Room` Transactions** ensure atomic groups of operations via the `@Transaction` annotation on DAO methods and the `withTransaction` extension on `RoomDatabase`. This is critical for maintaining data integrity across related entities.

Important: a transaction is rolled back only if an exception escapes the `@Transaction` method or the `withTransaction` block. Simply returning `Result.failure(...)` or swallowing/logging an exception without rethrowing does NOT trigger rollback.

### Why Transactions?

Without transactions, mid-operation failures cause:
- **Inconsistent data**: partially completed operations
- **Lost updates**: concurrent modifications
- **Referential integrity violations**: orphaned foreign keys

### Using @Transaction

```kotlin
@Dao
interface UserDao {
    @Insert
    suspend fun insertUser(user: User): Long

    @Insert
    suspend fun insertPosts(posts: List<Post>)

    // ✅ Atomic operation - all changes are committed together, or rolled back if an exception occurs
    @Transaction
    suspend fun insertUserWithPosts(user: User, posts: List<Post>) {
        val userId = insertUser(user)
        val postsWithUserId = posts.map { it.copy(authorId = userId) }
        insertPosts(postsWithUserId)
        // If an exception is thrown here or above, the transaction is rolled back
    }

    // ✅ Used for composite reads (e.g., with @Relation) so that all related queries
    // run in a single transaction with a consistent view.
    // For a single simple SELECT, @Transaction usually does not change semantics.
    @Transaction
    @Query("SELECT * FROM users WHERE userId = :userId")
    suspend fun getUserWithPosts(userId: Long): UserWithPosts?
}
```

### Manual Transactions with withTransaction

For complex logic that spans beyond a single DAO method, use `RoomDatabase.withTransaction` and return a value from its block. Do not swallow exceptions inside the block if you want rollback.

```kotlin
class UserRepository(
    private val database: AppDatabase,
    private val userDao: UserDao
) {
    suspend fun createUserWithComplexLogic(
        name: String,
        email: String
    ): Result<Long> = withContext(Dispatchers.IO) {
        runCatching {
            database.withTransaction {
                // ✅ Multi-step logic in a manual transaction
                val existingUser = userDao.findByEmail(email)
                if (existingUser != null) {
                    throw IllegalStateException("Email exists")
                }
                val newUserId = userDao.insertUser(User(name, email))
                database.statsDao().incrementUserCount()
                newUserId
            }
        }
    }
}
```

### Example: Money Transfer

```kotlin
@Dao
interface AccountDao {
    @Query("SELECT * FROM accounts WHERE accountId = :accountId")
    suspend fun getAccount(accountId: String): Account?

    @Query("UPDATE accounts SET balance = :newBalance WHERE accountId = :accountId")
    suspend fun updateBalance(accountId: String, newBalance: BigDecimal)

    // ✅ Atomic money transfer: if an exception occurs, all changes are rolled back
    @Transaction
    suspend fun transferMoney(
        fromAccountId: String,
        toAccountId: String,
        amount: BigDecimal
    ) {
        val fromAccount = getAccount(fromAccountId)
            ?: throw IllegalArgumentException("Source not found")
        val toAccount = getAccount(toAccountId)
            ?: throw IllegalArgumentException("Destination not found")

        if (fromAccount.balance < amount) {
            throw IllegalStateException("Insufficient balance")
        }

        // Both updates are executed within a single transaction
        updateBalance(fromAccountId, fromAccount.balance - amount)
        updateBalance(toAccountId, toAccount.balance + amount)
        // If an exception is thrown before method completes, the transaction is rolled back
    }
}
```

If you need a `Result` wrapper, wrap the call to `transferMoney` in `runCatching { ... }` (outside the `@Transaction` method) instead of catching exceptions inside it.

### Performance Optimization

```kotlin
// ❌ Bad: multiple separate transactions
suspend fun insertUsersBad(users: List<User>) {
    users.forEach { user ->
        userDao.insertUser(user)  // 1000 users = up to 1000 separate transactions
    }
}

// ✅ Good: single transaction for batch
@Transaction
suspend fun insertUsersGood(users: List<User>) {
    userDao.insertUsers(users)  // 1000 users = 1 transaction
    // Significantly reduces overhead of opening/committing many transactions
}
```

### Best Practices

1. **Keep transactions short** - avoid network calls and long-running work inside
2. **Use batch operations** instead of loops with many individual DAO calls
3. **Understand rollback semantics** - exceptions inside `@Transaction`/`withTransaction` cause rollback; if you catch and do not rethrow, changes will be committed
4. **Test rollback scenarios** - verify data consistency after failures

### Common Mistakes

```kotlin
// ❌ Forgot @Transaction - non-atomic operation
suspend fun transferMoney(from: String, to: String, amount: BigDecimal) {
    debit(from, amount)   // If this succeeds...
    credit(to, amount)    // ...but this fails = lost money!
}

// ✅ Atomic operation
@Transaction
suspend fun transferMoney(from: String, to: String, amount: BigDecimal) {
    debit(from, amount)
    credit(to, amount)  // Either both succeed, or on exception everything is rolled back
}
```

---

## Follow-ups

- How does `Room` handle nested transactions (savepoints)?
- What isolation level does `Room` use by default?
- How to test transaction rollback scenarios effectively?
- When should you use `withTransaction` vs `@Transaction`?
- How do transactions affect database performance and locking?

## References

- [[c-room]] - `Room` database architecture
- [[c-coroutines]] - Suspend functions and concurrency

## Related Questions

### Prerequisites
- [[q-room-library-definition--android--easy]] - Basic `Room` concepts

### Related
- [[q-room-code-generation-timing--android--medium]] - `Room` annotation processing
- [[q-room-paging3-integration--android--medium]] - `Room` with Paging
- [[q-room-type-converters--android--medium]] - Custom type handling

### Advanced
- [[q-room-fts-full-text-search--android--hard]] - Full-text search in `Room`
