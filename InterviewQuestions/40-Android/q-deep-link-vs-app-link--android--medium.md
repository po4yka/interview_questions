---
id: 20251020-200000
title: Deep Link Vs App Link / Deep Link против App Link
aliases:
  - Deep Link Vs App Link
  - Deep Link против App Link
topic: android
subtopics:
  - ui-navigation
  - app-startup
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-android-intent-system--android--medium
  - q-android-navigation-component--android--medium
  - q-android-webview-basics--android--easy
created: 2025-10-20
updated: 2025-10-20
tags:
  - android/ui-navigation
  - android/app-startup
  - app-linking
  - app-links
  - deep-linking
  - https
  - navigation
  - uri
  - verification
  - difficulty/medium
source: https://developer.android.com/training/app-links
source_note: Android App Links documentation
---
# Вопрос (RU)
> Какие особенности отличия deep link от app link?

# Question (EN)
> What are the differences between deep links and app links?

## Ответ (RU)

**Deep Link** работает через **пользовательскую URI схему** (например, `myapp://`) и требует конфигурации `intent-filter`.

**App Link** использует **HTTP/HTTPS URLs** и требует **верификации владения доменом** через файл `assetlinks.json`.

### Теория: Deep Link vs App Link

**Основные концепции:**
- **Deep Link** - пользовательская URI схема для внутренней навигации
- **App Link** - верифицированные HTTP/HTTPS ссылки для веб-контента
- **Intent Filter** - механизм обработки входящих намерений
- **Domain Verification** - проверка владения доменом для App Links
- **User Experience** - различный опыт пользователя для каждого типа

**Принципы работы:**
- Deep Links используют пользовательские схемы URI
- App Links требуют верификации домена через assetlinks.json
- Оба типа используют Intent Filter для обработки
- App Links обеспечивают лучшую безопасность
- Deep Links проще в настройке

### Сравнение Deep Link и App Link

| Критерий | Deep Link | App Link |
|----------|-----------|----------|
| **Схема** | Пользовательская (`myapp://`) | Только HTTPS (`https://`) |
| **Верификация** | Отсутствует | Требуется верификация домена |
| **Пользовательский опыт** | Показывает диалог выбора приложения | Открывает приложение напрямую |
| **Версия Android** | Все версии | Android 6.0+ (API 23+) |
| **Безопасность** | Низкая (любой может заявить схему) | Высокая (верифицированное владение) |
| **Сложность настройки** | Простая | Сложная (требует файл на сервере) |
| **Случай использования** | Внутренняя навигация | Верифицированный веб-контент |

### Deep Links

**Теоретические основы:**
Deep Links используют пользовательские URI схемы для навигации внутри приложения. Они просты в настройке, но не обеспечивают верификацию владения схемой.

**Характеристики:**
- Пользовательская URI схема (например, `myapp://`, `mydomain://`)
- Работает на всех версиях Android
- Простая настройка (без конфигурации сервера)
- Не верифицируется - любое приложение может заявить ту же схему
- Показывает диалог неоднозначности, если несколько приложений обрабатывают URI

**Компактная реализация:**
```xml
<activity android:name=".DetailActivity">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="myapp" android:host="detail" />
    </intent-filter>
</activity>
```

**Обработка в коде:**
```kotlin
class DetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val uri = intent.data
        if (uri != null) {
            val itemId = uri.getQueryParameter("id")
            // Обработка параметров
        }
    }
}
```

### App Links

**Теоретические основы:**
App Links используют HTTP/HTTPS URLs и требуют верификации владения доменом. Они обеспечивают лучшую безопасность и пользовательский опыт.

**Характеристики:**
- Использует HTTP/HTTPS URLs
- Требует верификации домена через assetlinks.json
- Открывает приложение напрямую без диалога выбора
- Работает на Android 6.0+ (API 23+)
- Высокая безопасность через верификацию

**Компактная реализация:**
```xml
<activity android:name=".DetailActivity">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="https" android:host="example.com" />
    </intent-filter>
</activity>
```

**Файл assetlinks.json:**
```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.example.app",
    "sha256_cert_fingerprints": ["AA:BB:CC:..."]
  }
}]
```

### Верификация App Links

**Теоретические основы:**
Верификация App Links происходит через файл assetlinks.json на сервере. Android проверяет соответствие между доменом и приложением.

**Процесс верификации:**
1. Android запрашивает `https://domain.com/.well-known/assetlinks.json`
2. Проверяет соответствие package_name и fingerprint
3. Устанавливает приложение как обработчик по умолчанию
4. Открывает приложение напрямую для верифицированных ссылок

**Проверка статуса верификации:**
```kotlin
val packageManager = packageManager
val domainVerificationState = packageManager.getDomainVerificationUserState(packageName)
val verifiedDomains = domainVerificationState?.verifiedDomains ?: emptySet()
```

### Выбор между Deep Link и App Link

**Теоретические принципы:**
Выбор между Deep Link и App Link зависит от требований безопасности, пользовательского опыта и сложности настройки.

**Deep Link подходит для:**
- Внутренней навигации в приложении
- Простых случаев использования
- Когда не требуется верификация домена
- Быстрой разработки и тестирования

**App Link подходит для:**
- Веб-контента, связанного с приложением
- Когда требуется высокая безопасность
- Публичных ссылок для пользователей
- Когда важен прямой доступ к приложению

### Лучшие практики

**Теоретические принципы:**
- Используйте App Links для публичного контента
- Используйте Deep Links для внутренней навигации
- Обрабатывайте ошибки и edge cases
- Тестируйте на разных устройствах и версиях Android
- Документируйте схемы URI

**Практические рекомендации:**
- Всегда проверяйте входящие данные
- Используйте валидацию параметров
- Обрабатывайте случаи отсутствия приложения
- Предоставляйте fallback для веб-версии
- Тестируйте верификацию App Links

## Answer (EN)

**Deep Link** works through a **custom URI scheme** (e.g., `myapp://`) and requires `intent-filter` configuration.

**App Link** uses **HTTP/HTTPS URLs** and requires **domain ownership verification** through the `assetlinks.json` file.

### Theory: Deep Link vs App Link

**Core Concepts:**
- **Deep Link** - custom URI scheme for internal navigation
- **App Link** - verified HTTP/HTTPS links for web content
- **Intent Filter** - mechanism for handling incoming intents
- **Domain Verification** - domain ownership verification for App Links
- **User Experience** - different user experience for each type

**Working Principles:**
- Deep Links use custom URI schemes
- App Links require domain verification through assetlinks.json
- Both types use Intent Filter for handling
- App Links provide better security
- Deep Links are simpler to set up

### Deep Link vs App Link Comparison

| Criterion | Deep Link | App Link |
|-----------|-----------|----------|
| **Scheme** | Custom (`myapp://`) | HTTPS only (`https://`) |
| **Verification** | None | Domain verification required |
| **User Experience** | Shows app chooser dialog | Opens app directly |
| **Android Version** | All versions | Android 6.0+ (API 23+) |
| **Security** | Low (anyone can claim scheme) | High (verified ownership) |
| **Setup Complexity** | Simple | Complex (requires server file) |
| **Use Case** | Internal navigation | Verified web content |

### Deep Links

**Theoretical Foundations:**
Deep Links use custom URI schemes for navigation within the application. They are simple to set up but don't provide scheme ownership verification.

**Characteristics:**
- Custom URI scheme (e.g., `myapp://`, `mydomain://`)
- Works on all Android versions
- Simple setup (no server configuration)
- Not verified - any app can claim the same scheme
- Shows disambiguation dialog if multiple apps handle the URI

**Compact Implementation:**
```xml
<activity android:name=".DetailActivity">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="myapp" android:host="detail" />
    </intent-filter>
</activity>
```

**Code Handling:**
```kotlin
class DetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val uri = intent.data
        if (uri != null) {
            val itemId = uri.getQueryParameter("id")
            // Handle parameters
        }
    }
}
```

### App Links

**Theoretical Foundations:**
App Links use HTTP/HTTPS URLs and require domain ownership verification. They provide better security and user experience.

**Characteristics:**
- Uses HTTP/HTTPS URLs
- Requires domain verification through assetlinks.json
- Opens app directly without chooser dialog
- Works on Android 6.0+ (API 23+)
- High security through verification

**Compact Implementation:**
```xml
<activity android:name=".DetailActivity">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="https" android:host="example.com" />
    </intent-filter>
</activity>
```

**assetlinks.json file:**
```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.example.app",
    "sha256_cert_fingerprints": ["AA:BB:CC:..."]
  }
}]
```

### App Links Verification

**Theoretical Foundations:**
App Links verification happens through the assetlinks.json file on the server. Android verifies the correspondence between the domain and the application.

**Verification Process:**
1. Android requests `https://domain.com/.well-known/assetlinks.json`
2. Checks correspondence between package_name and fingerprint
3. Sets app as default handler
4. Opens app directly for verified links

**Verification Status Check:**
```kotlin
val packageManager = packageManager
val domainVerificationState = packageManager.getDomainVerificationUserState(packageName)
val verifiedDomains = domainVerificationState?.verifiedDomains ?: emptySet()
```

### Choosing Between Deep Link and App Link

**Theoretical Principles:**
The choice between Deep Link and App Link depends on security requirements, user experience, and setup complexity.

**Deep Link is suitable for:**
- Internal navigation within the app
- Simple use cases
- When domain verification is not required
- Quick development and testing

**App Link is suitable for:**
- Web content related to the app
- When high security is required
- Public links for users
- When direct app access is important

### Best Practices

**Theoretical Principles:**
- Use App Links for public content
- Use Deep Links for internal navigation
- Handle errors and edge cases
- Test on different devices and Android versions
- Document URI schemes

**Practical Recommendations:**
- Always validate incoming data
- Use parameter validation
- Handle cases where app is not installed
- Provide fallback for web version
- Test App Links verification

## Follow-ups

- How do you handle deep links when the app is not installed?
- What are the security implications of each approach?
- How do you test deep links and app links?
