---
id: android-252
title: KMM vs Flutter Comparison / Сравнение KMM и Flutter
aliases: [KMM vs Flutter, Kotlin Multiplatform Mobile vs Flutter, Сравнение KMM и Flutter]
topic: android
subtopics:
- architecture-clean
- kmp
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-android-architectural-patterns--android--medium
sources:
- "https://flutter.dev/docs"
- "https://kotlinlang.org/docs/multiplatform.html"
created: 2025-10-15
updated: 2025-11-10
tags: [android/architecture-clean, android/kmp, cross-platform, difficulty/medium, flutter, multiplatform]

---

# Вопрос (RU)

> Сравните Kotlin Multiplatform Mobile (KMM) с Flutter для кросс-платформенной разработки.

## Ответ (RU)

KMM и Flutter представляют два фундаментально разных подхода к кросс-платформенной разработке.

### Теоретические Основы

**Кросс-платформенная разработка** — стратегия создания приложений для нескольких платформ с максимальным переиспользованием кода. Основные подходы:

**Native Development** — отдельные кодовые базы для каждой платформы, максимальная производительность и UX, но высокая стоимость разработки.

**Cross-platform** — общая кодовая база с платформенно-специфичными адаптациями. Компромиссы между производительностью, UX и скоростью разработки.

**Key Considerations:**
- **Platform fragmentation** — Android/iOS имеют разные UI-паттерны и системные API
- **Performance requirements** — игры/AR vs бизнес-приложения vs контентные приложения
- **Team composition** — нативная экспертиза vs универсальные разработчики
- **Time-to-market** — скорость MVP vs долгосрочная поддерживаемость

### Краткая Версия

KMM — типично шаринг бизнес-логики (~60-70%) с нативным UI; Flutter — шаринг UI + логики (до ~90-95% кода). KMM более уместен, когда критичны нативный UX и плотная интеграция с платформой, Flutter — когда важны скорость разработки и охват нескольких платформ (mobile + web + desktop). Основной компромисс: KMM требует нативной экспертизы и двух UI, Flutter — добавляет движок и слой абстракции, но ускоряет delivery.

### Подробная Версия

Сравните Kotlin Multiplatform Mobile (KMM) с Flutter для кросс-платформенной разработки:

**Архитектурные различия:**
- KMM: Shared бизнес-логика + нативный UI (Jetpack Compose, SwiftUI)
- Flutter: Shared UI + логика с использованием platform channels/FFI для доступа к нативным API

**Производительность (типичные тенденции, не гарантии):**
- KMM: Нативный UI и бизнес-логика, сборка под целевую платформу; поведение и метрики ближе к чисто нативным приложениям при правильной реализации.
- Flutter: Собственный движок (Skia) и слой рендеринга; AOT-компиляция на релизе дает близкую к нативной производительность для большинства бизнес-приложений, но есть накладные расходы движка и моста к нативным API.

**Trade-offs:**
- KMM: Лучше вписывается в существующие нативные приложения и UX-гайды, прямой доступ к платформенным фичам, но требует отдельного UI под Android и iOS.
- Flutter: Быстрее разработка благодаря общему UI и логике, единый стек для команды, но UI не нативный, а нарисованный движком; глубокая интеграция с последними фичами платформ опосредована Flutter SDK и плагинами.

**Когда выбирать:**
- KMM: Нужен нативный UX, есть существующие нативные приложения/команда, важна предсказуемая интеграция с платформой.
- Flutter: Быстрый MVP, кросс-платформенный продукт (mobile + web + desktop), сильный фокус на кастомном UI и единый стек для небольшой команды.

### Архитектурные Различия

**KMM (Kotlin Multiplatform Mobile)**:
- Shared: Бизнес-логика ~60-80% (repositories, use cases, models)
- Platform-specific: Нативный UI (Jetpack Compose, SwiftUI)
- Технология: Kotlin Multiplatform компилируется в артефакты под конкретные таргеты (JVM, iOS/Native и др.), общий код шарится между ними
- Философия: "Native UI with shared logic"

**Flutter**:
- Shared: UI + логика до ~90-95% (widgets, бизнес-логика, state)
- Platform-specific: Остаток (platform channels/FFI для доступа к нативным API, интеграция со специфичными фичами)
- Технология: Dart + собственный rendering engine (Skia)
- Философия: "Write once, run on multiple platforms" (с единым UI-слоем)

```kotlin
// ✅ KMM: Shared business logic (упрощенный пример)
class TaskRepository(
    private val api: TaskApi,
    private val database: TaskDatabase
) {
    suspend fun getTasks(): Result<List<Task>> {
        return try {
            val remote = api.fetchTasks()
            database.saveTasks(remote)
            Result.success(remote)
        } catch (e: Exception) {
            Result.success(database.getTasks())
        }
    }
}

// Android UI (Jetpack Compose)
@Composable
fun TaskList(tasks: List<Task>) {
    LazyColumn {
        items(tasks = tasks) { task ->
            TaskItem(task)
        }
    }
}

// iOS UI (SwiftUI)
struct TaskList: View {
    let tasks: [Task]

    var body: some View {
        List(tasks) { task in
            TaskRow(task: task)
        }
    }
}
```

```dart
// ✅ Flutter: Shared UI + logic (упрощенный пример)
class TaskRepository {
  final TaskApi api;
  final TaskDatabase database;

  TaskRepository(this.api, this.database);

  Future<List<Task>> getTasks() async {
    try {
      final remote = await api.fetchTasks();
      await database.saveTasks(remote);
      return remote;
    } catch (e) {
      return await database.getTasks();
    }
  }
}

// Single UI for both platforms
class TaskList extends StatelessWidget {
  final List<Task> tasks;

  const TaskList({super.key, required this.tasks});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: tasks.length,
      itemBuilder: (_, i) => TaskItem(task: tasks[i]),
    );
  }
}
```

### Производительность

(Цифры ниже — ориентировочные тенденции, реальные значения зависят от конкретного приложения, настроек и устройств.)

**Startup Time:**
- KMM: Близко к нативным приложениям аналогичной архитектуры.
- Flutter: Обычно немного выше за счет инициализации движка, но для большинства сценариев приемлем.

**Runtime Performance:**
- KMM: Нативный UI и код под конкретную платформу; предсказуемая производительность при корректной реализации.
- Flutter: AOT-компиляция и собственный рендеринг дают высокую производительность; для обычных бизнес-приложений часто сопоставима с нативной.

**App Size:**
- KMM: Сравним с нативными приложениями; итоговый размер зависит от shared-модулей и зависимостей.
- Flutter: Как правило больше из-за включения Flutter engine и фреймворка.

**Memory:**
- KMM: Использует механизмы управления памятью целевой платформы и рантайма Kotlin; накладные расходы минимальны относительно нативного.
- Flutter: Дополнительная память под Dart runtime и движок; в большинстве кейсов приемлемо, но выше базового нативного минимума.

### Development Experience

(Примеры ниже иллюстративные, а не нормативные.)

**Team Size & Skills:**
- KMM: Обычно нужен Kotlin/KMM + Android + iOS стек (часто 2 платформенные подкоманды).
- Flutter: Одна кросс-платформенная команда Flutter/Dart.

**Development Speed (пример для экрана профиля):**
- KMM: Время делится между shared-логикой и двумя нативными UI.
- Flutter: Одна реализация UI + логики для обеих мобильных платформ.

**Code Reuse:**
- KMM: Обычно 50-80% (зависит от объема доменной логики).
- Flutter: Часто 80-95% между mobile-платформами, выше при использовании web/desktop.

### Platform Integration

**KMM**:
```kotlin
// ✅ Прямой доступ к нативным Android API
class LocationManager(context: Context) {
    private val client = LocationServices
        .getFusedLocationProviderClient(context)

    suspend fun getLocation(): Location? {
        return client.lastLocation.await()
    }
}
```

**Flutter**:
```dart
// ✅ Доступ к нативным API через platform channel (есть дополнительный мост)
class LocationManager {
  static const platform = MethodChannel('location');

  Future<Map?> getLocation() async {
    return await platform.invokeMethod('getLocation');
  }
}
```

У Flutter есть небольшие накладные расходы на сериализацию и вызовы через канал по сравнению с прямыми нативными вызовами в KMM, но для большинства сценариев они некритичны.

### Use Cases

**Выбирайте KMM когда:**
- Критичен нативный UX (банкинг, health, приложения с жесткими guideline'ами платформ).
- Есть существующее нативное приложение и нужна постепенная мультиплатформенная стратегия.
- Нужна предсказуемая интеграция с новыми фичами iOS/Android с минимальными промежуточными слоями.
- Команда уже сильна в Android/iOS/Kotlin.

**Выбирайте Flutter когда:**
- Нужен быстрый MVP или прототип.
- Важен единый брендовый, кастомный UI на всех платформах.
- Маленькая команда / ограниченный бюджет.
- Цель — multi-platform (Web + Desktop + Mobile) с одним стеком.
- Требуется мощная анимация и pixel-perfect UI с высокой скоростью разработки.

### Cost Analysis

**Initial Development:**
- KMM: Выше, чем у Flutter, из-за двух UI и необходимости нативной экспертизы.
- Flutter: Ниже за счет единой реализации UI + логики.

**Maintenance:**
- KMM: Средняя сложность — shared логика + два UI.
- Flutter: Ниже при условии, что все платформы поддерживаются одной кодовой базой.

**Long-term:**
- KMM: Близость к платформам упрощает адаптацию к изменениям iOS/Android, но есть зависимость от зрелости Kotlin Multiplatform.
- Flutter: Зависимость от развития Flutter SDK и экосистемы; стабильность хорошая, но некоторые новые платформенные фичи требуют времени/плагинов.

### Decision Framework

**Native Experience Priority** → KMM
**Speed to Market Priority** → Flutter
**Existing Native App** → KMM (incremental adoption)
**Multi-platform (Web/Desktop)** → Flutter
**Deep Platform Integration priority** → KMM
**Small Team/Budget** → Flutter

### Лучшие Практики

- **Пилотный проект** — начните с небольшой фичи для оценки подхода перед полным переходом.
- **Platform expertise** — сохраняйте нативных разработчиков для платформенных требований (особенно с KMM).
- **Architecture alignment** — выбирайте подход в соответствии с текущими навыками команды и архитектурой.
- **Performance monitoring** — измеряйте реальные метрики до/после выбора технологии.
- **Migration strategy** — планируйте поэтапное внедрение с возможностью отката.

### Типичные Ошибки

- **Игнорирование UX differences** — Android/iOS имеют разные паттерны взаимодействия.
- **Неверные предположения о производительности** — Flutter достаточно быстрый для большинства бизнес-приложений; KMM не автоматически "магически быстрее" при неудачном дизайне.
- **Team composition mismatch** — команда только нативных разработчиков без Flutter-опыта или наоборот может замедлить проект.
- **Over-engineering** — использование KMM для очень простых приложений может излишне усложнить архитектуру.
- **Ignoring platform evolution** — регулярно пересматривайте стек, учитывая прогресс KMP и Flutter.

# Question (EN)

> Compare Kotlin Multiplatform Mobile (KMM) with Flutter for cross-platform development.

## Answer (EN)

KMM and Flutter represent two fundamentally different approaches to cross-platform development.

### Theoretical Foundations

**Cross-platform development** is a strategy for building apps across multiple platforms with maximum code reuse. Main approaches:

**Native Development** — separate codebases per platform, maximum performance and UX, but higher development cost.

**Cross-platform** — shared codebase with platform-specific adaptations. Trade-offs between performance, UX, and development speed.

**Key Considerations:**
- **Platform fragmentation** — Android/iOS have different UI patterns and system APIs
- **Performance requirements** — games/AR vs business apps vs content apps
- **Team composition** — native expertise vs generalist developers
- **Time-to-market** — MVP speed vs long-term maintainability

### Short Version

KMM typically shares business logic (~60-70%) with native UI; Flutter shares UI + logic (up to ~90-95% of code). KMM fits when you need native UX and deep platform integration; Flutter fits when you need faster development and broader multi-platform reach (mobile + web + desktop). Main trade-off: KMM needs native expertise and two UIs, Flutter adds engine overhead and abstraction but speeds up delivery.

### Detailed Version

Compare Kotlin Multiplatform Mobile (KMM) with Flutter for cross-platform development:

**Architectural differences:**
- KMM: Shared business logic + native UI (Jetpack Compose, SwiftUI)
- Flutter: Shared UI + logic, using platform channels/FFI for native APIs

**Performance (typical tendencies, not guarantees):**
- KMM: Native UI and platform-specific binaries; behavior and metrics are close to fully native apps when implemented correctly.
- Flutter: Custom rendering engine (Skia) and AOT-compiled Dart in release; near-native performance for most business apps, with some engine and bridging overhead.

**Trade-offs:**
- KMM: Better alignment with native UX and platform APIs; requires separate UIs per platform.
- Flutter: Faster development and higher code reuse; UI is rendered by Flutter engine rather than platform widgets, and access to the latest platform features goes through Flutter SDK/plugins.

### Architectural Differences

**KMM (Kotlin Multiplatform Mobile)**:
- Shared: Business logic ~60-80% (repositories, use cases, models)
- Platform-specific: Native UI (Jetpack Compose, SwiftUI)
- Technology: Kotlin Multiplatform compiles shared modules for different targets (JVM, Native, etc.), reused across Android/iOS
- Philosophy: "Native UI with shared logic"

**Flutter**:
- Shared: UI + logic up to ~90-95% (widgets, business logic, state)
- Platform-specific: Remaining code via platform channels/FFI for native APIs and platform-specific integrations
- Technology: Dart with custom rendering engine (Skia)
- Philosophy: "Write once, run on multiple platforms" with a unified UI layer

```kotlin
// ✅ KMM: Shared business logic (simplified example)
class TaskRepository(
    private val api: TaskApi,
    private val database: TaskDatabase
) {
    suspend fun getTasks(): Result<List<Task>> {
        return try {
            val remote = api.fetchTasks()
            database.saveTasks(remote)
            Result.success(remote)
        } catch (e: Exception) {
            Result.success(database.getTasks())
        }
    }
}

// Android UI (Jetpack Compose)
@Composable
fun TaskList(tasks: List<Task>) {
    LazyColumn {
        items(tasks = tasks) { task ->
            TaskItem(task)
        }
    }
}

// iOS UI (SwiftUI)
struct TaskList: View {
    let tasks: [Task]

    var body: some View {
        List(tasks) { task in
            TaskRow(task: task)
        }
    }
}
```

```dart
// ✅ Flutter: Shared UI + logic (simplified example)
class TaskRepository {
  final TaskApi api;
  final TaskDatabase database;

  TaskRepository(this.api, this.database);

  Future<List<Task>> getTasks() async {
    try {
      final remote = await api.fetchTasks();
      await database.saveTasks(remote);
      return remote;
    } catch (e) {
      return await database.getTasks();
    }
  }
}

// Single UI for both platforms
class TaskList extends StatelessWidget {
  final List<Task> tasks;

  const TaskList({super.key, required this.tasks});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: tasks.length,
      itemBuilder: (_, i) => TaskItem(task: tasks[i]),
    );
  }
}
```

### Performance

(Values below are indicative trends; real metrics depend on app design, size, device class, and build configuration.)

**Startup Time:**
- KMM: Similar to native apps with comparable stack.
- Flutter: Often slightly higher due to engine initialization, but acceptable for most apps.

**Runtime Performance:**
- KMM: Native UI and target-specific binaries; predictable performance similar to native implementations.
- Flutter: AOT-compiled Dart + Skia rendering provides high performance; typically near-native for standard business UIs.

**App Size:**
- KMM: Comparable to native apps; depends on shared modules and dependencies.
- Flutter: Usually larger due to bundling Flutter engine/framework.

**Memory:**
- KMM: Uses underlying platform memory management and Kotlin runtime; overhead close to native.
- Flutter: Extra memory for Dart runtime and engine; generally fine but higher than a minimal native app.

### Development Experience

(Examples below are illustrative, not prescriptive.)

**Team Size & Skills:**
- KMM: Often split between Android and iOS with shared Kotlin/KMM expertise.
- Flutter: Single cross-platform Flutter/Dart team.

**Development Speed (example: User Profile Screen):**
- KMM: Time split between shared logic and two native UIs.
- Flutter: One shared implementation of UI + logic.

**Code Reuse:**
- KMM: Commonly 50-80%, depending on how much domain logic can be shared.
- Flutter: Often 80-95% between mobile platforms, more with web/desktop.

### Platform Integration

**KMM**:
```kotlin
// ✅ Direct access to native Android APIs
class LocationManager(context: Context) {
    private val client = LocationServices
        .getFusedLocationProviderClient(context)

    suspend fun getLocation(): Location? {
        return client.lastLocation.await()
    }
}
```

**Flutter**:
```dart
// ✅ Access native APIs via platform channel (with an extra bridge)
class LocationManager {
  static const platform = MethodChannel('location');

  Future<Map?> getLocation() async {
    return await platform.invokeMethod('getLocation');
  }
}
```

Flutter's platform channels introduce serialization and IPC overhead compared to direct native calls, but this is usually negligible for typical use cases.

### Use Cases

**Choose KMM when:**
- Native UX is critical (banking, health, apps tightly following platform guidelines).
- You have an existing native app and want an incremental multiplatform strategy.
- You need predictable, low-friction access to the latest iOS/Android APIs.
- Your team already has strong Android/iOS/Kotlin expertise.

**Choose Flutter when:**
- You need a rapid MVP or prototype.
- You want a consistent, branded custom UI across platforms.
- You have a small team / limited budget.
- You target multiple platforms (Web + Desktop + Mobile) with one stack.
- You need rich animations and pixel-perfect UI with fast iteration.

### Cost Analysis

**Initial Development:**
- KMM: Higher than Flutter due to two UIs and native skills.
- Flutter: Lower due to single shared UI + logic.

**Maintenance:**
- KMM: Medium — shared logic plus separate UIs per platform.
- Flutter: Lower if all platforms share one codebase.

**Long-term:**
- KMM: Close to platforms, good for tracking OS changes; also depends on Kotlin Multiplatform maturity.
- Flutter: Depends on Flutter SDK evolution and ecosystem; very capable but one more layer between you and the platforms.

### Decision Framework

**Native Experience Priority** → KMM
**Speed to Market Priority** → Flutter
**Existing Native App** → KMM (incremental adoption)
**Multi-platform (Web/Desktop)** → Flutter
**Deep Platform Integration** → KMM
**Small Team/Budget** → Flutter

### Best Practices

- **Pilot project** — start with a small feature to validate the approach before full commitment.
- **Platform expertise** — keep native developers for platform-specific requirements (especially with KMM).
- **Architecture alignment** — pick an approach that matches your team's skills and existing architecture.
- **Performance monitoring** — measure real metrics before/after your technology choice.
- **Migration strategy** — plan gradual adoption with a rollback option.

### Common Pitfalls

- **Ignoring UX differences** — Android/iOS have different interaction patterns.
- **Performance assumptions** — Flutter is fast enough for most business apps; KMM is not automatically faster if poorly designed.
- **Team composition mismatch** — mismatch between chosen stack and real team skills slows delivery.
- **Over-engineering** — using KMM for very simple CRUD apps can add unnecessary complexity.
- **Ignoring platform evolution** — regularly reassess as KMP and Flutter evolve.

## Ссылки (RU)

- https://kotlinlang.org/docs/multiplatform.html — официальная документация KMM
- https://flutter.dev/docs — официальная документация Flutter
- https://developer.android.com/kotlin/multiplatform — руководство по KMM от Android

## References

- https://kotlinlang.org/docs/multiplatform.html - KMM official documentation
- https://flutter.dev/docs - Flutter official documentation
- https://developer.android.com/kotlin/multiplatform - Android KMM guide

## Дополнительные вопросы (RU)

- Как вы сравните React Native с KMM и Flutter по тем же критериям (архитектура, производительность, UX, стоимость)?
- В каких сценариях разумно комбинировать KMM и нативные модули вместо использования Flutter?
- Как изменится выбор стека для продукта с жесткими требованиями по офлайн-режиму и локальному шифрованию?
- Как архитектурно спроектировать проект, чтобы при необходимости можно было мигрировать с Flutter на KMM или наоборот?

## Follow-ups

- How would you compare React Native with KMM and Flutter using the same criteria (architecture, performance, UX, cost)?
- In which scenarios is it reasonable to combine KMM with native modules instead of using Flutter?
- How would strict offline and local encryption requirements change your stack choice?
- How would you architect a project to be able to migrate from Flutter to KMM or vice versa if needed?

## Связанные вопросы (RU)

- [[q-android-architectural-patterns--android--medium]]

## Related Questions

- [[q-android-architectural-patterns--android--medium]]
