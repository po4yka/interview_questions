---
topic: kotlin
tags:
  - kotlin
  - inline-functions
  - performance
  - limitations
difficulty: medium
status: draft
---

# Когда нельзя использовать inline функции?

**English**: When can't you use inline functions?

## Answer (EN)
Хотя `inline` функции повышают производительность за счет встраивания кода, существуют случаи, когда их использование невозможно, нежелательно или даже вредно.

### 1. Нельзя сохранить лямбду в переменную

Inline функция встраивает код лямбды в место вызова, поэтому нельзя сохранить лямбду для отложенного выполнения.

```kotlin
// - ОШИБКА КОМПИЛЯЦИИ
inline fun processData(callback: () -> Unit) {
    val storedCallback = callback  // ERROR: Illegal usage of inline-parameter
    // Нельзя сохранить callback для использования позже
}

// - ОШИБКА
inline fun deferExecution(action: () -> Unit) {
    val deferredAction = action
    Handler(Looper.getMainLooper()).post(deferredAction)  // ERROR
}

// ✓ ПРАВИЛЬНО - использовать noinline
inline fun processData(noinline callback: () -> Unit) {
    val storedCallback = callback  // OK
    Handler(Looper.getMainLooper()).post(storedCallback)
}

// ✓ ПРАВИЛЬНО - выполнить inline лямбду сразу
inline fun processDataNow(callback: () -> Unit) {
    callback()  // OK - прямой вызов
}
```

### 2. Нельзя передать лямбду в обычную (не-inline) функцию

```kotlin
// - ОШИБКА КОМПИЛЯЦИИ
inline fun withLogging(action: () -> Unit) {
    log("Starting")
    executeInBackground(action)  // ERROR: Illegal usage
    log("Finished")
}

fun executeInBackground(task: () -> Unit) {
    Thread { task() }.start()
}

// ✓ ПРАВИЛЬНО - использовать noinline
inline fun withLogging(noinline action: () -> Unit) {
    log("Starting")
    executeInBackground(action)  // OK
    log("Finished")
}

// ✓ АЛЬТЕРНАТИВА - не использовать inline
fun withLogging(action: () -> Unit) {
    log("Starting")
    executeInBackground(action)
    log("Finished")
}
```

### 3. Рекурсивные функции не могут быть inline

Встраивание рекурсивной функции привело бы к бесконечному росту кода.

```kotlin
// - ОШИБКА КОМПИЛЯЦИИ
inline fun factorial(n: Int): Int {  // ERROR: Inline function cannot be recursive
    return if (n <= 1) 1 else n * factorial(n - 1)
}

// ✓ ПРАВИЛЬНО - убрать inline
fun factorial(n: Int): Int {
    return if (n <= 1) 1 else n * factorial(n - 1)
}

// ✓ АЛЬТЕРНАТИВА - tailrec вместо inline
tailrec fun factorial(n: Int, acc: Int = 1): Int {
    return if (n <= 1) acc else factorial(n - 1, n * acc)
}
```

### 4. Большие функции - увеличение размера кода

Inline функции копируют свой код в каждое место вызова, что может значительно увеличить размер APK.

```kotlin
// - ПЛОХАЯ ПРАКТИКА - большая inline функция
inline fun processUserData(user: User, callback: (Result) -> Unit) {
    // 100+ строк кода
    val validatedUser = validateUser(user)
    val enrichedUser = enrichUserData(validatedUser)
    val processedUser = applyBusinessLogic(enrichedUser)
    val savedUser = saveToDatabase(processedUser)
    val notificationSent = sendNotification(savedUser)
    val analyticsLogged = logAnalytics(savedUser)
    // ... еще 90 строк

    callback(Result.Success(savedUser))
}

// Каждый вызов добавит ~100 строк кода!
processUserData(user1) { }  // +100 строк в bytecode
processUserData(user2) { }  // +100 строк в bytecode
processUserData(user3) { }  // +100 строк в bytecode

// ✓ ПРАВИЛЬНО - большие функции НЕ делать inline
fun processUserData(user: User, callback: (Result) -> Unit) {
    // Код выполняется только в одном месте
    // Все вызовы ссылаются на одну функцию
}
```

**Рекомендация**: Inline использовать только для маленьких функций (1-3 строки).

### 5. Функции с высоким порядком вызовов

```kotlin
// - ПЛОХАЯ ПРАКТИКА - inline функция вызывается очень часто
inline fun log(message: String) {
    println("[${System.currentTimeMillis()}] $message")
}

// Если вызывается 10,000 раз, код будет продублирован 10,000 раз
repeat(10_000) {
    log("Iteration $it")  // Раздутие кода!
}

// ✓ ПРАВИЛЬНО - обычная функция
fun log(message: String) {
    println("[${System.currentTimeMillis()}] $message")
}
```

### 6. Функции с reified типами без необходимости

```kotlin
// - ИЗБЫТОЧНО - reified без реальной необходимости
inline fun <reified T> createInstance(): T {
    // Просто создаем объект, reified не нужен
    return T::class.java.newInstance()
}

// ✓ ПРАВИЛЬНО - использовать reified только когда нужен тип в runtime
inline fun <reified T> Gson.fromJson(json: String): T {
    // Reified нужен чтобы передать T::class.java в Gson
    return fromJson(json, T::class.java)
}

// Правильное использование reified
inline fun <reified T : Activity> Context.startActivity() {
    val intent = Intent(this, T::class.java)
    startActivity(intent)
}

// Использование
context.startActivity<MainActivity>()  // Без явного .java
```

### 7. Public API библиотек

Inline функции встраиваются в клиентский код, что усложняет обновление библиотеки.

```kotlin
// - ПЛОХАЯ ПРАКТИКА - inline в public API библиотеки
// library version 1.0
inline fun processRequest(url: String, callback: (Response) -> Unit) {
    // Реализация версии 1.0
    val response = httpClient.get(url)
    callback(response)
}

// Если изменить реализацию в version 1.1:
inline fun processRequest(url: String, callback: (Response) -> Unit) {
    // Новая реализация версии 1.1
    val response = newHttpClient.get(url)  // Новый клиент!
    callback(response)
}

// Проблема: приложения, скомпилированные с 1.0, используют СТАРЫЙ код
// даже если обновили библиотеку до 1.1!

// ✓ ПРАВИЛЬНО - обычная функция в public API
fun processRequest(url: String, callback: (Response) -> Unit) {
    val response = httpClient.get(url)
    callback(response)
}

// Теперь обновление библиотеки сразу применит новую реализацию
```

### 8. Функции с внутренними/private зависимостями

```kotlin
// - ОШИБКА - inline функция обращается к private полю
class UserManager {
    private val cache = mutableMapOf<Int, User>()

    inline fun getUser(id: Int): User? {
        // ERROR: Public-API inline function cannot access non-public-API 'cache'
        return cache[id]
    }
}

// ✓ ПРАВИЛЬНО - убрать inline или сделать cache internal
class UserManager {
    internal val cache = mutableMapOf<Int, User>()

    inline fun getUser(id: Int): User? {
        return cache[id]  // OK
    }
}

// ✓ АЛЬТЕРНАТИВА - не использовать inline
class UserManager {
    private val cache = mutableMapOf<Int, User>()

    fun getUser(id: Int): User? {
        return cache[id]
    }
}
```

### 9. Функции с non-local returns в сложных конструкциях

```kotlin
// - СЛОЖНО ДЛЯ ПОНИМАНИЯ
inline fun processItems(items: List<String>) {
    items.forEach { item ->
        if (item.isEmpty()) {
            return  // Non-local return из processItems, НЕ из forEach!
        }
        println(item)
    }
}

fun caller() {
    processItems(listOf("a", "", "c"))
    println("After processItems")  // НЕ ВЫПОЛНИТСЯ если есть пустая строка!
}

// ✓ ПРАВИЛЬНО - использовать явные return или не inline
fun processItems(items: List<String>) {
    items.forEach { item ->
        if (item.isEmpty()) {
            return@forEach  // Локальный return из forEach
        }
        println(item)
    }
}
```

### 10. Когда производительность не критична

```kotlin
// - ИЗБЫТОЧНО - inline без выигрыша в производительности
inline fun formatUserName(firstName: String, lastName: String): String {
    return "$firstName $lastName"
}

// Вызывается 1 раз при загрузке профиля
val name = formatUserName(user.first, user.last)

// ✓ ПРАВИЛЬНО - обычная функция
fun formatUserName(firstName: String, lastName: String): String {
    return "$firstName $lastName"
}

// Inline стоит использовать только когда:
// 1. Функция вызывается часто (в циклах)
// 2. Принимает лямбды (избегает создания объектов)
// 3. Очень маленькая (1-3 строки)
```

### Когда СТОИТ использовать inline

```kotlin
// ✓ ПРАВИЛЬНО - inline для higher-order функций
inline fun <T> measureTime(block: () -> T): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val time = System.currentTimeMillis() - start
    return result to time
}

// ✓ ПРАВИЛЬНО - inline с reified
inline fun <reified T> Intent.getParcelableExtraCompat(key: String): T? {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        getParcelableExtra(key, T::class.java)
    } else {
        @Suppress("DEPRECATION")
        getParcelableExtra(key) as? T
    }
}

// ✓ ПРАВИЛЬНО - маленькие утилиты с лямбдами
inline fun <R> synchronized(lock: Any, block: () -> R): R {
    kotlin.synchronized(lock) {
        return block()
    }
}

// ✓ ПРАВИЛЬНО - DSL builders
inline fun buildUser(init: UserBuilder.() -> Unit): User {
    val builder = UserBuilder()
    builder.init()
    return builder.build()
}
```

### Ключевые правила

| Ситуация | Можно inline? | Причина |
|----------|---------------|---------|
| Маленькая функция с лямбдой | - Да | Оптимизация |
| Большая функция (50+ строк) | - Нет | Раздувание кода |
| Рекурсивная функция | - Нет | Бесконечное встраивание |
| Функция с reified типом | - Да | Необходимо inline |
| Public API библиотеки | WARNING: Осторожно | Проблемы с обновлениями |
| Сохранение лямбды | - Нет | Используйте noinline |
| Часто вызываемая функция | WARNING: Зависит | Баланс размера/скорости |

### Использование noinline и crossinline

```kotlin
// noinline - отключить inline для конкретного параметра
inline fun transaction(
    noinline onError: (Exception) -> Unit,  // Можно сохранить
    crossinline onSuccess: () -> Unit       // Нельзя non-local return
) {
    try {
        db.beginTransaction()
        onSuccess()
        db.setTransactionSuccessful()
    } catch (e: Exception) {
        errorHandler.handle(onError)  // onError можно передать
    } finally {
        db.endTransaction()
    }
}
```

**English**: Cannot use inline when: 1) **Storing lambda** in variable (use `noinline`), 2) **Passing lambda** to non-inline function (`noinline`), 3) **Recursive functions** (infinite inlining), 4) **Large functions** (code bloat), 5) **Frequently called** simple functions (bloat), 6) **Public library API** (update issues), 7) **Accessing private members** from public inline. Use inline only for: small functions with lambdas, `reified` type parameters, DSL builders. Use `noinline` to exclude specific parameters from inlining.
