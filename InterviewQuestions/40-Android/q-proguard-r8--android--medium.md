---
id: android-001
title: ProGuard and R8 / ProGuard и R8
aliases: [ProGuard and R8, ProGuard и R8]
topic: android
subtopics:
  - gradle
  - obfuscation
  - performance-memory
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
sources:
  - "https://github.com/Kirchhoff-Android-Interview-Questions"
status: draft
moc: moc-android
related:
  - c-gradle
  - c-memory-management
  - q-build-optimization-gradle--android--medium
  - q-dagger-build-time-optimization--android--medium
  - q-data-sync-unstable-network--android--hard
  - q-proguard-r8-rules--android--medium
  - q-reduce-app-size--android--medium
created: 2025-10-05
updated: 2025-11-10
tags: [android/gradle, android/obfuscation, android/performance-memory, difficulty/medium]
date created: Saturday, November 1st 2025, 12:47:01 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---
# Вопрос (RU)
> Что такое ProGuard и R8?

# Question (EN)
> What are ProGuard and R8?

---

## Ответ (RU)

**ProGuard** — более старый инструмент для минификации и обфускации Java/Android-кода. В Android он использовался для:
- удаления неиспользуемого кода (code shrinking),
- обфускации (переименования) классов и методов,
- простой оптимизации байткода.

**R8** — современный компилятор/шринкер, встроенный в Android Gradle Plugin и являющийся shrinker'ом по умолчанию (заменяет ProGuard в стандартном Android-пайплайне, но использует совместимый синтаксис правил). Выполняет четыре ключевые задачи во время сборки:

1. **Сжатие кода (code shrinking / tree-shaking)** — удаляет неиспользуемые классы, методы, поля
2. (Совместно с AGP) **Сжатие ресурсов (resource shrinking)** — Android Gradle Plugin на основе результатов анализа R8 удаляет неиспользуемые ресурсы из APK / AAB
3. **Обфускация** — переименовывает классы/методы короткими именами
4. **Оптимизация** — применяет оптимизации байткода/Dex и уменьшает размер DEX

### Конфигурация

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true           // включает R8 (или другой shrinker) для сжатия и обфускации
            shrinkResources true         // включает shrinker ресурсов (AGP, опирается на анализ R8)
            proguardFiles getDefaultProguardFile(
                'proguard-android-optimize.txt'),
                'proguard-rules.pro'     // файлы с правилами в формате ProGuard, которые также использует R8
        }
    }
}
```

### Сохранение Кода С Помощью Правил `-keep`

R8 (как и ProGuard) может удалить код, который используется только неявно, например через:
- reflection — динамическое создание экземпляров, доступ к методам/полям
- JNI — вызовы из нативного кода
- фреймворки сериализации (Gson, Moshi и т.п.)

```proguard
-keep public class com.example.MyClass  # сохраняет класс целиком
-keepclassmembers class * {
    @com.example.Keep *;               # пример сохранения членов, помеченных пользовательской аннотацией Keep
}
```

Для стандартного кейса можно использовать аннотацию `@Keep` из AndroidX (`androidx.annotation.Keep`), которую R8 обрабатывает напрямую.

### Преимущества И Недостатки R8/обфускации

**Преимущества:**
- Уменьшение размера APK/AAB (часто заметное, в ряде проектов может достигать десятков процентов)
- Усложнение обратной разработки
- Удаление мёртвого кода

**Недостатки:**
- Требуется настройка правил для reflection/serialization/JNI
- Усложнение отладки крашей (обфусцированные stacktrace'ы; нужно использовать mapping-файлы)
- Необходимо полноценно тестировать release-сборки

## Answer (EN)

**ProGuard** is the older tool for Java/Android code shrinking and obfuscation. In Android it was used to:
- remove unused code (code shrinking),
- obfuscate (rename) classes and methods,
- perform basic bytecode optimizations.

**R8** is the modern compiler/shrinker integrated into the Android Gradle Plugin and used as the default shrinker (it replaces ProGuard in the standard Android build pipeline while using ProGuard-compatible rule syntax). It performs four key build-time tasks:

1. **Code shrinking (tree-shaking)** — removes unused classes, methods, fields
2. (Together with AGP) **Resource shrinking** — the Android Gradle Plugin, based on R8’s analysis, removes unused resources from the APK/AAB
3. **Obfuscation** — renames classes/methods with short names
4. **Optimization** — applies bytecode/Dex optimizations and reduces DEX size

### Configuration

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true           // enables R8 (or another shrinker) for code shrinking and obfuscation
            shrinkResources true         // enables resource shrinking (AGP, relies on R8 analysis)
            proguardFiles getDefaultProguardFile(
                'proguard-android-optimize.txt'),
                'proguard-rules.pro'     // rule files in ProGuard format, also consumed by R8
        }
    }
}
```

### Preserving Code with `-keep` Rules

R8 (like ProGuard) can remove code that is only accessed indirectly, for example via:
- reflection — dynamic instantiation or reflective access to fields/methods
- JNI — calls from native code
- serialization libraries (Gson, Moshi, etc.)

```proguard
-keep public class com.example.MyClass  # preserves the entire class
-keepclassmembers class * {
    @com.example.Keep *;               # example of preserving members annotated with a custom Keep annotation
}
```

For typical Android projects you can use the `@Keep` annotation from AndroidX (`androidx.annotation.Keep`), which R8 honors directly.

### Trade-offs (R8/obfuscation)

**Benefits:**
- Reduces APK/AAB size (often significantly; in some projects can reach tens of percent)
- Makes reverse engineering harder
- Removes dead code

**Drawbacks:**
- Requires rules configuration for reflection/serialization/JNI
- Makes crash debugging harder (obfuscated stack traces; requires mapping files)
- Requires thorough testing of release builds

---

## Дополнительные Вопросы (RU)

- Как декодировать обфусцированные stacktrace'ы с помощью mapping-файлов?
- Когда стоит использовать аннотацию `@Keep` вместо правил `-keep` и наоборот?
- Как R8 оптимизирует байткод помимо простого удаления мёртвого кода?
- Каковы типичные подводные камни при настройке правил ProGuard для Gson/Retrofit?

## Follow-ups

- How to decode obfuscated stacktraces using mapping files?
- When should you use `@Keep` vs `-keep` rules?
- How does R8 optimize bytecode beyond simple dead code removal?
- What are common pitfalls when configuring ProGuard rules for Gson/Retrofit?

## Ссылки (RU)

- https://developer.android.com/studio/build/shrink-code

## References

- https://developer.android.com/studio/build/shrink-code

## Связанные Вопросы (RU)

### Предварительные Знания / Концепции

- [[c-gradle]]
- [[c-memory-management]]

### Предварительные (Проще)
- Понимание конфигурации сборки Gradle

### Связанные (Средний уровень)
- [[q-reduce-app-size--android--medium]] — техники оптимизации размера APK
- [[q-build-optimization-gradle--android--medium]] — оптимизация конфигурации сборки

### Продвинутые (Сложнее)
- Продвинутая оптимизация старта и производительности во время исполнения

## Related Questions

### Prerequisites / Concepts

- [[c-gradle]]
- [[c-memory-management]]

### Prerequisites (Easier)
- Understanding Gradle build configuration

### Related (Medium)
- [[q-reduce-app-size--android--medium]] - APK optimization techniques
- [[q-build-optimization-gradle--android--medium]] - Build configuration

### Advanced (Harder)
- Advanced startup and runtime performance optimization
