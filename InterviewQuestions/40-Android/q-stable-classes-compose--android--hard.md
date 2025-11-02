---
id: android-263
title: "Stable Classes Compose / Stable Классы Compose"
aliases: ["Stable Classes Compose", "Stable Классы Compose"]
topic: android
subtopics: [performance-rendering, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/performance-rendering, android/ui-compose, difficulty/hard, immutability, jetpack-compose, recomposition, stability]
date created: Saturday, November 1st 2025, 1:24:29 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Вопрос (RU)

Какие классы будут автоматически выводиться как stable в Jetpack Compose?

# Question (EN)

Which classes are automatically inferred as stable in Jetpack Compose?

---

## Ответ (RU)

В Jetpack Compose классы автоматически считаются **stable**, если они:
- **Data классы** с неизменяемыми свойствами (`val`)
- **Все свойства имеют stable типы** (String, Int, Float и т.д.)
- **Не содержат изменяемых коллекций** (MutableList, MutableMap)

### Что Такое Stability?

**Stability** определяет, может ли Compose **пропустить рекомпозицию**, если параметры Composable не изменились.

**Stable** означает:
- Значение **не меняется спонтанно**
- `equals()` всегда возвращает одинаковый результат для одних и тех же значений
- Compose может **безопасно пропустить рекомпозицию**, если параметры равны

### Автоматически Stable Типы

**Примитивы**: Int, Long, Float, Double, Boolean, Char, String

**Immutable data классы**:
```kotlin
// ✅ Автоматически stable
data class User(
    val id: String,
    val name: String,
    val age: Int
)

@Composable
fun UserCard(user: User) {
    // Compose пропускает рекомпозицию, если user не изменился
    Text("${user.name}, ${user.age}")
}
```

### Когда Классы НЕ Stable

**1. Изменяемые свойства (var)**:
```kotlin
// ❌ НЕ stable - есть var
data class User(
    val id: String,
    var name: String  // изменяемое свойство
)
```

**2. Изменяемые коллекции**:
```kotlin
// ❌ НЕ stable
data class Team(
    val members: MutableList<User>
)

// ✅ Stable
data class Team(
    val members: List<User>  // неизменяемый интерфейс
)
```

### Как Сделать Класс Stable

**Вариант 1: Data классы с val**:
```kotlin
data class Product(
    val id: String,
    val name: String,
    val price: Double
)
```

**Вариант 2: Аннотация @Stable**:
```kotlin
@Stable
class Settings(private val _darkMode: Boolean) {
    val darkMode: Boolean get() = _darkMode

    override fun equals(other: Any?): Boolean =
        other is Settings && other._darkMode == _darkMode

    override fun hashCode(): Int = _darkMode.hashCode()
}
```

### Влияние На Производительность

```kotlin
// Stable параметр
@Composable
fun UserCard(user: User) {  // User stable
    Text(user.name)
}
// ✅ Compose пропускает рекомпозицию, если user не изменился

// Unstable параметр
@Composable
fun UserCard(user: UnstableUser) {
    Text(user.name)
}
// ❌ Compose НЕ МОЖЕТ пропустить рекомпозицию
```

### Проверка Stability

Включите compiler metrics в `build.gradle.kts`:
```kotlin
android {
    kotlinOptions {
        freeCompilerArgs += listOf(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=${project.buildDir}/compose_metrics"
        )
    }
}
```

Вывод покажет:
```
stable class User {
  stable val id: String
  stable val name: String
}

unstable class UserProfile {
  unstable var name: String  // ← Проблема!
}
```

---

## Answer (EN)

Classes in Jetpack Compose are automatically considered **stable** if they are:
- **Data classes** with immutable properties (`val`)
- **All properties are stable types** (String, Int, Float, etc.)
- **No mutable collections** (MutableList, MutableMap)

### What is Stability?

**Stability** determines whether Compose can **skip recomposition** when parameters haven't changed.

**Stable** means:
- The value **doesn't change spontaneously**
- `equals()` always returns the same result for the same values
- Compose can **safely skip recomposition** if parameters are equal

### Automatically Stable Types

**Primitives**: Int, Long, Float, Double, Boolean, Char, String

**Immutable data classes**:
```kotlin
// ✅ Automatically stable
data class User(
    val id: String,
    val name: String,
    val age: Int
)

@Composable
fun UserCard(user: User) {
    // Compose skips recomposition if user hasn't changed
    Text("${user.name}, ${user.age}")
}
```

### When Classes Are NOT Stable

**1. Mutable properties (var)**:
```kotlin
// ❌ NOT stable - has var
data class User(
    val id: String,
    var name: String  // mutable property
)
```

**2. Mutable collections**:
```kotlin
// ❌ NOT stable
data class Team(
    val members: MutableList<User>
)

// ✅ Stable
data class Team(
    val members: List<User>  // immutable interface
)
```

### Making Classes Stable

**Option 1: Data classes with val**:
```kotlin
data class Product(
    val id: String,
    val name: String,
    val price: Double
)
```

**Option 2: @Stable annotation**:
```kotlin
@Stable
class Settings(private val _darkMode: Boolean) {
    val darkMode: Boolean get() = _darkMode

    override fun equals(other: Any?): Boolean =
        other is Settings && other._darkMode == _darkMode

    override fun hashCode(): Int = _darkMode.hashCode()
}
```

### Performance Impact

```kotlin
// Stable parameter
@Composable
fun UserCard(user: User) {  // User is stable
    Text(user.name)
}
// ✅ Compose skips recomposition if user hasn't changed

// Unstable parameter
@Composable
fun UserCard(user: UnstableUser) {
    Text(user.name)
}
// ❌ Compose CANNOT skip recomposition
```

### Checking Stability

Enable compiler metrics in `build.gradle.kts`:
```kotlin
android {
    kotlinOptions {
        freeCompilerArgs += listOf(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:metricsDestination=${project.buildDir}/compose_metrics"
        )
    }
}
```

Output shows:
```
stable class User {
  stable val id: String
  stable val name: String
}

unstable class UserProfile {
  unstable var name: String  // ← Problem!
}
```

---

## Follow-ups

1. What happens to recomposition if a class contains a stable property wrapped in an unstable container?
2. How does @Immutable differ from @Stable annotation?
3. Can you make a class with private var properties stable using @Stable?
4. How do kotlinx.collections.immutable types improve performance compared to standard List?
5. What's the performance difference between unstable and stable parameters in a deeply nested Composable tree?

## References

- [[c-compose-recomposition]] - Compose recomposition fundamentals
- [[c-compose-stability]] - Compose stability concepts
- [Compose Performance Guide](https://developer.android.com/jetpack/compose/performance)
- [Compose Compiler Metrics](https://github.com/androidx/androidx/blob/androidx-main/compose/compiler/design/compiler-metrics.md)

## Related Questions

### Prerequisites
- [[q-jetpack-compose-basics--android--medium]] - Compose fundamentals
- [[q-compose-recomposition--android--medium]] - Recomposition basics

### Related
- [[q-compose-stability-skippability--android--hard]] - Stability and skippability
- [[q-stable-annotation-compose--android--hard]] - @Stable annotation details
- [[q-compose-performance-optimization--android--hard]] - Performance optimization

### Advanced
- [[q-compose-slot-table-recomposition--android--hard]] - Slot table internals
- [[q-compose-compiler-plugin--android--hard]] - Analyzing compiler reports

