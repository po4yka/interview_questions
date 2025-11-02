---
id: lang-054
title: "Kotlin Inline Limitations / Ограничения inline в Kotlin"
aliases: [Kotlin Inline Limitations, Ограничения inline в Kotlin]
topic: programming-languages
subtopics: [inline-functions, performance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-access-modifiers--programming-languages--medium, q-object-companion-object--programming-languages--hard, q-context-receivers--kotlin--hard]
created: 2025-10-15
updated: 2025-10-31
tags:
  - programming-languages
  - inline
  - lambdas
  - optimization
  - performance
  - recursion
  - difficulty/medium
---
# Бывают ли случаи, когда нельзя использовать inline?

# Question (EN)
> Are there cases when inline cannot be used?

# Вопрос (RU)
> Бывают ли случаи, когда нельзя использовать inline?

---

## Answer (EN)

Yes, **inline cannot be used** if the function contains **large blocks of code** or **recursion**, as this will increase the size of compiled code. Also, **inline functions are not suitable** for passing or returning lambdas that capture variables from the context. This can lead to errors or significant increase in memory consumption.

## When Inline Should NOT Be Used

### 1. Large Function Bodies

**Problem:** Inlining copies function code to every call site.

```kotlin
// - BAD - Large function body
inline fun processLargeData(data: List<Int>) {
    // 100+ lines of complex logic
    val step1 = data.map { it * 2 }
    val step2 = step1.filter { it > 10 }
    val step3 = step2.groupBy { it % 3 }
    val step4 = step3.map { (key, values) -> key to values.sum() }
    // ... many more lines
    // This code is copied to EVERY call site!
}

// Called 10 times = code bloat (100+ lines × 10 = 1000+ lines)
repeat(10) {
    processLargeData(listOf(1, 2, 3))
}

// - GOOD - Regular function
fun processLargeData(data: List<Int>) {
    // Large code, called once
}
```

**Result of inlining large functions:**
- Increased compiled code size (.dex/.class files)
- Slower compilation
- Potential instruction cache misses
- Minimal performance benefit

---

### 2. Recursive Functions

**Problem:** Inlining creates infinite copy loop.

```kotlin
// - COMPILATION ERROR - Cannot inline recursive function
inline fun factorial(n: Int): Int {
    return if (n <= 1) 1
    else n * factorial(n - 1)  // - Error: Cannot inline recursive call
}
```

**Why it fails:**

```
Attempt to inline factorial(5):

factorial(5) = 5 * factorial(4)
             = 5 * (4 * factorial(3))
             = 5 * (4 * (3 * factorial(2)))
             = ... infinite inlining!
```

**Compiler error:**
```
Error: Inline function 'factorial' cannot be recursive
```

**Solution:** Don't use `inline` for recursive functions:

```kotlin
// - GOOD - Regular function
fun factorial(n: Int): Int {
    return if (n <= 1) 1
    else n * factorial(n - 1)
}
```

---

### 3. Passing or Storing Lambdas (Non-Inlined)

**Problem:** Lambdas passed to non-inline functions or stored create objects.

```kotlin
// - BAD - Lambda cannot be inlined
inline fun processData(data: List<Int>, action: (Int) -> Unit) {
    // Passing lambda to non-inline function
    data.forEach(action)  // forEach is inline, OK

    // Storing lambda - creates object!
    val storedAction = action  // - Capturing creates object
    someList.add(storedAction)  // - Cannot inline
}
```

**Compiler error:**
```
Error: Illegal usage of inline-parameter 'action'
```

**Workaround:** Use `noinline`:

```kotlin
// - GOOD - Mark lambda as noinline
inline fun processData(
    data: List<Int>,
    noinline action: (Int) -> Unit  // Won't be inlined
) {
    val storedAction = action  // OK now
    someList.add(storedAction)
}
```

---

### 4. Lambdas Capturing Variables (with caution)

**Problem:** Captured variables in lambdas can cause issues.

```kotlin
// WARNING: CAREFUL - Capturing variables
inline fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Fine
    }
}

fun test() {
    var count = 0
    repeat(5) {
        count++  // Captures 'count' - creates boxing overhead
    }
}
```

**What happens:**

Without inline:
```kotlin
// Lambda creates object with 'count' reference
class Lambda : Function0<Unit> {
    var count: Ref<Int>  // Wrapped in reference
    override fun invoke() {
        count.element++
    }
}
```

With inline:
```kotlin
// Lambda body inlined - direct variable access
for (i in 0 until 5) {
    count++  // Direct access, no wrapping
}
```

**When it becomes a problem:**

```kotlin
// - PROBLEM - Returns lambda that captures variables
inline fun createCounter(): () -> Int {
    var count = 0
    return { count++ }  // - Cannot inline returned lambda
}
```

**Compiler error:**
```
Error: Inline function cannot contain reified type parameters
```

---

### 5. Virtual/Abstract Functions

**Problem:** Inline requires compile-time knowledge of function body.

```kotlin
abstract class Base {
    // - COMPILATION ERROR - Abstract cannot be inline
    abstract inline fun process()  // - No body to inline
}

open class Parent {
    // - COMPILATION ERROR - Open cannot be inline
    open inline fun calculate() {  // - Can be overridden
        // ...
    }
}
```

**Why:** Inlining requires knowing exact implementation at compile time.

**Solution:** Don't use inline with virtual/abstract functions:

```kotlin
abstract class Base {
    abstract fun process()  // - OK
}
```

---

### 6. Functions with Reified Type Parameters (partially)

**Correct usage:**

```kotlin
// - OK - inline with reified
inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T
}
```

**Problematic usage:**

```kotlin
// - PROBLEM - Returning lambda with reified type
inline fun <reified T> createChecker(): (Any) -> Boolean {
    return { it is T }  // - Cannot return lambda using reified type
}
```

---

### 7. Functions Called from Java

**Problem:** Java doesn't understand Kotlin's inline.

```kotlin
// Kotlin
inline fun process(action: () -> Unit) {
    action()
}

// Called from Java - inline is ignored!
```

**Java sees:**

```java
public static final void process(@NotNull Function0 action) {
    action.invoke();  // Regular call, not inlined
}
```

**Result:** Performance benefit lost when called from Java.

---

## Code Size Impact

### Example: Inline vs Regular

```kotlin
// Inline function
inline fun log(message: String) {
    println("[LOG] $message")
}

// Called 100 times
fun main() {
    repeat(100) {
        log("Message $it")
    }
}
```

**After inlining:**

```kotlin
fun main() {
    repeat(100) {
        // Code copied 100 times!
        println("[LOG] Message $it")
    }
}
```

**Bytecode impact:**
- Regular function: ~10 lines of bytecode (1 function definition + 100 calls)
- Inlined function: ~200 lines of bytecode (println copied 100 times)

---

## When to Avoid Inline

| Case | Problem | Solution |
|------|---------|----------|
| **Large functions** | Code bloat | Regular function |
| **Recursive functions** | Infinite inlining | Regular function |
| **Stored lambdas** | Cannot inline | `noinline` modifier |
| **Returned lambdas** | Escaping lambda | `noinline` or regular function |
| **Virtual/abstract** | No body at compile time | Regular function |
| **Called from Java** | Inline ignored | Consider regular function |

---

## When TO Use Inline

- **Good use cases:**

1. **Higher-order functions with lambdas:**

```kotlin
inline fun <T> measureTime(block: () -> T): T {
    val start = System.currentTimeMillis()
    val result = block()
    val duration = System.currentTimeMillis() - start
    println("Took ${duration}ms")
    return result
}
```

2. **Functions with reified type parameters:**

```kotlin
inline fun <reified T> Gson.fromJson(json: String): T {
    return fromJson(json, T::class.java)
}
```

3. **Small utility functions:**

```kotlin
inline fun Int.isEven() = this % 2 == 0
inline fun String.isEmail() = contains("@")
```

4. **Performance-critical lambdas:**

```kotlin
inline fun List<Int>.sumByCustom(selector: (Int) -> Int): Int {
    var sum = 0
    for (element in this) {
        sum += selector(element)  // Inlined, no lambda object
    }
    return sum
}
```

---

## Summary

**Cannot use inline when:**

1. **Large function bodies** - causes code bloat
2. **Recursive functions** - infinite inlining
3. **Storing lambdas** - lambda must be invoked inline
4. **Returning lambdas** - escaping context
5. **Virtual/abstract functions** - no body to inline
6. **Called primarily from Java** - inline ignored

**Should use inline when:**

1. Small higher-order functions with lambdas
2. Functions with reified type parameters
3. Performance-critical small utilities
4. Eliminating lambda object allocation

**Key principle:** Only inline **small functions** with **lambda parameters** where **eliminating lambda objects** provides meaningful performance benefit.

**Memory impact:** Captured variables in non-inlined lambdas cause boxing and increased memory usage.

---

## Ответ (RU)

Да, **inline нельзя использовать** если функция содержит **большие блоки кода** или **рекурсию**, так как это увеличит размер скомпилированного кода. Также **inline-функции не подходят** для передачи или возврата лямбд, которые захватывают переменные из контекста. Это может привести к ошибкам или значительному увеличению потребления памяти.

## Когда Inline НЕ Следует Использовать

### 1. Большие Тела Функций

**Проблема:** Inlining копирует код функции в каждое место вызова.

```kotlin
// ПЛОХО - Большое тело функции
inline fun processLargeData(data: List<Int>) {
    // 100+ строк сложной логики
    val step1 = data.map { it * 2 }
    val step2 = step1.filter { it > 10 }
    val step3 = step2.groupBy { it % 3 }
    val step4 = step3.map { (key, values) -> key to values.sum() }
    // ... ещё много строк
    // Этот код копируется в КАЖДОЕ место вызова!
}

// Вызывается 10 раз = раздувание кода (100+ строк × 10 = 1000+ строк)
repeat(10) {
    processLargeData(listOf(1, 2, 3))
}

// ХОРОШО - Обычная функция
fun processLargeData(data: List<Int>) {
    // Большой код, вызывается один раз
}
```

**Результат inlining больших функций:**
- Увеличенный размер скомпилированного кода (.dex/.class файлы)
- Медленная компиляция
- Потенциальные промахи кэша инструкций
- Минимальная польза производительности

---

### 2. Рекурсивные Функции

**Проблема:** Inlining создаёт бесконечный цикл копирования.

```kotlin
// ОШИБКА КОМПИЛЯЦИИ - Нельзя сделать inline рекурсивную функцию
inline fun factorial(n: Int): Int {
    return if (n <= 1) 1
    else n * factorial(n - 1)  // Ошибка: Нельзя сделать inline рекурсивный вызов
}
```

**Почему это не работает:**

```
Попытка inline factorial(5):

factorial(5) = 5 * factorial(4)
             = 5 * (4 * factorial(3))
             = 5 * (4 * (3 * factorial(2)))
             = ... бесконечный inlining!
```

**Ошибка компилятора:**
```
Error: Inline function 'factorial' cannot be recursive
```

**Решение:** Не используйте `inline` для рекурсивных функций:

```kotlin
// ХОРОШО - Обычная функция
fun factorial(n: Int): Int {
    return if (n <= 1) 1
    else n * factorial(n - 1)
}
```

---

### 3. Передача или Сохранение Лямбд (Non-Inlined)

**Проблема:** Лямбды, переданные в не-inline функции или сохранённые, создают объекты.

```kotlin
// ПЛОХО - Лямбда не может быть inlined
inline fun processData(data: List<Int>, action: (Int) -> Unit) {
    // Передача лямбды в не-inline функцию
    data.forEach(action)  // forEach inline, OK

    // Сохранение лямбды - создаёт объект!
    val storedAction = action  // Захват создаёт объект
    someList.add(storedAction)  // Нельзя inline
}
```

**Ошибка компилятора:**
```
Error: Illegal usage of inline-parameter 'action'
```

**Решение:** Используйте `noinline`:

```kotlin
// ХОРОШО - Пометить лямбду как noinline
inline fun processData(
    data: List<Int>,
    noinline action: (Int) -> Unit  // Не будет inlined
) {
    val storedAction = action  // Теперь OK
    someList.add(storedAction)
}
```

---

### 4. Лямбды Захватывающие Переменные (с осторожностью)

**Проблема:** Захваченные переменные в лямбдах могут вызвать проблемы.

```kotlin
// ВНИМАНИЕ: ОСТОРОЖНО - Захват переменных
inline fun repeat(times: Int, action: () -> Unit) {
    for (i in 0 until times) {
        action()  // Нормально
    }
}

fun test() {
    var count = 0
    repeat(5) {
        count++  // Захватывает 'count' - создаёт boxing overhead
    }
}
```

**Что происходит:**

Без inline:
```kotlin
// Лямбда создаёт объект со ссылкой на 'count'
class Lambda : Function0<Unit> {
    var count: Ref<Int>  // Обёрнут в ссылку
    override fun invoke() {
        count.element++
    }
}
```

С inline:
```kotlin
// Тело лямбды inlined - прямой доступ к переменной
for (i in 0 until 5) {
    count++  // Прямой доступ, без обёртывания
}
```

**Когда это становится проблемой:**

```kotlin
// ПРОБЛЕМА - Возвращает лямбду которая захватывает переменные
inline fun createCounter(): () -> Int {
    var count = 0
    return { count++ }  // Нельзя inline возвращаемую лямбду
}
```

**Ошибка компилятора:**
```
Error: Inline function cannot contain reified type parameters
```

---

### 5. Виртуальные/Абстрактные Функции

**Проблема:** Inline требует знания тела функции на этапе компиляции.

```kotlin
abstract class Base {
    // ОШИБКА КОМПИЛЯЦИИ - Abstract не может быть inline
    abstract inline fun process()  // Нет тела для inline
}

open class Parent {
    // ОШИБКА КОМПИЛЯЦИИ - Open не может быть inline
    open inline fun calculate() {  // Может быть переопределена
        // ...
    }
}
```

**Почему:** Inlining требует знания точной реализации на этапе компиляции.

**Решение:** Не используйте inline с виртуальными/абстрактными функциями:

```kotlin
abstract class Base {
    abstract fun process()  // OK
}
```

---

### 6. Функции с Reified Type Parameters (частично)

**Правильное использование:**

```kotlin
// OK - inline с reified
inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T
}
```

**Проблемное использование:**

```kotlin
// ПРОБЛЕМА - Возврат лямбды с reified типом
inline fun <reified T> createChecker(): (Any) -> Boolean {
    return { it is T }  // Нельзя вернуть лямбду используя reified тип
}
```

---

### 7. Функции Вызываемые из Java

**Проблема:** Java не понимает Kotlin inline.

```kotlin
// Kotlin
inline fun process(action: () -> Unit) {
    action()
}

// Вызов из Java - inline игнорируется!
```

**Java видит:**

```java
public static final void process(@NotNull Function0 action) {
    action.invoke();  // Обычный вызов, не inlined
}
```

**Результат:** Польза производительности теряется при вызове из Java.

---

## Влияние на Размер Кода

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

**После inlining:**

```kotlin
fun main() {
    repeat(100) {
        // Код скопирован 100 раз!
        println("[LOG] Message $it")
    }
}
```

**Влияние на байткод:**
- Обычная функция: ~10 строк байткода (1 определение функции + 100 вызовов)
- Inlined функция: ~200 строк байткода (println скопирован 100 раз)

---

## Когда Избегать Inline

| Случай | Проблема | Решение |
|------|---------|----------|
| **Большие функции** | Раздувание кода | Обычная функция |
| **Рекурсивные функции** | Бесконечный inlining | Обычная функция |
| **Сохранённые лямбды** | Нельзя inline | Модификатор `noinline` |
| **Возвращаемые лямбды** | Утекающая лямбда | `noinline` или обычная функция |
| **Виртуальные/абстрактные** | Нет тела на этапе компиляции | Обычная функция |
| **Вызов из Java** | Inline игнорируется | Рассмотрите обычную функцию |

---

## Когда ИСПОЛЬЗОВАТЬ Inline

**Хорошие случаи использования:**

1. **Higher-order функции с лямбдами:**

```kotlin
inline fun <T> measureTime(block: () -> T): T {
    val start = System.currentTimeMillis()
    val result = block()
    val duration = System.currentTimeMillis() - start
    println("Took ${duration}ms")
    return result
}
```

2. **Функции с reified type parameters:**

```kotlin
inline fun <reified T> Gson.fromJson(json: String): T {
    return fromJson(json, T::class.java)
}
```

3. **Маленькие утилитные функции:**

```kotlin
inline fun Int.isEven() = this % 2 == 0
inline fun String.isEmail() = contains("@")
```

4. **Производительно-критичные лямбды:**

```kotlin
inline fun List<Int>.sumByCustom(selector: (Int) -> Int): Int {
    var sum = 0
    for (element in this) {
        sum += selector(element)  // Inlined, нет объекта лямбды
    }
    return sum
}
```

---

## Резюме

**Нельзя использовать inline когда:**

1. **Большие тела функций** - вызывает раздувание кода
2. **Рекурсивные функции** - бесконечный inlining
3. **Сохранение лямбд** - лямбда должна вызываться inline
4. **Возврат лямбд** - утекающий контекст
5. **Виртуальные/абстрактные функции** - нет тела для inline
6. **Вызов преимущественно из Java** - inline игнорируется

**Следует использовать inline когда:**

1. Маленькие higher-order функции с лямбдами
2. Функции с reified type parameters
3. Производительно-критичные маленькие утилиты
4. Устранение аллокации объектов лямбд

**Ключевой принцип:** Только inline **маленькие функции** с **параметрами-лямбдами** где **устранение объектов лямбд** даёт значимую пользу производительности.

**Влияние на память:** Захваченные переменные в не-inlined лямбдах вызывают boxing и увеличение использования памяти.

## Related Questions

- [[q-kotlin-access-modifiers--programming-languages--medium]]
- [[q-object-companion-object--programming-languages--hard]]
- [[q-context-receivers--kotlin--hard]]
