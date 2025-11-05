---
id: kotlin-193
title: "GlobalScope Anti-Pattern / Анти-Паттерн GlobalScope"
aliases: [Antipattern, Globalscope]
topic: kotlin
subtopics: []
question_kind: theory
difficulty: easy
original_language: en
language_tags: []
status: draft
moc: moc-kotlin
related: [q-object-companion-object--kotlin--medium, q-test-dispatcher-types--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy]
date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# Question (EN)
> Why should you avoid using GlobalScope in Android applications?
# Вопрос (RU)
> Почему следует избегать использования GlobalScope в Android приложениях?

---

## Answer (EN)

**GlobalScope is an anti-pattern in Android** because it creates coroutines that are not tied to any lifecycle, leading to memory leaks, wasted resources, and potential crashes.

### What is GlobalScope?

**Definition**: `GlobalScope` is a top-level coroutine scope that lives for the entire lifetime of the application.

```kotlin
// GlobalScope coroutine
GlobalScope.launch {
    // This coroutine lives until manually canceled
    // or the app process is killed
}
```

**Key Characteristics**:
- Lives for entire application lifetime
- Not tied to any component lifecycle
- Doesn't cancel automatically
- Uses application-level context

### Why GlobalScope is Problematic

**Problem 1: Memory Leaks**

```kotlin
// BAD: Memory leak risk
class UserProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        GlobalScope.launch {
            // Loads user data
            val user = repository.loadUser()

            // Activity might be destroyed here!
            // But coroutine is still running
            updateUI(user) // CRASH! View is destroyed
        }
    }

    private fun updateUI(user: User) {
        // Access destroyed views
        textViewName.text = user.name // NullPointerException or worse
    }
}
```

**What Happens**:
1. Activity starts, launches GlobalScope coroutine
2. User rotates device or presses back
3. Activity is destroyed
4. Coroutine keeps running (not tied to Activity lifecycle)
5. Coroutine tries to update destroyed views → **Crash or memory leak**

**Problem 2: Wasted Resources**

```kotlin
// BAD: Wasted network/CPU resources
class SearchActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        searchButton.setOnClickListener {
            GlobalScope.launch {
                // Expensive network call
                val results = searchRepository.search(query)

                // User might have left the screen!
                // But we're still processing results
                displayResults(results)
            }
        }
    }
}
```

**Issue**:
- User navigates away from SearchActivity
- Network call completes anyway
- Results are processed even though nobody needs them
- Wasted bandwidth, battery, CPU

**Problem 3: Unhandled Exceptions**

```kotlin
// BAD: Exceptions can crash the app
GlobalScope.launch {
    // If this throws an exception, it might not be caught
    riskyOperation()
}

// No CoroutineExceptionHandler installed!
// Exception propagates to default handler → app crash
```

**Problem 4: Testing Difficulties**

```kotlin
// BAD: Hard to test
class UserViewModel {
    fun loadUser() {
        GlobalScope.launch {
            val user = repository.getUser()
            _userData.value = user
        }
    }
}

// In test:
@Test
fun testLoadUser() {
    viewModel.loadUser()

    // How do we wait for GlobalScope coroutine to finish?
    // Can't inject TestDispatcher
    // Can't control coroutine timing
}
```

### The Right Way: Lifecycle-Scoped Coroutines

**Solution 1: Use lifecycleScope (Activities/Fragments)**

```kotlin
// GOOD: Tied to Activity lifecycle
class UserProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val user = repository.loadUser()

            // Automatically canceled if Activity is destroyed
            updateUI(user) // Safe!
        }
    }
}
```

**Benefits**:
- Coroutine canceled when Activity destroyed
- No memory leaks
- No wasted resources
- Safe UI updates

**Solution 2: Use viewModelScope (ViewModels)**

```kotlin
// GOOD: Tied to ViewModel lifecycle
class UserViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData

    fun loadUser() {
        viewModelScope.launch {
            val user = repository.getUser()
            _userData.value = user
        }
    }

    // Automatically canceled when ViewModel.onCleared() is called
}
```

**Benefits**:
- Survives configuration changes (rotation)
- Canceled when ViewModel cleared
- Testable with TestDispatcher
- No memory leaks

**Solution 3: Use repeatOnLifecycle for Flow collection**

```kotlin
// BEST: Lifecycle-aware Flow collection
class UserProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Only collect when lifecycle is STARTED
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.userData.collect { user ->
                    updateUI(user)
                }
            }
        }
    }
}
```

**Benefits**:
- Respects lifecycle states
- No updates when app is in background
- Optimal resource usage

### When GlobalScope Might Be Acceptable

**Rare Legitimate Use Cases**:

```kotlin
// WARNING: MAYBE ACCEPTABLE: Application-level singleton
class AnalyticsManager {
    fun logEvent(event: String) {
        // This SHOULD run even if Activity is destroyed
        GlobalScope.launch(Dispatchers.IO) {
            analyticsApi.sendEvent(event)
        }
    }
}
```

**But Even Here, Better Alternatives Exist**:

```kotlin
// BETTER: Custom application-scoped coroutine
class MyApplication : Application() {
    val applicationScope = CoroutineScope(
        SupervisorJob() + Dispatchers.Default
    )

    override fun onTerminate() {
        applicationScope.cancel()
        super.onTerminate()
    }
}

class AnalyticsManager(private val scope: CoroutineScope) {
    fun logEvent(event: String) {
        scope.launch(Dispatchers.IO) {
            analyticsApi.sendEvent(event)
        }
    }
}
```

**Why Better**:
- Explicit scope ownership
- Can inject TestScope in tests
- Can add CoroutineExceptionHandler
- Clear lifecycle management

### Comparison Table

| Aspect | GlobalScope | lifecycleScope/viewModelScope |
|--------|-------------|-------------------------------|
| **Lifetime** | Entire app process | Component lifecycle |
| **Cancellation** | Manual only | Automatic |
| **Memory Leaks** | High risk | Safe |
| **Resource Waste** | Possible | Prevented |
| **Testing** | Difficult | Easy (inject dispatcher) |
| **Exception Handling** | Global default | Scope-specific handler |
| **Android Best Practice** | Anti-pattern | Recommended |

### Common Mistakes and Fixes

**Mistake 1: Background work after user leaves**

```kotlin
// BAD
GlobalScope.launch {
    delay(10000) // 10 second delay
    showNotification()
}

// GOOD - Use WorkManager for deferrable work
val workRequest = OneTimeWorkRequestBuilder<NotificationWorker>()
    .setInitialDelay(10, TimeUnit.SECONDS)
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
```

**Mistake 2: Fire-and-forget network calls**

```kotlin
// BAD
fun sendAnalytics() {
    GlobalScope.launch {
        api.sendEvent(event)
    }
}

// GOOD - Tie to appropriate scope
class MyViewModel : ViewModel() {
    fun sendAnalytics() {
        viewModelScope.launch {
            api.sendEvent(event)
        }
    }
}
```

### Summary

**Why Avoid GlobalScope**:
- Causes memory leaks (holds Activity/Fragment references)
- Wastes resources (continues after component destroyed)
- Hard to test (can't inject TestDispatcher)
- Uncontrolled lifecycle (runs until app dies)
- Exception handling issues (global crash handler)

**Use Instead**:
- `lifecycleScope` for Activities/Fragments
- `viewModelScope` for ViewModels
- Custom scopes with clear lifecycle ownership
- `WorkManager` for background tasks that outlive UI

**Key Principle**: **Always tie coroutines to a lifecycle-aware scope**. If you think you need GlobalScope, you probably need a better architecture or WorkManager instead.

---

## Ответ (RU)

**GlobalScope является анти-паттерном в Android**, потому что создает корутины, не привязанные к жизненному циклу, что приводит к утечкам памяти, потере ресурсов и возможным крэшам.

### Что Такое GlobalScope?

**Определение**: `GlobalScope` - это корутинная область верхнего уровня, которая существует в течение всего времени жизни приложения.

```kotlin
// Корутина в GlobalScope
GlobalScope.launch {
    // Эта корутина живет до ручной отмены
    // или до завершения процесса приложения
}
```

**Ключевые Характеристики**:
- Существует все время жизни приложения
- Не привязана к жизненному циклу компонентов
- Не отменяется автоматически
- Использует контекст уровня приложения

### Почему GlobalScope Проблематичен

**Проблема 1: Утечки Памяти**

```kotlin
// ПЛОХО: Риск утечки памяти
class UserProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        GlobalScope.launch {
            // Загружает данные пользователя
            val user = repository.loadUser()

            // Activity может быть уничтожен здесь!
            // Но корутина все еще работает
            updateUI(user) // КРЭШ! View уничтожен
        }
    }

    private fun updateUI(user: User) {
        // Доступ к уничтоженным view
        textViewName.text = user.name // NullPointerException или хуже
    }
}
```

**Что Происходит**:
1. Activity запускается, запускает корутину в GlobalScope
2. Пользователь поворачивает устройство или нажимает назад
3. Activity уничтожается
4. Корутина продолжает работать (не привязана к жизненному циклу Activity)
5. Корутина пытается обновить уничтоженные view → **Крэш или утечка памяти**

**Проблема 2: Потраченные Ресурсы**

```kotlin
// ПЛОХО: Потеря сетевых/CPU ресурсов
class SearchActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        searchButton.setOnClickListener {
            GlobalScope.launch {
                // Дорогой сетевой запрос
                val results = searchRepository.search(query)

                // Пользователь мог уйти с экрана!
                // Но мы все еще обрабатываем результаты
                displayResults(results)
            }
        }
    }
}
```

**Проблема**:
- Пользователь уходит из SearchActivity
- Сетевой запрос все равно завершается
- Результаты обрабатываются, хотя никому не нужны
- Потраченный трафик, батарея, CPU

**Проблема 3: Необработанные Исключения**

```kotlin
// ПЛОХО: Исключения могут крэшить приложение
GlobalScope.launch {
    // Если это выбросит исключение, оно может не быть перехвачено
    riskyOperation()
}

// CoroutineExceptionHandler не установлен!
// Исключение идет к обработчику по умолчанию → крэш приложения
```

**Проблема 4: Сложности с Тестированием**

```kotlin
// ПЛОХО: Сложно тестировать
class UserViewModel {
    fun loadUser() {
        GlobalScope.launch {
            val user = repository.getUser()
            _userData.value = user
        }
    }
}

// В тесте:
@Test
fun testLoadUser() {
    viewModel.loadUser()

    // Как нам дождаться завершения корутины в GlobalScope?
    // Нельзя внедрить TestDispatcher
    // Нельзя контролировать timing корутин
}
```

### Правильный Способ: Корутины С Жизненным Циклом

**Решение 1: Использовать lifecycleScope (Activity/Fragment)**

```kotlin
// ХОРОШО: Привязано к жизненному циклу Activity
class UserProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val user = repository.loadUser()

            // Автоматически отменяется при уничтожении Activity
            updateUI(user) // Безопасно!
        }
    }
}
```

**Преимущества**:
- Корутина отменяется при уничтожении Activity
- Нет утечек памяти
- Нет потери ресурсов
- Безопасные обновления UI

**Решение 2: Использовать viewModelScope (ViewModel)**

```kotlin
// ХОРОШО: Привязано к жизненному циклу ViewModel
class UserViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData

    fun loadUser() {
        viewModelScope.launch {
            val user = repository.getUser()
            _userData.value = user
        }
    }

    // Автоматически отменяется при вызове ViewModel.onCleared()
}
```

**Преимущества**:
- Переживает изменения конфигурации (поворот)
- Отменяется при очистке ViewModel
- Тестируется с TestDispatcher
- Нет утечек памяти

**Решение 3: Использовать repeatOnLifecycle для сбора Flow**

```kotlin
// ЛУЧШЕ ВСЕГО: Сбор Flow с учетом жизненного цикла
class UserProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Собирать только когда lifecycle в состоянии STARTED
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.userData.collect { user ->
                    updateUI(user)
                }
            }
        }
    }
}
```

**Преимущества**:
- Уважает состояния жизненного цикла
- Нет обновлений когда приложение в фоне
- Оптимальное использование ресурсов

### Когда GlobalScope Может Быть Приемлем

**Редкие Легитимные Случаи**:

```kotlin
// WARNING: ВОЗМОЖНО ПРИЕМЛЕМО: Singleton уровня приложения
class AnalyticsManager {
    fun logEvent(event: String) {
        // Это ДОЛЖНО работать даже если Activity уничтожен
        GlobalScope.launch(Dispatchers.IO) {
            analyticsApi.sendEvent(event)
        }
    }
}
```

**Но Даже Здесь Есть Лучшие Альтернативы**:

```kotlin
// ЛУЧШЕ: Пользовательская область уровня приложения
class MyApplication : Application() {
    val applicationScope = CoroutineScope(
        SupervisorJob() + Dispatchers.Default
    )

    override fun onTerminate() {
        applicationScope.cancel()
        super.onTerminate()
    }
}

class AnalyticsManager(private val scope: CoroutineScope) {
    fun logEvent(event: String) {
        scope.launch(Dispatchers.IO) {
            analyticsApi.sendEvent(event)
        }
    }
}
```

**Почему Лучше**:
- Явное владение областью
- Можно внедрить TestScope в тестах
- Можно добавить CoroutineExceptionHandler
- Четкое управление жизненным циклом

### Резюме

**Почему Избегать GlobalScope**:
- Вызывает утечки памяти (держит ссылки на Activity/Fragment)
- Тратит ресурсы (продолжает после уничтожения компонента)
- Сложно тестировать (нельзя внедрить TestDispatcher)
- Неконтролируемый жизненный цикл (работает пока приложение живо)
- Проблемы с обработкой исключений (глобальный обработчик крэшей)

**Используйте Вместо**:
- `lifecycleScope` для Activity/Fragment
- `viewModelScope` для ViewModel
- Пользовательские области с четким владением жизненным циклом
- `WorkManager` для фоновых задач, переживающих UI

**Ключевой Принцип**: **Всегда привязывайте корутины к области, учитывающей жизненный цикл**. Если вы думаете, что вам нужен GlobalScope, вам, вероятно, нужна лучшая архитектура или WorkManager.

---

## References

- [GlobalScope Documentation - Kotlin](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-global-scope/)
- [Coroutines on Android - Android Developers](https://developer.android.com/kotlin/coroutines)
- [Lifecycle-aware coroutines - AndroidX](https://developer.android.com/topic/libraries/architecture/coroutines)

---

**Source**: Kotlin Coroutines Interview Questions for Android Developers PDF

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Related Questions

- [[q-object-companion-object--kotlin--medium]]
- [[q-test-dispatcher-types--kotlin--medium]]
-
