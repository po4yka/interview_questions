---
id: android-636
title: Network Security Hardening / Укрепление сетевой безопасности
aliases:
- Network Security Hardening
- Укрепление сетевой безопасности
topic: android
subtopics:
- network-security-config
- keystore-crypto
- networking-http
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- c-android-keystore
- moc-android
created: 2025-11-02
updated: 2025-11-10
tags:
- android/network-security-config
- android/keystore-crypto
- android/networking-http
- certificate-pinning
- difficulty/hard
sources:
- "https://developer.android.com/training/articles/security-config"
- "https://square.github.io/okhttp/https/#certificate-pinning"
- "https://cloud.google.com/security/en-transit/application-layer-transport-security"

---

# Вопрос (RU)
> Как спроектировать сетевой уровень Android-приложения с усиленной безопасностью: Network Security Config, certificate pinning, двустороннее TLS, key attestation и мониторинг нарушений?

# Question (EN)
> How do you harden an Android app’s networking stack with Network Security Config, certificate pinning, mutual TLS, key attestation, and violation monitoring?

---

## Ответ (RU)

### Краткая версия

- Network Security Config как обязательная база: запрет cleartext, явные домены, строгие trust anchors и пины.
- Certificate pinning: минимум два пина, ротация через CI/CD, телеметрия при несоответствиях.
- mTLS: краткоживущие клиентские сертификаты, приватные ключи в аппаратно защищенном Keystore.
- Key attestation: ключи только из `AndroidKeyStore` с hardware-backed, серверная проверка аттестации.
- Мониторинг и реакция: логирование критичных сбоев, алерты, fail-close для подозрительных условий на критичных endpoint и план экстренного обновления.
- CI/CD и тесты: автопроверки на небезопасный TLS/TrustManager, интеграционные тесты с MockWebServer.
- Экосистема: контроль SDK и WebView, документированный incident response.

### Подробная версия

### 1. Network Security Config как база

```xml
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="@raw/app_certs" />
        </trust-anchors>
    </base-config>
    <domain-config includeSubdomains="true">
        <domain>api.example.com</domain>
        <pin-set expiration="2025-12-31">
            <pin digest="SHA-256">kO1Cc9Y...</pin>
            <pin digest="SHA-256">Gru4sDf...</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

- Отключите cleartext (нешифрованный HTTP) в `base-config`.
- Явно перечислите разрешённые домены в `domain-config`.
- Разместите `pin-set` внутри соответствующего `domain-config`.
- Пины: минимум два разных пина (основной и резервный), `expiration` и план ротации.

### 2. Certificate pinning (runtime)

- Для OkHttp: используйте `CertificatePinner`; при необходимости допускайте системные CA, пингуя конкретные публичные ключи.
- Включите reporting: при pin mismatch → отправлять событие в телеметрию (без логирования ключей или самих пинов).
- Ротация: CI/CD обновляет `@raw/app_certs` и конфиг синхронно с выпуском новых серверных сертификатов.

### 3. Взаимная аутентификация TLS (mTLS)

- Создавайте краткоживущие клиентские сертификаты и храните приватные ключи в аппаратно защищенном (`hardware-backed`) Keystore.
- Используйте `KeyChain.choosePrivateKeyAlias` или собственный `SSLSocketFactory`/`X509KeyManager` для выбора ключа.
- На бэкенде включите отзыв и короткий срок жизни (например, ≤ 7 дней) для клиентских сертификатов.

### 4. Key attestation

- Генерируйте ключи только в `AndroidKeyStore` с `KeyGenParameterSpec`, требующим аппаратно защищённое (`hardware-backed`) хранилище и аутентификацию где нужно.
- Запрашивайте attestation chain при создании ключа и отправляйте её на сервер.
- На сервере проверяйте, что ключ создан в доверенном окружении и не импортирован; используйте SafetyNet/Play Integrity как отдельные дополнительные сигналы.
- Настройте ротацию ключей при подозрении компрометации или изменении политик.

### 5. Мониторинг и реакция

- Логируйте (с учётом приватности):
  - pin mismatch;
  - ошибки `TrustManager` / валидации цепочки сертификатов;
  - ошибки рукопожатия mTLS.
- Стройте дашборды и алерты (Grafana/Looker и т.п.).
- Для критичных endpoint используйте поведение fail-close при подозрительных условиях, уведомляйте SecOps и имейте план экстренного обновления конфигурации/пинов.

### 6. CI/CD и тестирование

- Автотесты: instrumentation и интеграционные тесты с `MockWebServer` для сценариев pin mismatch, истёкших/ротированных сертификатов и сбоев mTLS.
- Статический анализ: сканируйте репозиторий на:
  - использование plain HTTP или отключенный TLS;
  - отключённую проверку hostname;
  - кастомные `TrustManager`, доверяющие всем сертификатам.
- Проводите security review при добавлении новых API/доменов и изменении конфигурации безопасности.

### 7. Экосистема

- Ведите список SDK → домены → ожидаемая конфигурация безопасности; запрещайте SDK, ослабляющие ваши политики.
- Для WebView: включайте Safe Browsing, запрещайте mixed content и принудительно используйте HTTPS для своих ресурсов.
- Документируйте incident response (включая out-of-band обновление пинов/config при компрометации CA или ключа).

### Требования (RU)

- Функциональные:
  - Обеспечить защищённые соединения для всех критичных endpoint через TLS 1.2+.
  - Применять certificate pinning и, при необходимости, mTLS для чувствительных операций.
  - Проверять подлинность устройства и ключей через key attestation.
  - Логировать и сигнализировать о нарушениях (pin mismatch, ошибки проверки сертификатов, сбои mTLS).
- Нефункциональные:
  - Поддерживаемость и ротация ключей/пинов без снижения безопасности.
  - Минимальное влияние на производительность сети.
  - Совместимость с типичными Android-устройствами и версиями.
  - Высокая отказоустойчивость и предсказуемое fail-close поведение.

### Архитектура (RU)

- Клиент:
  - `OkHttp`/`HttPClient` сконфигурирован через `network-security-config` и `CertificatePinner`.
  - Использование `AndroidKeyStore` для хранения ключей, аппаратная защита где доступна.
  - Компонент для key attestation и отправки результатов на сервер.
  - Модуль мониторинга: сбор и отправка телеметрии по сбоям TLS/pinning.
- Сервер:
  - Терминация TLS с поддержкой pinning/mTLS.
  - Верификатор key attestation.
  - Логирование, алертинг и панели мониторинга для событий безопасности.
- Потоки данных:
  - Запросы из приложения проходят через настроенный TLS слой.
  - При аномалиях запросы блокируются (fail-close) и события уходят в систему мониторинга.

---

## Answer (EN)

### Short Version

- Use Network Security Config as a mandatory baseline: no cleartext, explicit domains, strict trust anchors and pins.
- Certificate pinning: at least two pins, rotation via CI/CD, telemetry for mismatches.
- mTLS: short-lived client certs, private keys in hardware-backed Keystore.
- Key attestation: keys only from `AndroidKeyStore` with hardware-backed storage; backend verifies attestation.
- Monitoring/response: log critical failures, alerts, fail-close on suspicious conditions for critical endpoints, emergency update plan.
- CI/CD and tests: automated checks for insecure TLS/TrustManagers, integration tests with MockWebServer.
- Ecosystem: control SDKs and WebView, documented incident response.

### Detailed Version

### 1. Network Security Config as the baseline

- Define a strict `network-security-config`:
  - Disable cleartext traffic in `base-config`.
  - Explicitly enumerate allowed domains in `domain-config`.
  - Put `pin-set` inside the relevant `domain-config` with at least two pins (primary + backup) and an `expiration` plus a rotation plan.

### 2. Certificate pinning (runtime)

- With OkHttp, use `CertificatePinner` and, if needed, still rely on system CAs while pinning specific public keys.
- Report pin mismatches to telemetry (without logging keys or raw pins) and investigate anomalies.
- Use CI/CD to update bundled certs / pins (`@raw` resources and XML config) in sync with server certificate rotation.

### 3. Mutual TLS (mTLS)

- Issue short-lived client certificates and keep private keys in the hardware-backed Android Keystore.
- Use `KeyChain.choosePrivateKeyAlias` or a custom `SSLSocketFactory`/`X509KeyManager` to select the client cert.
- On the backend, enforce revocation and short lifetimes (e.g., ≤ 7 days) for client certs.

### 4. Key attestation

- Generate keys in `AndroidKeyStore` with `KeyGenParameterSpec`, requiring hardware-backed storage and auth where appropriate.
- Request an attestation certificate chain when creating the key and send it to the backend.
- On the backend, verify that the key is bound to genuine device hardware and not imported; treat SafetyNet/Play Integrity as separate, additional signals.
- Rotate keys on suspected compromise or when policies change.

### 5. Monitoring and response

- Monitor and log (privacy-aware):
  - Pin mismatches
  - Trust manager / certificate validation failures
  - mTLS handshake failures
- Build dashboards and alerts (e.g., Grafana/Looker) for these events.
- For critical endpoints, prefer fail-close behavior on suspicious conditions and have an emergency config/pin update playbook.

### 6. CI/CD and testing

- Use instrumentation/integration tests with mock servers to cover pin mismatch, expired/rotated certs, and mTLS errors.
- Run static analysis to detect:
  - plain HTTP or TLS disabled;
  - disabled hostname verification;
  - permissive trust managers that trust all certs.
- Require security review for new domains/APIs and changes to security config.

### 7. Ecosystem

- Maintain a mapping of SDK → domains → expected security config; block SDKs that bypass or weaken your policies.
- For WebView content, enable Safe Browsing, block mixed content, and enforce HTTPS for your own origins.
- Document incident response for pin/config updates (including out-of-band updates in case of CA or key compromise).

### Requirements

- Functional:
  - Secure all critical endpoints with TLS 1.2+.
  - Apply certificate pinning and, where needed, mTLS for sensitive operations.
  - Verify device and key authenticity via key attestation.
  - Log and surface security violations (pin mismatches, cert validation failures, mTLS issues).
- Non-functional:
  - Support maintainable key/pin rotation without weakening security.
  - Minimize performance overhead on network calls.
  - Remain compatible with common Android devices and OS versions.
  - Provide high reliability with predictable fail-close behavior.

### Architecture

- Client:
  - `OkHttp`/HTTP client configured via `network-security-config` and `CertificatePinner`.
  - Use Android Keystore for key storage with hardware-backed protection where available.
  - Component for key attestation and sending attestation results to the backend.
  - Monitoring module to collect and send TLS/pinning failure telemetry.
- Server:
  - TLS termination with support for pinning/mTLS policies.
  - Key attestation verification service.
  - Centralized logging, alerting, and dashboards for security events.
- Data flow:
  - App requests pass through the hardened TLS layer.
  - On anomalies, requests fail closed and emit events into the monitoring pipeline.

---

## Дополнительные вопросы (RU)
- Как безопасно выполнять горячую ротацию пинов без обновления приложения?
- Как интегрировать Key Attestation с Play Integrity score и backend-политиками?
- Какая стратегия fallback для пользователей в странах с TLS-интерцепцией (enterprise proxies)?

## Follow-ups (EN)
- How can you safely perform hot pin rotation without requiring an app update?
- How would you integrate Key Attestation with Play Integrity score and backend policies?
- What fallback strategy would you use for users behind TLS-intercepting enterprise proxies?

## Ссылки (RU)

- [[c-android-keystore]]
- [Network Security Configuration](https://developer.android.com/training/articles/security-config)

## References (EN)

- [[c-android-keystore]]
- [Network Security Configuration](https://developer.android.com/training/articles/security-config)

## Связанные вопросы (RU)

- [[moc-android]]

## Related Questions (EN)

- [[moc-android]]
