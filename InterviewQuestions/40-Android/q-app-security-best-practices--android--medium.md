---
id: android-277
title: App Security Best Practices / Лучшие практики безопасности приложения
aliases: [App Security Best Practices, Лучшие практики безопасности приложения]
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
status: reviewed
moc: moc-android
related:
  - c-android-keystore
  - c-encryption
created: 2025-10-15
updated: 2025-10-30
sources: []
tags: [android/keystore-crypto, android/network-security-config, android/permissions, difficulty/medium, owasp, security]
date created: Thursday, October 30th 2025, 11:43:21 am
date modified: Sunday, November 2nd 2025, 12:54:53 pm
---

# Вопрос (RU)

> Какие основные практики безопасности следует применять в Android-приложении?


# Question (EN)

> What are the essential security best practices for Android applications?


---

## Ответ (RU)

**Концепция**: Безопасность Android требует defense-in-depth — многоуровневой защиты сети, данных, кода и runtime. Если один слой скомпрометирован, остальные продолжают защищать приложение.

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

**Network Security Config** запрещает HTTP:

```xml
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">  <!-- ✅ Только HTTPS -->
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">ABC123...</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### 2. Защита Данных

**EncryptedSharedPreferences** с hardware-backed ключами:

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

Ключи хранятся в Android Keystore и не могут быть извлечены.

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

### 4. Защита От SQL-инъекций

```kotlin
// ✅ Параметризованные запросы
@Query("SELECT * FROM users WHERE email = :email")
suspend fun findUser(email: String): User?

// ❌ Конкатенация строк — уязвимость
// db.rawQuery("SELECT * FROM users WHERE email = '$email'")
```

### 5. Критические Правила

- **Permissions**: Минимальный набор, проверка во время выполнения
- **Logging**: Никогда не логировать токены, пароли, PII
- **Biometric Auth**: BiometricPrompt для критичных операций
- **Root Detection**: Ограничить функциональность на скомпрометированных устройствах
- **Dependencies**: Регулярное обновление, сканирование уязвимостей

---


## Answer (EN)

**Concept**: Android security requires defense-in-depth — layered protection of network, data, code, and runtime. If one layer is compromised, others continue to protect the app.

### 1. Network Security

**Certificate Pinning** prevents MITM attacks:

```kotlin
val pinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/ABC123...")  // ✅ Pin to certificate
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(pinner)
    .build()
```

**Network Security Config** disables HTTP:

```xml
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">  <!-- ✅ HTTPS only -->
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">ABC123...</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### 2. Data Protection

**EncryptedSharedPreferences** with hardware-backed keys:

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

Keys are stored in Android Keystore and cannot be extracted.

### 3. Code Obfuscation

**R8** makes reverse engineering difficult:

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true  // ✅ Obfuscation + dead code removal
            proguardFiles(
                getDefaultProguardFile('proguard-android-optimize.txt'),
                'proguard-rules.pro'
            )
        }
    }
}
```

### 4. SQL Injection Prevention

```kotlin
// ✅ Parameterized queries
@Query("SELECT * FROM users WHERE email = :email")
suspend fun findUser(email: String): User?

// ❌ String concatenation — vulnerability
// db.rawQuery("SELECT * FROM users WHERE email = '$email'")
```

### 5. Critical Rules

- **Permissions**: Minimal set, runtime validation
- **Logging**: Never log tokens, passwords, PII
- **Biometric Auth**: BiometricPrompt for sensitive operations
- **Root Detection**: Limit functionality on compromised devices
- **Dependencies**: Regular updates, vulnerability scanning

## Follow-ups

- How do you rotate certificate pins without breaking existing app versions?
- What's the difference between R8 obfuscation and native code protection?
- When should you reject rooted devices vs. warning users?
- How to implement secure key rotation for EncryptedSharedPreferences?
- What are the trade-offs between SafetyNet and Play Integrity API?

## References

- [[c-encryption]] — Encryption fundamentals
- [[c-android-keystore]] — Android Keystore system
- [OWASP Mobile Security](https://owasp.org/www-project-mobile-top-10/)
- [Android Security Best Practices](https://developer.android.com/topic/security/best-practices)

## Related Questions

### Prerequisites
 — Runtime permission basics
 — Manifest security configuration

### Related
 — Permission handling patterns
 — Network security configuration
