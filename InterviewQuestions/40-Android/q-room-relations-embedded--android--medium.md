---
id: android-148
title: Room Relations and Embedded / Отношения и Embedded в Room
aliases:
- Room Relations and Embedded
- Отношения и Embedded в Room
topic: android
subtopics:
- architecture-clean
- room
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
- c-database-design
- c-room-database
created: 2025-10-15
updated: 2025-11-10
tags:
- android/architecture-clean
- android/room
- difficulty/medium
- embedded
- relations
anki_cards:
- slug: android-148-0-en
  language: en
  anki_id: 1768396545600
  synced_at: '2026-01-23T16:45:05.400249'
- slug: android-148-0-ru
  language: ru
  anki_id: 1768396545625
  synced_at: '2026-01-23T16:45:05.401916'
---
# Вопрос (RU)

> Как реализовать связи между сущностями в `Room` `Database`? Объясни использование `@Relation` для отношений один-ко-многим и многие-ко-многим, а также `@Embedded` для встраивания объектов в одну таблицу.

# Question (EN)

> How do you implement relationships between entities in `Room` `Database`? Explain using `@Relation` for one-to-many and many-to-many relationships, and `@Embedded` for flattening objects into a single table.

---

## Ответ (RU)

`Room` предоставляет два механизма для работы со связями: `@Embedded` для встраивания объектов в одну таблицу и `@Relation` для моделирования связей между отдельными сущностями.

### @Embedded — Встраивание Объектов

`@Embedded` позволяет встроить поля объекта непосредственно в таблицу, избегая создания отдельных таблиц или JSON-сериализации.

```kotlin
data class Address(
    val street: String,
    val city: String
)

@Entity(tableName = "users")
data class User(
    @PrimaryKey val userId: Long,
    val name: String,
    @Embedded val address: Address  // ✅ Поля встраиваются в таблицу users
)
// Результат: users(userId, name, street, city)
```

**Префиксы для избежания конфликтов**:

```kotlin
data class Coordinates(
    val lat: Double,
    val lon: Double
)

@Entity(tableName = "stores")
data class Store(
    @PrimaryKey val storeId: Long,
    @Embedded(prefix = "pickup_") val pickupLocation: Coordinates,  // ✅ pickup_lat, pickup_lon
    @Embedded(prefix = "delivery_") val deliveryLocation: Coordinates  // ✅ delivery_lat, delivery_lon
)
```

### @Relation — Связи Между Сущностями

**Один-ко-многим**:

```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey val userId: Long,
    val name: String
)

@Entity(
    tableName = "posts",
    foreignKeys = [
        ForeignKey(  // ✅ Обеспечивает целостность данных
            entity = User::class,
            parentColumns = ["userId"],
            childColumns = ["authorId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("authorId")]  // ✅ Важно для производительности при связях по внешнему ключу
)

data class Post(
    @PrimaryKey val postId: Long,
    val authorId: Long,
    val content: String
)

data class UserWithPosts(
    @Embedded val user: User,
    @Relation(
        parentColumn = "userId",
        entityColumn = "authorId"
    )
    val posts: List<Post>
)

@Dao
interface UserDao {
    @Transaction  // ✅ Гарантирует, что все связанные запросы для @Relation выполняются атомарно и возвращают консистентные данные
    @Query("SELECT * FROM users WHERE userId = :id")
    suspend fun getUserWithPosts(id: Long): UserWithPosts?
}
```

**Многие-ко-многим через Junction Table**:

```kotlin
@Entity(tableName = "students")
data class Student(@PrimaryKey val studentId: Long, val name: String)

@Entity(tableName = "courses")
data class Course(@PrimaryKey val courseId: Long, val code: String)

@Entity(
    tableName = "enrollments",
    primaryKeys = ["studentId", "courseId"],  // ✅ Составной ключ
    foreignKeys = [
        ForeignKey(
            entity = Student::class,
            parentColumns = ["studentId"],
            childColumns = ["studentId"],
            onDelete = ForeignKey.CASCADE
        ),
        ForeignKey(
            entity = Course::class,
            parentColumns = ["courseId"],
            childColumns = ["courseId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("studentId"), Index("courseId")]  // ✅ Рекомендуется для производительности
)
data class Enrollment(
    val studentId: Long,
    val courseId: Long,
    val grade: String? = null  // ✅ Дополнительные данные связи
)

data class StudentWithCourses(
    @Embedded val student: Student,
    @Relation(
        parentColumn = "studentId",
        entityColumn = "courseId",
        associateBy = Junction(Enrollment::class)  // ✅ Junction указывает таблицу связей; Room использует её колонки по именам
    )
    val courses: List<Course>
)

@Dao
interface EnrollmentDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun enroll(enrollment: Enrollment)

    @Transaction  // ✅ Обеспечивает атомарную и консистентную загрузку связанных данных
    @Query("SELECT * FROM students WHERE studentId = :id")
    suspend fun getStudentWithCourses(id: Long): StudentWithCourses?
}
```

### Ключевые Принципы

1. **Внешние ключи**: Рекомендуются для гарантии целостности данных на уровне БД, но не являются строго обязательными для работы `@Relation` (она опирается на соответствие значений колонок; связь описывается в data class).
2. **Индексы**: Индексируйте колонки, используемые как внешние ключи и в условиях JOIN/фильтрации — это важно для производительности, хотя не строго обязательно.
3. **@Transaction**: Используйте при запросах, которые читают несколько связанных сущностей или требуют нескольких SQL-запросов под капотом (`@Relation` может генерировать отдельные запросы), чтобы получить консистентные данные.
4. **CASCADE**: `onDelete = CASCADE` удобно для связей parent-child, но включайте его только если логика домена требует автоматического удаления дочерних записей.
5. **Загрузка данных**: `Room` не делает "ленивую" загрузку автоматически. Данные по `@Relation` загружаются в рамках соответствующего DAO-метода и могут требовать дополнительных запросов. Для больших наборов данных используйте отдельные запросы, лимиты, пагинацию и/или Paging 3.

**Сравнение @Embedded vs @Relation**:

| Критерий | @Embedded | @Relation |
|----------|-----------|-----------|
| Таблицы | Одна | Несколько |
| Производительность | Обычно быстрее и проще (без отношений между таблицами) | Может быть дороже (нужны связи между таблицами, JOIN или несколько запросов) |
| Нормализация | Денормализована | Нормализована |
| Использование | Address, Coordinates | One-to-many, Many-to-many |

## Answer (EN)

`Room` provides two mechanisms for working with relationships: `@Embedded` for flattening objects into a single table and `@Relation` for modeling relationships between separate entities.

### @Embedded — Object Flattening

`@Embedded` allows you to flatten an object's fields directly into a table, avoiding separate tables or JSON serialization.

```kotlin
data class Address(
    val street: String,
    val city: String
)

@Entity(tableName = "users")
data class User(
    @PrimaryKey val userId: Long,
    val name: String,
    @Embedded val address: Address  // ✅ Fields are flattened into users table
)
// Result: users(userId, name, street, city)
```

**Prefixes to avoid conflicts**:

```kotlin
data class Coordinates(
    val lat: Double,
    val lon: Double
)

@Entity(tableName = "stores")
data class Store(
    @PrimaryKey val storeId: Long,
    @Embedded(prefix = "pickup_") val pickupLocation: Coordinates,  // ✅ pickup_lat, pickup_lon
    @Embedded(prefix = "delivery_") val deliveryLocation: Coordinates  // ✅ delivery_lat, delivery_lon
)
```

### @Relation — Entity Relationships

**One-to-Many**:

```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey val userId: Long,
    val name: String
)

@Entity(
    tableName = "posts",
    foreignKeys = [
        ForeignKey(  // ✅ Enforces data integrity
            entity = User::class,
            parentColumns = ["userId"],
            childColumns = ["authorId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("authorId")]  // ✅ Important for performance when querying by foreign key
)

data class Post(
    @PrimaryKey val postId: Long,
    val authorId: Long,
    val content: String
)

data class UserWithPosts(
    @Embedded val user: User,
    @Relation(
        parentColumn = "userId",
        entityColumn = "authorId"
    )
    val posts: List<Post>
)

@Dao
interface UserDao {
    @Transaction  // ✅ Ensures that all underlying queries for @Relation run atomically and return a consistent snapshot
    @Query("SELECT * FROM users WHERE userId = :id")
    suspend fun getUserWithPosts(id: Long): UserWithPosts?
}
```

**Many-to-Many via Junction Table**:

```kotlin
@Entity(tableName = "students")
data class Student(@PrimaryKey val studentId: Long, val name: String)

@Entity(tableName = "courses")
data class Course(@PrimaryKey val courseId: Long, val code: String)

@Entity(
    tableName = "enrollments",
    primaryKeys = ["studentId", "courseId"],  // ✅ Composite key
    foreignKeys = [
        ForeignKey(
            entity = Student::class,
            parentColumns = ["studentId"],
            childColumns = ["studentId"],
            onDelete = ForeignKey.CASCADE
        ),
        ForeignKey(
            entity = Course::class,
            parentColumns = ["courseId"],
            childColumns = ["courseId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("studentId"), Index("courseId")]  // ✅ Recommended indices for performance
)
data class Enrollment(
    val studentId: Long,
    val courseId: Long,
    val grade: String? = null  // ✅ Additional relationship data
)

data class StudentWithCourses(
    @Embedded val student: Student,
    @Relation(
        parentColumn = "studentId",
        entityColumn = "courseId",
        associateBy = Junction(Enrollment::class)  // ✅ Junction points to the link table; Room infers columns by their names
    )
    val courses: List<Course>
)

@Dao
interface EnrollmentDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun enroll(enrollment: Enrollment)

    @Transaction  // ✅ Ensures all queries needed to load the relation run atomically and see a consistent state
    @Query("SELECT * FROM students WHERE studentId = :id")
    suspend fun getStudentWithCourses(id: Long): StudentWithCourses?
}
```

### Key Principles

1. **Foreign Keys**: Recommended to guarantee data integrity at the database level, but `@Relation` itself relies on matching column values in the mapped data class and does not require foreign keys to function.
2. **Indices**: Index the columns used as foreign keys and in JOIN/WHERE clauses for performance; not strictly required but important in real applications.
3. **@Transaction**: Use when reading multiple related entities or when `@Relation` triggers multiple queries under the hood, so the result is consistent.
4. **CASCADE**: `onDelete = CASCADE` is useful for parent-child relationships but should be enabled only if your domain logic expects automatic deletion of child rows.
5. **Data loading**: `Room` does not provide implicit lazy loading. `@Relation` data is loaded as part of the DAO method execution and may involve multiple queries. For large datasets, design dedicated queries, use limits/pagination, and/or Paging 3.

**Comparison @Embedded vs @Relation**:

| Criterion | @Embedded | @Relation |
|-----------|-----------|-----------|
| Tables | Single | Multiple |
| Performance | Typically simpler and faster (no cross-table relationships) | Potentially more expensive (requires cross-table relationships via JOINs or multiple queries) |
| Normalization | Denormalized | Normalized |
| Use Case | Address, Coordinates | One-to-many, Many-to-many |

---

## Follow-ups

- How do you handle bidirectional relationships (e.g., User → Post and Post → User) without circular dependencies?
- What performance considerations should you keep in mind when querying deeply nested relations?
- How would you implement pagination for `@Relation` queries with large datasets?
- When should you use `@Embedded` vs creating a separate entity with `@Relation`?
- How do you handle migration when changing from `@Embedded` to `@Relation` or vice versa?

## References

- [[c-room-database]]
- https://developer.android.com/training/data-storage/room/relationships
- https://developer.android.com/reference/androidx/room/Relation
- https://developer.android.com/reference/androidx/room/Embedded

## Related Questions

### Prerequisites (Easier)
- [[q-room-library-definition--android--easy]] — `Room` basics and setup
- [[q-sharedpreferences-commit-vs-apply--android--easy]] — Alternative storage options

### Related (Same Level)
- [[q-room-transactions-dao--android--medium]] — Transaction handling in `Room`
- [[q-room-type-converters-advanced--android--medium]] — Converting complex types
- [[q-room-code-generation-timing--android--medium]] — `Room` annotation processing
- [[q-room-vs-sqlite--android--medium]] — `Room` vs raw `SQLite` comparison

### Advanced (Harder)
- [[q-room-fts-full-text-search--android--hard]] — Full-text search in `Room`
