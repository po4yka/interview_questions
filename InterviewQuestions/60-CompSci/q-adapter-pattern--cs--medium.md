---
id: cs-009
title: "Adapter Pattern / Adapter Паттерн"
aliases: ["Adapter Pattern", "Паттерн Adapter"]
topic: cs
subtopics: [adapter, design-patterns, structural-patterns]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-decorator-pattern, c-design-patterns, c-facade-pattern]
created: 2025-10-15
updated: 2025-01-25
tags: [adapter, design-patterns, difficulty/medium, gof-patterns, structural-patterns, wrapper]
sources: [https://refactoring.guru/design-patterns/adapter]
---

# Вопрос (RU)
> Что такое паттерн Adapter? Когда и зачем его использовать?

# Question (EN)
> What is the Adapter pattern? When and why should it be used?

---

## Ответ (RU)

**Теория Adapter:**
Adapter - структурный паттерн, который позволяет двум несовместимым интерфейсам работать вместе, действуя как мост между двумя классами с разными интерфейсами. Решает проблему невозможности переиспользования класса из-за несовместимого интерфейса.

**Проблема:**
Часто (уже существующий) класс не может быть переиспользован только потому, что его интерфейс не соответствует интерфейсу, требуемому клиентами. Негибко: привязывает к конкретным объектам, затрудняет изменение реализации.

**Решение:**
Определить отдельный класс "adapter", который конвертирует (несовместимый) интерфейс класса ("adaptee") в другой интерфейс ("target"), требуемый клиентами. Работать через adapter для переиспользования классов с несовместимым интерфейсом.

**Ключевые компоненты:**
- **Target** - интерфейс, ожидаемый клиентом
- **Adaptee** - существующая функциональность с несовместимым интерфейсом
- **Adapter** - класс, который реализует целевой интерфейс и оборачивает adaptee

**Применение:**
```kotlin
// ✅ Target interface
interface ThreePinSocket {
    fun acceptThreePinPlug()
}

// ✅ Adaptee
class TwoPinPlug {
    fun insertTwoPinPlug() {
        println("Two-pin plug inserted!")
    }
}

// ✅ Adapter
class PlugAdapter(private val plug: TwoPinPlug) : ThreePinSocket {
    override fun acceptThreePinPlug() {
        plug.insertTwoPinPlug()
        println("Adapter made it compatible with three-pin socket!")
    }
}
```

**Android применение:**
```kotlin
// ✅ RecyclerView Adapter - классический пример
class UserAdapter(private val users: List<User>) :
    RecyclerView.Adapter<UserViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)
        return UserViewHolder(view)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        holder.bind(users[position])
    }

    override fun getItemCount() = users.size
}
```

**Преимущества:**
- Переиспользование кода без изменения
- Единая ответственность
- Гибкость - легко менять адаптеры
- Принцип открытости/закрытости
- Разделение клиента от реализаций

**Недостатки:**
- Увеличенная сложность
- Издержки производительности
- Сложности поддержки при множестве адаптеров
- Риск избыточной инженерии

---

## Answer (EN)

**Adapter Theory:**
Adapter is a structural design pattern that permits two incompatible interfaces to work together by acting as a bridge between two classes with different interfaces. Solves the problem of inability to reuse an existing class due to incompatible interface.

**Problem:**
Often an (already existing) class cannot be reused only because its interface does not conform to the interface clients require. Inflexible: binds to particular objects, makes it impossible to change implementation later.

**Solution:**
Define a separate "adapter" class that converts the (incompatible) interface of a class ("adaptee") into another interface ("target") that clients require. Work through an adapter to reuse classes with incompatible interface.

**Key Components:**
- **Target** - interface expected by client
- **Adaptee** - existing functionality with incompatible interface
- **Adapter** - class that implements target interface and wraps adaptee

**Application:**
```kotlin
// ✅ Target interface
interface ThreePinSocket {
    fun acceptThreePinPlug()
}

// ✅ Adaptee
class TwoPinPlug {
    fun insertTwoPinPlug() {
        println("Two-pin plug inserted!")
    }
}

// ✅ Adapter
class PlugAdapter(private val plug: TwoPinPlug) : ThreePinSocket {
    override fun acceptThreePinPlug() {
        plug.insertTwoPinPlug()
        println("Adapter made it compatible with three-pin socket!")
    }
}
```

**Android Application:**
```kotlin
// ✅ RecyclerView Adapter - classic example
class UserAdapter(private val users: List<User>) :
    RecyclerView.Adapter<UserViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)
        return UserViewHolder(view)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        holder.bind(users[position])
    }

    override fun getItemCount() = users.size
}
```

**Advantages:**
- Code reusability without modification
- Single Responsibility
- Flexibility - easy to switch adapters
- Open/Closed Principle
- Decoupling client from implementations

**Disadvantages:**
- Increased complexity
- Performance overhead
- Maintenance challenges with multiple adapters
- Over-engineering risk

## Follow-ups

- Adapter vs Decorator pattern differences?
- When to use extension functions vs adapters?
- RecyclerView adapters best practices?

## References

- [[c-design-patterns]]
- https://refactoring.guru/design-patterns/adapter

## Related Questions

### Prerequisites (Easier)
- [[q-design-patterns-fundamentals--software-engineering--hard]] - Design patterns overview

### Related (Medium)
- [[q-decorator-pattern--design-patterns--medium]] - Decorator pattern
- [[q-facade-pattern--design-patterns--medium]] - Facade pattern
- [[q-proxy-pattern--design-patterns--medium]] - Proxy pattern

### Advanced (Harder)
- [[q-strategy-pattern--design-patterns--medium]] - Strategy pattern
