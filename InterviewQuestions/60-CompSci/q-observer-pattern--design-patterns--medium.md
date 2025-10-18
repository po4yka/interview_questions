---
id: 20251012-1227111169
title: "Observer Pattern / Observer Паттерн"
topic: computer-science
difficulty: medium
status: draft
moc: moc-cs
related: [q-throw-vs-throws--programming-languages--easy, q-abstract-class-purpose--programming-languages--medium, q-oop-principles-deep-dive--computer-science--medium]
created: 2025-10-15
tags:
  - design-patterns
  - behavioral-patterns
  - observer
  - gof-patterns
  - publish-subscribe
---
# Observer Pattern

# Question (EN)
> What is the Observer pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Observer? Когда и зачем его следует использовать?

---

## Answer (EN)


**Observer (Наблюдатель)** - это поведенческий паттерн проектирования, который определяет зависимость типа "один ко многим" между объектами таким образом, что при изменении состояния одного объекта все зависящие от него объекты уведомляются об этом и обновляются автоматически.

### Definition


The observer pattern is a software design pattern in which an object, named the **subject**, maintains a list of its dependents, called **observers**, and notifies them automatically of any state changes, usually by calling one of their methods.

### Problems it Solves


The Observer pattern addresses the following problems:

1. **A one-to-many dependency between objects should be defined without making the objects tightly coupled**
2. **It should be ensured that when one object changes state, an open-ended number of dependent objects are updated automatically**
3. **It should be possible that one object can notify an open-ended number of other objects**

### Why is this a problem?


Defining a one-to-many dependency between objects by defining one object (subject) that updates the state of dependent objects directly is inflexible because it couples the subject to particular dependent objects. Tightly coupled objects can be hard to implement in some scenarios, and hard to reuse because they refer to and know about many different objects with different interfaces.

### Solution


The observer pattern proposes the following solution:

- Define **`Subject`** and **`Observer`** objects
- When a subject changes state, all registered observers are notified and updated automatically (and probably asynchronously)

The sole responsibility of a subject is to maintain a list of observers and to notify them of state changes by calling their `update()` operation. The responsibility of observers is to register (and unregister) themselves on a subject and to update their state when they are notified.

This makes subject and observers **loosely coupled**. Subject and observers have no explicit knowledge of each other. Observers can be added and removed independently at run-time.

## Пример: Basic Observer

```java
// Observer interface
public interface Observer {
    void update(Object obj);
}

// Concrete observers
public final class IntObserver implements Observer {
    private final String id;

    IntObserver(String id) {
        this.id = id;
    }

    @Override
    public void update(Object obj) {
        if (obj instanceof Integer) {
            System.out.println("Update IntObserver with id = " + id);
            System.out.println("Update value = " + obj);
        }
    }
}

public final class LongObserver implements Observer {
    private final String id;

    LongObserver(String id) {
        this.id = id;
    }

    @Override
    public void update(Object obj) {
        if (obj instanceof Long) {
            System.out.println("Update LongObserver with id = " + id);
            System.out.println("Update value = " + obj);
        }
    }
}

// Subject
public final class Subject {
    private final List<Observer> observerList;

    Subject() {
        this.observerList = new ArrayList<>();
    }

    void addObserver(Observer observer) {
        observerList.add(observer);
    }

    void removeObserver(Observer observer) {
        observerList.remove(observer);
    }

    void notifyValue(Object obj) {
        for(Observer observer: observerList) {
            observer.update(obj);
        }
    }
}
```

**Usage**:
```java
Subject subject = new Subject();
Observer observer1 = new LongObserver("1");
Observer observer2 = new IntObserver("2");

subject.addObserver(observer1);
subject.addObserver(observer2);

subject.notifyValue(new Long(1000));  // Updates LongObserver
subject.notifyValue(new Integer(500)); // Updates IntObserver
```

## Android/Kotlin Example: UI Updates

```kotlin
// Observer interface
interface DataObserver {
    fun onDataChanged(data: String)
}

// Subject (Observable)
class DataRepository {
    private val observers = mutableListOf<DataObserver>()

    fun addObserver(observer: DataObserver) {
        observers.add(observer)
    }

    fun removeObserver(observer: DataObserver) {
        observers.remove(observer)
    }

    fun updateData(newData: String) {
        // Update internal data
        notifyObservers(newData)
    }

    private fun notifyObservers(data: String) {
        observers.forEach { it.onDataChanged(data) }
    }
}

// Concrete observers (Android components)
class MainActivity : AppCompatActivity(), DataObserver {
    private val repository = DataRepository()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.addObserver(this)
    }

    override fun onDataChanged(data: String) {
        // Update UI
        runOnUiThread {
            textView.text = data
        }
    }

    override fun onDestroy() {
        repository.removeObserver(this)
        super.onDestroy()
    }
}
```

## Kotlin Flow/LiveData Example

```kotlin
// Modern Android approach using Flow
class UserRepository {
    private val _userFlow = MutableStateFlow<User?>(null)
    val userFlow: StateFlow<User?> = _userFlow.asStateFlow()

    fun updateUser(user: User) {
        _userFlow.value = user
    }
}

// Observer (ViewModel)
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    val user: StateFlow<User?> = repository.userFlow

    init {
        viewModelScope.launch {
            user.collect { updatedUser ->
                // Handle user updates
                println("User updated: $updatedUser")
            }
        }
    }
}

// Using LiveData (older approach)
class UserRepositoryLiveData {
    private val _userData = MutableLiveData<User>()
    val userData: LiveData<User> = _userData

    fun updateUser(user: User) {
        _userData.value = user
    }
}
```

### Example Explanation


**Explanation**:

- **`Observer` interface** defines the contract for objects that want to be notified
- **`Subject`** maintains a list of observers and notifies them when state changes
- **Concrete observers** implement the update logic for handling notifications
- In Android, **LiveData and Flow** provide built-in observer pattern implementation
- **ViewModel** often acts as the subject, UI components as observers

## Преимущества и недостатки

### Pros (Преимущества)


1. **Loose coupling** - Provides a loosely coupled design between objects that interact
2. **Flexibility** - Observers can be added/removed at runtime
3. **Broadcast communication** - Subject doesn't need to know about specific observers
4. **Reusability** - Subject and observer classes can be reused independently
5. **Open/Closed Principle** - Can introduce new observers without modifying the subject

### Cons (Недостатки)


1. **Memory leaks** - Can cause memory leaks (Lapsed listener problem) if observers aren't properly unregistered
2. **Unexpected updates** - Observers may receive updates in unpredictable order
3. **Performance overhead** - Notifying many observers can be expensive
4. **Complex debugging** - Hard to track which observer caused what change
5. **Cascade updates** - Can lead to complex update chains that are hard to understand

## Best Practices

```kotlin
// - DO: Always unregister observers to prevent memory leaks
class MyActivity : AppCompatActivity(), DataObserver {
    override fun onDestroy() {
        repository.removeObserver(this)
        super.onDestroy()
    }
}

// - DO: Use lifecycle-aware observers in Android
viewModel.userData.observe(viewLifecycleOwner) { user ->
    // Automatically unregistered when lifecycle is destroyed
}

// - DO: Use Flow/LiveData for Android development
val dataFlow: Flow<Data> = repository.dataFlow
    .flowOn(Dispatchers.IO)

// - DO: Consider using weak references for observers
class WeakObserverList {
    private val observers = mutableListOf<WeakReference<Observer>>()

    fun addObserver(observer: Observer) {
        observers.add(WeakReference(observer))
    }
}

// - DON'T: Forget to remove observers
// - DON'T: Create circular observer dependencies
// - DON'T: Perform heavy operations in update methods
```

**English**: **Observer** is a behavioral design pattern that defines one-to-many dependency between objects so when one object changes state, all dependents are notified automatically. **Problem**: Objects need to be notified of changes without tight coupling. **Solution**: Subject maintains list of observers and notifies them of changes. **Use when**: (1) Changes to one object require changing others, (2) Number of dependent objects is unknown or dynamic, (3) Want to notify objects without knowing who they are. **Android**: LiveData, Flow, StateFlow provide built-in observer pattern. **Pros**: loose coupling, flexibility, broadcast communication. **Cons**: memory leaks if not unregistered, unpredictable update order. **Examples**: UI updates, data binding, event handling, LiveData, Flow.

## Links

- [Observer pattern](https://en.wikipedia.org/wiki/Observer_pattern)
- [Observer Pattern Set 1](https://www.geeksforgeeks.org/observer-pattern-set-1-introduction/)
- [Observer Design Pattern](https://refactoring.guru/design-patterns/observer)

## Further Reading

- [Observer Pattern in Kotlin](https://www.baeldung.com/kotlin/observer-pattern)
- [Android LiveData Overview](https://developer.android.com/topic/libraries/architecture/livedata)
- [Kotlin Flow](https://developer.android.com/kotlin/flow)

---
*Source: Kirchhoff Android Interview Questions*


## Ответ (RU)

### Определение

Паттерн Observer (Наблюдатель) - это паттерн проектирования программного обеспечения, в котором объект, называемый **субъектом (subject)**, поддерживает список своих зависимостей, называемых **наблюдателями (observers)**, и автоматически уведомляет их о любых изменениях состояния, обычно путем вызова одного из их методов.

### Проблемы, которые решает

Паттерн Observer решает следующие проблемы:

1. **Зависимость "один ко многим" между объектами должна быть определена без тесной связанности объектов**
2. **Должно быть обеспечено автоматическое обновление неограниченного числа зависимых объектов при изменении состояния одного объекта**
3. **Должна быть возможность для одного объекта уведомлять неограниченное число других объектов**

### Почему это проблема?

Определение зависимости "один ко многим" между объектами путем определения одного объекта (субъекта), который напрямую обновляет состояние зависимых объектов, негибко, потому что это связывает субъект с конкретными зависимыми объектами. Тесно связанные объекты могут быть сложны в реализации в некоторых сценариях и сложны для повторного использования, потому что они ссылаются и знают о многих разных объектах с разными интерфейсами.

### Решение

Паттерн Observer предлагает следующее решение:

- Определить объекты **`Subject`** и **`Observer`**
- Когда субъект меняет состояние, все зарегистрированные наблюдатели уведомляются и обновляются автоматически (и вероятно асинхронно)

Единственная ответственность субъекта - поддерживать список наблюдателей и уведомлять их об изменениях состояния путем вызова их операции `update()`. Ответственность наблюдателей - регистрировать (и отменять регистрацию) себя на субъекте и обновлять свое состояние при получении уведомления.

Это делает субъект и наблюдателей **слабо связанными**. Субъект и наблюдатели не имеют явного знания друг о друге. Наблюдатели могут быть добавлены и удалены независимо во время выполнения.

### Объяснение примера

**Объяснение**:

- **Интерфейс `Observer`** определяет контракт для объектов, которые хотят получать уведомления
- **`Subject`** поддерживает список наблюдателей и уведомляет их при изменении состояния
- **Конкретные наблюдатели** реализуют логику обновления для обработки уведомлений
- В Android **LiveData и Flow** предоставляют встроенную реализацию паттерна Observer
- **ViewModel** часто выступает в роли субъекта, UI-компоненты - в роли наблюдателей

### Преимущества

1. **Слабая связанность** - Обеспечивает слабо связанный дизайн между взаимодействующими объектами
2. **Гибкость** - Наблюдатели могут быть добавлены/удалены во время выполнения
3. **Широковещательная коммуникация** - Субъекту не нужно знать о конкретных наблюдателях
4. **Переиспользуемость** - Классы субъекта и наблюдателей могут быть повторно использованы независимо
5. **Принцип открытости/закрытости** - Можно вводить новых наблюдателей без модификации субъекта

### Недостатки

1. **Утечки памяти** - Может вызывать утечки памяти (проблема забытого слушателя), если наблюдатели не отменяют регистрацию должным образом
2. **Непредсказуемые обновления** - Наблюдатели могут получать обновления в непредсказуемом порядке
3. **Накладные расходы на производительность** - Уведомление многих наблюдателей может быть дорогостоящим
4. **Сложная отладка** - Сложно отследить, какой наблюдатель вызвал какое изменение
5. **Каскадные обновления** - Может приводить к сложным цепочкам обновлений, которые трудно понять

### Примеры в Android

В Android паттерн Observer широко используется:

- **LiveData** - Lifecycle-aware реализация паттерна Observer для UI-обновлений
- **Flow/StateFlow** - Современная асинхронная реализация на основе корутин
- **RxJava** - Реактивное программирование с Observable и Observer
- **Data Binding** - Автоматическое обновление UI при изменении данных
- **BroadcastReceiver** - Системные события как паттерн Observer

### Когда использовать

Используйте паттерн Observer когда:

1. **Изменения одного объекта требуют изменения других** - Несколько объектов должны реагировать на изменения
2. **Количество зависимых объектов неизвестно или динамично** - Список наблюдателей может меняться
3. **Нужно уведомлять объекты, не зная, кто они** - Широковещательная коммуникация
4. **UI должен реагировать на изменения данных** - Автоматическое обновление интерфейса

### Лучшие практики

В Android для избежания утечек памяти:

1. **Всегда отменяйте регистрацию наблюдателей** - В onDestroy() или при уничтожении компонента
2. **Используйте lifecycle-aware компоненты** - LiveData автоматически отписывается
3. **Используйте viewLifecycleOwner** - Для фрагментов используйте viewLifecycleOwner вместо this
4. **Рассмотрите WeakReference** - Для предотвращения удержания ссылок на активности
5. **Избегайте тяжелых операций в update** - Выполняйте в фоновых потоках


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Behavioral Patterns
- [[q-strategy-pattern--design-patterns--medium]] - Strategy pattern
- [[q-command-pattern--design-patterns--medium]] - Command pattern
- [[q-template-method-pattern--design-patterns--medium]] - Template Method pattern
- [[q-iterator-pattern--design-patterns--medium]] - Iterator pattern
- [[q-state-pattern--design-patterns--medium]] - State pattern

### Creational Patterns
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern

### Structural Patterns
- [[q-adapter-pattern--design-patterns--medium]] - Adapter pattern

