---
id: kotlin-155
title: "Reified Type Parameters / Reified параметры типов"
aliases: [Reified, Reified Type Parameters, Type Parameters]
topic: kotlin
subtopics: [inline-functions, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-kotlin-features, q-inline-functions--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, generics, inline-functions, kotlin, reified, type-system]
---

# Вопрос (RU)

> Зачем нужен `reified` в Kotlin?

# Question (EN)

> What is `reified` for in Kotlin?

## Ответ (RU)

Модификатор `reified` для параметров типов в `inline`-функциях позволяет получить конкретный типовой аргумент внутри тела функции в местах вызова. В JVM обобщённые типы стираются (type erasure), и обычно `T` недоступен во время выполнения. С `reified` + `inline` компилятор подставляет конкретный тип при инлайнинге, поэтому внутри такой функции можно использовать `T::class`, проверки `is T` и другие операции с типом.

Важно: `reified` не отменяет стирание типов на JVM глобально, он лишь даёт доступ к конкретному типу внутри инлайновой функции, где компилятор его знает.

### Проблема: стирание типов в Java/Kotlin

```kotlin
// - НЕ РАБОТАЕТ - тип T стирается на этапе компиляции
fun <T> isInstanceOf(value: Any): Boolean {
    return value is T  // ERROR: Cannot check for instance of erased type
}

// - НЕ РАБОТАЕТ - нельзя получить T::class
fun <T> createInstance(): T {
    return T::class.java.newInstance()  // ERROR: Cannot use T::class
}

// Старый способ — передавать Class явно
fun <T> createInstance(clazz: Class<T>): T {
    return clazz.newInstance() // newInstance() устаревший и работает только для public no-arg конструкторов
}

// Использование — громоздко
val user = createInstance(User::class.java)
```

### Решение: Reified + inline

```kotlin
// С reified — информация о типе доступна внутри инлайнового тела
inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T  // OK
}

inline fun <reified T> createInstance(): T {
    // Упрощённый пример; в реальном коде нужно обрабатывать доступность конструктора и исключения
    return T::class.java.getDeclaredConstructor().newInstance()
}

// Использование — просто и читабельно
val user = createInstance<User>()
val isUser = isInstanceOf<User>(someObject)
```

### Практические примеры

#### 1. Фильтрация коллекций по типу

```kotlin
// Без reified — нужно передавать Class
fun <T> List<*>.filterByType(clazz: Class<T>): List<T> {
    return this.filter { clazz.isInstance(it) }
        .map { it as T }
}

// Использование
val numbers = listOf<Any>(1, "two", 3, "four", 5)
val ints = numbers.filterByType(Int::class.java)  // Неудобно

// С reified — как stdlib-функция filterIsInstance
inline fun <reified T> List<*>.filterByTypeReified(): List<T> {
    return this.filterIsInstance<T>()
}

// Использование — лаконично и type-safe
val ints2 = numbers.filterByTypeReified<Int>()
val strings = numbers.filterByTypeReified<String>()
```

#### 2. JSON-десериализация (Gson, Moshi, kotlinx.serialization)

```kotlin
// Без reified — нужно передавать Type/Class
fun <T> parseJson(json: String, type: Class<T>): T {
    return Gson().fromJson(json, type)
}

val user = parseJson(jsonString, User::class.java)  // Повторение типов

// С reified — проще для негeneric-типов
inline fun <reified T> Gson.fromJsonReified(json: String): T {
    return fromJson(json, T::class.java)
}

// Использование
val user2 = gson.fromJsonReified<User>(jsonString)

// Для generic/сложных типов
inline fun <reified T> Gson.fromJsonGeneric(json: String): T {
    return fromJson(json, object : TypeToken<T>() {}.type)
}

val users: List<User> = gson.fromJsonGeneric(jsonString)
val map: Map<String, User> = gson.fromJsonGeneric(jsonString)
```

#### 3. Extras в Intent в Android

```kotlin
// Без reified — многословно
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

// С reified — короче
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
val user2 = intent.getParcelableExtraCompat<User>("user")
val location = intent.getParcelableExtraCompat<Location>("location")
```

#### 4. Type-safe запуск Activity

```kotlin
// Старый способ
val intent = Intent(context, UserDetailActivity::class.java)
context.startActivity(intent)

// С reified — DSL-стиль
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

#### 5. Создание ViewModel

```kotlin
// Без reified — многословно
val viewModel = ViewModelProvider(this)[UserViewModel::class.java]

// С reified-расширением (упрощённо)
inline fun <reified VM : ViewModel> ComponentActivity.viewModel(): Lazy<VM> {
    return lazy {
        ViewModelProvider(this)[VM::class.java]
    }
}

// Использование
class UserActivity : AppCompatActivity() {
    private val viewModel by viewModel<UserViewModel>()
}

// Для Fragment
inline fun <reified VM : ViewModel> Fragment.viewModel(): Lazy<VM> {
    return lazy {
        ViewModelProvider(this)[VM::class.java]
    }
}
```

#### 6. Dependency Injection (Koin, Kodein)

```kotlin
// Использование Koin с reified (API может отличаться по версиям; иллюстрация)
inline fun <reified T> koinGet(): T {
    return KoinContext.get().get(T::class) // Иллюстрация; зависит от конкретного API
}

// Использование
val repository: UserRepository = koinGet()
val apiService: ApiService = koinGet()

// Пример для Kodein (упрощённо)
inline fun <reified T : Any> Kodein.instanceTyped(): T {
    return direct.instance(generic<T>()) // Иллюстрация; реальный API может отличаться
}

val db: AppDatabase = kodein.instanceTyped()
```

#### 7. Проверка типа во время выполнения

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

// В виде расширения
inline fun <reified T> Any.isType(): Boolean = this is T

val x: Any = "test"
println(x.isType<String>())  // true
println(x.isType<Int>())     // false
```

#### 8. Запросы к Room Database

```kotlin
// Пример паттерна с Room и reified (упрощённо; требует явного сопоставления типов)
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

### Как работает reified под капотом

```kotlin
// Kotlin-код
inline fun <reified T> createList(): List<T> {
    println("Creating list of ${T::class.simpleName}")
    return emptyList()
}

fun test() {
    val users = createList<User>()
    val products = createList<Product>()
}

// Концептуально компилируется примерно в следующее:
fun test() {
    // Тело функции инлайнится с конкретными типами
    println("Creating list of User")
    val users = emptyList<User>()

    println("Creating list of Product")
    val products = emptyList<Product>()
}
```

Ключевой момент: компилятор инлайнит тело функции в место вызова, подставляя конкретные типы вместо `T`. Поэтому `T::class` и проверки `is T` работают внутри таких функций, несмотря на стирание типов на JVM.

### Ограничения reified

```kotlin
// РАЗРЕШЕНО
inline fun <reified T> getClassName() = T::class.simpleName
inline fun <reified T> isInstance(obj: Any) = obj is T
inline fun <reified T> createArray(size: Int) = arrayOfNulls<T>(size)

// ЗАПРЕЩЕНО — функция с reified должна быть inline
fun <reified T> nonInlineFunction() {}  // ERROR: reified type parameters are only allowed in inline functions

// ВАЖНО — reified-параметры разрешены только в inline-функциях;
// inline-члены не могут быть open/override и их нельзя объявлять в интерфейсах,
// поэтому reified-нельзя использовать как обобщённый виртуальный контракт.
interface Repository<T> {
    // Неверно: inline/reified здесь использовать нельзя
    // fun <reified R> find(): R
}

// ЗАПРЕЩЕНО — value-параметры не могут быть reified
inline fun test(reified param: Any) {}  // ERROR: only type parameters can be reified
```

### Сравнение подходов

```kotlin
// 1. Без обобщений — дублирование кода
fun parseUser(json: String): User = gson.fromJson(json, User::class.java)
fun parseProduct(json: String): Product = gson.fromJson(json, Product::class.java)
// ... много отдельных функций

// 2. Обобщённая функция без reified — нужно передавать Class
fun <T> parse(json: String, clazz: Class<T>): T = gson.fromJson(json, clazz)

val user = parse(jsonString, User::class.java)

// 3. Обобщённая функция с reified — короче
inline fun <reified T> parseReified(json: String): T = gson.fromJson(json, T::class.java)

val user2 = parseReified<User>(jsonString)
```

### Продвинутые паттерны

#### Несколько reified-параметров

```kotlin
inline fun <reified K, reified V> createMap(): MutableMap<K, V> {
    println("Creating Map<${K::class.simpleName}, ${V::class.simpleName}>")
    return mutableMapOf()
}

val userMap = createMap<Int, User>()  // MutableMap<Int, User>
```

#### Reified с ограничениями

```kotlin
inline fun <reified T : Number> sumOf(vararg values: T): Double {
    return values.sumOf { it.toDouble() }
}

val sum1 = sumOf(1, 2, 3)
val sum2 = sumOf(1.5, 2.5, 3.5)
```

#### Reified для рефлексии

```kotlin
inline fun <reified T> getAnnotations(): List<Annotation> {
    return T::class.annotations
}

@Deprecated("Use UserV2")
data class User(val name: String)

val annotations = getAnnotations<User>()
annotations.forEach { println(it) }  // @Deprecated(...)
```

#### Безопасное приведение с reified

```kotlin
inline fun <reified T> Any?.safeCast(): T? {
    return this as? T
}

val obj: Any? = "Hello"
val str = obj.safeCast<String>()  // "Hello"
val num = obj.safeCast<Int>()     // null
```

### Производительность

```kotlin
// Reified-функции — inline, накладные расходы на вызов убираются (но возможны расходы на рефлексию)
inline fun <reified T> create(): T = T::class.java.getDeclaredConstructor().newInstance()

// Каждый вызов инлайнится с конкретным типом
val user = create<User>()
val product = create<Product>()

// Если тело функции большое и используется с множеством типов,
// инлайнинг может привести к раздутию байткода. Используйте компактные reified-хелперы.
```

### Рекомендации по использованию

1. Используйте `reified` для type-safe API.
   ```kotlin
   inline fun <reified T> Bundle.getTyped(key: String): T? = get(key) as? T
   ```

2. Комбинируйте с extension-функциями.
   ```kotlin
   inline fun <reified T> Context.getSystemServiceTyped(): T? {
       return ContextCompat.getSystemService(this, T::class.java)
   }
   ```

3. DSL-строители (упрощённый пример; требуется доступный no-arg конструктор и учитывайте расходы на рефлексию).
   ```kotlin
   inline fun <reified T> json(init: T.() -> Unit): T {
       return T::class.java.getDeclaredConstructor().newInstance().apply(init)
   }
   ```

4. Избегайте больших inline-функций с `reified`, чтобы не раздувать код.
   ```kotlin
   inline fun <reified T> hugeFunctionWithLotsOfCode() {
       // 100+ строк кода
   }
   ```

## Answer (EN)

`reified` is a modifier for type parameters in inline functions that makes the concrete type argument available inside the inlined function body at call sites. On the JVM, generic types are normally erased (type erasure), so you usually cannot access `T` at runtime. With `reified` + `inline`, the compiler substitutes the actual type during inlining so you can use `T::class`, `is T` checks, and similar type operations inside such functions.

Important nuance: this does NOT change the fact that the JVM uses type erasure globally; it only gives you access to the concrete type within inlined code where the compiler knows the type argument.

### Problem: Type Erasure in Java/Kotlin

```kotlin
// - DOESN'T WORK - type T is erased at compile time
fun <T> isInstanceOf(value: Any): Boolean {
    return value is T  // ERROR: Cannot check for instance of erased type
}

// - DOESN'T WORK - cannot obtain T::class
fun <T> createInstance(): T {
    return T::class.java.newInstance()  // ERROR: Cannot use T::class
}

// Old way - pass Class explicitly
fun <T> createInstance(clazz: Class<T>): T {
    return clazz.newInstance() // newInstance() is deprecated and works only for public no-arg constructors
}

// Usage - inconvenient
val user = createInstance(User::class.java)
```

### Solution: Reified + Inline

```kotlin
// With reified - type information is available inside the inlined body
inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T  // OK
}

inline fun <reified T> createInstance(): T {
    // Simplified example; real code should handle constructor availability and exceptions
    return T::class.java.getDeclaredConstructor().newInstance()
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

// With reified - like stdlib's filterIsInstance
inline fun <reified T> List<*>.filterByTypeReified(): List<T> {
    return this.filterIsInstance<T>()
}

// Usage - concise and type-safe
val ints2 = numbers.filterByTypeReified<Int>()
val strings = numbers.filterByTypeReified<String>()
```

#### 2. JSON Deserialization (Gson, Moshi, kotlinx.serialization)

```kotlin
// Without reified - need to pass Type/Class
fun <T> parseJson(json: String, type: Class<T>): T {
    return Gson().fromJson(json, type)
}

val user = parseJson(jsonString, User::class.java)  // Repetitive

// With reified - simpler for non-generic types
inline fun <reified T> Gson.fromJsonReified(json: String): T {
    return fromJson(json, T::class.java)
}

// Usage
val user2 = gson.fromJsonReified<User>(jsonString)

// For generic/complex types
inline fun <reified T> Gson.fromJsonGeneric(json: String): T {
    return fromJson(json, object : TypeToken<T>() {}.type)
}

val users: List<User> = gson.fromJsonGeneric(jsonString)
val map: Map<String, User> = gson.fromJsonGeneric(jsonString)
```

#### 3. Intent Extras in Android

```kotlin
// Without reified - verbose
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

// With reified - concise
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

// Usage
val user2 = intent.getParcelableExtraCompat<User>("user")
val location = intent.getParcelableExtraCompat<Location>("location")
```

#### 4. Type-safe Activity Launch

```kotlin
// Old way
val intent = Intent(context, UserDetailActivity::class.java)
context.startActivity(intent)

// With reified - DSL style
inline fun <reified T : Activity> Context.startActivity(
    configureIntent: Intent.() -> Unit = {}
) {
    val intent = Intent(this, T::class.java)
    intent.configureIntent()
    startActivity(intent)
}

// Usage
context.startActivity<UserDetailActivity> {
    putExtra("user_id", 123)
    putExtra("mode", "edit")
}

context.startActivity<MainActivity>()
```

#### 5. ViewModel Creation

```kotlin
// Without reified - verbose
val viewModel = ViewModelProvider(this)[UserViewModel::class.java]

// With reified extension (simplified example)
inline fun <reified VM : ViewModel> ComponentActivity.viewModel(): Lazy<VM> {
    return lazy {
        ViewModelProvider(this)[VM::class.java]
    }
}

// Usage
class UserActivity : AppCompatActivity() {
    private val viewModel by viewModel<UserViewModel>()
}

// Or for Fragment
inline fun <reified VM : ViewModel> Fragment.viewModel(): Lazy<VM> {
    return lazy {
        ViewModelProvider(this)[VM::class.java]
    }
}
```

#### 6. Dependency Injection (Koin, Kodein)

```kotlin
// Koin-style usage with reified (API may vary by version; illustrative)
inline fun <reified T> koinGet(): T {
    return KoinContext.get().get(T::class) // Illustrative; depends on actual API
}

// Usage
val repository: UserRepository = koinGet()
val apiService: ApiService = koinGet()

// Kodein-style (simplified)
inline fun <reified T : Any> Kodein.instanceTyped(): T {
    return direct.instance(generic<T>()) // Illustrative; real API may differ
}

val db: AppDatabase = kodein.instanceTyped()
```

#### 7. Runtime Type Checking

```kotlin
inline fun <reified T> checkType(value: Any): String {
    return when (value) {
        is T -> "Value is of type ${T::class.simpleName}"
        else -> "Value is NOT of type ${T::class.simpleName}"
    }
}

// Usage
println(checkType<String>("Hello"))  // Value is of type String
println(checkType<String>(123))      // Value is NOT of type String

// Extension form
inline fun <reified T> Any.isType(): Boolean = this is T

val x: Any = "test"
println(x.isType<String>())  // true
println(x.isType<Int>())     // false
```

#### 8. Room Database Queries

```kotlin
// Room with reified (pattern example; requires explicit mapping)
inline fun <reified T> RoomDatabase.getDao(): T {
    return when (T::class) {
        UserDao::class -> userDao() as T
        ProductDao::class -> productDao() as T
        else -> throw IllegalArgumentException("Unknown DAO type")
    }
}

// Usage
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

// Conceptually, this compiles to something like:
fun test() {
    // Function body is inlined with the concrete type arguments
    println("Creating list of User")
    val users = emptyList<User>()

    println("Creating list of Product")
    val products = emptyList<Product>()
}
```

Key point: the compiler inlines the function body at the call site, substituting the concrete types for `T` where it knows them. That's why `T::class` and `is T` checks work here, despite JVM type erasure.

### Reified Limitations

```kotlin
// ALLOWED
inline fun <reified T> getClassName() = T::class.simpleName
inline fun <reified T> isInstance(obj: Any) = obj is T
inline fun <reified T> createArray(size: Int) = arrayOfNulls<T>(size)

// NOT ALLOWED - function with reified parameter must be inline
fun <reified T> nonInlineFunction() {}  // ERROR: reified type parameters are only allowed in inline functions

// IMPORTANT - reified type parameters are only allowed in inline functions.
// Inline members cannot be open/override and cannot be declared in interfaces,
// so you cannot use reified as a generic virtual contract.
interface Repository<T> {
    // Incorrect here: inline/reified cannot be used in this context
    // fun <reified R> find(): R
}

// NOT ALLOWED - value parameters cannot be reified
inline fun test(reified param: Any) {}  // ERROR: only type parameters can be reified
```

### Comparison of Approaches

```kotlin
// 1. Without generics - code duplication
fun parseUser(json: String): User = gson.fromJson(json, User::class.java)
fun parseProduct(json: String): Product = gson.fromJson(json, Product::class.java)
// ... many more functions

// 2. Generic without reified - need to pass Class
fun <T> parse(json: String, clazz: Class<T>): T = gson.fromJson(json, clazz)

val user = parse(jsonString, User::class.java)

// 3. Generic with reified - concise
inline fun <reified T> parseReified(json: String): T = gson.fromJson(json, T::class.java)

val user2 = parseReified<User>(jsonString)
```

### Advanced Patterns

#### Multiple Reified Parameters

```kotlin
inline fun <reified K, reified V> createMap(): MutableMap<K, V> {
    println("Creating Map<${K::class.simpleName}, ${V::class.simpleName}>")
    return mutableMapOf()
}

val userMap = createMap<Int, User>()  // MutableMap<Int, User>
```

#### Reified with Bounds

```kotlin
inline fun <reified T : Number> sumOf(vararg values: T): Double {
    return values.sumOf { it.toDouble() }
}

val sum1 = sumOf(1, 2, 3)
val sum2 = sumOf(1.5, 2.5, 3.5)
```

#### Reified for Reflection

```kotlin
inline fun <reified T> getAnnotations(): List<Annotation> {
    return T::class.annotations
}

@Deprecated("Use UserV2")
data class User(val name: String)

val annotations = getAnnotations<User>()
annotations.forEach { println(it) }  // @Deprecated(...)
```

#### Safe Cast with Reified

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
// Reified functions are inline - call overhead is removed (but reflection may still be expensive)
inline fun <reified T> create(): T = T::class.java.getDeclaredConstructor().newInstance()

// Each call is inlined with its concrete type
val user = create<User>()
val product = create<Product>()

// If the function body is large and used with many different types,
// inlining can cause code bloat. Prefer small, focused reified helpers.
```

### Best Practices

1. Use reified for type-safe APIs.
   ```kotlin
   inline fun <reified T> Bundle.getTyped(key: String): T? = get(key) as? T
   ```

2. Combine with extension functions.
   ```kotlin
   inline fun <reified T> Context.getSystemServiceTyped(): T? {
       return ContextCompat.getSystemService(this, T::class.java)
   }
   ```

3. DSL-style builders (simplified; require accessible no-arg constructor and consider reflection overhead).
   ```kotlin
   inline fun <reified T> json(init: T.() -> Unit): T {
       return T::class.java.getDeclaredConstructor().newInstance().apply(init)
   }
   ```

4. Avoid large inline reified functions to reduce code bloat.
   ```kotlin
   // Not ideal: big function body will be duplicated for each T
   inline fun <reified T> hugeFunctionWithLotsOfCode() {
       // 100+ lines of code
   }
   ```

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Дополнительные вопросы (RU)

- В чем ключевые отличия этого механизма от Java?
- В каких практических сценариях вы бы использовали `reified`?
- Каковы типичные ошибки и подводные камни при использовании `reified`?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions

- [[q-inline-functions--kotlin--medium]]
- [[q-compose-side-effects-coroutines--kotlin--medium]]
- [[q-suspending-vs-blocking--kotlin--medium]]

## Связанные вопросы (RU)

- [[q-inline-functions--kotlin--medium]]
- [[q-compose-side-effects-coroutines--kotlin--medium]]
- [[q-suspending-vs-blocking--kotlin--medium]]
