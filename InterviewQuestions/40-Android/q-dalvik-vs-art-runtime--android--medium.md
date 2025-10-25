---
id: 20251020-200000
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
- q-android-performance-optimization--android--medium
- q-app-startup-time--android--medium
- q-android-memory-management--android--hard
created: 2025-10-20
updated: 2025-10-20
tags:
- android/performance-memory
- dalvik
- art
- runtime
- jit
- aot
- compilation
- difficulty/medium
source: https://developer.android.com/guide/practices/verifying-app-behavior-on-runtime
source_note: Android Runtime documentation
---

# Вопрос (RU)
> В чем различия между рантаймами Dalvik и ART в Android? Почему Android перешел с Dalvik на ART?

# Question (EN)
> What are the differences between Dalvik and ART runtimes in Android? Why did Android migrate from Dalvik to ART?

## Ответ (RU)

Dalvik и ART (Android Runtime) - это среды выполнения для запуска Android приложений. ART заменил Dalvik начиная с Android 5.0 (Lollipop) для улучшения производительности, времени работы батареи и опыта разработчиков.

### Теория: Архитектурные различия

**Основные концепции:**
- **Dalvik** - интерпретируемая виртуальная машина с JIT компиляцией
- **ART** - Ahead-of-Time (AOT) компиляция с оптимизациями
- **JIT vs AOT** - время компиляции и оптимизации
- **Производительность** - скорость выполнения и потребление ресурсов
- **Память** - использование RAM и место на диске

**Принципы работы:**
- Dalvik интерпретирует байт-код во время выполнения
- ART компилирует байт-код в машинный код при установке
- AOT компиляция позволяет более агрессивные оптимизации
- JIT компиляция адаптируется к паттернам использования

### 1. Dalvik Virtual Machine (Legacy)

**Архитектура Dalvik:**
```
APK Installation:
  .apk file → Extract .dex files → Store on device
                                   (Dalvik bytecode)

App Execution:
  Launch app → JIT Compiler → Machine code → Execute
              (Just-In-Time)  (at runtime)
```

**Характеристики Dalvik:**
- **JIT компиляция** - компиляция во время выполнения
- **Интерпретация** - выполнение байт-кода через интерпретатор
- **Медленный старт** - компиляция при каждом запуске
- **Адаптивная оптимизация** - оптимизация на основе использования

**Проблемы Dalvik:**
- Низкая производительность из-за интерпретации
- Высокое потребление батареи
- Медленный старт приложений
- Ограниченные возможности оптимизации

### 2. ART Runtime (Current)

**Архитектура ART:**
```
APK Installation:
  .apk file → Extract .dex files → AOT Compiler → Native code
                                   (Ahead-of-Time)   (stored on device)

App Execution:
  Launch app → Load native code → Execute (FAST)
```

**Характеристики ART:**
- **AOT компиляция** - компиляция при установке
- **Нативный код** - выполнение скомпилированного машинного кода
- **Быстрый старт** - готовый к выполнению код
- **Агрессивные оптимизации** - оптимизация на этапе компиляции

**Преимущества ART:**
- Высокая производительность выполнения
- Низкое потребление батареи
- Быстрый старт приложений
- Улучшенная сборка мусора

### 3. Сравнение производительности

**Время выполнения:**
- **Dalvik**: Медленное из-за интерпретации
- **ART**: Быстрое из-за нативного кода

**Время запуска:**
- **Dalvik**: Медленный старт, JIT компиляция
- **ART**: Быстрый старт, готовый код

**Потребление памяти:**
- **Dalvik**: Меньше места на диске, больше RAM
- **ART**: Больше места на диске, меньше RAM

**Потребление батареи:**
- **Dalvik**: Высокое из-за постоянной компиляции
- **ART**: Низкое из-за предварительной компиляции

### 4. Технические детали

**Dalvik особенности:**
- Регистровая виртуальная машина
- 16 регистров для локальных переменных
- JIT компиляция с профилированием
- Адаптивная оптимизация

**ART особенности:**
- AOT компиляция при установке
- Оптимизация на основе статического анализа
- Улучшенная сборка мусора
- Поддержка 64-битных архитектур

### 5. Миграция и совместимость

**Переход на ART:**
- Android 4.4 (KitKat) - опциональный ART
- Android 5.0 (Lollipop) - ART по умолчанию
- Обратная совместимость с Dalvik байт-кодом

**Совместимость:**
- Тот же DEX байт-код
- Те же API и библиотеки
- Прозрачная миграция для разработчиков

## Answer (EN)

Dalvik and ART (Android Runtime) are execution environments for running Android applications. ART replaced Dalvik starting from Android 5.0 (Lollipop) to improve performance, battery life, and developer experience.

### Theory: Architectural Differences

**Core Concepts:**
- **Dalvik** - interpreted virtual machine with JIT compilation
- **ART** - Ahead-of-Time (AOT) compilation with optimizations
- **JIT vs AOT** - compilation timing and optimizations
- **Performance** - execution speed and resource consumption
- **Memory** - RAM usage and disk space

**Working Principles:**
- Dalvik interprets bytecode at runtime
- ART compiles bytecode to machine code at installation
- AOT compilation allows more aggressive optimizations
- JIT compilation adapts to usage patterns

### 1. Dalvik Virtual Machine (Legacy)

**Dalvik Architecture:**
```
APK Installation:
  .apk file → Extract .dex files → Store on device
                                   (Dalvik bytecode)

App Execution:
  Launch app → JIT Compiler → Machine code → Execute
              (Just-In-Time)  (at runtime)
```

**Dalvik Characteristics:**
- **JIT compilation** - compilation at runtime
- **Interpretation** - bytecode execution through interpreter
- **Slow startup** - compilation on every launch
- **Adaptive optimization** - optimization based on usage

**Dalvik Problems:**
- Low performance due to interpretation
- High battery consumption
- Slow app startup
- Limited optimization opportunities

### 2. ART Runtime (Current)

**ART Architecture:**
```
APK Installation:
  .apk file → Extract .dex files → AOT Compiler → Native code
                                   (Ahead-of-Time)   (stored on device)

App Execution:
  Launch app → Load native code → Execute (FAST)
```

**ART Characteristics:**
- **AOT compilation** - compilation at installation
- **Native code** - execution of compiled machine code
- **Fast startup** - ready-to-execute code
- **Aggressive optimizations** - optimization at compilation time

**ART Benefits:**
- High execution performance
- Low battery consumption
- Fast app startup
- Improved garbage collection

### 3. Performance Comparison

**Execution Time:**
- **Dalvik**: Slow due to interpretation
- **ART**: Fast due to native code

**Startup Time:**
- **Dalvik**: Slow startup, JIT compilation
- **ART**: Fast startup, ready code

**Memory Usage:**
- **Dalvik**: Less disk space, more RAM
- **ART**: More disk space, less RAM

**Battery Consumption:**
- **Dalvik**: High due to constant compilation
- **ART**: Low due to pre-compilation

### 4. Technical Details

**Dalvik Features:**
- Register-based virtual machine
- 16 registers for local variables
- JIT compilation with profiling
- Adaptive optimization

**ART Features:**
- AOT compilation at installation
- Optimization based on static analysis
- Improved garbage collection
- 64-bit architecture support

### 5. Migration and Compatibility

**Transition to ART:**
- Android 4.4 (KitKat) - optional ART
- Android 5.0 (Lollipop) - ART by default
- Backward compatibility with Dalvik bytecode

**Compatibility:**
- Same DEX bytecode
- Same APIs and libraries
- Transparent migration for developers

**See also:** c-jvm, c-virtual-machine


## Follow-ups

- How does ART's garbage collection differ from Dalvik's?
- What are the memory implications of AOT compilation?
- How does ART handle app updates and recompilation?
