---
id: cs-030
title: "Abstract Factory Pattern / Abstract Factory Паттерн"
aliases: ["Abstract Factory Pattern", "Паттерн Abstract Factory"]
topic: cs
subtopics: [design-patterns, creational-patterns, factory]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-factory-method-pattern--design-patterns--medium, q-builder-pattern--design-patterns--medium, q-design-patterns-fundamentals--software-engineering--hard]
created: 2025-10-15
updated: 2025-01-25
tags: [abstract-factory, creational-patterns, design-patterns, factory, gof-patterns, difficulty/medium]
sources: [https://refactoring.guru/design-patterns/abstract-factory]
---

# Вопрос (RU)
> Что такое паттерн Abstract Factory? Когда и зачем его использовать?

# Question (EN)
> What is the Abstract Factory pattern? When and why should it be used?

---

## Ответ (RU)

**Теория Abstract Factory:**
Abstract Factory - порождающий паттерн, цель которого - предоставить единый интерфейс для создания семейств связанных объектов без раскрытия конкретной реализации. Решает проблему создания семейств объектов одной темы, гарантируя их совместимость и согласованность.

**Проблема:**
Создание объектов напрямую внутри класса делает код негибким - привязывает к конкретным объектам, затрудняет изменение реализации, препятствует повторному использованию, затрудняет тестирование.

**Решение:**
Инкапсулировать создание объектов в отдельном (фабричном) объекте, делегировать создание фабричному объекту. Это делает класс независимым от способа создания объектов - фабричный объект может быть заменён во время выполнения.

**Ключевые компоненты:**
- **Abstract Factory** - интерфейс для создания семейств объектов
- **Concrete Factory** - конкретная реализация для каждого семейства
- **Abstract Product** - интерфейс для объекта семейства
- **Concrete Product** - конкретные реализации объектов

**Применение:**
```kotlin
// ✅ Интерфейсы продуктов
interface Button { fun display(): String }
interface Window { fun display(): String }

// ✅ Продукты для Light темы
class LightButton : Button {
    override fun display() = "Displaying Light Theme Button"
}
class LightWindow : Window {
    override fun display() = "Displaying Light Theme Window"
}

// ✅ Продукты для Dark темы
class DarkButton : Button {
    override fun display() = "Displaying Dark Theme Button"
}
class DarkWindow : Window {
    override fun display() = "Displaying Dark Theme Window"
}

// ✅ Abstract Factory
interface GUIFactory {
    fun createButton(): Button
    fun createWindow(): Window
}

// ✅ Конкретные фабрики
class LightThemeFactory : GUIFactory {
    override fun createButton() = LightButton()
    override fun createWindow() = LightWindow()
}

class DarkThemeFactory : GUIFactory {
    override fun createButton() = DarkButton()
    override fun createWindow() = DarkWindow()
}
```

**Преимущества:**
- Обеспечивает совместимость созданных объектов
- Снижает связанность
- Обеспечивает согласованность интерфейса
- Изолирует конкретные классы от клиента
- Легко менять семейства продуктов

**Недостатки:**
- Много классов для множественных семейств
- Излишняя сложность для простых систем
- Поддержка новых продуктов требует расширения фабрики

**Когда использовать:**
- Клиент независим от способа создания объектов
- Система состоит из нескольких семейств объектов
- Нужно значение времени выполнения для построения зависимости

---

## Answer (EN)

**Abstract Factory Theory:**
Abstract Factory is a creational design pattern that provides a single interface for creating families of related objects without exposing their concrete implementation. Solves the problem of creating families of objects with the same theme, ensuring compatibility and consistency.

**Problem:**
Creating objects directly within a class makes code inflexible - binds to particular objects, makes it impossible to change implementation later, prevents reusability, makes testing difficult.

**Solution:**
Encapsulate object creation in a separate (factory) object by defining and implementing an interface for creating objects, delegate object creation to a factory object. This makes a class independent of how its objects are created - factory object can be exchanged at runtime.

**Key Components:**
- **Abstract Factory** - interface for creating families of objects
- **Concrete Factory** - concrete implementation for each family
- **Abstract Product** - interface for family objects
- **Concrete Product** - concrete implementations of objects

**Application:**
```kotlin
// ✅ Product interfaces
interface Button { fun display(): String }
interface Window { fun display(): String }

// ✅ Products for Light theme
class LightButton : Button {
    override fun display() = "Displaying Light Theme Button"
}
class LightWindow : Window {
    override fun display() = "Displaying Light Theme Window"
}

// ✅ Products for Dark theme
class DarkButton : Button {
    override fun display() = "Displaying Dark Theme Button"
}
class DarkWindow : Window {
    override fun display() = "Displaying Dark Theme Window"
}

// ✅ Abstract Factory
interface GUIFactory {
    fun createButton(): Button
    fun createWindow(): Window
}

// ✅ Concrete factories
class LightThemeFactory : GUIFactory {
    override fun createButton() = LightButton()
    override fun createWindow() = LightWindow()
}

class DarkThemeFactory : GUIFactory {
    override fun createButton() = DarkButton()
    override fun createWindow() = DarkWindow()
}
```

**Advantages:**
- Ensures compatibility of created objects
- Promotes decoupling
- Enforces consistency of interface
- Isolates concrete classes from client
- Easy to exchange product families

**Disadvantages:**
- Many classes for multiple families
- Complexity for simple systems
- Supporting new products requires extending factory

**When to use:**
- Client is independent of how objects are created
- System consists of multiple families of objects
- Need runtime value to construct particular dependency

## Follow-ups

- Abstract Factory vs Factory Method pattern?
- Android UI theme implementation?
- Database factory patterns?

## References

- [[c-design-patterns]]
- https://refactoring.guru/design-patterns/abstract-factory

## Related Questions

### Prerequisites (Easier)
- [[q-design-patterns-fundamentals--software-engineering--hard]] - Design patterns overview

### Related (Medium)
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern
- [[q-builder-pattern--design-patterns--medium]] - Builder pattern

### Advanced (Harder)
- [[q-interpreter-pattern--design-patterns--hard]] - Interpreter pattern
