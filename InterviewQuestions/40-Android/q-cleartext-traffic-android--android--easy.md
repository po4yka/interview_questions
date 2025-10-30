---
id: 20251006-100011
title: What is cleartext traffic in Android? / Что такое cleartext traffic в Android?
aliases: [Cleartext traffic, Незашифрованный трафик, Network Security Config]
topic: android
subtopics: [networking-http, network-security-config, permissions]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-encryption, c-https-tls, q-android-keystore-system--security--medium, q-android-security-practices-checklist--android--medium, q-certificate-pinning--security--medium]
created: 2025-10-06
updated: 2025-10-29
tags: [android/networking-http, android/network-security-config, android/permissions, security, difficulty/easy]
sources: [https://developer.android.com/training/articles/security-config]
date created: Thursday, October 30th 2025, 11:17:59 am
date modified: Thursday, October 30th 2025, 12:43:39 pm
---

# Вопрос (RU)
> Что такое cleartext traffic в Android и как его контролировать?

# Question (EN)
> What is cleartext traffic in Android and how to control it?

---

## Ответ (RU)

**Cleartext traffic** — это незашифрованная HTTP-связь без TLS/SSL. Любой узел на пути передачи может перехватить и изменить данные.

**Политика Android**:
- **API 28+ (Android 9+)**: cleartext заблокирован по умолчанию
- **API 23-27**: разрешён по умолчанию
- **API <23**: всегда разрешён (устаревшие версии)

### Контроль через Network Security Config

**Для локальной разработки** (минимальные разрешения):
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <!-- ✅ Разрешить только localhost/эмулятор -->
  <domain-config cleartextTrafficPermitted="true">
    <domain includeSubdomains="true">localhost</domain>
    <domain includeSubdomains="true">10.0.2.2</domain>
  </domain-config>

  <!-- Блокировать для всех остальных -->
  <base-config cleartextTrafficPermitted="false" />
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config">
</application>
```

**Антипаттерн** (небезопасно для production):
```xml
<!-- ❌ Разрешает cleartext для ВСЕХ доменов -->
<application android:usesCleartextTraffic="true" />
```

### Типичная ошибка

При попытке HTTP-запроса на API 28+:
```
java.net.UnknownServiceException:
CLEARTEXT communication not permitted by network security policy
```

### Production стратегия

1. **HTTPS везде** — используйте TLS для всех соединений
2. **Certificate pinning** — для критичных API (банковские, платёжные)
3. **Build variant config** — cleartext только в debug-сборках
4. **ProGuard/R8** — удаляйте debug-конфигурации из release

## Answer (EN)

**Cleartext traffic** is unencrypted HTTP communication without TLS/SSL. Any node on the network path can intercept and modify the data.

**Android Policy**:
- **API 28+ (Android 9+)**: cleartext blocked by default
- **API 23-27**: allowed by default
- **API <23**: always allowed (legacy versions)

### Control via Network Security Config

**For local development** (minimal permissions):
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <!-- ✅ Allow only localhost/emulator -->
  <domain-config cleartextTrafficPermitted="true">
    <domain includeSubdomains="true">localhost</domain>
    <domain includeSubdomains="true">10.0.2.2</domain>
  </domain-config>

  <!-- Block for all others -->
  <base-config cleartextTrafficPermitted="false" />
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config">
</application>
```

**Anti-pattern** (unsafe for production):
```xml
<!-- ❌ Allows cleartext for ALL domains -->
<application android:usesCleartextTraffic="true" />
```

### Common Error

When attempting HTTP request on API 28+:
```
java.net.UnknownServiceException:
CLEARTEXT communication not permitted by network security policy
```

### Production Strategy

1. **HTTPS everywhere** — use TLS for all connections
2. **Certificate pinning** — for sensitive APIs (banking, payments)
3. **Build variant config** — cleartext only in debug builds
4. **ProGuard/R8** — strip debug configs from release

---

## Follow-ups

- How to configure different Network Security Config for debug/release builds?
- When should certificate pinning be mandatory beyond HTTPS?
- How to detect cleartext violations during automated testing?
- What happens if subdomain uses HTTP but parent domain has `cleartextTrafficPermitted="false"`?
- Can WebView bypass Network Security Config restrictions?

## References

- [[c-encryption]] — Encryption fundamentals
- [[c-https-tls]] — HTTPS/TLS concepts
- [Android Network Security Configuration](https://developer.android.com/training/articles/security-config)
- [Protecting Against Unintended Data Leakage](https://developer.android.com/privacy-and-security/security-tips#UnintendedDataLeakage)
- [[q-certificate-pinning--security--medium]] — Advanced network security

## Related Questions

### Prerequisites (Easier)
- [[c-encryption]] — What is encryption?
- [[c-https-tls]] — How does HTTPS work?
- Basic networking concepts (HTTP vs HTTPS)

### Related (Same Level)
- [[q-android-security-practices-checklist--android--medium]] — Security best practices
- [[q-android-permissions--android--easy]] — Permission system
- Network debugging with Charles/Proxyman

### Advanced (Harder)
- [[q-certificate-pinning--security--medium]] — Certificate pinning implementation
- [[q-android-keystore-system--security--medium]] — Android Keystore
- SSL/TLS handshake internals
- Man-in-the-middle attack prevention
