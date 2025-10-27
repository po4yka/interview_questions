---
id: 20251005-143000
title: Android App Bundle (AAB) / Android App Bundle (AAB)
aliases:
  - AAB
  - Android App Bundle
  - Android App Bundles
  - Формат AAB
  - Андроид App Bundle
topic: android
subtopics:
  - app-bundle
  - play-console
question_kind: android
difficulty: easy
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-gradle-basics--android--easy
  - q-play-feature-delivery--android--medium
created: 2025-10-05
updated: 2025-10-27
sources:
  - https://github.com/Kirchhoff-/Android-Interview-Questions
  - https://developer.android.com/guide/app-bundle
tags: [android/app-bundle, android/play-console, difficulty/easy]
---
# Вопрос (RU)
> Что такое Android App Bundle (AAB)?

---

# Question (EN)
> What are Android App Bundles?

## Ответ (RU)

**Android App Bundle (AAB)** — формат публикации приложений для Google Play, который содержит скомпилированный код и ресурсы. Google Play самостоятельно генерирует оптимизированные APK для каждого устройства.

**Ключевые преимущества:**

- **Меньший размер загрузки**: Пользователь скачивает только код и ресурсы для своего устройства
- **Динамическая доставка**: Возможность загружать функции по требованию
- **Лимит 150 МБ**: Увеличен с 100 МБ для сжатой загрузки
- **Подписывание Google**: Автоматическое подписывание APK через Google Play

**Настройка Bundle:**

```kotlin
// build.gradle.kts
android {
    bundle {
        language { enableSplit = true }  // ✅ Разделение по языкам
        density { enableSplit = true }   // ✅ Разделение по плотности экрана
        abi { enableSplit = true }       // ✅ Разделение по архитектуре процессора
    }
}
```

**Тестирование AAB локально:**

```bash
# Генерация универсального APK для тестирования
bundletool build-apks --bundle=app-release.aab --output=app.apks --mode=universal

# Установка на устройство
bundletool install-apks --apks=app.apks
```

**Требования:**

- **Обязательно**: AAB требуется для новых приложений с августа 2021
- **Поддержка APK**: Только для существующих приложений
- **Asset-паки**: Не учитываются в лимите 150 МБ

---

## Answer (EN)

**Android App Bundle (AAB)** is a publishing format for Google Play that contains compiled code and resources. Google Play generates optimized APKs for each device configuration.

**Key Benefits:**

- **Smaller downloads**: Users download only device-specific code and resources
- **Dynamic delivery**: Features can be downloaded on-demand
- **150MB limit**: Increased from 100MB for compressed downloads
- **Google signing**: Automatic APK signing by Google Play

**Bundle Configuration:**

```kotlin
// build.gradle.kts
android {
    bundle {
        language { enableSplit = true }  // ✅ Split by language
        density { enableSplit = true }   // ✅ Split by screen density
        abi { enableSplit = true }       // ✅ Split by CPU architecture
    }
}
```

**Testing AABs Locally:**

```bash
# Generate universal APK for testing
bundletool build-apks --bundle=app-release.aab --output=app.apks --mode=universal

# Install on device
bundletool install-apks --apks=app.apks
```

**Requirements:**

- **Mandatory**: AAB required for new apps since August 2021
- **APK support**: Only for existing apps
- **Asset packs**: Don't count toward 150MB limit

---

## Follow-ups

- How do you test AABs on different device configurations?
- What are the differences between feature modules and asset packs?
- How does AAB signing work with Google Play App Signing?

## References

- [[c-gradle]] - Gradle build system concepts
- [Android App Bundle Guide](https://developer.android.com/guide/app-bundle)
- [BundleTool Documentation](https://developer.android.com/studio/command-line/bundletool)

## Related Questions

### Prerequisites
- [[q-gradle-basics--android--easy]]

### Related
- [[q-play-feature-delivery--android--medium]]