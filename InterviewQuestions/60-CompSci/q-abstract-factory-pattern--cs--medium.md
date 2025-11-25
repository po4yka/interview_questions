---
id: cs-030
title: "Abstract Factory Pattern / Abstract Factory Паттерн"
aliases: ["Abstract Factory Pattern", "Паттерн Abstract Factory"]
topic: cs
subtopics: [creational-patterns, design-patterns, factory]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, c-computer-science, q-abstract-class-purpose--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [abstract-factory, creational-patterns, design-patterns, difficulty/medium, factory, gof-patterns]
sources: ["https://refactoring.guru/design-patterns/abstract-factory"]

date created: Saturday, November 1st 2025, 1:26:52 pm
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---

# Вопрос (RU)
> Что такое паттерн Abstract Factory? Когда и зачем его использовать?

# Question (EN)
> What is the Abstract Factory pattern? When and why should it be used?

---

## Ответ (RU)

**Теория Abstract Factory:**
Abstract Factory — порождающий паттерн, цель которого — предоставить единый интерфейс для создания семейств связанных объектов без раскрытия их конкретной реализации. Он решает проблему создания семейств объектов одной темы, гарантируя их совместимость и согласованность.

**Проблема:**
Создание объектов напрямую внутри класса делает код негибким: жёстко привязывает к конкретным реализациям, усложняет замену реализации, препятствует повторному использованию и усложняет тестирование.

**Решение:**
Инкапсулировать создание объектов в отдельном (фабричном) объекте: определить интерфейс фабрики и делегировать ей создание продуктов. Клиентский код работает только с абстракциями (Abstract Factory и Abstract Product), а конкретная фабрика может быть выбрана или заменена во время выполнения для переключения семейств продуктов без изменения клиентского кода.

**Ключевые компоненты:**
- **Abstract Factory** — интерфейс для создания семейств связанных объектов
- **Concrete Factory** — конкретная реализация для каждого семейства
- **Abstract Product** — интерфейс/абстракция для объектов семейства
- **Concrete Product** — конкретные реализации объектов

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

// Клиентский код получает GUIFactory (например, на основе темы)
// и использует только её абстрактный интерфейс:
fun createUI(factory: GUIFactory): Pair<Button, Window> =
    factory.createButton() to factory.createWindow()
```

**Преимущества:**
- Обеспечивает совместимость созданных объектов
- Снижает связанность между клиентом и конкретными классами
- Обеспечивает согласованность интерфейсов внутри семейства
- Изолирует конкретные классы от клиента
- Позволяет легко менять семейства продуктов (сменой фабрики)

**Недостатки:**
- Увеличивает количество классов при множестве семейств
- Вводит излишнюю сложность для простых систем
- Добавление новых типов продуктов требует изменения всех фабрик

**Когда использовать:**
- Клиент должен быть независим от того, как создаются и как представлены объекты
- Система использует несколько семейств связанных продуктов, и нужно гарантировать их совместимость
- Необходимо выбирать конкретное семейство продуктов (конкретную фабрику) на этапе конфигурации или во время выполнения (например, по платформе, теме, окружению)

---

## Answer (EN)

**Abstract Factory Theory:**
Abstract Factory is a creational design pattern that provides a single interface for creating families of related objects without exposing their concrete implementations. It solves the problem of creating themed families of objects while ensuring their compatibility and consistency.

**Problem:**
Creating objects directly inside a class makes the code inflexible: it tightly couples the client to concrete implementations, makes replacing implementations harder, hinders reuse, and complicates testing.

**Solution:**
Encapsulate object creation in a separate factory object: define a factory interface and delegate product creation to it. Client code works only with abstractions (Abstract Factory and Abstract Products), and a concrete factory can be selected or swapped at runtime to switch product families without changing client code.

**Key Components:**
- **Abstract Factory** - interface for creating families of related objects
- **Concrete Factory** - concrete implementation for each product family
- **Abstract Product** - interface/abstraction for family objects
- **Concrete Product** - concrete implementations of the products

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

// Client code receives a GUIFactory (e.g., based on theme)
// and uses only its abstract interface:
fun createUI(factory: GUIFactory): Pair<Button, Window> =
    factory.createButton() to factory.createWindow()
```

**Advantages:**
- Ensures compatibility of created objects
- Promotes decoupling between client and concrete classes
- Enforces consistency of interfaces within a family
- Isolates concrete classes from client code
- Makes it easy to switch product families (by swapping factories)

**Disadvantages:**
- Increases the number of classes when many families exist
- Adds unnecessary complexity for simple systems
- Adding new product types requires modifying all factories

**When to use:**
- Client should be independent of how objects are created and represented
- System consists of multiple families of related products that must be used together
- You need to select the concrete product family (concrete factory) at configuration time or at runtime (e.g., by platform, theme, or environment)

## Follow-ups

- Abstract Factory vs Factory Method pattern?
- Android UI theme implementation?
- Database factory patterns?

## References

- https://refactoring.guru/design-patterns/abstract-factory

## Related Questions

### Prerequisites (Easier)
- [[q-abstract-class-purpose--cs--medium]] - Abstract class purpose

### Related (Medium)
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern

### Advanced (Harder)
- No specific advanced related questions linked (previous broken links removed)
