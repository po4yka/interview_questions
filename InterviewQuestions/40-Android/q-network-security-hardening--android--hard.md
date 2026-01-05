---
id: android-636
title: Network Security Hardening / Укрепление сетевой безопасности
aliases: [Network Security Hardening, Укрепление сетевой безопасности]
topic: android
subtopics: [keystore-crypto, network-security-config, networking-http]
question_kind: android
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-keystore, moc-android, q-android-security-practices-checklist--android--medium, q-app-security-best-practices--android--medium, q-data-sync-unstable-network--android--hard]
created: 2025-11-02
updated: 2025-11-11
tags: [android/keystore-crypto, android/network-security-config, android/networking-http, certificate-pinning, difficulty/hard]
sources:
  - "https://cloud.google.com/security/en-transit/application-layer-transport-security"
  - "https://developer.android.com/training/articles/security-config"
  - "https://square.github.io/okhttp/https/#certificate-pinning"

---
# Вопрос (RU)
> Как спроектировать сетевой уровень Android-приложения с усиленной безопасностью: Network Security Config, certificate pinning, двустороннее TLS, key attestation и мониторинг нарушений?

# Question (EN)
> How do you harden an Android app’s networking stack with Network Security Config, certificate pinning, mutual TLS, key attestation, and violation monitoring?

---

## Ответ (RU)

## Краткая Версия
- Network Security Config как обязательная база: запрет cleartext, явные домены, строгие trust anchors и пины.
- Certificate pinning: минимум два пина, ротация через CI/CD, телеметрия при несоответствиях.
- mTLS: краткоживущие клиентские сертификаты, приватные ключи в аппаратно защищенном Keystore.
- Key attestation: ключи только из `AndroidKeyStore` с hardware-backed при доступности, серверная проверка аттестации.
- Мониторинг и реакция: логирование критичных сбоев, алерты, fail-close для подозрительных условий на критичных endpoint и план экстренного обновления.
- CI/CD и тесты: автопроверки на небезопасный TLS/TrustManager, интеграционные тесты с MockWebServer.
- Экосистема: контроль SDK и WebView, документированный incident response.

## Подробная Версия
### 1. Network Security Config Как База

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
- При использовании своих trust anchors (`@raw/app_certs`) по возможности ограничивайте их конкретными доменами через `domain-config`, чтобы не расширять доверие глобально без необходимости.

### 2. Certificate Pinning (runtime)

- Для OkHttp: используйте `CertificatePinner`; при необходимости допускайте системные CA, пингуя конкретные публичные ключи.
- Включите reporting: при pin mismatch → отправлять событие в телеметрию (без логирования ключей или самих пинов).
- Ротация: CI/CD обновляет `@raw/app_certs` и конфиг синхронно с выпуском новых серверных сертификатов.

### 3. Взаимная Аутентификация TLS (mTLS)

- Создавайте краткоживущие клиентские сертификаты и храните приватные ключи в аппаратно защищенном (`hardware-backed`) Keystore, где он доступен.
- Используйте `KeyChain.choosePrivateKeyAlias` или собственный `SSLSocketFactory`/`X509KeyManager` для выбора ключа.
- На бэкенде включите отзыв и короткий срок жизни (например, ≤ 7 дней) для клиентских сертификатов.

### 4. Key Attestation

- Генерируйте ключи только в `AndroidKeyStore` с `KeyGenParameterSpec`, запрашивая аппаратно защищённое (`hardware-backed`) хранилище и аутентификацию пользователя там, где это релевантно, учитывая, что не на всех устройствах доступны такие гарантии.
- Запрашивайте attestation chain при создании ключа и отправляйте её на сервер.
- На сервере проверяйте, что ключ создан в доверенном окружении и не импортирован; используйте SafetyNet/Play Integrity как отдельные дополнительные сигналы.
- Настройте ротацию ключей при подозрении компрометации или изменении политик.

### 5. Мониторинг И Реакция

- Логируйте (с учётом приватности):
  - pin mismatch;
  - ошибки `TrustManager` / валидации цепочки сертификатов;
  - ошибки рукопожатия mTLS.
- Стройте дашборды и алерты (Grafana/Looker и т.п.).
- Для критичных endpoint используйте поведение fail-close при подозрительных условиях, уведомляйте SecOps и имейте план экстренного обновления конфигурации/пинов.

### 6. CI/CD И Тестирование

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
  - `OkHttp`/HTTP client сконфигурирован через `network-security-config` и `CertificatePinner`.
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

## Short Version
- Use Network Security Config as a mandatory baseline: no cleartext, explicit domains, strict trust anchors and pins.
- Certificate pinning: at least two pins, rotation via CI/CD, telemetry for mismatches.
- mTLS: short-lived client certs, private keys in hardware-backed Keystore.
- Key attestation: keys only from `AndroidKeyStore` with hardware-backed storage where available; backend verifies attestation.
- Monitoring/response: log critical failures, alerts, fail-close on suspicious conditions for critical endpoints, emergency update plan.
- CI/CD and tests: automated checks for insecure TLS/TrustManagers, integration tests with MockWebServer.
- Ecosystem: control SDKs and WebView, documented incident response.

## Detailed Version
### 1. Network Security Config as the Baseline

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

- Disable cleartext HTTP in `base-config`.
- Explicitly list allowed domains in `domain-config`.
- Place `pin-set` inside the corresponding `domain-config`.
- Pins: at least two different pins (primary and backup), `expiration`, and a rotation plan.
- When using custom trust anchors (`@raw/app_certs`), scope them to specific `domain-config` entries where possible to avoid unnecessarily broad trust.

### 2. Certificate Pinning (runtime)

- With OkHttp, use `CertificatePinner`; when necessary, still rely on system CAs while pinning specific public keys.
- Enable reporting: on pin mismatch, send a telemetry event (without logging keys or pins).
- Rotation: use CI/CD to update `@raw/app_certs` and config in sync with server certificate changes.

### 3. Mutual TLS (mTLS)

- Issue short-lived client certificates and store private keys in a hardware-backed Keystore when available.
- Use `KeyChain.choosePrivateKeyAlias` or a custom `SSLSocketFactory`/`X509KeyManager` to select the key.
- On the backend, use revocation and short lifetimes (e.g., ≤ 7 days) for client certs.

### 4. Key Attestation

- Generate keys only in `AndroidKeyStore` with `KeyGenParameterSpec`, requesting hardware-backed storage and user auth where appropriate, acknowledging that not all devices provide the same guarantees.
- Request the attestation chain when creating the key and send it to the backend.
- On the backend, verify that the key is created in a trusted environment and not imported; use SafetyNet/Play Integrity as additional signals.
- Configure key rotation on suspected compromise or policy changes.

### 5. Monitoring and Response

- Log (with privacy safeguards):
  - pin mismatches;
  - `TrustManager` / certificate validation failures;
  - mTLS handshake errors.
- Build dashboards and alerts (e.g., Grafana/Looker).
- For critical endpoints, use fail-close behavior on suspicious conditions, notify SecOps, and maintain an emergency config/pin update plan.

### 6. CI/CD And Testing

- Instrumentation and integration tests with `MockWebServer` for pin mismatch, expired/rotated certs, and mTLS failures.
- Static analysis to detect:
  - plain HTTP or disabled TLS;
  - disabled hostname verification;
  - permissive `TrustManager` implementations.
- Security review required when adding new APIs/domains or changing security configuration.

### 7. Ecosystem

- Maintain a list of SDKs → domains → expected security configuration; block SDKs that weaken your policies.
- For WebView: enable Safe Browsing, block mixed content, and enforce HTTPS for your own resources.
- Document incident response (including out-of-band pin/config updates in case of CA or key compromise).

### Requirements

- Functional:
  - Secure all critical endpoints with TLS 1.2+.
  - Apply certificate pinning and, where needed, mTLS for sensitive operations.
  - Verify device and key authenticity via key attestation.
  - Log and surface security violations (pin mismatches, certificate validation failures, mTLS issues).
- Non-functional:
  - Maintainable key/pin rotation without reducing security.
  - Minimal performance overhead on network calls.
  - Compatibility with common Android devices and OS versions.
  - High reliability with predictable fail-close behavior.

### Architecture

- Client:
  - `OkHttp`/HTTP client configured via `network-security-config` and `CertificatePinner`.
  - Use `AndroidKeyStore` for key storage with hardware-backed protection where available.
  - Component for key attestation and sending results to the backend.
  - Monitoring module for collecting and sending TLS/pinning failure telemetry.
- Server:
  - TLS termination with pinning/mTLS policies.
  - Key attestation verification service.
  - Centralized logging, alerting, and dashboards for security events.
- Data flow:
  - Requests pass through the hardened TLS layer.
  - On anomalies, requests fail closed and emit events into the monitoring pipeline.

---

## Дополнительные Вопросы (RU)
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

## Связанные Вопросы (RU)

- [[moc-android]]

## Related Questions (EN)

- [[moc-android]]
