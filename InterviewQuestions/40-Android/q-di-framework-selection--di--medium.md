---
id: android-749
title: DI Framework Selection Guide 2026 / Выбор DI-фреймворка в 2026
aliases:
- DI Framework Selection
- Choosing DI Framework
- Выбор DI фреймворка
- Какой DI выбрать
topic: android
subtopics:
- di-hilt
- di-koin
- di-dagger
- architecture-clean
question_kind: decision
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dependency-injection
- c-hilt
- q-koin-vs-hilt-comparison--android--medium
- q-hilt-vs-dagger--di--medium
- q-hilt-vs-koin--di--medium
- q-manual-di-vs-framework--di--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-hilt
- android/di-koin
- android/di-dagger
- android/architecture-clean
- dependency-injection
- difficulty/medium
- architecture
---
# Вопрос (RU)
> Как выбрать DI-фреймворк для нового Android-проекта в 2026 году? Какие факторы учитывать?

# Question (EN)
> How to choose a DI framework for a new Android project in 2026? What factors should you consider?

---

## Ответ (RU)

### Текущий Ландшафт DI (2026)

| Фреймворк | Статус | Рекомендация Google |
|-----------|--------|---------------------|
| **Hilt** | Recommended | Официально рекомендован |
| **Koin 4.x** | Mature | Популярная альтернатива |
| **Dagger** | Maintained | Для не-Android/SDK |
| **Manual DI** | Always viable | Для простых проектов |

### Дерево Принятия Решений

```
Новый Android-проект (2026)
│
├─ Kotlin Multiplatform?
│  ├─ Да → Koin 4.x
│  └─ Нет ↓
│
├─ Простое приложение (<20 зависимостей)?
│  ├─ Да → Manual DI или Koin
│  └─ Нет ↓
│
├─ SDK/библиотека без Application?
│  ├─ Да → Dagger или Manual DI
│  └─ Нет ↓
│
├─ Команда знакома с Dagger?
│  ├─ Да → Hilt
│  └─ Нет ↓
│
├─ Время сборки критично?
│  ├─ Да → Koin 4.x
│  └─ Нет ↓
│
├─ Нужна compile-time безопасность?
│  ├─ Да → Hilt
│  └─ Нет → Koin 4.x
│
└─ По умолчанию → Hilt
```

### Матрица Выбора

| Критерий | Hilt | Koin 4.x | Dagger | Manual |
|----------|------|----------|--------|--------|
| **Порог входа** | Средний | Низкий | Высокий | Низкий |
| **Compile-time safety** | Да | Нет | Да | Нет |
| **Время сборки** | +30-60с | +0с | +30-60с | +0с |
| **Jetpack интеграция** | Отличная | Хорошая | Ручная | Ручная |
| **KMP поддержка** | Нет | Да | Частичная | Да |
| **Тестируемость** | Отличная | Отличная | Хорошая | Отличная |
| **Документация** | Отличная | Хорошая | Обширная | N/A |
| **Поддержка Google** | Да | Нет | Да | N/A |

### Рекомендации по Типам Проектов

**Стартап / MVP:**
```
Рекомендация: Koin 4.x или Manual DI
Причина: Быстрая итерация, минимум ceremony
```

**Корпоративное приложение:**
```
Рекомендация: Hilt
Причина: Compile-time safety, долгосрочная поддержка
```

**KMP проект:**
```
Рекомендация: Koin 4.x
Причина: Единственный зрелый вариант для KMP
```

**SDK / Библиотека:**
```
Рекомендация: Manual DI или Dagger
Причина: Нет зависимости от Application
```

**Микросервисы / Backend на Kotlin:**
```
Рекомендация: Koin или Dagger
Причина: Hilt только для Android
```

### Пример Конфигурации для Каждого Варианта

**Hilt (корпоративное приложение):**
```kotlin
// build.gradle.kts
plugins {
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")  // KSP в 2026 предпочтительнее kapt
}

dependencies {
    implementation("com.google.dagger:hilt-android:2.51")
    ksp("com.google.dagger:hilt-compiler:2.51")
}
```

**Koin 4.x (стартап / KMP):**
```kotlin
// build.gradle.kts
dependencies {
    implementation("io.insert-koin:koin-android:4.0.0")
    implementation("io.insert-koin:koin-androidx-compose:4.0.0")

    // Для KMP
    implementation("io.insert-koin:koin-core:4.0.0")
}
```

**Manual DI (простой проект):**
```kotlin
// Без зависимостей - только архитектура кода
class AppContainer(context: Context) {
    private val database = AppDatabase.create(context)
    private val api = ApiClient.create()

    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(api, database.userDao())
    }
}
```

### Критерии Миграции

Когда менять фреймворк:

| Триггер | Действие |
|---------|----------|
| Проект перерос Manual DI | Migrate to Koin или Hilt |
| Частые runtime ошибки в Koin | Migrate to Hilt |
| Добавление KMP | Migrate to Koin |
| Build time стал проблемой | Migrate to Koin или оптимизировать Hilt |

### Итоговая Рекомендация (2026)

**Для большинства новых Android-проектов: Hilt**
- Официальная поддержка Google
- Отличная интеграция с Jetpack
- Compile-time безопасность
- Растущая экосистема

**Для KMP и быстрых прототипов: Koin 4.x**
- Единственный зрелый KMP-вариант
- Быстрая сборка
- Простой API

---

## Answer (EN)

### Current DI Landscape (2026)

| Framework | Status | Google Recommendation |
|-----------|--------|----------------------|
| **Hilt** | Recommended | Officially recommended |
| **Koin 4.x** | Mature | Popular alternative |
| **Dagger** | Maintained | For non-Android/SDK |
| **Manual DI** | Always viable | For simple projects |

### Decision Tree

```
New Android Project (2026)
│
├─ Kotlin Multiplatform?
│  ├─ Yes → Koin 4.x
│  └─ No ↓
│
├─ Simple app (<20 dependencies)?
│  ├─ Yes → Manual DI or Koin
│  └─ No ↓
│
├─ SDK/library without Application?
│  ├─ Yes → Dagger or Manual DI
│  └─ No ↓
│
├─ Team familiar with Dagger?
│  ├─ Yes → Hilt
│  └─ No ↓
│
├─ Build time critical?
│  ├─ Yes → Koin 4.x
│  └─ No ↓
│
├─ Need compile-time safety?
│  ├─ Yes → Hilt
│  └─ No → Koin 4.x
│
└─ Default → Hilt
```

### Selection Matrix

| Criterion | Hilt | Koin 4.x | Dagger | Manual |
|-----------|------|----------|--------|--------|
| **Entry barrier** | Medium | Low | High | Low |
| **Compile-time safety** | Yes | No | Yes | No |
| **Build time** | +30-60s | +0s | +30-60s | +0s |
| **Jetpack integration** | Excellent | Good | Manual | Manual |
| **KMP support** | No | Yes | Partial | Yes |
| **Testability** | Excellent | Excellent | Good | Excellent |
| **Documentation** | Excellent | Good | Extensive | N/A |
| **Google support** | Yes | No | Yes | N/A |

### Recommendations by Project Type

**Startup / MVP:**
```
Recommendation: Koin 4.x or Manual DI
Reason: Fast iteration, minimal ceremony
```

**Enterprise application:**
```
Recommendation: Hilt
Reason: Compile-time safety, long-term support
```

**KMP project:**
```
Recommendation: Koin 4.x
Reason: Only mature option for KMP
```

**SDK / Library:**
```
Recommendation: Manual DI or Dagger
Reason: No dependency on Application
```

**Microservices / Kotlin Backend:**
```
Recommendation: Koin or Dagger
Reason: Hilt is Android-only
```

### Configuration Example for Each Option

**Hilt (enterprise app):**
```kotlin
// build.gradle.kts
plugins {
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")  // KSP preferred over kapt in 2026
}

dependencies {
    implementation("com.google.dagger:hilt-android:2.51")
    ksp("com.google.dagger:hilt-compiler:2.51")
}
```

**Koin 4.x (startup / KMP):**
```kotlin
// build.gradle.kts
dependencies {
    implementation("io.insert-koin:koin-android:4.0.0")
    implementation("io.insert-koin:koin-androidx-compose:4.0.0")

    // For KMP
    implementation("io.insert-koin:koin-core:4.0.0")
}
```

**Manual DI (simple project):**
```kotlin
// No dependencies - just code architecture
class AppContainer(context: Context) {
    private val database = AppDatabase.create(context)
    private val api = ApiClient.create()

    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(api, database.userDao())
    }
}
```

### Migration Criteria

When to change framework:

| Trigger | Action |
|---------|--------|
| Project outgrew Manual DI | Migrate to Koin or Hilt |
| Frequent runtime errors in Koin | Migrate to Hilt |
| Adding KMP | Migrate to Koin |
| Build time became a problem | Migrate to Koin or optimize Hilt |

### Final Recommendation (2026)

**For most new Android projects: Hilt**
- Official Google support
- Excellent Jetpack integration
- Compile-time safety
- Growing ecosystem

**For KMP and rapid prototypes: Koin 4.x**
- Only mature KMP option
- Fast builds
- Simple API

---

## Follow-ups

- Как убедить команду перейти на другой DI-фреймворк?
- Какие метрики отслеживать при оценке DI-решения?
- Как спланировать миграцию между DI-фреймворками?

## References

- [Android DI Guide](https://developer.android.com/training/dependency-injection)
- [Hilt Best Practices](https://developer.android.com/training/dependency-injection/hilt-android)
- [Koin Getting Started](https://insert-koin.io/docs/quickstart/android)

## Related Questions

### Prerequisites
- [[q-dagger-purpose--android--easy]] - Why use DI
- [[c-dependency-injection]] - DI concept

### Related
- [[q-koin-vs-hilt-comparison--android--medium]] - Detailed Koin vs Hilt
- [[q-hilt-vs-dagger--di--medium]] - Hilt vs pure Dagger
- [[q-hilt-vs-koin--di--medium]] - Performance comparison
- [[q-manual-di-vs-framework--di--medium]] - Manual vs framework

### Advanced
- [[q-koin-vs-dagger-philosophy--android--hard]] - Philosophy comparison
- [[q-multi-module-best-practices--android--hard]] - DI in multi-module
