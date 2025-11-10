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
status: draft
moc: moc-android
related:
  - c-android-keystore
  - c-encryption
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/keystore-crypto, android/network-security-config, android/permissions, difficulty/medium, owasp, security]
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
<!-- Фрагмент network-security-config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">  <!-- ✅ Только HTTPS -->
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">ABC123...</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

(Этот конфиг должен быть подключен в `AndroidManifest.xml` через атрибут `android:networkSecurityConfig` для применения.)

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

Ключи генерируются и хранятся через Android Keystore и недоступны напрямую приложению; на устройствах с аппаратной поддержкой это существенно усложняет их извлечение.

Не хардкодить секреты (API-ключи, приватные токены) в коде/ресурсах; для чувствительных значений использовать серверную выдачу, Keystore и минимизацию чувствительных данных на клиенте.

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
// ✅ Параметризованные запросы
@Query("SELECT * FROM users WHERE email = :email")
suspend fun findUser(email: String): User?

// ❌ Конкатенация строк — уязвимость
// db.rawQuery("SELECT * FROM users WHERE email = '$email'")
```

### 5. Критические Правила

- **Permissions**: Запрашивать минимально необходимый набор, проверять во время выполнения, обосновывать пользователю.
- **Logging**: Никогда не логировать токены, пароли, PII и другие секреты, особенно в релизных сборках.
- **Biometric Auth**: Использовать BiometricPrompt / Biometric APIs для критичных операций, не хранить PIN/пароли в явном виде.
- **Root Detection**: Использовать как эвристический сигнал (может быть обойдён); при необходимости ограничивать особо чувствительные функции.
- **Dependencies**: Регулярно обновлять библиотеки и SDK, использовать сканирование уязвимостей.

---

## Answer (EN)

**Concept**: Android security requires defense-in-depth — layered protection of network, data, code, and runtime. If one layer is compromised, others continue to protect the app.

### 1. Network Security

**Certificate Pinning** helps prevent MITM attacks:

```kotlin
val pinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/ABC123...")  // ✅ Pin to certificate
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(pinner)
    .build()
```

**Network Security Config** disables HTTP for pinned domains:

```xml
<!-- Fragment of network-security-config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">  <!-- ✅ HTTPS only -->
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">ABC123...</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

(This config must be referenced from `AndroidManifest.xml` via the `android:networkSecurityConfig` attribute to take effect.)

### 2. Data Protection

**EncryptedSharedPreferences** using Android Keystore (hardware-backed when available):

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

Keys are generated and stored via Android Keystore and are not directly accessible to the app; on devices with hardware-backed support this significantly raises the bar for extraction.

Avoid hardcoding secrets (API keys, private tokens) in code/resources; use server-side issuance, Keystore, and minimize sensitive data on the client.

### 3. Code Obfuscation

**R8** makes reverse engineering harder:

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

Obfuscation does not replace proper cryptography and should not be treated as the primary protection for secrets.

### 4. SQL Injection Prevention

```kotlin
// ✅ Parameterized queries
@Query("SELECT * FROM users WHERE email = :email")
suspend fun findUser(email: String): User?

// ❌ String concatenation — vulnerability
// db.rawQuery("SELECT * FROM users WHERE email = '$email'")
```

### 5. Critical Rules

- **Permissions**: Request minimal required set, validate at runtime, provide clear justification to users.
- **Logging**: Never log tokens, passwords, PII, or other secrets, especially in release builds.
- **Biometric Auth**: Use BiometricPrompt / Biometric APIs for sensitive operations; do not store PIN/passwords in plaintext.
- **Root Detection**: Use as a heuristic signal only (bypassable); restrict especially sensitive capabilities if needed.
- **Dependencies**: Update libraries and SDKs regularly; use vulnerability scanning.

## Дополнительные вопросы (RU)

- Как безопасно обновлять (ротировать) пины сертификатов, не ломая старые версии приложения?
- В чем разница между обфускацией R8 и защитой нативного кода?
- Когда стоит отклонять использование приложения на рутованных устройствах, а когда ограничиться предупреждением?
- Как реализовать безопасную ротацию ключей для EncryptedSharedPreferences?
- Каковы компромиссы между SafetyNet и Play Integrity API?

## Follow-ups

- How do you rotate certificate pins without breaking existing app versions?
- What's the difference between R8 obfuscation and native code protection?
- When should you reject rooted devices vs. warning users?
- How to implement secure key rotation for EncryptedSharedPreferences?
- What are the trade-offs between SafetyNet and Play Integrity API?

## Ссылки (RU)

- [[c-encryption]] — Основы шифрования
- [[c-android-keystore]] — Система Android Keystore
- "OWASP Mobile Security" — https://owasp.org/www-project-mobile-top-10/
- "Android Security Best Practices" — https://developer.android.com/topic/security/best-practices

## References

- [[c-encryption]] — Encryption fundamentals
- [[c-android-keystore]] — Android Keystore system
- [OWASP Mobile Security](https://owasp.org/www-project-mobile-top-10/)
- [Android Security Best Practices](https://developer.android.com/topic/security/best-practices)

## Связанные вопросы (RU)

### Предпосылки

- Основы runtime-разрешений
- Конфигурация безопасности манифеста

### Связанные

- Шаблоны обработки разрешений
- Конфигурация сетевой безопасности

## Related Questions

### Prerequisites
- Runtime permission basics
- Manifest security configuration

### Related
- Permission handling patterns
- Network security configuration
