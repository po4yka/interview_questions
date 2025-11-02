---
id: kotlin-173
title: "Desugaring Android Java / Desugaring в Android"
aliases: [Desugaring Android, Desugaring Android Java]
topic: kotlin
subtopics: [compilation]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-coroutine-cancellation-mechanisms--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android, backward-compatibility, compilation, difficulty/medium, java, kotlin]
date created: Friday, October 31st 2025, 6:34:09 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# Desugaring В Android

# Question (EN)
> What is desugaring in Android and how does it work?

# Вопрос (RU)
> Что такое desugaring в Android и как он работает?

---

## Answer (EN)

Desugaring is the process of transforming modern language syntax into simpler code compatible with older platform versions. In Android, this means converting new Java and Kotlin features into code that works on legacy Android Runtime versions.

**What it enables:**
- Java 8+ features (lambdas, method references, default interface methods)
- Modern APIs (java.time, Stream API, Optional) on Android 5.0+ (API 21+)
- Writing modern code while maintaining backward compatibility

**How to enable:**
```gradle
android {
    compileOptions {
        coreLibraryDesugaringEnabled true
    }
}
dependencies {
    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.0.4'
}
```

**Trade-offs:**
- Adds 100-300 KB to APK size
- Slight performance overhead
- Minimum Android 5.0 (API 21)

**When to use:** Need java.time or Stream API on devices below Android 8.0, acceptable APK size increase.

---

## Ответ (RU)

**Desugaring** — это процесс преобразования современного синтаксиса языка программирования в более простой код, совместимый со старыми версиями платформы. В контексте Android это означает трансформацию новых возможностей Java и Kotlin в код, который может работать на устаревших версиях Android Runtime.

### Зачем Нужен Desugaring?

Android-устройства используют разные версии Android Runtime (ART или старую Dalvik VM). Многие устройства работают на Android 5.0 (API 21) или ниже, где нет поддержки современных Java API, таких как:

- Лямбды (lambda expressions)
- Stream API
- Optional
- java.time (LocalDate, LocalDateTime)
- Методы интерфейсов по умолчанию (default methods)
- try-with-resources

Desugaring позволяет использовать эти возможности, автоматически преобразуя их в совместимый код.

### Типы Desugaring

#### 1. Java 8+ Language Features Desugaring

Android Gradle Plugin автоматически поддерживает desugaring для:

```kotlin
// Лямбды
val list = listOf(1, 2, 3, 4, 5)
val filtered = list.filter { it > 2 } // Преобразуется в анонимный класс

// Method references
val names = listOf("Alice", "Bob", "Charlie")
names.forEach(::println) // Преобразуется в анонимный класс

// Default interface methods
interface Printer {
    fun print(message: String) {
        println("Printing: $message")
    }
}
```

**Что происходит под капотом:**

Лямбда `{ it > 2 }` преобразуется в:

```java
// До desugaring (Java 8+)
list.stream().filter(x -> x > 2)

// После desugaring (совместимо с Java 6/7)
list.stream().filter(new Predicate<Integer>() {
    @Override
    public boolean test(Integer x) {
        return x > 2;
    }
})
```

#### 2. Java 8+ API Desugaring (Core Library Desugaring)

Для использования современных Java API на старых Android версиях нужно включить Core Library Desugaring:

```gradle
// build.gradle (Module: app)
android {
    compileOptions {
        // Включаем поддержку Java 8
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8

        // Включаем Core Library Desugaring
        coreLibraryDesugaringEnabled true
    }
}

dependencies {
    // Добавляем библиотеку для desugaring
    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.0.4'
}
```

**Что это даёт:**

```kotlin
// java.time API (доступен с Android 8.0, API 26)
// Но благодаря desugaring работает на Android 4.0+ (API 21+)
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

fun getCurrentDate(): String {
    val now = LocalDate.now()
    val formatter = DateTimeFormatter.ofPattern("dd.MM.yyyy")
    return now.format(formatter)
}

// Stream API
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
val sum = numbers.stream()
    .filter { it % 2 == 0 }
    .mapToInt { it * it }
    .sum()

// Optional
val optional = Optional.of("Hello")
optional.ifPresent { println(it) }
```

### Как Работает Desugaring?

#### Этап 1: Компиляция

```
Kotlin/Java код → Kotlin Compiler → JVM Bytecode (Java 8+)
```

#### Этап 2: Desugaring

```
JVM Bytecode (Java 8+) → D8/R8 Desugar → DEX bytecode (совместимый с Android 5.0+)
```

#### Этап 3: Упаковка

```
DEX bytecode → APK/AAB
```

### Какие API Поддерживаются Через Core Library Desugaring?

| API | Минимальная версия Android | С Desugaring |
|-----|----------------------------|--------------|
| `java.time.*` | Android 8.0 (API 26) | Android 5.0 (API 21) |
| `java.util.stream.*` | Android 7.0 (API 24) | Android 5.0 (API 21) |
| `java.util.Optional` | Android 7.0 (API 24) | Android 5.0 (API 21) |
| `java.util.function.*` | Android 7.0 (API 24) | Android 5.0 (API 21) |

### Пример: Работа С Датами Без Desugaring

**Без Desugaring (старый способ):**

```kotlin
import java.util.Calendar
import java.text.SimpleDateFormat

fun getDateOldWay(): String {
    val calendar = Calendar.getInstance()
    val formatter = SimpleDateFormat("dd.MM.yyyy", Locale.getDefault())
    return formatter.format(calendar.time)
}

fun addDaysOldWay(days: Int): String {
    val calendar = Calendar.getInstance()
    calendar.add(Calendar.DAY_OF_MONTH, days)
    val formatter = SimpleDateFormat("dd.MM.yyyy", Locale.getDefault())
    return formatter.format(calendar.time)
}
```

**С Desugaring (современный способ):**

```kotlin
import java.time.LocalDate
import java.time.format.DateTimeFormatter

fun getDateModern(): String {
    val now = LocalDate.now()
    val formatter = DateTimeFormatter.ofPattern("dd.MM.yyyy")
    return now.format(formatter)
}

fun addDaysModern(days: Long): String {
    val future = LocalDate.now().plusDays(days)
    val formatter = DateTimeFormatter.ofPattern("dd.MM.yyyy")
    return future.format(formatter)
}
```

### Пример: Stream API

```kotlin
data class User(val name: String, val age: Int, val city: String)

fun filterUsersWithDesugaring() {
    val users = listOf(
        User("Alice", 25, "Moscow"),
        User("Bob", 30, "London"),
        User("Charlie", 22, "Moscow"),
        User("Diana", 28, "Paris")
    )

    // Stream API работает благодаря desugaring
    val moscowAdults = users.stream()
        .filter { it.city == "Moscow" }
        .filter { it.age >= 25 }
        .map { it.name }
        .collect(Collectors.toList())

    println(moscowAdults) // [Alice]
}
```

### Ограничения Desugaring

1. **Минимальная версия Android:** Core Library Desugaring работает с Android 5.0 (API 21) и выше.
2. **Увеличение размера APK:** Добавляет около 100-300 КБ к размеру APK.
3. **Не все API:** Некоторые Java 9+ API недоступны даже с desugaring.
4. **Производительность:** Небольшое снижение производительности из-за дополнительного слоя совместимости.

### Альтернативы Desugaring

#### 1. Использование ThreeTenABP (для java.time)

```gradle
dependencies {
    implementation 'com.jakewharton.threetenabp:threetenabp:1.4.6'
}
```

```kotlin
import org.threeten.bp.LocalDate
import org.threeten.bp.format.DateTimeFormatter

fun getDateWithThreeTen(): String {
    val now = LocalDate.now()
    val formatter = DateTimeFormatter.ofPattern("dd.MM.yyyy")
    return now.format(formatter)
}
```

#### 2. Повышение minSdkVersion

Если ваше приложение не поддерживает старые версии Android:

```gradle
android {
    defaultConfig {
        minSdkVersion 26 // Android 8.0+
    }
}
```

### Проверка Работы Desugaring

```kotlin
class DesugaringExample {
    // Проверка java.time
    fun testJavaTime() {
        val date = LocalDate.of(2024, 1, 1)
        println("Date: $date")
    }

    // Проверка Stream API
    fun testStreamAPI() {
        val numbers = listOf(1, 2, 3, 4, 5)
        val sum = numbers.stream()
            .filter { it > 2 }
            .mapToInt { it }
            .sum()
        println("Sum: $sum")
    }

    // Проверка Optional
    fun testOptional() {
        val optional = Optional.ofNullable("Hello")
        optional.ifPresent { println(it) }
    }
}
```

### Как Включить Desugaring: Полная Конфигурация

```gradle
// build.gradle (Module: app)
android {
    compileSdk 34

    defaultConfig {
        applicationId "com.example.myapp"
        minSdk 21  // Android 5.0+
        targetSdk 34
    }

    compileOptions {
        // Поддержка Java 8
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8

        // Включаем Core Library Desugaring
        coreLibraryDesugaringEnabled true
    }

    kotlinOptions {
        jvmTarget = "1.8"
    }
}

dependencies {
    // Core Library Desugaring
    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.0.4'
}
```

### Практический Пример: До И После Desugaring

**До Desugaring (Java 6/7 стиль):**

```kotlin
fun processUsersBefore(users: List<User>): List<String> {
    val result = mutableListOf<String>()
    for (user in users) {
        if (user.age >= 18 && user.city == "Moscow") {
            result.add(user.name.uppercase())
        }
    }
    return result
}

fun formatDateBefore(timestamp: Long): String {
    val calendar = Calendar.getInstance()
    calendar.timeInMillis = timestamp
    val sdf = SimpleDateFormat("dd.MM.yyyy HH:mm", Locale.getDefault())
    return sdf.format(calendar.time)
}
```

**После Desugaring (Java 8+ стиль):**

```kotlin
fun processUsersAfter(users: List<User>): List<String> {
    return users.stream()
        .filter { it.age >= 18 }
        .filter { it.city == "Moscow" }
        .map { it.name.uppercase() }
        .collect(Collectors.toList())
}

fun formatDateAfter(timestamp: Long): String {
    val instant = Instant.ofEpochMilli(timestamp)
    val dateTime = LocalDateTime.ofInstant(instant, ZoneId.systemDefault())
    val formatter = DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm")
    return dateTime.format(formatter)
}
```

### Вывод

Desugaring — это мощный инструмент, который позволяет:

1. Использовать современный синтаксис Java 8+ на старых Android-устройствах
2. Писать более читаемый и безопасный код
3. Избавиться от устаревших API вроде `Calendar` и `SimpleDateFormat`
4. Поддерживать широкий спектр устройств без жертв в качестве кода

**Когда использовать:**

- Если вам нужна поддержка Android 5.0+ (API 21+)
- Если вы хотите использовать `java.time`, Stream API, Optional
- Если размер APK не критичен (+100-300 КБ приемлемо)

**Когда НЕ использовать:**

- Если minSdkVersion уже 26+ (тогда desugaring не нужен)
- Если критичен размер APK
- Если используете альтернативные библиотеки (ThreeTenABP)

## Related Questions

-
- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
-
