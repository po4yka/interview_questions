---
id: android-637
title: Sensitive Data Lifecycle / Жизненный цикл чувствительных данных
aliases: [Sensitive Data Lifecycle, Жизненный цикл чувствительных данных]
topic: android
subtopics:
  - keystore-crypto
  - privacy-sdks
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android-keystore
  - q-android-security-best-practices--android--medium
  - q-data-sync-unstable-network--android--hard
  - q-save-data-outside-fragment--android--medium
  - q-what-is-data-binding--android--easy
created: 2025-11-02
updated: 2025-11-10
tags: [android/keystore-crypto, android/privacy-sdks, data-lifecycle, difficulty/hard]
sources:
- url: "https://developer.android.com/topic/security/data"
  note: Protecting user data guide
- url: "https://developer.android.com/topic/security/best-practices"
  note: Android security best practices
- url: "https://owasp.org/www-project-mobile-security-testing-guide/"
  note: OWASP MSTG data storage/testing guidance

date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---

# Вопрос (RU)
> Как построить систему управления жизненным циклом чувствительных данных в Android: классификация, минимизация, шифрование, контролируемое кеширование, безопасное удаление и аудит?

# Question (EN)
> How do you manage the lifecycle of sensitive data in an Android app, covering classification, minimization, encryption, controlled caching, secure deletion, and auditing?

---

## Ответ (RU)

### Краткий Вариант
- Классифицируйте данные, минимизируйте сбор и храните только необходимое.
- Используйте шифрование at rest и in transit, ключи — в аппаратно-защищённом Keystore.
- Ограничьте кеширование чувствительных данных.
- Введите явные политики ретенции, безопасное удаление (crypto-shredding).
- Обеспечьте аудит, мониторинг и проверку через тесты и статический анализ.

### Подробный Вариант

### 1. Классификация И Минимизация

- Разбейте данные на уровни (PII, финансовые, биометрические данные, телеметрия).
- Принцип минимизации: не собирайте данные без явной, задокументированной цели.
- Обновляйте классификацию при изменении схем (Room migrations, DTO) и при добавлении новых типов данных.

### 2. Хранение (at rest)

- Используйте `EncryptedSharedPreferences`, `EncryptedFile` (Jetpack Security), `SQLCipher` для критичных БД.
- Для временных данных/кешей — используйте файлы в `context.cacheDir` (при необходимости через `File.createTempFile`) и гарантируйте удаление после использования.
- Изолируйте ключи через аппаратно-защищённый Keystore (`Hardware-backed Keystore`), задавайте корректные атрибуты ключей (алгоритм, режим, допустимое назначение, срок действия, требования к аутентификации пользователя).

### 3. Передача (in transit)

- Используйте TLS 1.2+; сертификат pinning применяйте обоснованно (для высокорисковых сценариев, с продуманным механизмом ротации), избегайте незашифрованной передачи чувствительных данных.
- Учитывайте offline-сценарии: шифруйте payload перед сохранением в локальную очередь отправки.
- Добавьте криптографическую подпись/механизм целостности (например, HMAC) для защиты от модификации.

### 4. Контролируемое Кеширование

- На сетевом уровне для содержимого с PII используйте заголовки `Cache-Control: no-store`/`no-cache` по необходимости, чтобы предотвратить кеширование на клиенте/прокси.
- Для загрузчиков изображений (Glide/Picasso и др.) отключайте диск-кеш для изображений, содержащих чувствительные данные (например, персональные документы, медицинские снимки), через `DiskCacheStrategy.NONE`/аналогичные настройки.
- В хранилище (Room и др.) разделяйте таблицы с PII и прочими данными, используйте шифрование на уровне таблиц/колонок, когда необходимо, чтобы минимизировать объём чувствительных данных в кеше/индексах.

### 5. Удаление И Ретенция

- Имплементируйте явную retention policy (например, в днях) для каждого типа данных. Используйте `WorkManager` или аналог для периодической очистки.
- Безопасное удаление: для зашифрованных данных предпочитайте crypto-shredding (удаление ключа, делая данные необратимо нечитаемыми); попытки перезаписи файлов могут не гарантировать полное удаление на уровне ФС/носителя.
- Учитывайте бэкапы: исключите чувствительные файлы из Auto Backup (`android:allowBackup="false"` или настройка `fullBackupContent`) и из собственных механизмов резервного копирования.

### 6. Аудит И Мониторинг

- Ведите audit log действий с данными: какие операции выполнены, каким техническим идентификатором (используйте псевдонимизацию/анонимизацию, не логируйте сами чувствительные значения).
- Настройте риск-алерты (аномальное количество запросов, нетипичные IP/устройства/гео при наличии серверной поддержки).
- Храните необходимые доказательства (evidence) для compliance review, не нарушая принцип минимизации и не дублируя PII в логах.

### 7. Инструменты И Тестирование

- Unit/-интеграционные тесты безопасности: проверяют, что чувствительные данные не попадают в intents, `logcat`, уведомления и незашифрованные файлы.
- Статический анализ: настройте правила (например, Checkstyle/Detekt/Lint) для запрета `Log.*` с PII и для контроля использования безопасных API.
- Security-проверки и пентесты по OWASP MSTG: проверяйте кеши, бэкапы, debug-сборки, обработку root/Jailbreak, экспортируемые компоненты и др.

### Требования

- Функциональные:
  - Поддержка классификации и ретенции для каждого типа чувствительных данных.
  - Шифрование данных at rest и in transit.
  - Управляемое кеширование и безопасное удаление.
  - Аудит ключевых операций над чувствительными данными.
- Нефункциональные:
  - Соответствие требованиям OWASP MSTG и актуальным рекомендациям Android.
  - Минимальное влияние на UX и производительность.
  - Масштабируемость и поддерживаемость политик безопасности.

### Архитектура

- На клиенте:
  - Слой абстракции для доступа к чувствительным данным (secure repository), инкапсулирующий шифрование, кеш и ретенцию.
  - Использование Android Keystore для ключей и Jetpack Security для безопасного хранения.
  - Интеграция с `WorkManager` для фоновой очистки.
- На бэкенде:
  - Централизованное применение политик хранения, логирования и аномалий.
  - Защищённые API (TLS, авторизация, rate limiting) и согласованная модель классификации.

---

## Answer (EN)

### Short Version
- Classify data, minimize collection, and store only what is necessary.
- Use encryption at rest and in transit; keep keys in hardware-backed Keystore.
- Restrict sensitive data caching.
- Enforce explicit retention policies and secure deletion (crypto-shredding).
- Provide auditability, monitoring, and security testing/analysis.

### Detailed Version

- Classify sensitive data (PII, financial, biometric, telemetry), minimize collection, and document purposes; keep classifications updated when schemas or data types change.
- Protect data at rest with encrypted storage (`EncryptedSharedPreferences`, `EncryptedFile` via Jetpack Security, SQLCipher for critical DBs) and store keys in a hardware-backed Keystore with appropriate key properties.
- Secure data in transit with TLS 1.2+; use certificate pinning selectively for high-risk use cases with a well-thought rotation mechanism; avoid sending sensitive data unencrypted. For offline queues, encrypt payloads and add integrity protection (e.g., HMAC).
- Control caching layers: use appropriate HTTP cache headers (e.g., `Cache-Control: no-store`/`no-cache` for PII responses), disable disk caching in image loaders (Glide/Picasso/etc.) for images containing sensitive data, and structure local storage (e.g., Room) so that PII is separated and encrypted at table/column level when needed.
- Enforce explicit retention policies per data type, automate cleanup with scheduled work (e.g., WorkManager), use crypto-shredding (key deletion) as the primary secure deletion mechanism (overwriting files alone does not guarantee secure deletion at the FS/storage level), and exclude sensitive files from OS or custom backups.
- Maintain audit logs of security-relevant actions using pseudonymous identifiers (no raw sensitive values), monitor for anomalies (abnormal access patterns, unusual IPs/devices/geo), and preserve necessary evidence for compliance without violating minimization principles.
- Add automated tests and static analysis rules to detect leaks in logs, intents, notifications, backups, and ensure coverage for caches, backups, debug builds, root/jailbreak handling, and exported components as per OWASP MSTG.

### Requirements

- Functional:
  - Support classification and retention policies per sensitive data type.
  - Provide encryption for data at rest and in transit.
  - Implement controlled caching and secure deletion.
  - Enable auditing of key operations on sensitive data.
- Non-functional:
  - Comply with OWASP MSTG and current Android security guidance.
  - Minimize impact on UX and performance.
  - Ensure scalable and maintainable security policies.

### Architecture

- Client side:
  - A secure data access layer (secure repository) encapsulating encryption, caching, and retention.
  - Android Keystore for key management and Jetpack Security for secure storage.
  - Integration with WorkManager for background cleanup.
- Backend side:
  - Centralized policies for storage, logging, and anomaly detection.
  - Secure APIs (TLS, authorization, rate limiting) and aligned data classification model.

---

## Дополнительные Вопросы (RU)
- Как реализовать пользовательское "забыть меня" (GDPR) с полным удалением и отчетом?
- Как обеспечить безопасную передачу данных между приложением и Wear/IoT устройствами?
- Какие подходы для secret management в рантайме (remote config, key rotation)?

## Follow-ups (EN)
- How would you implement a user "forget me" (GDPR) flow with full deletion and reporting?
- How would you securely transfer data between the app and Wear/IoT devices?
- What runtime secret-management approaches would you use (remote config, key rotation)?

## Ссылки (RU)
- [[c-android-keystore]]
- "https://developer.android.com/topic/security/data"

## References (EN)
- [[c-android-keystore]]
- "https://developer.android.com/topic/security/data"

## Связанные Вопросы (RU)

- [[q-android-security-best-practices--android--medium]]

## Related Questions (EN)

- [[q-android-security-best-practices--android--medium]]
