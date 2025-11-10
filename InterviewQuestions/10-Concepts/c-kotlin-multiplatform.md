---
id: "20251110-041750"
title: "Kotlin Multiplatform / Kotlin Multiplatform"
aliases: ["Kotlin Multiplatform"]
summary: "Foundational concept for interview preparation"
topic: "kotlin"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: []
created: "2025-11-10"
updated: "2025-11-10"
tags: ["kotlin", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Kotlin Multiplatform (KMP) is a Kotlin ecosystem feature that enables sharing code (including business logic, data models, and networking) across multiple platforms such as Android, iOS, JVM, JS, and native targets while allowing platform-specific implementations where needed. It helps reduce duplication, keep behavior consistent, and speed up development of multi-platform products without forcing a single UI technology. Commonly used in mobile (Android/iOS) apps, backend + client code sharing, and libraries targeting several runtimes.

*This concept file was auto-generated. Please expand with additional details and examples as needed.*

# Краткое Описание (RU)

Kotlin Multiplatform (KMP) — это возможность экосистемы Kotlin, позволяющая совместно использовать код (бизнес-логику, модели данных, сетевой слой и др.) между несколькими платформами: Android, iOS, JVM, JS и нативными таргетами, сохраняя при этом возможность платформенно-специфичных реализаций. Подход уменьшает дублирование, повышает согласованность поведения и ускоряет разработку мультиплатформенных продуктов без навязывания единой UI-технологии. Чаще всего используется для совместного кода между Android/iOS, клиентом и backend-частью, а также для мультиплатформенных библиотек.

*Этот файл концепции был создан автоматически. При необходимости дополняйте его дополнительными деталями и примерами.*

## Key Points (EN)

- Shared code via `kotlin-multiplatform` projects: place common logic in `commonMain` (expect/actual or fully common code), then provide platform-specific code in `androidMain`, `iosMain`, etc.
- Expect/Actual mechanism: `expect` declarations define a common API contract; `actual` implementations provide platform-specific behavior while keeping call sites platform-agnostic.
- Flexible UI strategy: KMP focuses on sharing logic, not forcing a shared UI; teams can use native UI (SwiftUI/UIKit, Jetpack Compose, etc.) or shared UI approaches where appropriate.
- Gradual adoption: can be introduced into existing projects incrementally (e.g., start by sharing networking, serialization, domain layer) without a full rewrite.
- Tooling and ecosystem: supported by Kotlin Multiplatform plugins in Gradle/IntelliJ/Android Studio, with libraries like Ktor, Kotlinx Serialization, and SQLDelight offering multiplatform support.

## Ключевые Моменты (RU)

- Общий код через проекты `kotlin-multiplatform`: основная логика размещается в `commonMain` (общий или expect-код), а платформенно-специфичный код — в `androidMain`, `iosMain` и других source sets.
- Механизм expect/actual: `expect`-декларации задают общий контракт API, а `actual`-реализации обеспечивают платформенно-зависимое поведение при единообразном использовании в общем коде.
- Гибкая стратегия для UI: KMP ориентирован на совместное использование логики, а не UI; можно использовать нативные UI-стэки (SwiftUI/UIKit, Jetpack Compose и др.) или общие решения там, где это оправдано.
- Постепенное внедрение: KMP легко интегрировать в существующие проекты поэтапно (например, сначала разделить сеть, сериализацию, доменный слой), избегая полного переписывания.
- Инструменты и экосистема: поддерживается плагинами Kotlin Multiplatform в Gradle/IntelliJ/Android Studio; библиотеки Ktor, Kotlinx Serialization, SQLDelight и др. имеют мультиплатформенную поддержку.

## References

- Official Kotlin Multiplatform docs: https://kotlinlang.org/docs/multiplatform.html
- Kotlin language overview: https://kotlinlang.org/docs/reference/
