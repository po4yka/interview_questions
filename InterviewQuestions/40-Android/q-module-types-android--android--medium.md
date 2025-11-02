---
id: android-112
title: "Module Types Android / Типы модулей Android"
aliases: [Android Module Types, Module Types, Типы модулей, Типы модулей Android]
topic: android
subtopics: [architecture-modularization, build-variants, gradle]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-10-30
tags: [android/architecture-modularization, android/build-variants, android/gradle, architecture, difficulty/medium, modularization, modules]
moc: moc-android
related: [c-gradle, c-modularization]
sources: [https://developer.android.com/topic/modularization/patterns]
date created: Saturday, November 1st 2025, 1:25:21 pm
date modified: Saturday, November 1st 2025, 5:43:33 pm
---

# Вопрос (RU)

> Какие типы модулей существуют в Android?

# Question (EN)

> What types of modules do you know in Android?

---

## Ответ (RU)

В модуляризации Android существует 5 основных типов модулей:

### 1. Data Модули (Модули данных)

Data модуль содержит репозиторий, источники данных и классы моделей. Три основные обязанности:

- **Инкапсуляция данных и бизнес-логики домена** — каждый data модуль отвечает за обработку данных определённого домена
- **Репозиторий как публичный API** — публичный API модуля должен быть репозиторием, отвечающим за предоставление данных остальной части приложения
- **Скрытие деталей реализации** — источники данных доступны только репозиториям из того же модуля (использовать `private` или `internal`)

```kotlin
// ✅ Структура data модуля
:core:data:user
 repository/
    UserRepository.kt          // публичный API
 datasource/
    UserRemoteDataSource.kt    // internal
    UserLocalDataSource.kt     // internal
 model/
    User.kt
```

### 2. Feature Модули (Модули функций)

Feature модуль — изолированная часть функциональности приложения, соответствующая экрану или серии связанных экранов (регистрация, checkout flow).

Feature модули:
- Связаны с экранами/навигационными точками
- Содержат UI и `ViewModel` для логики и состояния
- **Зависят от data модулей**

```kotlin
// ✅ Структура feature модуля
:feature:profile
 ProfileScreen.kt
 ProfileViewModel.kt
 ProfileUiState.kt
 components/
    ProfileHeader.kt
```

### 3. App Модули (Модули приложения)

App модули — точка входа в приложение:
- Зависят от feature модулей
- Предоставляют корневую навигацию
- Компилируются в разные бинарные файлы благодаря build variants

```kotlin
// ✅ Структура app модуля
:app
 MainActivity.kt
 MyApplication.kt
 navigation/
    NavGraph.kt
 di/
    AppModule.kt
```

Для разных типов устройств создавать отдельные app модули:

```
:app              // mobile
:app-wear         // wearOS
:app-tv           // Android TV
:app-auto         // Android Auto
```

### 4. Common Модули (Core модули)

Common/core модули содержат код, часто используемый другими модулями. Уменьшают избыточность и не представляют конкретный слой архитектуры:

**UI модуль** — пользовательские UI элементы и брендинг:

```kotlin
// ✅ UI модуль
:core:ui
 theme/
    Theme.kt
    Color.kt
 components/
    Button.kt
    TextField.kt
```

**Analytics модуль** — трекинг и метрики:

```kotlin
:core:analytics
 AnalyticsTracker.kt
```

**Network модуль** — HTTP клиент с кастомной конфигурацией:

```kotlin
:core:network
 RetrofitClient.kt
 interceptors/
    AuthInterceptor.kt
```

**Utility модуль** — вспомогательные функции:

```kotlin
:core:common
 extensions/
    StringExt.kt
 utils/
    EmailValidator.kt
```

### 5. Test Модули (Тестовые модули)

Test модули используются только для тестирования. Содержат тестовый код, ресурсы и зависимости.

**Варианты использования:**
- **Общий тестовый код** — переиспользование тестовых утилит, ассертов, тестовых данных между модулями
- **Чистые конфигурации сборки** — отдельный `build.gradle` для тестовых зависимостей
- **Интеграционные тесты** — тестирование взаимодействия между частями приложения
- **Крупные приложения** — улучшение организации кода в сложных кодовых базах

```kotlin
// ✅ Структура test модуля
:core:testing
 fakes/
    FakeUserRepository.kt
 rules/
    MainDispatcherRule.kt
 data/
    TestData.kt
```

### Пример Зависимостей Модулей

```
:app
   → :feature:login, :feature:home
      → :feature:login
         → :core:data:auth, :core:ui
            → :core:data:auth
               → :core:network, :core:database
```

### Резюме

| Тип модуля | Назначение | Зависимости |
|------------|-----------|------------|
| **Data** | Репозитории, источники данных, модели | Core модули |
| **Feature** | UI, ViewModel, логика функции | Data, Core модули |
| **App** | Точка входа, навигация, DI | Feature модули |
| **Common/Core** | Общий код (UI, network, analytics) | Минимальные |
| **Test** | Фейки, тестовые утилиты | Тестируемые модули |

## Answer (EN)

In Android modularization, there are 5 main module types:

### 1. Data Modules

Data modules contain repositories, data sources, and model classes. Three primary responsibilities:

- **Encapsulate domain data and business logic** — each data module handles data for a specific domain
- **Expose repository as public API** — the public API should be a repository responsible for exposing data to the rest of the app
- **Hide implementation details** — data sources accessible only by repositories from the same module (use `private` or `internal`)

```kotlin
// ✅ Data module structure
:core:data:user
 repository/
    UserRepository.kt          // public API
 datasource/
    UserRemoteDataSource.kt    // internal
    UserLocalDataSource.kt     // internal
 model/
    User.kt
```

### 2. Feature Modules

Feature modules are isolated parts of app functionality corresponding to a screen or series of related screens (sign up, checkout flow).

Feature modules:
- Associated with screens/navigation destinations
- Contain UI and `ViewModel` for logic and state
- **Depend on data modules**

```kotlin
// ✅ Feature module structure
:feature:profile
 ProfileScreen.kt
 ProfileViewModel.kt
 ProfileUiState.kt
 components/
    ProfileHeader.kt
```

### 3. App Modules

App modules are entry points to the application:
- Depend on feature modules
- Provide root navigation
- Compile to different binaries via build variants

```kotlin
// ✅ App module structure
:app
 MainActivity.kt
 MyApplication.kt
 navigation/
    NavGraph.kt
 di/
    AppModule.kt
```

For multiple device types, define separate app modules:

```
:app              // mobile
:app-wear         // wearOS
:app-tv           // Android TV
:app-auto         // Android Auto
```

### 4. Common Modules (Core Modules)

Common/core modules contain code frequently used by other modules. They reduce redundancy and don't represent specific architecture layers:

**UI module** — custom UI elements and branding:

```kotlin
// ✅ UI module
:core:ui
 theme/
    Theme.kt
    Color.kt
 components/
    Button.kt
    TextField.kt
```

**Analytics module** — tracking and metrics:

```kotlin
:core:analytics
 AnalyticsTracker.kt
```

**Network module** — HTTP client with custom configuration:

```kotlin
:core:network
 RetrofitClient.kt
 interceptors/
    AuthInterceptor.kt
```

**Utility module** — helper functions:

```kotlin
:core:common
 extensions/
    StringExt.kt
 utils/
    EmailValidator.kt
```

### 5. Test Modules

Test modules are used for testing purposes only. They contain test code, resources, and dependencies.

**Use cases:**
- **Shared test code** — reuse test utilities, assertions, test data across modules
- **Cleaner build configurations** — separate `build.gradle` for test dependencies
- **Integration tests** — test interactions between different app parts
- **Large-scale applications** — improve code organization in complex codebases

```kotlin
// ✅ Test module structure
:core:testing
 fakes/
    FakeUserRepository.kt
 rules/
    MainDispatcherRule.kt
 data/
    TestData.kt
```

### Module Dependency Example

```
:app
   → :feature:login, :feature:home
      → :feature:login
         → :core:data:auth, :core:ui
            → :core:data:auth
               → :core:network, :core:database
```

### Summary

| Module Type | Purpose | Dependencies |
|------------|---------|--------------|
| **Data** | Repositories, data sources, models | Core modules |
| **Feature** | UI, ViewModel, feature logic | Data, Core modules |
| **App** | Entry point, navigation, DI | Feature modules |
| **Common/Core** | Shared code (UI, network, analytics) | Minimal |
| **Test** | Fakes, test utilities | Modules under test |

---

## Follow-ups

- How do you prevent circular dependencies between modules?
- What are the performance implications of having too many modules?
- How do you handle shared resources (strings, drawables) across modules?
- What strategy do you use for inter-module communication?
- How do you manage dependency injection across module boundaries?

## References

- [[c-modularization]]
- [[c-gradle]]
- [[c-dependency-injection]]
- [Types of modules - Android Developers](https://developer.android.com/topic/modularization/patterns)

## Related Questions

### Same Level (Medium)
- Related content to be added

### Advanced (Hard)
- Related content to be added
