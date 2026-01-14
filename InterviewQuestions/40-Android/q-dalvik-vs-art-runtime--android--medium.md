---
id: android-442
title: Dalvik vs ART Runtime / Dalvik против ART Runtime
aliases:
- Dalvik vs ART Runtime
- Dalvik против ART Runtime
topic: android
subtopics:
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
- c-android-components
- q-android-runtime-art--android--medium
- q-how-to-create-dynamic-screens-at-runtime--android--hard
- q-runtime-permissions-best-practices--android--medium
created: 2025-10-20
updated: 2025-11-10
tags:
- android/performance-memory
- aot
- art
- compilation
- dalvik
- difficulty/medium
- jit
- runtime
anki_cards:
- slug: android-442-0-en
  language: en
  anki_id: 1768366747779
  synced_at: '2026-01-14T09:17:53.050256'
- slug: android-442-0-ru
  language: ru
  anki_id: 1768366747800
  synced_at: '2026-01-14T09:17:53.052078'
sources:
- https://developer.android.com/guide/practices/verifying-app-behavior-on-runtime
---
# Вопрос (RU)
> В чем различия между рантаймами Dalvik и ART в Android? Почему Android перешел с Dalvik на ART?

# Question (EN)
> What are the differences between Dalvik and ART runtimes in Android? Why did Android migrate from Dalvik to ART?

## Ответ (RU)

Dalvik и ART (Android Runtime) - это среды выполнения для Android приложений. ART окончательно заменил Dalvik начиная с Android 5.0 для улучшения производительности, отзывчивости и энергоэффективности, сохранив совместимость с DEX-байткодом.

### Ключевые Различия

**Dalvik (устаревший):**
- Основан на интерпретации DEX-байткода с JIT (Just-In-Time) компиляцией горячих участков во время выполнения
- Более медленный старт и выполнение по сравнению с ART из-за интерпретации и ограниченной оптимизации
- Более высокое среднее потребление CPU и батареи при нагрузке
- Меньше использование места на диске (нет полного AOT-кода), но накладные расходы JIT во время работы

**ART (текущий):**
- Использует компиляцию Ahead-of-Time (AOT), а в современных версиях Android — гибридный подход: AOT + JIT + profile-guided compilation (оптимизация на основе профилей выполнения)
- Выполняет высоко оптимизированный машинный код: часть кода компилируется при установке/обновлении, часть — JIT во время выполнения, с последующей перекомпиляцией на основе профилей
- Быстрый старт и более высокая производительность за счет готовых и/или оптимизированных компилированных путей
- Как правило, более низкое энергопотребление за счет меньшего объема интерпретации и более эффективного кода
- Использует больше места на диске под скомпилированный код (оптимизированные артефакты), в зависимости от политики компиляции, при этом уменьшая накладные расходы JIT во время работы
- Улучшенная и более предсказуемая сборка мусора (паузы короче и менее заметны)

### Архитектура Выполнения

```text
# Dalvik
APK → .dex bytecode → Интерпретатор + JIT Compiler (во время выполнения) → Execute

# ART (ранние версии, Android 5.x)
APK → .dex bytecode → AOT Compiler (dex2oat при установке) → Скомпилированный код → Execute

# ART (современный, упрощенно)
APK → .dex bytecode → Базовая компиляция (AOT) + JIT во время выполнения → Профили выполнения → Дополнительная AOT-оптимизация → Execute (быстрее и стабильнее)
```

### Производительность

| Характеристика | Dalvik | ART |
|----------------|--------|-----|
| Скорость выполнения | Обычно медленнее (интерпретация + ограниченный JIT) | Обычно быстрее (AOT + JIT + оптимизации) |
| Время запуска | Медленнее | Быстрее (больше кода уже оптимизировано) |
| Место на диске | Меньше (нет полноразмерного AOT-кода) | Больше (оптимизированный код хранится), зависит от политики компиляции |
| Использование RAM | Доп. накладные расходы под JIT-данные и интерпретацию | Более эффективное использование на практике, но зависит от конфигурации (не всегда строго ниже) |
| Потребление батареи | Выше при длительных нагрузках из-за интерпретации/JIT | Ниже за счет более эффективного кода и оптимизаций |

### Миграция

- Android 4.4 - ART доступен как опциональный (экспериментальный) рантайм
- Android 5.0+ - ART используется по умолчанию вместо Dalvik
- Сохранена полная совместимость с DEX-байткодом: большинство приложений не требовали изменений кода
- Миграция была в основном прозрачной для разработчиков; изменения касались главным образом инструментов и процессов оптимизации

## Answer (EN)

Dalvik and ART (Android Runtime) are execution environments for Android applications. ART fully replaced Dalvik starting from Android 5.0 to improve performance, responsiveness, and energy efficiency while retaining compatibility with DEX bytecode.

### Key Differences

**Dalvik (Legacy):**
- Based on interpreting DEX bytecode with JIT (Just-In-Time) compilation of hot paths at runtime
- Slower startup and execution compared to ART due to interpretation and limited optimizations
- Typically higher CPU and battery usage under load
- Uses less disk space (no full AOT-compiled code), but incurs runtime overhead for JIT

**ART (Current):**
- Uses Ahead-of-Time (AOT) compilation, and in modern Android versions a hybrid model: AOT + JIT + profile-guided compilation
- Executes highly optimized machine code: some compiled at install/update time, some JIT-compiled at runtime, then recompiled based on collected profiles
- Faster app startup and better overall performance due to pre-optimized and profiled code paths
- Generally lower battery consumption thanks to more efficient execution and reduced interpretation
- Consumes more disk space for compiled artifacts (optimized code stored), depending on compilation policy, while reducing some runtime JIT overhead
- Improved and more predictable garbage collection with shorter, less noticeable pauses

### Execution Architecture

```text
# Dalvik
APK → .dex bytecode → Interpreter + JIT Compiler (runtime) → Execute

# ART (early, Android 5.x)
APK → .dex bytecode → AOT Compiler (dex2oat at install time) → Compiled code → Execute

# ART (modern, simplified)
APK → .dex bytecode → Baseline AOT compilation + JIT at runtime → Execution profiles → Further AOT optimization → Execute (faster, more efficient)
```

### Performance Comparison

| Characteristic | Dalvik | ART |
|----------------|--------|-----|
| Execution speed | Typically slower (interpretation + limited JIT) | Typically faster (AOT + JIT + optimizations) |
| Startup time | Slower | Faster (more code already compiled/optimized) |
| Disk space | Less (no full AOT artifacts) | More (optimized code stored), policy-dependent |
| RAM usage | Overhead from interpreter/JIT structures | More efficient in practice, but depends on configuration (not always strictly lower) |
| Battery consumption | Higher under sustained workloads | Lower on average due to more efficient code |

### Migration Timeline

- Android 4.4 - ART available as an optional (experimental) runtime
- Android 5.0+ - ART enabled by default, replacing Dalvik
- Full backward compatibility with DEX bytecode; most apps required no source changes
- Migration was largely transparent to developers, with differences mainly in tooling and optimization behavior

## Дополнительные Вопросы (RU)

- Как в современных версиях Android работает гибридная компиляция ART (AOT + JIT + profile-guided)?
- Каковы компромиссы между местом на диске, временем установки и производительностью во время выполнения?
- Как компиляция dex2oat влияет на время установки и обновления приложения?
- Какие оптимизации применяет ART при AOT и компиляции на основе профилей выполнения?

## Follow-ups

- How does ART's hybrid compilation (AOT + JIT + profile-guided) work in modern Android versions?
- What are the trade-offs between disk space, installation time, and runtime performance?
- How does dex2oat compilation affect app installation and update time?
- What optimizations does ART apply during AOT and profile-guided compilation?

## Ссылки (RU)

- "https://source.android.com/docs/core/runtime"

## References

- https://source.android.com/docs/core/runtime

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-android-components]]

### Предпосылки
- Понимание виртуальных машин и выполнения байткода

### Связанные
- Механизмы сборки мусора в Android
- Формат и оптимизация DEX-байткода

### Продвинутое
- Профилируемая (profile-guided) компиляция в современном ART
- Оптимизация формата Compact DEX

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]

### Prerequisites
- Understanding of virtual machines and bytecode execution

### Related
- Android garbage collection mechanisms
- DEX bytecode format and optimization

### Advanced
- Profile-guided compilation in modern ART
- Compact DEX format optimization
