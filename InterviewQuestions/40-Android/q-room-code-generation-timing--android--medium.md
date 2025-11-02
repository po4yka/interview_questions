---
id: android-122
title: "Room Code Generation Timing / Время генерации кода Room"
aliases: ["Room Code Generation Timing", "Время генерации кода Room"]
topic: android
subtopics: [gradle, room]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-dagger-framework-overview--android--hard, q-kapt-ksp-migration--android--medium, q-kapt-vs-ksp--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/gradle, android/room, code-generation, compile-time, difficulty/medium, kapt, ksp]
date created: Saturday, November 1st 2025, 12:47:02 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Вопрос (RU)

В какой момент генерируется код при использовании SQLite/Room?

# Question (EN)

When is code generated when using SQLite/Room?

## Ответ (RU)

**Room** генерирует код **на этапе компиляции** через процессоры аннотаций: **kapt** или **KSP**.

**SQLite** сам по себе не генерирует код - это runtime библиотека. Room как слой абстракции над SQLite использует annotation processing для генерации реализаций DAO и Database классов.

### Процесс Генерации

1. **Аннотированный код**
```kotlin
@Entity
data class User(
    @PrimaryKey val id: Int,
    val name: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM user") // ✅ SQL валидируется на этапе компиляции
    fun getAll(): List<User>

    @Insert
    suspend fun insert(user: User)
}
```

2. **Конфигурация процессора**
```kotlin
// kapt (медленнее, Java API)
dependencies {
    kapt "androidx.room:room-compiler"
}

// KSP (в 2 раза быстрее, Kotlin API) ✅ рекомендуется
dependencies {
    ksp "androidx.room:room-compiler"
}
```

3. **Генерируемая реализация** (в `build/generated/`)
```kotlin
class UserDao_Impl : UserDao {
    override fun getAll(): List<User> {
        val statement = RoomSQLiteQuery.acquire("SELECT * FROM user", 0)
        // ✅ Генерируется маппинг курсора в объекты
        return executeSqlQuery(statement) { cursor ->
            User(cursor.getInt(0), cursor.getString(1))
        }
    }
}
```

### Kapt Vs KSP

| Аспект | kapt | KSP |
|--------|------|-----|
| API | Java | Kotlin |
| Скорость | Базовая | 2x быстрее |
| Инкрементальная компиляция | Ограниченная | Полная |

**Рекомендация:** KSP для новых проектов.

### Валидация На Этапе Компиляции

```kotlin
@Query("SELECT * FROM usres") // ❌ Ошибка: таблица не существует
fun getAll(): List<User>

// Результат компиляции:
// error: no such table: usres
```

**Преимущества:**
- Ошибки в SQL обнаруживаются до запуска приложения
- Type safety: автоматическая типизация результатов
- Нет runtime reflection - лучшая производительность

## Answer (EN)

**Room** generates code **at compile time** using annotation processors: **kapt** or **KSP**.

**SQLite** itself doesn't generate code - it's a runtime library. Room as an abstraction layer over SQLite uses annotation processing to generate DAO and Database implementations.

### Generation Process

1. **Annotated Code**
```kotlin
@Entity
data class User(
    @PrimaryKey val id: Int,
    val name: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM user") // ✅ SQL validated at compile time
    fun getAll(): List<User>

    @Insert
    suspend fun insert(user: User)
}
```

2. **Processor Configuration**
```kotlin
// kapt (slower, Java API)
dependencies {
    kapt "androidx.room:room-compiler"
}

// KSP (2x faster, Kotlin API) ✅ recommended
dependencies {
    ksp "androidx.room:room-compiler"
}
```

3. **Generated Implementation** (in `build/generated/`)
```kotlin
class UserDao_Impl : UserDao {
    override fun getAll(): List<User> {
        val statement = RoomSQLiteQuery.acquire("SELECT * FROM user", 0)
        // ✅ Generates cursor-to-object mapping
        return executeSqlQuery(statement) { cursor ->
            User(cursor.getInt(0), cursor.getString(1))
        }
    }
}
```

### Kapt Vs KSP

| Aspect | kapt | KSP |
|--------|------|-----|
| API | Java | Kotlin |
| Speed | Baseline | 2x faster |
| Incremental | Limited | Full |

**Recommendation:** KSP for new projects.

### Compile-Time Validation

```kotlin
@Query("SELECT * FROM usres") // ❌ Error: table doesn't exist
fun getAll(): List<User>

// Compilation result:
// error: no such table: usres
```

**Benefits:**
- SQL errors caught before app runs
- Type safety: automatic result typing
- No runtime reflection - better performance

---

## Follow-ups

- How does Room handle schema migrations with generated code?
- What are the trade-offs between kapt and KSP incremental compilation?
- How does Room's compile-time validation differ from raw SQLite runtime errors?
- Can annotation processors access database schema at compile time?
- How does KSP achieve 2x performance improvement over kapt?

## References

- Android Room Documentation
- KSP vs KAPT performance comparison studies

## Related Questions

### Prerequisites
- Basic annotation processing concepts
- Understanding of compile-time vs runtime code generation

### Related
- [[q-dagger-framework-overview--android--hard]] - Another annotation processing framework
- Room migration strategies
- Type converters in Room

### Advanced
- Custom annotation processor implementation
- Multi-module Room database architecture
