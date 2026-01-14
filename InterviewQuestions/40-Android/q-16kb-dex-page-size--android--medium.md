---
id: android-483
title: 16kb Dex Page Size / Размер страницы DEX 16KB
aliases:
- 16 КБ страница DEX
- 16KB DEX Page Size
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
status: draft
moc: moc-android
related:
- c-app-bundle
- c-gradle
- q-android-app-bundles--android--easy
- q-app-size-optimization--android--medium
- q-build-optimization-gradle--android--medium
- q-dagger-build-time-optimization--android--medium
- q-proguard-r8--android--medium
- q-reduce-apk-size-techniques--android--medium
created: 2025-10-25
updated: 2025-10-29
sources: []
tags:
- android/gradle
- android/performance-memory
- difficulty/medium
anki_cards:
- slug: android-483-0-en
  language: en
  anki_id: 1768363328621
  synced_at: '2026-01-14T09:17:53.378757'
- slug: android-483-0-ru
  language: ru
  anki_id: 1768363328646
  synced_at: '2026-01-14T09:17:53.381460'
---
# Вопрос (RU)
> Что такое проблема размера страницы DEX 16KB в Android?

---

# Question (EN)
> What is the 16KB DEX page size issue in Android?

---

## Ответ (RU)

Проблема «16KB DEX page size» относится к тому, как DEX-код и связанные данные выравниваются и отображаются страницами памяти (на некоторых версиях Android — с эффективным размером страницы 16 КБ) в рантайме ART и связанных форматах (например, oat/odex). Определённые варианты раскладки DEX могут приводить к неэффективному использованию этих страниц и, как следствие, к заметному росту размера установочного артефакта и к большему объёму загружаемых данных.

Это не баг R8/ProGuard как таковых, а эффект того, как их оптимизации (переупаковка, переупорядочивание, уменьшение числа методов/классов) взаимодействуют с выравниванием секций/страниц под 16 КБ.

**Причина (упрощённо)**: при отображении и оптимизации DEX рантайм и формат oat используют страницы фиксированного размера (например, 16 КБ на части устройств/версий). Если данные (классы, методы, таблицы индексов и др.) размещены так, что границы страниц попадают в «неудачные» места, часть пространства на странице остаётся неиспользованной, а следующий блок данных переносится на новую страницу. При определённом расположении и количестве методов это может накопить значительное количество «пустого» пространства.

Условная иллюстрация:

```text
Оптимально:      [Data A.......][Data B.......]
Неоптимально:    [Data A..padding][Data B......]
                             ^^^^^ Потерянное место
```

**Влияние (типично, не гарантированно)**:
- Малые приложения (< 5 MB): рост размера может достигать ~20–40%
- Большие приложения (> 50 MB): увеличение обычно меньше, порядка нескольких–десяти процентов

Фактический эффект зависит от структуры DEX, порядка методов/классов, конфигурации сборки и конкретной среды выполнения.

**Решение / смягчение**:

- Использовать актуальные версии Android Gradle Plugin (AGP), D8 и R8, в которых реализованы улучшения раскладки DEX и упаковки.
- Включить минификацию и шринк ресурсов для релизных сборок, но обязательно отслеживать реальные размеры артефактов: изменения порядка/количества элементов могут как уменьшить, так и увеличить потери на выравнивании.
- Сравнивать размеры и содержимое DEX/APK/AAB между сборками (включая отчёты AGP/R8 по размерам), чтобы обнаружить аномальный рост из-за неэффективного выравнивания.

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
- Использовать App `Bundle` вместо монолитного APK, чтобы уменьшить итоговый размер загружаемого пользователю пакета.
- Мониторить размер DEX и финальных артефактов в CI/CD и сравнивать сборки при изменении конфигурации R8/AGP, чтобы вовремя заметить регрессии, связанные с выравниванием.

---

## Answer (EN)

The "16KB DEX page size" issue refers to how DEX code and related data are laid out and memory-mapped using fixed-size pages (on some Android versions/environments effectively 16 KB) by the ART runtime and related formats (such as oat/odex). Certain DEX layouts can cause inefficient use of these pages, leading to noticeable increases in the installable artifact size and the amount of data that must be loaded.

This is not a bug in R8/ProGuard themselves. Instead, their optimizations (repackaging, reordering, shrinking methods/classes) can interact with 16 KB-aligned sections/pages in ways that expose or worsen padding overhead.

**Cause (simplified)**: when DEX files are mapped/optimized, the runtime and oat format operate on fixed-size memory pages (e.g., 16 KB on some devices/versions). If DEX sections (classes, methods, index tables, etc.) are arranged so that page boundaries cut through them unfavorably, part of a page ends up unused while the next section is pushed onto a new page. Depending on method/class counts and ordering, this accumulated padding can become significant.

Illustrative view:

```text
Optimal:       [Data A.......][Data B.......]
Suboptimal:    [Data A..padding][Data B......]
                          ^^^^^ Wasted space
```

**Impact (typical, not guaranteed)**:
- Small apps (< 5 MB): size increase can reach roughly ~20–40%
- Large apps (> 50 MB): increases are usually smaller, on the order of several to low tens of percent

The actual impact depends on the DEX structure, method/class ordering, build configuration, and the specific runtime environment.

**Mitigation / solution**:

- Use up-to-date versions of the Android Gradle Plugin (AGP), D8, and R8, which include improvements to DEX layout and packing.
- Enable code shrinking and resource shrinking for release builds, but always monitor resulting artifact sizes: changes in ordering/counts can either reduce or, in some edge cases, increase alignment-related padding.
- Compare DEX/APK/AAB sizes and contents between builds (including AGP/R8 size reports) to detect abnormal growth caused by inefficient alignment.

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
- Track DEX and artifact sizes in CI/CD and compare builds when changing R8/AGP configurations so alignment-related regressions are caught early.

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
- [App `Bundle` Guide](https://developer.android.com/guide/app-bundle)
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
