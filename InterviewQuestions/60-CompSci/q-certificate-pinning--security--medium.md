---
id: sec-002
title: Certificate Pinning / Закрепление сертификатов
aliases:
- Certificate Pinning
- Закрепление сертификатов
topic: cs
subtopics:
- security
- networking
- tls
question_kind: android
difficulty: medium
status: draft
moc: moc-cs
related:
- c-computer-science
- q-android-keystore-system--android--medium
- q-android-security-practices-checklist--android--medium
- q-api-rate-limiting-throttling--android--medium
- q-app-security-best-practices--android--medium
- q-okhttp-interceptors-advanced--networking--medium
- q-retrofit-coroutines-best-practices--kotlin--medium
created: 2025-10-15
updated: 2025-11-11
original_language: en
language_tags:
- en
- ru
tags:
- difficulty/medium
- networking
- okhttp
- security
- tls
anki_cards:
- slug: sec-002-0-en
  language: en
  anki_id: 1768454033640
  synced_at: '2026-01-15T09:43:17.082954'
- slug: sec-002-0-ru
  language: ru
  anki_id: 1768454033665
  synced_at: '2026-01-15T09:43:17.084229'
---
# Вопрос (RU)
> Что такое закрепление сертификатов, зачем оно нужно и как безопасно реализовать его в Android (`OkHttp` и Network Security Config)?

---

# Question (EN)
> What is certificate pinning, why use it, and how to implement it safely on Android (`OkHttp` and Network Security Config)?

---

## Ответ (RU)

### Теория
- Назначение: ограничить доверие TLS известным сертификатом/ключом, чтобы исключить MITM даже при компрометации CA.
- Что пинить: предпочтительно публичный ключ (переживает продление), всегда добавлять резервные пины для ротации.
- Область: пинить на хост; wildcard — только при чётком понимании рисков.

См. также: [[c-computer-science]], moc-security.

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
- Ручное: прокси (mitmproxy/Charles). Приложение должно падать с `SSLPeerUnverifiedException`.

---

## Answer (EN)

### Core Theory
- Purpose: constrain TLS trust to known cert/public key to defeat MITM even if a rogue/root CA exists.
- What to pin: prefer public key (survives cert renewal), include backup pins for rotation.
- Scope: pin per host; add wildcards only if necessary and well understood.

See also: [[c-computer-science]], moc-security.

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
- Manual: proxy (mitmproxy/Charles). App must fail with `SSLPeerUnverifiedException`.

---

## Follow-ups (RU)
- Компромиссы между пиннингом публичного ключа и конечного сертификата?
- Как планировать и выкатывать ротацию пинов без блокировки пользователей?
- Как отслеживать срок действия сертификатов и автоматизировать оповещения?

## References (RU)
- https://square.github.io/okhttp/features/certificate_pinning/
- https://developer.android.com/training/articles/security-config#CertificatePinning

## Related Questions (RU)

### Предпосылки (проще)
- [[q-app-security-best-practices--android--medium]]

### Связанные (тот Же уровень)
- [[q-android-security-practices-checklist--android--medium]]
- [[q-android-keystore-system--android--medium]]

### Продвинутые (сложнее)
- [[q-android-runtime-art--android--medium]]

---

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
- [[q-android-keystore-system--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]]
