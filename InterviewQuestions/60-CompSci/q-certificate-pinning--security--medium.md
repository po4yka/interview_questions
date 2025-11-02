---
id: sec-002
title: Certificate Pinning / Закрепление сертификатов
aliases: [Certificate Pinning, Закрепление сертификатов]
topic: security
subtopics:
  - networking
  - tls
question_kind: android
difficulty: medium
status: reviewed
moc: moc-security
related:
  - q-android-keystore-system--security--medium
  - q-android-security-practices-checklist--android--medium
  - q-app-security-best-practices--android--medium
created: 2025-10-15
updated: 2025-10-20
original_language: en
language_tags:
  - en
  - ru
tags: [difficulty/medium, networking, okhttp, security, tls]
date created: Sunday, October 12th 2025, 12:27:51 pm
date modified: Saturday, October 25th 2025, 8:32:52 pm
---

# Вопрос (RU)
> Что такое закрепление сертификатов, зачем оно нужно и как безопасно реализовать его в Android (OkHttp и Network Security Config)?

---

# Question (EN)
> What is certificate pinning, why use it, and how to implement it safely on Android (OkHttp and Network Security Config)?

## Ответ (RU)

### Теория
- Назначение: ограничить доверие TLS известным сертификатом/ключом, чтобы исключить MITM даже при компрометации CA.
- Что пинить: предпочтительно публичный ключ (переживает продление), всегда добавлять резервные пины для ротации.
- Область: пинить на хост; wildcard — только при чётком понимании рисков.

### Минимальная Настройка OkHttp
```kotlin
val pinner = CertificatePinner.Builder()
  .add("api.example.com", "sha256/BASE64_PIN_PRIMARY")
  .add("api.example.com", "sha256/BASE64_PIN_BACKUP")
  .build()

val client = OkHttpClient.Builder()
  .certificatePinner(pinner)
  .build()
```

### Альтернатива: Network Security Config
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <domain-config cleartextTrafficPermitted="false">
    <domain includeSubdomains="true">api.example.com</domain>
    <pin-set>
      <pin digest="SHA-256">BASE64_PIN_PRIMARY</pin>
      <pin digest="SHA-256">BASE64_PIN_BACKUP</pin>
    </pin-set>
  </domain-config>
</network-security-config>
```

### Ротация И Обработка Сбоёв
- Поставлять основной + резервные пины; добавлять новый пин до ротации; удалять старый после.
- При сбое пиннинга: жёстко падать, логировать событие безопасности, показывать понятную ошибку; не обходить проверку.

### Тестирование
- Авто: MockWebServer с выданным сертификатом; проверять успех/неуспех.
- Ручное: прокси (mitmproxy/Charles). Приложение должно падать с SSLPeerUnverifiedException.

---

## Answer (EN)

### Core Theory
- Purpose: constrain TLS trust to known cert/public key to defeat MITM even if a rogue/root CA exists.
- What to pin: prefer public key (survives cert renewal), include backup pins for rotation.
- Scope: pin per host; add wildcards only if necessary and well understood.

### Minimal OkHttp Setup
```kotlin
val pinner = CertificatePinner.Builder()
  .add("api.example.com", "sha256/BASE64_PIN_PRIMARY")
  .add("api.example.com", "sha256/BASE64_PIN_BACKUP")
  .build()

val client = OkHttpClient.Builder()
  .certificatePinner(pinner)
  .build()
```

### Network Security Config Alternative
```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <domain-config cleartextTrafficPermitted="false">
    <domain includeSubdomains="true">api.example.com</domain>
    <pin-set>
      <pin digest="SHA-256">BASE64_PIN_PRIMARY</pin>
      <pin digest="SHA-256">BASE64_PIN_BACKUP</pin>
    </pin-set>
  </domain-config>
</network-security-config>
```

### Rotation and Failure Handling
- Ship primary + backup pins; add next pin before rotation; remove old after rollout.
- On pin failure: fail closed, log security event, show clear error; never silently bypass.

### Testing
- Automated: MockWebServer with held certificate; verify success/failure paths.
- Manual: proxy (mitmproxy/Charles). App must fail with SSLPeerUnverifiedException.

## Follow-ups
- Public key vs leaf certificate pinning trade-offs?
- How to plan/ship pin rotation without lockouts?
- How to monitor cert expiry and automate alerts?

## References
- https://square.github.io/okhttp/features/certificate_pinning/
- https://developer.android.com/training/articles/security-config#CertificatePinning

## Related Questions

### Prerequisites (Easier)
- [[q-app-security-best-practices--android--medium]]

### Related (Same Level)
- [[q-android-security-practices-checklist--android--medium]]
- [[q-android-keystore-system--security--medium]]

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]]

