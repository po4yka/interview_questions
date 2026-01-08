---id: lang-025
title: "Sealed Classes Limitations / Ограничения Sealed Классов"
aliases: [Sealed Classes Limitations, Ограничения Sealed Классов]
topic: kotlin
subtopics: [class-hierarchy, oop, sealed-classes]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-sealed-classes, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml]
created: 2025-10-15
updated: 2025-11-09
tags: [class-hierarchy, difficulty/medium, kotlin, programming-languages, sealed-classes]
---
# Вопрос (RU)
> Какие есть ограничения у sealed классов?

---

# Question (EN)
> What are the limitations of sealed classes?

## Ответ (RU)

Основные ограничения sealed классов (и интерфейсов) в Kotlin:

- Ограниченный контроль наследования: непосредственными наследниками sealed класса/интерфейса могут быть только типы, объявленные в явно разрешённых местах.
  - Для классического `sealed class` / `sealed interface`: в том же модуле и в том же пакете (или в том же файле для старого формата, если вся иерархия объявлена вместе).
  - Нельзя вынести новый наследник в другой модуль или в пакет вне этой области.
- Нельзя свободно расширять иерархию извне: вы не можете сделать произвольный наследник sealed-типа в другом ("чужом") модуле/пакете/файле, поэтому иерархия жёстко фиксирована и контролируется.
- Sealed класс задаёт закрытую, но расширяемую только в ограниченной области иерархию: он по смыслу не сочетается с идеей "полностью final" (запретить всех наследников), так как использование `sealed` уже описывает контролируемый набор подтипов. Одновременно объявить один и тот же класс и `sealed`, и `final` нельзя.
- Подтипы должны удовлетворять правилам видимости и места объявления для sealed типов; это делает архитектуру более жёсткой и иногда усложняет рефакторинг или разделение по модулям.

Важно:
- Sealed классы не обязаны быть помечены `abstract`, но они нефинализируемы для создания экземпляров: нельзя создать экземпляр непосредственно sealed класса без конкретного подтипа.
- В Kotlin также существуют sealed интерфейсы; утверждение, что sealed можно использовать только для классов и объектов и не для интерфейсов, неверно.
- Sealed типы не запрещают наследование от других классов или реализацию интерфейсов; ограничение относится к тому, кто может наследовать sealed тип.

(Не путать с преимуществами: исчерпывающие `when`, контроль иерархии, удобное сопоставление с образцом — это плюсы, а не ограничения.)

## Answer (EN)

Key limitations of sealed classes (and interfaces) in Kotlin:

- Restricted inheritance scope: direct subtypes of a sealed class/interface can only be declared in explicitly allowed locations.
  - For the classic `sealed class` / `sealed interface`: in the same module and the same package (or in the same file for the older style where the whole hierarchy lives together).
  - You cannot place a new subtype in another module or in a package outside this scope.
- You cannot arbitrarily extend a sealed type from another ("foreign") module/package/file, so the hierarchy is tightly controlled and closed to uncontrolled extension.
- A sealed class defines a closed hierarchy that is only extendable within a restricted scope; conceptually this conflicts with the idea of making it completely `final` (disallowing all inheritance). You cannot mark the same class as both `sealed` and `final`.
- Subtypes must follow visibility and placement rules for sealed types; this can make the architecture more rigid and sometimes complicates refactoring or splitting across modules.

Important clarifications:
- Sealed classes do not have to be declared with `abstract`, but they are not directly instantiable: you cannot create an instance of a sealed class itself, only of its concrete subclasses.
- Kotlin also has sealed interfaces; the claim that `sealed` applies only to classes/objects and not interfaces is incorrect.
- Sealed types are not forbidden from inheriting from other classes or implementing interfaces; the restriction is on who may inherit from a sealed type, not what a sealed type may inherit from.

(Do not confuse these with advantages: exhaustive `when` expressions, controlled hierarchies, and pattern-matching-like usage are benefits, not limitations.)

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java?
- Когда вы бы использовали sealed классы на практике?
- Какие распространенные ошибки следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-sealed-classes]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-sealed-classes]]

## Связанные Вопросы (RU)

- [[q-what-is-flow--kotlin--medium]]

## Related Questions

- [[q-what-is-flow--kotlin--medium]]
