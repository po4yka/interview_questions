---
tags:
  - kotlin
  - java
  - generics
  - type-safety
  - runtime-errors
difficulty: hard
status: draft
---

# Heap Pollution (Загрязнение кучи)

**English**: Heap pollution - type safety violation with generics at runtime

## Ответ

**Heap pollution** (загрязнение кучи) — это ситуация, когда в памяти (heap) оказывается объект несоответствующего типа из-за неправильного использования дженериков. Это происходит из-за стирания типов (type erasure) в Java/Kotlin и может привести к `ClassCastException` во время выполнения программы, несмотря на успешную компиляцию.

### Причины Heap Pollution

В Java и Kotlin дженерики стираются во время компиляции:

```kotlin
// Во время компиляции
val list: List<String> = listOf("A", "B", "C")

// Во время выполнения (после type erasure)
val list: List = listOf("A", "B", "C")  // Информация о <String> потеряна!
```

Это приводит к тому, что во время выполнения невозможно проверить фактический тип дженерика.

### Пример 1: Базовый случай Heap Pollution

```kotlin
fun heapPollutionExample() {
    // Создаём список строк
    val stringList: MutableList<String> = mutableListOf("Hello", "World")

    // Получаем raw type (без дженерика)
    val rawList: MutableList<Any?> = stringList as MutableList<Any?>

    // HEAP POLLUTION: добавляем Integer в список String!
    rawList.add(42)  // Компилятор не видит проблемы из-за type erasure

    // RUNTIME ERROR: ClassCastException
    try {
        val first: String = stringList[0]  // OK: "Hello"
        val second: String = stringList[1] // OK: "World"
        val third: String = stringList[2]  // CRASH! Integer не может быть приведён к String
    } catch (e: ClassCastException) {
        println("Heap pollution detected: ${e.message}")
        // Output: java.lang.Integer cannot be cast to java.lang.String
    }
}
```

### Пример 2: Проблема с Varargs

```kotlin
// Небезопасный метод с varargs
@SafeVarargs  // Подавляет предупреждение (НЕ используйте без понимания!)
fun <T> dangerousMethod(vararg elements: T): Array<T> {
    return elements as Array<T>  // HEAP POLLUTION!
}

fun testDangerousVarargs() {
    // Создаём массив строк
    val strings: Array<String> = dangerousMethod("A", "B", "C")

    // Получаем raw array
    val rawArray: Array<Any?> = strings as Array<Any?>

    // HEAP POLLUTION
    rawArray[0] = 42

    // RUNTIME ERROR
    try {
        val first: String = strings[0]  // CRASH!
    } catch (e: ClassCastException) {
        println("Heap pollution in varargs: ${e.message}")
    }
}
```

### Пример 3: Проблема с Array<T> в Kotlin

```kotlin
fun <T> unsafeArrayCreation(size: Int, defaultValue: T): Array<T> {
    // HEAP POLLUTION: нельзя создать типизированный массив из-за type erasure
    @Suppress("UNCHECKED_CAST")
    return arrayOfNulls<Any?>(size) as Array<T>  // ОПАСНО!
}

fun testUnsafeArray() {
    val stringArray: Array<String> = unsafeArrayCreation(3, "default")

    // Массив на самом деле Array<Any?>, не Array<String>
    val rawArray = stringArray as Array<Any?>
    rawArray[0] = 42  // HEAP POLLUTION

    try {
        val first: String = stringArray[0]  // CRASH!
    } catch (e: ClassCastException) {
        println("Array heap pollution: ${e.message}")
    }
}
```

### Как избежать Heap Pollution

#### Решение 1: Использовать reified в inline функциях

```kotlin
// БЕЗОПАСНО: reified позволяет сохранить информацию о типе
inline fun <reified T> safeArrayCreation(size: Int, defaultValue: T): Array<T> {
    return Array(size) { defaultValue }
}

fun testSafeArray() {
    val stringArray: Array<String> = safeArrayCreation(3, "default")

    // Попытка добавить Integer приведёт к ошибке компиляции
    // val rawArray = stringArray as Array<Any?>  // Compiler error!

    println(stringArray.contentToString())  // [default, default, default]
}
```

#### Решение 2: Использовать List вместо Array

```kotlin
// БЕЗОПАСНО: List<T> в Kotlin неизменяемый
fun <T> safeListCreation(vararg elements: T): List<T> {
    return elements.toList()
}

fun testSafeList() {
    val strings: List<String> = safeListCreation("A", "B", "C")

    // Нельзя изменить, следовательно нет heap pollution
    // strings.add(42)  // Compiler error: List is immutable

    println(strings)  // [A, B, C]
}
```

#### Решение 3: Передавать KClass для создания типизированных массивов

```kotlin
// БЕЗОПАСНО: явная передача информации о типе
fun <T : Any> safeTypedArray(clazz: KClass<T>, size: Int, defaultValue: T): Array<T> {
    @Suppress("UNCHECKED_CAST")
    return java.lang.reflect.Array.newInstance(clazz.java, size) as Array<T>
}

fun testSafeTypedArray() {
    val stringArray: Array<String> = safeTypedArray(String::class, 3, "default")

    // Массив реально типизирован как Array<String>
    stringArray[0] = "Hello"
    stringArray[1] = "World"

    println(stringArray.contentToString())  // [Hello, World, default]
}
```

### Пример 4: Проблема с коллекциями в Android

```kotlin
// ПЛОХО: Heap pollution в RecyclerView Adapter
class BadAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
    private val items: MutableList<Any> = mutableListOf()  // Raw type!

    fun addString(item: String) {
        items.add(item)
    }

    fun addInt(item: Int) {
        items.add(item)  // HEAP POLLUTION: смешивание типов
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
        TODO()
    }
}

// ХОРОШО: Типизированный adapter
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
        TODO()
    }
}
```

### Пример 5: Проблема с Bundle в Android

```kotlin
// ПЛОХО: Heap pollution через Bundle
class BadActivity : AppCompatActivity() {
    companion object {
        private const val KEY_DATA = "data"

        fun start(context: Context, data: List<String>) {
            val intent = Intent(context, BadActivity::class.java)
            // HEAP POLLUTION: ArrayList<String> → ArrayList (type erasure)
            intent.putStringArrayListExtra(KEY_DATA, ArrayList(data))
            context.startActivity(intent)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Потенциальная проблема: тип может быть неверным
        val data: ArrayList<String>? = intent.getStringArrayListExtra(KEY_DATA)

        // Если кто-то случайно передал ArrayList<Int>, получим ClassCastException
    }
}

// ХОРОШО: Типобезопасная передача через Parcelable
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

        // Типобезопасно
        val wrapper: DataWrapper? = intent.getParcelableExtra(KEY_DATA)
        val data: List<String> = wrapper?.items ?: emptyList()
    }
}
```

### Предупреждения компилятора

Kotlin компилятор выдаёт предупреждения при потенциальном heap pollution:

```kotlin
// Предупреждение: "Unchecked cast: Array<Any?> to Array<String>"
@Suppress("UNCHECKED_CAST")
fun <T> dangerousArray(size: Int): Array<T> {
    return arrayOfNulls<Any?>(size) as Array<T>
}

// Предупреждение: "Creating an array of reifiable type with a vararg parameter"
fun <T> varargsMethod(vararg items: T): Array<T> {
    return items as Array<T>
}
```

### Аннотации для подавления предупреждений

```kotlin
// @SafeVarargs: гарантирует, что метод не создаёт heap pollution
// ИСПОЛЬЗУЙТЕ ТОЛЬКО ЕСЛИ УВЕРЕНЫ!
@SafeVarargs
fun <T> safeVarargs(vararg items: T): List<T> {
    return items.toList()  // toList() создаёт новую копию, безопасно
}

// @Suppress("UNCHECKED_CAST"): подавляет предупреждение
// ОПАСНО: используйте только если точно знаете, что делаете
@Suppress("UNCHECKED_CAST")
fun <T> unsafeCast(obj: Any): T {
    return obj as T  // Может привести к ClassCastException
}
```

### Best Practices

#### 1. Используйте неизменяемые коллекции

```kotlin
// ХОРОШО
fun createList(): List<String> {
    return listOf("A", "B", "C")  // Неизменяемый
}

// ПЛОХО
fun createMutableList(): MutableList<String> {
    return mutableListOf("A", "B", "C")  // Можно испортить
}
```

#### 2. Избегайте raw types

```kotlin
// ПЛОХО
val list: MutableList = mutableListOf()  // Raw type

// ХОРОШО
val list: MutableList<String> = mutableListOf()  // Типизированный
```

#### 3. Используйте sealed классы для разнородных данных

```kotlin
// ХОРОШО
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
}

// ПЛОХО
data class MixedResult(val data: Any?, val error: Exception?)  // Any?!
```

#### 4. Используйте inline + reified для типобезопасности

```kotlin
// ХОРОШО
inline fun <reified T> fromJson(json: String): T {
    return Gson().fromJson(json, T::class.java)
}

// Использование
val user: User = fromJson<User>(jsonString)
```

### Проверка на heap pollution в runtime

```kotlin
fun <T> checkHeapPollution(array: Array<T>, expectedClass: KClass<*>) {
    array.forEach { element ->
        if (element != null && !expectedClass.isInstance(element)) {
            throw IllegalStateException(
                "Heap pollution detected! Expected ${expectedClass.simpleName}, " +
                "but found ${element::class.simpleName}"
            )
        }
    }
}

fun test() {
    val stringArray: Array<String> = arrayOf("A", "B", "C")

    // Проверка
    checkHeapPollution(stringArray, String::class)  // OK

    // Если добавим Integer через небезопасное приведение
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

**Heap pollution** — это серьёзная проблема типобезопасности, которая может привести к:
- `ClassCastException` в runtime
- Сложно отлаживаемым багам
- Нарушению контрактов типов

**Как избежать:**
1. Используйте `inline` + `reified` для сохранения информации о типе
2. Предпочитайте `List<T>` вместо `Array<T>`
3. Избегайте raw types (типов без дженериков)
4. Используйте sealed классы для разнородных данных
5. Не подавляйте предупреждения компилятора без понимания
6. Используйте неизменяемые коллекции
7. Передавайте `KClass<T>` для создания типизированных массивов

**English**: Heap pollution occurs when an object of incorrect type appears in memory due to improper generics usage and type erasure in Java/Kotlin. It causes `ClassCastException` at runtime despite successful compilation. Happens when mixing raw types with generic types, using unchecked casts, or creating generic arrays without `reified`. Prevent by: using `inline` + `reified`, preferring `List<T>` over `Array<T>`, avoiding raw types, using sealed classes for heterogeneous data, and not suppressing compiler warnings without understanding the risks.
