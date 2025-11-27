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
updated: 2025-11-10
tags: [android/architecture-modularization, android/build-variants, android/gradle, architecture, difficulty/medium, modularization, modules]
moc: moc-android
related: [c-gradle, c-modularization]
sources: ["https://developer.android.com/topic/modularization/patterns"]

date created: Saturday, November 1st 2025, 1:25:21 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---
# Вопрос (RU)

> Какие типы модулей существуют в Android?

# Question (EN)

> What types of modules do you know in Android?

---

## Ответ (RU)

Важно различать:
- официальные типы Android/Gradle-модулей (например, `com.android.application`, `com.android.library`, dynamic feature и т.п.), и
- архитектурные/организационные категории модулей, которые команды используют при модуляризации.

Ниже описаны именно архитектурные типы модулей, строящиеся поверх стандартных Gradle-модулей, а не формальные типы плагинов.

### 1. Data Модули (Модули данных)

Data модуль содержит репозитории, источники данных и классы моделей. Основные обязанности:

- **Инкапсуляция работы с данными** — каждый data-модуль отвечает за получение, кэширование, объединение и преобразование данных по определённому домену (фича/контекст)
- **Репозиторий как публичный API** — публичный API модуля должен быть репозиторием (или набором use-case-like фасадов), предоставляющим данные остальной части приложения
- **Скрытие деталей реализации** — источники данных (remote/local) и внутренние модели доступны только внутри модуля; для этого используют `internal` для верхнеуровневых объявлений и более узкие уровни видимости для членов классов

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

(Бизнес-правила домена обычно живут в domain-/use-case модулях; data-модули реализуют доступ к данным и маппинг.)

### 2. Feature Модули (Модули функций)

Feature модуль — изолированная часть функциональности приложения, соответствующая экрану или серии связанных экранов (регистрация, checkout flow).

Feature модули:
- Связаны с экранами/навигационными точками
- Содержат UI и `ViewModel` для логики презентации и состояния
- **Зависят от data и core/common модулей**, но не наоборот

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

App модули — точки входа в приложение (обычно Android `Application`/`Activity`, манифест, packaging options и т.п.):
- Зависят от feature модулей
- Предоставляют корневую навигацию
- Конфигурируют DI, логирование, трекинг и др. инфраструктуру
- Используют build variants (и product flavors), чтобы собирать разные APK/AAB из одного или нескольких app модулей

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

Для разных типов устройств можно создавать отдельные app модули (каждый со своим манифестом и конфигурацией):

```groovy
:app              // Mobile
:app-wear         // WearOS
:app-tv           // Android TV
:app-auto         // Android Auto
```

### 4. Common Модули (Core модули)

Common/core модули содержат код, часто используемый другими модулями. Они уменьшают избыточность и выступают как общий инфраструктурный слой, поддерживающий остальные модули.

**UI модуль** — общие UI элементы и брендинг:

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

**Utility модуль** — вспомогательные функции и общие утилиты:

```kotlin
:core:common
 extensions/
    StringExt.kt
 utils/
    EmailValidator.kt
```

### 5. Test Модули (Тестовые модули)

Test модули используются для тестирования и переиспользования тестового кода. В Android большая часть тестов живёт в `test/` и `androidTest/` source set'ах каждого модуля, но также часто создают отдельные модуль(и), например `:core:testing`, для общих фейков и утилит.

**Варианты использования отдельных test-модулей:**
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

```text
:app
  → :feature:login, :feature:home
  → :core:ui
  → :core:analytics

:feature:login
  → :core:data:auth
  → :core:ui

:core:data:auth
  → :core:network
  → :core:database
```

### Резюме

| Тип модуля | Назначение | Зависимости |
|------------|-----------|------------|
| **Data** | Репозитории, источники данных, модели | Зависят от Core/Common; используются Feature/App |
| **Feature** | UI, `ViewModel`, логика функции | Data, Core/Common модули |
| **App** | Точка входа, навигация, DI, конфигурация | Feature, Core/Common модули |
| **Common/Core** | Общий/инфраструктурный код (UI, network, analytics) | Минимальные; зависят от платформы/базовых либ |
| **Test** | Фейки, тестовые утилиты, общие тестовые зависимости | Подключаются к тестируемым модулям |

## Answer (EN)

It is important to distinguish between:
- official Android/Gradle module types (e.g., `com.android.application`, `com.android.library`, dynamic feature, etc.), and
- architectural/organizational module categories teams use when modularizing apps.

Below we focus on architectural module types built on top of standard Gradle modules, not on the plugin types themselves.

### 1. Data Modules

Data modules contain repositories, data sources, and model classes. Primary responsibilities:

- **Encapsulate data access** — each data module handles fetching, caching, combining, and transforming data for a specific domain/feature context
- **Expose repository as public API** — the public API should be a repository (or thin facade/use-case-like entry point) exposing data to the rest of the app
- **Hide implementation details** — data sources (remote/local) and internal models should only be visible inside the module; use `internal` for top-level declarations and narrower visibilities for class members

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

(Domain business rules typically live in domain/use-case modules; data modules implement data access and mapping.)

### 2. Feature Modules

Feature modules are isolated parts of app functionality corresponding to a screen or a set of related screens (sign-up, checkout flow).

Feature modules:
- Associated with screens/navigation destinations
- Contain UI and `ViewModel` for presentation logic and state
- **Depend on data and core/common modules**, but not vice versa

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

App modules are the entry points to the application (typically host the `Application`/`Activity`, manifest, packaging configuration, etc.):
- Depend on feature modules
- Provide root navigation
- Configure DI, logging, analytics, and other infrastructure
- Use build variants (and product flavors) to produce different APKs/AABs from one or more app modules

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

For multiple device types, you can define separate app modules (each with its own manifest and configuration):

```groovy
:app              // Mobile
:app-wear         // WearOS
:app-tv           // Android TV
:app-auto         // Android Auto
```

### 4. Common Modules (Core Modules)

Common/core modules contain code frequently used by other modules. They reduce duplication and act as a shared infrastructure layer supporting other modules.

**UI module** — shared UI elements and branding:

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

**Utility module** — helper functions and shared utilities:

```kotlin
:core:common
 extensions/
    StringExt.kt
 utils/
    EmailValidator.kt
```

### 5. Test Modules

Test modules are used to support testing and reuse of test code. In Android, most tests live in `test/` and `androidTest/` source sets inside each module, but it's also common to create dedicated modules such as `:core:testing` for shared fakes and utilities.

**Use cases for separate test modules:**
- **Shared test code** — reuse test utilities, assertions, and test data across modules
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

```text
:app
  → :feature:login, :feature:home
  → :core:ui
  → :core:analytics

:feature:login
  → :core:data:auth
  → :core:ui

:core:data:auth
  → :core:network
  → :core:database
```

### Summary

| Module Type | Purpose | Dependencies |
|------------|---------|--------------|
| **Data** | Repositories, data sources, models | Depend on Core/Common; consumed by Feature/App |
| **Feature** | UI, `ViewModel`, feature logic | Depend on Data, Core/Common modules |
| **App** | Entry point, navigation, DI, configuration | Depend on Feature, Core/Common modules |
| **Common/Core** | Shared/infrastructure code (UI, network, analytics) | Minimal; depend on platform/base libs |
| **Test** | Fakes, test utilities, shared test dependencies | Attached to modules under test |

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

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]] - Gradle build system basics
- [[q-android-project-parts--android--easy]] - Android project structure
- [[q-android-manifest-file--android--easy]] - Manifest configuration

### Same Level (Medium)
- [[q-android-modularization--android--medium]] - Modularization strategies
- [[q-multiple-manifests-multimodule--android--medium]] - Multi-module manifests
- [[q-build-optimization-gradle--android--medium]] - Gradle optimization
- [[q-kapt-vs-ksp--android--medium]] - Annotation processing

### Advanced (Hard)
- [[q-modularization-patterns--android--hard]] - Advanced module patterns
- [[q-multi-module-best-practices--android--hard]] - Best practices
- [[q-android-release-pipeline-cicd--android--hard]] - CI/CD pipelines
