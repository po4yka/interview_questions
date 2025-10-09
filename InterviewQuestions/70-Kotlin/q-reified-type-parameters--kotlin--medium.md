---
tags:
  - kotlin
  - generics
  - reified
  - inline-functions
  - type-system
difficulty: medium
status: reviewed
---

# Зачем нужен reified в Kotlin?

**English**: What is `reified` for in Kotlin?

## Answer

`reified` — это модификатор для параметров типа в inline функциях, который позволяет сохранить информацию о типе во время выполнения (runtime). Обычно в JVM generic типы стираются (type erasure), но `reified` позволяет обращаться к типу как к обычному классу внутри функции.

### Проблема: Type Erasure в Java/Kotlin

```kotlin
// - НЕ РАБОТАЕТ - тип T стирается во время компиляции
fun <T> isInstanceOf(value: Any): Boolean {
    return value is T  // ERROR: Cannot check for instance of erased type
}

// - НЕ РАБОТАЕТ - нельзя получить Class<T>
fun <T> createInstance(): T {
    return T::class.java.newInstance()  // ERROR: Cannot use T::class
}

// Старый способ - передавать Class явно
fun <T> createInstance(clazz: Class<T>): T {
    return clazz.newInstance()
}

// Использование - неудобно
val user = createInstance(User::class.java)
```

### Решение: reified + inline

```kotlin
// ✓ С reified - тип доступен в runtime
inline fun <reified T> isInstanceOf(value: Any): Boolean {
    return value is T  // OK!
}

inline fun <reified T> createInstance(): T {
    return T::class.java.newInstance()  // OK!
}

// Использование - красиво и просто
val user = createInstance<User>()
val isUser = isInstanceOf<User>(someObject)
```

### Практические примеры

#### 1. Фильтрация коллекций по типу

```kotlin
// Без reified - нужно передавать Class
fun <T> List<*>.filterByType(clazz: Class<T>): List<T> {
    return this.filter { clazz.isInstance(it) }
        .map { it as T }
}

// Использование
val numbers = listOf<Any>(1, "two", 3, "four", 5)
val ints = numbers.filterByType(Int::class.java)  // Громоздко

// ✓ С reified - встроено в Kotlin
inline fun <reified T> List<*>.filterIsInstance(): List<T> {
    return this.filterIsInstance(T::class.java)
}

// Использование - элегантно
val ints = numbers.filterIsInstance<Int>()
val strings = numbers.filterIsInstance<String>()
```

#### 2. JSON десериализация (Gson, Moshi, kotlinx.serialization)

```kotlin
// Без reified - нужно передавать Type/Class
fun <T> parseJson(json: String, type: Class<T>): T {
    return Gson().fromJson(json, type)
}

val user = parseJson(jsonString, User::class.java)  // Повторяющийся код

// ✓ С reified - чище
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

#### 3. Intent extras в Android

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

// ✓ С reified - элегантно
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

#### 4. Запуск Activity с типобезопасностью

```kotlin
// Старый способ
val intent = Intent(context, UserDetailActivity::class.java)
context.startActivity(intent)

// ✓ С reified - DSL стиль
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

#### 5. ViewModel creation

```kotlin
// Без reified - многословно
val viewModel = ViewModelProvider(this)[UserViewModel::class.java]

// ✓ С reified extension
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

#### 7. Проверка типов в runtime

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

#### 8. Room Database queries

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

### Как работает reified под капотом

```kotlin
// Kotlin код
inline fun <reified T> createList(): List<T> {
    println("Creating list of ${T::class.simpleName}")
    return emptyList()
}

fun test() {
    val users = createList<User>()
    val products = createList<Product>()
}

// Компилируется в (примерно):
fun test() {
    // Код функции встраивается с конкретным типом
    println("Creating list of User")
    val users = emptyList<User>()

    println("Creating list of Product")
    val products = emptyList<Product>()
}
```

**Ключевой момент**: Компилятор встраивает (inline) код функции в место вызова, подставляя конкретный тип вместо `T`. Поэтому `T::class` работает - компилятор знает конкретный тип.

### Ограничения reified

```kotlin
// ✓ МОЖНО
inline fun <reified T> getClassName() = T::class.simpleName
inline fun <reified T> isInstance(obj: Any) = obj is T
inline fun <reified T> createArray(size: Int) = Array<T?>(size) { null }

// - НЕЛЬЗЯ - функция ДОЛЖНА быть inline
fun <reified T> nonInlineFunction() {}  // ERROR: reified requires inline

// - НЕЛЬЗЯ - virtual/override функции не могут быть inline
interface Repository<T> {
    fun <reified T> find(): T  // ERROR: reified не работает с interface methods
}

// - НЕЛЬЗЯ - параметры функции не могут быть reified
inline fun test(reified param: Any) {}  // ERROR: только type parameters
```

### Сравнение подходов

```kotlin
// 1. Без generics - дублирование кода
fun parseUser(json: String): User = gson.fromJson(json, User::class.java)
fun parseProduct(json: String): Product = gson.fromJson(json, Product::class.java)
// ... еще 50 функций

// 2. Generic без reified - неудобно
fun <T> parse(json: String, clazz: Class<T>): T = gson.fromJson(json, clazz)

val user = parse(jsonString, User::class.java)  // Повторение типа

// 3. Generic с reified - идеально
inline fun <reified T> parse(json: String): T = gson.fromJson(json, T::class.java)

val user = parse<User>(jsonString)  // Тип указан один раз
```

### Продвинутые паттерны

#### Множественные reified параметры

```kotlin
inline fun <reified K, reified V> createMap(): MutableMap<K, V> {
    println("Creating Map<${K::class.simpleName}, ${V::class.simpleName}>")
    return mutableMapOf()
}

val userMap = createMap<Int, User>()  // Map<Int, User>
```

#### Reified с bounds

```kotlin
inline fun <reified T : Number> sumOf(vararg values: T): Double {
    return values.sumOf { it.toDouble() }
}

val sum1 = sumOf(1, 2, 3)           // Int
val sum2 = sumOf(1.5, 2.5, 3.5)     // Double
```

#### Reified для reflection

```kotlin
inline fun <reified T> getAnnotations(): List<Annotation> {
    return T::class.annotations
}

@Deprecated("Use UserV2")
data class User(val name: String)

val annotations = getAnnotations<User>()
annotations.forEach { println(it) }  // @Deprecated(...)
```

#### Safe cast с reified

```kotlin
inline fun <reified T> Any?.safeCast(): T? {
    return this as? T
}

val obj: Any? = "Hello"
val str = obj.safeCast<String>()  // "Hello"
val num = obj.safeCast<Int>()     // null
```

### Performance consideration

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
