---
id: 20251006-100011
title: What is cleartext traffic in Android? / Что такое cleartext traffic в Android?
aliases: [Cleartext traffic, Незашифрованный трафик]
# Classification
topic: android
subtopics: [security, networking]
question_kind: android
difficulty: easy
# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://developer.android.com/training/articles/security-config#CleartextTrafficPermitted
source_note: Android docs
# Workflow & relations
status: reviewed
moc: moc-android
related: [q-certificate-pinning--security--medium, q-android-security-practices-checklist--android--medium, q-android-keystore-system--security--medium]
# Timestamps
created: 2025-10-06
updated: 2025-10-20
# Tags (English only)
tags: [android/security, android/networking, https, cleartext, difficulty/easy]
---# Вопрос (RU)
> Что такое cleartext traffic в Android?

---

# Question (EN)
> What is cleartext traffic in Android?

## Ответ (RU)

### Определение
- Cleartext traffic = незашифрованный HTTP (без TLS). Любой посредник может читать/менять.

### Политика Android
- Android 9+ (API 28): cleartext по умолчанию запрещён
- Старые версии: по умолчанию разрешён

### Разрешать только для разработки (по доменам)
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <domain-config cleartextTrafficPermitted="true">
    <domain includeSubdomains="true">localhost</domain>
    <domain includeSubdomains="true">10.0.2.2</domain>
  </domain-config>
  <base-config cleartextTrafficPermitted="false" />
</network-security-config>
```
```xml
<!-- AndroidManifest.xml -->
<application android:networkSecurityConfig="@xml/network_security_config" />
```

### Не включайте глобально
```xml
<!-- Не рекомендуется (включает cleartext для ВСЕХ доменов) -->
<application android:usesCleartextTraffic="true" />
```

### Практика для продакшена
- Принудительно HTTPS везде; при необходимости — certificate pinning для чувствительных API

### Типичная ошибка
```
java.net.UnknownServiceException: CLEARTEXT communication ... not permitted by network security policy
```

---

## Answer (EN)

### Definition
- Cleartext traffic = unencrypted HTTP communication (no TLS). Anyone on path can read/modify.

### Android policy
- Android 9+ (API 28): cleartext is blocked by default
- Older versions: allowed by default

### Allow only for development (per‑domain)
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <domain-config cleartextTrafficPermitted="true">
    <domain includeSubdomains="true">localhost</domain>
    <domain includeSubdomains="true">10.0.2.2</domain>
  </domain-config>
  <base-config cleartextTrafficPermitted="false" />
</network-security-config>
```
```xml
<!-- AndroidManifest.xml -->
<application android:networkSecurityConfig="@xml/network_security_config" />
```

### Do NOT enable globally
```xml
<!-- Not recommended (enables cleartext for ALL domains) -->
<application android:usesCleartextTraffic="true" />
```

### Production best practice
- Enforce HTTPS everywhere; optionally add certificate pinning for sensitive APIs

### Error you’ll see
```
java.net.UnknownServiceException: CLEARTEXT communication ... not permitted by network security policy
```

## Follow-ups
- When should certificate pinning be added on top of HTTPS?
- How to enable cleartext only for internal dev environments?
- How to detect accidental cleartext usage in CI?

## References
- https://developer.android.com/training/articles/security-config#CleartextTrafficPermitted

## Related Questions

### Prerequisites (Easier)
- [[q-android-security-practices-checklist--android--medium]]

### Related (Same Level)
- [[q-certificate-pinning--security--medium]]
- [[q-android-keystore-system--security--medium]]

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]]

