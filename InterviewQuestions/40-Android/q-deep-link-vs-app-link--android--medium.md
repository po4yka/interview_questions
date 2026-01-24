---
id: android-450
title: Deep Link Vs App Link / Deep Link против App Link
aliases:
- Deep Link Vs App Link
- Deep Link против App Link
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
status: draft
moc: moc-android
related:
- c-compose-navigation
- c-fragments
- c-intent
- q-app-startup-optimization--android--medium
- q-design-uber-app--android--hard
- q-macrobenchmark-startup--android--medium
created: 2025-10-20
updated: 2025-11-02
tags:
- android/intents-deeplinks
- android/ui-navigation
- app-links
- deep-linking
- difficulty/medium
anki_cards:
- slug: android-450-0-en
  language: en
  anki_id: 1768366955681
  synced_at: '2026-01-23T16:45:05.874687'
- slug: android-450-0-ru
  language: ru
  anki_id: 1768366955706
  synced_at: '2026-01-23T16:45:05.876018'
sources:
- https://developer.android.com/training/app-links
---
# Вопрос (RU)
> Какие основные отличия между Deep Link и App Link в Android?

# Question (EN)
> What are the main differences between Deep Link and App Link in Android?

## Ответ (RU)

**Deep Link** обычно использует **пользовательскую URI-схему** (`myapp://`) для навигации внутри приложения. Прост в настройке, но любое приложение может заявить ту же схему, что создает риски перехвата (hijacking) и отсутствие гарантии, что откроется именно ваше приложение.

**App Link** использует **HTTPS URL** с **верификацией домена** через `assetlinks.json`. Обеспечивает подтвержденное владение доменом и возможность прямого запуска приложения при успешной верификации. Это современный стандарт Google для глубоких ссылок с проверкой владения доменом.

### Ключевые Различия

| Критерий | Deep Link | App Link |
|----------|-----------|----------|
| **Схема** | Пользовательская (`myapp://`) | HTTPS (`https://`) |
| **Верификация** | Нет встроенной проверки владения — любую схему может заявить любое приложение | Верификация домена через `assetlinks.json` — доказательство владения |
| **UX** | Зависит от совпадений: если несколько приложений обрабатывают схему — диалог выбора; если одно или выбрано по умолчанию — открывается сразу | При успешной верификации домена и отсутствии конфликтов — прямой запуск приложения; при ошибке верификации или нескольких претендентах возможен диалог |
| **Android API** | Все версии (API 1+) | API 23+ (Android 6.0 Marshmallow) для официальных Android App Links |
| **Безопасность** | Ниже: нет подтверждения владения, возможен перехват схемы другим приложением | Выше: проверка владения доменом значительно снижает риск перехвата; поведение зависит от успешной верификации и настроек пользователя |
| **Настройка** | Простая (только `AndroidManifest.xml`) | Более сложная (`AndroidManifest.xml` + `assetlinks.json` на сервере) |

### Deep Link: Реализация

**`Intent` Filter (AndroidManifest.xml):**
```xml
<activity android:name=".DetailActivity">
    <intent-filter>
        <!-- ✅ VIEW action для обработки ссылок -->
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <!-- ❌ Пользовательская схема — любой может заявить такую же -->
        <data android:scheme="myapp" android:host="detail" />
    </intent-filter>
</activity>
```

**Обработка в `Activity`:**
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

**Пример использования:** `myapp://detail?id=123` — если несколько приложений заявили эту схему и host/path, система покажет диалог выбора; если только одно приложение или пользователь уже выбрал по умолчанию — откроется оно напрямую.

### App Link: Реализация

**`Intent` Filter с autoVerify:**
```xml
<activity android:name=".DetailActivity">
    <!-- ✅ autoVerify=true для автоматической верификации App Links -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <!-- ✅ HTTPS схема с конкретным доменом -->
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

**Пример использования:** `https://example.com/detail?id=123` — при успешной верификации домена и отсутствии других приоритетных обработчиков ссылка откроется в приложении без диалога; иначе система может предложить выбор (браузер / приложения).

### Проверка Верификации

```kotlin
// API 31+ (Android 12+)
val manager = getSystemService(DomainVerificationManager::class.java)
val userState = manager.getDomainVerificationUserState(packageName)

userState?.hostToStateMap?.forEach { (domain, state) ->
    when (state) {
        // ✅ Домен верифицирован для App Links
        DomainVerificationUserState.DOMAIN_STATE_VERIFIED -> {
            Log.d("AppLink", "$domain verified")
        }
        // ❌ Верификация не прошла или неактивна
        else -> Log.w("AppLink", "$domain not verified: $state")
    }
}
```

### Выбор Подхода

**Deep Link → для:**
- Внутренней навигации (между частями приложения), когда критичная безопасность не требуется
- Быстрого прототипирования — минимальная настройка
- Случаев без строгих требований к безопасности — тестирование, внутренние инструменты
- Legacy-приложений — поддержка старых версий Android

**App Link → для:**
- Публичного веб-контента с мобильной версией — единая ссылка для веба и приложения
- Маркетинговых кампаний — надежная маршрутизация пользователей в ваше приложение
- Сценариев с повышенными требованиями к безопасности — защита от перехвата домена другими приложениями при корректной верификации
- Согласованности с Universal Links (iOS) — единый формат ссылок на обеих платформах

## Answer (EN)

**Deep Link** typically uses a **custom URI scheme** (`myapp://`) for in-app navigation. It is simple to configure, but any app can claim the same scheme, which introduces hijacking risks and no guarantee that your app will handle the link.

**App Link** uses **HTTPS URLs** with **domain verification** via `assetlinks.json`. It provides proven domain ownership and allows direct app opening when verification succeeds. This is Google's modern standard for deep linking with domain ownership verification.

### Key Differences

| Criterion | Deep Link | App Link |
|-----------|-----------|----------|
| **Scheme** | Custom (`myapp://`) | HTTPS (`https://`) |
| **Verification** | No built-in ownership check — any app can claim the scheme | Domain verification via `assetlinks.json` — proof of ownership |
| **UX** | Depends on matches: if multiple apps handle the scheme, user sees a chooser; if only one or a default is set, it opens directly | With successful domain verification and no conflicts, links can open the app directly; on verification failure or multiple contenders, a chooser or browser may appear |
| **Android API** | All versions (API 1+) | API 23+ (Android 6.0) for official Android App Links |
| **Security** | Lower: no ownership proof, scheme can be hijacked | Higher: verified domain ownership greatly reduces hijacking risk; behavior depends on verification status and user preferences |
| **Setup** | Simple (`AndroidManifest.xml` only) | More complex (`AndroidManifest.xml` + `assetlinks.json` on server) |

### Deep Link: Implementation

**`Intent` Filter (AndroidManifest.xml):**
```xml
<activity android:name=".DetailActivity">
    <intent-filter>
        <!-- ✅ VIEW action for link handling -->
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <!-- ❌ Custom scheme — any app can declare the same -->
        <data android:scheme="myapp" android:host="detail" />
    </intent-filter>
</activity>
```

**`Activity` Handling:**
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

**Usage example:** `myapp://detail?id=123` — if multiple apps claim this scheme and matching host/path, the system shows a chooser; if only one or the user set a default, it opens that app directly.

### App Link: Implementation

**`Intent` Filter with autoVerify:**
```xml
<activity android:name=".DetailActivity">
    <!-- ✅ autoVerify=true for automatic verification of App Links -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <!-- ✅ HTTPS scheme with specific domain -->
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

**Usage example:** `https://example.com/detail?id=123` — if domain verification succeeds and there are no higher-priority handlers, the app opens directly; otherwise the system may fall back to a chooser or open in a browser.

### Verification Check

```kotlin
// API 31+ (Android 12+)
val manager = getSystemService(DomainVerificationManager::class.java)
val userState = manager.getDomainVerificationUserState(packageName)

userState?.hostToStateMap?.forEach { (domain, state) ->
    when (state) {
        // ✅ Domain verified for App Links
        DomainVerificationUserState.DOMAIN_STATE_VERIFIED -> {
            Log.d("AppLink", "$domain verified")
        }
        // ❌ Not verified / inactive
        else -> Log.w("AppLink", "$domain not verified: $state")
    }
}
```

### Choosing the Approach

**Deep Link → for:**
- Internal navigation (between screens within the app) when strong security is not required
- Rapid prototyping — minimal configuration
- Non-critical flows — testing, internal tools
- Legacy apps — broad Android version support

**App Link → for:**
- Public web content that also has an in-app representation — single URL for web and app
- Marketing campaigns — reliable routing into your app
- Security-sensitive scenarios — protect against domain hijacking by other apps when verification is correctly configured
- Alignment with iOS Universal Links — unified link strategy across platforms

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

### Prerequisites / Concepts

- [[c-compose-navigation]]
- [[c-intent]]
- [[c-fragments]]

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
