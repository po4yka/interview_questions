---
id: "20251110-195645"
title: "Mockk / Mockk"
aliases: ["Mockk"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-unit-testing, c-test-doubles, c-junit, c-kotlin-coroutines, c-testing-strategies]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

MockK is a Kotlin-native mocking library for unit and integration testing that enables creating mocks, stubs, and spies in a type-safe and idiomatic Kotlin style. It supports mocking classes, functions (including suspend and extension functions), coroutines, and object/singleton behaviors without requiring open classes or additional bytecode manipulation setup. MockK is widely used in Kotlin/JVM projects (including Android) to isolate code under test and express expectations in a readable DSL.

*This concept file was auto-generated and enriched for interview preparation.*

# Краткое Описание (RU)

MockK — это нативная для Kotlin библиотека для мокинга, используемая в модульном и интеграционном тестировании для создания моков, стабов и шпионов с типобезопасным и идиоматичным Kotlin-синтаксисом. Она поддерживает мокинг классов, функций (включая suspend и extension-функции), корутин и объектов/одиночек без необходимости делать классы open или настраивать сложную байткод-инструментацию. MockK широко используется в Kotlin/JVM и Android-проектах для изоляции тестируемого кода и декларативного описания ожиданий.

*Этот файл концепции был создан автоматически и дополнен для подготовки к собеседованиям.*

## Key Points (EN)

- Kotlin-first design: Provides an idiomatic DSL aligned with Kotlin syntax (e.g., `every { ... } returns ...`, `verify { ... }`).
- Powerful mocking capabilities: Supports mocking final classes, objects, singletons, top-level and extension functions, and suspend functions out of the box.
- Coroutine support: Integrates cleanly with coroutines and structured concurrency, allowing verification of suspend calls and asynchronous logic.
- Clear behavior specification: Separates stubbing (`every {}` / `coEvery {}`) from verification (`verify {}` / `coVerify {}`) for readable, maintainable tests.
- Android and JVM friendly: Commonly used in Android tests instead of or alongside Mockito when working with pure Kotlin codebases.

## Ключевые Моменты (RU)

- Ориентация на Kotlin: Предоставляет идиоматичный DSL в стиле Kotlin (например, `every { ... } returns ...`, `verify { ... }`).
- Расширенные возможности мокинга: Поддерживает мокинг final-классов, объектов и синглтонов, top-level и extension-функций, а также suspend-функций «из коробки».
- Поддержка корутин: Корректно работает с корутинами и асинхронным кодом, позволяя задавать ожидания и верифицировать вызовы suspend-функций.
- Ясное разделение поведения: Явно разделяет настройку поведения (`every {}` / `coEvery {}`) и проверку вызовов (`verify {}` / `coVerify {}`), повышая читаемость и поддержку тестов.
- Подходит для Android и JVM: Часто используется в Android и Kotlin-проектах как основная библиотека для мокинга вместо или вместе с Mockito.

## References

- Official MockK documentation: https://mockk.io
- GitHub repository (MockK): https://github.com/mockk/mockk

