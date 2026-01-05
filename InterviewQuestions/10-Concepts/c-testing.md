---
id: concept-testing
title: Android Testing / Тестирование Android
aliases: [Android Testing, Mobile Testing, Тестирование Android]
kind: concept
summary: Comprehensive testing strategies for Android applications including unit, integration, and UI tests
links: []
created: 2025-11-06
updated: 2025-11-06
tags: [android, concept, quality, testing]
---

# Summary (EN)

Android testing encompasses multiple testing levels to ensure app quality, reliability, and correctness:

1. **Unit Tests** - Test individual components in isolation (JUnit, Mockito)
2. **Integration Tests** - Test interaction between components
3. **UI Tests** - Test user interface and user flows (Espresso, Compose Testing)
4. **Instrumented Tests** - Tests running on device/emulator with Android framework

**Testing Pyramid**:
- Many unit tests (fast, cheap)
- Moderate integration tests
- Few UI tests (slow, expensive)

Key testing frameworks:
- JUnit 4/5 for unit tests
- Mockito/MockK for mocking
- Espresso for View-based UI testing
- Compose Test for Compose UI testing
- Robolectric for local Android tests

# Сводка (RU)

Тестирование Android охватывает несколько уровней для обеспечения качества, надёжности и корректности приложения:

1. **Модульные тесты** - Тестирование отдельных компонентов в изоляции (JUnit, Mockito)
2. **Интеграционные тесты** - Тестирование взаимодействия между компонентами
3. **UI тесты** - Тестирование пользовательского интерфейса и пользовательских сценариев (Espresso, Compose Testing)
4. **Инструментальные тесты** - Тесты, выполняемые на устройстве/эмуляторе с Android framework

**Пирамида тестирования**:
- Много модульных тестов (быстрые, дешёвые)
- Умеренное количество интеграционных тестов
- Мало UI тестов (медленные, дорогие)

Ключевые фреймворки тестирования:
- JUnit 4/5 для модульных тестов
- Mockito/MockK для моков
- Espresso для UI тестирования на View
- Compose Test для UI тестирования Compose
- Robolectric для локальных Android тестов

## Use Cases / Trade-offs

**Unit Testing**:
- ViewModels with LiveData/StateFlow
- Use cases and business logic
- Data transformations
- Utility functions

**Integration Testing**:
- Repository with Room database
- Network + local cache interaction
- Dependency injection graph
- Navigation flows

**UI Testing**:
- User authentication flows
- Form validation
- List scrolling and interaction
- Screen rotation handling

**Trade-offs**:
- Test speed vs coverage
- Real device vs emulator vs Robolectric
- Mocking vs real dependencies
- Flakiness vs comprehensive testing

## References

- [Android Testing Fundamentals](https://developer.android.com/training/testing/fundamentals)
- [Testing with JUnit](https://developer.android.com/training/testing/local-tests)
- [Espresso Testing](https://developer.android.com/training/testing/espresso)
- [Compose Testing](https://developer.android.com/jetpack/compose/testing)
