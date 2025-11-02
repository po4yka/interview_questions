---
id: cs-032
title: "Where to Call Suspend Functions / Где можно вызывать suspend-функции"
aliases: ["Suspend Functions Call Context", "Контекст вызова suspend-функций"]
topic: cs
subtopics: [async-programming, coroutines, suspend-functions]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-how-to-create-suspend-function--programming-languages--medium, q-launch-vs-async-await--programming-languages--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [async-programming, coroutines, difficulty/medium, kotlin, suspend-functions]
sources: [https://kotlinlang.org/docs/composing-suspending-functions.html]
date created: Saturday, November 1st 2025, 1:26:12 pm
date modified: Saturday, November 1st 2025, 5:43:28 pm
---

# Вопрос (RU)
> Где можно вызывать suspend-функции?

# Question (EN)
> Where can you call suspend functions?

---

## Ответ (RU)

**Теория Suspend Functions Context:**
Suspend functions can only be called from **coroutines**. Valid contexts: other suspend functions, launch {}, async {}, runBlocking {}, coroutineScope {}, supervisorScope {}, withContext {}, flow {} builders. Cannot call from regular functions - must use coroutine builder.

**Определение:**

*Теория:* Suspend function requires coroutine context для execution. Cannot call directly из regular function - compilation error. Must wrap в coroutine builder или another suspend function. Key: suspend functions are coroutine-only operations.

**1. From other suspend functions:**
*Теория:* Suspend function can call other suspend functions directly. No need для coroutine builder - already in coroutine context. Allows chaining suspend calls.

```kotlin
// ✅ Other suspend function
suspend fun fetchUserData(userId: Int): UserData {
    val profile = fetchUserProfile(userId)  // ✅ OK
    val settings = fetchUserSettings(userId)  // ✅ OK
    return UserData(profile, settings)
}

// ✅ Composition of suspend functions
suspend fun processData(id: Int): Result {
    val data = fetchData(id)  // suspend call
    val validated = validateData(data)  // suspend call
    return transformData(validated)  // suspend call
}
```

**2. From launch {} builder:**
*Теория:* `launch {}` creates coroutine, provides context для suspend calls. Fire-and-forget pattern - no result returned. Suitable для background work.

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

**3. From async {} builder:**
*Теория:* `async {}` creates coroutine with result. Returns `Deferred<T>`. Can call suspend functions для parallel execution. Use `await()` для get result.

```kotlin
// ✅ async builder
suspend fun loadParallelData(): CombinedData = coroutineScope {
    val userData = async { fetchUserData(1) }  // ✅ OK
    val postsData = async { fetchPostsData(1) }  // ✅ OK
    val settingsData = async { fetchSettings() }  // ✅ OK

    CombinedData(
        user = userData.await(),
        posts = postsData.await(),
        settings = settingsData.await()
    )
}
```

**4. From runBlocking {}:**
*Теория:* `runBlocking {}` blocks current thread пока coroutine completes. Use для tests, main functions, bridging sync/async code. **Blocks thread** - not suitable для production async code.

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

**5. From withContext {}:**
*Теория:* `withContext {}` switches dispatcher и provides coroutine context. Can call suspend functions во всех dispatchers. Use для change execution context.

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

**6. From flow {} builders:**
*Теория:* `flow {}` builder provides coroutine context. Can call suspend functions внутри. Emits values для downstream collectors.

```kotlin
// ✅ flow builder
fun getUserFlow(): Flow<User> = flow {
    val user = fetchUser(1)  // ✅ OK - suspend call
    emit(user)

    delay(1000)  // ✅ OK - suspend call
    emit(fetchUser(2))
}
```

**7. Cannot call from regular functions:**
*Теория:* Regular functions not in coroutine context. Cannot call suspend functions directly. Must use coroutine builder или make function suspend.

```kotlin
// ❌ Regular function - compilation error
fun regularFunction() {
    val data = fetchData()  // ❌ Compilation error!
    // "Suspend function should be called only from a coroutine"
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

| Context | Can Call Suspend? | Blocks Thread? | Use Case |
|---------|-------------------|----------------|----------|
| Another suspend function | ✅ Yes | No | Sequential suspend calls |
| `launch {}` | ✅ Yes | No | Fire-and-forget |
| `async {}` | ✅ Yes | No | Parallel execution |
| `runBlocking {}` | ✅ Yes | **Yes** | Tests, main function |
| `coroutineScope {}` | ✅ Yes | No | Structured concurrency |
| `withContext {}` | ✅ Yes | No | Change dispatcher |
| `flow {}` | ✅ Yes | No | Stream of values |
| Regular function | ❌ No | - | Must use builder |

## Answer (EN)

**Suspend Functions Context Theory:**
Suspend functions can only be called from **coroutines**. Valid contexts: other suspend functions, launch {}, async {}, runBlocking {}, coroutineScope {}, supervisorScope {}, withContext {}, flow {} builders. Cannot call from regular functions - must use coroutine builder.

**Definition:**

*Theory:* Suspend function requires coroutine context for execution. Cannot call directly from regular function - compilation error. Must wrap in coroutine builder or another suspend function. Key: suspend functions are coroutine-only operations.

**1. From other suspend functions:**
*Theory:* Suspend function can call other suspend functions directly. No need for coroutine builder - already in coroutine context. Allows chaining suspend calls.

```kotlin
// ✅ Other suspend function
suspend fun fetchUserData(userId: Int): UserData {
    val profile = fetchUserProfile(userId)  // ✅ OK
    val settings = fetchUserSettings(userId)  // ✅ OK
    return UserData(profile, settings)
}

// ✅ Composition of suspend functions
suspend fun processData(id: Int): Result {
    val data = fetchData(id)  // suspend call
    val validated = validateData(data)  // suspend call
    return transformData(validated)  // suspend call
}
```

**2. From launch {} builder:**
*Theory:* `launch {}` creates coroutine, provides context for suspend calls. Fire-and-forget pattern - no result returned. Suitable for background work.

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

**3. From async {} builder:**
*Theory:* `async {}` creates coroutine with result. Returns `Deferred<T>`. Can call suspend functions for parallel execution. Use `await()` to get result.

```kotlin
// ✅ async builder
suspend fun loadParallelData(): CombinedData = coroutineScope {
    val userData = async { fetchUserData(1) }  // ✅ OK
    val postsData = async { fetchPostsData(1) }  // ✅ OK
    val settingsData = async { fetchSettings() }  // ✅ OK

    CombinedData(
        user = userData.await(),
        posts = postsData.await(),
        settings = settingsData.await()
    )
}
```

**4. From runBlocking {}:**
*Theory:* `runBlocking {}` blocks current thread until coroutine completes. Use for tests, main functions, bridging sync/async code. **Blocks thread** - not suitable for production async code.

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

**5. From withContext {}:**
*Theory:* `withContext {}` switches dispatcher and provides coroutine context. Can call suspend functions in all dispatchers. Use to change execution context.

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

**6. From flow {} builders:**
*Theory:* `flow {}` builder provides coroutine context. Can call suspend functions inside. Emits values to downstream collectors.

```kotlin
// ✅ flow builder
fun getUserFlow(): Flow<User> = flow {
    val user = fetchUser(1)  // ✅ OK - suspend call
    emit(user)

    delay(1000)  // ✅ OK - suspend call
    emit(fetchUser(2))
}
```

**7. Cannot call from regular functions:**
*Theory:* Regular functions not in coroutine context. Cannot call suspend functions directly. Must use coroutine builder or make function suspend.

```kotlin
// ❌ Regular function - compilation error
fun regularFunction() {
    val data = fetchData()  // ❌ Compilation error!
    // "Suspend function should be called only from a coroutine"
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

| Context | Can Call Suspend? | Blocks Thread? | Use Case |
|---------|-------------------|----------------|----------|
| Another suspend function | ✅ Yes | No | Sequential suspend calls |
| `launch {}` | ✅ Yes | No | Fire-and-forget |
| `async {}` | ✅ Yes | No | Parallel execution |
| `runBlocking {}` | ✅ Yes | **Yes** | Tests, main function |
| `coroutineScope {}` | ✅ Yes | No | Structured concurrency |
| `withContext {}` | ✅ Yes | No | Change dispatcher |
| `flow {}` | ✅ Yes | No | Stream of values |
| Regular function | ❌ No | - | Must use builder |

---

## Follow-ups

- What is the difference between launch and async?
- What happens when you call a suspend function from a regular function?
- How does withContext work internally?

## Related Questions

### Prerequisites (Easier)
- Basic coroutines concepts
- Understanding of suspend functions

### Related (Same Level)
- [[q-how-to-create-suspend-function--programming-languages--medium]] - Creating suspend functions
- [[q-launch-vs-async-await--programming-languages--medium]] - launch vs async

### Advanced (Harder)
- Advanced coroutine patterns
- Suspend function internals
- Coroutine cancellation
