---
id: android-442
title: Dalvik vs ART Runtime / Dalvik против ART Runtime
aliases: ["Dalvik vs ART Runtime", "Dalvik против ART Runtime"]
topic: android
subtopics: [performance-memory]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
created: 2025-10-20
updated: 2025-01-27
tags: [android/performance-memory, aot, art, compilation, dalvik, difficulty/medium, jit, runtime]
sources: [https://developer.android.com/guide/practices/verifying-app-behavior-on-runtime]
date created: Monday, October 27th 2025, 3:46:58 pm
date modified: Thursday, October 30th 2025, 12:47:32 pm
---

# Вопрос (RU)
> В чем различия между рантаймами Dalvik и ART в Android? Почему Android перешел с Dalvik на ART?

# Question (EN)
> What are the differences between Dalvik and ART runtimes in Android? Why did Android migrate from Dalvik to ART?

## Ответ (RU)

Dalvik и ART (Android Runtime) - это среды выполнения для Android приложений. ART заменил Dalvik начиная с Android 5.0 для улучшения производительности и энергоэффективности.

### Ключевые различия

**Dalvik (устаревший):**
- JIT (Just-In-Time) компиляция во время выполнения
- Интерпретация байт-кода с постоянной компиляцией горячих участков
- Медленный старт приложений из-за компиляции при каждом запуске
- Высокое потребление CPU и батареи
- Меньше места на диске, больше использования RAM

**ART (текущий):**
- AOT (Ahead-of-Time) компиляция при установке приложения
- Выполнение скомпилированного машинного кода
- Быстрый старт приложений - код готов к выполнению
- Низкое потребление батареи
- Больше места на диске, эффективное использование RAM
- Улучшенная сборка мусора

### Архитектура выполнения

```text
# ❌ Dalvik - компиляция при каждом запуске
APK → .dex bytecode → JIT Compiler (runtime) → Execute

# ✅ ART - компиляция один раз при установке
APK → .dex bytecode → AOT Compiler (install) → Native code → Execute (fast)
```

### Производительность

| Характеристика | Dalvik | ART |
|----------------|--------|-----|
| Скорость выполнения | Медленнее (интерпретация) | Быстрее (нативный код) |
| Время запуска | Медленное (JIT компиляция) | Быстрое (готовый код) |
| Место на диске | Меньше | Больше |
| Использование RAM | Больше (runtime компиляция) | Меньше |
| Потребление батареи | Высокое | Низкое |

### Миграция

- Android 4.4 - ART опционально (экспериментально)
- Android 5.0+ - ART по умолчанию
- Полная обратная совместимость с DEX байт-кодом
- Прозрачная миграция для разработчиков

## Answer (EN)

Dalvik and ART (Android Runtime) are execution environments for Android applications. ART replaced Dalvik starting from Android 5.0 to improve performance and energy efficiency.

### Key Differences

**Dalvik (Legacy):**
- JIT (Just-In-Time) compilation at runtime
- Interprets bytecode with continuous compilation of hot paths
- Slow app startup due to compilation on every launch
- High CPU and battery consumption
- Less disk space, higher RAM usage

**ART (Current):**
- AOT (Ahead-of-Time) compilation at app installation
- Executes compiled machine code
- Fast app startup - code ready to run
- Low battery consumption
- More disk space, efficient RAM usage
- Improved garbage collection

### Execution Architecture

```text
# ❌ Dalvik - compiles on every launch
APK → .dex bytecode → JIT Compiler (runtime) → Execute

# ✅ ART - compiles once at installation
APK → .dex bytecode → AOT Compiler (install) → Native code → Execute (fast)
```

### Performance Comparison

| Characteristic | Dalvik | ART |
|----------------|--------|-----|
| Execution speed | Slower (interpretation) | Faster (native code) |
| Startup time | Slow (JIT compilation) | Fast (ready code) |
| Disk space | Less | More |
| RAM usage | Higher (runtime compilation) | Lower |
| Battery consumption | High | Low |

### Migration Timeline

- Android 4.4 - ART optional (experimental)
- Android 5.0+ - ART by default
- Full backward compatibility with DEX bytecode
- Transparent migration for developers

## Follow-ups

- How does ART's hybrid compilation (AOT + JIT) work in modern Android versions?
- What are the trade-offs between disk space and runtime performance?
- How does dex2oat compilation affect app installation time?
- What optimizations does ART apply during AOT compilation?

## References

- https://source.android.com/docs/core/runtime

## Related Questions

### Prerequisites
- Understanding of virtual machines and bytecode execution

### Related
- Android garbage collection mechanisms
- DEX bytecode format and optimization

### Advanced
- Profile-guided compilation in modern ART
- Compact DEX format optimization
