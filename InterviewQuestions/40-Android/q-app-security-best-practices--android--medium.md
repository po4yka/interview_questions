---
id: android-277
title: App Security Best Practices / 1b4347483835 3f40303a42383a38 3135373e3f30413d3e414238
  3f40383b3e36353d384f
aliases:
- 1b4347483835 3f40303a42383a38 3135373e3f30413d3e414238 3f40383b3e36353d384f
- App Security Best Practices
topic: android
subtopics:
- keystore-crypto
- network-security-config
- permissions
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-keystore
- c-encryption
- q-android-security-best-practices--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/keystore-crypto
- android/network-security-config
- android/permissions
- difficulty/medium
- owasp
- security
anki_cards:
- slug: android-277-0-en
  language: en
  anki_id: 1768364267823
  synced_at: '2026-01-14T09:17:53.403238'
- slug: android-277-0-ru
  language: ru
  anki_id: 1768364267846
  synced_at: '2026-01-14T09:17:53.405571'
---
# Вопрос (RU)

> Какие основные практики безопасности следует применять в Android-приложении?

# Question (EN)

> What are the essential security best practices for Android applications?

---

## Ответ (RU)

**Концепция**: Безопасность Android требует многоуровневой защиты (defense-in-depth) сети, данных, кода и runtime. Если один слой скомпрометирован, остальные продолжают защищать приложение.

### 1. Защита Сетевых Соединений

**Certificate Pinning** предотвращает MITM-атаки:

```kotlin
val pinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/ABC123...")  // ✅ Привязка к сертификату
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(pinner)
    .build()
```

**Network Security Config** запрещает HTTP и может:
- отключать нешифрованный HTTP для доменов (cleartextTrafficPermitted="false"), принуждая HTTPS; и
- опционально настраивать certificate pinning на уровне платформы.

```xml
<!-- Фрагмент network-security-config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">  <!-- ✅ Только HTTPS для этого домена -->
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">ABC123...</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

(Этот конфиг должен быть подключен в `AndroidManifest.xml` через атрибут `android:networkSecurityConfig` для применения. Будьте осторожны при одновременном использовании pinning в `OkHttp` и в XML, чтобы не дублировать пины без продуманной стратегии ротации.)

### 2. Защита Данных

**EncryptedSharedPreferences** с использованием Android Keystore (при наличии — аппаратно защищённого):

```kotlin
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)  // ✅ AES-256-GCM
    .build()

val prefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    PrefKeyEncryptionScheme.AES256_SIV,
    PrefValueEncryptionScheme.AES256_GCM
)
prefs.edit().putString("token", authToken).apply()
```

Ключи генерируются и хранятся через Android Keystore и недоступны напрямую для экспорта; на устройствах с аппаратной поддержкой это существенно усложняет их извлечение. Однако вредоносный код, выполняющийся в том же контексте приложения, всё ещё может запрашивать криптооперации с этими ключами, поэтому это элемент defense-in-depth, а не абсолютная защита.

Не хардкодить секреты (API-ключи, приватные токены) в коде/ресурсах; для чувствительных значений использовать серверную выдачу, хранение с использованием Keystore при необходимости и минимизацию чувствительных данных на клиенте.

### 3. Обфускация Кода

**R8** затрудняет реверс-инжиниринг:

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true  // ✅ Обфускация + удаление неиспользуемого кода
            proguardFiles(
                getDefaultProguardFile('proguard-android-optimize.txt'),
                'proguard-rules.pro'
            )
        }
    }
}
```

Обфускация не заменяет криптографию и не должна рассматриваться как основная защита секрета.

### 4. Защита От SQL-инъекций

```kotlin
// ✅ Параметризованный запрос через Room @Query
@Query("SELECT * FROM users WHERE email = :email")
suspend fun findUser(email: String): User?

// ❌ Конкатенация строк — уязвимость
// db.rawQuery("SELECT * FROM users WHERE email = '$email'")
```

### 5. Критические Правила

- **Permissions**: Запрашивать минимально необходимый набор, проверять во время выполнения, обосновывать пользователю.
- **Logging**: Никогда не логировать токены, пароли, PII и другие секреты, особенно в релизных сборках.
- **Biometric Auth**: Использовать BiometricPrompt / Biometric APIs для критичных операций, обычно для разблокировки ключей из Keystore (`setUserAuthenticationRequired`); не считать одну только биометрию полноценной заменой аутентификации и авторизации на сервере.
- **Root Detection**: Использовать только как эвристический сигнал (может быть обойдён); не полагаться на него как на единственный контроль. В особо чувствительных приложениях можно ограничивать отдельные функции при обнаружении высокорискованных сигналов (например, root).
- **Dependencies**: Регулярно обновлять библиотеки и SDK, использовать инструменты сканирования уязвимостей зависимостей.

---

## Answer (EN)

**Concept**: Android security requires defense-in-depth layered protection of network, data, code, and runtime. If one layer is compromised, others continue to protect the app.

### 1. Network Security

**Certificate Pinning** helps prevent MITM attacks:

```kotlin
val pinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/ABC123...")  //  Pin to certificate
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(pinner)
    .build()
```

**Network Security Config** can:
- disable cleartext HTTP for specific domains (cleartextTrafficPermitted="false"), enforcing HTTPS; and
- optionally configure certificate pinning at the platform level.

```xml
<!-- Fragment of network-security-config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">  <!--  HTTPS only for this domain -->
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">ABC123...</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

(This config must be referenced from `AndroidManifest.xml` via the `android:networkSecurityConfig` attribute to take effect. Be careful when combining `OkHttp` pinning and XML pinning to avoid duplicated pins without a rotation strategy.)

### 2. Data Protection

**EncryptedSharedPreferences** using Android Keystore (hardware-backed when available):

```kotlin
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)  //  AES-256-GCM
    .build()

val prefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    PrefKeyEncryptionScheme.AES256_SIV,
    PrefValueEncryptionScheme.AES256_GCM
)
prefs.edit().putString("token", authToken).apply()
```

Keys are generated and stored via Android Keystore and are not directly exportable; on devices with hardware-backed support this significantly increases resistance to key extraction. However, malware running in the same app context can still request crypto operations, so this is defense-in-depth, not absolute protection.

Avoid hardcoding secrets (API keys, private tokens) in code/resources; prefer server-side issuance, Keystore-backed storage where necessary, and minimize sensitive data on the client.

### 3. Code Obfuscation

**R8** makes reverse engineering harder:

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true  //  Obfuscation + dead code removal
            proguardFiles(
                getDefaultProguardFile('proguard-android-optimize.txt'),
                'proguard-rules.pro'
            )
        }
    }
}
```

Obfuscation does not replace proper cryptography and should not be treated as the primary protection for secrets.

### 4. SQL Injection Prevention

```kotlin
//  Parameterized query via Room @Query
@Query("SELECT * FROM users WHERE email = :email")
suspend fun findUser(email: String): User?

//  String concatenation in raw queries is vulnerable
// db.rawQuery("SELECT * FROM users WHERE email = '$email'")
```

### 5. Critical Rules

- **Permissions**: `Request` minimal required set, validate at runtime, and clearly justify to users.
- **Logging**: Never log tokens, passwords, PII, or other secrets, especially in release builds.
- **Biometric Auth**: Use BiometricPrompt / Biometric APIs for sensitive operations, typically to unlock Keystore-backed keys (`setUserAuthenticationRequired`); do not treat biometrics alone as a full replacement for proper authentication and authorization on the server.
- **Root Detection**: Use only as a heuristic signal (easily bypassed); do not rely on it as a sole control. For highly sensitive apps, you may restrict certain capabilities when high-risk signals (e.g., root) are detected.
- **Dependencies**: Update libraries and SDKs regularly; use dependency and vulnerability scanning tools.

## Follow-ups (RU)

- Как вы будете реализовывать ротацию сертификатных пинов, чтобы не "сломать" старые версии приложения?
- В чем разница между обфускацией R8 и защитой нативного кода?
- В каких случаях стоит не пускать пользователей с root, а в каких достаточно предупредить?
- Как реализовать безопасную ротацию ключей для `EncryptedSharedPreferences`?
- Каковы trade-off'ы между SafetyNet и Play Integrity API?

## Follow-ups

- How do you rotate certificate pins without breaking existing app versions?
- What's the difference between R8 obfuscation and native code protection?
- When should you reject rooted devices vs. warning users?
- How to implement secure key rotation for `EncryptedSharedPreferences`?
- What are the trade-offs between SafetyNet and Play Integrity API?

## References (RU)

- [[c-encryption]]
- [[c-android-keystore]]  Android Keystore
- "OWASP Mobile Security"  https://owasp.org/www-project-mobile-top-10/
- "Android Security Best Practices"  https://developer.android.com/topic/security/best-practices

## References

- [[c-encryption]]  Encryption fundamentals
- [[c-android-keystore]]  Android Keystore system
- [OWASP Mobile Security](https://owasp.org/www-project-mobile-top-10/)
- [Android Security Best Practices](https://developer.android.com/topic/security/best-practices)

## Related Questions (RU)

### Предпосылки
- Базовые принципы runtime-разрешений
- Настройка безопасности в `AndroidManifest` и Network Security Config

### Связанные
- Подходы к обработке разрешений
- Настройка Network Security Config

## Related Questions

### Prerequisites
- Runtime permission basics
- Manifest security configuration

### Related
- Permission handling patterns
- Network security configuration
