---
id: android-450
title: Deep Link Vs App Link / Deep Link против App Link
aliases: [Deep Link Vs App Link, Deep Link против App Link]
topic: android
subtopics:
  - intents-deeplinks
  - ui-navigation
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related: []
created: 2025-10-20
updated: 2025-11-02
tags: [android/intents-deeplinks, android/ui-navigation, app-links, deep-linking, difficulty/medium]
sources:
  - https://developer.android.com/training/app-links
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Sunday, November 2nd 2025, 7:40:58 pm
---

# Вопрос (RU)
> Какие основные отличия между Deep Link и App Link в Android?

# Question (EN)
> What are the main differences between Deep Link and App Link in Android?

## Ответ (RU)

**Deep Link** использует **пользовательскую URI-схему** (`myapp://`) для навигации внутри приложения. Прост в настройке, но любое приложение может заявить ту же схему, что создает риски безопасности.

**App Link** использует **HTTPS URL** с **верификацией домена** через `assetlinks.json`. Обеспечивает безопасность и прямой запуск приложения без диалога выбора. Это современный стандарт Google для глубоких ссылок с проверкой владения доменом.

### Ключевые Различия

| Критерий | Deep Link | App Link |
|----------|-----------|----------|
| **Схема** | Пользовательская (`myapp://`) | HTTPS (`https://`) |
| **Верификация** | Отсутствует — любой может перехватить | Верификация домена через `assetlinks.json` — доказательство владения |
| **UX** | Диалог выбора приложения — пользователь выбирает вручную | Прямой запуск приложения — без диалога |
| **Android API** | Все версии (API 1+) | API 23+ (Android 6.0 Marshmallow) |
| **Безопасность** | Низкая (схема не защищена, возможно перехватывание) | Высокая (верифицированное владение доменом, исключает перехватывание) |
| **Настройка** | Простая (только `AndroidManifest.xml`) | Сложная (`AndroidManifest.xml` + `assetlinks.json` на сервере) |

### Deep Link: Реализация

**Intent Filter (AndroidManifest.xml):**
```xml
<activity android:name=".DetailActivity">
    <intent-filter>
        <!-- ✅ VIEW action для обработки ссылок -->
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <!-- ❌ Пользовательская схема — любой может перехватить -->
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

**Пример использования:** `myapp://detail?id=123` — открывается диалог выбора приложения, если несколько приложений заявляют эту схему.

### App Link: Реализация

**Intent Filter с autoVerify:**
```xml
<activity android:name=".DetailActivity">
    <!-- ✅ autoVerify=true для автоматической верификации -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <!-- ✅ HTTPS схема — только верифицированный домен -->
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

**Пример использования:** `https://example.com/detail?id=123` — приложение открывается напрямую без диалога, если домен верифицирован.

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
- Внутренней навигации (между частями приложения) — когда безопасность не критична
- Быстрого прототипирования — минимальная настройка
- Случаев без требований к безопасности — тестирование, внутренние инструменты
- Legacy приложений — поддержка старых версий Android

**App Link → для:**
- Публичного веб-контента с мобильной версией — единая ссылка для веб и мобильного приложения
- Интеграции с маркетинговыми кампаниями — надежная доставка пользователей
- Случаев с высокими требованиями к безопасности — предотвращение перехватывания ссылок
- Universal Links совместимости (iOS) — единый формат для обеих платформ

## Answer (EN)

**Deep Link** uses a **custom URI scheme** (`myapp://`) for in-app navigation. Simple to configure, but any app can claim the same scheme, creating security risks.

**App Link** uses **HTTPS URLs** with **domain verification** via `assetlinks.json`. Provides security and direct app launch without chooser dialog. This is Google's modern standard for deep linking with domain ownership verification.

### Key Differences

| Criterion | Deep Link | App Link |
|-----------|-----------|----------|
| **Scheme** | Custom (`myapp://`) | HTTPS (`https://`) |
| **Verification** | None — anyone can intercept | Domain verification via `assetlinks.json` — proof of ownership |
| **UX** | App chooser dialog — user selects manually | Direct app launch — no dialog |
| **Android API** | All versions (API 1+) | API 23+ (Android 6.0 Marshmallow) |
| **Security** | Low (unprotected scheme, possible hijacking) | High (verified domain ownership, prevents hijacking) |
| **Setup** | Simple (`AndroidManifest.xml` only) | Complex (`AndroidManifest.xml` + `assetlinks.json` on server) |

### Deep Link: Implementation

**Intent Filter (AndroidManifest.xml):**
```xml
<activity android:name=".DetailActivity">
    <intent-filter>
        <!-- ✅ VIEW action for link handling -->
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <!-- ❌ Custom scheme — anyone can intercept -->
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

**Usage example:** `myapp://detail?id=123` — opens app chooser dialog if multiple apps claim this scheme.

### App Link: Implementation

**Intent Filter with autoVerify:**
```xml
<activity android:name=".DetailActivity">
    <!-- ✅ autoVerify=true for automatic verification -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <!-- ✅ HTTPS scheme — verified domain only -->
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

**Usage example:** `https://example.com/detail?id=123` — app opens directly without dialog if domain is verified.

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
- Internal navigation (between app sections) — when security isn't critical
- Rapid prototyping — minimal setup
- Cases without security requirements — testing, internal tools
- Legacy apps — support for older Android versions

**App Link → for:**
- Public web content with mobile app version — single link for web and mobile app
- Marketing campaign integration — reliable user delivery
- Cases with high security requirements — prevents link hijacking
- Universal Links compatibility (iOS) — unified format for both platforms

## Follow-ups

- How to handle unverified `App Link` fallback?
- What happens if multiple apps claim the same `App Link` domain?
- How to test `App Link` verification during development?
- What are security best practices for parsing deep link parameters?
- How to implement deferred deep linking for app installs?

## References

- [Android App Links Documentation](https://developer.android.com/training/app-links)
- [assetlinks.json Generator](https://developers.google.com/digital-asset-links/tools/generator)

## Related Questions

### Prerequisites (Easier)
- Understanding of Android `Intent` system
- Basic knowledge of URI schemes and `AndroidManifest.xml`

### Related (Same Level)
- `Intent` filters and navigation patterns
- `App Link` verification debugging and troubleshooting
- URL routing in Android applications

### Advanced (Harder)
- Implementing `branch.io` or `Firebase Dynamic Links` for cross-platform deep linking
- `App Link` security: preventing deep link hijacking attacks
- Universal Links (iOS) and `App Link` coordination strategy
