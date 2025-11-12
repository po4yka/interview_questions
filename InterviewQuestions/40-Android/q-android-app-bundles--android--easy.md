---
id: android-015
title: Android App Bundle (AAB)
aliases: [AAB, Android App Bundle, Android App Bundles, 4ndroid App Bundle, 608088847290 AAB]
topic: android
subtopics:
- app-bundle
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-app-bundle
- c-gradle
- q-gradle-basics--android--easy
- q-play-feature-delivery--android--medium
created: 2025-10-05
updated: 2025-11-10
sources:
- "https://developer.android.com/guide/app-bundle"
tags: [android/app-bundle, difficulty/easy]

---

# Вопрос (RU)
> Что такое Android App `Bundle` (AAB)?

---

# Question (EN)
> What is Android App `Bundle` (AAB)?

---

## Ответ (RU)

**Android App `Bundle` (AAB)** — это формат публикации для Google Play, который заменяет загрузку одного универсального APK. Пользователь по-прежнему получает APK, но Google Play генерирует оптимизированные APK под конкретную конфигурацию устройства, что обычно уменьшает размер загрузки примерно на 15–35%.

С 2021 года новые приложения, публикуемые в Google Play, должны использовать формат AAB (за редкими исключениями, например, для некоторых устройств/каналов распространения).

**Архитектура AAB:**

AAB содержит:
- **Base module** — основной код приложения
- **Feature modules** — опциональные модули с динамической доставкой
- **Asset packs** — крупные ресурсы (например, игры, ML-модели)
- Метаданные для генерации split APK

Google Play генерирует Split APK по измерениям:
- **Языковые ресурсы** — только нужные пользователю локали
- **Плотность экрана (screen density)** — только нужные drawable для конкретного dpi
- **ABI** — только необходимые нативные библиотеки для архитектуры CPU устройства (например, arm64-v8a, x86)

**Преимущества:**

```kotlin
// Примечание: сплиты формируются Google Play на основе AAB.
android {
    bundle {
        // Языковые сплиты по умолчанию включены для app bundle.
        // Установите enableSplit = false, если хотите их отключить.
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}

// Без AAB: один универсальный APK заставляет пользователя скачивать все ресурсы
// APK = 100 MB (все языки + все плотности + все ABI)

// С AAB: пользователь скачивает только то, что нужно его устройству
// Base APK = 20 MB + язык (5 MB) + плотность (2 MB) + ABI (8 MB) = 35 MB (пример)
```

**Тестирование AAB локально:**

```bash
# Сгенерировать набор APK (APK set) для всех конфигураций
bundletool build-apks --bundle=app.aab --output=app.apks

# Сгенерировать универсальный APK (для быстрого локального тестирования)
bundletool build-apks --bundle=app.aab --output=app.apks --mode=universal

# Установить на подключённое устройство (bundletool выберет подходящие APK)
bundletool install-apks --apks=app.apks
```

**Подпись:**

AAB подписывается локально upload-ключом разработчика. Для приложений, распространяемых через Google Play с использованием AAB, используется **Google Play App Signing**: Google управляет ключами подписи и на их основе генерирует и подписывает фактические APK, доставляемые пользователям. На практике при загрузке AAB в Google Play использование Play App Signing является обязательным.

---

## Answer (EN)

**Android App `Bundle` (AAB)** is a publishing format for Google Play that replaces a single universal APK upload. Users still receive APKs generated from the bundle: Google Play builds optimized APKs for each device configuration, typically reducing download size by about 15-35%.

Since 2021, new apps published on Google Play are required to use the AAB format (with limited exceptions, e.g., for specific device types/distribution channels).

**AAB Architecture:**

AAB contains:
- **Base module** — core app code
- **Feature modules** — optional modules with dynamic delivery
- **Asset packs** — large resources (e.g., games, ML models)
- Metadata for generating split APKs

Google Play generates Split APKs by dimensions:
- **Language resources** — only the locales needed for the user
- **Screen density** — only drawables for the specific dpi
- **ABI** — only the native libraries needed for the device CPU architecture (e.g., arm64-v8a, x86)

**Benefits:**

```kotlin
// Note: splits are handled by Google Play based on the AAB.
android {
    bundle {
        // Language splits are enabled by default for app bundles.
        // Set enableSplit = false if you explicitly want to disable them.
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}

// Without AAB: a single universal APK may force users to download all resources
// APK = 100 MB (all languages + all densities + all ABIs)

// With AAB: the user downloads only what is needed for their device
// Base APK = 20 MB + language (5 MB) + density (2 MB) + ABI (8 MB) = 35 MB (example)
```

**Testing AAB Locally:**

```bash
# Generate APK set for all configurations
bundletool build-apks --bundle=app.aab --output=app.apks

# Generate a universal APK (for quick local testing)
bundletool build-apks --bundle=app.aab --output=app.apks --mode=universal

# Install on connected device (bundletool selects appropriate APKs)
bundletool install-apks --apks=app.apks
```

**Signing:**

The AAB is signed locally with the developer's upload key. For apps distributed via Google Play using AAB, **Google Play App Signing** is used: Google manages the signing keys and uses them to generate and sign the actual APKs delivered to users. In practice, when uploading an AAB to Google Play, Play App Signing is required.

---

## Дополнительные вопросы (RU)

- Что такое Split APK и чем он отличается от обычного APK?
- Как работает Dynamic Feature Delivery с AAB?
- Что такое Google Play App Signing и почему он требуется для AAB?
- Чем Asset Packs отличаются от Feature Modules?
- Что происходит, если сжатый AAB превышает лимит 150 MB?

## Follow-ups

- What are Split APKs and how do they differ from regular APKs?
- How does Dynamic Feature Delivery work with AAB?
- What is Google Play App Signing and why is it required for AAB?
- How do Asset Packs differ from Feature Modules?
- What happens if AAB exceeds 150 MB compressed size limit?

## Ссылки (RU)

- [[c-app-bundle]] — концепции и архитектура App `Bundle`
- [[c-gradle]] — основы Gradle build-системы
- [Руководство по Android App `Bundle`](https://developer.android.com/guide/app-bundle)
- [Документация BundleTool](https://developer.android.com/studio/command-line/bundletool)

## References

- [[c-app-bundle]] - App `Bundle` concepts and architecture
- [[c-gradle]] - Gradle build system fundamentals
- [Android App `Bundle` Guide](https://developer.android.com/guide/app-bundle)
- [BundleTool Documentation](https://developer.android.com/studio/command-line/bundletool)

## Связанные вопросы (RU)

### Предпосылки
- [[q-gradle-basics--android--easy]] - основы конфигурации Gradle

### Похожие
- [[q-play-feature-delivery--android--medium]] - Dynamic Feature Delivery

### Продвинутые
- [[q-app-size-optimization--android--medium]] - стратегии оптимизации размера приложения

## Related Questions

### Prerequisites
- [[q-gradle-basics--android--easy]] - Gradle build configuration basics

### Related
- [[q-play-feature-delivery--android--medium]] - Dynamic Feature Delivery

### Advanced
- [[q-app-size-optimization--android--medium]] - App size optimization strategies
