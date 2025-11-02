---
id: kotlin-155
title: "Reified Type Parameters / Reified параметры типов"
aliases: [Generics, Reified, Reified Type Parameters, Type Parameters]
topic: kotlin
subtopics: [generics, inline-functions, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-compose-side-effects-coroutines--kotlin--medium, q-inline-functions--kotlin--medium, q-suspending-vs-blocking--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium, generics, inline-functions, kotlin, reified, type-system]
date created: Friday, October 31st 2025, 6:30:28 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---

# Зачем Нужен Reified В Kotlin?

**English**: What is `reified` for in Kotlin?

## Answer (EN)
`reified` is a modifier for type parameters in inline functions that preserves type information at runtime. Normally in JVM, generic types are erased (type erasure), but `reified` allows accessing the type as a regular class inside the function.

### Problem: Type Erasure in Java/Kotlin

```kotlin
// - DOESN'T WORK - type T is erased at compile time
fun <T> isInstanceOf(value: Any): Boolean {
    return value is T  // ERROR: Cannot check for instance of erased type
}

// - НЕ РАБОТАЕТ - нельзя получить Class<T>
fun <T> createInstance(): T {
    return T::class.java.newInstance()  // ERROR: Cannot use T::class
}

// Old way - pass Class explicitly
fun <T> createInstance(clazz: Class<T>): T {
    return clazz.newInstance()
}

// Usage - inconvenient
val user = createInstance(User::class.java)
```

### Solution: Reified + Inline

```kotlin
//  With reified - type available at runtime
inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T  // OK!
}

inline fun <reified T> createInstance(): T {
    return T::class.java.newInstance()  // OK!
}

// Usage - clean and simple
val user = createInstance<User>()
val isUser = isInstanceOf<User>(someObject)
```

### Practical Examples

#### 1. Collection Filtering by Type

```kotlin
// Without reified - need to pass Class
fun <T> List<*>.filterByType(clazz: Class<T>): List<T> {
    return this.filter { clazz.isInstance(it) }
        .map { it as T }
}

// Usage
val numbers = listOf<Any>(1, "two", 3, "four", 5)
val ints = numbers.filterByType(Int::class.java)  // Clumsy

//  With reified - built into Kotlin
inline fun <reified T> List<*>.filterIsInstance(): List<T> {
    return this.filterIsInstance(T::class.java)
}

// Использование - элегантно
val ints = numbers.filterIsInstance<Int>()
val strings = numbers.filterIsInstance<String>()
```

#### 2. JSON Deserialization (Gson, Moshi, kotlinx.serialization)

```kotlin
// Без reified - нужно передавать Type/Class
fun <T> parseJson(json: String, type: Class<T>): T {
    return Gson().fromJson(json, type)
}

val user = parseJson(jsonString, User::class.java)  // Повторяющийся код

//  С reified - чище
inline fun <reified T> Gson.fromJson(json: String): T {
    return fromJson(json, T::class.java)
}

// Использование
val user = gson.fromJson<User>(jsonString)
val users = gson.fromJson<List<User>>(jsonString)

// Для сложных типов
inline fun <reified T> Gson.fromJson(json: String): T {
    return fromJson(json, object : TypeToken<T>() {}.type)
}

val map = gson.fromJson<Map<String, User>>(jsonString)
```

#### 3. Intent Extras in Android

```kotlin
// Без reified - многословно
fun <T : Parcelable> Intent.getParcelableExtraCompat(
    key: String,
    clazz: Class<T>
): T? {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        getParcelableExtra(key, clazz)
    } else {
        @Suppress("DEPRECATION")
        getParcelableExtra(key) as? T
    }
}

val user = intent.getParcelableExtraCompat("user", User::class.java)

//  С reified - элегантно
inline fun <reified T : Parcelable> Intent.getParcelableExtraCompat(
    key: String
): T? {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        getParcelableExtra(key, T::class.java)
    } else {
        @Suppress("DEPRECATION")
        getParcelableExtra(key) as? T
    }
}

// Использование
val user = intent.getParcelableExtraCompat<User>("user")
val location = intent.getParcelableExtraCompat<Location>("location")
```

#### 4. Type-safe Activity Launch

```kotlin
// Старый способ
val intent = Intent(context, UserDetailActivity::class.java)
context.startActivity(intent)

//  С reified - DSL стиль
inline fun <reified T : Activity> Context.startActivity(
    configureIntent: Intent.() -> Unit = {}
) {
    val intent = Intent(this, T::class.java)
    intent.configureIntent()
    startActivity(intent)
}

// Использование
context.startActivity<UserDetailActivity> {
    putExtra("user_id", 123)
    putExtra("mode", "edit")
}

context.startActivity<MainActivity>()
```

#### 5. ViewModel Creation

```kotlin
// Без reified - многословно
val viewModel = ViewModelProvider(this)[UserViewModel::class.java]

//  С reified extension
inline fun <reified VM : ViewModel> ComponentActivity.viewModel(): Lazy<VM> {
    return lazy {
        ViewModelProvider(this)[VM::class.java]
    }
}

// Использование
class UserActivity : AppCompatActivity() {
    private val viewModel by viewModel<UserViewModel>()
}

// Или для Fragment
inline fun <reified VM : ViewModel> Fragment.viewModel(): Lazy<VM> {
    return lazy {
        ViewModelProvider(this)[VM::class.java]
    }
}
```

#### 6. Dependency Injection (Koin, Kodein)

```kotlin
// Koin с reified
inline fun <reified T> get(): T {
    return KoinContext.get().get(T::class)
}

// Использование
val repository: UserRepository = get()
val apiService: ApiService = get()

// Kodein
inline fun <reified T : Any> Kodein.instance(): T {
    return direct.instance(generic<T>())
}

val db: AppDatabase = kodein.instance()
```

#### 7. Runtime Type Checking

```kotlin
inline fun <reified T> checkType(value: Any): String {
    return when (value) {
        is T -> "Value is of type ${T::class.simpleName}"
        else -> "Value is NOT of type ${T::class.simpleName}"
    }
}

// Использование
println(checkType<String>("Hello"))  // Value is of type String
println(checkType<String>(123))      // Value is NOT of type String

// Проверка нескольких типов
inline fun <reified T> Any.isType(): Boolean = this is T

val x: Any = "test"
println(x.isType<String>())  // true
println(x.isType<Int>())     // false
```

#### 8. Room Database Queries

```kotlin
// Room с reified
inline fun <reified T> RoomDatabase.getDao(): T {
    return when (T::class) {
        UserDao::class -> userDao() as T
        ProductDao::class -> productDao() as T
        else -> throw IllegalArgumentException("Unknown DAO type")
    }
}

// Использование
val userDao = database.getDao<UserDao>()
val productDao = database.getDao<ProductDao>()
```

### How Reified Works under the Hood

```kotlin
// Kotlin code
inline fun <reified T> createList(): List<T> {
    println("Creating list of ${T::class.simpleName}")
    return emptyList()
}

fun test() {
    val users = createList<User>()
    val products = createList<Product>()
}

// Compiles to (approximately):
fun test() {
    // Function code is inlined with concrete type
    println("Creating list of User")
    val users = emptyList<User>()

    println("Creating list of Product")
    val products = emptyList<Product>()
}
```

**Key point**: The compiler inlines the function code at the call site, substituting the concrete type for `T`. That's why `T::class` works - the compiler knows the concrete type.

### Reified Limitations

```kotlin
//  ALLOWED
inline fun <reified T> getClassName() = T::class.simpleName
inline fun <reified T> isInstance(obj: Any) = obj is T
inline fun <reified T> createArray(size: Int) = Array<T?>(size) { null }

// - NOT ALLOWED - function MUST be inline
fun <reified T> nonInlineFunction() {}  // ERROR: reified requires inline

// - NOT ALLOWED - virtual/override functions cannot be inline
interface Repository<T> {
    fun <reified T> find(): T  // ERROR: reified doesn't work with interface methods
}

// - NOT ALLOWED - function parameters cannot be reified
inline fun test(reified param: Any) {}  // ERROR: only type parameters
```

### Comparison of Approaches

```kotlin
// 1. Without generics - code duplication
fun parseUser(json: String): User = gson.fromJson(json, User::class.java)
fun parseProduct(json: String): Product = gson.fromJson(json, Product::class.java)
// ... 50 more functions

// 2. Generic without reified - inconvenient
fun <T> parse(json: String, clazz: Class<T>): T = gson.fromJson(json, clazz)

val user = parse(jsonString, User::class.java)  // Type repetition

// 3. Generic with reified - ideal
inline fun <reified T> parse(json: String): T = gson.fromJson(json, T::class.java)

val user = parse<User>(jsonString)  // Type specified once
```

### Advanced Patterns

#### Multiple Reified Parameters

```kotlin
inline fun <reified K, reified V> createMap(): MutableMap<K, V> {
    println("Creating Map<${K::class.simpleName}, ${V::class.simpleName}>")
    return mutableMapOf()
}

val userMap = createMap<Int, User>()  // Map<Int, User>
```

#### Reified with Bounds

```kotlin
inline fun <reified T : Number> sumOf(vararg values: T): Double {
    return values.sumOf { it.toDouble() }
}

val sum1 = sumOf(1, 2, 3)           // Int
val sum2 = sumOf(1.5, 2.5, 3.5)     // Double
```

#### Reified Для Reflection

```kotlin
inline fun <reified T> getAnnotations(): List<Annotation> {
    return T::class.annotations
}

@Deprecated("Use UserV2")
data class User(val name: String)

val annotations = getAnnotations<User>()
annotations.forEach { println(it) }  // @Deprecated(...)
```

#### Safe Cast С Reified

```kotlin
inline fun <reified T> Any?.safeCast(): T? {
    return this as? T
}

val obj: Any? = "Hello"
val str = obj.safeCast<String>()  // "Hello"
val num = obj.safeCast<Int>()     // null
```

### Performance Consideration

```kotlin
// reified функции inline - нет вызова функции
inline fun <reified T> create(): T = T::class.java.newInstance()

// Каждый вызов встраивается:
val user = create<User>()        // User::class.java.newInstance()
val product = create<Product>()  // Product::class.java.newInstance()

// Если функция большая и вызывается часто - раздутие кода
// Лучше использовать reified только для маленьких функций
```

### Best Practices

1. **Используйте reified для type-safe API**
   ```kotlin
   inline fun <reified T> Bundle.get(key: String): T? = get(key) as? T
   ```

2. **Комбинируйте с extension functions**
   ```kotlin
   inline fun <reified T> Context.getSystemService(): T? {
       return ContextCompat.getSystemService(this, T::class.java)
   }
   ```

3. **DSL builders**
   ```kotlin
   inline fun <reified T> json(init: T.() -> Unit): T {
       return T::class.java.newInstance().apply(init)
   }
   ```

4. **Избегайте больших reified функций**
   ```kotlin
   // - Плохо - большая функция будет копироваться
   inline fun <reified T> hugeFunctionWithLotsOfCode() {
       // 100+ строк кода
   }
   ```

**English**: `reified` modifier for type parameters in inline functions preserves type information at runtime, bypassing JVM type erasure. Enables: `T::class`, `is T` checks, `Array<T>()` creation without passing `Class<T>`. Must be `inline` function. Use cases: JSON parsing (`gson.fromJson<User>()`), Intent extras (`intent.getParcelableExtra<User>()`), Activity launch (`startActivity<MainActivity>()`), ViewModel creation, collection filtering (`filterIsInstance<String>()`). Compiler inlines function code with concrete type. Cannot use with non-inline, virtual, or interface methods.

## Ответ (RU)

Модификатор `reified` для параметров типов в inline функциях сохраняет информацию о типе во время выполнения, обходя стирание типов (type erasure) в JVM.

### Что Дает Reified

- Доступ к `T::class` (получение класса типа)
- Проверки `is T` (runtime type checks)
- Создание `Array<T>()` без передачи `Class<T>`
- Работа с reflection для типа T

### Обязательные Требования

Функция **должна быть inline**. Нельзя использовать с:
- Не-inline функциями
- Virtual/override методами
- Методами интерфейсов

### Практические Примеры Использования

1. **JSON парсинг**: `gson.fromJson<User>(json)` вместо `gson.fromJson(json, User::class.java)`
2. **Intent extras в Android**: `intent.getParcelableExtra<User>("user")` вместо передачи класса
3. **Запуск Activity**: `startActivity<MainActivity>()` - короткий DSL синтаксис
4. **ViewModel creation**: `viewModel<UserViewModel>()` - автоматическое определение класса
5. **Фильтрация коллекций**: `list.filterIsInstance<String>()` - фильтрация по типу

### Как Работает

Компилятор встраивает (inlines) код функции в место вызова, подставляя конкретный тип вместо `T`. Поэтому `T::class` работает - компилятор знает конкретный тип.

## Related Questions

- [[q-compose-side-effects-coroutines--kotlin--medium]]
- [[q-inline-functions--kotlin--medium]]
- [[q-suspending-vs-blocking--kotlin--medium]]
