---
id: 20251012-122767
title: Android Modularization / Модуляризация Android
aliases: [Android Modularization, Модуляризация Android]
topic: android
subtopics:
  - architecture-clean
  - build-variants
  - gradle
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-architectural-patterns--android--medium
  - q-android-build-optimization--android--medium
  - q-gradle-build-system--android--medium
created: 2025-10-15
updated: 2025-10-15
tags: [android/architecture-clean, android/build-variants, android/gradle, difficulty/medium]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:53:13 pm
---

# Вопрос (RU)
> Что такое Модуляризация Android?

---

# Question (EN)
> What is Android Modularization?

## Answer (EN)
**Android Modularization** is the practice of organizing codebases into loosely coupled, self-contained modules. Each module serves a specific purpose and can be developed, tested, and maintained independently.

**Modularization Theory:**
Modularization follows the principle of c-separation-of-concerns, breaking complex systems into manageable components. Each module encapsulates related functionality and exposes a well-defined interface, reducing coupling and improving maintainability through [[c-dependency-injection]].

**Core Benefits:**
- **Reusability**: Modules can be shared across multiple apps or features
- **Strict Visibility Control**: Internal implementation details are hidden from other modules
- **Customizable Delivery**: Play Feature Delivery enables on-demand feature loading
- **Scalability**: Changes in one module don't cascade to others
- **Ownership**: Each module can have dedicated maintainers
- **Testability**: Modules can be tested in isolation

**Module Types:**
- **App Module**: Main application entry point
- **Feature Modules**: Self-contained features (news, profile, settings)
- **Core Modules**: Shared functionality (data, network, UI)
- **Library Modules**: Reusable components

**Basic Module Structure:**
```
app/
├── app/                    # Main app module
├── feature:news/          # News feature module
├── feature:profile/       # Profile feature module
├── core:data/            # Data layer
├── core:network/         # Network layer
├── core:ui/              # UI components
└── shared:utils/         # Shared utilities
```

**Module Dependencies:**
```gradle
// app/build.gradle
dependencies {
    implementation project(':feature:news')
    implementation project(':feature:profile')
    implementation project(':core:data')
    implementation project(':core:network')
}

// feature:news/build.gradle
dependencies {
    implementation project(':core:data')
    implementation project(':core:ui')
    // No direct dependency on other features
}
```

**Visibility Control:**
```kotlin
// In core:data module
internal class DatabaseHelper {
    // Internal - only accessible within this module
}

public class UserRepository {
    // Public - accessible from other modules
    fun getUser(id: String): User = // ...
}

// In feature:news module
class NewsViewModel {
    private val userRepo = UserRepository() // Can access public API
    // Cannot access DatabaseHelper directly
}
```

**Play Feature Delivery:**
```gradle
// feature:news/build.gradle
android {
    dynamicFeatures = [':feature:news']
}

// app/build.gradle
dependencies {
    implementation 'com.google.android.play:core:1.10.3'
}
```

**Common Pitfalls:**
- **Too Fine-grained**: Excessive modules increase build complexity
- **Too Coarse-grained**: Large modules become monoliths
- **Circular Dependencies**: Modules depending on each other
- **Inconsistent Naming**: Unclear module purposes

**Best Practices:**
- Start with app and core modules
- Add feature modules as they grow
- Use clear dependency hierarchy
- Avoid circular dependencies
- Keep modules focused and cohesive

## Follow-ups

- How to handle shared dependencies between modules?
- What are the best practices for module communication?
- How to implement feature flags in modularized apps?

## References

- https://developer.android.com/topic/modularization
- https://developer.android.com/guide/playcore/feature-delivery

## Related Questions

### Prerequisites (Easier)
- [[q-android-architectural-patterns--android--medium]] - Architecture patterns
- [[q-gradle-build-system--android--medium]] - Build system basics

### Related (Medium)
- [[q-android-build-optimization--android--medium]] - Build optimization
- [[q-android-app-components--android--easy]] - App components
- [[q-android-jetpack-overview--android--easy]] - Jetpack libraries

### Advanced (Harder)
- q-android-dependency-injection--android--hard - Dependency injection
- [[q-android-testing-strategies--android--medium]] - Testing approaches