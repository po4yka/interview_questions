---\
id: android-122
title: Room Code Generation Timing / Время генерации кода Room
aliases: [Room Code Generation Timing, Время генерации кода Room]
topic: android
subtopics: [room]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-room, q-dagger-framework-overview--android--hard, q-kapt-ksp-migration--android--medium, q-kapt-vs-ksp--android--medium, q-room-database-migrations--android--medium, q-room-relations-embedded--android--medium, q-room-type-converters-advanced--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/room, difficulty/medium]
---\
# Вопрос (RU)

> В какой момент генерируется код при использовании SQLite/Room?

# Question (EN)

> When is code generated when using SQLite/Room?

## Ответ (RU)

**`Room`** генерирует код **на этапе компиляции** в процессе сборки Gradle через процессоры аннотаций (`kapt` или `KSP`). Генерация выполняется во время соответствующих задач сборки (annotation processing), до упаковки APK/AAB, а не в рантайме приложения.

**`SQLite`** — это встраиваемый движок базы данных, а не фреймворк кодогенерации и не annotation processor. Он не генерирует код за вас; с ним вы либо пишете SQL вручную, либо используете библиотеки-обертки (такие как `Room`), которые уже занимаются генерацией вспомогательного кода на этапе сборки.

`Room` как слой абстракции над `SQLite` использует annotation processing для генерации реализаций DAO и `Database` классов и для compile-time валидации сущностей и запросов на основе известных ему моделей.

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
// kapt (использует Java Annotation Processing API)
dependencies {
    kapt "androidx.room:room-compiler"
}

// KSP (использует Kotlin Symbol Processing API) ✅ рекомендуется для новых проектов
dependencies {
    ksp "androidx.room:room-compiler"
}
```

> На практике KSP для `Room` обычно быстрее и лучше интегрируется с Kotlin и инкрементальной компиляцией, но выигрыш в производительности зависит от проекта и не является гарантированным фиксированным "2x".

1. **Генерируемая реализация** (примерно, в `build/generated/`) — упрощённый псевдокод
```kotlin
class UserDao_Impl : UserDao {
    override fun getAll(): List<User> {
        val statement = RoomSQLiteQuery.acquire("SELECT * FROM user", 0)
        // ✅ Генерируется код, который выполняет запрос и маппит Cursor в User
        val cursor = db.query(statement)
        val result = mutableListOf<User>()
        while (cursor.moveToNext()) {
            result.add(User(cursor.getInt(0), cursor.getString(1)))
        }
        cursor.close()
        return result
    }
}
```

### Kapt Vs KSP

| Аспект | kapt | KSP |
|--------|------|-----|
| API | Java Annotation Processing | Kotlin Symbol Processing |
| Скорость | Обычно медленнее для Kotlin-heavy проектов | Как правило быстрее за счёт работы с Kotlin-символами |
| Инкрементальная компиляция | Ограниченная поддержка | Лучшая поддержка, более точная инкрементальность |

**Рекомендация:** использовать KSP для новых проектов и при миграции, если это поддерживается версиями `Room` и Gradle.

### Валидация На Этапе Компиляции

```kotlin
@Query("SELECT * FROM usres") // ❌ Ошибка: таблица не существует (по данным Room о сущностях)
fun getAll(): List<User>

// Результат компиляции (Room annotation processor):
// error: There is a problem with the query: no such table: usres
```

**Преимущества:**
- Ошибки в SQL и несоответствия схемы (по информации, известной `Room` на этапе компиляции) обнаруживаются до запуска приложения.
- Type safety: сопоставление типов Kotlin/Java и колонок проверяется на этапе генерации кода.
- Нет runtime reflection — выше предсказуемость и, как правило, лучшая производительность.

> Ограничение: проверки основаны на описанных `@Entity`/`@Dao` и известных миграциях; динамически создаваемые таблицы или изменения вне модели `Room` могут привести к ошибкам уже в рантайме.

## Answer (EN)

**`Room`** generates code **at compile time** during the Gradle build via annotation processors (`kapt` or `KSP`). Generation happens in the relevant build tasks (annotation processing) before the APK/AAB is packaged, not at application runtime.

**`SQLite`** is an embedded database engine, not a code generation framework or annotation processor. It does not generate code for you; you either write SQL manually or use wrapper libraries (such as `Room`) that perform helper code generation at build time.

`Room`, as an abstraction layer over `SQLite`, uses annotation processing to generate implementations of DAO and `Database` classes, and to perform compile-time validation of entities and queries based on its known schema model.

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
// kapt (uses Java Annotation Processing API)
dependencies {
    kapt "androidx.room:room-compiler"
}

// KSP (uses Kotlin Symbol Processing API) ✅ recommended for new projects
dependencies {
    ksp "androidx.room:room-compiler"
}
```

> In practice, `Room` with KSP is typically faster and integrates better with Kotlin and incremental builds, but the "2x faster" figure is project-dependent and not a guaranteed constant.

1. **Generated Implementation** (roughly, in `build/generated/`) — simplified pseudocode
```kotlin
class UserDao_Impl : UserDao {
    override fun getAll(): List<User> {
        val statement = RoomSQLiteQuery.acquire("SELECT * FROM user", 0)
        // ✅ Generated code executes the query and maps the Cursor to User
        val cursor = db.query(statement)
        val result = mutableListOf<User>()
        while (cursor.moveToNext()) {
            result.add(User(cursor.getInt(0), cursor.getString(1)))
        }
        cursor.close()
        return result
    }
}
```

### Kapt Vs KSP

| Aspect | kapt | KSP |
|--------|------|-----|
| API | Java Annotation Processing | Kotlin Symbol Processing |
| Speed | Often slower for Kotlin-heavy projects | Typically faster due to direct Kotlin symbol access |
| Incremental | Limited support | Better, more precise incremental behavior |

**Recommendation:** Prefer KSP for new projects and when migrating, if supported by your Room/Gradle setup.

### Compile-Time Validation

```kotlin
@Query("SELECT * FROM usres") // ❌ Error: table doesn't exist (according to Room's known entities)
fun getAll(): List<User>

// Compilation result (from Room annotation processor):
// error: There is a problem with the query: no such table: usres
```

**Benefits:**
- SQL and schema mismatch errors (based on `Room`'s model) are caught before the app runs.
- Type safety: mapping between columns and Kotlin/Java types is checked during code generation.
- No runtime reflection, leading to more predictable and often better performance.

> Limitation: validation is based on `@Entity`/`@Dao` definitions and known migrations; dynamic schema changes or objects created outside `Room` can still cause runtime errors.

---

## Дополнительные Вопросы (RU)

- Как `Room` обрабатывает миграции схемы с использованием сгенерированного кода?
- Каковы компромиссы между инкрементальной компиляцией `kapt` и `KSP`?
- Чем compile-time валидация `Room` отличается от runtime-ошибок при работе с "сырым" `SQLite`?
- Могут ли annotation processors получать доступ к схеме базы данных на этапе компиляции?
- Как KSP достигает улучшения производительности по сравнению с `kapt` на практике?

## Follow-ups

- How does `Room` handle schema migrations with generated code?
- What are the trade-offs between `kapt` and `KSP` incremental compilation?
- How does `Room`'s compile-time validation differ from raw `SQLite` runtime errors?
- Can annotation processors access database schema at compile time?
- How does KSP achieve performance improvements over `kapt` in practice?

## Ссылки (RU)

- [[c-room]]
- Официальная документация по `Room` (developer.android.com)

## References

- [[c-room]]
- Official Android `Room` documentation (developer.android.com)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-room]]

### Предпосылки

- Базовые представления о работе annotation processing
- Понимание различий между генерацией кода на этапе компиляции и в рантайме

### Связанные

- [[q-dagger-framework-overview--android--hard]] — другой фреймворк, использующий annotation processing
- [[q-kapt-ksp-migration--android--medium]]
- [[q-kapt-vs-ksp--android--medium]]

### Продвинутое

- Реализация собственного annotation processor
- Архитектура `Room` в multi-module проектах

## Related Questions

### Prerequisites / Concepts

- [[c-room]]

### Prerequisites

- Basic annotation processing concepts
- Understanding of compile-time vs runtime code generation

### Related

- [[q-dagger-framework-overview--android--hard]] - Another annotation processing framework
- [[q-kapt-ksp-migration--android--medium]]
- [[q-kapt-vs-ksp--android--medium]]

### Advanced

- Custom annotation processor implementation
- Multi-module `Room` database architecture
