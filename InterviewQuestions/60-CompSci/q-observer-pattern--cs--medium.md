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
related: [q-command-pattern--design-patterns--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [behavioral-patterns, design-patterns, difficulty/medium, flow, gof-patterns, livedata, observer, publish-subscribe]
sources: [https://refactoring.guru/design-patterns/observer]
date created: Monday, October 6th 2025, 7:19:01 am
date modified: Saturday, November 1st 2025, 5:43:28 pm
---

# Вопрос (RU)
> Что такое паттерн Observer? Когда его использовать и как он работает?

# Question (EN)
> What is the Observer pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория Observer Pattern:**
Observer - behavioral pattern, определяет one-to-many dependency между objects. Subject maintains list observers, notifies при state changes. Solve: need notify objects без tight coupling, open-ended number dependents, flexibility в adding/removing observers. Solution: Subject+Observer interface, automatic notification, loose coupling.

**Определение:**

*Теория:* Observer - software design pattern где object (subject) maintains list dependents (observers). При state change, notifies observers автоматически через calling их methods. Обеспечивает loose coupling: subject doesn't know specific observers, observers don't know other observers. Open-ended: можно добавить/удалить observers без changing subject code.

```kotlin
// ✅ Basic Observer Structure
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
*Теория:* Without Observer: subject directly updates specific dependents. Tight coupling - subject knows exact dependents. Hard to reuse, hard to maintain. With Observer: subject knows только Observer interface, doesn't know конкретных implementations. Loose coupling - легко add/remove observers без changing subject code.

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
*Теория:* Number dependent objects unknown или dynamic. Нужно notify open-ended number objects. Subject не знает сколько observers, но can notify все. Flexibility - можно add/remove observers at runtime без modifying subject.

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
*Теория:* Subject needs notify objects без knowing who they are. Observer Pattern provides broadcast mechanism: subject publishes changes, interested objects subscribe. Decoupled: subject doesn't know subscribers, subscribers don't know each other.

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
*Теория:* Subject - observable object. Maintains list observers. Provides methods: addObserver(), removeObserver(), notifyObservers(). Single responsibility: manage observers и notify при state changes. Doesn't depend on concrete observer types.

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
*Теория:* Observer - object interested в state changes. Implements Observer interface с update() method. Registers with subject через addObserver(). Updates state при notify. Single responsibility: respond to notifications. Doesn't know about other observers.

```kotlin
// ✅ Observer interface
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

**1. LiveData Pattern:**
*Теория:* LiveData - lifecycle-aware observable data holder. Implements Observer pattern для UI updates. ViewModel (subject) holds LiveData. View (observer) observes changes. Auto unregisters при lifecycle destroyed. Prevents memory leaks.

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

**2. Flow Pattern:**
*Теория:* Flow - Kotlin coroutines implementation of Observer pattern. Cold stream - emissions happen when collector subscribes. StateFlow/SharedFlow provide hot streams. Backpressure support через Flow operators. Suitable для data streams.

```kotlin
// ✅ Flow Observer Pattern
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
                // Observer reaction
                handleData(data)
            }
        }
    }
}
```

**Преимущества:**

1. **Loose Coupling** - Subject и observers decoupled
2. **Flexibility** - Add/remove observers at runtime
3. **Broadcast** - Subject не знает конкретных observers
4. **Open/Closed** - Можем add observers без changing subject
5. **Reusability** - Subject и observers reusable independently

**Недостатки:**

1. **Memory Leaks** - Need unregister observers (Lapsed listener problem)
2. **Unpredictable Order** - Observers notified в unknown order
3. **Performance** - Notifying many observers expensive
4. **Debugging** - Hard track which observer caused change
5. **Cascade Updates** - Can lead complex update chains

**Когда использовать:**

✅ **Use Observer when:**
- Changes to one object require changing others
- Number dependent objects unknown или dynamic
- Want notify objects without knowing who they are
- Need broadcast communication pattern
- UI updates based on data changes

❌ **Don't use Observer when:**
- Simple one-to-one dependencies
- Tight coupling acceptable
- Performance critical (many observers)
- Update order matters critically

## Answer (EN)

**Observer Pattern Theory:**
Observer - behavioral pattern that defines one-to-many dependency between objects. Subject maintains list of observers, notifies them on state changes. Solves: need to notify objects without tight coupling, open-ended number of dependents, flexibility in adding/removing observers. Solution: Subject + Observer interface, automatic notification, loose coupling.

**Definition:**

*Theory:* Observer - software design pattern where object (subject) maintains list of dependents (observers). On state change, notifies observers automatically by calling their methods. Ensures loose coupling: subject doesn't know specific observers, observers don't know about other observers. Open-ended: can add/remove observers without changing subject code.

```kotlin
// ✅ Basic Observer Structure
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
*Theory:* Without Observer: subject directly updates specific dependents. Tight coupling - subject knows exact dependents. Hard to reuse, hard to maintain. With Observer: subject knows only Observer interface, doesn't know concrete implementations. Loose coupling - easy to add/remove observers without changing subject code.

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
*Theory:* Number of dependent objects unknown or dynamic. Need to notify open-ended number of objects. Subject doesn't know how many observers, but can notify all. Flexibility - can add/remove observers at runtime without modifying subject.

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
*Theory:* Subject needs to notify objects without knowing who they are. Observer Pattern provides broadcast mechanism: subject publishes changes, interested objects subscribe. Decoupled: subject doesn't know subscribers, subscribers don't know each other.

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
*Theory:* Subject - observable object. Maintains list of observers. Provides methods: addObserver(), removeObserver(), notifyObservers(). Single responsibility: manage observers and notify on state changes. Doesn't depend on concrete observer types.

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
*Theory:* Observer - object interested in state changes. Implements Observer interface with update() method. Registers with subject via addObserver(). Updates state on notify. Single responsibility: respond to notifications. Doesn't know about other observers.

```kotlin
// ✅ Observer interface
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

**1. LiveData Pattern:**
*Theory:* LiveData - lifecycle-aware observable data holder. Implements Observer pattern for UI updates. ViewModel (subject) holds LiveData. View (observer) observes changes. Auto unregisters when lifecycle destroyed. Prevents memory leaks.

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

**2. Flow Pattern:**
*Theory:* Flow - Kotlin coroutines implementation of Observer pattern. Cold stream - emissions happen when collector subscribes. StateFlow/SharedFlow provide hot streams. Backpressure support via Flow operators. Suitable for data streams.

```kotlin
// ✅ Flow Observer Pattern
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
                // Observer reaction
                handleData(data)
            }
        }
    }
}
```

**Advantages:**

1. **Loose Coupling** - Subject and observers decoupled
2. **Flexibility** - Add/remove observers at runtime
3. **Broadcast** - Subject doesn't know specific observers
4. **Open/Closed** - Can add observers without changing subject
5. **Reusability** - Subject and observers reusable independently

**Disadvantages:**

1. **Memory Leaks** - Need to unregister observers (Lapsed listener problem)
2. **Unpredictable Order** - Observers notified in unknown order
3. **Performance** - Notifying many observers expensive
4. **Debugging** - Hard to track which observer caused change
5. **Cascade Updates** - Can lead to complex update chains

**When to Use:**

✅ **Use Observer when:**
- Changes to one object require changing others
- Number of dependent objects unknown or dynamic
- Want to notify objects without knowing who they are
- Need broadcast communication pattern
- UI updates based on data changes

❌ **Don't use Observer when:**
- Simple one-to-one dependencies
- Tight coupling acceptable
- Performance critical (many observers)
- Update order matters critically

---

## Follow-ups

- How does Observer differ from Pub/Sub pattern?
- What are common Android implementations of Observer?
- How to prevent memory leaks with Observer pattern?

## Related Questions

### Prerequisites (Easier)
- Basic design patterns concepts
- Understanding of event-driven programming

### Related (Same Level)
- [[q-strategy-pattern--design-patterns--medium]] - Strategy pattern
- [[q-command-pattern--design-patterns--medium]] - Command pattern
- [[q-state-pattern--design-patterns--medium]] - State pattern

### Advanced (Harder)
- RxJava observable patterns
- Advanced Flow patterns with backpressure
- Event-driven architecture design
