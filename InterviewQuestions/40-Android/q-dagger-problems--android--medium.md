---
tags:
  - android
  - android/di-hilt
  - dagger
  - dependency-injection
  - di-hilt
  - platform/android
difficulty: medium
---

# Какие проблемы есть у Dagger?

**English**: What problems does Dagger have?

## Answer

Dagger has configuration and learning complexity, long compilation times due to code generation at compile time, debugging difficulty with non-obvious compilation error messages, problems with inheritance and code reuse due to complex component and module configurations, code redundancy from creating modules, components and annotations, and testing difficulties due to the complexity of setting up test components and modules. In real projects, the number of modules and components can grow significantly, increasing code complexity. Dagger is a powerful DI tool but it's complex to learn, increases compilation time, can cause debugging difficulties, and requires significant additional code.

## Ответ

Dagger имеет сложность конфигурации и обучения, длинные времена компиляции из-за генерации кода на этапе компиляции, сложность отладки и обработки ошибок из-за неочевидных сообщений об ошибках компиляции, проблемы с наследованием и повторным использованием кода из-за сложных конфигураций компонентов и модулей, избыточность кода из-за необходимости создания модулей компонентов и аннотаций, а также сложности с тестированием из-за трудоемкости настройки тестовых компонентов и модулей. Пример использования Dagger показывает, что в реальных проектах количество модулей и компонентов может значительно возрасти увеличивая сложность кода. Dagger - мощный инструмент для внедрения зависимостей но он сложен в освоении увеличивает время компиляции может вызывать трудности с отладкой и требует значительного количества дополнительного кода.

