---
id: cs-009
title: Adapter Pattern / Adapter Паттерн
aliases:
- Adapter Pattern
- Паттерн Adapter
topic: cs
subtopics:
- adapter
- design-patterns
- structural-patterns
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-cs
related:
- c-adapter-pattern
- c-design-patterns
- q-abstract-factory-pattern--cs--medium
created: 2025-10-15
updated: 2025-11-11
tags:
- adapter
- design-patterns
- difficulty/medium
- gof-patterns
- structural-patterns
- wrapper
sources:
- https://refactoring.guru/design-patterns/adapter
anki_cards:
- slug: cs-009-0-en
  language: en
  anki_id: 1768454033342
  synced_at: '2026-01-15T09:41:02.774967'
- slug: cs-009-0-ru
  language: ru
  anki_id: 1768454033362
  synced_at: '2026-01-15T09:41:02.777609'
---
# Вопрос (RU)
> Что такое паттерн `Adapter`? Когда и зачем его использовать?

# Question (EN)
> What is the `Adapter` pattern? When and why should it be used?

---

## Ответ (RU)

**Теория `Adapter`:**
`Adapter` — структурный паттерн, который позволяет двум несовместимым интерфейсам работать вместе, действуя как мост между двумя классами с разными интерфейсами. Решает проблему невозможности прямого переиспользования класса из-за несовместимого интерфейса.

**Проблема:**
Часто (уже существующий) класс не может быть переиспользован только потому, что его интерфейс не соответствует интерфейсу, требуемому клиентами или существующим абстракциям. Без адаптации клиентский код оказывается жёстко привязан к конкретным реализациям и их контрактам, что усложняет подмену реализаций и интеграцию стороннего кода.

**Решение:**
Определить отдельный класс "`Adapter`", который конвертирует (несовместимый) интерфейс класса ("Adaptee") в другой интерфейс ("Target"), требуемый клиентами. Клиент работает с Target, а `Adapter` внутри переадресует вызовы к Adaptee, позволяя переиспользовать существующие классы с несовместимым интерфейсом без их изменения.

**Ключевые компоненты:**
- **Target** — интерфейс, ожидаемый клиентом
- **Adaptee** — существующая функциональность с несовместимым интерфейсом
- **`Adapter`** — класс, который реализует интерфейс Target и оборачивает Adaptee

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
// ✅ RecyclerView Adapter — пример адаптера между моделью данных и представлением RecyclerView
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

(Здесь `Adapter` выступает посредником, приводящим коллекцию "сырых" данных к форме, с которой умеет работать `RecyclerView`. Однако это не буквальный учебный пример GoF `Adapter`, а прикладная вариация идеи адаптации.)

**Преимущества:**
- Переиспользование существующего кода без его изменения
- Изоляция логики преобразования интерфейсов в отдельном классе (улучшение соблюдения Single Responsibility)
- Гибкость — легко добавлять и менять адаптеры под разные источники/клиентов
- Соответствие принципу открытости/закрытости
- Ослабление связности: клиент зависит от Target, а не от конкретных реализаций Adaptee

**Недостатки:**
- Увеличенная структурная сложность
- Небольшие накладные расходы на дополнительный уровень индирекции
- Сложности поддержки при большом количестве адаптеров
- Риск избыточной инженерии при слишком агрессивном применении

## Дополнительные Вопросы (RU)

- Отличия между `Adapter` и Decorator?
- Когда использовать extension-функции, а когда адаптеры?
- Лучшие практики использования `RecyclerView` адаптеров?

## Ссылки (RU)

- [[c-design-patterns]]
- [[c-adapter-pattern]]
- https://refactoring.guru/design-patterns/adapter

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-abstract-factory-pattern--cs--medium]] - Паттерн Abstract Factory

### Похожие (средний уровень)

### Продвинутые (сложнее)

---

## Answer (EN)

**`Adapter` Theory:**
`Adapter` is a structural design pattern that lets two incompatible interfaces work together by acting as a bridge between classes with different interfaces. It solves the problem of not being able to directly reuse an existing class because its interface is incompatible with what the client expects.

**Problem:**
Often an existing class cannot be reused simply because its interface does not match the interface required by clients or existing abstractions. Without adaptation, client code becomes tightly coupled to concrete implementations and their contracts, which complicates swapping implementations and integrating third-party code.

**Solution:**
Define a separate "`Adapter`" class that converts the (incompatible) interface of a class (the "Adaptee") into another interface (the "Target") required by clients. The client works with Target, and the `Adapter` internally translates calls to the Adaptee, enabling reuse of existing classes with incompatible interfaces without modifying them.

**Key Components:**
- **Target** — interface expected by the client
- **Adaptee** — existing functionality with an incompatible interface
- **`Adapter`** — class that implements Target and wraps Adaptee

**`Application`:**
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

**Android `Application`:**
```kotlin
// ✅ RecyclerView Adapter — an adapter between the data model and RecyclerView's view API
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

(Here the adapter plays a mediator role, adapting a collection of raw data into the form that `RecyclerView` understands. It illustrates the idea of adaptation, though it is not a literal textbook GoF `Adapter` example.)

**Advantages:**
- Reuse of existing code without modification
- Isolation of interface-translation logic in a dedicated class (better Single Responsibility adherence)
- Flexibility — easy to introduce or swap adapters for different sources/clients
- Compliance with the Open/Closed Principle
- Decouples the client from concrete Adaptee implementations via Target

**Disadvantages:**
- Increased structural complexity
- Minor performance overhead due to an extra indirection layer
- Maintenance challenges when many adapters are introduced
- Risk of over-engineering if used unnecessarily

## Follow-ups

- `Adapter` vs Decorator pattern differences?
- When to use extension functions vs adapters?
- `RecyclerView` adapters best practices?

## References

- [[c-design-patterns]]
- [[c-adapter-pattern]]
- https://refactoring.guru/design-patterns/adapter

## Related Questions

### Prerequisites (Easier)
- [[q-abstract-factory-pattern--cs--medium]] - Abstract Factory pattern

### Related (Medium)

### Advanced (Harder)
