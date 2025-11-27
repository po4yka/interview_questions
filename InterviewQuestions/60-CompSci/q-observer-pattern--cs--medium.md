---
id: cs-028
title: "Observer Pattern / Паттерн Observer"
aliases: ["Observer Pattern", "Паттерн Observer"]
topic: cs
subtopics: [behavioral-patterns, design-patterns, publish-subscribe]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, q-strategy-pattern--design-patterns--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [behavioral-patterns, design-patterns, difficulty/medium, flow, gof-patterns, livedata, observer, publish-subscribe]
sources: ["https://refactoring.guru/design-patterns/observer"]

date created: Saturday, November 1st 2025, 1:26:49 pm
date modified: Tuesday, November 25th 2025, 8:53:53 pm
---
# Вопрос (RU)
> Что такое паттерн Observer? Когда его использовать и как он работает?

# Question (EN)
> What is the Observer pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория Observer Pattern:**
Observer — поведенческий паттерн проектирования, который определяет отношение "один-ко-многим" между объектами. Subject (издатель) хранит список observers (подписчиков) и оповещает их при изменении своего состояния. Он решает задачи: уведомить связанные объекты без жёсткой связанности, поддержать произвольное количество зависимых объектов и дать гибкость в добавлении/удалении наблюдателей. Решение: общий интерфейс `Subject` + `Observer`, автоматическое уведомление, слабое зацепление (loose coupling). См. также [[c-architecture-patterns]].

**Определение:**

*Теория:* Observer — шаблон, при котором объект (subject) хранит список зависимых от него объектов (observers). При изменении состояния subject уведомляет наблюдателей через вызов их методов. Обеспечивается слабое зацепление: subject не знает конкретных типов наблюдателей, наблюдатели не зависят друг от друга. Открытость: можно добавлять/удалять observers без изменения кода subject.

```kotlin
// ✅ Basic Observer Structure (simple, non-generic variant)
interface Observer {
    fun update(data: Any)
}

interface Subject {
    fun addObserver(observer: Observer)
    fun removeObserver(observer: Observer)
    fun notifyObservers(data: Any)
}

// ✅ Concrete Subject
class DataSubject : Subject {
    private val observers = mutableListOf<Observer>()

    override fun addObserver(observer: Observer) {
        observers.add(observer)
    }

    override fun removeObserver(observer: Observer) {
        observers.remove(observer)
    }

    override fun notifyObservers(data: Any) {
        observers.forEach { it.update(data) }
    }

    fun changeData(newData: String) {
        notifyObservers(newData)
    }
}

// ✅ Concrete Observer
class DataObserver(private val name: String) : Observer {
    override fun update(data: Any) {
        println("$name received: $data")
    }
}

// ✅ Usage
fun main() {
    val subject = DataSubject()
    val observer1 = DataObserver("Observer1")
    val observer2 = DataObserver("Observer2")

    subject.addObserver(observer1)
    subject.addObserver(observer2)
    subject.changeData("New Data")  // Both notified
}
```

**Проблемы, которые решает:**

**1. Loose Coupling:**
*Теория:* Без Observer subject напрямую обновляет конкретные зависимые объекты. Это порождает tight coupling — subject знает точные типы зависимых объектов. Трудно переиспользовать и расширять. С Observer subject работает только с интерфейсом Observer и не зависит от конкретных реализаций. Loose coupling — легко добавлять/удалять наблюдателей без изменения кода subject.

```kotlin
// ❌ Tight Coupling (Bad)
class Subject {
    private val dependent1: Type1 = ...
    private val dependent2: Type2 = ...

    fun notifyDependents() {
        dependent1.update1()
        dependent2.update2()
    }
}

// ✅ Loose Coupling (Good) - Observer Pattern
class Subject {
    private val observers = mutableListOf<Observer>()

    fun addObserver(observer: Observer) {
        observers.add(observer)
    }

    fun notifyObservers() {
        observers.forEach { it.update() }
    }
}
```

**2. Open-Ended Dependents:**
*Теория:* Количество зависимых объектов заранее неизвестно или динамично. Нужно уведомлять произвольное количество объектов. Subject не знает, сколько observers подписано, но уведомляет всех. Гибкость — можно добавлять/удалять observers во время выполнения без модификации subject.

```kotlin
// ✅ Dynamic observer management
class EventManager {
    private val listeners = mutableListOf<EventListener>()

    fun addListener(listener: EventListener) {
        listeners.add(listener)
    }

    fun removeListener(listener: EventListener) {
        listeners.remove(listener)
    }

    fun fireEvent(event: Event) {
        listeners.forEach { it.onEvent(event) }
    }
}

// ✅ Runtime observers
val manager = EventManager()
manager.addListener(LoggingListener())
manager.addListener(UiUpdateListener())
manager.addListener(NotificationListener())
manager.fireEvent(SomeEvent())  // All notified
```

**3. Broadcast Communication:**
*Теория:* Subject нужно уведомлять множество объектов, не зная их конкретных типов. Observer Pattern предоставляет механизм "издатель-подписчик": subject публикует изменения, заинтересованные объекты подписываются и получают уведомления. Связь ослаблена: subject не знает подписчиков, подписчики не знают друг друга.

```kotlin
// ✅ Broadcast communication
class NewsPublisher {
    private val subscribers = mutableListOf<NewsSubscriber>()

    fun subscribe(subscriber: NewsSubscriber) {
        subscribers.add(subscriber)
    }

    fun publishNews(news: News) {
        subscribers.forEach { it.receiveNews(news) }
    }
}
```

**Компоненты Observer:**

**1. Subject:**
*Теория:* Subject — наблюдаемый объект. Хранит список observers. Предоставляет методы: addObserver()/attach(), removeObserver()/detach(), notifyObservers(). Основная ответственность: управлять наблюдателями и уведомлять их при изменении своего состояния. Не зависит от конкретных типов наблюдателей.

```kotlin
// ✅ Subject implementation
class StockPriceSubject {
    private val observers = mutableListOf<StockObserver>()
    private var price: Double = 0.0

    fun attach(observer: StockObserver) {
        observers.add(observer)
    }

    fun detach(observer: StockObserver) {
        observers.remove(observer)
    }

    fun setPrice(newPrice: Double) {
        price = newPrice
        observers.forEach { it.priceChanged(newPrice) }
    }
}
```

**2. Observer:**
*Теория:* Observer — объект, который заинтересован в изменениях состояния subject. Реализует интерфейс Observer с методом update() (или специализированным методом). Регистрируется в subject через addObserver()/attach(). Обновляет своё состояние при получении уведомления. Не знает о других наблюдателях.

```kotlin
// ✅ Observer interface (generic variant)
interface Observer<T> {
    fun update(data: T)
}

// ✅ Concrete observers
class EmailNotifier : Observer<String> {
    override fun update(data: String) {
        sendEmail(data)
    }
}

class SMSNotifier : Observer<String> {
    override fun update(data: String) {
        sendSMS(data)
    }
}

class LogNotifier : Observer<String> {
    override fun update(data: String) {
        logMessage(data)
    }
}
```

**Android/Kotlin примеры:**

**1. Паттерн `LiveData`:**
*Теория:* `LiveData` — lifecycle-aware observable data holder, реализующий принципы паттерна Observer для обновления UI. `ViewModel` (как источник данных) держит `LiveData`. `View` (`Activity`/`Fragment`) выступает как наблюдатель и подписывается на изменения. При использовании `observe(owner, ...)` `LiveData` автоматически удаляет observer, когда соответствующий `LifecycleOwner` уничтожается, что снижает риск утечек памяти (при не зависящих от жизненного цикла наблюдателях ответственность за отписку остаётся на разработчике).

```kotlin
// ✅ LiveData Observer Pattern
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user  // Read-only for observers

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _user.value = repository.getUser(userId)
        }
    }
}

class UserActivity : AppCompatActivity() {
    private lateinit var viewModel: UserViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel = ViewModelProvider(this)[UserViewModel::class.java]

        // Observer: подписывается на изменения
        viewModel.user.observe(this) { user ->
            updateUI(user)
        }
    }
}
```

**2. Паттерн `Flow`:**
*Теория:* `Flow` — часть корутин в Kotlin, предоставляющая асинхронные потоки значений и поддерживающая реактивный стиль программирования. Холодный `Flow` генерирует значения при подписке (collect), `StateFlow`/`SharedFlow` предоставляют горячие потоки. Эти абстракции удобно использовать для реализации взаимодействий в духе паттерна Observer (подписка-уведомление), хотя они не являются буквальной реализацией GoF Observer. Управление нагрузкой и координацией возможно через операторы `Flow`.

```kotlin
// ✅ Flow-based reactive updates
class DataRepository {
    private val _dataFlow = MutableStateFlow<Data?>(null)
    val dataFlow: StateFlow<Data?> = _dataFlow.asStateFlow()

    fun updateData(data: Data) {
        _dataFlow.value = data
    }
}

class MainViewModel(private val repository: DataRepository) : ViewModel() {
    val data: StateFlow<Data?> = repository.dataFlow

    init {
        viewModelScope.launch {
            data.collect { data ->
                // Observer-like reaction to new data
                handleData(data)
            }
        }
    }
}
```

**Преимущества:**

1. Loose Coupling — Subject и observers слабо связаны
2. Flexibility — Можно добавлять/удалять observers во время выполнения
3. Broadcast — Subject не знает конкретных observers
4. Open/Closed — Можно добавлять новых observers без изменения subject
5. Reusability — Subject и observers можно переиспользовать независимо

**Недостатки:**

1. Memory Leaks — Нужно корректно отписывать observers (проблема "lapsed listener"), если нет автоматического управления жизненным циклом
2. Unpredictable Order — Порядок уведомления observers обычно не гарантируется
3. Performance — Уведомление большого количества observers может быть затратным
4. Debugging — Сложно отследить, какой observer вызвал цепочку изменений
5. Cascade Updates — Возможны сложные каскадные обновления

**Когда использовать:**

✅ Используйте Observer, когда:
- изменения одного объекта требуют изменения других;
- количество зависимых объектов неизвестно или динамично;
- нужно уведомлять объекты, не зная, кто именно подписан;
- нужен механизм широковещательной рассылки уведомлений;
- требуются обновления UI на основе изменений данных.

❌ Не используйте Observer, когда:
- связь простая один-к-одному;
- допустима жёсткая связанность;
- критична производительность при большом количестве подписчиков;
- критичен строгий порядок уведомлений.

## Answer (EN)

**Observer Pattern Theory:**
Observer is a behavioral design pattern that defines a one-to-many dependency between objects. A Subject maintains a list of Observers and notifies them when its state changes. It solves: notifying dependents without tight coupling, supporting an open-ended number of dependents, and allowing flexible adding/removing of observers. The solution: `Subject` + `Observer` interface, automatic notification, loose coupling. See also [[c-architecture-patterns]].

**Definition:**

*Theory:* Observer is a pattern where an object (subject) maintains a list of dependent objects (observers). On state change, it notifies observers automatically by calling their methods. This ensures loose coupling: the subject does not depend on concrete observer implementations, and observers do not depend on each other. It is open-ended: you can add/remove observers without changing subject code.

```kotlin
// ✅ Basic Observer Structure (simple, non-generic variant)
interface Observer {
    fun update(data: Any)
}

interface Subject {
    fun addObserver(observer: Observer)
    fun removeObserver(observer: Observer)
    fun notifyObservers(data: Any)
}

// ✅ Concrete Subject
class DataSubject : Subject {
    private val observers = mutableListOf<Observer>()

    override fun addObserver(observer: Observer) {
        observers.add(observer)
    }

    override fun removeObserver(observer: Observer) {
        observers.remove(observer)
    }

    override fun notifyObservers(data: Any) {
        observers.forEach { it.update(data) }
    }

    fun changeData(newData: String) {
        notifyObservers(newData)
    }
}

// ✅ Concrete Observer
class DataObserver(private val name: String) : Observer {
    override fun update(data: Any) {
        println("$name received: $data")
    }
}

// ✅ Usage
fun main() {
    val subject = DataSubject()
    val observer1 = DataObserver("Observer1")
    val observer2 = DataObserver("Observer2")

    subject.addObserver(observer1)
    subject.addObserver(observer2)
    subject.changeData("New Data")  // Both notified
}
```

**Problems Solved:**

**1. Loose Coupling:**
*Theory:* Without Observer, the subject directly updates specific dependents. This creates tight coupling — the subject knows exact dependent types. Hard to reuse and maintain. With Observer, the subject depends only on the Observer interface and does not know concrete implementations. Loose coupling — easy to add/remove observers without changing subject code.

```kotlin
// ❌ Tight Coupling (Bad)
class Subject {
    private val dependent1: Type1 = ...
    private val dependent2: Type2 = ...

    fun notifyDependents() {
        dependent1.update1()
        dependent2.update2()
    }
}

// ✅ Loose Coupling (Good) - Observer Pattern
class Subject {
    private val observers = mutableListOf<Observer>()

    fun addObserver(observer: Observer) {
        observers.add(observer)
    }

    fun notifyObservers() {
        observers.forEach { it.update() }
    }
}
```

**2. Open-Ended Dependents:**
*Theory:* The number of dependent objects is unknown or dynamic. You need to notify an open-ended number of objects. The subject does not know how many observers are registered but can notify all of them. Flexibility — you can add/remove observers at runtime without modifying the subject.

```kotlin
// ✅ Dynamic observer management
class EventManager {
    private val listeners = mutableListOf<EventListener>()

    fun addListener(listener: EventListener) {
        listeners.add(listener)
    }

    fun removeListener(listener: EventListener) {
        listeners.remove(listener)
    }

    fun fireEvent(event: Event) {
        listeners.forEach { it.onEvent(event) }
    }
}

// ✅ Runtime observers
val manager = EventManager()
manager.addListener(LoggingListener())
manager.addListener(UiUpdateListener())
manager.addListener(NotificationListener())
manager.fireEvent(SomeEvent())  // All notified
```

**3. Broadcast Communication:**
*Theory:* The subject needs to notify multiple objects without knowing who they are. The Observer pattern provides a publisher-subscriber style mechanism: the subject publishes changes, interested objects subscribe. Decoupled: the subject does not know subscribers, subscribers do not know each other.

```kotlin
// ✅ Broadcast communication
class NewsPublisher {
    private val subscribers = mutableListOf<NewsSubscriber>()

    fun subscribe(subscriber: NewsSubscriber) {
        subscribers.add(subscriber)
    }

    fun publishNews(news: News) {
        subscribers.forEach { it.receiveNews(news) }
    }
}
```

**Observer Components:**

**1. Subject:**
*Theory:* The Subject is the observable object. It maintains a list of observers. It provides methods like addObserver()/attach(), removeObserver()/detach(), notifyObservers(). Its main responsibility is to manage observers and notify them on state changes. It does not depend on concrete observer types.

```kotlin
// ✅ Subject implementation
class StockPriceSubject {
    private val observers = mutableListOf<StockObserver>()
    private var price: Double = 0.0

    fun attach(observer: StockObserver) {
        observers.add(observer)
    }

    fun detach(observer: StockObserver) {
        observers.remove(observer)
    }

    fun setPrice(newPrice: Double) {
        price = newPrice
        observers.forEach { it.priceChanged(newPrice) }
    }
}
```

**2. Observer:**
*Theory:* An Observer is an object interested in the Subject's state changes. It implements an Observer interface with an update() (or specialized) method. It registers with the Subject via addObserver()/attach(). It updates its state when notified. It does not know about other observers.

```kotlin
// ✅ Observer interface (generic variant)
interface Observer<T> {
    fun update(data: T)
}

// ✅ Concrete observers
class EmailNotifier : Observer<String> {
    override fun update(data: String) {
        sendEmail(data)
    }
}

class SMSNotifier : Observer<String> {
    override fun update(data: String) {
        sendSMS(data)
    }
}

class LogNotifier : Observer<String> {
    override fun update(data: String) {
        logMessage(data)
    }
}
```

**Android/Kotlin Examples:**

**1. `LiveData` Pattern:**
*Theory:* `LiveData` is a lifecycle-aware observable data holder that applies Observer pattern principles for UI updates. A `ViewModel` (as a data source) holds `LiveData`. A `View` (`Activity`/`Fragment`) acts as an observer and observes changes. When using `observe(owner, ...)`, `LiveData` automatically removes the observer when the associated `LifecycleOwner` is destroyed, which helps prevent memory leaks (with non-lifecycle-aware observation, proper unsubscription is still the developer's responsibility).

```kotlin
// ✅ LiveData Observer Pattern
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user  // Read-only for observers

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _user.value = repository.getUser(userId)
        }
    }
}

class UserActivity : AppCompatActivity() {
    private lateinit var viewModel: UserViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel = ViewModelProvider(this)[UserViewModel::class.java]

        // Observer: subscribes to changes
        viewModel.user.observe(this) { user ->
            updateUI(user)
        }
    }
}
```

**2. `Flow` Pattern:**
*Theory:* `Flow` is part of Kotlin coroutines providing asynchronous streams of values and supporting a reactive programming style. A cold `Flow` emits values when a collector subscribes; `StateFlow`/`SharedFlow` provide hot streams. These abstractions are convenient for building Observer-like publisher-subscriber interactions, although they are not a literal implementation of the GoF Observer pattern. Backpressure and coordination can be handled via `Flow` operators.

```kotlin
// ✅ Flow-based reactive updates
class DataRepository {
    private val _dataFlow = MutableStateFlow<Data?>(null)
    val dataFlow: StateFlow<Data?> = _dataFlow.asStateFlow()

    fun updateData(data: Data) {
        _dataFlow.value = data
    }
}

class MainViewModel(private val repository: DataRepository) : ViewModel() {
    val data: StateFlow<Data?> = repository.dataFlow

    init {
        viewModelScope.launch {
            data.collect { data ->
                // Observer-like reaction to new data
                handleData(data)
            }
        }
    }
}
```

**Advantages:**

1. Loose Coupling — Subject and observers are decoupled
2. Flexibility — Add/remove observers at runtime
3. Broadcast — Subject does not know specific observers
4. Open/Closed — Add new observers without changing the subject
5. Reusability — Subject and observers can be reused independently

**Disadvantages:**

1. Memory Leaks — Need to unregister observers properly (lapsed listener problem), unless lifecycle-aware mechanisms handle it
2. Unpredictable Order — Notification order of observers is usually not guaranteed
3. Performance — Notifying many observers may be expensive
4. Debugging — Hard to trace which observer caused follow-up changes
5. Cascade Updates — Can lead to complex update chains

**When to Use:**

✅ Use Observer when:
- Changes to one object require updating others
- Number of dependent objects is unknown or dynamic
- You want to notify objects without knowing who they are
- You need a broadcast-like notification mechanism
- You need UI updates based on data changes

❌ Don't use Observer when:
- Dependencies are simple one-to-one
- Tight coupling is acceptable
- Scenario is highly performance-critical with many observers
- Strict notification order is critical

---

## Дополнительные Вопросы (RU)

- Как Observer отличается от паттерна Pub/Sub?
- Каковы типичные реализации Observer в Android?
- Как предотвратить утечки памяти при использовании паттерна Observer?

## Follow-ups

- How does Observer differ from Pub/Sub pattern?
- What are common Android implementations of Observer?
- How to prevent memory leaks with Observer pattern?

## Связанные Вопросы (RU)

### Предпосылки (проще)
- Базовые концепции паттернов проектирования
- Понимание событийно-ориентированного программирования

### Связанные (того Же уровня)
- [[q-strategy-pattern--cs--medium]] — паттерн Strategy
- Паттерн Command (см. соответствующий вопрос)
- Паттерн State (см. соответствующий вопрос)

### Продвинутое (сложнее)
- Паттерны наблюдаемых в RxJava
- Продвинутые паттерны `Flow` с контролем нагрузки
- Проектирование событийно-ориентированных архитектур

## Related Questions

### Prerequisites (Easier)
- Basic design patterns concepts
- Understanding of event-driven programming

### Related (Same Level)
- [[q-strategy-pattern--cs--medium]] - Strategy pattern
- Command pattern (see corresponding question)
- State pattern (see corresponding question)

### Advanced (Harder)
- RxJava observable patterns
- Advanced `Flow` patterns with backpressure
- Event-driven architecture design

## References

- [[c-architecture-patterns]]
- "https://refactoring.guru/design-patterns/observer"
