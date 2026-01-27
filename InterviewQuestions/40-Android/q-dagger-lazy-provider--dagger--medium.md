---
id: android-dagger-006
title: Dagger Lazy vs Provider / Lazy vs Provider в Dagger
aliases:
- Dagger Lazy
- Dagger Provider
- Lazy vs Provider
topic: android
subtopics:
- dagger
- di-dagger
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dependency-injection
- q-dagger-component-module--dagger--medium
- q-dagger-inject-provides--dagger--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-dagger
- dependency-injection
- difficulty/medium
- dagger
- lazy
- provider
anki_cards:
- slug: android-dagger-006-0-en
  language: en
- slug: android-dagger-006-0-ru
  language: ru
---
# Вопрос (RU)
> В чём разница между Lazy<T> и Provider<T> в Dagger?

# Question (EN)
> What is the difference between Lazy<T> and Provider<T> in Dagger?

---

## Ответ (RU)

**Lazy<T>** и **Provider<T>** - это обёртки для отложенного получения зависимостей в Dagger. Они решают разные задачи.

### Provider<T> - Каждый Раз Новый Экземпляр

`Provider<T>` возвращает результат `@Provides` метода при каждом вызове `get()`. Если зависимость без scope - каждый раз новый объект.

```kotlin
class EventLogger @Inject constructor(
    private val eventProvider: Provider<Event>
) {
    fun logEvents() {
        // Каждый get() вызывает @Provides метод
        val event1 = eventProvider.get() // Новый Event
        val event2 = eventProvider.get() // Новый Event
        val event3 = eventProvider.get() // Новый Event

        println(event1 === event2) // false (разные объекты)
    }
}

@Module
class EventModule {
    @Provides // Без scope - каждый раз новый
    fun provideEvent(): Event {
        return Event(timestamp = System.currentTimeMillis())
    }
}
```

### Lazy<T> - Один Экземпляр с Ленивой Инициализацией

`Lazy<T>` создаёт объект только при первом вызове `get()` и кэширует его. Последующие вызовы возвращают тот же экземпляр.

```kotlin
class ProfileScreen @Inject constructor(
    private val heavyRepository: Lazy<HeavyRepository>
) {
    fun onUserAction() {
        // Создаётся только когда действительно нужен
        val repo = heavyRepository.get() // Создание происходит здесь
        val sameRepo = heavyRepository.get() // Тот же объект

        println(repo === sameRepo) // true (один объект)
    }
}

@Module
class RepositoryModule {
    @Provides
    fun provideHeavyRepository(
        database: AppDatabase,
        api: ApiService
    ): HeavyRepository {
        println("Creating HeavyRepository") // Вызовется только один раз
        return HeavyRepository(database, api)
    }
}
```

### Сравнительная Таблица

| Критерий | Lazy<T> | Provider<T> |
|----------|---------|-------------|
| Количество экземпляров | Один (кэшируется) | Зависит от scope |
| Момент создания | Первый get() | Каждый get() |
| Типичное использование | Отложенная инициализация | Фабрика объектов |
| Thread-safety | Да, встроенная | Зависит от реализации |
| Import | `dagger.Lazy` | `javax.inject.Provider` |

### Когда Использовать Provider<T>

**1. Нужен новый экземпляр каждый раз:**

```kotlin
class NotificationService @Inject constructor(
    private val notificationProvider: Provider<Notification>
) {
    fun showNotification(title: String, message: String) {
        val notification = notificationProvider.get().apply {
            this.title = title
            this.message = message
        }
        notificationManager.show(notification)
    }
}
```

**2. Доступ к scoped зависимости из другого scope:**

```kotlin
// @Singleton компонент
@Singleton
class UserSessionManager @Inject constructor(
    // ActivityScope объект из Singleton - нельзя напрямую
    // Но можно через Provider с subcomponent
)

// Правильный паттерн
@Singleton
class AnalyticsTracker @Inject constructor(
    private val eventProvider: Provider<AnalyticsEvent>
) {
    fun track(name: String) {
        val event = eventProvider.get() // Новый event каждый раз
        event.name = name
        send(event)
    }
}
```

**3. Избежание циклических зависимостей:**

```kotlin
// Циклическая зависимость: A -> B -> A
class ServiceA @Inject constructor(
    private val serviceBProvider: Provider<ServiceB> // Разрывает цикл
) {
    fun doWork() {
        serviceBProvider.get().process()
    }
}

class ServiceB @Inject constructor(
    private val serviceA: ServiceA
) {
    fun process() { /* ... */ }
}
```

### Когда Использовать Lazy<T>

**1. Дорогая инициализация:**

```kotlin
class SettingsScreen @Inject constructor(
    private val analytics: Lazy<AnalyticsManager>, // Тяжёлая инициализация
    private val crashReporter: Lazy<CrashReporter>
) {
    fun onSettingChanged(key: String, value: Any) {
        // Создаются только если пользователь что-то изменил
        analytics.get().trackSettingChange(key, value)
        crashReporter.get().setCustomKey(key, value.toString())
    }
}
```

**2. Опциональная зависимость:**

```kotlin
class DebugScreen @Inject constructor(
    private val debugTools: Lazy<DebugTools>
) {
    fun showDebugInfo() {
        if (BuildConfig.DEBUG) {
            // Не создаётся в release
            debugTools.get().showInfo()
        }
    }
}
```

**3. Зависимость может не понадобиться:**

```kotlin
class PaymentProcessor @Inject constructor(
    private val payPalProcessor: Lazy<PayPalProcessor>,
    private val stripeProcessor: Lazy<StripeProcessor>,
    private val cryptoProcessor: Lazy<CryptoProcessor>
) {
    fun process(method: PaymentMethod, amount: Money) {
        // Инициализируется только нужный процессор
        when (method) {
            PaymentMethod.PAYPAL -> payPalProcessor.get().charge(amount)
            PaymentMethod.STRIPE -> stripeProcessor.get().charge(amount)
            PaymentMethod.CRYPTO -> cryptoProcessor.get().charge(amount)
        }
    }
}
```

### Lazy + Provider Комбинация

```kotlin
class BatchProcessor @Inject constructor(
    // Ленивая инициализация фабрики
    private val taskProvider: Lazy<Provider<Task>>
) {
    fun processBatch(items: List<Item>) {
        // Provider создаётся один раз при первом использовании
        val factory = taskProvider.get()

        items.forEach { item ->
            // Новый Task для каждого item
            val task = factory.get()
            task.process(item)
        }
    }
}
```

### Lazy с Scope

Lazy работает независимо от scope:

```kotlin
@Singleton
@Provides
fun provideSingleton(): MySingleton = MySingleton()

class Consumer @Inject constructor(
    private val singleton: Lazy<MySingleton>
) {
    fun use() {
        // Всегда один экземпляр (из-за @Singleton),
        // но создаётся только при первом get()
        val instance = singleton.get()
    }
}
```

### Provider с Scope

Provider с scoped зависимостью всегда возвращает тот же экземпляр:

```kotlin
@Singleton
@Provides
fun provideSingleton(): MySingleton = MySingleton()

class Consumer @Inject constructor(
    private val singletonProvider: Provider<MySingleton>
) {
    fun use() {
        val s1 = singletonProvider.get()
        val s2 = singletonProvider.get()
        println(s1 === s2) // true - один экземпляр из-за @Singleton
    }
}
```

### Важные Нюансы

```kotlin
// Правильный import для Lazy
import dagger.Lazy // НЕ kotlin.Lazy!

// Provider всегда из javax.inject
import javax.inject.Provider
```

---

## Answer (EN)

**Lazy<T>** and **Provider<T>** are wrappers for deferred dependency retrieval in Dagger. They solve different problems.

### Provider<T> - New Instance Each Time

`Provider<T>` returns the result of `@Provides` method on each `get()` call. If dependency is unscoped - new object every time.

```kotlin
class EventLogger @Inject constructor(
    private val eventProvider: Provider<Event>
) {
    fun logEvents() {
        // Each get() calls @Provides method
        val event1 = eventProvider.get() // New Event
        val event2 = eventProvider.get() // New Event
        val event3 = eventProvider.get() // New Event

        println(event1 === event2) // false (different objects)
    }
}

@Module
class EventModule {
    @Provides // No scope - new every time
    fun provideEvent(): Event {
        return Event(timestamp = System.currentTimeMillis())
    }
}
```

### Lazy<T> - Single Instance with Lazy Initialization

`Lazy<T>` creates object only on first `get()` call and caches it. Subsequent calls return the same instance.

```kotlin
class ProfileScreen @Inject constructor(
    private val heavyRepository: Lazy<HeavyRepository>
) {
    fun onUserAction() {
        // Created only when actually needed
        val repo = heavyRepository.get() // Creation happens here
        val sameRepo = heavyRepository.get() // Same object

        println(repo === sameRepo) // true (same object)
    }
}

@Module
class RepositoryModule {
    @Provides
    fun provideHeavyRepository(
        database: AppDatabase,
        api: ApiService
    ): HeavyRepository {
        println("Creating HeavyRepository") // Called only once
        return HeavyRepository(database, api)
    }
}
```

### Comparison Table

| Criterion | Lazy<T> | Provider<T> |
|-----------|---------|-------------|
| Instance count | One (cached) | Depends on scope |
| Creation moment | First get() | Each get() |
| Typical use | Deferred initialization | Object factory |
| Thread-safety | Yes, built-in | Depends on implementation |
| Import | `dagger.Lazy` | `javax.inject.Provider` |

### When to Use Provider<T>

**1. Need new instance each time:**

```kotlin
class NotificationService @Inject constructor(
    private val notificationProvider: Provider<Notification>
) {
    fun showNotification(title: String, message: String) {
        val notification = notificationProvider.get().apply {
            this.title = title
            this.message = message
        }
        notificationManager.show(notification)
    }
}
```

**2. Access scoped dependency from different scope:**

```kotlin
// @Singleton component
@Singleton
class UserSessionManager @Inject constructor(
    // ActivityScope object from Singleton - cannot directly
    // But possible through Provider with subcomponent
)

// Correct pattern
@Singleton
class AnalyticsTracker @Inject constructor(
    private val eventProvider: Provider<AnalyticsEvent>
) {
    fun track(name: String) {
        val event = eventProvider.get() // New event each time
        event.name = name
        send(event)
    }
}
```

**3. Breaking circular dependencies:**

```kotlin
// Circular dependency: A -> B -> A
class ServiceA @Inject constructor(
    private val serviceBProvider: Provider<ServiceB> // Breaks cycle
) {
    fun doWork() {
        serviceBProvider.get().process()
    }
}

class ServiceB @Inject constructor(
    private val serviceA: ServiceA
) {
    fun process() { /* ... */ }
}
```

### When to Use Lazy<T>

**1. Expensive initialization:**

```kotlin
class SettingsScreen @Inject constructor(
    private val analytics: Lazy<AnalyticsManager>, // Heavy initialization
    private val crashReporter: Lazy<CrashReporter>
) {
    fun onSettingChanged(key: String, value: Any) {
        // Created only if user changes something
        analytics.get().trackSettingChange(key, value)
        crashReporter.get().setCustomKey(key, value.toString())
    }
}
```

**2. Optional dependency:**

```kotlin
class DebugScreen @Inject constructor(
    private val debugTools: Lazy<DebugTools>
) {
    fun showDebugInfo() {
        if (BuildConfig.DEBUG) {
            // Not created in release
            debugTools.get().showInfo()
        }
    }
}
```

**3. Dependency might not be needed:**

```kotlin
class PaymentProcessor @Inject constructor(
    private val payPalProcessor: Lazy<PayPalProcessor>,
    private val stripeProcessor: Lazy<StripeProcessor>,
    private val cryptoProcessor: Lazy<CryptoProcessor>
) {
    fun process(method: PaymentMethod, amount: Money) {
        // Only needed processor gets initialized
        when (method) {
            PaymentMethod.PAYPAL -> payPalProcessor.get().charge(amount)
            PaymentMethod.STRIPE -> stripeProcessor.get().charge(amount)
            PaymentMethod.CRYPTO -> cryptoProcessor.get().charge(amount)
        }
    }
}
```

### Lazy + Provider Combination

```kotlin
class BatchProcessor @Inject constructor(
    // Lazy initialization of factory
    private val taskProvider: Lazy<Provider<Task>>
) {
    fun processBatch(items: List<Item>) {
        // Provider created once on first use
        val factory = taskProvider.get()

        items.forEach { item ->
            // New Task for each item
            val task = factory.get()
            task.process(item)
        }
    }
}
```

### Lazy with Scope

Lazy works independently of scope:

```kotlin
@Singleton
@Provides
fun provideSingleton(): MySingleton = MySingleton()

class Consumer @Inject constructor(
    private val singleton: Lazy<MySingleton>
) {
    fun use() {
        // Always same instance (due to @Singleton),
        // but created only on first get()
        val instance = singleton.get()
    }
}
```

### Provider with Scope

Provider with scoped dependency always returns same instance:

```kotlin
@Singleton
@Provides
fun provideSingleton(): MySingleton = MySingleton()

class Consumer @Inject constructor(
    private val singletonProvider: Provider<MySingleton>
) {
    fun use() {
        val s1 = singletonProvider.get()
        val s2 = singletonProvider.get()
        println(s1 === s2) // true - same instance due to @Singleton
    }
}
```

### Important Notes

```kotlin
// Correct import for Lazy
import dagger.Lazy // NOT kotlin.Lazy!

// Provider always from javax.inject
import javax.inject.Provider
```

---

## Дополнительные Вопросы (RU)

- Как Lazy обеспечивает thread-safety?
- Можно ли использовать kotlin.Lazy вместо dagger.Lazy?
- Как Provider работает со scoped зависимостями?

## Follow-ups

- How does Lazy ensure thread-safety?
- Can you use kotlin.Lazy instead of dagger.Lazy?
- How does Provider work with scoped dependencies?

## Ссылки (RU)

- [Dagger Lazy](https://dagger.dev/api/latest/dagger/Lazy.html)
- [javax.inject.Provider](https://docs.oracle.com/javaee/6/api/javax/inject/Provider.html)

## References

- [Dagger Lazy](https://dagger.dev/api/latest/dagger/Lazy.html)
- [javax.inject.Provider](https://docs.oracle.com/javaee/6/api/javax/inject/Provider.html)

## Связанные Вопросы (RU)

### Medium
- [[q-dagger-component-module--dagger--medium]]
- [[q-dagger-inject-provides--dagger--medium]]
- [[q-dagger-component-builder--dagger--medium]]

### Hard
- [[q-dagger-scopes-custom--dagger--hard]]

## Related Questions

### Medium
- [[q-dagger-component-module--dagger--medium]]
- [[q-dagger-inject-provides--dagger--medium]]
- [[q-dagger-component-builder--dagger--medium]]

### Hard
- [[q-dagger-scopes-custom--dagger--hard]]
