---
id: "20251110-202339"
title: "Anr / Anr"
aliases: ["Anr"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-android-background-execution, c-main-thread, c-multithreading, c-strictmode, c-performance-optimization]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
---

# Summary (EN)

ANR (Application Not Responding) is an Android runtime condition where an app's UI thread is blocked for too long, causing the system to show a dialog allowing the user to force close the app. It typically occurs when long-running operations (I/O, network, heavy computation) are executed on the main thread or when the app stops processing input/events. Understanding ANRs is critical for building responsive Android applications and is a common topic in mobile development interviews.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

ANR (Application Not Responding) — это состояние во время выполнения Android-приложения, при котором главный (UI) поток надолго блокируется, и система показывает пользователю диалог с предложением принудительно закрыть приложение. Обычно возникает, когда длительные операции (I/O, сеть, тяжелые вычисления) выполняются в главном потоке или когда приложение перестает обрабатывать ввод/события. Понимание ANR критично для создания отзывчивых Android-приложений и часто спрашивается на собеседованиях по мобильной разработке.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- ANR is triggered when the main thread is unresponsive: e.g., no input event processing or broadcast handling within system-defined timeouts (commonly ~5s for UI, ~10s+ for broadcasts/services).
- Root causes include heavy work on the UI thread, synchronous disk/network operations, infinite loops or deadlocks, and blocking the main thread on long locks.
- Prevention strategies: move expensive operations to background threads (Kotlin coroutines, Executors, WorkManager), keep UI thread work short and focused on rendering, and avoid blocking calls on the main thread.
- Debugging ANRs typically involves analyzing stack traces from `traces.txt`, logcat output, and inspecting where the main thread is blocked.
- Proper lifecycle and responsiveness handling (e.g., cancelling work on pause/stop, debouncing input) reduces ANR risk and improves user experience.

## Ключевые Моменты (RU)

- ANR возникает, когда главный поток становится «неотзывчивым»: например, не обрабатывает события ввода или выполнения бродкаста в пределах системных таймаутов (обычно ~5 с для UI, ~10+ с для broadcast/service).
- Основные причины: тяжелые операции в UI-потоке, синхронные операции ввода-вывода/сети, бесконечные циклы или дедлоки, блокировка главного потока на долгих логах/мониторах.
- Профилактика: выносить затратные операции в фоновые потоки (Kotlin coroutines, Executors, WorkManager), оставлять в главном потоке только логику UI и быстрые операции, избегать блокирующих вызовов в UI-потоке.
- Для диагностики ANR анализируют stack trace в `traces.txt`, логи logcat и смотрят, где именно заблокирован главный поток.
- Корректная работа с жизненным циклом и отзывчивостью интерфейса (отмена фоновых задач, аккуратная обработка ввода) снижает риск ANR и улучшает пользовательский опыт.

## References

- Android Developers: "App responsiveness" and "ANR" documentation at developer.android.com
