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
related: [c-kotlin, q-coroutine-cancellation-mechanisms--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [android, backward-compatibility, compilation, difficulty/medium, java, kotlin]
---
# Вопрос (RU)
> Что такое desugaring в Android и как он работает?

---

## Ответ (RU)

**Desugaring** — это процесс преобразования более современных конструкций языка и стандартной библиотеки в более примитивный байткод и/или вызовы вспомогательных библиотек, совместимые с ранними версиями Android Runtime. В контексте Android обычно выделяют:

- desugaring языковых возможностей Java 8+;
- Core Library Desugaring — подмена части Java стандартной библиотеки (jdk8+ API) на реализации из `desugar_jdk_libs`.

Kotlin-компилятор сам по себе компилирует Kotlin-код в байткод, совместимый с выбранным `jvmTarget` (часто 1.8); на Android дальнейший desugaring языка/библиотек делает D8/R8.

### Зачем Нужен Desugaring?

Android-устройства используют разные версии Android Runtime (ART или старую Dalvik VM). Часть устройств всё ещё работает на версиях, где нет поддержки многих Java 8+ языковых конструкций и стандартных API:

- Java-лямбды и method references (на уровне Java-байткода);
- default и static методы в интерфейсах;
- `java.time` (официально доступен только с Android 8.0 / API 26);
- `java.util.stream.*`;
- `java.util.Optional`;
- другие API Java 8+.

Desugaring позволяет использовать эти возможности при таргетинге minSdk 21+, автоматически преобразуя их в совместимый DEX-код и подключая нужные реализации библиотек.

### Типы Desugaring

#### 1. Java 8+ Language Features Desugaring

Android Gradle Plugin выполняет desugaring языковых возможностей Java 8+ на этапе D8/R8 для проекта с `minSdk < 24` (и соответствующими `compileOptions`). Это касается кода на Java. Kotlin-лямбды и inline-функции обрабатываются самим Kotlin-компилятором и не требуют отдельного Java-лямбда-desugaring.

Пример (идея для Java-кода):

```java
// Java 8 стиль
list.stream().filter(x -> x > 2);

// После desugaring для ранних API
list.stream().filter(new Predicate<Integer>() {
    @Override
    public boolean test(Integer x) {
        return x > 2;
    }
});
```

Пример Kotlin-кода, использующего лямбду (важно не путать с Java-лямбдами):

```kotlin
val list = listOf(1, 2, 3, 4, 5)
val filtered = list.filter { it > 2 } // Обрабатывается Kotlin-компилятором; D8 лишь переводит байткод в DEX

val names = listOf("Alice", "Bob", "Charlie")
names.forEach(::println)

interface Printer {
    fun print(message: String) {
        println("Printing: $message")
    }
}
```

Ключевой момент: на Android desugaring языка в D8/R8 гарантирует, что Java 8+ конструкции будут работать на устройствах с `minSdk 21+`, даже если VM не поддерживает их нативно.

#### 2. Java 8+ API Desugaring (Core Library Desugaring)

Для использования современных Java API (например, `java.time`, `java.util.stream`, `java.util.function`, `Optional`) на устройствах с `minSdk 21+` включают Core Library Desugaring:

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
    // Библиотека для Core Library Desugaring
    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.0.4'
}
```

**Что это даёт (для minSdk 21+):**

```kotlin
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.Optional
import java.util.stream.Collectors

fun getCurrentDate(): String {
    val now = LocalDate.now()
    val formatter = DateTimeFormatter.ofPattern("dd.MM.yyyy")
    return now.format(formatter)
}

// Использование Stream API через Java Streams
fun sumOfEvenSquares(numbers: List<Int>): Int {
    return numbers.stream() // Kotlin-список представлен как java.util.List
        .filter { it % 2 == 0 }
        .mapToInt { it * it }
        .sum()
}

fun printOptional() {
    val optional = Optional.of("Hello")
    optional.ifPresent { println(it) }
}
```

`desugar_jdk_libs` поставляет реализации нужных API, и D8/R8 перенаправляет вызовы на них.

### Как Работает Desugaring?

Упрощённо для Kotlin/Java-проекта под Android:

#### Этап 1: Компиляция

```
Kotlin/Java код → Kotlin/Java Compiler → JVM bytecode (обычно Java 8)
```

#### Этап 2: Desugaring + DEX

```
JVM bytecode (Java 8) → D8/R8: language desugaring + перенаправление на desugar_jdk_libs → DEX bytecode (для minSdk 21+)
```

#### Этап 3: Упаковка

```
DEX bytecode + desugar_jdk_libs → APK/AAB
```

### Какие API Поддерживаются Через Core Library Desugaring?

(актуальные диапазоны зависят от версии `desugar_jdk_libs`, ниже типичный пример для minSdk 21+):

| API | Минимальная версия Android без desugaring | С Core Library Desugaring |
|-----|-------------------------------------------|----------------------------|
| `java.time.*` | Android 8.0 (API 26) | Android 5.0+ (API 21+) |
| `java.util.stream.*` | Android 7.0 (API 24) | Android 5.0+ (API 21+) |
| `java.util.Optional` | Android 7.0 (API 24) | Android 5.0+ (API 21+) |
| `java.util.function.*` | Android 7.0 (API 24) | Android 5.0+ (API 21+) |

Важно: официально поддерживаемый Core Library Desugaring ориентирован на `minSdk 21+`.

### Пример: Работа С Датами Без Desugaring

**Без Core Library Desugaring (старый способ, совместим с minSdk < 21):**

```kotlin
import java.util.Calendar
import java.text.SimpleDateFormat
import java.util.Locale

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

**С Core Library Desugaring (современный способ при minSdk 21+):**

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
import java.util.stream.Collectors

data class User(val name: String, val age: Int, val city: String)

fun filterUsersWithDesugaring() {
    val users = listOf(
        User("Alice", 25, "Moscow"),
        User("Bob", 30, "London"),
        User("Charlie", 22, "Moscow"),
        User("Diana", 28, "Paris")
    )

    // Stream API работает благодаря Core Library Desugaring (minSdk 21+)
    val moscowAdults = users.stream()
        .filter { it.city == "Moscow" }
        .filter { it.age >= 25 }
        .map { it.name }
        .collect(Collectors.toList())

    println(moscowAdults) // [Alice]
}
```

### Ограничения Desugaring

1. Минимальная версия Android: официально поддерживаемый Core Library Desugaring рассчитан на `minSdk 21+`.
2. Увеличение размера APK: добавляет порядка 100–300 КБ к размеру APK/AAB (в зависимости от фич и R8).
3. Покрытие API: не все API Java 9+ и части Java 8+ доступны; нужно проверять документацию `desugar_jdk_libs`.
4. Производительность: возможен небольшой overhead из-за дополнительного слоя совместимости и реализаций поверх рантайма.

### Альтернативы Desugaring

#### 1. Использование ThreeTenABP (для java.time, особенно при minSdk < 21)

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

Если ваше приложение не поддерживает старые версии Android и `minSdk >= 26`, большинство нужных Java 8 API уже доступны нативно, и Core Library Desugaring может быть не нужен:

```gradle
android {
    defaultConfig {
        minSdk 26 // Android 8.0+
    }
}
```

### Проверка Работы Desugaring

```kotlin
import java.time.LocalDate
import java.util.Optional

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
        // Поддержка Java 8+
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8

        // Включаем Core Library Desugaring для Java 8+ API
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

**До (без Core Library Desugaring, Java 6/7 стиль):**

```kotlin
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

data class User(val name: String, val age: Int, val city: String)

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

**После (с Core Library Desugaring, Java 8+ стиль при minSdk 21+):**

```kotlin
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.stream.Collectors

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
    val formatter = DateTimeFormatter.ofPattern("dd.MM.yYYY HH:mm")
    return dateTime.format(formatter)
}
```

### Вывод

Desugaring в Android — это механизм, позволяющий:

1. Использовать Java 8+ языковые фичи при таргетинге `minSdk 21+`, даже если рантайм не поддерживает их нативно.
2. Использовать часть Java 8+ API (через Core Library Desugaring) — `java.time`, Streams, `Optional`, `java.util.function` и др.
3. Писать более читаемый и безопасный код, уменьшая зависимость от устаревших API вроде `Calendar` и `SimpleDateFormat`.
4. Сохранить поддержку широкого спектра устройств за счёт совместимости на уровне DEX и дополнительных библиотек.

Когда использовать:

- Если `minSdk 21+` и вы хотите использовать `java.time`, Stream API, Optional и другие Java 8+ API.
- Если приемлем небольшой рост размера APK.

Когда не использовать или он не критичен:

- Если `minSdk >= 26` и нужные API доступны нативно.
- Если критичен каждый килобайт и вы не используете соответствующие Java 8+ API.
- Если вы используете альтернативы (например, ThreeTenABP) для более низких minSdk.

---

# Question (EN)
> What is desugaring in Android and how does it work?

## Answer (EN)

Desugaring in Android is the process of converting newer Java 8+ language constructs and selected standard library APIs into simpler bytecode and/or calls to helper libraries so that they are compatible with older Android runtimes (ART/Dalvik and DEX). It lets you write modern code while still targeting lower API levels (commonly `minSdk 21+`), and is implemented primarily by D8/R8 based on your Gradle configuration.

### Why Desugaring Is Needed

Android devices run different versions of the runtime (ART or the older Dalvik VM), and many of them originally lacked native support for key Java 8+ features. Without desugaring, the following would not work (or would be inconsistently available) on older API levels:

- Java lambdas and method references (at the Java bytecode level),
- default and static interface methods,
- `java.time` (formally only on Android 8.0 / API 26+),
- `java.util.stream.*`,
- `java.util.Optional`,
- other Java 8+ APIs.

Desugaring bridges this gap: it rewrites language features and selected APIs so that they run on older Android versions while you keep a modern code style and a low `minSdk`.

### Types of Desugaring

#### 1. Java 8+ Language Features Desugaring

- For Java sources (especially with `minSdk < 24`), Java 8+ language constructs such as lambdas, method references, default methods, and static interface methods are rewritten into an older-style representation that is executable on older runtimes.
- Kotlin lambdas and inline functions are lowered by the Kotlin compiler itself; D8/R8 only converts that resulting bytecode to DEX and optimizes it, so no separate Java-lambda desugaring step is required for Kotlin.

Example (Java):

```java
// Java 8 style
list.stream().filter(x -> x > 2);

// Conceptual desugared form for older runtimes
list.stream().filter(new Predicate<Integer>() {
    @Override
    public boolean test(Integer x) {
        return x > 2;
    }
});
```

Example (Kotlin lambdas):

```kotlin
val list = listOf(1, 2, 3, 4, 5)
val filtered = list.filter { it > 2 } // Lowered by the Kotlin compiler; D8 only converts to DEX

val names = listOf("Alice", "Bob", "Charlie")
names.forEach(::println)

interface Printer {
    fun print(message: String) {
        println("Printing: $message")
    }
}
```

Key idea: language desugaring ensures Java 8+ constructs run correctly even when the VM does not natively support them.

#### 2. Java 8+ API Desugaring (Core Library Desugaring)

To use modern Java APIs such as `java.time`, `java.util.stream`, `java.util.function`, `java.util.Optional` on devices with `minSdk 21+`, you enable Core Library Desugaring. D8/R8 rewrites calls so they are routed to compatible implementations in `desugar_jdk_libs`.

Configuration example:

```gradle
// build.gradle (Module: app)
android {
    compileOptions {
        // Enable Java 8
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8

        // Enable Core Library Desugaring
        coreLibraryDesugaringEnabled true
    }
}

dependencies {
    // Core Library Desugaring runtime
    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.0.4'
}
```

What this enables (for `minSdk 21+`):

```kotlin
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.Optional
import java.util.stream.Collectors

fun getCurrentDate(): String {
    val now = LocalDate.now()
    val formatter = DateTimeFormatter.ofPattern("dd.MM.yyyy")
    return now.format(formatter)
}

// Stream API backed by Core Library Desugaring
fun sumOfEvenSquares(numbers: List<Int>): Int {
    return numbers.stream()
        .filter { it % 2 == 0 }
        .mapToInt { it * it }
        .sum()
}

fun printOptional() {
    val optional = Optional.of("Hello")
    optional.ifPresent { println(it) }
}
```

`desugar_jdk_libs` provides the implementations; D8/R8 redirects the calls.

### How Desugaring Works (Pipeline)

1. Kotlin/Java code → Kotlin/Java compiler → JVM bytecode (usually targeting Java 8).
2. JVM bytecode → D8/R8:
   - performs language desugaring for Java 8+ features,
   - rewrites supported Java 8+ API calls to `desugar_jdk_libs`,
   - outputs DEX bytecode compatible with the configured `minSdk`.
3. DEX bytecode + `desugar_jdk_libs` → packaged into APK/AAB.

### Supported APIs via Core Library Desugaring (API Mapping)

Typical mapping (exact support depends on `desugar_jdk_libs` version):

- `java.time.*`
  - Without desugaring: officially from Android 8.0 (API 26).
  - With Core Library Desugaring: usable from Android 5.0+ (API 21+).
- `java.util.stream.*`
  - Without desugaring: from Android 7.0 (API 24).
  - With Core Library Desugaring: usable from Android 5.0+ (API 21+).
- `java.util.Optional`
  - Without desugaring: from Android 7.0 (API 24).
  - With Core Library Desugaring: usable from Android 5.0+ (API 21+).
- `java.util.function.*`
  - Without desugaring: from Android 7.0 (API 24).
  - With Core Library Desugaring: usable from Android 5.0+ (API 21+).

Official Core Library Desugaring support is focused on `minSdk 21+`.

### Example: Working with Dates Without vs With Desugaring

Without Core Library Desugaring (legacy, suitable for very low `minSdk`):

```kotlin
import java.util.Calendar
import java.text.SimpleDateFormat
import java.util.Locale

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

With Core Library Desugaring enabled (`minSdk 21+`, modern style):

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

### Example: Stream API

```kotlin
import java.util.stream.Collectors

data class User(val name: String, val age: Int, val city: String)

fun filterUsersWithDesugaring() {
    val users = listOf(
        User("Alice", 25, "Moscow"),
        User("Bob", 30, "London"),
        User("Charlie", 22, "Moscow"),
        User("Diana", 28, "Paris")
    )

    // Stream API works on minSdk 21+ when Core Library Desugaring is enabled
    val moscowAdults = users.stream()
        .filter { it.city == "Moscow" }
        .filter { it.age >= 25 }
        .map { it.name }
        .collect(Collectors.toList())

    println(moscowAdults) // [Alice]
}
```

### Limitations of Desugaring

1. Minimum API: Core Library Desugaring is officially supported for `minSdk 21+`.
2. APK size: typically adds about 100–300 KB to APK/AAB size (depending on usage and R8 shrinking).
3. API coverage: not all Java 8+/9+ APIs are available; always check the `desugar_jdk_libs` documentation.
4. Performance: small overhead is possible due to the compatibility layer instead of native implementations.

### Alternatives to Desugaring

#### 1. Using ThreeTenABP (for `java.time`, especially when `minSdk < 21`)

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

#### 2. Increasing minSdkVersion

If your app targets only newer Android versions and `minSdk >= 26`, most required Java 8 APIs are available natively and Core Library Desugaring may not be needed:

```gradle
android {
    defaultConfig {
        minSdk 26 // Android 8.0+
    }
}
```

### Verifying Desugaring Works

```kotlin
import java.time.LocalDate
import java.util.Optional

class DesugaringExample {
    fun testJavaTime() {
        val date = LocalDate.of(2024, 1, 1)
        println("Date: $date")
    }

    fun testStreamAPI() {
        val numbers = listOf(1, 2, 3, 4, 5)
        val sum = numbers.stream()
            .filter { it > 2 }
            .mapToInt { it }
            .sum()
        println("Sum: $sum")
    }

    fun testOptional() {
        val optional = Optional.ofNullable("Hello")
        optional.ifPresent { println(it) }
    }
}
```

### How to Enable Desugaring: Full Configuration

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
        // Java 8+ language features
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8

        // Enable Core Library Desugaring for Java 8+ APIs
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

### Practical Before/After Example

Before (no Core Library Desugaring, Java 6/7 style):

```kotlin
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

data class User(val name: String, val age: Int, val city: String)

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

After (with Core Library Desugaring, Java 8+ style on `minSdk 21+`):

```kotlin
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.stream.Collectors

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
    val formatter = DateTimeFormatter.ofPattern("dd.MM.yYYY HH:mm")
    return dateTime.format(formatter)
}
```

### Summary

Desugaring in Android allows you to:

1. Use Java 8+ language features on devices that do not natively support them.
2. Use selected Java 8+ APIs (via Core Library Desugaring), such as `java.time`, Streams, `Optional`, and `java.util.function`.
3. Keep your code modern, readable, and safer while still supporting a wide range of devices.

Use desugaring when:

- `minSdk 21+` and you want modern Java 8+ APIs like `java.time`, Streams, `Optional`.
- The small size increase (~100–300 KB) is acceptable.

It is less critical when:

- `minSdk >= 26` and the required APIs are available natively.
- Every kilobyte of APK size matters and you are not using those APIs.
- You rely on alternatives such as ThreeTenABP for very low `minSdk`.

## Дополнительные вопросы (RU)

- В чем разница между language desugaring и Core Library Desugaring?
- Как взаимодействует Java/Kotlin desugaring с Kotlin-компилятором и `jvmTarget`?
- Какие типичные подводные камни (рост размера APK, частичное покрытие API, требования к minSdk)?

## Follow-ups (EN)

- What is the difference between language desugaring and Core Library Desugaring?
- How does Java/Kotlin desugaring interact with the Kotlin compiler and `jvmTarget`?
- What are common pitfalls (APK size growth, partial API coverage, `minSdk` constraints)?

## Ссылки (RU)

- [[c-kotlin]]

## References (EN)

- https://kotlinlang.org/docs/home.html

## Связанные вопросы (RU)

- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]

## Related Questions (EN)

- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
