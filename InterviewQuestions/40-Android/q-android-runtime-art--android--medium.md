---
id: 20251012-122770
title: Android Runtime ART / Android Runtime ART
aliases: [Android Runtime ART, Android Runtime ART]
topic: android
subtopics: [performance, runtime, memory-management]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: reviewed
moc: moc-android
created: 2025-10-15
updated: 2025-10-15
tags: [android/performance, android/runtime, android/memory-management, runtime, art, dalvik, difficulty/medium]
related: [q-android-app-lag-analysis--android--medium, q-android-performance-measurement-tools--android--medium, q-android-build-optimization--android--medium]
---
# Question (EN)
> What is Runtime in Android context?

# Вопрос (RU)
> Что такое Runtime в контексте Android?

---

## Answer (EN)

**Android Runtime (ART)** is the execution environment for Android applications, responsible for running code, managing memory, and interacting with the operating system. ART replaced Dalvik VM from Android 5.0 and uses **AOT (Ahead-of-Time) compilation** for improved performance.

**Runtime Theory:**
Android Runtime provides a managed execution environment that abstracts hardware differences and provides memory management, garbage collection, and security isolation. It converts DEX bytecode to native machine code for optimal performance while maintaining portability across different Android devices.

**ART vs Dalvik:**
- **Dalvik**: JIT (Just-In-Time) compilation during execution
- **ART**: AOT (Ahead-of-Time) compilation at install time + JIT profiling since Android 7.0

**AOT Compilation Process:**
```
APK → DEX bytecode → AOT compilation → Native machine code
                    (at install time)
```

**Key ART Features:**
- **AOT Compilation**: Converts DEX to native code at install time
- **Improved Garbage Collection**: Concurrent copying GC with heap compaction
- **Better Performance**: Faster app startup and execution
- **Lower Battery Consumption**: No runtime compilation overhead
- **Hybrid Compilation**: AOT + JIT profiling for optimal performance

**Memory Management:**
```kotlin
class MemoryExample {
    fun createObjects() {
        val list = mutableListOf<String>()
        repeat(10000) {
            list.add("Object $it")
        }
        // ART automatically manages garbage collection
    }
}
```

**Garbage Collection Theory:**
ART uses a concurrent copying garbage collector that runs alongside the application, minimizing pause times. It performs heap compaction to reduce fragmentation and improve memory allocation efficiency.

**Class Loading:**
```kotlin
class MyActivity : AppCompatActivity() {
    // Classes loaded on-demand from DEX files
    private val helper by lazy { DatabaseHelper(this) }
}
```

**DEX Format:**
```
Java/Kotlin code → .class files → .dex files → ART execution
```

**DEX Theory:**
DEX (Dalvik Executable) format is optimized for mobile devices with smaller file sizes than Java bytecode. All classes are packaged in a single DEX file for efficient loading and execution.

**Hybrid Compilation (Android 7.0+):**
```
Install: Basic AOT compilation (fast)
         ↓
First runs: JIT compilation of "hot" code paths
         ↓
Background: Full AOT optimization
```

**Performance Optimization:**
```kotlin
class PerformanceExample {
    fun hotMethod() {
        // Frequently called - compiled to optimized native code
        processData()
    }

    fun coldMethod() {
        // Rarely called - may remain interpreted
        cleanup()
    }
}
```

**Security Features:**
- **Sandboxed Execution**: Each app runs in isolated environment
- **Process Isolation**: Apps run in separate processes
- **Permission System**: Controlled access to system resources

**Runtime Detection:**
```kotlin
fun checkRuntime() {
    val runtime = System.getProperty("java.vm.name")
    Log.d("Runtime", "VM: $runtime") // "ART" or "Dalvik"
}
```

**Key Differences:**
- **ART**: AOT compilation, better GC, faster execution, larger app size
- **Dalvik**: JIT compilation, simpler GC, slower execution, smaller app size

## Ответ (RU)

**Android Runtime (ART)** — это среда выполнения для Android приложений, отвечающая за выполнение кода, управление памятью и взаимодействие с операционной системой. ART заменил Dalvik VM начиная с Android 5.0 и использует **AOT (Ahead-of-Time) компиляцию** для улучшенной производительности.

**Теория Runtime:**
Android Runtime предоставляет управляемую среду выполнения, которая абстрагирует различия в оборудовании и обеспечивает управление памятью, сборку мусора и изоляцию безопасности. Он конвертирует DEX байт-код в нативный машинный код для оптимальной производительности при сохранении переносимости между различными Android устройствами.

**ART vs Dalvik:**
- **Dalvik**: JIT (Just-In-Time) компиляция во время выполнения
- **ART**: AOT (Ahead-of-Time) компиляция при установке + JIT профилирование с Android 7.0

**Процесс AOT компиляции:**
```
APK → DEX байт-код → AOT компиляция → Нативный машинный код
                    (при установке)
```

**Ключевые особенности ART:**
- **AOT компиляция**: Конвертирует DEX в нативный код при установке
- **Улучшенная сборка мусора**: Concurrent copying GC с компактификацией кучи
- **Лучшая производительность**: Быстрый запуск и выполнение приложений
- **Меньшее энергопотребление**: Нет накладных расходов на компиляцию во время выполнения
- **Гибридная компиляция**: AOT + JIT профилирование для оптимальной производительности

**Управление памятью:**
```kotlin
class MemoryExample {
    fun createObjects() {
        val list = mutableListOf<String>()
        repeat(10000) {
            list.add("Object $it")
        }
        // ART автоматически управляет сборкой мусора
    }
}
```

**Теория сборки мусора:**
ART использует concurrent copying сборщик мусора, который работает параллельно с приложением, минимизируя время пауз. Он выполняет компактификацию кучи для уменьшения фрагментации и улучшения эффективности выделения памяти.

**Загрузка классов:**
```kotlin
class MyActivity : AppCompatActivity() {
    // Классы загружаются по требованию из DEX файлов
    private val helper by lazy { DatabaseHelper(this) }
}
```

**DEX формат:**
```
Java/Kotlin код → .class файлы → .dex файлы → Выполнение ART
```

**Теория DEX:**
DEX (Dalvik Executable) формат оптимизирован для мобильных устройств с меньшим размером файлов по сравнению с Java байт-кодом. Все классы упакованы в один DEX файл для эффективной загрузки и выполнения.

**Гибридная компиляция (Android 7.0+):**
```
Установка: Базовая AOT компиляция (быстро)
           ↓
Первые запуски: JIT компиляция "горячих" участков кода
           ↓
Фоновая оптимизация: Полная AOT оптимизация
```

**Оптимизация производительности:**
```kotlin
class PerformanceExample {
    fun hotMethod() {
        // Часто вызываемый - компилируется в оптимизированный нативный код
        processData()
    }

    fun coldMethod() {
        // Редко вызываемый - может оставаться интерпретируемым
        cleanup()
    }
}
```

**Функции безопасности:**
- **Изолированное выполнение**: Каждое приложение работает в изолированной среде
- **Изоляция процессов**: Приложения работают в отдельных процессах
- **Система разрешений**: Контролируемый доступ к системным ресурсам

**Определение Runtime:**
```kotlin
fun checkRuntime() {
    val runtime = System.getProperty("java.vm.name")
    Log.d("Runtime", "VM: $runtime") // "ART" или "Dalvik"
}
```

**Ключевые различия:**
- **ART**: AOT компиляция, лучшая GC, быстрое выполнение, больший размер приложения
- **Dalvik**: JIT компиляция, простая GC, медленное выполнение, меньший размер приложения

---

## Follow-ups

- How does ART's garbage collection differ from Dalvik's approach?
- What are the performance implications of AOT vs JIT compilation?
- How does hybrid compilation work in modern Android versions?

## References

- https://developer.android.com/guide/practices/verifying-app-behavior-on-runtime
- https://source.android.com/docs/core/runtime

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-android-manifest-file--android--easy]] - App configuration

### Related (Medium)
- [[q-android-app-lag-analysis--android--medium]] - Performance analysis
- [[q-android-performance-measurement-tools--android--medium]] - Performance tools
- [[q-android-build-optimization--android--medium]] - Build optimization

### Advanced (Harder)
- [[q-android-architectural-patterns--android--medium]] - Architecture patterns
