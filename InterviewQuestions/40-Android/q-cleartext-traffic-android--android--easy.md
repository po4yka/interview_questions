---
id: android-033
title: What is cleartext traffic in Android? / Что такое cleartext traffic в Android?
aliases: [Cleartext traffic, Network Security Config, Незашифрованный трафик]
topic: android
subtopics:
  - network-security-config
  - networking-http
  - permissions
question_kind: android
difficulty: easy
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-encryption
  - q-android-manifest-file--android--easy
  - q-android-security-best-practices--android--medium
  - q-android-security-practices-checklist--android--medium
created: 2025-10-06
updated: 2025-11-10
tags: [android/network-security-config, android/networking-http, android/permissions, difficulty/easy, security]
sources:
  - "https://developer.android.com/training/articles/security-config"
date created: Saturday, November 1st 2025, 1:24:15 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---
# Вопрос (RU)
> Что такое cleartext traffic в Android и как его контролировать?

# Question (EN)
> What is cleartext traffic in Android and how to control it?

---

## Ответ (RU)

**Cleartext traffic** — это незашифрованная HTTP-связь без TLS/SSL (HTTP, WebSocket без wss и т.п.). Любой узел на пути передачи может перехватить и изменить данные.

**Политика Android (упрощённо):**
- **API 28+ (Android 9+)**: действует принцип «secure by default». По умолчанию cleartext-трафик разрешён только если:
  - приложение явно разрешает его через `android:usesCleartextTraffic="true"` в `<application>` ИЛИ
  - домен явно разрешён в Network Security Config (`cleartextTrafficPermitted="true"`).
  В остальных случаях попытки cleartext-запросов приводят к ошибке политики безопасности сети. Практически: относитесь к незашифрованному трафику как к тому, что должно быть явно разрешено и локализовано.
- **API 23-27**: cleartext разрешён по умолчанию; его можно ограничить с помощью `android:usesCleartextTraffic` и (на поддерживаемых версиях) Network Security Config. Без явных ограничений HTTP-соединения будут работать.
- **API <23**: cleartext всегда разрешён (устаревшие версии, поддержки Network Security Config нет).

`android:usesCleartextTraffic` — грубый (app-wide) флаг. Network Security Config даёт более тонкий (per-domain) контроль и предпочтителен для production.

### Контроль Через Network Security Config

**Для локальной разработки** (минимальные разрешения):
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <!-- ✅ Разрешить cleartext только для локальных адресов -->
  <domain-config cleartextTrafficPermitted="true">
    <domain>localhost</domain>
    <domain>10.0.2.2</domain>
  </domain-config>

  <!-- Блокировать cleartext для всех остальных доменов по умолчанию -->
  <base-config cleartextTrafficPermitted="false" />
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config">
</application>
```

(Примечание: `domain-config` переопределяет `base-config` для перечисленных доменов.)

**Антипаттерн** (небезопасно для production):
```xml
<!-- ❌ Разрешает cleartext для ВСЕХ доменов приложения -->
<application android:usesCleartextTraffic="true" />
```

### Типичная Ошибка

При попытке HTTP-запроса на API 28+ без разрешённого cleartext:
```java
java.net.UnknownServiceException:
CLEARTEXT communication not permitted by network security policy
```

### Production Стратегия

1. **HTTPS везде** — используйте TLS для всех соединений.
2. **Certificate pinning** — для критичных API (банковские, платёжные и т.п.).
3. **Build variants** — разрешайте cleartext только в debug-сборках (отдельные Network Security Config и манифесты для debug/release).
4. **Сборочный пайплайн** — убедитесь, что debug-конфигурации (включая XML и `usesCleartextTraffic="true"`) не попадают в release; это решается через productFlavors/Build Types, а не ProGuard/R8 напрямую.

## Answer (EN)

**Cleartext traffic** is unencrypted HTTP communication without TLS/SSL (e.g., HTTP, non-TLS WebSocket). Any node on the network path can intercept and modify the data.

**Android policy (simplified):**
- **API 28+ (Android 9+)**: follows a "secure by default" approach. By default, cleartext traffic is only allowed if:
  - the app explicitly allows it via `android:usesCleartextTraffic="true"` on `<application>`, OR
  - the target domain is explicitly allowed in the Network Security Config (`cleartextTrafficPermitted="true"`).
  Otherwise, cleartext requests will fail with a network security policy error. Practically: treat cleartext as something that must be explicitly and narrowly allowed.
- **API 23-27**: cleartext is allowed by default; it can be restricted using `android:usesCleartextTraffic` and (on supported versions) Network Security Config. Without explicit restrictions, HTTP connections will work.
- **API <23**: cleartext is always allowed (legacy versions; Network Security Config not supported).

`android:usesCleartextTraffic` is a coarse, app-wide flag. Network Security Config provides fine-grained, per-domain control and is preferred for production setups.

### Control via Network Security Config

**For local development** (minimal permissions):
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <!-- ✅ Allow cleartext only for local addresses -->
  <domain-config cleartextTrafficPermitted="true">
    <domain>localhost</domain>
    <domain>10.0.2.2</domain>
  </domain-config>

  <!-- Block cleartext for all other domains by default -->
  <base-config cleartextTrafficPermitted="false" />
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config">
</application>
```

(Note: `domain-config` overrides `base-config` for the specified domains.)

**Anti-pattern** (unsafe for production):
```xml
<!-- ❌ Allows cleartext for ALL domains of the app -->
<application android:usesCleartextTraffic="true" />
```

### Common Error

When attempting an HTTP request on API 28+ without permitted cleartext:
```java
java.net.UnknownServiceException:
CLEARTEXT communication not permitted by network security policy
```

### Production Strategy

1. **HTTPS everywhere** — use TLS for all connections.
2. **Certificate pinning** — for sensitive APIs (banking, payments, etc.).
3. **Build variants** — allow cleartext only in debug builds (separate Network Security Config and manifest per debug/release).
4. **Build pipeline** — ensure debug configs (including XML and `usesCleartextTraffic="true"`) are excluded from release; do this via productFlavors/Build Types instead of relying on ProGuard/R8.

---

## Follow-ups

- How to configure different Network Security Config for debug/release builds?
- When should certificate pinning be mandatory beyond HTTPS?
- How to detect cleartext violations during automated testing?
- What happens if subdomain uses HTTP but parent domain has `cleartextTrafficPermitted="false"`?
- Can WebView bypass Network Security Config restrictions?

## References

- [[c-encryption]] — Encryption fundamentals
- https://developer.android.com/training/articles/security-config
- https://developer.android.com/privacy-and-security/security-tips#UnintendedDataLeakage
- [[q-certificate-pinning--security--medium]] — Advanced network security

## Related Questions

### Prerequisites (Easier)
- [[c-encryption]] — What is encryption?
- Basic networking concepts (HTTP vs HTTPS)

### Related (Same Level)
- [[q-android-security-practices-checklist--android--medium]] — Security best practices
- Network debugging with Charles/Proxyman

### Advanced (Harder)
- [[q-certificate-pinning--security--medium]] — Certificate pinning implementation
- [[q-android-keystore-system--android--medium]] — Android Keystore
- SSL/TLS handshake internals
- Man-in-the-middle attack prevention
