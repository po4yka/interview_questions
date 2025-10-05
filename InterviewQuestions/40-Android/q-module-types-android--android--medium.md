---
tags:
  - android
  - modules
  - app-module
  - library-module
  - feature-module
  - difficulty/medium
difficulty: medium
---

# Types of Android Modules / Типы модулей Android

**English**: What types of modules do you know?

## Answer

In Android modularization, there are several types of modules, each serving a specific purpose in the app's architecture:

**1. Data Modules**

A data module usually contains a repository, data sources and model classes. The three primary responsibilities of a data module are:

- **Encapsulate all data and business logic of a certain domain**: Each data module should be responsible for handling data that represents a certain domain. It can handle many types of data as long as they are related
- **Expose the repository as an external API**: The public API of a data module should be a repository as they are responsible for exposing the data to the rest of the app
- **Hide all implementation details and data sources from the outside**: Data sources should only be accessible by repositories from the same module. They remain hidden to the outside. You can enforce this by using Kotlin's `private` or `internal` visibility keyword

```kotlin
// Example data module structure
:core:data:user
├── repository/
│   └── UserRepository.kt (public API)
├── datasource/
│   ├── UserRemoteDataSource.kt (internal)
│   └── UserLocalDataSource.kt (internal)
└── model/
    └── User.kt
```

**2. Feature Modules**

A feature is an isolated part of an app's functionality that usually corresponds to a screen or series of closely related screens, like a sign up or checkout flow.

Features are associated with screens or destinations in your app. Therefore, they're likely to have an associated UI and `ViewModel` to handle their logic and state. A single feature doesn't have to be limited to a single view or navigation destination. **Feature modules depend on data modules**.

```kotlin
// Example feature module structure
:feature:profile
├── ProfileScreen.kt
├── ProfileViewModel.kt
├── ProfileUiState.kt
└── components/
    ├── ProfileHeader.kt
    └── ProfileSettings.kt
```

**3. App Modules**

App modules are an entry point to the application. They depend on feature modules and usually provide root navigation. A single app module can be compiled to a number of different binaries thanks to build variants.

```kotlin
// Example app module structure
:app
├── MainActivity.kt
├── MyApplication.kt
├── navigation/
│   └── NavGraph.kt
└── di/
    └── AppModule.kt
```

If your app targets multiple device types, such as auto, wear or TV, define an app module per each. This helps separate platform specific dependencies.

```
:app (mobile)
:app-wear (wearOS)
:app-tv (Android TV)
:app-auto (Android Auto)
```

**4. Common Modules (Core Modules)**

Common modules, also known as core modules, contain code that other modules frequently use. They reduce redundancy and don't represent any specific layer in an app's architecture. The following are examples of common modules:

- **UI module**: If you use custom UI elements or elaborate branding in your app, you should consider encapsulating your widget collection into a module for all the features to reuse. This could help make your UI consistent across different features. For example, if your theming is centralized, you can avoid a painful refactor when a rebrand happens

```kotlin
:core:ui
├── theme/
│   ├── Color.kt
│   ├── Theme.kt
│   └── Type.kt
└── components/
    ├── Button.kt
    ├── TextField.kt
    └── Card.kt
```

- **Analytics module**: Tracking is often dictated by business requirements with little consideration to the software architecture. Analytics trackers are often used in many unrelated components. If that's the case for you, it might be a good idea to have a dedicated analytics module

```kotlin
:core:analytics
└── AnalyticsTracker.kt
```

- **Network module**: When many modules require a network connection, you might consider having a module dedicated to providing a http client. It is especially useful when your client requires custom configuration

```kotlin
:core:network
├── RetrofitClient.kt
├── NetworkConfig.kt
└── interceptors/
    └── AuthInterceptor.kt
```

- **Utility module**: Utilities, also known as helpers, are usually small pieces of code that are reused across the application. Examples of utilities include testing helpers, a currency formatting function, email validator or a custom operator

```kotlin
:core:common
├── extensions/
│   ├── StringExt.kt
│   └── DateExt.kt
└── utils/
    ├── EmailValidator.kt
    └── CurrencyFormatter.kt
```

**5. Test Modules**

Test modules are Android modules that are used for testing purposes only. The modules contain test code, test resources, and test dependencies that are only required for running tests and are not needed during the application's runtime. Test modules are created to separate test-specific code from the main application, making the module code easier to manage and maintain.

**Use cases for test modules:**

- **Shared test code**: If you have multiple modules in your project and some of the test code is applicable to more than one module, you can create a test module to share the code. This can help reduce duplication and make your test code easier to maintain. Shared test code can include utility classes or functions, such as custom assertions or matchers, as well as test data, such as simulated JSON responses

- **Cleaner Build Configurations**: Test modules allow you to have cleaner build configurations, as they can have their own `build.gradle` file. You don't have to clutter your app module's `build.gradle` file with configurations that are only relevant for tests

- **Integration Tests**: Test modules can be used to store integration tests that are used to test interactions between different parts of your app, including user interface, business logic, network requests, and database queries

- **Large-scale applications**: Test modules are particularly useful for large-scale applications with complex codebases and multiple modules. In such cases, test modules can help improve code organization and maintainability

```kotlin
:core:testing
├── fakes/
│   ├── FakeUserRepository.kt
│   └── FakeNetworkDataSource.kt
├── rules/
│   └── MainDispatcherRule.kt
└── data/
    └── TestData.kt
```

**Module Dependency Example:**

```
:app
  └── depends on :feature:login, :feature:home
      └── :feature:login depends on :core:data:auth, :core:ui
          └── :core:data:auth depends on :core:network, :core:database
              └── :core:network (no dependencies)
              └── :core:database (no dependencies)
```

**Summary:**

- **Data modules**: Contain repositories, data sources, and models
- **Feature modules**: Contain UI, ViewModels, and feature-specific logic
- **App modules**: Entry points, navigation, dependency injection setup
- **Common modules**: Shared code (UI, network, analytics, utilities)
- **Test modules**: Shared test code, fakes, test utilities

**Source**: [Types of modules](https://developer.android.com/topic/modularization/patterns#types-of-modules)

## Ответ

В модуляризации Android существует несколько типов модулей, каждый из которых служит определённой цели в архитектуре приложения:

**1. Data модули (Модули данных)**

Data модуль обычно содержит репозиторий, источники данных и классы моделей. Три основные обязанности data модуля:
- Инкапсулировать все данные и бизнес-логику определённого домена
- Предоставлять репозиторий как внешний API
- Скрывать все детали реализации и источники данных от внешнего мира

**2. Feature модули (Модули функций)**

Feature модуль — это изолированная часть функциональности приложения, которая обычно соответствует экрану или серии тесно связанных экранов, например, процессу регистрации или оформления заказа. Feature модули зависят от data модулей и содержат UI и ViewModel для обработки логики и состояния.

**3. App модули (Модули приложения)**

App модули — это точка входа в приложение. Они зависят от feature модулей и обычно предоставляют корневую навигацию. Один app модуль может быть скомпилирован в несколько различных бинарных файлов благодаря вариантам сборки. Если приложение ориентировано на несколько типов устройств (auto, wear, TV), следует определить отдельный app модуль для каждого.

**4. Common модули (Общие модули / Core модули)**

Common модули, также известные как core модули, содержат код, который часто используют другие модули. Они уменьшают избыточность и не представляют какой-либо конкретный слой в архитектуре приложения. Примеры:
- **UI модуль** — пользовательские UI элементы, темы, компоненты
- **Analytics модуль** — трекинг и аналитика
- **Network модуль** — HTTP клиент и конфигурация сети
- **Utility модуль** — вспомогательные функции, валидаторы, форматтеры

**5. Test модули (Тестовые модули)**

Test модули — это Android модули, используемые только для целей тестирования. Они содержат тестовый код, тестовые ресурсы и тестовые зависимости. Варианты использования:
- Совместно используемый тестовый код
- Более чистые конфигурации сборки
- Интеграционные тесты
- Крупномасштабные приложения с сложной кодовой базой

**Резюме:**

- **Data модули** содержат репозитории, источники данных и модели
- **Feature модули** содержат UI, ViewModel и логику, специфичную для функции
- **App модули** — точки входа, навигация, настройка внедрения зависимостей
- **Common модули** — общий код (UI, сеть, аналитика, утилиты)
- **Test модули** — общий тестовый код, фейки, тестовые утилиты
