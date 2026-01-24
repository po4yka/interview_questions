---
id: kotlin-252
title: ProGuard and R8 Optimization / Оптимизация ProGuard и R8
aliases:
- ProGuard R8
- Code Shrinking
- ProGuard и R8 оптимизация
topic: kotlin
subtopics:
- build-tools
- optimization
- obfuscation
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-build-tools
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- proguard
- r8
- optimization
- obfuscation
- difficulty/medium
anki_cards:
- slug: kotlin-252-0-en
  language: en
  anki_id: 1769170327496
  synced_at: '2026-01-23T17:03:51.204876'
- slug: kotlin-252-0-ru
  language: ru
  anki_id: 1769170327521
  synced_at: '2026-01-23T17:03:51.206662'
---
# Вопрос (RU)
> Что такое ProGuard и R8? Как они оптимизируют Kotlin код?

# Question (EN)
> What are ProGuard and R8? How do they optimize Kotlin code?

---

## Ответ (RU)

**ProGuard** и **R8** - инструменты для уменьшения и оптимизации кода Android приложений.

**R8** - современная замена ProGuard от Google, используется по умолчанию.

**Функции:**

| Функция | Описание |
|---------|----------|
| **Shrinking** | Удаление неиспользуемого кода |
| **Optimization** | Оптимизация байткода |
| **Obfuscation** | Переименование классов/методов |
| **Desugaring** | Преобразование новых Java API |

**Включение в проекте:**
```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

**Kotlin-специфичные правила:**
```proguard
# proguard-rules.pro

# Сохранить Kotlin metadata для reflection
-keep class kotlin.Metadata { *; }

# Coroutines
-keepclassmembers class kotlinx.coroutines.** {
    volatile <fields>;
}

# Serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.**
-keep,includedescriptorclasses class com.example.**$$serializer { *; }
-keepclassmembers class com.example.** {
    *** Companion;
}

# Data classes (если используются с reflection)
-keep class com.example.data.** { *; }
```

**Распространённые проблемы:**
```kotlin
// ПРОБЛЕМА: R8 удаляет классы используемые через reflection
@Keep  // Решение: аннотация Keep
data class User(val name: String)

// ПРОБЛЕМА: Enum values удаляются
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
```

**Отладка:**
```kotlin
// Сохранить mapping файл для деобфускации stack traces
release {
    proguardFiles(...)
    // mapping.txt создаётся автоматически
}

// Отключить обфускацию для отладки
-dontobfuscate
```

## Answer (EN)

**ProGuard** and **R8** are tools for shrinking and optimizing Android application code.

**R8** - modern replacement for ProGuard from Google, used by default.

**Functions:**

| Function | Description |
|----------|-------------|
| **Shrinking** | Removing unused code |
| **Optimization** | Bytecode optimization |
| **Obfuscation** | Renaming classes/methods |
| **Desugaring** | Converting new Java APIs |

**Enabling in Project:**
```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

**Kotlin-specific Rules:**
```proguard
# proguard-rules.pro

# Keep Kotlin metadata for reflection
-keep class kotlin.Metadata { *; }

# Coroutines
-keepclassmembers class kotlinx.coroutines.** {
    volatile <fields>;
}

# Serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.**
-keep,includedescriptorclasses class com.example.**$$serializer { *; }
-keepclassmembers class com.example.** {
    *** Companion;
}

# Data classes (if used with reflection)
-keep class com.example.data.** { *; }
```

**Common Issues:**
```kotlin
// PROBLEM: R8 removes classes used via reflection
@Keep  // Solution: Keep annotation
data class User(val name: String)

// PROBLEM: Enum values get removed
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
```

**Debugging:**
```kotlin
// Keep mapping file for deobfuscating stack traces
release {
    proguardFiles(...)
    // mapping.txt created automatically
}

// Disable obfuscation for debugging
-dontobfuscate
```

---

## Follow-ups

- How do you deobfuscate crash reports from production?
- What is the difference between -keep and -keepclassmembers?
- How does R8 full mode differ from compatibility mode?
