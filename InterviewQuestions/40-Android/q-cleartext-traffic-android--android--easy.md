---
id: 20251006-100011
title: What is cleartext traffic in Android? / Что такое cleartext traffic в Android?
aliases: [Cleartext traffic, Незашифрованный трафик]
topic: android
subtopics: [networking-http, network-security-config]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-keystore-system--security--medium, q-android-security-practices-checklist--android--medium, q-certificate-pinning--security--medium]
created: 2025-10-06
updated: 2025-10-28
tags: [android/networking-http, android/network-security-config, difficulty/easy]
sources: [https://developer.android.com/training/articles/security-config#CleartextTrafficPermitted]
---
# Вопрос (RU)
> Что такое cleartext traffic в Android?

# Question (EN)
> What is cleartext traffic in Android?

---

## Ответ (RU)

**Cleartext traffic** — незашифрованная HTTP-связь без TLS/SSL. Любая сторона на пути передачи может читать и модифицировать данные. Для защиты используйте [[c-encryption]].

**Политика Android**:
- Android 9+ (API 28+): cleartext **заблокирован по умолчанию**
- Старые версии: разрешён по умолчанию

**Для разработки** (только конкретные домены):
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <!-- ✅ Разрешить cleartext только для localhost -->
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

**Не использовать** (включает cleartext для всех доменов):
```xml
<!-- ❌ Небезопасно для production -->
<application android:usesCleartextTraffic="true" />
```

**Production**: используйте HTTPS везде, для критичных API добавьте certificate pinning.

**Типичная ошибка**:
```text
java.net.UnknownServiceException: CLEARTEXT communication not permitted by network security policy
```

## Answer (EN)

**Cleartext traffic** is unencrypted HTTP communication without TLS/SSL. Anyone on the network path can read and modify the data. Use [[c-encryption]] for secure communication.

**Android Policy**:
- Android 9+ (API 28+): cleartext is **blocked by default**
- Older versions: allowed by default

**For development** (specific domains only):
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <!-- ✅ Allow cleartext only for localhost -->
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

**Do NOT use** (enables cleartext for all domains):
```xml
<!-- ❌ Unsafe for production -->
<application android:usesCleartextTraffic="true" />
```

**Production**: enforce HTTPS everywhere, add certificate pinning for sensitive APIs.

**Common error**:
```text
java.net.UnknownServiceException: CLEARTEXT communication not permitted by network security policy
```

## Follow-ups
- When should certificate pinning be used in addition to HTTPS?
- How to enable cleartext only for debug builds using build variants?
- How to detect cleartext traffic violations during testing?
- What happens when an app tries cleartext on API 28+ without configuration?

## References
- [Android Network Security Configuration](https://developer.android.com/training/articles/security-config#CleartextTrafficPermitted)
- [[q-android-security-practices-checklist--android--medium]]
- [[q-certificate-pinning--security--medium]]

## Related Questions

### Prerequisites (Easier)
- Basic HTTP vs HTTPS understanding
- Android manifest configuration basics

### Related (Same Level)
- [[q-android-security-practices-checklist--android--medium]]
- [[q-certificate-pinning--security--medium]]

### Advanced (Harder)
- [[q-android-keystore-system--security--medium]]
- Certificate pinning implementation patterns
