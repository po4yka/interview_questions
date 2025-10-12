---
id: 20251006-100011
title: "What is cleartext traffic in Android? / Что такое cleartext traffic в Android?"
aliases: []

# Classification
topic: android
subtopics: [security, network, https, cleartext]
question_kind: explanation
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android, 20251006-100011, difficulty/easy]
---
# Question (EN)
> What is cleartext traffic in Android?
# Вопрос (RU)
> Что такое cleartext traffic в Android?

---

## Answer (EN)

**Cleartext traffic** refers to unencrypted network communication sent over HTTP instead of HTTPS. Starting with Android 9 (API 28), cleartext traffic is disabled by default for security.

### What is Cleartext Traffic?

**Cleartext (HTTP):** Data sent without encryption
```
Client ─── HTTP (plaintext) ───> Server
Request: GET /api/user HTTP/1.1
         Host: example.com
         Authorization: Bearer secret_token  ← Visible to attackers!
```

**Encrypted (HTTPS):** Data encrypted with TLS/SSL
```
Client ─── HTTPS (encrypted) ───> Server
Request: [encrypted data]  ← Protected from eavesdropping
```

### Android Cleartext Policy

**Android 9+** - Cleartext disabled by default
**Android 8.1 and below** - Cleartext allowed by default

### Allowing Cleartext Traffic (Development Only)

#### Method 1: Network Security Configuration (Recommended)

```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Allow cleartext for specific domains (development only) -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">localhost</domain>
        <domain includeSubdomains="true">10.0.2.2</domain>  <!-- Android Emulator -->
        <domain includeSubdomains="true">192.168.1.100</domain>  <!-- Local dev server -->
    </domain-config>

    <!-- Enforce HTTPS for production -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

**AndroidManifest.xml:**
```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
</application>
```

#### Method 2: Allow All Cleartext (NOT Recommended for Production)

```xml
<!-- AndroidManifest.xml -->
<application
    android:usesCleartextTraffic="true"
    ...>
</application>
```

**⚠️ Warning:** This allows cleartext for ALL domains - insecure!

### Production Best Practices

```xml
<!-- res/xml/network_security_config.xml (Production) -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Enforce HTTPS everywhere -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Certificate pinning for extra security -->
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2026-01-01">
            <pin digest="SHA-256">base64encodedpin==</pin>
            <pin digest="SHA-256">backuppin==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### Build Variant Configuration

```kotlin
// build.gradle.kts
android {
    buildTypes {
        debug {
            // Allow cleartext for debug builds only
            manifestPlaceholders["usesCleartextTraffic"] = "true"
        }
        release {
            // Enforce HTTPS for release builds
            manifestPlaceholders["usesCleartextTraffic"] = "false"
        }
    }
}
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:usesCleartextTraffic="${usesCleartextTraffic}"
    ...>
</application>
```

### Detecting Cleartext Issues

**Error message:**
```
java.net.UnknownServiceException: CLEARTEXT communication to example.com not permitted by network security policy
```

**Solution:** Either use HTTPS or explicitly allow cleartext for that domain (development only).

### Security Recommendations

**✅ DO:**
- Use HTTPS everywhere in production
- Implement certificate pinning for sensitive APIs
- Use Network Security Configuration for granular control
- Allow cleartext only for localhost/development servers

**❌ DON'T:**
- Use `android:usesCleartextTraffic="true"` in production
- Send sensitive data over HTTP
- Allow cleartext for production APIs
- Ignore cleartext warnings

### Summary

**Cleartext traffic** = unencrypted HTTP communication (insecure)
**Android 9+** disables it by default for security
**Development:** Use Network Security Configuration to allow specific domains
**Production:** Always use HTTPS with certificate pinning

## Ответ (RU)

**Cleartext traffic** - это незашифрованное сетевое соединение через HTTP вместо HTTPS. Начиная с Android 9 (API 28), cleartext traffic отключен по умолчанию для безопасности.

### Что такое Cleartext Traffic?

**Cleartext (HTTP):** Данные без шифрования
```
Клиент ─── HTTP (открытый текст) ───> Сервер
Запрос: GET /api/user HTTP/1.1
        Host: example.com
        Authorization: Bearer secret_token  ← Видно атакующим!
```

**Зашифрованный (HTTPS):** Данные зашифрованы TLS/SSL
```
Клиент ─── HTTPS (зашифрованные данные) ───> Сервер
Запрос: [зашифрованные данные]  ← Защищено от прослушивания
```

### Политика Cleartext в Android

**Android 9+** - Cleartext отключен по умолчанию
**Android 8.1 и ниже** - Cleartext разрешен по умолчанию

### Разрешение Cleartext Traffic (Только для разработки)

#### Метод 1: Network Security Configuration (Рекомендуется)

```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Разрешить cleartext для конкретных доменов (только разработка) -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">localhost</domain>
        <domain includeSubdomains="true">10.0.2.2</domain>  <!-- Эмулятор Android -->
        <domain includeSubdomains="true">192.168.1.100</domain>  <!-- Локальный dev сервер -->
    </domain-config>

    <!-- Принудительный HTTPS для продакшена -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

**AndroidManifest.xml:**
```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
</application>
```

#### Метод 2: Разрешить весь Cleartext (НЕ рекомендуется для продакшена)

```xml
<!-- AndroidManifest.xml -->
<application
    android:usesCleartextTraffic="true"
    ...>
</application>
```

**⚠️ Предупреждение:** Это разрешает cleartext для ВСЕХ доменов - небезопасно!

### Лучшие практики для продакшена

```xml
<!-- res/xml/network_security_config.xml (Продакшен) -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Принудительный HTTPS везде -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Certificate pinning для дополнительной безопасности -->
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2026-01-01">
            <pin digest="SHA-256">base64encodedpin==</pin>
            <pin digest="SHA-256">backuppin==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### Конфигурация Build Variant

```kotlin
// build.gradle.kts
android {
    buildTypes {
        debug {
            // Разрешить cleartext только для debug сборок
            manifestPlaceholders["usesCleartextTraffic"] = "true"
        }
        release {
            // Принудительный HTTPS для release сборок
            manifestPlaceholders["usesCleartextTraffic"] = "false"
        }
    }
}
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:usesCleartextTraffic="${usesCleartextTraffic}"
    ...>
</application>
```

### Обнаружение проблем с Cleartext

**Сообщение об ошибке:**
```
java.net.UnknownServiceException: CLEARTEXT communication to example.com not permitted by network security policy
```

**Решение:** Используйте HTTPS или явно разрешите cleartext для этого домена (только для разработки).

### Рекомендации по безопасности

**✅ ДЕЛАТЬ:**
- Использовать HTTPS везде в продакшене
- Реализовать certificate pinning для чувствительных API
- Использовать Network Security Configuration для детального контроля
- Разрешать cleartext только для localhost/серверов разработки

**❌ НЕ ДЕЛАТЬ:**
- Использовать `android:usesCleartextTraffic="true"` в продакшене
- Отправлять чувствительные данные через HTTP
- Разрешать cleartext для production API
- Игнорировать предупреждения о cleartext

### Резюме

**Cleartext traffic** = незашифрованное HTTP соединение (небезопасно)
**Android 9+** отключает его по умолчанию для безопасности
**Разработка:** Используйте Network Security Configuration для конкретных доменов
**Продакшен:** Всегда используйте HTTPS с certificate pinning

---

## Related Questions
- Related question 1
- Related question 2

## References
- [Android Documentation](https://developer.android.com)
