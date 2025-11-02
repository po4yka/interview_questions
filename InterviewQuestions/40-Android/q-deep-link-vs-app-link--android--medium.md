---
id: android-450
title: Deep Link Vs App Link / Deep Link против App Link
aliases: ["Deep Link Vs App Link", "Deep Link против App Link"]
topic: android
subtopics: [intents-deeplinks, ui-navigation]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-deep-linking]
created: 2025-10-20
updated: 2025-10-27
tags: [android/intents-deeplinks, android/ui-navigation, app-links, deep-linking, difficulty/medium]
sources: [https://developer.android.com/training/app-links]
date created: Monday, October 27th 2025, 10:26:58 pm
date modified: Saturday, November 1st 2025, 5:43:36 pm
---

# Вопрос (RU)
> Какие основные отличия между Deep Link и App Link в Android?

# Question (EN)
> What are the main differences between Deep Link and App Link in Android?

---

## Ответ (RU)

**Deep Link** использует **пользовательскую URI-схему** (`myapp://`) для навигации внутри приложения. Прост в настройке, но любое приложение может заявить ту же схему.

**App Link** использует **HTTPS URL** с **верификацией домена** через `assetlinks.json`. Обеспечивает безопасность и прямой запуск приложения без диалога выбора.

### Ключевые Различия

| Критерий | Deep Link | App Link |
|----------|-----------|----------|
| **Схема** | Пользовательская (`myapp://`) | HTTPS (`https://`) |
| **Верификация** | Отсутствует | Верификация домена через `assetlinks.json` |
| **UX** | Диалог выбора приложения | Прямой запуск приложения |
| **Android API** | Все версии | 23+ (Marshmallow 6.0+) |
| **Безопасность** | Низкая (схема не защищена) | Высокая (верифицированное владение) |
| **Настройка** | Простая (только manifest) | Сложная (manifest + файл на сервере) |

### Deep Link: Реализация

**Intent Filter (AndroidManifest.xml):**
```xml
<activity android:name=".DetailActivity">
    <intent-filter>
        <!-- ✅ VIEW action для обработки ссылок -->
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <!-- ❌ Пользовательская схема - любой может перехватить -->
        <data android:scheme="myapp" android:host="detail" />
    </intent-filter>
</activity>
```

**Обработка в Activity:**
```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    // ✅ Безопасная обработка с валидацией
    intent.data?.let { uri ->
        val id = uri.getQueryParameter("id")
        if (id != null && id.matches(Regex("\\d+"))) {
            loadDetail(id)
        }
    }
}
```

**Пример использования:** `myapp://detail?id=123`

### App Link: Реализация

**Intent Filter с autoVerify:**
```xml
<activity android:name=".DetailActivity">
    <!-- ✅ autoVerify=true для автоматической верификации -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <!-- ✅ HTTPS схема - только верифицированный домен -->
        <data android:scheme="https"
              android:host="example.com"
              android:pathPrefix="/detail" />
    </intent-filter>
</activity>
```

**Файл assetlinks.json (на сервере):**
Размещается: `https://example.com/.well-known/assetlinks.json`

```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.example.app",
    "sha256_cert_fingerprints": ["14:6D:E9:..."]
  }
}]
```

**Пример использования:** `https://example.com/detail?id=123`

### Проверка Верификации

```kotlin
// API 31+ (Android 12+)
val manager = getSystemService(DomainVerificationManager::class.java)
val userState = manager.getDomainVerificationUserState(packageName)

userState?.hostToStateMap?.forEach { (domain, state) ->
    when (state) {
        // ✅ Домен верифицирован
        DomainVerificationUserState.DOMAIN_STATE_VERIFIED -> {
            Log.d("AppLink", "$domain verified")
        }
        // ❌ Верификация не прошла
        else -> Log.w("AppLink", "$domain not verified: $state")
    }
}
```

### Выбор Подхода

**Deep Link → для:**
- Внутренней навигации (между частями приложения)
- Быстрого прототипирования
- Случаев без требований к безопасности

**App Link → для:**
- Публичного веб-контента с мобильной версией
- Интеграции с маркетинговыми кампаниями
- Случаев с высокими требованиями к безопасности
- Universal Links совместимости (iOS)

---

## Answer (EN)

**Deep Link** uses a **custom URI scheme** (`myapp://`) for in-app navigation. Simple to configure, but any app can claim the same scheme.

**App Link** uses **HTTPS URLs** with **domain verification** via `assetlinks.json`. Provides security and direct app launch without chooser dialog.

### Key Differences

| Criterion | Deep Link | App Link |
|-----------|-----------|----------|
| **Scheme** | Custom (`myapp://`) | HTTPS (`https://`) |
| **Verification** | None | Domain verification via `assetlinks.json` |
| **UX** | App chooser dialog | Direct app launch |
| **Android API** | All versions | 23+ (Marshmallow 6.0+) |
| **Security** | Low (unprotected scheme) | High (verified ownership) |
| **Setup** | Simple (manifest only) | Complex (manifest + server file) |

### Deep Link: Implementation

**Intent Filter (AndroidManifest.xml):**
```xml
<activity android:name=".DetailActivity">
    <intent-filter>
        <!-- ✅ VIEW action for link handling -->
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <!-- ❌ Custom scheme - anyone can intercept -->
        <data android:scheme="myapp" android:host="detail" />
    </intent-filter>
</activity>
```

**Activity Handling:**
```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    // ✅ Safe handling with validation
    intent.data?.let { uri ->
        val id = uri.getQueryParameter("id")
        if (id != null && id.matches(Regex("\\d+"))) {
            loadDetail(id)
        }
    }
}
```

**Usage example:** `myapp://detail?id=123`

### App Link: Implementation

**Intent Filter with autoVerify:**
```xml
<activity android:name=".DetailActivity">
    <!-- ✅ autoVerify=true for automatic verification -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <!-- ✅ HTTPS scheme - verified domain only -->
        <data android:scheme="https"
              android:host="example.com"
              android:pathPrefix="/detail" />
    </intent-filter>
</activity>
```

**assetlinks.json file (on server):**
Location: `https://example.com/.well-known/assetlinks.json`

```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.example.app",
    "sha256_cert_fingerprints": ["14:6D:E9:..."]
  }
}]
```

**Usage example:** `https://example.com/detail?id=123`

### Verification Check

```kotlin
// API 31+ (Android 12+)
val manager = getSystemService(DomainVerificationManager::class.java)
val userState = manager.getDomainVerificationUserState(packageName)

userState?.hostToStateMap?.forEach { (domain, state) ->
    when (state) {
        // ✅ Domain verified
        DomainVerificationUserState.DOMAIN_STATE_VERIFIED -> {
            Log.d("AppLink", "$domain verified")
        }
        // ❌ Verification failed
        else -> Log.w("AppLink", "$domain not verified: $state")
    }
}
```

### Choosing the Approach

**Deep Link → for:**
- Internal navigation (between app sections)
- Rapid prototyping
- Cases without security requirements

**App Link → for:**
- Public web content with mobile app version
- Marketing campaign integration
- Cases with high security requirements
- Universal Links compatibility (iOS)

---

## Follow-ups

- How to handle unverified App Links fallback?
- What happens if multiple apps claim the same App Link domain?
- How to test App Link verification during development?
- What are security best practices for parsing deep link parameters?

## References

- [Android App Links Documentation](https://developer.android.com/training/app-links)
- [assetlinks.json Generator](https://developers.google.com/digital-asset-links/tools/generator)

## Related Questions

### Prerequisites

### Related
- How to implement deferred deep linking for app installs
- App Link verification debugging and troubleshooting

### Advanced
- Implementing branch.io or Firebase Dynamic Links for cross-platform deep linking
- App Link security: preventing deep link hijacking attacks
- Universal Links (iOS) and App Links coordination strategy
