---
id: android-148
title: "Room Relations and Embedded / Отношения и Embedded в Room"
aliases: ["Room Relations and Embedded", "Отношения и Embedded в Room"]

# Classification
topic: android
subtopics: [architecture-clean, room]
question_kind: theory
difficulty: medium

# Language
original_language: en
language_tags: [en, ru]
sources: []

# Workflow
status: draft
moc: moc-android
related: [c-database-relations, c-room-database]

# Timestamps
created: 2025-10-15
updated: 2025-10-28

# Tags
tags: [android/architecture-clean, android/room, database, difficulty/medium, embedded, relations]
---

# Вопрос (RU)

> Как реализовать связи между сущностями в Room Database? Объясни использование `@Relation` для отношений один-ко-многим и многие-ко-многим, а также `@Embedded` для встраивания объектов в одну таблицу.

# Question (EN)

> How do you implement relationships between entities in Room Database? Explain using `@Relation` for one-to-many and many-to-many relationships, and `@Embedded` for flattening objects into a single table.

---

## Ответ (RU)

Room предоставляет два механизма для работы с связями: `@Embedded` для встраивания объектов в одну таблицу и `@Relation` для моделирования связей между отдельными сущностями.

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
    foreignKeys = [ForeignKey(  // ✅ Обеспечивает целостность данных
        entity = User::class,
        parentColumns = ["userId"],
        childColumns = ["authorId"],
        onDelete = ForeignKey.CASCADE
    )],
    indices = [Index("authorId")]  // ✅ Критически важно для производительности
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
    @Transaction  // ✅ Обязательна для атомарности
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
        ForeignKey(entity = Student::class, parentColumns = ["studentId"], childColumns = ["studentId"], onDelete = ForeignKey.CASCADE),
        ForeignKey(entity = Course::class, parentColumns = ["courseId"], childColumns = ["courseId"], onDelete = ForeignKey.CASCADE)
    ],
    indices = [Index("studentId"), Index("courseId")]  // ✅ Обязательные индексы
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
        associateBy = Junction(Enrollment::class)  // ✅ Junction определяет связь
    )
    val courses: List<Course>
)

@Dao
interface EnrollmentDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun enroll(enrollment: Enrollment)

    @Transaction
    @Query("SELECT * FROM students WHERE studentId = :id")
    suspend fun getStudentWithCourses(id: Long): StudentWithCourses?
}
```

### Ключевые Принципы

1. **Foreign Keys обязательны**: Гарантируют целостность данных на уровне БД
2. **Индексы критичны**: Индексируйте все внешние ключи (иначе JOIN будет медленным)
3. **@Transaction обязательна**: Обеспечивает атомарность при загрузке связей
4. **CASCADE для parent-child**: Автоматически удаляет дочерние записи
5. **Ленивая загрузка**: Не загружайте все связи заранее, используйте пагинацию для больших списков

**Сравнение @Embedded vs @Relation**:

| Критерий | @Embedded | @Relation |
|----------|-----------|-----------|
| Таблицы | Одна | Несколько |
| Производительность | Быстрая (без JOIN) | Медленнее (JOIN) |
| Нормализация | Денормализована | Нормализована |
| Использование | Address, Coordinates | One-to-many, Many-to-many |

## Answer (EN)

Room provides two mechanisms for working with relationships: `@Embedded` for flattening objects into a single table and `@Relation` for modeling relationships between separate entities.

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
    foreignKeys = [ForeignKey(  // ✅ Enforces data integrity
        entity = User::class,
        parentColumns = ["userId"],
        childColumns = ["authorId"],
        onDelete = ForeignKey.CASCADE
    )],
    indices = [Index("authorId")]  // ✅ Critical for performance
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
    @Transaction  // ✅ Required for atomicity
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
        ForeignKey(entity = Student::class, parentColumns = ["studentId"], childColumns = ["studentId"], onDelete = ForeignKey.CASCADE),
        ForeignKey(entity = Course::class, parentColumns = ["courseId"], childColumns = ["courseId"], onDelete = ForeignKey.CASCADE)
    ],
    indices = [Index("studentId"), Index("courseId")]  // ✅ Required indices
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
        associateBy = Junction(Enrollment::class)  // ✅ Junction defines the relationship
    )
    val courses: List<Course>
)

@Dao
interface EnrollmentDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun enroll(enrollment: Enrollment)

    @Transaction
    @Query("SELECT * FROM students WHERE studentId = :id")
    suspend fun getStudentWithCourses(id: Long): StudentWithCourses?
}
```

### Key Principles

1. **Foreign Keys are mandatory**: Guarantee data integrity at database level
2. **Indices are critical**: Index all foreign keys (otherwise JOINs will be slow)
3. **@Transaction is required**: Ensures atomicity when loading relations
4. **CASCADE for parent-child**: Automatically deletes child records
5. **Lazy loading**: Don't load all relations upfront, use pagination for large lists

**Comparison @Embedded vs @Relation**:

| Criterion | @Embedded | @Relation |
|-----------|-----------|-----------|
| Tables | Single | Multiple |
| Performance | Fast (no JOIN) | Slower (JOIN) |
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
- [[c-database-relations]]
- [[c-database-normalization]]
- https://developer.android.com/training/data-storage/room/relationships
- https://developer.android.com/reference/androidx/room/Relation
- https://developer.android.com/reference/androidx/room/Embedded

## Related Questions

### Prerequisites (Easier)
- [[q-room-library-definition--android--easy]] — Room basics and setup
- [[q-sharedpreferences-commit-vs-apply--android--easy]] — Alternative storage options

### Related (Same Level)
- [[q-room-transactions-dao--android--medium]] — Transaction handling in Room
- [[q-room-type-converters-advanced--android--medium]] — Converting complex types
- [[q-room-code-generation-timing--android--medium]] — Room annotation processing
- [[q-room-vs-sqlite--android--medium]] — Room vs raw SQLite comparison

### Advanced (Harder)
- [[q-room-fts-full-text-search--android--hard]] — Full-text search in Room
- [[q-room-paging3-integration--room--hard]] — Integrating Room with Paging 3
- [[q-room-multidb-sharding--room--hard]] — Multi-database architecture
