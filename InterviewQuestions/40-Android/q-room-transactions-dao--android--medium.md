---
id: android-279
title: "Room Transactions Dao / Транзакции DAO в Room"
aliases: ["Room Transactions Dao", "Транзакции DAO в Room"]
topic: android
subtopics: [coroutines, room]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-room, q-room-library-definition--android--easy]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/coroutines, android/room, dao, database, difficulty/medium, transactions]
---

# Вопрос (RU)

> Как обеспечить атомарность операций с несколькими таблицами в Room? Покажите использование @Transaction для критических операций.

# Question (EN)

> How do you ensure atomicity for multi-table operations in Room? Show @Transaction usage for critical operations.

---

## Ответ (RU)

**Транзакции Room** гарантируют атомарность операций с базой данных через аннотацию `@Transaction` и метод `withTransaction`. Это критично для поддержания целостности связанных данных.

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

    // ✅ Атомарная операция - обе успешны или обе откатятся
    @Transaction
    suspend fun insertUserWithPosts(user: User, posts: List<Post>) {
        val userId = insertUser(user)
        val postsWithUserId = posts.map { it.copy(authorId = userId) }
        insertPosts(postsWithUserId)
    }

    // ✅ Операция чтения обеспечивает согласованный снимок
    @Transaction
    @Query("SELECT * FROM users WHERE userId = :userId")
    suspend fun getUserWithPosts(userId: Long): UserWithPosts?
}
```

### Ручные Транзакции Через withTransaction

Для сложной логики, не выражаемой в одном методе DAO:

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
                // ✅ Многошаговая логика в ручной транзакции
                val existingUser = userDao.findByEmail(email)
                if (existingUser != null) {
                    throw IllegalStateException("Email exists")
                }
                val userId = userDao.insertUser(User(name, email))
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

### Пример: Перевод Денег

```kotlin
@Dao
interface AccountDao {
    @Query("SELECT * FROM accounts WHERE accountId = :accountId")
    suspend fun getAccount(accountId: String): Account?

    @Query("UPDATE accounts SET balance = :newBalance WHERE accountId = :accountId")
    suspend fun updateBalance(accountId: String, newBalance: BigDecimal)

    // ✅ Атомарный перевод денег
    @Transaction
    suspend fun transferMoney(
        fromAccountId: String,
        toAccountId: String,
        amount: BigDecimal
    ): Result<Unit> {
        return try {
            val fromAccount = getAccount(fromAccountId)
                ?: throw IllegalArgumentException("Исходный счёт не найден")
            val toAccount = getAccount(toAccountId)
                ?: throw IllegalArgumentException("Целевой счёт не найден")

            if (fromAccount.balance < amount) {
                throw IllegalStateException("Недостаточно средств")
            }

            // Оба обновления успешны или оба откатятся
            updateBalance(fromAccountId, fromAccount.balance - amount)
            updateBalance(toAccountId, toAccount.balance + amount)

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Оптимизация Производительности

```kotlin
// ❌ Плохо: множество отдельных транзакций
suspend fun insertUsersBad(users: List<User>) {
    users.forEach { user ->
        userDao.insertUser(user)  // 1000 users = 1000 transactions
    }
}

// ✅ Хорошо: одна транзакция для пакета
@Transaction
suspend fun insertUsersGood(users: List<User>) {
    userDao.insertUsers(users)  // 1000 users = 1 transaction
    // В 25-100 раз быстрее
}
```

### Best Practices

1. **Держать транзакции короткими** - не включать сетевые вызовы
2. **Использовать batch операции** вместо циклов
3. **Всегда обрабатывать исключения** - проверять откат
4. **Тестировать сценарии отката** - проверять согласованность данных

### Распространённые Ошибки

```kotlin
// ❌ Забыли @Transaction - неатомарная операция
suspend fun transferMoney(from: String, to: String, amount: BigDecimal) {
    debit(from, amount)   // Если успешно...
    credit(to, amount)    // ...но это упало = потеряли деньги!
}

// ✅ Атомарная операция
@Transaction
suspend fun transferMoney(from: String, to: String, amount: BigDecimal) {
    debit(from, amount)
    credit(to, amount)  // Либо обе успешны, либо обе откатятся
}
```

---

## Answer (EN)

**Room Transactions** ensure atomic database operations via `@Transaction` annotation and `withTransaction` method. This is critical for maintaining data integrity across related entities.

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

    // ✅ Atomic operation - both succeed or both fail
    @Transaction
    suspend fun insertUserWithPosts(user: User, posts: List<Post>) {
        val userId = insertUser(user)
        val postsWithUserId = posts.map { it.copy(authorId = userId) }
        insertPosts(postsWithUserId)
    }

    // ✅ Read operation ensures consistent snapshot
    @Transaction
    @Query("SELECT * FROM users WHERE userId = :userId")
    suspend fun getUserWithPosts(userId: Long): UserWithPosts?
}
```

### Manual Transactions with withTransaction

For complex logic not expressible in single DAO method:

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
                // ✅ Multi-step logic in manual transaction
                val existingUser = userDao.findByEmail(email)
                if (existingUser != null) {
                    throw IllegalStateException("Email exists")
                }
                val userId = userDao.insertUser(User(name, email))
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

### Example: Money Transfer

```kotlin
@Dao
interface AccountDao {
    @Query("SELECT * FROM accounts WHERE accountId = :accountId")
    suspend fun getAccount(accountId: String): Account?

    @Query("UPDATE accounts SET balance = :newBalance WHERE accountId = :accountId")
    suspend fun updateBalance(accountId: String, newBalance: BigDecimal)

    // ✅ Atomic money transfer
    @Transaction
    suspend fun transferMoney(
        fromAccountId: String,
        toAccountId: String,
        amount: BigDecimal
    ): Result<Unit> {
        return try {
            val fromAccount = getAccount(fromAccountId)
                ?: throw IllegalArgumentException("Source not found")
            val toAccount = getAccount(toAccountId)
                ?: throw IllegalArgumentException("Destination not found")

            if (fromAccount.balance < amount) {
                throw IllegalStateException("Insufficient balance")
            }

            // Both updates succeed or both fail
            updateBalance(fromAccountId, fromAccount.balance - amount)
            updateBalance(toAccountId, toAccount.balance + amount)

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Performance Optimization

```kotlin
// ❌ Bad: multiple separate transactions
suspend fun insertUsersBad(users: List<User>) {
    users.forEach { user ->
        userDao.insertUser(user)  // 1000 users = 1000 transactions
    }
}

// ✅ Good: single transaction for batch
@Transaction
suspend fun insertUsersGood(users: List<User>) {
    userDao.insertUsers(users)  // 1000 users = 1 transaction
    // 25-100x faster
}
```

### Best Practices

1. **Keep transactions short** - no network calls inside
2. **Use batch operations** instead of loops
3. **Always handle exceptions** - verify rollback
4. **Test rollback scenarios** - verify data consistency

### Common Mistakes

```kotlin
// ❌ Forgot @Transaction - non-atomic operation
suspend fun transferMoney(from: String, to: String, amount: BigDecimal) {
    debit(from, amount)   // If succeeds...
    credit(to, amount)    // ...but this fails = lost money!
}

// ✅ Atomic operation
@Transaction
suspend fun transferMoney(from: String, to: String, amount: BigDecimal) {
    debit(from, amount)
    credit(to, amount)  // Either both succeed or both rollback
}
```

---

## Follow-ups

- How does Room handle nested transactions (savepoints)?
- What isolation level does Room use by default?
- How to test transaction rollback scenarios effectively?
- When should you use `withTransaction` vs `@Transaction`?
- How do transactions affect database performance and locking?

## References

- [[c-room]] - Room database architecture
- [[c-coroutines]] - Suspend functions and concurrency

## Related Questions

### Prerequisites
- [[q-room-library-definition--android--easy]] - Basic Room concepts

### Related
- [[q-room-code-generation-timing--android--medium]] - Room annotation processing
- [[q-room-paging3-integration--android--medium]] - Room with Paging
- [[q-room-type-converters--android--medium]] - Custom type handling

### Advanced
- [[q-room-fts-full-text-search--android--hard]] - Full-text search in Room
