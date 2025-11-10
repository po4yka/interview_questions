---
id: android-483
title: 16kb Dex Page Size / Размер страницы DEX 16KB
aliases: [16 КБ страница DEX, 16KB DEX Page Size]
topic: android
subtopics:
  - gradle
  - performance-memory
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-app-bundle
  - c-gradle
  - q-android-app-bundles--android--easy
  - q-build-optimization-gradle--android--medium
  - q-proguard-r8--android--medium
created: 2025-10-25
updated: 2025-10-29
sources: []
tags: [android/gradle, android/performance-memory, difficulty/medium]
---

# Вопрос (RU)
> Что такое проблема размера страницы DEX 16KB в Android?

---

# Question (EN)
> What is the 16KB DEX page size issue in Android?

---

## Ответ (RU)

Проблема «16KB DEX page size» относится к тому, как DEX-код и связанные данные выравниваются и отображаются страницами памяти (обычно 16 КБ) в рантайме ART на некоторых версиях Android. Определённые варианты раскладки DEX могут приводить к неэффективному использованию 16 КБ страниц и, как следствие, к заметному росту размера установочного артефакта и к большему объёму загружаемых данных.

Это не баг R8/ProGuard как таковых, а эффект того, как их оптимизации (переупаковка, переупорядочивание, уменьшение числа методов/классов) взаимодействуют с 16 КБ выравниванием секций/страниц.

**Причина (упрощённо)**: при загрузке и оптимизации DEX рантайм использует страницы фиксированного размера (16 КБ). Если данные (классы, методы, таблицы индексов и др.) размещены так, что границы страниц попадают в «неудачные» места, часть пространства на странице остаётся неиспользованной, а следующий блок данных переносится на новую страницу. При определённом расположении и количестве методов это может накопить значительное количество «пустого» пространства.

Условная иллюстрация:

```
Оптимально:      [Data A.......][Data B.......]
Неоптимально:    [Data A..padding][Data B......]
                             ^^^^^ Потерянное место
```

**Влияние (типично, не гарантированно)**:
- Малые приложения (< 5 MB): рост размера может достигать ~20–40%
- Большие приложения (> 50 MB): увеличение обычно меньше, порядка нескольких–десяти процентов

Фактический эффект зависит от структуры DEX, порядка методов/классов и конфигурации сборки.

**Решение / смягчение**:

- Использовать актуальные версии Android Gradle Plugin (AGP), D8 и R8, в которых реализованы улучшения раскладки DEX и упаковки.
- Включить минификацию и шринк ресурсов для релизных сборок, но отслеживать реальные размеры артефактов, так как изменения порядка/количества элементов могут как уменьшить, так и увеличить потери на выравнивании.

Пример базовой конфигурации:

```kotlin
plugins {
    id("com.android.application") version "8.2+" // пример актуальной версии; используйте свежий AGP
}

android {
    buildTypes {
        release {
            isMinifyEnabled = true          // Включает R8 (AGP 3.4+ по умолчанию вместо ProGuard)
            isShrinkResources = true        // Дополнительное уменьшение размера APK/AAB
        }
    }
}
```

**Лучшие практики**:
- Использовать App Bundle вместо монолитного APK, чтобы уменьшить итоговый размер загружаемого пользователю пакета.
- Мониторить размер DEX и финальных артефактов в CI/CD и сравнивать сборки при изменении конфигурации R8/AGP.

---

## Answer (EN)

The "16KB DEX page size" issue refers to how DEX code and related data are laid out and mapped into memory using fixed-size pages (commonly 16 KB) by the ART runtime on some Android versions. Certain DEX layouts can lead to inefficient use of these 16 KB pages, causing noticeable increases in installable artifact size and the amount of data that must be loaded.

This is not a bug in R8/ProGuard themselves. Instead, their optimizations (repackaging, reordering, shrinking methods/classes) can interact with 16 KB page alignment of sections/pages in a way that exposes or worsens padding overhead.

**Cause (simplified)**: when DEX files are loaded/optimized, the runtime works with fixed-size memory pages (e.g., 16 KB). If sections of the DEX (classes, methods, index tables, etc.) are arranged such that page boundaries cut through them unfavorably, part of a page can remain unused while the next section is pushed onto a new page. Depending on method/class counts and ordering, this accumulated padding can become significant.

Illustrative view:

```
Optimal:       [Data A.......][Data B.......]
Suboptimal:    [Data A..padding][Data B......]
                          ^^^^^ Wasted space
```

**Impact (typical, not guaranteed)**:
- Small apps (< 5 MB): size increase can reach roughly ~20–40%
- Large apps (> 50 MB): increases are usually smaller, on the order of several to low tens of percent

The actual impact depends on DEX structure, method/class ordering, and build configuration.

**Mitigation / solution**:

- Use up-to-date versions of the Android Gradle Plugin (AGP), D8, and R8, which include improvements to DEX layout and packing.
- Enable code shrinking and resource shrinking for release builds, while monitoring resulting artifact sizes, since changes in ordering/counts can either reduce or, in some edge cases, increase alignment-related padding.

Example baseline configuration:

```kotlin
plugins {
    id("com.android.application") version "8.2+" // example of a recent AGP; prefer latest stable
}

android {
    buildTypes {
        release {
            isMinifyEnabled = true          // Enables R8 (default instead of ProGuard in AGP 3.4+)
            isShrinkResources = true        // Further reduces APK/AAB size
        }
    }
}
```

**Best practices**:
- Use App Bundles instead of a single universal APK to reduce what each user downloads.
- Track DEX and artifact sizes in CI/CD and compare builds when changing R8/AGP configurations.

---

## Follow-ups

- How do App Bundles mitigate this issue?
- What's the difference between R8 and ProGuard handling?
- How to detect alignment issues in CI/CD?
- Why does R8 optimization sometimes increase APK size?
- How does dex page alignment affect cold start performance?

## References

- [[c-gradle]] - Build system
- [[c-app-bundle]] - App distribution format
- [R8 Optimization](https://developer.android.com/studio/build/shrink-code)
- [App Bundle Guide](https://developer.android.com/guide/app-bundle)
- [DEX Format Specification](https://source.android.com/docs/core/runtime/dex-format)

## Related Questions

### Prerequisites (Easy)
- [[q-gradle-basics--android--easy]]
- [[q-android-app-bundles--android--easy]]

### Related (Medium)
- [[q-proguard-r8--android--medium]]
- [[q-build-optimization-gradle--android--medium]]
- [[q-gradle-build-system--android--medium]]

### Advanced (Hard)
- APK size analysis and optimization strategies
- Custom R8 rules for extreme size reduction
