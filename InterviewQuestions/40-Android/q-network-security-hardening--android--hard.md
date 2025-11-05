---
id: android-636
title: Network Security Hardening / Укрепление сетевой безопасности
aliases:
  - Network Security Hardening
  - Укрепление сетевой безопасности
topic: android
subtopics:
  - security
  - networking
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-security-hardening
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/security
  - android/networking
  - certificate-pinning
  - difficulty/hard
sources:
  - url: https://developer.android.com/training/articles/security-config
    note: Network Security Config guide
  - url: https://square.github.io/okhttp/https/#certificate-pinning
    note: OkHttp certificate pinning docs
  - url: https://cloud.google.com/security/encryption-in-transit/application-layer-transport-security
    note: mTLS best practices
---

# Вопрос (RU)
> Как спроектировать сетевой уровень Android-приложения с усиленной безопасностью: Network Security Config, certificate pinning, двустороннее TLS, key attestation и мониторинг нарушений?

# Question (EN)
> How do you harden an Android app’s networking stack with Network Security Config, certificate pinning, mutual TLS, key attestation, and violation monitoring?

---

## Ответ (RU)

### 1. Network Security Config как база

```xml
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="@raw/app_certs" />
        </trust-anchors>
        <pin-set expiration="2025-12-31">
            <pin digest="SHA-256">kO1Cc9Y...</pin>
            <pin digest="SHA-256">Gru4sDf...</pin>
        </pin-set>
    </base-config>
    <domain-config includeSubdomains="true">
        <domain>api.example.com</domain>
    </domain-config>
</network-security-config>
```

- Выключите cleartext, используйте white-list доменов.
- Пины: минимум два разных сертификата (primary + backup).
- Обновляйте срок действия (expiration) и держите план ротации.

### 2. Certificate pinning (runtime)

- Для OkHttp: `CertificatePinner` + partially trust system CAs.
- Включите reporting: при pin mismatch → отправить в telemetry (не отправлять сам pin).
- Ротация: CI/CD pipeline обновляет `@raw/app_certs` и config.

### 3. Взаимная аутентификация TLS (mTLS)

- Создайте клиентский сертификат (short-lived) и храните в `Hardware-backed Keystore`.
- Используйте `KeyChain.choosePrivateKeyAlias` или собственный TLS socket factory.
- На бэкенде включите revocation и короткий срок жизни (<= 7 дней).

### 4. Key attestation

- При первой настройке запросите `KeyStore` `KeyPair`, получите attestation chain (`attestKey`).
- Передайте отпечаток на сервер → сверка доверенного устройства (SafetyNet/Play Integrity как дополнительный сигнал).
- Ротация ключей при подозрении компрометации.

### 5. Мониторинг и реакция

- Логируйте следующие события:
  - Pin mismatch
  - Trust manager failure
  - mTLS handshake error
- Создайте дашборд (Grafana/Looker) + alert rules.
- При аномалиях: fallback на fail-close (отказать запрос), уведомить SecOps.

### 6. CI/CD и тестирование

- Автотесты: instrumentation с `MockWebServer` (pin mismatch, expired cert).
- Static анализ: сканируйте репозиторий на случай использования `HttpURLConnection` без TLS.
- Проводите security review при добавлении нового API/доменов.

### 7. Экосистема

- Поддерживайте список SDK → домен → security config. Запрещайте SDK, нарушающие правила.
- Для вебвью: включите `Safe Browsing`, запретите mixed content.
- Документируйте incident response (как обновить пины out-of-band).

---

## Answer (EN)

- Lock down Network Security Config: disable cleartext, whitelist domains, and pin certificates with backup pins and rotation plans.
- Enforce runtime pinning (e.g., OkHttp) and log violations for telemetry; ensure CI updates bundled certs.
- Implement mutual TLS with short-lived client certs stored in hardware-backed keystore; manage server-side revocation.
- Use Android Key Attestation to verify device integrity and tie keys to genuine hardware.
- Monitor pin mismatches, trust failures, and mTLS errors, triggering alerts and fail-close behavior.
- Test with mock servers, run static analysis to catch insecure transports, and maintain strict policies for third-party SDK networking.

---

## Follow-ups
- Как безопасно выполнять горячую ротацию пинов без обновления приложения?
- Как интегрировать Key Attestation с Play Integrity score и backend policies?
- Какая стратегия fallback для пользователей в странах с TLS интерцепцией (enterprise proxies)?

## References

- [[c-security-hardening]]
- [[q-android-coverage-gaps--android--hard]]
- [Network Security Configuration](https://developer.android.com/training/articles/security-config)


## Related Questions

- [[c-security-hardening]]
- [[q-android-coverage-gaps--android--hard]]
