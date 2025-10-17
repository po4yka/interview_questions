---
id: "20251015082237464"
title: "Android Runtime Art"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [runtime, art, dalvik, difficulty/medium]
---
# Что такое Runtime в контексте Android?

# Question (EN)
> What is Runtime in Android context?

# Вопрос (RU)
> Что такое Runtime в контексте Android?

---

## Answer (EN)

Android Runtime (ART) is the execution environment for Android apps. It replaced Dalvik VM from Android 5.0. ART uses **AOT (Ahead-of-Time) compilation** converting DEX bytecode to native code at install time, improving performance. Key features: improved GC, better debugging, optimized app startup.

**Dalvik vs ART**: Dalvik used JIT (Just-In-Time), ART uses AOT + JIT hybrid since Android 7.0 for optimal performance and install time balance.

---

## Ответ (RU)

Runtime в контексте Android — это среда выполнения приложений, которая отвечает за выполнение кода, управление памятью и взаимодействие с операционной системой.

### Android Runtime (ART)

**ART** (Android Runtime) — текущая среда выполнения в Android (с версии 5.0 Lollipop).

#### Основные функции

**1. Исполнение кода**

ART использует **AOT (Ahead-Of-Time) компиляцию** — код компилируется в машинный код при установке приложения.

```
APK → DEX bytecode → AOT компиляция → Native code
                    (при установке)
```

**Преимущества AOT:**
- Быстрый запуск приложения
- Лучшая производительность
- Меньше энергопотребления
- Не нужна JIT компиляция во время выполнения

**2. Управление памятью**

Улучшенная система сборки мусора (Garbage Collection):

```kotlin
class MemoryExample {
    fun createObjects() {
        val list = mutableListOf<String>()
        repeat(10000) {
            list.add("Object $it")
        }
        // ART автоматически очистит неиспользуемые объекты
    }
}
```

**Особенности GC в ART:**
- Более эффективная сборка мусора
- Меньше пауз в работе приложения
- Concurrent копирующий GC
- Компактификация памяти (heap compaction)

**3. Загрузка классов**

Классы загружаются из `.dex` файлов по мере необходимости.

```kotlin
// Lazy loading классов
class MyActivity : AppCompatActivity() {
    // Класс загружается только при первом использовании
    private val helper by lazy { DatabaseHelper(this) }
}
```

**4. Безопасность**

- Изолированная среда выполнения (sandbox)
- Каждое приложение в отдельном процессе
- Система разрешений

**5. Обработка исключений**

```kotlin
try {
    riskyOperation()
} catch (e: Exception) {
    // ART перехватывает и обрабатывает исключения
    Log.e("TAG", "Error", e)
}
```

### ART vs Dalvik

| Аспект | Dalvik (старый) | ART (текущий) |
|--------|-----------------|---------------|
| **Компиляция** | JIT (Just-In-Time) | AOT (Ahead-Of-Time) + JIT |
| **Установка** | Быстрая | Медленнее (компиляция) |
| **Запуск приложения** | Медленнее | Быстрее |
| **Производительность** | Хорошая | Отличная |
| **Размер кода** | Меньше | Больше (native code) |
| **Энергопотребление** | Выше | Ниже |
| **GC** | Простой | Улучшенный |

### Dalvik Virtual Machine (устаревшая)

Использовалась до Android 5.0.

```
APK → DEX bytecode → JIT компиляция → Выполнение
                     (во время работы)
```

**Проблемы Dalvik:**
- JIT компиляция во время выполнения замедляла приложение
- Больше энергопотребления
- Медленная сборка мусора с длительными паузами

### Гибридная компиляция в современном ART

С Android 7.0 (Nougat) ART использует **гибридный подход**:

```
Установка: Базовая AOT компиляция (быстрая)
            ↓
Первые запуски: JIT компиляция "горячих" участков кода
            ↓
Фоновая оптимизация: Полная AOT компиляция
```

**Преимущества:**
- Быстрая установка приложений
- Быстрый первый запуск
- Оптимизация производительности со временем

### Работа с памятью в ART

```kotlin
class MemoryManagement {
    // Объекты в куче (heap)
    private val largeList = mutableListOf<ByteArray>()

    fun allocateMemory() {
        // ART выделяет память в куче
        val data = ByteArray(1024 * 1024) // 1 MB
        largeList.add(data)

        // Когда largeList больше не используется,
        // GC автоматически освободит память
    }

    fun triggerGC() {
        // Явный вызов GC (не рекомендуется!)
        System.gc()
        // ART сам управляет сборкой мусора
    }
}
```

### DEX формат

**DEX** (Dalvik Executable) — формат байткода для Android.

```
Java/Kotlin код → .class файлы → .dex файлы
                                  ↓
                              ART выполняет
```

**Особенности DEX:**
- Оптимизирован для мобильных устройств
- Меньший размер, чем Java bytecode
- Все классы в одном файле

```bash

# Просмотр .dex файла в APK
unzip app.apk
ls -lh classes.dex
```

### Профилирование и оптимизация

```kotlin
class PerformanceOptimization {
    // ART использует профилирование для оптимизации
    fun hotMethod() {
        // Часто вызываемый метод
        // ART скомпилирует в оптимизированный native код
    }

    fun coldMethod() {
        // Редко вызываемый метод
        // Может оставаться в интерпретируемом виде
    }
}
```

### Практические аспекты

**1. Размер приложения**

```kotlin
// ART сохраняет скомпилированный код
// Приложение на устройстве занимает больше места

// В AndroidManifest.xml можно указать:
android:extractNativeLibs="false"  // Уменьшить размер
```

**2. Производительность**

```kotlin
// Оптимизация для ART
class Optimized {
    // Избегайте создания объектов в циклах
    fun processData(items: List<String>) {
        val result = StringBuilder()  // Переиспользуем объект
        for (item in items) {
            result.append(item)
        }
    }
}
```

**3. Debugging**

```kotlin
// ART поддерживает JDWP для отладки
// Android Studio подключается к ART через ADB
```

### Проверка Runtime

```kotlin
fun checkRuntime() {
    val runtime = System.getProperty("java.vm.name")
    Log.d("Runtime", "VM: $runtime")
    // Output: "Dalvik" или "ART"
}
```

**English**: Android Runtime (ART) is the execution environment responsible for running apps, managing memory, and interacting with OS. Uses AOT (Ahead-Of-Time) compilation for better performance vs old Dalvik's JIT. Features improved garbage collection, faster app launch, lower battery consumption, and hybrid compilation (AOT + JIT profiling). Loads classes from DEX files and provides sandboxed execution environment.
