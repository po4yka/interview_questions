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

# Question (EN)
> What is desugaring in Android and how does it work?

---

## Ответ (RU)

**Desugaring** — это процесс преобразования более современных конструкций языка и стандартной библиотеки в более примитивный байткод и/или вызовы вспомогательных библиотек, совместимые с более старыми реализациями Android Runtime (ART/Dalvik) и форматом DEX.

В контексте Android обычно выделяют:

- desugaring языковых возможностей Java 8+ (language desugaring);
- Core Library Desugaring — подмена части Java стандартной библиотеки (Java 8+ API) на реализации из `desugar_jdk_libs` (API desugaring).

Kotlin-компилятор сам по себе компилирует Kotlin-код в байткод, совместимый с выбранным `jvmTarget` (часто `1.8`). На Android дальнейший desugaring и преобразование в DEX делает D8/R8 (для Java-байткода и перенаправления вызовов API).

Важно различать:
- language desugaring (языковые конструкции Java 8+) — работает для низких `minSdk` (ниже 21 тоже),
- Core Library Desugaring (Java 8+ API) — официально поддерживается для проектов с `minSdk 21+`.

### Зачем Нужен Desugaring?

Android-устройства используют разные версии Android Runtime (ART или старую Dalvik VM). Исторически часть устройств не имела поддержки многих Java 8+ языковых конструкций и стандартных API.

Без desugaring было бы проблематично использовать:

- Java-лямбды и method references (как фичу байткода Java 8);
- default и static методы в интерфейсах;
- `java.time` (официально доступен нативно с Android 8.0 / API 26);
- `java.util.stream.*`;
- `java.util.Optional`;
- другие Java 8+ API.

Desugaring позволяет использовать эти возможности при таргетинге старых API-уровней, автоматически преобразуя их в совместимый DEX-код и/или подключая нужные реализации библиотек.

### Типы Desugaring

#### 1. Java 8+ Language Features Desugaring

Android Gradle Plugin через D8/R8 выполняет desugaring Java 8+ языковых возможностей на этапе преобразования JVM-байткода в DEX, если таргетируемые устройства не поддерживают их нативно.

Это касается Java-кода: лямбды, method references, default/static методы в интерфейсах и т.п. переписываются в эквивалентные конструкции, понятные старому рантайму.

Kotlin-лямбды, inline-функции и другие фичи Kotlin понижаются самим Kotlin-компилятором в обычные анонимные классы/вызовы (в соответствии с `jvmTarget`), а D8/R8 затем просто оптимизирует и конвертирует этот байткод в DEX.

Упрощённый пример для Java (идея именно language desugaring):

```java
// Java 8 стиль (лямбда)
Runnable r = () -> System.out.println("Hello");

// Концептуально после desugaring
Runnable r2 = new Runnable() {
    @Override
    public void run() {
        System.out.println("Hello");
    }
};
```

Ключевой момент: language desugaring обеспечивает поддержку Java 8+ языковых конструкций на устройствах, чьи VM их нативно не понимают (при корректной конфигурации Gradle/AGP).

#### 2. Java 8+ API Desugaring (Core Library Desugaring)

Для использования современных Java API (например, `java.time`, `java.util.stream`, `java.util.function`, `Optional`) на устройствах с `minSdk 21+` включают Core Library Desugaring. В этом режиме D8/R8 переписывает вызовы этих API на реализации из `desugar_jdk_libs`.

Пример конфигурации:

```gradle
// build.gradle (Module: app)
android {
    compileOptions {
        // Включаем поддержку Java 8+ синтаксиса
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8

        // Включаем Core Library Desugaring для Java 8+ API
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

// Пример Stream API обычно пишут в Java-коде; в Kotlin аналогичное делают через функции коллекций.
// Здесь иллюстрируем концепцию для Java Streams (предполагается Java-код или соответствующий interop):
fun sumOfEvenSquaresJavaStyle(numbers: java.util.List<Int>): Int {
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

`desugar_jdk_libs` поставляет реализации нужных API, а D8/R8 переписывает байткод так, чтобы вызовы шли на них.

### Как Работает Desugaring?

Упрощённо для Kotlin/Java-проекта под Android:

#### Этап 1: Компиляция

```text
Kotlin/Java код → Kotlin/Java Compiler → JVM bytecode (обычно Java 8)
```

#### Этап 2: Desugaring + DEX

```text
JVM bytecode → D8/R8:
  - language desugaring для Java 8+ фич (где нужно),
  - переписывание поддерживаемых Java 8+ API на desugar_jdk_libs (если coreLibraryDesugaringEnabled),
  - вывод DEX bytecode под заданный minSdk.
```

#### Этап 3: Упаковка

```text
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

Важно: ограничение по `minSdk 21+` относится именно к Core Library Desugaring (API), а не к language desugaring Java.

### Пример: Работа С Датами Без Desugaring

**Без Core Library Desugaring (старый способ, подходит и для очень низких minSdk):**

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

// Для чистого Kotlin обычно используют функции стандартной библиотеки вместо Java Streams.
// Здесь пример показывает, что при Core Library Desugaring Java Streams могут работать на API 21+,
// если они используются из Java-кода или через Java-коллекции.
fun filterUsersWithDesugaring(users: java.util.List<User>) {
    val moscowAdults = users.stream()
        .filter { it.city == "Moscow" }
        .filter { it.age >= 25 }
        .map { it.name }
        .collect(Collectors.toList())

    println(moscowAdults)
}
```

### Ограничения Desugaring

1. Core Library Desugaring официально поддерживается для проектов с `minSdk 21+`.
2. Увеличение размера APK: обычно добавляет порядка 100–300 КБ к размеру APK/AAB (в зависимости от используемых API и R8).
3. Покрытие API: поддерживается только определённый поднабор Java 8+ (и некоторых более новых) API; нужно проверять документацию `desugar_jdk_libs`.
4. Производительность: возможен небольшой overhead из-за дополнительного слоя совместимости по сравнению с нативными реализациями.

### Альтернативы Desugaring

#### 1. Использование ThreeTenABP (для `java.time`, Особенно При Очень Низком minSdk)

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

Если приложение поддерживает только новые версии Android и `minSdk >= 26`, большинство нужных Java 8 API доступны нативно, и Core Library Desugaring может быть не нужен:

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

    // Проверка Stream API (для Java-коллекций)
    fun testStreamAPI(numbers: java.util.List<Int>) {
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
        // Java 8+ language features
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
    val sdf = SimpleDateFormat("dd.MM.yYYY HH:mm", Locale.getDefault())
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

fun processUsersAfter(users: java.util.List<User>): java.util.List<String> {
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
    return dateTime.format(dateTime)
}
```

### Вывод

Desugaring в Android — это механизм, позволяющий:

1. Использовать Java 8+ языковые фичи даже на устройствах, где рантайм их нативно не поддерживает (language desugaring).
2. Использовать часть Java 8+ API (через Core Library Desugaring) — `java.time`, Streams, `Optional`, `java.util.function` и др. при `minSdk 21+`.
3. Писать более читаемый и безопасный код, уменьшая зависимость от устаревших API вроде `Calendar` и `SimpleDateFormat`.
4. Сохранить поддержку широкого спектра устройств за счёт преобразований на уровне байткода и дополнительных библиотек.

Когда использовать:

- Если `minSdk 21+` и вы хотите использовать `java.time`, Stream API, Optional и другие Java 8+ API.
- Если приемлем небольшой рост размера APK.

Когда он менее критичен или может быть не нужен:

- Если `minSdk >= 26` и нужные API доступны нативно.
- Если критичен каждый килобайт и вы не используете соответствующие Java 8+ API.
- Если вы используете альтернативы (например, ThreeTenABP) для очень низких `minSdk`.

---

## Answer (EN)

In Android, desugaring is the process of transforming newer Java 8+ language constructs and selected standard library APIs into simpler bytecode and/or calls to helper libraries so that they are compatible with older Android runtimes (ART/Dalvik) and the DEX format.

In practice this includes two related mechanisms:

- Java 8+ language desugaring: rewriting Java 8+ language features to older-style constructs.
- Core Library Desugaring: providing alternative implementations of certain Java 8+ library APIs via `desugar_jdk_libs` and rewriting calls to them.

Kotlin is compiled by the Kotlin compiler to JVM bytecode targeting a given `jvmTarget` (commonly `1.8`). On Android, D8/R8 then takes that bytecode (from both Java and Kotlin), performs desugaring where applicable, and converts it to DEX.

Important distinction:
- Language desugaring (Java 8+ syntax/features) works for low `minSdk` values.
- Core Library Desugaring (Java 8+ APIs) is officially supported for projects with `minSdk 21+`.

### Why Desugaring Is Needed

Android devices run different runtime versions, and many older releases did not natively support important Java 8+ features. Without desugaring, the following would not work reliably on older API levels:

- Java lambdas and method references (as Java 8 bytecode features),
- default and static interface methods,
- `java.time` (natively from Android 8.0 / API 26),
- `java.util.stream.*`,
- `java.util.Optional`,
- other Java 8+ APIs.

Desugaring bridges this gap by rewriting language constructs and (optionally) selected APIs so you can keep a modern style while targeting lower API levels.

### Types of Desugaring

#### 1. Java 8+ Language Features Desugaring

For Java sources, when targeting devices that do not support Java 8 features natively, D8/R8 performs language desugaring during bytecode-to-DEX conversion:

- lambdas,
- method references,
- default/static interface methods,
- etc.

These are lowered to constructs executable on older runtimes.

Kotlin lambdas and inline functions are lowered by the Kotlin compiler itself based on `jvmTarget`. D8/R8 then optimizes and converts the resulting JVM bytecode to DEX; there is no separate "Java lambda" desugaring step for Kotlin language features.

Conceptual Java example (focusing on language desugaring):

```java
// Java 8 style lambda
Runnable r = () -> System.out.println("Hello");

// Conceptually desugared form
Runnable r2 = new Runnable() {
    @Override
    public void run() {
        System.out.println("Hello");
    }
};
```

Key idea: language desugaring enables Java 8+ constructs to run even when the underlying VM does not support them natively, assuming proper Gradle/AGP configuration.

#### 2. Java 8+ API Desugaring (Core Library Desugaring)

To use modern Java APIs such as `java.time`, `java.util.stream`, `java.util.function`, `java.util.Optional` on devices when your project has `minSdk 21+`, you can enable Core Library Desugaring. D8/R8 then rewrites those API calls to implementations shipped in `desugar_jdk_libs`.

Configuration example:

```gradle
// build.gradle (Module: app)
android {
    compileOptions {
        // Enable Java 8+ language level
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8

        // Enable Core Library Desugaring for Java 8+ APIs
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

// Java Streams are typically used from Java code; here we show a Java-style example:
fun sumOfEvenSquaresJavaStyle(numbers: java.util.List<Int>): Int {
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

`desugar_jdk_libs` supplies the implementations; D8/R8 rewrites bytecode so calls are routed there.

### How Desugaring Works (Pipeline)

1. Kotlin/Java code → Kotlin/Java compiler → JVM bytecode (usually targeting Java 8).
2. JVM bytecode → D8/R8:
   - performs language desugaring for Java 8+ features where required,
   - rewrites supported Java 8+ API calls to `desugar_jdk_libs` when Core Library Desugaring is enabled,
   - outputs DEX bytecode compatible with your configured `minSdk`.
3. DEX bytecode + `desugar_jdk_libs` → packaged into APK/AAB.

### Supported APIs via Core Library Desugaring (Typical Mapping)

(Exact support depends on the `desugar_jdk_libs` version.)

- `java.time.*`
  - Without desugaring: officially available from Android 8.0 (API 26).
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

Remember: the `minSdk 21+` constraint is specific to Core Library Desugaring for these APIs; language desugaring is more broadly applicable.

### Example: Working with Dates Without Vs With Desugaring

Without Core Library Desugaring (legacy style, also fine for very low `minSdk`):

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

// In Kotlin you normally use collection operations; this example shows Java Streams
// working on a Java List when Core Library Desugaring is enabled (minSdk 21+).
fun filterUsersWithDesugaring(users: java.util.List<User>) {
    val moscowAdults = users.stream()
        .filter { it.city == "Moscow" }
        .filter { it.age >= 25 }
        .map { it.name }
        .collect(Collectors.toList())

    println(moscowAdults)
}
```

### Limitations of Desugaring

1. Minimum API:
   - Core Library Desugaring is officially supported for `minSdk 21+`.
   - Language desugaring itself is not limited to 21+ and can support lower `minSdk` values.
2. APK size: typically adds about 100–300 KB to APK/AAB size (depending on usage and R8 shrinking).
3. API coverage: only a subset of Java 8+/9+ APIs is supported; always check `desugar_jdk_libs` documentation.
4. Performance: there can be a small overhead compared to native platform implementations.

### Alternatives to Desugaring

#### 1. Using ThreeTenABP (for `java.time`, Especially with Very Low `minSdk`)

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

If your app only targets newer Android versions and `minSdk >= 26`, most required Java 8 APIs are available natively and Core Library Desugaring might not be necessary:

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

    fun testStreamAPI(numbers: java.util.List<Int>) {
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

fun processUsersAfter(users: java.util.List<User>): java.util.List<String> {
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
    return dateTime.format(dateTime)
}
```

### Summary

Desugaring in Android allows you to:

1. Use Java 8+ language features on devices that do not natively support them (language desugaring).
2. Use selected Java 8+ APIs via Core Library Desugaring (`java.time`, Streams, `Optional`, `java.util.function`, etc.) when your project has `minSdk 21+`.
3. Keep your code modern, readable, and safer while still supporting a wide range of devices.

Use desugaring when:

- `minSdk 21+` and you want modern Java 8+ APIs like `java.time`, Streams, `Optional`.
- The small size increase (~100–300 KB) is acceptable.

It is less critical or may be unnecessary when:

- `minSdk >= 26` and the required APIs are available natively.
- Every kilobyte of APK size matters and you are not using those APIs.
- You rely on alternatives such as ThreeTenABP for very low `minSdk`.

## Дополнительные Вопросы (RU)

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

## Связанные Вопросы (RU)

- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]

## Related Questions (EN)

- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
