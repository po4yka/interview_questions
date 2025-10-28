---
id: 20251012-122781
title: App Security Best Practices / Лучшие практики безопасности приложения
aliases: ["App Security Best Practices", "Лучшие практики безопасности приложения"]
topic: android
subtopics: [keystore-crypto, permissions, network-security-config]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-encryption, c-android-keystore, q-android-runtime-permissions--android--medium, q-android-network-security--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/keystore-crypto, android/permissions, android/network-security-config, security, owasp, difficulty/medium]
---

# Вопрос (RU)

> Какие основные практики безопасности следует применять в Android-приложении?

## Ответ (RU)

**Концепция**: Безопасность Android-приложения требует многоуровневой защиты (defense-in-depth): защита сети, данных, кода и runtime-среды. Ключевой принцип — каждый уровень обеспечивает защиту, даже если другие скомпрометированы.

### 1. Защита сетевого взаимодействия

**Certificate Pinning** — привязка к конкретным сертификатам предотвращает MITM-атаки:

```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/BASE64_HASH=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    // ✅ Принудительное использование HTTPS
    .build()
```

**Network Security Config** (XML) для системной защиты:

```xml
<network-security-config>
    <!-- ✅ Запрет cleartext (HTTP) -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">BASE64_HASH=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### 2. Защита данных

**Android Keystore + EncryptedSharedPreferences** для безопасного хранения:

```kotlin
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val prefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    PrefKeyEncryptionScheme.AES256_SIV,
    PrefValueEncryptionScheme.AES256_GCM
)

// ✅ Автоматическое шифрование/дешифрование
prefs.edit().putString("token", authToken).apply()
```

**Важно**: Ключи хранятся в hardware-backed Keystore (если поддерживается), защищены от извлечения.

### 3. Обфускация кода

**R8/ProGuard** затрудняет реверс-инжиниринг:

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true  // ✅ Включить обфускацию
            proguardFiles(
                getDefaultProguardFile('proguard-android-optimize.txt'),
                'proguard-rules.pro'
            )
        }
    }
}
```

### 4. Runtime-защита

Обнаружение компрометации устройства:

```kotlin
fun isDeviceCompromised(): Boolean {
    // ✅ Проверка root
    val rootPaths = listOf("/sbin/su", "/system/bin/su")
    val hasRoot = rootPaths.any { File(it).exists() }

    // ✅ Проверка отладчика
    val isDebugged = Debug.isDebuggerConnected()

    return hasRoot || isDebugged
}
```

### 5. Валидация входных данных

```kotlin
// ✅ Параметризованные запросы (защита от SQL-инъекций)
@Query("SELECT * FROM users WHERE email = :email")
suspend fun findUser(email: String): User?

// ❌ ОПАСНО: конкатенация строк
// db.rawQuery("SELECT * FROM users WHERE email = '$email'")
```

### 6. Критические моменты

- **Permissions**: Запрашивать минимально необходимые, проверять runtime
- **Biometric Auth**: Использовать BiometricPrompt для чувствительных операций
- **Logging**: Никогда не логировать токены, пароли, PII
- **Session Management**: Таймауты, очистка токенов при выходе
- **Dependencies**: Регулярные обновления, сканирование уязвимостей

---

# Question (EN)

> What are the essential security best practices for Android applications?

## Answer (EN)

**Concept**: Android app security requires defense-in-depth: protecting network, data, code, and runtime. Key principle — each layer provides protection even if others are compromised.

### 1. Network Security

**Certificate Pinning** prevents MITM attacks by validating server certificates:

```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/BASE64_HASH=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    // ✅ Enforce HTTPS only
    .build()
```

**Network Security Config** (XML) for system-level protection:

```xml
<network-security-config>
    <!-- ✅ Disable cleartext (HTTP) -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">BASE64_HASH=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### 2. Data Protection

**Android Keystore + EncryptedSharedPreferences** for secure storage:

```kotlin
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val prefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    PrefKeyEncryptionScheme.AES256_SIV,
    PrefValueEncryptionScheme.AES256_GCM
)

// ✅ Automatic encryption/decryption
prefs.edit().putString("token", authToken).apply()
```

**Important**: Keys stored in hardware-backed Keystore (when supported), protected from extraction.

### 3. Code Obfuscation

**R8/ProGuard** makes reverse engineering difficult:

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true  // ✅ Enable obfuscation
            proguardFiles(
                getDefaultProguardFile('proguard-android-optimize.txt'),
                'proguard-rules.pro'
            )
        }
    }
}
```

### 4. Runtime Protection

Detecting device compromise:

```kotlin
fun isDeviceCompromised(): Boolean {
    // ✅ Check for root
    val rootPaths = listOf("/sbin/su", "/system/bin/su")
    val hasRoot = rootPaths.any { File(it).exists() }

    // ✅ Check for debugger
    val isDebugged = Debug.isDebuggerConnected()

    return hasRoot || isDebugged
}
```

### 5. Input Validation

```kotlin
// ✅ Parameterized queries (SQL injection protection)
@Query("SELECT * FROM users WHERE email = :email")
suspend fun findUser(email: String): User?

// ❌ DANGEROUS: string concatenation
// db.rawQuery("SELECT * FROM users WHERE email = '$email'")
```

### 6. Critical Considerations

- **Permissions**: Request minimal necessary, validate at runtime
- **Biometric Auth**: Use BiometricPrompt for sensitive operations
- **Logging**: Never log tokens, passwords, PII
- **Session Management**: Timeouts, token clearing on logout
- **Dependencies**: Regular updates, vulnerability scanning

## Follow-ups

- How do you rotate certificate pins without breaking existing app versions?
- What's the difference between R8 obfuscation and code encryption?
- How to balance security and performance for biometric authentication?
- When should you reject rooted devices vs. just warning users?
- How to implement secure key backup for encrypted data recovery?

## References

- [[c-encryption]] — Encryption fundamentals
- [[c-android-keystore]] — Android Keystore system
- [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/)
- [Android Security Best Practices](https://developer.android.com/topic/security/best-practices)

## Related Questions

### Prerequisites
- [[q-android-runtime-permissions--android--easy]] — Runtime permission basics
- [[q-android-manifest-security--android--easy]] — Manifest security configuration

### Related
- [[q-android-runtime-permissions--android--medium]] — Permission handling patterns
- [[q-android-network-security--android--medium]] — Network security in depth
- [[q-android-data-encryption--android--medium]] — Encryption strategies

### Advanced
- [[q-android-safetynet-attestation--android--hard]] — Device integrity verification
- [[q-android-reverse-engineering-prevention--android--hard]] — Advanced protection techniques