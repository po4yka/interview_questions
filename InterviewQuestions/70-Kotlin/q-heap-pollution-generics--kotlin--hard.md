---
id: kotlin-177
title: Heap Pollution Generics / Heap Pollution (Загрязнение кучи)
aliases:
- Heap Pollution
- Heap Pollution (Загрязнение кучи)
- Heap Pollution Generics
topic: kotlin
subtopics:
- collections
- functions
- types
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-collections
- c-kotlin
- q-suspend-functions-basics--kotlin--easy
created: 2023-10-15
updated: 2025-11-11
tags:
- difficulty/hard
- kotlin/collections
- kotlin/functions
- kotlin/types
anki_cards:
- slug: kotlin-177-0-en
  language: en
  difficulty: 0.7
  tags:
  - Kotlin
  - difficulty::hard
  - collections
  - functions
  - types
- slug: kotlin-177-0-ru
  language: ru
  difficulty: 0.7
  tags:
  - Kotlin
  - difficulty::hard
  - collections
  - functions
  - types
---
# Вопрос (RU)
> Что такое heap pollution (загрязнение кучи) в дженериках Kotlin/Java? Как это происходит и как можно предотвратить?

# Question (EN)
> What is heap pollution in Kotlin/Java generics? How does it occur and how can you prevent it?

## Ответ (RU)

**Heap pollution** (загрязнение кучи) — это ситуация, когда переменная параметризованного типа (например, `List<String>`) на самом деле указывает на объект, который не удовлетворяет этому параметру типа (например, содержит не-`String`). Это результат некорректного использования дженериков и/или raw-типов, усугубляемый стиранием типов (type erasure) в Java/Kotlin. Это может привести к `ClassCastException` во время выполнения программы, несмотря на успешную компиляцию.

### Причины Heap Pollution

В Java и Kotlin (на JVM) дженерики стираются во время компиляции:

```kotlin
// Во время компиляции
val list: List<String> = listOf("A", "B", "C")

// Во время выполнения (после type erasure)
val list: List<*> = listOf("A", "B", "C")  // Информация о <String> потеряна
```

Это приводит к тому, что во время выполнения невозможно проверить фактический параметр типа дженерика, и небезопасные приведения могут загрязнить кучу.

### Пример 1: Базовый Случай Heap Pollution

```kotlin
fun heapPollutionExample() {
    // Создаём список строк
    val stringList: MutableList<String> = mutableListOf("Hello", "World")

    // Небезопасное приведение к менее специфичному типу
    @Suppress("UNCHECKED_CAST")
    val rawList: MutableList<Any?> = stringList as MutableList<Any?>

    // HEAP POLLUTION: добавляем Int в список, который по контракту должен содержать только String
    rawList.add(42)

    // RUNTIME ERROR: ClassCastException при использовании как MutableList<String>
    try {
        val first: String = stringList[0]  // OK: "Hello"
        val second: String = stringList[1] // OK: "World"
        val third: String = stringList[2]  // CRASH! Integer не может быть приведён к String
    } catch (e: ClassCastException) {
        println("Heap pollution detected: ${e.message}")
        // Пример вывода: java.lang.Integer cannot be cast to java.lang.String
    }
}
```

### Пример 2: Varargs И Небезопасные Массивы (концепт)

Kotlin `vararg`-параметры представляются как массивы (`Array<out T>`), и при неправильных небезопасных приведениях можно получить heap pollution.

```kotlin
// Небезопасный метод с vararg + небезопасным приведением
fun <T> dangerousMethod(vararg elements: T): Array<T> {
    @Suppress("UNCHECKED_CAST")
    return elements as Array<T> // Потенциально опасно, зависит от реального массива под капотом
}

fun testDangerousVarargs() {
    val strings: Array<String> = dangerousMethod("A", "B", "C")

    val rawArray: Array<Any?> = strings as Array<Any?>
    // HEAP POLLUTION: нарушаем контракт массива строк
    rawArray[0] = 42

    try {
        val first: String = strings[0]  // CRASH!
    } catch (e: ClassCastException) {
        println("Heap pollution in varargs: ${e.message}")
    }
}
```

Важно: в Kotlin `@SafeVarargs` обычно не используется напрямую для Kotlin-функций и применим в основном к Java-коду или специальным случаям. Он не делает небезопасный код безопасным и не исправляет логически ошибочные тела методов.

### Пример 3: Проблема С `Array<T>` В Kotlin

```kotlin
fun <T> unsafeArrayCreation(size: Int): Array<T> {
    // HEAP POLLUTION: создаём массив без реальной информации о T
    @Suppress("UNCHECKED_CAST")
    return arrayOfNulls<Any?>(size) as Array<T>
}

fun testUnsafeArray() {
    val stringArray: Array<String> = unsafeArrayCreation(3)

    // Массив на самом деле Array<Any?>, не гарантированно Array<String>
    val rawArray = stringArray as Array<Any?>
    rawArray[0] = 42  // HEAP POLLUTION

    try {
        val first: String = stringArray[0]  // CRASH!
    } catch (e: ClassCastException) {
        println("Array heap pollution: ${e.message}")
    }
}
```

### Как Избежать Heap Pollution

#### Решение 1: Использовать Reified В Inline-функциях

```kotlin
// Более безопасно: reified позволяет корректно создавать массив нужного типа
inline fun <reified T> safeArrayCreation(size: Int, defaultValue: T): Array<T> {
    return Array(size) { defaultValue }
}

fun testSafeArray() {
    val stringArray: Array<String> = safeArrayCreation(3, "default")

    // Небезопасное расширяющее приведение по-прежнему возможно (и потенциально опасно):
    val rawArray: Array<Any?> = stringArray as Array<Any?>
    // Heap pollution появится, только если записать в rawArray элемент неверного типа.

    println(stringArray.contentToString())  // [default, default, default]
}
```

#### Решение 2: Использовать `List` Вместо `Array`, Когда Это Возможно

```kotlin
// БЕЗОПАСНЕЕ: List<T> в Kotlin неизменяемый по интерфейсу
fun <T> safeListCreation(vararg elements: T): List<T> {
    return elements.toList()
}

fun testSafeList() {
    val strings: List<String> = safeListCreation("A", "B", "C")

    // Нельзя добавить элемент, контракт списка не нарушается
    // strings.add(42)  // Ошибка компиляции: List не имеет add

    println(strings)  // [A, B, C]
}
```

#### Решение 3: Передавать `KClass<T>` Для Создания Типизированных Массивов

```kotlin
// БЕЗОПАСНО: явная передача информации о типе
fun <T : Any> safeTypedArray(clazz: KClass<T>, size: Int, defaultValue: T): Array<T> {
    @Suppress("UNCHECKED_CAST")
    val array = java.lang.reflect.Array.newInstance(clazz.java, size) as Array<T>
    array.fill(defaultValue)
    return array
}

fun testSafeTypedArray() {
    val stringArray: Array<String> = safeTypedArray(String::class, 3, "default")

    // Массив реально типизирован как Array<String>
    stringArray[0] = "Hello"
    stringArray[1] = "World"

    println(stringArray.contentToString())  // [Hello, World, default]
}
```

### Пример 4: Коллекции В Android (риск Небезопасных приводов)

```kotlin
// ПЛОХО: несогласованный контракт типов в RecyclerView Adapter
class BadAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
    private val items: MutableList<Any> = mutableListOf()  // Грубо типизированный список

    fun addString(item: String) {
        items.add(item)
    }

    fun addInt(item: Int) {
        items.add(item)  // Смешивание типов усложняет безопасное использование
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        try {
            val item: String = items[position] as String  // Может упасть!
        } catch (e: ClassCastException) {
            println("Runtime error in adapter: ${e.message}")
        }
    }

    override fun getItemCount(): Int = items.size
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        throw NotImplementedError("Implementation depends on specific ViewHolder")
    }
}

// ХОРОШО: типизированный адаптер с sealed-классами
sealed class AdapterItem {
    data class StringItem(val text: String) : AdapterItem()
    data class IntItem(val number: Int) : AdapterItem()
}

class GoodAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
    private val items: MutableList<AdapterItem> = mutableListOf()

    fun addString(text: String) {
        items.add(AdapterItem.StringItem(text))
    }

    fun addInt(number: Int) {
        items.add(AdapterItem.IntItem(number))
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (val item = items[position]) {
            is AdapterItem.StringItem -> bindString(holder, item.text)
            is AdapterItem.IntItem -> bindInt(holder, item.number)
        }
    }

    private fun bindString(holder: RecyclerView.ViewHolder, text: String) {
        // Безопасная работа со строкой
    }

    private fun bindInt(holder: RecyclerView.ViewHolder, number: Int) {
        // Безопасная работа с числом
    }

    override fun getItemCount(): Int = items.size
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        throw NotImplementedError("Implementation depends on specific ViewHolder")
    }
}
```

Этот пример показывает, как нарушение контракта типов (использование `Any` и небезопасных cast'ов) может приводить к ошибкам, аналогичным heap pollution.

### Пример 5: `Bundle` В Android

```kotlin
// Опасность: несогласованное использование ключей и типов
class BadActivity : AppCompatActivity() {
    companion object {
        private const val KEY_DATA = "data"

        fun start(context: Context, data: List<String>) {
            val intent = Intent(context, BadActivity::class.java)
            intent.putStringArrayListExtra(KEY_DATA, ArrayList(data)) // ОК при правильном типе
            context.startActivity(intent)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Потенциальная проблема: если кто-то переиспользует тот же ключ с другим типом
        val data: ArrayList<String>? = intent.getStringArrayListExtra(KEY_DATA)
        // Если в другой части кода под тем же KEY_DATA положат не-String список,
        // можно получить ClassCastException — концептуально похоже на heap pollution договора типов.
    }
}

// ЛУЧШЕ: типобезопасная передача через Parcelable
@Parcelize
data class DataWrapper(val items: List<String>) : Parcelable

class GoodActivity : AppCompatActivity() {
    companion object {
        private const val KEY_DATA = "data"

        fun start(context: Context, data: List<String>) {
            val intent = Intent(context, GoodActivity::class.java)
            intent.putExtra(KEY_DATA, DataWrapper(data))
            context.startActivity(intent)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val wrapper: DataWrapper? = intent.getParcelableExtra(KEY_DATA)
        val data: List<String> = wrapper?.items ?: emptyList()
    }
}
```

### Предупреждения Компилятора

Kotlin/Java выдают предупреждения при потенциальном heap pollution (непроверяемые приведения, массивы дженериков и т.п.). Их нельзя игнорировать без понимания.

```kotlin
// Предупреждение: "Unchecked cast: Array<Any?> to Array<String>"
@Suppress("UNCHECKED_CAST")
fun <T> dangerousArray(size: Int): Array<T> {
    return arrayOfNulls<Any?>(size) as Array<T>
}

// Предупреждение: "Unchecked cast" при приведении vararg-массива
fun <T> varargsMethod(vararg items: T): Array<T> {
    @Suppress("UNCHECKED_CAST")
    return items as Array<T>
}
```

### Аннотации Для Подавления Предупреждений

```kotlin
// В Kotlin используйте специальные подавления очень осторожно.
// @SafeVarargs относится в первую очередь к Java-методам и не делает небезопасный код безопасным.

// @Suppress("UNCHECKED_CAST"): подавляет предупреждение
// ОПАСНО: используйте только если точно уверены, что приведение корректно
@Suppress("UNCHECKED_CAST")
fun <T> unsafeCast(obj: Any): T {
    return obj as T  // Может привести к ClassCastException
}
```

### Best Practices (RU)

#### 1. Используйте Неизменяемые Коллекции, Когда Можно

```kotlin
// ХОРОШО
fun createList(): List<String> {
    return listOf("A", "B", "C")  // Неизменяемый интерфейс
}

// Потенциально ОПАСНЕЕ (контракт можно нарушить через небезопасные операции)
fun createMutableList(): MutableList<String> {
    return mutableListOf("A", "B", "C")
}
```

#### 2. Избегайте Raw Types / Слишком Общих Типов Без Необходимости

```kotlin
// ПЛОХО
val listRaw: MutableList<*> = mutableListOf<String>()  // или без указания дженерика в Java-коде

// ХОРОШО
val list: MutableList<String> = mutableListOf()
```

#### 3. Используйте Sealed-классы Для Разнородных Данных

```kotlin
// ХОРОШО
sealed class Result<out T> {
    data class Success<out T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
}

// ПЛОХО
data class MixedResult(val data: Any?, val error: Exception?)  // Any? затрудняет типобезопасность
```

#### 4. Используйте Inline + Reified Для Типобезопасности Там, Где Нужно Знать Реальный Тип

```kotlin
inline fun <reified T> fromJson(json: String): T {
    return Gson().fromJson(json, T::class.java)
}

// Использование
val user: User = fromJson<User>(jsonString)
```

#### 5. Относитесь К Непроверяемым Операциям Как К Потенциальным Ошибкам

- Минимизируйте область действия `@Suppress("UNCHECKED_CAST")`.
- Явно документируйте инварианты, на которых основан небезопасный код.

#### 6. Проверяйте Инварианты В Критичных Местах

```kotlin
fun <T> checkHeapPollution(array: Array<T>, expectedClass: KClass<*>): Unit {
    array.forEach { element ->
        if (element != null && !expectedClass.isInstance(element)) {
            throw IllegalStateException(
                "Heap pollution detected! Expected ${expectedClass.simpleName}, " +
                    "but found ${element::class.simpleName}"
            )
        }
    }
}
```

### Проверка На Heap Pollution В Runtime

```kotlin
fun testHeapPollutionCheck() {
    val stringArray: Array<String> = arrayOf("A", "B", "C")

    // Проверка
    checkHeapPollution(stringArray, String::class)  // OK

    // Если добавить Int через небезопасное приведение
    val rawArray = stringArray as Array<Any?>
    rawArray[0] = 42

    try {
        checkHeapPollution(stringArray, String::class)  // CRASH
    } catch (e: IllegalStateException) {
        println(e.message)
        // Output: Heap pollution detected! Expected String, but found Int
    }
}
```

### Вывод

**Heap pollution** — это серьёзная проблема типобезопасности, когда переменная параметризованного типа ссылается на значение несоответствующего типа. Это приводит к:
- `ClassCastException` в runtime
- сложным для отладки багам
- нарушению контрактов типов и потере доверия к дженерикам

**Как избежать:**
1. Не смешивать raw-типы и параметризованные типы.
2. Аккуратно обращаться с массивами дженериков; при необходимости использовать `inline` + `reified` или `KClass`.
3. Предпочитать `List<T>` и другие коллекции, скрывающие детали реализации.
4. Использовать sealed-классы и точные типы вместо `Any` для разнородных данных.
5. Не подавлять предупреждения компилятора без понимания причин.
6. Отдавать предпочтение неизменяемым коллекциям на границах API.

## Answer (EN)

Heap pollution is a type-safety violation where a variable of a parameterized type (for example, `List<String>`) actually refers to an object whose runtime contents are not consistent with its type argument (for example, it contains a non-`String`). On the JVM this is enabled by type erasure and usually appears when you mix raw/loosely typed code with generics, use unchecked casts, or work unsafely with arrays and varargs.

Core mechanism:
- At runtime, generic type arguments are erased, so the JVM cannot distinguish `List<String>` from `List<Any?>`. If you mutate through a less specific view, you can corrupt the heap so that a supposedly typed reference points to values of the wrong type, causing `ClassCastException` and violating contracts.

### Example 1: Basic Heap Pollution with Collections

```kotlin
fun heapPollutionExample() {
    val stringList: MutableList<String> = mutableListOf("Hello", "World")

    @Suppress("UNCHECKED_CAST")
    val rawList: MutableList<Any?> = stringList as MutableList<Any?>

    // Heap pollution: list is declared as MutableList<String>, but we store an Int
    rawList.add(42)

    try {
        val first: String = stringList[0]
        val second: String = stringList[1]
        val third: String = stringList[2] // ClassCastException: Int -> String
    } catch (e: ClassCastException) {
        println("Heap pollution detected: ${e.message}")
    }
}
```

### Example 2: Varargs and Generic Arrays

```kotlin
fun <T> dangerousMethod(vararg elements: T): Array<T> {
    @Suppress("UNCHECKED_CAST")
    return elements as Array<T> // unchecked, relies on underlying array representation
}

fun testDangerousVarargs() {
    val strings: Array<String> = dangerousMethod("A", "B", "C")

    val rawArray: Array<Any?> = strings as Array<Any?>
    rawArray[0] = 42 // violates the "Array<String>" contract

    try {
        val first: String = strings[0] // ClassCastException
    } catch (e: ClassCastException) {
        println("Heap pollution in varargs: ${e.message}")
    }
}
```

Important: in Kotlin, `@SafeVarargs` is typically relevant for Java methods or very specific interop cases. It does not make inherently unsafe code safe and does not fix logically unsafe method bodies.

### Example 3: Unsafe `Array<T>` Construction

```kotlin
fun <T> unsafeArrayCreation(size: Int): Array<T> {
    @Suppress("UNCHECKED_CAST")
    return arrayOfNulls<Any?>(size) as Array<T> // element type not truly T
}

fun testUnsafeArray() {
    val stringArray: Array<String> = unsafeArrayCreation(3)

    val rawArray = stringArray as Array<Any?>
    rawArray[0] = 42

    try {
        val first: String = stringArray[0] // ClassCastException
    } catch (e: ClassCastException) {
        println("Array heap pollution: ${e.message}")
    }
}
```

### Example 4: Android RecyclerView Adapter

```kotlin
// BAD: uses MutableList<Any> and unsafe casts
class BadAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
    private val items: MutableList<Any> = mutableListOf()

    fun addString(item: String) {
        items.add(item)
    }

    fun addInt(item: Int) {
        items.add(item)
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        try {
            val item: String = items[position] as String // may throw at runtime
        } catch (e: ClassCastException) {
            println("Runtime error in adapter: ${e.message}")
        }
    }

    override fun getItemCount(): Int = items.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        throw NotImplementedError("Implementation depends on specific ViewHolder")
    }
}

// GOOD: sealed hierarchy with precise types
sealed class AdapterItem {
    data class StringItem(val text: String) : AdapterItem()
    data class IntItem(val number: Int) : AdapterItem()
}

class GoodAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
    private val items: MutableList<AdapterItem> = mutableListOf()

    fun addString(text: String) {
        items.add(AdapterItem.StringItem(text))
    }

    fun addInt(number: Int) {
        items.add(AdapterItem.IntItem(number))
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (val item = items[position]) {
            is AdapterItem.StringItem -> bindString(holder, item.text)
            is AdapterItem.IntItem -> bindInt(holder, item.number)
        }
    }

    private fun bindString(holder: RecyclerView.ViewHolder, text: String) {
        // type-safe binding
    }

    private fun bindInt(holder: RecyclerView.ViewHolder, number: Int) {
        // type-safe binding
    }

    override fun getItemCount(): Int = items.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        throw NotImplementedError("Implementation depends on specific ViewHolder")
    }
}
```

### Example 5: Android `Bundle`/`Intent` Extras

```kotlin
// RISKY: inconsistent use of key/type
class BadActivity : AppCompatActivity() {
    companion object {
        private const val KEY_DATA = "data"

        fun start(context: Context, data: List<String>) {
            val intent = Intent(context, BadActivity::class.java)
            intent.putStringArrayListExtra(KEY_DATA, ArrayList(data))
            context.startActivity(intent)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val data: ArrayList<String>? = intent.getStringArrayListExtra(KEY_DATA)
        // If some other code wrote extras under KEY_DATA with a different type,
        // this assumption may break at runtime (conceptually same contract violation).
    }
}

// BETTER: strongly-typed Parcelable wrapper
@Parcelize
data class DataWrapper(val items: List<String>) : Parcelable

class GoodActivity : AppCompatActivity() {
    companion object {
        private const val KEY_DATA = "data"

        fun start(context: Context, data: List<String>) {
            val intent = Intent(context, GoodActivity::class.java)
            intent.putExtra(KEY_DATA, DataWrapper(data))
            context.startActivity(intent)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val wrapper: DataWrapper? = intent.getParcelableExtra(KEY_DATA)
        val data: List<String> = wrapper?.items ?: emptyList()
    }
}
```

### Compiler Warnings (EN)

```kotlin
@Suppress("UNCHECKED_CAST")
fun <T> dangerousArray(size: Int): Array<T> {
    // Warning: Unchecked cast: Array<Any?> to Array<T>
    return arrayOfNulls<Any?>(size) as Array<T>
}

fun <T> varargsMethod(vararg items: T): Array<T> {
    @Suppress("UNCHECKED_CAST")
    return items as Array<T> // Unchecked cast
}
```

Treat such warnings as indicators of potential heap pollution; suppress only with strict reasoning.

### Annotations and Suppression (EN)

- `@Suppress("UNCHECKED_CAST")` or Java's `@SuppressWarnings("unchecked")` only hide warnings.
- `@SafeVarargs` is primarily relevant for certain Java methods and does not make unsafe code safe or fix logically unsafe bodies.
- Confine these annotations to narrow, well-justified helpers and never suppress warnings without understanding the cause.

### Runtime Heap Pollution Check (EN)

```kotlin
fun <T> checkHeapPollution(array: Array<T>, expectedClass: KClass<*>): Unit {
    array.forEach { element ->
        if (element != null && !expectedClass.isInstance(element)) {
            throw IllegalStateException(
                "Heap pollution detected! Expected ${expectedClass.simpleName}, " +
                    "but found ${element::class.simpleName}"
            )
        }
    }
}

fun testHeapPollutionCheck() {
    val stringArray: Array<String> = arrayOf("A", "B", "C")

    checkHeapPollution(stringArray, String::class) // OK

    val rawArray = stringArray as Array<Any?>
    rawArray[0] = 42

    try {
        checkHeapPollution(stringArray, String::class) // throws
    } catch (e: IllegalStateException) {
        println(e.message)
        // Output: Heap pollution detected! Expected String, but found Int
    }
}
```

### Best Practices (EN)

1. Use immutable, precisely typed collections when possible.
2. Avoid raw types and over-generic `Any` containers in public APIs.
3. Use sealed hierarchies for heterogeneous data instead of `Any`.
4. Use `inline` + `reified` or explicit `KClass` where real type information is required.
5. Treat unchecked operations as exceptional: localize `@Suppress("UNCHECKED_CAST")`, document assumptions, and do not suppress warnings without understanding them.
6. Validate invariants in critical code using runtime checks (for example, `checkHeapPollution`).

## Follow-ups (RU)

- В чем ключевые отличия поведения heap pollution в Kotlin по сравнению с Java?
- Где на практике чаще всего проявляются такие ошибки в Android/Kotlin-проектах?
- Какие типичные анти-паттерны (например, чрезмерное использование `Any` или raw-типов) приводят к heap pollution?

## Follow-ups (EN)

- What are the key differences in heap pollution behavior between Kotlin on the JVM and Java?
- When would you most commonly encounter these issues in real-world Kotlin/Android projects?
- Which common anti-patterns (for example, overuse of `Any` or raw types) tend to cause heap pollution?

## References (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-collections]]

## References (EN)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-collections]]

## Related Questions (RU/EN)

- [[q-suspend-functions-basics--kotlin--easy]]
