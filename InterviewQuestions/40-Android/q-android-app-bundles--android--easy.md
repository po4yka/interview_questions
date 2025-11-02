---
id: android-015
title: Android App Bundle (AAB) / Android App Bundle (AAB)
aliases: ["AAB", "Android App Bundle", "Android App Bundles", "Андроид App Bundle", "Формат AAB"]
topic: android
subtopics: [app-bundle, gradle]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-app-bundle, c-gradle, q-gradle-basics--android--easy, q-play-feature-delivery--android--medium]
created: 2025-10-05
updated: 2025-10-29
sources: ["https://developer.android.com/guide/app-bundle"]
tags: [android/app-bundle, android/gradle, difficulty/easy]
date created: Wednesday, October 29th 2025, 4:18:34 pm
date modified: Saturday, November 1st 2025, 3:59:52 pm
---

# Вопрос (RU)
> Что такое Android App Bundle (AAB)?

---

# Question (EN)
> What is Android App Bundle (AAB)?

---

## Ответ (RU)

**Android App Bundle (AAB)** — формат публикации для Google Play, заменяющий универсальный APK. Google Play генерирует оптимизированные APK для каждой конфигурации устройства, уменьшая размер загрузки на 15-35%.

**Архитектура AAB:**

AAB содержит:
- **Base module** — основной код приложения
- **Feature modules** — опциональные модули с динамической доставкой
- **Asset packs** — большие ресурсы (игры, ML-модели)
- Метаданные для генерации split APK

Google Play генерирует Split APK по измерениям:
- **Языковые ресурсы** — только выбранные пользователем локали
- **Плотность экрана** — drawable для конкретного dpi
- **ABI** — нативные библиотеки для архитектуры процессора (arm64-v8a, x86)

**Преимущества:**

```kotlin
// ✅ Настройка разделения в build.gradle.kts
android {
    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}

// ❌ Без AAB: пользователь скачивает ВСЕ ресурсы
// APK = 100 MB (все языки + все плотности + все ABI)

// ✅ С AAB: пользователь скачивает только нужное
// Base APK = 20 MB + язык (5 MB) + плотность (2 MB) + ABI (8 MB) = 35 MB
```

**Тестирование AAB локально:**

```bash
# Генерация набора APK для всех конфигураций
bundletool build-apks --bundle=app.aab --output=app.apks

# Генерация универсального APK (для быстрого тестирования)
bundletool build-apks --bundle=app.aab --output=app.apks --mode=universal

# Установка на подключенное устройство (автоматический выбор APK)
bundletool install-apks --apks=app.apks
```

**Подписывание:**

AAB подписывается локально ключом разработчика, но **Google Play App Signing** пересоздает и подписывает все APK собственным ключом. Это обязательное требование при публикации AAB.

---

## Answer (EN)

**Android App Bundle (AAB)** is a publishing format for Google Play that replaces universal APK. Google Play generates optimized APKs for each device configuration, reducing download size by 15-35%.

**AAB Architecture:**

AAB contains:
- **Base module** — core app code
- **Feature modules** — optional modules with dynamic delivery
- **Asset packs** — large resources (games, ML models)
- Metadata for generating split APKs

Google Play generates Split APKs by dimensions:
- **Language resources** — only user-selected locales
- **Screen density** — drawables for specific dpi
- **ABI** — native libraries for CPU architecture (arm64-v8a, x86)

**Benefits:**

```kotlin
// ✅ Configure splits in build.gradle.kts
android {
    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}

// ❌ Without AAB: user downloads ALL resources
// APK = 100 MB (all languages + all densities + all ABIs)

// ✅ With AAB: user downloads only what's needed
// Base APK = 20 MB + language (5 MB) + density (2 MB) + ABI (8 MB) = 35 MB
```

**Testing AAB Locally:**

```bash
# Generate APK set for all configurations
bundletool build-apks --bundle=app.aab --output=app.apks

# Generate universal APK (for quick testing)
bundletool build-apks --bundle=app.aab --output=app.apks --mode=universal

# Install on connected device (automatic APK selection)
bundletool install-apks --apks=app.apks
```

**Signing:**

AAB is signed locally with developer key, but **Google Play App Signing** recreates and signs all APKs with its own key. This is mandatory when publishing AAB.

---

## Follow-ups

- What are Split APKs and how do they differ from regular APKs?
- How does Dynamic Feature Delivery work with AAB?
- What is Google Play App Signing and why is it required for AAB?
- How do Asset Packs differ from Feature Modules?
- What happens if AAB exceeds 150 MB compressed size limit?

## References

- [[c-app-bundle]] - App Bundle concepts and architecture
- [[c-gradle]] - Gradle build system fundamentals
- [Android App Bundle Guide](https://developer.android.com/guide/app-bundle)
- [BundleTool Documentation](https://developer.android.com/studio/command-line/bundletool)

## Related Questions

### Prerequisites
- [[q-gradle-basics--android--easy]] - Gradle build configuration basics

### Related
- [[q-play-feature-delivery--android--medium]] - Dynamic Feature Delivery

### Advanced
- [[q-app-size-optimization--android--medium]] - App size optimization strategies