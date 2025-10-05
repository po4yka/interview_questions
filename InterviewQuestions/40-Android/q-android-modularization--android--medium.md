---
tags:
  - android
  - modularization
  - architecture
  - multi-module
  - gradle
  - difficulty/medium
difficulty: medium
---

# Android Modularization / Модуляризация Android

**English**: Describe Android modularization in general

## Answer

**Android modularization** is a practice of organizing a codebase into **loosely coupled and self-contained parts** where each part is a module. A project with multiple Gradle modules is known as a **multi-module project**.

In an ever-growing codebase, scalability, readability, and overall code quality often decrease through time. This comes as a result of the codebase increasing in size without its maintainers taking active measures to enforce a structure that is easily maintainable. Modularization is a means of structuring your codebase in a way that improves maintainability and helps avoid these problems.

**What is modularization?**

Modularization is a practice of organizing a codebase into loosely coupled and self-contained parts. Each part is a module. Each module is independent and serves a clear purpose. By dividing a problem into smaller and easier to solve subproblems, you reduce the complexity of designing and maintaining a large system.

**Benefits of modularization:**

**Primary benefits (only achievable with modularization):**

| Benefit | Summary |
|---|---|
| **Reusability** | Modularization enables opportunities for code sharing and building multiple apps from the same foundation. Modules are effectively building blocks. Apps should be a sum of their features where the features are organized as separate modules. The functionality that a certain module provides may or may not be enabled in a particular app. For example, a `:feature:news` can be a part of the full version flavor and wear app but not part of the demo version flavor. |
| **Strict visibility control** | Modules enable you to easily control what you expose to other parts of your codebase. You can mark everything but your public interface as `internal` or `private` to prevent it from being used outside the module. |
| **Customizable delivery** | Play Feature Delivery uses the advanced capabilities of app bundles, allowing you to deliver certain features of your app conditionally or on demand. |

**Additional benefits (enhanced by modularization):**

| Benefit | Summary |
|---|---|
| **Scalability** | In a tightly coupled codebase a single change can trigger a cascade of alterations in seemingly unrelated parts of code. A properly modularized project will embrace the separation of concerns principle and therefore limit the coupling. This empowers the contributors through greater autonomy. |
| **Ownership** | In addition to enabling autonomy, modules can also be used to enforce accountability. A module can have a dedicated owner who is responsible for maintaining the code, fixing bugs, adding tests, and reviewing changes. |
| **Encapsulation** | Encapsulation means that each part of your code should have the smallest possible amount of knowledge about other parts. Isolated code is easier to read and understand. |
| **Testability** | Testability characterizes how easy it is to test your code. A testable code is one where components can be easily tested in isolation. |
| **Build time** | Some Gradle functionalities such as incremental build, build cache or parallel build, can leverage modularity to improve build performance. |

**Common pitfalls:**

The granularity of your codebase is the extent to which it is composed of modules. A more granular codebase has more, smaller modules. When designing a modularized codebase, you should decide on a level of granularity. To do so, take into account the size of your codebase and its relative complexity.

Some common pitfalls are as follows:

- **Too fine-grained**: Every module brings a certain amount of overhead in the form of increased build complexity and boilerplate code. A complex build configuration makes it difficult to keep configurations consistent across modules. Too much boilerplate code results in a cumbersome codebase that is difficult to maintain. If overhead counteracts scalability improvements, you should consider consolidating some modules.

- **Too coarse-grained**: Conversely, if your modules are growing too large you might end up with yet another monolith and miss the benefits that modularity has to offer. For example, in a small project it's ok to put the data layer inside a single module. But as it grows, it might be necessary to separate repositories and data sources into standalone modules.

- **Too complex**: It doesn't always make sense to modularize your project. A dominating factor is the size of the codebase. If you don't expect your project to grow beyond a certain threshold, the scalability and build time gains won't apply.

**Example structure:**

```
app/
├── :app (app module)
├── :feature:news
├── :feature:profile
├── :feature:settings
├── :core:data
├── :core:network
├── :core:database
└── :core:ui
```

**Summary:**

- **Modularization**: Organizing codebase into loosely coupled modules
- **Benefits**: Reusability, strict visibility, customizable delivery, scalability, ownership
- **Challenges**: Finding the right granularity
- **Use cases**: Large projects, multiple apps from same codebase, feature delivery
- **Best practices**: Separation of concerns, proper dependency management, clear module boundaries

**Source**: [Guide to Android app modularization](https://developer.android.com/topic/modularization)

## Ответ

**Модуляризация Android** — это практика организации кодовой базы на слабо связанные и самодостаточные части, где каждая часть является модулем. Проект с несколькими модулями Gradle называется многомодульным проектом.

В постоянно растущей кодовой базе масштабируемость, читаемость и общее качество кода часто снижаются со временем. Это происходит в результате увеличения размера кодовой базы без активных мер со стороны её поддерживающих для обеспечения легко поддерживаемой структуры. Модуляризация — это способ структурирования кодовой базы, который улучшает её поддерживаемость и помогает избежать этих проблем.

**Что такое модуляризация?**

Модуляризация — это практика организации кодовой базы на слабо связанные и самодостаточные части. Каждая часть — это модуль. Каждый модуль независим и служит чёткой цели. Разделяя проблему на более мелкие и легко решаемые подзадачи, вы снижаете сложность проектирования и поддержки большой системы.

**Преимущества модуляризации:**

- **Переиспользуемость** — возможность совместного использования кода и создания нескольких приложений на одной основе
- **Строгий контроль видимости** — возможность контролировать, что вы предоставляете другим частям кодовой базы
- **Настраиваемая доставка** — Play Feature Delivery позволяет доставлять определённые функции приложения условно или по требованию
- **Масштабируемость** — правильно модуляризованный проект следует принципу разделения ответственности
- **Владение** — модули могут иметь выделенных владельцев, ответственных за поддержку кода
- **Инкапсуляция** — изолированный код легче читать и понимать
- **Тестируемость** — компоненты можно легко тестировать изолированно
- **Время сборки** — функциональность Gradle может использовать модульность для улучшения производительности сборки

**Распространённые ошибки:**

- **Слишком детальная модуляризация** — каждый модуль добавляет накладные расходы в виде повышенной сложности сборки
- **Слишком грубая модуляризация** — если модули становятся слишком большими, вы получаете ещё один монолит
- **Слишком сложная** — не всегда имеет смысл модуляризировать проект, особенно если он небольшой

**Резюме:**

Модуляризация — это организация кодовой базы на слабо связанные модули для улучшения переиспользуемости, масштабируемости, тестируемости и времени сборки. Ключевые преимущества включают строгий контроль видимости, настраиваемую доставку функций и лучшее разделение ответственности. Важно найти правильный баланс детализации модулей.
