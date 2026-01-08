---
id: "20251110-133040"
title: "Strictmode / Strictmode"
aliases: ["Strictmode"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: ["c-anr", "c-main-thread", "c-threading", "c-debugging", "c-android-profiler"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---

# Summary (EN)

StrictMode is a runtime tool (available in platforms like Android/JavaScript/TypeScript) that makes "strict" behavior opt-in: it detects bad practices, disallows unsafe or ambiguous constructs, and fails fast instead of silently tolerating errors. It is used to surface performance, threading, and correctness issues early in development, making bugs easier to catch and code more predictable. In interviews, StrictMode often appears when discussing code quality, runtime checks, and how to enforce safer language or framework semantics.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

StrictMode — это инструмент времени выполнения (используется, например, в Android и JavaScript/TypeScript), который включает «строгий» режим: выявляет плохие практики, запрещает небезопасные или неоднозначные конструкции и приводит к раннему падению вместо скрытых ошибок. Он помогает обнаруживать проблемы производительности, потокобезопасности и корректности на этапе разработки, делая поведение кода более предсказуемым. На собеседованиях StrictMode часто обсуждают в контексте контроля качества кода, дополнительных проверок и усиленных гарантий языка/фреймворка.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Detects problematic operations: In Android, StrictMode flags disk and network access on the main thread; in React/JS it highlights unsafe lifecycle patterns and side effects.
- Enforces stricter semantics: JavaScript/TypeScript strict mode changes `this` binding, disallows silent errors (e.g., assigning to undeclared variables), and reserves certain identifiers.
- Development-time safety: Typically enabled only in debug/development builds to catch issues without impacting production behavior or performance.
- Fail-fast philosophy: Surfaces issues early via warnings, logs, or crashes, encouraging developers to fix root causes instead of relying on undefined or permissive behavior.
- Interview angle: Demonstrates understanding of how languages/frameworks provide tools to enforce best practices and avoid subtle bugs.

## Ключевые Моменты (RU)

- Обнаружение проблемных операций: В Android StrictMode выявляет обращения к диску и сети в главном потоке; в React/JS помогает подсветить небезопасные жизненные циклы и побочные эффекты.
- Более строгая семантика: В JavaScript/TypeScript строгий режим меняет привязку `this`, запрещает «тихие» ошибки (например, присваивание необъявленным переменным) и резервирует некоторые идентификаторы.
- Безопасность на этапе разработки: Обычно включается только в debug/разработческой конфигурации, чтобы находить проблемы без влияния на продакшн-поведение и производительность.
- Принцип fail-fast: Раннее выявление ошибок через предупреждения, логи или падения, стимулируя исправление первопричин вместо опоры на нестрогое или неопределённое поведение.
- Аспект для собеседований: Показывает понимание инструментов языка/фреймворка для обеспечения лучших практик и предотвращения скрытых багов.

## References

- Android StrictMode: https://developer.android.com/reference/android/os/StrictMode
- JavaScript strict mode (MDN): https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode
