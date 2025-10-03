---
id: 20251003140207
title: What problems does Dagger have / Какие проблемы есть у Dagger?
aliases: []

# Classification
topic: android
subtopics: [di-hilt]
question_kind: android
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/298
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-architecture
  - c-dependency-injection

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [android, dagger, dependency-injection, android/di-hilt, difficulty/medium, easy_kotlin, lang/ru, platform/android]
---

# Question (EN)
> What problems does Dagger have

# Вопрос (RU)
> Какие проблемы есть у Dagger?

---

## Answer (EN)

Dagger has configuration and learning complexity, long compilation times due to code generation at compile time, debugging difficulty with non-obvious compilation error messages, problems with inheritance and code reuse due to complex component and module configurations, code redundancy from creating modules, components and annotations, and testing difficulties due to the complexity of setting up test components and modules. In real projects, the number of modules and components can grow significantly, increasing code complexity. Dagger is a powerful DI tool but it's complex to learn, increases compilation time, can cause debugging difficulties, and requires significant additional code.

## Ответ (RU)

Dagger имеет сложность конфигурации и обучения, длинные времена компиляции из-за генерации кода на этапе компиляции, сложность отладки и обработки ошибок из-за неочевидных сообщений об ошибках компиляции, проблемы с наследованием и повторным использованием кода из-за сложных конфигураций компонентов и модулей, избыточность кода из-за необходимости создания модулей компонентов и аннотаций, а также сложности с тестированием из-за трудоемкости настройки тестовых компонентов и модулей. Пример использования Dagger показывает, что в реальных проектах количество модулей и компонентов может значительно возрасти увеличивая сложность кода. Dagger - мощный инструмент для внедрения зависимостей но он сложен в освоении увеличивает время компиляции может вызывать трудности с отладкой и требует значительного количества дополнительного кода.

---

## Follow-ups
- How does this pattern compare to alternatives?
- What are the performance implications?
- When should you use this approach?

## References
- [[c-android-architecture]]
- [[c-dependency-injection]]
- [[moc-android]]

## Related Questions
- [[q-mvvm-vs-mvp--android--medium]]
- [[q-single-activity-approach--android--medium]]
