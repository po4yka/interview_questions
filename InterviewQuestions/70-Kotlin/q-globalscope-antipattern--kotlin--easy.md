---
anki_cards:
- slug: q-globalscope-antipattern--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-globalscope-antipattern--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: kotlin-193
title: "GlobalScope Anti-Pattern / Анти-Паттерн GlobalScope"
aliases: [GlobalScope Anti-Pattern, GlobalScope Antipattern]
topic: kotlin
subtopics: [coroutines, structured-concurrency]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, q-object-companion-object--kotlin--medium, q-test-dispatcher-types--kotlin--medium]
created: 2024-10-15
updated: 2025-11-09
tags: [difficulty/easy]
---\
# Вопрос (RU)
> Почему следует избегать использования `GlobalScope` в Android приложениях?

---

# Question (EN)
> Why should you avoid using `GlobalScope` in Android applications?

## Ответ (RU)

**`GlobalScope` является анти-паттерном в Android**, потому что создает корутины, не привязанные к жизненному циклу, что легко приводит к ситуациям, где долго живущие задачи держат ссылки на UI/`Activity`/`Fragment`, вызывая утечки памяти, потерю ресурсов и возможные крэши.

### Что Такое GlobalScope?

**Определение**: `GlobalScope` — это корутинная область верхнего уровня, существующая до завершения процесса приложения. Корутины в ней не привязаны к конкретному владельцу жизненного цикла.

```kotlin
// Корутина в GlobalScope
GlobalScope.launch {
    // Эта корутина живет до ручной отмены
    // или до завершения процесса приложения
}
```

**Ключевые Характеристики**:
- Существует все время жизни процесса приложения
- Не привязана к жизненному циклу Android-компонентов
- Не отменяется автоматически при уничтожении `Activity`/`Fragment`/`ViewModel`
- Использует глобальный контекст (по умолчанию Dispatchers.Default)

### Почему GlobalScope Проблематичен

**Проблема 1: Утечки Памяти и Доступ к Уничтоженному UI**

```kotlin
// ПЛОХО: Риск утечки памяти и крэша
class UserProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        GlobalScope.launch {
            // Загружает данные пользователя
            val user = repository.loadUser()

            // Activity может быть уничтожена здесь!
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
1. `Activity` запускается и создает корутину в `GlobalScope`
2. Пользователь поворачивает устройство или уходит назад
3. `Activity` уничтожается
4. Корутина продолжает работать (не привязана к жизненному циклу `Activity`)
5. Корутина пытается обновить уничтоженные view → **крэш** или удержание ссылок на `Activity`/Views → **утечка памяти**

Ключевой момент: сам `GlobalScope` не "создает утечки" автоматически, но корутины в нем живут дольше компонентов и легко захватывают их ссылки.

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
- Пользователь уходит из `SearchActivity`
- Сетевой запрос все равно завершается
- Результаты обрабатываются, хотя UI уже не актуален
- Потраченный трафик, батарея, CPU

**Проблема 3: Необработанные Исключения**

```kotlin
// ПЛОХО: Исключения могут крэшить приложение
GlobalScope.launch {
    // Если это выбросит исключение, оно может не быть перехвачено
    riskyOperation()
}

// Если не установлен CoroutineExceptionHandler,
// необработанное исключение пойдет к обработчику по умолчанию → крэш приложения
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
    // Нельзя корректно внедрить TestDispatcher
    // Сложно контролировать время выполнения корутин
}
```

### Правильный Способ: Корутины С Жизненным Циклом

**Решение 1: Использовать lifecycleScope (`Activity`/`Fragment`)**

```kotlin
// ХОРОШО: Привязано к жизненному циклу `Activity`
class UserProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val user = repository.loadUser()

            // Автоматически отменяется при уничтожении `Activity`
            updateUI(user) // Безопаснее
        }
    }
}
```

**Преимущества**:
- Корутина отменяется при уничтожении `Activity`
- Меньше риска утечек памяти
- Нет ненужных трат ресурсов после уничтожения экрана
- Безопасные обновления UI

**Решение 2: Использовать viewModelScope (`ViewModel`)**

```kotlin
// ХОРОШО: Привязано к жизненному циклу `ViewModel`
class UserViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData

    fun loadUser() {
        viewModelScope.launch {
            val user = repository.getUser()
            _userData.value = user
        }
    }

    // Корутины отменяются при вызове `ViewModel.onCleared()`
}
```

**Преимущества**:
- Переживает изменения конфигурации (поворот экрана)
- Отменяется при очистке `ViewModel`
- Удобно тестировать с TestDispatcher/TestScope
- Снижает риск утечек памяти

**Решение 3: Использовать repeatOnLifecycle для сбора `Flow`**

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
- Нет обновлений, когда приложение в фоне
- Оптимальное использование ресурсов

### Когда GlobalScope Может Быть Приемлем

**Редкие Легитимные Случаи**:

```kotlin
// WARNING: ВОЗМОЖНО ПРИЕМЛЕМО: Singleton уровня приложения
class AnalyticsManager {
    fun logEvent(event: String) {
        // Это ДОЛЖНО работать даже если `Activity` уничтожен
        GlobalScope.launch(Dispatchers.IO) {
            analyticsApi.sendEvent(event)
            // Обратите внимание: без явного обработчика ошибок
            // возможна потеря ошибок или крэш через глобальный handler
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
        // ВАЖНО: onTerminate() не гарантированно вызывается на реальных устройствах,
        // поэтому не полагайтесь на него как на главный механизм очистки.
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
- Можно внедрить TestScope/TestDispatcher в тестах
- Можно добавить CoroutineExceptionHandler
- Четкое управление жизненным циклом

### Сравнительная Таблица

| Аспект | GlobalScope | lifecycleScope/viewModelScope |
|--------|-------------|-------------------------------|
| **Время жизни** | Весь процесс приложения | Жизненный цикл компонента |
| **Отмена** | Только вручную | Автоматическая |
| **Утечки памяти** | Высокий риск (если захватывать компоненты) | Безопаснее |
| **Потеря ресурсов** | Возможна | Снижена |
| **Тестирование** | Сложно | Проще (можно внедрять dispatcher/scope) |
| **Обработка исключений** | Глобальный обработчик по умолчанию | Обработчик области |
| **Практика Android** | Анти-паттерн | Рекомендуется |

### Распространенные Ошибки И Как Их Исправить

**Ошибка 1: Фоновая работа после ухода пользователя**

```kotlin
// ПЛОХО
GlobalScope.launch {
    delay(10000) // Задержка 10 секунд
    showNotification()
}

// ХОРОШО — использовать WorkManager для отложенной работы
val workRequest = OneTimeWorkRequestBuilder<NotificationWorker>()
    .setInitialDelay(10, TimeUnit.SECONDS)
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
```

**Ошибка 2: Fire-and-forget сетевые вызовы**

```kotlin
// ПЛОХО
fun sendAnalytics() {
    GlobalScope.launch {
        api.sendEvent(event)
    }
}

// ХОРОШО — привязать к подходящей области
class MyViewModel : ViewModel() {
    fun sendAnalytics() {
        viewModelScope.launch {
            api.sendEvent(event)
        }
    }
}
```

### Резюме

**Почему Избегать `GlobalScope`**:
- Корутины могут пережить компоненты и удерживать ссылки на `Activity`/`Fragment` → утечки памяти
- Тратит ресурсы (продолжает работу после уничтожения компонента)
- Сложно тестировать (нельзя удобно внедрить TestDispatcher / управлять временем)
- Неконтролируемый жизненный цикл (работает, пока живет процесс приложения)
- Проблемы с обработкой исключений (попадает в глобальный обработчик, возможен крэш)

**Используйте Вместо**:
- `lifecycleScope` для `Activity`/`Fragment`
- `viewModelScope` для `ViewModel`
- Пользовательские области с четким владением жизненным циклом
- `WorkManager` для фоновых задач, переживающих UI
- См. также: [[c-coroutines]]

**Ключевой Принцип**: **Всегда привязывайте корутины к области, учитывающей жизненный цикл**. Если кажется, что нужен `GlobalScope`, вероятно нужна лучшая архитектура или `WorkManager`.

---

## Answer (EN)

**GlobalScope is considered an anti-pattern in Android** because it creates coroutines that are not tied to any lifecycle, which makes it easy for long-lived tasks to capture references to `Activity`, `Fragment`, or views, leading to memory leaks, wasted resources, and potential crashes.

### What is GlobalScope?

**Definition**: `GlobalScope` is a top-level coroutine scope that exists until the app process is killed. Coroutines launched in it are not bound to a specific lifecycle owner.

```kotlin
// GlobalScope coroutine
GlobalScope.launch {
    // This coroutine lives until manually canceled
    // or the app process is killed
}
```

**Key Characteristics**:
- Lives for the entire app process lifetime
- Not tied to Android component lifecycles
- Not automatically canceled when `Activity`/`Fragment`/`ViewModel` is destroyed
- Uses a global context (Dispatchers.Default by default)

### Why GlobalScope is Problematic

**Problem 1: Memory Leaks and Accessing Destroyed UI**

```kotlin
// BAD: Memory leak and crash risk
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
1. `Activity` starts and launches a coroutine in `GlobalScope`
2. User rotates device or presses back
3. `Activity` is destroyed
4. `Coroutine` keeps running (not tied to `Activity` lifecycle)
5. `Coroutine` tries to update destroyed views → **crash** or holding references to `Activity`/Views → **memory leak**

Key point: `GlobalScope` itself does not magically leak, but coroutines in it outlive components and can easily capture them.

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
- User navigates away from `SearchActivity`
- Network call completes anyway
- Results are processed even though UI no longer cares
- Wasted bandwidth, battery, CPU

**Problem 3: Unhandled Exceptions**

```kotlin
// BAD: Exceptions can crash the app
GlobalScope.launch {
    // If this throws an exception, it might not be caught
    riskyOperation()
}

// Without a CoroutineExceptionHandler,
// the exception is routed to the default handler → app crash
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

    // How do we wait for the GlobalScope coroutine to finish?
    // Can't cleanly inject a TestDispatcher
    // Hard to control coroutine timing
}
```

### The Right Way: Lifecycle-Scoped Coroutines

**Solution 1: Use lifecycleScope (Activities/Fragments)**

```kotlin
// GOOD: Tied to `Activity` lifecycle
class UserProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val user = repository.loadUser()

            // Automatically canceled if `Activity` is destroyed
            updateUI(user) // Safer
        }
    }
}
```

**Benefits**:
- `Coroutine` is canceled when `Activity` is destroyed
- Reduced risk of memory leaks
- Avoids wasting work after screen is gone
- Safe UI updates

**Solution 2: Use viewModelScope (ViewModels)**

```kotlin
// GOOD: Tied to `ViewModel` lifecycle
class UserViewModel : ViewModel() {
    private val _userData = MutableStateFlow<User?>(null)
    val userData: StateFlow<User?> = _userData

    fun loadUser() {
        viewModelScope.launch {
            val user = repository.getUser()
            _userData.value = user
        }
    }

    // Coroutines are canceled when `ViewModel.onCleared()` is called
}
```

**Benefits**:
- Survives configuration changes (e.g., rotation)
- Canceled when `ViewModel` is cleared
- Testable with TestDispatcher/TestScope
- Reduced risk of leaks

**Solution 3: Use repeatOnLifecycle for `Flow` collection**

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
- No updates while app is in background
- Efficient resource usage

### When GlobalScope Might Be Acceptable

**Rare Legitimate Use Cases**:

```kotlin
// WARNING: MAYBE ACCEPTABLE: Application-level singleton
class AnalyticsManager {
    fun logEvent(event: String) {
        // This SHOULD run even if `Activity` is destroyed
        GlobalScope.launch(Dispatchers.IO) {
            analyticsApi.sendEvent(event)
            // Note: without explicit error handling,
            // failures may be lost or crash via default handler
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
        // IMPORTANT: onTerminate() is not reliably called on real devices;
        // don't rely on it as the primary cleanup mechanism.
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
- Can inject TestScope/TestDispatcher in tests
- Can attach a CoroutineExceptionHandler
- Clear lifecycle management

### Comparison Table

| Aspect | GlobalScope | lifecycleScope/viewModelScope |
|--------|-------------|-------------------------------|
| **Lifetime** | Entire app process | `Component` lifecycle |
| **Cancellation** | Manual only | Automatic |
| **Memory Leaks** | High risk (if capturing components) | Safer |
| **Resource Waste** | Possible | Reduced |
| **Testing** | Difficult | Easier (inject dispatcher/scope) |
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

**Why Avoid `GlobalScope`**:
- Coroutines can outlive components and capture `Activity`/`Fragment` references → memory leaks
- Wastes resources (continues after component is destroyed)
- Hard to test (can't easily inject TestDispatcher or control timing)
- Uncontrolled lifecycle (runs until app process dies)
- Exception handling issues (falls back to global handler → possible crash)

**Use Instead**:
- `lifecycleScope` for Activities/Fragments
- `viewModelScope` for ViewModels
- Custom scopes with clear lifecycle ownership
- `WorkManager` for background tasks that outlive UI
- See also: [[c-coroutines]]

**Key Principle**: **Always tie coroutines to a lifecycle-aware scope**. If you think you need `GlobalScope`, you probably need a better architecture or `WorkManager` instead.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java-потоков?
- В каких редких случаях использование `GlobalScope` все же можно обосновать?
- Каковы типичные ошибки при работе с корутинами и жизненным циклом в Android?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация GlobalScope - Kotlin](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-global-scope/)
- [Coroutines on Android - Android Developers](https://developer.android.com/kotlin/coroutines)
- [Lifecycle-aware coroutines - AndroidX](https://developer.android.com/topic/libraries/architecture/coroutines)

## References

- [GlobalScope Documentation - Kotlin](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-global-scope/)
- [Coroutines on Android - Android Developers](https://developer.android.com/kotlin/coroutines)
- [Lifecycle-aware coroutines - AndroidX](https://developer.android.com/topic/libraries/architecture/coroutines)

---

## Связанные Вопросы (RU)

- [[q-object-companion-object--kotlin--medium]]
- [[q-test-dispatcher-types--kotlin--medium]]

## Related Questions

- [[q-object-companion-object--kotlin--medium]]
- [[q-test-dispatcher-types--kotlin--medium]]
