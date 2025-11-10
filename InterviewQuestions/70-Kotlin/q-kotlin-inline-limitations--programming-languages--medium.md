---
id: lang-054
title: "Kotlin Inline Limitations / Ограничения inline в Kotlin"
aliases: [Kotlin Inline Limitations, Ограничения inline в Kotlin]
topic: kotlin
subtopics: [inline-functions, performance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-context-receivers--kotlin--hard]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, inline, lambdas, optimization, performance, kotlin]
---
# Вопрос (RU)
> Бывают ли случаи, когда нельзя использовать inline?

---

# Question (EN)
> Are there cases when inline cannot be used?

## Ответ (RU)

Да, есть случаи, когда `inline` **нельзя использовать технически** (компилятор выдаст ошибку), и случаи, когда `inline` **формально можно**, но использовать его **не рекомендуется** из-за раздувания кода или неочевидного поведения.

Технически `inline` запрещён, в частности, для:
- рекурсивных функций (прямая/косвенная рекурсия);
- абстрактных функций (нет тела);
- некоторых случаев, где параметры-лямбды «убегают» (escape) и не могут быть заинлайнены без `noinline`/`crossinline`.

Также обычно **не следует** делать `inline`:
- для функций с большими телами (прирост размера кода, минимальный профит),
- когда функция часто вызывается из Java-кода, где преимущества inlining на стороне Kotlin-вызывателей несущественны.

## Answer (EN)

Yes, there are cases where `inline` is **technically not allowed** (the compiler will reject it), and cases where `inline` is **allowed** but **not recommended** because of code bloat or subtle behavior.

Technically, `inline` is disallowed for:
- recursive functions (direct or indirect recursion),
- abstract functions (no body),
- certain cases where lambda parameters "escape" and cannot be inlined without `noinline`/`crossinline`.

It is also usually a bad idea to mark as `inline`:
- functions with large bodies (code size increase, negligible benefit),
- APIs called predominantly from Java, where inlining benefits at Kotlin call sites are less relevant.

## Когда Inline НЕ Следует Использовать

### 1. Большие Тела Функций

**Проблема:** Inlining копирует код функции в каждое место вызова, поэтому для больших функций это приводит к раздуванию кода.

```kotlin
// НЕЖЕЛАТЕЛЬНО - Большое тело функции
inline fun processLargeData(data: List<Int>) {
    // 100+ строк сложной логики
    val step1 = data.map { it * 2 }
    val step2 = step1.filter { it > 10 }
    val step3 = step2.groupBy { it % 3 }
    val step4 = step3.map { (key, values) -> key to values.sum() }
    // ... ещё много строк
    // Этот код будет скопирован в КАЖДОЕ место вызова.
}

// Вызывается 10 раз = раздувание кода (100+ строк × 10 = 1000+ строк)
repeat(10) {
    processLargeData(listOf(1, 2, 3))
}

// ЛУЧШЕ - Обычная функция
fun processLargeData(data: List<Int>) {
    // Большой код, одно определение, многократные вызовы
}
```

**Результат inlining больших функций:**
- увеличенный размер скомпилированного кода (.class/.dex),
- более медленная компиляция,
- возможные промахи кэша инструкций,
- часто минимальная или отрицательная выгода по производительности.

---

### 2. Рекурсивные Функции

**Проблема:** Рекурсивная `inline`-функция теоретически требует бесконечного разворачивания, поэтому компилятор это запрещает.

```kotlin
// ОШИБКА КОМПИЛЯЦИИ - Нельзя сделать inline рекурсивную функцию
inline fun factorial(n: Int): Int { // error: inline function 'factorial' cannot be recursive
    return if (n <= 1) 1
    else n * factorial(n - 1)
}
```

**Решение:** Не используйте `inline` для рекурсивных функций.

```kotlin
// ОК - Обычная рекурсивная функция
fun factorial(n: Int): Int {
    return if (n <= 1) 1
    else n * factorial(n - 1)
}
```

---

### 3. Передача Или Сохранение Лямбд (Escaping Parameters)

**Проблема:** Параметры-лямбды `inline`-функции по умолчанию предполагаются к inlining-у в месте вызова. Если такую лямбду:
- сохранить в переменную,
- положить в коллекцию,
- вернуть из функции,
- передать в другую функцию, которая не является inline,
то она «убегает» (escapes), и компилятор запрещает такое использование без явной маркировки.

```kotlin
val someList = mutableListOf<(Int) -> Unit>()

inline fun processData(data: List<Int>, action: (Int) -> Unit) {
    // Вызов в inline-контексте — OK
    data.forEach { action(it) }

    // НЕЛЬЗЯ: использовать inline-параметр как значение, которое утекает
    // val storedAction = action             // Error: Illegal usage of inline-parameter 'action'
    // someList.add(storedAction)
}
```

**Решение:** Использовать `noinline` для параметров, которые нужно сохранить или вернуть.

```kotlin
val someList = mutableListOf<(Int) -> Unit>()

inline fun processData(
    data: List<Int>,
    noinline action: (Int) -> Unit  // Не будет inlined, можно сохранять
) {
    val storedAction = action
    someList.add(storedAction)      // OK
}
```

(Аналогично, `crossinline` используется, когда лямбда не должна делать non-local return.)

---

### 4. Лямбды, Захватывающие Переменные (с Осторожностью)

**Контекст:** Захват переменных замыканием сам по себе не запрещает inline. Наоборот, inline часто помогает избежать дополнительного объекта-лямбды и бокса для изменяемых переменных. Проблемы возникают, когда такая лямбда утекает за пределы inline-контекста.

```kotlin
inline fun repeatInline(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()
    }
}

fun test() {
    var count = 0
    repeatInline(5) {
        count++  // c inline: тело будет подставлено, без отдельного объекта-лямбды
    }
}
```

**Когда это становится проблемой:** когда вы пытаетесь вернуть или сохранить лямбду, зависящую от локального контекста inline-функции, без `noinline`.

```kotlin
// НЕЛЬЗЯ: параметр-лямбда по умолчанию предполагается inline и не может утекать
inline fun <T> wrap(block: () -> T): () -> T {
    // return block          // Error: Illegal usage of inline-parameter 'block'
    TODO("example")
}
```

Вернуть можно только `noinline`-лямбду:

```kotlin
inline fun <T> wrap(noinline block: () -> T): () -> T {
    return block  // OK
}
```

Пример с локальной переменной в самой inline-функции закончен в момент выхода из функции, поэтому лямбда, которая её захватывает и при этом должна жить дольше (быть возвращённой), неприменима без отказа от inlining для этого параметра.

---

### 5. Виртуальные/Абстрактные Функции

**Проблема:** Для inlining нужно знать тело функции на этапе компиляции в месте вызова.

```kotlin
abstract class Base {
    // ОШИБКА - abstract inline невозможен (нет тела)
    // abstract inline fun process()
}
```

Абстрактные функции не могут быть `inline`.

Для `open inline` ситуация тоньше: такая функция должна иметь тело в том же модуле (или быть доступной), и есть ограничения на переопределения. На практике:
- помечать как `inline` функции, которые предполагаются виртуальными и полиморфными, обычно бессмысленно,
- если функция будет переопределяться, лучше не полагаться на `inline` для её вызовов.

**Рекомендация:**
- Для абстрактных/полиморфных API — обычные функции.
- `inline` — для финальных, хорошо известных реализаций.

---

### 6. Reified Type Parameters

`inline` обязателен, если вы хотите использовать `reified` параметр типа.

```kotlin
// OK - inline с reified
inline fun <reified T> isInstanceOf(value: Any): Boolean = value is T
```

Ограничения:
- `reified` работает только в `inline`-функциях,
- использование `reified`-типов в лямбдах, которые утекают (`noinline`/возвращаемые), не даёт преимуществ, так как эти лямбды не будут заинлайнены в вызывающем месте.

Пример, который не даёт ожидаемого эффекта (но компилируется):

```kotlin
inline fun <reified T> createChecker(): (Any) -> Boolean {
    // Лямбда возвращается и больше не может быть заинлайнена в вызывающем коде,
    // поэтому преимущества reified-типа ограничены и могут быть не тем, что вы ожидаете.
    return { it is T }
}
```

Главная идея: `reified` полезен, когда проверка типа выполняется непосредственно в месте вызова, а не в «утекшей» лямбде.

---

### 7. Функции, Вызываемые Из Java

**Проблема формулировки:** Java как язык не имеет ключевого слова `inline`, и вызовы из Java исходного кода не могут быть дополнительно заинлайнены на уровне Java-компилятора.

Как это работает в JVM-контексте:
- Kotlin-компилятор разворачивает `inline` при компиляции Kotlin-кода, который вызывает `inline`-функцию.
- Для Java-кода, который вызывает уже скомпилированный Kotlin-класс, этот вызов выглядит как обычный метод: для Java нет специального механизма повторного inlining на уровне исходников.

```kotlin
// Kotlin
inline fun process(action: () -> Unit) {
    action()
}
```

```java
// Java
// В уже скомпилированном байткоде Java видит обычный статический метод.
// Дополнительного source-level inlining на стороне Java не происходит.
```

**Вывод:** Если функция предназначена в основном для вызова из Java,
- `inline` не принесёт выгод на уровне Java-исходников,
- но может быть полезен для Kotlin-вызывающих сторон.

---

## When You SHOULD NOT Use Inline (EN)

### 1. Large Function Bodies

Inlining copies the function body into each call site. For large functions this leads to code bloat.

```kotlin
inline fun processLargeData(data: List<Int>) {
    val step1 = data.map { it * 2 }
    val step2 = step1.filter { it > 10 }
    val step3 = step2.groupBy { it % 3 }
    val step4 = step3.map { (key, values) -> key to values.sum() }
    // ... many more lines
}

fun useLarge() {
    repeat(10) {
        processLargeData(listOf(1, 2, 3))
    }
}

fun processLargeData(data: List<Int>) {
    // Large implementation in one place
}
```

Drawbacks:
- increased bytecode size (.class/.dex),
- slower compilation,
- potential instruction cache issues,
- often minimal or negative performance benefit.

---

### 2. Recursive Functions

Recursive `inline` functions would conceptually require infinite unrolling, so the compiler forbids them.

```kotlin
inline fun factorial(n: Int): Int { // error: inline function 'factorial' cannot be recursive
    return if (n <= 1) 1 else n * factorial(n - 1)
}
```

Use a regular (non-inline) function instead:

```kotlin
fun factorial(n: Int): Int = if (n <= 1) 1 else n * factorial(n - 1)
```

---

### 3. Escaping Lambdas (Saved/Returned Lambdas)

Inline lambda parameters are expected to be inlined at the call site. If you store/return/pass them in a non-inline way, the compiler disallows it unless they are marked `noinline`.

```kotlin
val someList = mutableListOf<(Int) -> Unit>()

inline fun processData(data: List<Int>, action: (Int) -> Unit) {
    data.forEach { action(it) }
    // val storedAction = action // Error: Illegal usage of inline-parameter 'action'
    // someList.add(storedAction)
}
```

Use `noinline` when the lambda must escape.

---

### 4. Lambdas Capturing Variables (With Escaping)

Capturing variables itself is fine as long as the lambda does not escape the inline scope. If you need to return or store such a lambda, mark it `noinline` or redesign the API.

```kotlin
inline fun repeatInline(times: Int, action: () -> Unit) {
    for (i in 0 until times) action()
}
```

---

### 5. Abstract/Virtual APIs

Inlining requires a known body at the call site.

- `abstract inline` is illegal.
- `open inline` is restricted and rarely desirable for polymorphic APIs.

Prefer normal functions for abstract/virtual designs.

---

### 6. Reified Type Parameters

`inline` is required when you use `reified` type parameters in a function.

```kotlin
inline fun <reified T> isInstanceOf(value: Any): Boolean = value is T
```

Constraints:
- `reified` only works in `inline` functions.
- Using `reified` types inside escaping lambdas (`noinline`/returned) does not provide the expected benefits because those lambdas are not inlined at the call site.

Example with limited effect:

```kotlin
inline fun <reified T> createChecker(): (Any) -> Boolean {
    // Returned lambda is no longer inlined at each call site,
    // so the advantages of reified are limited here.
    return { it is T }
}
```

Key idea: `reified` is most useful when the type check happens directly at the call site, not in an escaped lambda.

---

### 7. Functions Mainly Called from Java

From Java's perspective, inline functions are just regular methods in bytecode; there is no extra source-level inlining done by the Java compiler.

So if an API is primarily used from Java, `inline` usually gives little benefit, though it can still help Kotlin callers.

---

## Влияние На Размер Кода

### Пример: Inline vs Обычная

```kotlin
// Inline функция
inline fun log(message: String) {
    println("[LOG] $message")
}

// Вызывается 100 раз
fun main() {
    repeat(100) {
        log("Message $it")
    }
}
```

**После inlining (концептуально):**

```kotlin
fun main() {
    repeat(100) {
        // Код println подставлен много раз
        println("[LOG] Message $it")
    }
}
```

**Влияние на байткод:**
- обычная функция: одно определение + вызовы,
- inline: тело копируется в вызывающие места → больше байткода.

Поэтому имеет смысл делать inline только для маленьких, часто вызываемых функций, особенно с лямбда-параметрами.

---

## Code Size Impact (EN)

Example: inline vs normal function

```kotlin
inline fun log(message: String) {
    println("[LOG] $message")
}

fun main() {
    repeat(100) {
        log("Message $it")
    }
}
```

Conceptually after inlining:

```kotlin
fun main() {
    repeat(100) {
        println("[LOG] Message $it")
    }
}
```

Effects on bytecode:
- normal function: one definition + calls,
- inline: body duplicated at call sites → larger bytecode.

Use `inline` mainly for small, frequently called functions, especially higher-order ones with lambdas.

---

## Когда Избегать Inline

| Случай | Проблема | Рекомендация |
|------|---------|----------|
| **Большие функции** | Раздувание кода, слабый профит | Использовать обычную функцию |
| **Рекурсивные функции** | Технически запрещено компилятором | Обычная рекурсивная функция |
| **Сохранённые/возвращаемые лямбды без noinline** | Запрещено: escape inline-параметров | Пометить параметр как `noinline` или изменить дизайн |
| **Абстрактные / полиморфные API** | Нет стабильного тела для inlining | Обычные (не inline) функции |
| **Преимущественно вызовы из Java** | Нет доп. inlining на стороне Java | Оценить, нужен ли inline вообще |

---

## When to Avoid Inline (EN)

Avoid marking a function as `inline` when:
- it has a large body (code bloat),
- it is recursive (forbidden),
- it stores/returns lambda parameters without `noinline`,
- it is abstract/virtual or part of a polymorphic API,
- it is primarily called from Java.

---

## Когда ИСПОЛЬЗОВАТЬ Inline

Хорошие случаи использования:

1. **Небольшие higher-order функции с лямбдами** — чтобы избежать аллокации лямбд и получить non-local returns.

```kotlin
inline fun <T> measureTime(block: () -> T): T {
    val start = System.currentTimeMillis()
    val result = block()
    val duration = System.currentTimeMillis() - start
    println("Took ${duration}ms")
    return result
}
```

2. **Функции с reified type parameters** — когда нужно работать с типом в рантайме без явной передачи `Class`/`KClass`.

```kotlin
inline fun <reified T> Gson.fromJson(json: String): T =
    fromJson(json, T::class.java)
```

3. **Маленькие утилитные функции**, вызываемые очень часто, когда стоимость вызова существенна.

```kotlin
inline fun Int.isEven() = this % 2 == 0
inline fun String.isEmail() = contains("@")
```

4. **Производительно-критичные higher-order функции**, где хочется избежать объектов-лямбд.

```kotlin
inline fun List<Int>.sumByCustom(selector: (Int) -> Int): Int {
    var sum = 0
    for (element in this) {
        sum += selector(element)  // inlined, без отдельного объекта-лямбды
    }
    return sum
}
```

---

## When to USE Inline (EN)

Good use cases:

1. Small higher-order functions with lambdas, to:

```kotlin
inline fun <T> measureTime(block: () -> T): T {
    val start = System.currentTimeMillis()
    val result = block()
    val duration = System.currentTimeMillis() - start
    println("Took ${duration}ms")
    return result
}
```

2. Functions with `reified` type parameters that need runtime type information without passing `Class`/`KClass` explicitly.

```kotlin
inline fun <reified T> Gson.fromJson(json: String): T =
    fromJson(json, T::class.java)
```

3. Small, frequently called utility functions where call overhead is significant.

```kotlin
inline fun Int.isEven() = this % 2 == 0
inline fun String.isEmail() = contains("@")
```

4. Performance-critical higher-order functions where avoiding lambda objects matters.

```kotlin
inline fun List<Int>.sumByCustom(selector: (Int) -> Int): Int {
    var sum = 0
    for (element in this) {
        sum += selector(element)
    }
    return sum
}
```

---

## Резюме

**Технически нельзя использовать inline, когда:**

1. Функция рекурсивна (прямая или косвенная).
2. Функция абстрактная (нет тела).
3. Параметр-лямбда используется как значение, которое утекает (без `noinline`).

**Обычно не следует использовать inline, когда:**

1. Функции имеют большие тела → раздувание кода.
2. Функция предназначена для полиморфного/виртуального использования.
3. Функция в основном вызывается из Java, и выигрыш от inline минимален.

**Следует использовать inline, когда:**

1. Небольшие higher-order функции с лямбдами.
2. Нужны `reified` type parameters.
3. Маленькие, часто вызываемые утилиты.
4. Нужно убрать аллокацию объектов лямбд и/или поддержать non-local return.

**Ключевой принцип:** Инлайнить только те функции, где:
- тело маленькое и стабильное,
- есть параметры-лямбды,
- устранение вызова/аллокаций даёт реальную пользу.

**Влияние на память:** Лямбды без inline создают объекты и могут боксить изменяемые захваченные переменные; inline помогает это уменьшить, пока лямбды не утекают.

---

## Summary (EN)

Technically, you cannot use `inline` when:
- the function is recursive (directly or indirectly),
- the function is abstract (no body),
- a lambda parameter is used as an escaping value without `noinline`.

Usually you should avoid `inline` when:
- the function body is large (code bloat),
- the function is meant to be polymorphic/virtual,
- the function is mainly called from Java.

You should use `inline` when:
- you have small higher-order functions with lambdas,
- you need `reified` type parameters (which require `inline`),
- you have small, frequently called utilities,
- you want to avoid lambda allocations or enable non-local returns.

Key idea: inline only when it is small, stable, lambda-heavy code where removing call/alloc overhead brings real benefits.

Memory impact: lambdas without `inline` create objects and may box captured mutable variables; `inline` can reduce these costs as long as lambdas do not escape.

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия поведения inline по сравнению с Java?
- Когда вы бы применили inline на практике?
- Каковы типичные ошибки при использовании inline?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные вопросы (RU)

- [[q-context-receivers--kotlin--hard]]

## Related Questions

- [[q-context-receivers--kotlin--hard]]
