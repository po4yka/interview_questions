---
id: android-001
title: "ProGuard and R8 / ProGuard и R8"
aliases: ["ProGuard and R8", "ProGuard и R8"]

# Classification
topic: android
subtopics: [gradle, performance-memory, obfuscation]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: [https://github.com/Kirchhoff-Android-Interview-Questions]

# Workflow & relations
status: draft
moc: moc-android
related: [q-reduce-app-size--android--medium, q-build-optimization-gradle--android--medium]

# Timestamps
created: 2025-10-05
updated: 2025-01-27

tags: [android/gradle, android/performance-memory, android/obfuscation, difficulty/medium]
---
# Вопрос (RU)
> Что такое ProGuard и R8?

# Question (EN)
> What are ProGuard and R8?

---

## Ответ (RU)

**R8** — современный компилятор Android, который заменил ProGuard. Выполняет четыре задачи во время сборки:

1. **Сжатие кода (tree-shaking)** — удаляет неиспользуемые классы, методы, поля
2. **Сжатие ресурсов** — удаляет неиспользуемые ресурсы из APK
3. **Обфускация** — переименовывает классы/методы короткими именами
4. **Оптимизация** — улучшает производительность и уменьшает размер DEX

### Конфигурация

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true           // ✅ включает сжатие и обфускацию
            shrinkResources true         // ✅ удаляет неиспользуемые ресурсы
            proguardFiles getDefaultProguardFile(
                'proguard-android-optimize.txt'),
                'proguard-rules.pro'
        }
    }
}
```

### Сохранение кода с -keep правилами

R8 может ошибочно удалить код, используемый через:
- **Reflection** — динамическое создание экземпляров
- **JNI** — вызовы из нативного кода

```proguard
-keep public class com.example.MyClass  # ✅ сохраняет класс целиком
-keepclassmembers class * {             # ✅ сохраняет поля/методы
    @com.example.Keep *;
}
```

Альтернатива: аннотация `@Keep` из AndroidX.

### Преимущества и недостатки

**Преимущества:**
- Уменьшение размера APK (на 20-40%)
- Усложнение обратной разработки
- Удаление мёртвого кода

**Недостатки:**
- Требуется настройка правил для reflection/serialization
- Усложнение отладки крашей (обфусцированные стектрейсы)
- Необходимо тестировать release-сборки

## Answer (EN)

**R8** is the modern Android compiler that replaced ProGuard. It performs four compile-time tasks:

1. **Code shrinking (tree-shaking)** — removes unused classes, methods, fields
2. **Resource shrinking** — removes unused resources from APK
3. **Obfuscation** — renames classes/methods with short names
4. **Optimization** — improves performance and reduces DEX size

### Configuration

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true           // ✅ enables shrinking and obfuscation
            shrinkResources true         // ✅ removes unused resources
            proguardFiles getDefaultProguardFile(
                'proguard-android-optimize.txt'),
                'proguard-rules.pro'
        }
    }
}
```

### Preserving code with -keep rules

R8 may incorrectly remove code accessed via:
- **Reflection** — dynamic instantiation
- **JNI** — calls from native code

```proguard
-keep public class com.example.MyClass  # ✅ preserves entire class
-keepclassmembers class * {             # ✅ preserves fields/methods
    @com.example.Keep *;
}
```

Alternative: `@Keep` annotation from AndroidX.

### Trade-offs

**Benefits:**
- Reduces APK size (by 20-40%)
- Makes reverse engineering harder
- Removes dead code

**Drawbacks:**
- Requires rules configuration for reflection/serialization
- Makes crash debugging harder (obfuscated stacktraces)
- Requires testing release builds

---

## Follow-ups

- How to decode obfuscated stacktraces using mapping files?
- When should you use `@Keep` vs `-keep` rules?
- How does R8 optimize bytecode beyond simple dead code removal?
- What are common pitfalls when configuring ProGuard rules for Gson/Retrofit?

## References

- https://developer.android.com/studio/build/shrink-code

## Related Questions

### Prerequisites (Easier)
- Understanding Gradle build configuration

### Related (Medium)
- [[q-reduce-app-size--android--medium]] - APK optimization techniques
- [[q-build-optimization-gradle--android--medium]] - Build configuration

### Advanced (Harder)
- Advanced startup and runtime performance optimization
