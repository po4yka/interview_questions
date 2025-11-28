---
id: "20251110-165110"
title: "Test Doubles / Test Doubles"
aliases: ["Test Doubles"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-unit-testing, c-mockk, c-junit, c-testing-strategies, c-testing-pyramid]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Test doubles are controlled, lightweight replacements for real dependencies used in tests to isolate the unit under test and make its behavior predictable. They help you test specific code paths without involving slow, flaky, or hard-to-set-up external systems such as databases, networks, message queues, or third-party APIs. Common forms include dummies, stubs, fakes, spies, and mocks, each serving a distinct purpose in structuring clear, reliable, and intention-revealing tests.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Test doubles (тестовые двойники) — это управляемые заменители реальных зависимостей, используемые в тестах для изоляции тестируемого кода и обеспечения предсказуемого поведения. Они позволяют проверять конкретную логику без участия медленных, нестабильных или сложных внешних систем, таких как базы данных, сеть, очереди сообщений или сторонние API. Распространённые виды: dummy, stub, fake, spy и mock, каждый решает свою задачу и помогает писать понятные и надёжные тесты.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Different roles:
  - Dummy: passed but never used; satisfies a parameter requirement.
  - Stub: returns predefined data to drive specific test cases.
  - Fake: simplified working implementation (e.g., in-memory repo) suitable for tests.
  - Spy: records calls/arguments for later verification.
  - Mock: pre-programmed expectations about interactions, often framework-driven.
- Isolation and determinism: Test doubles decouple the unit under test from external systems, reducing flakiness and making tests fast and deterministic.
- Design feedback: Heavy use of doubles can expose design issues (e.g., too many responsibilities, tight coupling), guiding better abstractions and boundaries.
- Interaction vs state testing: Mocks/spies are used for verifying interactions (who called what), while stubs/fakes focus on resulting state/outputs.
- Trade-offs: Overuse or misuse of mocks can lead to brittle tests tied to implementation details; prefer using doubles where there is a genuine external dependency or side effect.

## Ключевые Моменты (RU)

- Разные виды:
  - Dummy: передаётся как аргумент, но не используется; просто заполняет параметр.
  - Stub: возвращает заранее заданные значения для нужных сценариев.
  - Fake: упрощённая рабочая реализация (например, in-memory репозиторий) для тестов.
  - Spy: фиксирует вызовы и аргументы для последующей проверки.
  - Mock: содержит заранее описанные ожидания по взаимодействиям, часто с помощью фреймворков.
- Изоляция и детерминизм: Тестовые двойники отделяют тестируемый код от внешних систем, уменьшая нестабильность и делая тесты быстрыми и предсказуемыми.
- Обратная связь по дизайну: Массовое использование двойников часто выявляет проблемы дизайна (слишком много зависимостей, плотное связывание) и помогает улучшить архитектуру.
- Тестирование взаимодействий и состояния: Mocks/spy подходят для проверки того, какие вызовы были сделаны, тогда как stubs/fakes фокусируются на результирующем состоянии и выходных данных.
- Компромиссы: Чрезмерное или некорректное использование моков делает тесты хрупкими и завязанными на реализацию; двойники стоит применять в местах реальных внешних зависимостей и побочных эффектов.

## References

- xUnit Test Patterns (Gerard Meszaros) — canonical source describing test double types.
- Documentation of mocking frameworks (e.g., Mockito, JUnit + Mockito, pytest-mock) for practical usage patterns.
