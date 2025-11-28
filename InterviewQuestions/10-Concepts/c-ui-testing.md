---
id: "20251110-194613"
title: "Ui Testing / Ui Testing"
aliases: ["Ui Testing"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-espresso-testing, c-unit-testing, c-testing-pyramid, c-test-sharding, c-android-testing]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

UI Testing (User Interface Testing) is a type of automated or manual testing that verifies how an application’s visual interface behaves from the end user’s perspective. It checks that screens, widgets, layouts, navigation flows, and input handling work correctly and consistently across devices, states, and edge cases. UI tests help catch regressions in user-facing behavior that unit or integration tests may miss and are critical for ensuring usability and reliability before release.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

UI-тестирование (User Interface Testing) — это вид автоматизированного или ручного тестирования, который проверяет поведение графического интерфейса приложения с точки зрения пользователя. Оно подтверждает корректность экранов, элементов управления, верстки, навигации и обработки ввода на разных устройствах, в разных состояниях и граничных сценариях. UI-тесты позволяют выявить регрессии и проблемы в пользовательском интерфейсе, которые не покрываются модульными или интеграционными тестами, и критичны для качества продукта перед релизом.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Covers user-visible behavior: validates layout, text, colors, controls, navigation, error messages, and responsiveness as seen by the user.
- Scenario-based: tests real usage flows (login, search, checkout, form submission) instead of isolated functions or classes.
- End-to-end interactions: often runs against a full build (web, mobile, desktop), interacting with the app via clicks, taps, typing, and gestures.
- Higher cost than unit tests: slower, more brittle, and sensitive to UI changes, so they are usually fewer and focused on critical paths.
- Common tools: Selenium/WebDriver for web, Cypress/Playwright for modern web, Espresso/UI Automator for Android, XCUITest for iOS.

## Ключевые Моменты (RU)

- Ориентация на видимое поведение: проверяет верстку, тексты, цвета, элементы управления, навигацию, сообщения об ошибках и адаптивность с точки зрения пользователя.
- Сценарный подход: тестирует реальные пользовательские сценарии (логин, поиск, оформление заказа, отправка форм), а не отдельные функции или классы.
- Сквозные проверки: чаще всего выполняется на полном приложении (web, mobile, desktop), взаимодействуя с ним кликами, тапами, вводом текста и жестами.
- Более высокая стоимость, чем модульные тесты: медленнее, менее стабильны и чувствительны к изменениям интерфейса, поэтому фокусируются на ключевых пользовательских потоках.
- Типичные инструменты: Selenium/WebDriver для веба, Cypress/Playwright для современного веба, Espresso/UI Automator для Android, XCUITest для iOS.

## References

- Selenium WebDriver documentation: https://www.selenium.dev/documentation/
- Cypress documentation: https://docs.cypress.io/
- Playwright documentation: https://playwright.dev/docs/intro
- Android Espresso documentation: https://developer.android.com/training/testing/espresso
- XCUITest documentation: https://developer.apple.com/documentation/xctest/user_interface_tests
