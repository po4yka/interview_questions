---
id: android-005
title: "Android Modularization Patterns / Паттерны модуляризации в Android"
aliases: []

# Classification
topic: android
subtopics: [architecture-clean, architecture-modularization]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru, android/architecture, android/modularization, android/best-practices, difficulty/hard]
source: https://github.com/Kirchhoff-Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: [q-does-state-made-in-compose-help-avoid-race-condition--android--medium, q-what-should-you-pay-attention-to-in-order-to-optimize-a-large-list--android--hard, q-ot-kogo-nasleduyutsya-viewgroup--programming-languages--easy]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [android/architecture-clean, android/architecture-modularization, en, ru, difficulty/hard]
date created: Sunday, October 12th 2025, 12:27:49 pm
date modified: Thursday, October 30th 2025, 3:13:52 pm
---

# Question (EN)
> What modularization patterns do you know?
# Вопрос (RU)
> Какие паттерны модуляризации вы знаете?

---

## Answer (EN)

### High cohesion and low coupling principle

One way of characterizing a modular codebase would be to use the **coupling** and **cohesion** properties. Coupling measures the degree to which modules depend on each other. Cohesion, in this context, measures how the elements of a single module are functionally related. As a general rule, you should strive for low coupling and high cohesion:

- **Low coupling** means that modules should be as independent as possible from one another, so that changes to one module have zero or minimal impact on other modules. **Modules shouldn't have knowledge of the inner workings of other modules**
- **High cohesion** means that modules should comprise a collection of code that acts as a system. They should have clearly defined responsibilities and stay within boundaries of certain domain knowledge. Consider a sample ebook application. It might be inappropriate to mix book and payment related code together in the same module as they are two different functional domains.

### Module to module communication

Modules rarely exist in total separation and often rely on other modules and communicate with them. It's important to keep the coupling low even when modules work together and exchange information frequently. Sometimes direct communication between two modules is either not desirable as in the case of architecture constraints. It may also be impossible, such as with cyclic dependencies.

To overcome this problem you can have a third module mediating between two other modules. The mediator module can listen for messages from both of the modules and forward them as needed. The mediator is the module that owns the navigation graph (usually an app module).

You shouldn't pass objects as navigation arguments. Instead, use simple ids that features can use to access and load desired resources from the data layer. This way, you keep the coupling low and don't violate the single source of truth principle.

In the example below, both feature modules depend on the same data module. This makes it possible to minimize the amount of data that the mediator module needs to forward and keeps the coupling between the modules low. Instead of passing objects, modules should exchange primitive IDs and load the resources from a shared data module.

### Dependency inversion

Dependency inversion is when you organize your code such that the abstraction is separate from a concrete implementation.

- **Abstraction**: A contract that defines how components or modules in your application interact with each other. Abstraction modules define the API of your system and contain interfaces and models
- **Concrete implementation**: Modules that depend on the abstraction module and implement the behavior of an abstraction

Modules that rely on the behavior defined in the abstraction module should only depend on the abstraction itself, rather than the specific implementations.

The feature module is connected with the implementation module via Dependency Injection. The feature module doesn't directly create the required database instance. Instead, it specifies what dependencies it needs. These dependencies are then supplied externally, usually in the app module.

It is beneficial to separate your APIs from their implementations in the following cases:

- **Diverse capabilities**: If you can implement parts of your system in multiple ways, a clear API allows interchangeability of different implementations. For example, you may have a rendering system that uses OpenGL or Vulkan, or a billing system that works with Play or your in-house billing API
- **Multiple applications**: If you're developing multiple applications with shared capabilities for different platforms, you can define common APIs and develop specific implementations per platform
- **Independent teams**: The separation allows different developers or teams to work on different parts of the codebase simultaneously. Developers should focus on understanding the API contracts and using them correctly. They don't need to worry about the implementation details of other modules
- **Large codebase**: When the codebase is large or complex, separating the API from the implementation makes the code more manageable. It lets you break the codebase down into more granular, understandable, and maintainable units

### Keep your configuration consistent

Every module introduces configuration overhead. If the number of your modules reaches a certain threshold, managing consistent configuration becomes a challenge. For example, it's important that modules use dependencies of the same version. If you need to update a large number of modules just to bump a dependency version, it is not only an effort but also a room for potential mistakes. To solve this problem, you can use one of the gradle's tools to centralize your configuration:

- [Version catalogs](https://docs.gradle.org/current/userguide/platforms.html) are a type safe list of dependencies generated by Gradle during sync. It's a central place to declare all your dependencies and is available to all the modules in a project
- Use [convention plugins](https://docs.gradle.org/current/samples/sample_convention_plugins.html) to share build logic between modules

### Expose as little as possible

The public interface of a module should be minimal and expose only the essentials. It shouldn't leak any implementation details outside. Scope everything to the smallest extent possible. Use Kotlin's `private` or `internal` visibility scope to make the declarations module-private. When declaring dependencies in your module, prefer `implementation` over `api`. The latter exposes transitive dependencies to the consumers of your module. Using implementation may improve build time since it reduces the number of modules that need to be rebuilt.

### Prefer Kotlin & Java modules

There are three essential types of modules that Android studio supports:

- **App modules** are an entry point to your application. They can contain source code, resources, assets and an `AndroidManifest.xml`. The output of an app module is an Android App Bundle (AAB) or an Android Application Package (APK)
- **Library modules** have the same content as the app modules. They are used by other Android modules as a dependency. The output of a library module is an Android Archive (AAR) are structurally identical to app modules but they are compiled to an Android Archive (AAR) file which can later be used by other modules as a dependency. A library module makes it possible to encapsulate and reuse the same logic and resources across many app modules
- **Kotlin and Java** libraries don't contain any Android resources, assets, or manifest files

Since Android modules come with overhead, preferably, you'd want to use the Kotlin or Java kind as much as possible.

## Ответ (RU)

### Принцип высокой связности и слабого связывания

Одним из способов характеризации модульной кодовой базы является использование свойств **связывания (coupling)** и **связности (cohesion)**. Связывание измеряет степень зависимости модулей друг от друга. Связность в данном контексте измеряет, насколько элементы одного модуля функционально связаны. Как общее правило, вы должны стремиться к слабому связыванию и высокой связности:

- **Слабое связывание** означает, что модули должны быть максимально независимыми друг от друга, чтобы изменения в одном модуле имели нулевое или минимальное влияние на другие модули. **Модули не должны знать о внутреннем устройстве других модулей**
- **Высокая связность** означает, что модули должны представлять собой совокупность кода, который действует как система. Они должны иметь четко определенные обязанности и оставаться в рамках определенной предметной области. Рассмотрим пример приложения для электронных книг. Было бы неуместно смешивать код, связанный с книгами и платежами, в одном модуле, поскольку это две разные функциональные области.

### Взаимодействие между модулями

Модули редко существуют в полной изоляции и часто полагаются на другие модули и взаимодействуют с ними. Важно поддерживать низкое связывание даже тогда, когда модули работают вместе и часто обмениваются информацией. Иногда прямое взаимодействие между двумя модулями либо нежелательно, как в случае архитектурных ограничений. Оно также может быть невозможным, например, при циклических зависимостях.

Чтобы преодолеть эту проблему, вы можете использовать третий модуль, посредничающий между двумя другими модулями. Модуль-посредник может прослушивать сообщения от обоих модулей и пересылать их по мере необходимости. Посредник - это модуль, которому принадлежит граф навигации (обычно модуль приложения).

Вы не должны передавать объекты в качестве аргументов навигации. Вместо этого используйте простые идентификаторы, которые функции могут использовать для доступа и загрузки желаемых ресурсов из слоя данных. Таким образом, вы сохраняете низкое связывание и не нарушаете принцип единственного источника истины.

В приведенном ниже примере оба модуля функций зависят от одного и того же модуля данных. Это позволяет минимизировать объем данных, которые модулю-посреднику необходимо пересылать, и сохранять низкое связывание между модулями. Вместо передачи объектов модули должны обмениваться примитивными идентификаторами и загружать ресурсы из общего модуля данных.

### Инверсия зависимостей

Инверсия зависимостей - это когда вы организуете свой код таким образом, чтобы абстракция была отделена от конкретной реализации.

- **Абстракция**: Контракт, который определяет, как компоненты или модули в вашем приложении взаимодействуют друг с другом. Модули абстракции определяют API вашей системы и содержат интерфейсы и модели
- **Конкретная реализация**: Модули, которые зависят от модуля абстракции и реализуют поведение абстракции

Модули, которые полагаются на поведение, определенное в модуле абстракции, должны зависеть только от самой абстракции, а не от конкретных реализаций.

Модуль функции связан с модулем реализации через внедрение зависимостей. Модуль функции не создает напрямую требуемый экземпляр базы данных. Вместо этого он указывает, какие зависимости ему нужны. Эти зависимости затем предоставляются извне, обычно в модуле приложения.

Отделение API от их реализаций полезно в следующих случаях:

- **Разнообразные возможности**: Если вы можете реализовать части вашей системы несколькими способами, четкий API позволяет взаимозаменяемость различных реализаций. Например, у вас может быть система рендеринга, использующая OpenGL или Vulkan, или система биллинга, работающая с Play или вашим собственным API биллинга
- **Множественные приложения**: Если вы разрабатываете несколько приложений с общими возможностями для разных платформ, вы можете определить общие API и разработать конкретные реализации для каждой платформы
- **Независимые команды**: Разделение позволяет разным разработчикам или командам работать над разными частями кодовой базы одновременно. Разработчики должны сосредоточиться на понимании контрактов API и правильном их использовании. Им не нужно беспокоиться о деталях реализации других модулей
- **Большая кодовая база**: Когда кодовая база большая или сложная, отделение API от реализации делает код более управляемым. Это позволяет разбить кодовую базу на более детальные, понятные и поддерживаемые единицы

### Поддерживайте согласованность конфигурации

Каждый модуль вносит накладные расходы на конфигурацию. Если количество ваших модулей достигает определенного порога, управление согласованной конфигурацией становится проблемой. Например, важно, чтобы модули использовали зависимости одной и той же версии. Если вам нужно обновить большое количество модулей только для того, чтобы повысить версию зависимости, это не только трудоемко, но и чревато потенциальными ошибками. Для решения этой проблемы вы можете использовать один из инструментов gradle для централизации вашей конфигурации:

- [Каталоги версий (Version catalogs)](https://docs.gradle.org/current/userguide/platforms.html) - это типобезопасный список зависимостей, генерируемый Gradle во время синхронизации. Это центральное место для объявления всех ваших зависимостей, доступное всем модулям в проекте
- Используйте [плагины соглашений (convention plugins)](https://docs.gradle.org/current/samples/sample_convention_plugins.html) для совместного использования логики сборки между модулями

### Раскрывайте как можно меньше

Публичный интерфейс модуля должен быть минимальным и раскрывать только самое необходимое. Он не должен раскрывать никакие детали реализации наружу. Ограничивайте область видимости всего до минимально возможной. Используйте область видимости Kotlin `private` или `internal`, чтобы сделать объявления приватными для модуля. При объявлении зависимостей в вашем модуле предпочитайте `implementation` вместо `api`. Последнее раскрывает транзитивные зависимости потребителям вашего модуля. Использование implementation может улучшить время сборки, поскольку уменьшает количество модулей, которые необходимо перестроить.

### Предпочитайте модули Kotlin и Java

Существует три основных типа модулей, которые поддерживает Android Studio:

- **Модули приложений** являются точкой входа в ваше приложение. Они могут содержать исходный код, ресурсы, ассеты и `AndroidManifest.xml`. Результатом модуля приложения является Android App Bundle (AAB) или Android Application Package (APK)
- **Модули библиотек** имеют то же содержимое, что и модули приложений. Они используются другими модулями Android в качестве зависимости. Результатом модуля библиотеки является Android Archive (AAR), структурно идентичный модулям приложений, но компилируемый в файл Android Archive (AAR), который позже может быть использован другими модулями в качестве зависимости. Модуль библиотеки позволяет инкапсулировать и повторно использовать одну и ту же логику и ресурсы во многих модулях приложений
- **Библиотеки Kotlin и Java** не содержат никаких ресурсов Android, ассетов или файлов манифеста

Поскольку модули Android имеют накладные расходы, предпочтительно использовать модули Kotlin или Java как можно больше.

---

## References
- [Common modularization patterns](https://developer.android.com/topic/modularization/patterns)

## Related Questions

### Related (Hard)
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-multi-module-best-practices--android--hard]] - Architecture
- [[q-clean-architecture-android--android--hard]] - Architecture
- [[q-design-instagram-stories--android--hard]] - Media

### Prerequisites (Easier)
- [[q-android-security-practices-checklist--android--medium]] - Security
- [[q-build-optimization-gradle--android--medium]] - Gradle
- [[q-usecase-pattern-android--android--medium]] - Architecture
