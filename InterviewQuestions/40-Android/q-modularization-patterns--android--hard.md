---
id: android-005
title: Android Modularization Patterns / Паттерны модуляризации в Android
aliases: [Android Modularization Patterns, Паттерны модуляризации в Android]
topic: android
subtopics:
  - architecture-clean
  - architecture-modularization
question_kind: theory
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
source: https://github.com/Kirchhoff-Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository
status: draft
moc: moc-android
related:
  - c-clean-architecture
  - q-android-architectural-patterns--android--medium
  - q-android-lint-tool--android--medium
  - q-android-modularization--android--medium
  - q-does-state-made-in-compose-help-avoid-race-condition--android--medium
  - q-what-should-you-pay-attention-to-in-order-to-optimize-a-large-list--android--hard
created: 2025-10-05
updated: 2025-11-11
tags: [android/architecture-clean, android/architecture-modularization, difficulty/hard, en, ru]
date created: Saturday, November 1st 2025, 12:46:58 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---

# Вопрос (RU)
> Какие паттерны модуляризации вы знаете?

# Question (EN)
> What modularization patterns do you know?

---

## Ответ (RU)

### Принцип Высокой Связности И Слабого Зацепления

Одним из способов описания модульной кодовой базы является использование свойств **зацепления (coupling)** и **связности (cohesion)**. Зацепление измеряет степень зависимости модулей друг от друга. Связность в данном контексте измеряет, насколько элементы одного модуля функционально связаны. Как общее правило, вы должны стремиться к слабому зацеплению и высокой связности:

- **Слабое зацепление** означает, что модули должны быть максимально независимыми друг от друга, чтобы изменения в одном модуле имели нулевое или минимальное влияние на другие модули. **Модули не должны знать о внутреннем устройстве других модулей.**
- **Высокая связность** означает, что модуль представляет собой совокупность кода, который работает как целостная система. У модулей должны быть чётко определённые зоны ответственности в рамках определённой предметной области. Например, в приложении для электронных книг не стоит смешивать код, связанный с книгами, и код, связанный с оплатой, в одном модуле, так как это разные функциональные домены.

### Взаимодействие Между Модулями

Модули редко существуют в полной изоляции и часто зависят от других модулей и взаимодействуют с ними. Важно поддерживать низкое зацепление даже тогда, когда модули активно обмениваются данными. Иногда прямое взаимодействие между двумя модулями нежелательно из-за архитектурных ограничений или вообще невозможно, например при циклических зависимостях.

Чтобы преодолеть эту проблему, вы можете использовать третий модуль, выступающий посредником между двумя другими модулями. Модуль-посредник может принимать сообщения от обоих модулей и перенаправлять их по мере необходимости. Часто таким модулем является модуль приложения, которому принадлежит граф навигации.

Хотя навигационные библиотеки технически позволяют передавать `Parcelable`/`Serializable`-объекты как аргументы навигации, в модульной архитектуре следует предпочитать передачу простых идентификаторов, которые фичи могут использовать для доступа и загрузки нужных данных из слоя данных. Так вы снижаете зацепление, не раскрываете детали реализации и не нарушаете принцип единственного источника истины.

В этой схеме оба feature-модуля зависят от общего data-модуля. Это позволяет минимизировать объём данных, которые модулю-посреднику необходимо пересылать, и поддерживать низкое зацепление между модулями. Вместо передачи объектов модули обмениваются примитивными идентификаторами и загружают ресурсы из общего модуля данных.

### Инверсия Зависимостей

Инверсия зависимостей — это подход, при котором вы организуете код так, чтобы абстракции были отделены от конкретных реализаций.

- **Абстракция**: контракт, определяющий, как компоненты или модули в приложении взаимодействуют друг с другом. Модули абстракций определяют API системы и содержат интерфейсы и модели.
- **Конкретная реализация**: модули, которые зависят от модуля абстракций и реализуют описанное в нём поведение.

Модули, использующие поведение, определённое в модуле абстракций, должны зависеть только от абстракций, а не от конкретных реализаций.

Feature-модуль связан с модулем реализации через механизм внедрения зависимостей (DI). Feature-модуль не создаёт напрямую, например, экземпляр базы данных. Вместо этого он объявляет, какие зависимости ему нужны, а необходимые реализации предоставляются извне, обычно на уровне application-модуля.

Отделение API от их реализаций полезно в следующих случаях:

- **Разнообразные реализации**: если части системы можно реализовать несколькими способами, чёткий API позволяет взаимозаменяемость реализаций. Например, система рендеринга на OpenGL или Vulkan, или биллинг через Play Billing или внутренний API.
- **Несколько приложений**: если вы разрабатываете несколько приложений с общими возможностями для разных платформ, можно определить общие API и реализовать платформо-специфичные модули отдельно.
- **Независимые команды**: разделение позволяет командам работать над разными частями кодовой базы параллельно, фокусируясь на контрактах API, не погружаясь в детали реализации других модулей.
- **Большая кодовая база**: при большой или сложной кодовой базе отделение API от реализации упрощает поддержку за счёт более мелких, понятных и независимых модулей.

### Поддерживайте Согласованность Конфигурации

Каждый модуль добавляет накладные расходы на конфигурацию. При большом количестве модулей поддержание единой конфигурации становится сложной задачей. Важно, чтобы модули использовали согласованные версии зависимостей. Массовое ручное обновление версий во множестве модулей трудоёмко и повышает риск ошибок. Для решения этой проблемы используйте инструменты Gradle для централизованного управления конфигурацией:

- [Version catalogs](https://docs.gradle.org/current/userguide/platforms.html) — типобезопасный список зависимостей, объявляемый централизованно и доступный всем модулям проекта.
- [Convention plugins](https://docs.gradle.org/current/samples/sample_convention_plugins.html) — для переиспользования общей логики сборки между модулями.

### Раскрывайте Как Можно Меньше

Публичный интерфейс модуля должен быть минимальным и включать только необходимое. Он не должен раскрывать детали реализации наружу. Ограничивайте область видимости сущностей максимально разумно. Используйте модификаторы видимости Kotlin `private` и `internal`, чтобы сделать объявления доступными только внутри модуля. При объявлении зависимостей в модуле отдавайте предпочтение `implementation` вместо `api`. `api` раскрывает транзитивные зависимости потребителям модуля; использование `implementation` уменьшает количество модулей, которые требуется пересобирать, и может улучшить время сборки.

### Предпочитайте Модули Kotlin И Java

Существует три основных типа модулей, которые поддерживает Android Studio:

- **Модули приложений (App modules)** — точка входа в приложение. Содержат исходный код, ресурсы, ассеты и `AndroidManifest.xml`. Результат сборки — Android App `Bundle` (AAB) или Android `Application` Package (APK).
- **Модули библиотек (Library modules)** — по структуре похожи на app-модули и используются другими Android-модулями как зависимости. Результат — Android Archive (AAR), который затем может подключаться к другим модулям. Library-модули позволяют инкапсулировать и переиспользовать логику и ресурсы.
- **Модули Kotlin и Java (plain JVM libraries)** — не содержат Android-ресурсов, ассетов или манифеста.

Поскольку Android-модули (app/library) создают дополнительные накладные расходы на сборку и конфигурацию, предпочтительно везде, где не требуются Android-специфичные возможности, использовать обычные Kotlin/Java-модули.

---

## Answer (EN)

### High Cohesion and Low Coupling Principle

One way of characterizing a modular codebase would be to use the **coupling** and **cohesion** properties. Coupling measures the degree to which modules depend on each other. Cohesion, in this context, measures how the elements of a single module are functionally related. As a general rule, you should strive for low coupling and high cohesion:

- **Low coupling** means that modules should be as independent as possible from one another, so that changes to one module have zero or minimal impact on other modules. **Modules shouldn't have knowledge of the inner workings of other modules.**
- **High cohesion** means that modules should comprise a collection of code that acts as a system. They should have clearly defined responsibilities and stay within boundaries of certain domain knowledge. Consider a sample ebook application. It might be inappropriate to mix book- and payment-related code together in the same module as they are two different functional domains.

### Module to Module Communication

Modules rarely exist in total separation and often rely on other modules and communicate with them. It's important to keep the coupling low even when modules work together and exchange information frequently. Sometimes direct communication between two modules is either not desirable, as in the case of architecture constraints. It may also be impossible, such as with cyclic dependencies.

To overcome this problem you can have a third module mediating between two other modules. The mediator module can listen for messages from both of the modules and forward them as needed. The mediator is often the module that owns the navigation graph (usually an app module).

Although navigation libraries technically allow passing `Parcelable`/`Serializable` objects as navigation arguments, in a modularized architecture you should prefer passing simple IDs that features can use to access and load desired resources from the data layer. This way, you keep the coupling low, avoid leaking implementation details, and don't violate the single source of truth principle.

In this pattern, both feature modules depend on the same data module. This makes it possible to minimize the amount of data that the mediator module needs to forward and keeps the coupling between the modules low. Instead of passing objects, modules should exchange primitive IDs and load the resources from a shared data module.

### Dependency Inversion

Dependency inversion is when you organize your code such that the abstraction is separate from a concrete implementation.

- **Abstraction**: A contract that defines how components or modules in your application interact with each other. Abstraction modules define the API of your system and contain interfaces and models.
- **Concrete implementation**: Modules that depend on the abstraction module and implement the behavior of an abstraction.

Modules that rely on the behavior defined in the abstraction module should only depend on the abstraction itself, rather than the specific implementations.

The feature module is connected with the implementation module via Dependency Injection. The feature module doesn't directly create the required database instance. Instead, it specifies what dependencies it needs. These dependencies are then supplied externally, usually in the app module or the DI layer.

It is beneficial to separate your APIs from their implementations in the following cases:

- **Diverse capabilities**: If you can implement parts of your system in multiple ways, a clear API allows interchangeability of different implementations. For example, you may have a rendering system that uses OpenGL or Vulkan, or a billing system that works with Play or your in-house billing API.
- **Multiple applications**: If you're developing multiple applications with shared capabilities for different platforms, you can define common APIs and develop specific implementations per platform.
- **Independent teams**: The separation allows different developers or teams to work on different parts of the codebase simultaneously. Developers should focus on understanding the API contracts and using them correctly. They don't need to worry about the implementation details of other modules.
- **Large codebase**: When the codebase is large or complex, separating the API from the implementation makes the code more manageable. It lets you break the codebase down into more granular, understandable, and maintainable units.

### Keep Your Configuration Consistent

Every module introduces configuration overhead. If the number of your modules reaches a certain threshold, managing consistent configuration becomes a challenge. For example, it's important that modules use dependencies of the same version. If you need to update a large number of modules just to bump a dependency version, it is not only an effort but also a room for potential mistakes. To solve this problem, you can use one of Gradle's tools to centralize your configuration:

- [Version catalogs](https://docs.gradle.org/current/userguide/platforms.html) are a type-safe list of dependencies generated by Gradle during sync. It's a central place to declare all your dependencies and is available to all the modules in a project.
- Use [convention plugins](https://docs.gradle.org/current/samples/sample_convention_plugins.html) to share build logic between modules.

### Expose as Little as Possible

The public interface of a module should be minimal and expose only the essentials. It shouldn't leak any implementation details outside. Scope everything to the smallest extent possible. Use Kotlin's `private` or `internal` visibility scope to make the declarations module-private. When declaring dependencies in your module, prefer `implementation` over `api`. The latter exposes transitive dependencies to the consumers of your module. Using `implementation` may improve build time since it reduces the number of modules that need to be rebuilt.

### Prefer Kotlin & Java Modules

There are three essential types of modules that Android Studio supports:

- **App modules** are an entry point to your application. They can contain source code, resources, assets and an `AndroidManifest.xml`. The output of an app module is an Android App `Bundle` (AAB) or an Android `Application` Package (APK).
- **Library modules** have the same content as the app modules. They are used by other Android modules as a dependency. The output of a library module is an Android Archive (AAR); they are structurally similar to app modules but are compiled to an AAR file which can later be used by other modules as a dependency. A library module makes it possible to encapsulate and reuse the same logic and resources across many app modules.
- **Kotlin and Java** modules (plain JVM libraries) don't contain any Android resources, assets, or manifest files.

Since Android (app/library) modules come with additional build and configuration overhead, you should use plain Kotlin or Java modules where Android-specific capabilities are not required.

---

## Follow-ups

- [[q-does-state-made-in-compose-help-avoid-race-condition--android--medium]]
- [[q-what-should-you-pay-attention-to-in-order-to-optimize-a-large-list--android--hard]]
- How would you structure your modules to support on-demand features or dynamic feature delivery?
- What strategies would you use to minimize build times in a heavily modularized project?
- How would you handle cross-cutting concerns (analytics, logging, auth) in a modular architecture without increasing coupling?

## References

- [Common modularization patterns](https://developer.android.com/topic/modularization/patterns)

## Related Questions

### Prerequisites / Concepts

- [[c-clean-architecture]]

### Related (Hard)

- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-multi-module-best-practices--android--hard]] - Architecture
- [[q-clean-architecture-android--android--hard]] - Architecture
- [[q-design-instagram-stories--android--hard]] - Media

### Prerequisites (Easier)

- [[q-android-security-practices-checklist--android--medium]] - Security
- [[q-build-optimization-gradle--android--medium]] - Gradle
- [[q-usecase-pattern-android--android--medium]] - Architecture

## Ссылки (RU)

- [Паттерны модуляризации (Common modularization patterns)](https://developer.android.com/topic/modularization/patterns)

## Дополнительные Вопросы (RU)

- Как бы вы спроектировали модули для поддержки on-demand фич или динамической доставки модулей?
- Какие стратегии вы бы использовали для минимизации времени сборки в сильно модульном проекте?
- Как вы бы обрабатывали сквозные задачи (аналитика, логирование, аутентификация) в модульной архитектуре без увеличения зацепления?

## Связанные Вопросы (RU)

### Предварительные Знания / Концепции

- [[c-clean-architecture]]

### Связанные (Сложные)

- [[q-data-sync-unstable-network--android--hard]] - Сетевое взаимодействие
- [[q-multi-module-best-practices--android--hard]] - Архитектура
- [[q-clean-architecture-android--android--hard]] - Архитектура
- [[q-design-instagram-stories--android--hard]] - Медиа

### Предварительные (Проще)

- [[q-android-security-practices-checklist--android--medium]] - Безопасность
- [[q-build-optimization-gradle--android--medium]] - Gradle
- [[q-usecase-pattern-android--android--medium]] - Архитектура
