---
id: cs-032
title: Where to Call Suspend Functions / Где можно вызывать suspend-функции
aliases:
- Suspend Functions Call Context
- Контекст вызова suspend-функций
topic: cs
subtopics:
- coroutines
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-cs
related:
- c-coroutines
created: 2025-10-15
updated: 2025-11-11
tags:
- coroutines
- difficulty/medium
- kotlin
- suspend-functions
sources:
- https://kotlinlang.org/docs/composing-suspending-functions.html
anki_cards:
- slug: cs-suspend-0-en
  language: en
  anki_id: 1768455796694
  synced_at: '2026-01-25T13:01:16.947389'
- slug: cs-suspend-0-ru
  language: ru
  anki_id: 1768455796720
  synced_at: '2026-01-25T13:01:16.949601'
---
# Вопрос (RU)
> Где можно вызывать suspend-функции?

# Question (EN)
> Where can you call suspend functions?

---

## Ответ (RU)

**Теория контекста вызова suspend-функций (Kotlin):**
Suspend-функции в Kotlin можно вызывать только из кода, который уже выполняется в контексте корутины: из других suspend-функций или из блоков, создающих/предоставляющих корутину. Валидные контексты: другие suspend-функции, `launch {}`, `async {}`, `runBlocking {}`, `coroutineScope {}`, `supervisorScope {}`, `withContext {}`, `flow {}`-билдеры и другие API, принимающие suspend-лямбды. Нельзя вызывать напрямую из обычной функции — нужно либо сделать её `suspend`, либо запустить корутину через билдер.

**Определение:**

*Теория:* `suspend`-функция требует, чтобы её вызов происходил из приостановимого контекста корутины. Прямой вызов из обычной функции (которая не является `suspend` и не находится внутри suspend-лямбды корутинного API) приводит к ошибке компиляции. Нужно либо обернуть вызов в корутинный билдер (например, `launch`, `async`, `runBlocking`), либо вызывать из другой `suspend`-функции/`suspend`-лямбды. Ключ: suspend-функции — операции только для корутинного (приостановимого) контекста.

**1. Из других suspend-функций:**
*Теория:* Одна suspend-функция может напрямую вызывать другие suspend-функции. Дополнительный корутинный билдер не нужен — мы уже находимся в приостановимом контексте. Это позволяет композицию и цепочки suspend-вызовов.

```kotlin
// ✅ Другая suspend-функция
suspend fun fetchUserData(userId: Int): UserData {
    val profile = fetchUserProfile(userId)  // ✅ OK
    val settings = fetchUserSettings(userId)  // ✅ OK
    return UserData(profile, settings)
}

// ✅ Композиция suspend-функций
suspend fun processData(id: Int): Result {
    val data = fetchData(id)          // suspend-вызов
    val validated = validateData(data) // suspend-вызов
    return transformData(validated)    // suspend-вызов
}
```

**2. Из билдера `launch {}`:**
*Теория:* `launch {}` создаёт корутину и предоставляет контекст для suspend-вызовов. «Fire-and-forget» — результат не возвращается, используется для фоновых операций.

```kotlin
// ✅ launch-билдер
fun loadData() {
    CoroutineScope(Dispatchers.IO).launch {
        val data = fetchData()  // ✅ OK
        println(data)
    }
}

// ✅ Android ViewModel
class MyViewModel : ViewModel() {
    fun loadUser(id: Int) {
        viewModelScope.launch {
            val user = fetchUser(id)  // ✅ OK
            _userState.value = user
        }
    }
}
```

**3. Из билдера `async {}`:**
*Теория:* `async {}` создаёт корутину с результатом и возвращает `Deferred<T>`. Можно вызывать suspend-функции для параллельного выполнения и затем получать результаты через `await()`.

```kotlin
// ✅ async-билдер
suspend fun loadParallelData(): CombinedData = coroutineScope {
    val userData = async { fetchUserData(1) }     // ✅ OK
    val postsData = async { fetchPostsData(1) }   // ✅ OK
    val settingsData = async { fetchSettings() }  // ✅ OK

    CombinedData(
        user = userData.await(),
        posts = postsData.await(),
        settings = settingsData.await()
    )
}
```

**4. Из `runBlocking {}`:**
*Теория:* `runBlocking {}` создаёт корутину и блокирует текущий поток до завершения её работы. Используется для тестов, `main`-функций, мостика между синхронным и асинхронным кодом. Блокирует поток — не подходит для долгих операций в продакшене на UI-потоке.

```kotlin
// ✅ runBlocking для теста
fun testFetchUser() = runBlocking {
    val user = fetchUser(1)  // ✅ OK
    assertEquals("User 1", user.name)
}

// ✅ main-функция
fun main() = runBlocking {
    val data = fetchData()  // ✅ OK
    println(data)
}
```

**5. Из `withContext {}`:**
*Теория:* `withContext(...)` — suspend-функция, которая переключает диспетчер/контекст, но не создаёт новую корутину уровня structured concurrency; она сама должна вызываться из suspend-контекста. Внутри её блока также можно вызывать другие suspend-функции.

```kotlin
// ✅ withContext — переключение диспетчера
suspend fun saveToDatabase(data: String) {
    withContext(Dispatchers.IO) {  // ✅ OK
        val validated = validateData(data)
        database.save(validated)
    }
}

suspend fun processOnMain(data: String) {
    withContext(Dispatchers.Main) {  // ✅ OK
        val processed = processData(data)
        updateUI(processed)
    }
}
```

**6. Из билдеров `flow {}`:**
*Теория:* `flow {}`-билдер запускает код в корутинном контексте. Внутри можно вызывать suspend-функции и приостанавливающие операции (`emit`, `delay` и т.д.).

```kotlin
// ✅ flow-билдер
fun getUserFlow(): Flow<User> = flow {
    val user = fetchUser(1)  // ✅ OK - suspend-вызов
    emit(user)

    delay(1000)              // ✅ OK - suspend-вызов
    emit(fetchUser(2))       // ✅ OK - suspend-вызов
}
```

**7. Нельзя вызывать напрямую из обычных функций:**
*Теория:* Обычная функция сама по себе не является приостановимым контекстом. Нельзя сделать прямой вызов suspend-функции, если вы не находитесь внутри `suspend`-функции или suspend-лямбды корутинного API. Нужно либо:
- объявить функцию как `suspend`, либо
- внутри обычной функции запустить корутину через билдер (`launch`, `async`, `runBlocking` и т.п.) и вызывать suspend-функции уже там.

```kotlin
// ❌ Обычная функция — ошибка компиляции
fun regularFunction() {
    val data = fetchData()  // ❌ Compilation error!
    // "Suspend function 'fetchData' should be called only from a coroutine or another suspend function"
}

// ✅ Решение 1: сделать функцию suspend
suspend fun suspendFunction() {
    val data = fetchData()  // ✅ OK
}

// ✅ Решение 2: использовать корутинный билдер
fun regularFunctionFixed() {
    CoroutineScope(Dispatchers.IO).launch {
        val data = fetchData()  // ✅ OK
    }
}
```

**Summary (RU):**

| `Context` | Можно вызывать suspend? | Блокирует поток? | Назначение |
|---------|-------------------------|------------------|-----------|
| Другая suspend-функция | ✅ Да | Нет | Последовательные suspend-вызовы |
| `launch {}` | ✅ Да | Нет | Фоновые задачи (fire-and-forget) |
| `async {}` | ✅ Да | Нет | Параллельное выполнение |
| `runBlocking {}` | ✅ Да | **Да** | Тесты, `main` |
| `coroutineScope {}` | ✅ Да | Нет | Структурированная конкурентность |
| `withContext {}` | ✅ Да | Нет (только приостановка) | Смена диспетчера |
| `flow {}` | ✅ Да | Нет | Поток значений |
| Обычная функция | ❌ Нет (напрямую) | - | Нужен билдер или `suspend` |

---

## Answer (EN)

**Suspend Functions `Call` `Context` Theory (Kotlin):**
In Kotlin, suspend functions can be called only from code that already runs in a coroutine (suspending) context: from other suspend functions or from blocks/builders that create or provide such a context. Valid contexts include: other suspend functions, `launch {}`, `async {}`, `runBlocking {}`, `coroutineScope {}`, `supervisorScope {}`, `withContext {}`, `flow {}` builders, and other APIs that accept suspending lambdas. They cannot be called directly from a regular function; you must either make it `suspend` or start a coroutine via a builder.

**Definition:**

*Theory:* A `suspend` function requires its call site to be in a suspending coroutine context. A direct call from a non-suspend regular function (not inside a suspending lambda of coroutine APIs) is a compilation error. You must either wrap the call into a coroutine builder (e.g., `launch`, `async`, `runBlocking`) or call it from another `suspend` function/suspending lambda. Key idea: suspend functions are coroutine-only (suspending-context-only) operations.

**1. From other suspend functions:**
*Theory:* A suspend function can directly call other suspend functions. No additional coroutine builder is needed because we are already in a suspending context. This enables composition and chaining.

```kotlin
// ✅ Other suspend function
suspend fun fetchUserData(userId: Int): UserData {
    val profile = fetchUserProfile(userId)  // ✅ OK
    val settings = fetchUserSettings(userId)  // ✅ OK
    return UserData(profile, settings)
}

// ✅ Composition of suspend functions
suspend fun processData(id: Int): Result {
    val data = fetchData(id)           // suspend call
    val validated = validateData(data) // suspend call
    return transformData(validated)    // suspend call
}
```

**2. From `launch {}` builder:**
*Theory:* `launch {}` creates a coroutine and provides a context for suspend calls. It is fire-and-forget — it does not return a result; good for background work.

```kotlin
// ✅ launch builder
fun loadData() {
    CoroutineScope(Dispatchers.IO).launch {
        val data = fetchData()  // ✅ OK
        println(data)
    }
}

// ✅ Android ViewModel
class MyViewModel : ViewModel() {
    fun loadUser(id: Int) {
        viewModelScope.launch {
            val user = fetchUser(id)  // ✅ OK
            _userState.value = user
        }
    }
}
```

**3. From `async {}` builder:**
*Theory:* `async {}` creates a coroutine with a result and returns `Deferred<T>`. You can call suspend functions for concurrent execution and get results via `await()`.

```kotlin
// ✅ async builder
suspend fun loadParallelData(): CombinedData = coroutineScope {
    val userData = async { fetchUserData(1) }     // ✅ OK
    val postsData = async { fetchPostsData(1) }   // ✅ OK
    val settingsData = async { fetchSettings() }  // ✅ OK

    CombinedData(
        user = userData.await(),
        posts = postsData.await(),
        settings = settingsData.await()
    )
}
```

**4. From `runBlocking {}`:**
*Theory:* `runBlocking {}` starts a coroutine and blocks the current thread until it completes. Use in tests, `main` functions, and to bridge synchronous and asynchronous code. It blocks the thread, so avoid long-running work on UI threads in production.

```kotlin
// ✅ runBlocking for tests
fun testFetchUser() = runBlocking {
    val user = fetchUser(1)  // ✅ OK
    assertEquals("User 1", user.name)
}

// ✅ main function
fun main() = runBlocking {
    val data = fetchData()  // ✅ OK
    println(data)
}
```

**5. From `withContext {}`:**
*Theory:* `withContext(...)` is a suspend function that switches the dispatcher/context. It must itself be called from a suspending context. Inside its block you can call other suspend functions.

```kotlin
// ✅ withContext switch dispatcher
suspend fun saveToDatabase(data: String) {
    withContext(Dispatchers.IO) {  // ✅ OK
        val validated = validateData(data)
        database.save(validated)
    }
}

suspend fun processOnMain(data: String) {
    withContext(Dispatchers.Main) {  // ✅ OK
        val processed = processData(data)
        updateUI(processed)
    }
}
```

**6. From `flow {}` builders:**
*Theory:* The `flow {}` builder runs its body in a coroutine context. You can call suspend functions and suspending operations (`emit`, `delay`, etc.) inside.

```kotlin
// ✅ flow builder
fun getUserFlow(): Flow<User> = flow {
    val user = fetchUser(1)  // ✅ OK - suspend call
    emit(user)

    delay(1000)              // ✅ OK - suspend call
    emit(fetchUser(2))       // ✅ OK - suspend call
}
```

**7. Cannot call directly from regular functions:**
*Theory:* A plain regular function is not itself a suspending context. You cannot directly call a suspend function from it unless you are inside a coroutine started by a builder or inside a suspending lambda. To call suspend functions, either:
- mark the function as `suspend`, or
- start a coroutine via a builder (`launch`, `async`, `runBlocking`, etc.) inside it and call suspend functions from there.

```kotlin
// ❌ Regular function - compilation error
fun regularFunction() {
    val data = fetchData()  // ❌ Compilation error!
    // "Suspend function 'fetchData' should be called only from a coroutine or another suspend function"
}

// ✅ Solution 1: Make function suspend
suspend fun suspendFunction() {
    val data = fetchData()  // ✅ OK
}

// ✅ Solution 2: Use coroutine builder
fun regularFunctionFixed() {
    CoroutineScope(Dispatchers.IO).launch {
        val data = fetchData()  // ✅ OK
    }
}
```

**Summary:**

| `Context` | Can `Call` Suspend? | Blocks `Thread`? | Use Case |
|---------|-------------------|----------------|----------|
| Another suspend function | ✅ Yes | No | Sequential suspend calls |
| `launch {}` | ✅ Yes | No | Fire-and-forget |
| `async {}` | ✅ Yes | No | Parallel execution |
| `runBlocking {}` | ✅ Yes | **Yes** | Tests, main function |
| `coroutineScope {}` | ✅ Yes | No | Structured concurrency |
| `withContext {}` | ✅ Yes | No (suspends only) | Change dispatcher |
| `flow {}` | ✅ Yes | No | Stream of values |
| Regular function | ❌ No (directly) | - | Must use builder or make it suspend |

---

## Дополнительные Вопросы (RU)

- В чем разница между `launch` и `async`?
- Что произойдет, если вызвать `suspend`-функцию из обычной функции напрямую?
- Как работает `withContext` внутренне?

## Follow-ups

- What is the difference between `launch` and `async`?
- What happens when you call a suspend function from a regular function?
- How does `withContext` work internally?

## Связанные Вопросы (RU)

### Предпосылки (проще)
- Базовые понятия корутин
- Понимание `suspend`-функций

### Связанные (такой Же уровень)
- [[q-how-to-create-suspend-function--kotlin--medium]] — создание `suspend`-функций
- [[q-launch-vs-async-await--kotlin--medium]] — различия `launch` и `async`

### Продвинутые (сложнее)
- Продвинутые паттерны корутин
- Внутреннее устройство `suspend`-функций
- Отмена корутин

## Related Questions

### Prerequisites (Easier)
- Basic coroutines concepts
- Understanding of suspend functions

### Related (Same Level)
- [[q-how-to-create-suspend-function--kotlin--medium]] - Creating suspend functions
- [[q-launch-vs-async-await--kotlin--medium]] - `launch` vs `async`

### Advanced (Harder)
- Advanced coroutine patterns
- Suspend function internals
- `Coroutine` cancellation

## Ссылки (RU)

- [[c-coroutines]]
- Официальная документация Kotlin по композиции `suspend`-функций: "https://kotlinlang.org/docs/composing-suspending-functions.html"

## References

- [[c-coroutines]]
- "https://kotlinlang.org/docs/composing-suspending-functions.html"