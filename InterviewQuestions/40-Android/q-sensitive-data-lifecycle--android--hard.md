---
id: android-637
title: Sensitive Data Lifecycle / Жизненный цикл чувствительных данных
aliases:
  - Sensitive Data Lifecycle
  - Жизненный цикл чувствительных данных
topic: android
subtopics:
  - security
  - privacy
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
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/security
  - android/privacy
  - data-lifecycle
  - difficulty/hard
sources:
  - url: https://developer.android.com/topic/security/data
    note: Protecting user data guide
  - url: https://developer.android.com/topic/security/best-practices
    note: Android security best practices
  - url: https://owasp.org/www-project-mobile-security-testing-guide/
    note: OWASP MSTG data storage/testing guidance
---

# Вопрос (RU)
> Как построить систему управления жизненным циклом чувствительных данных в Android: классификация, минимизация, шифрование, контролируемое кеширование, безопасное удаление и аудит?

# Question (EN)
> How do you manage the lifecycle of sensitive data in an Android app, covering classification, minimization, encryption, controlled caching, secure deletion, and auditing?

---

## Ответ (RU)

### 1. Классификация и минимизация

- Разбейте данные на уровни (PII, финансовые, biometrics, telemetry).
- Принцип минимизации: не собирайте данные без явной цели.
- Обновляйте классификацию при изменении схем (Room migrations, DTO).

### 2. Хранение (at rest)

- Используйте `EncryptedSharedPreferences`, `EncryptedFile`, `SQLCipher` или Jetpack Security.
- Для кешей — `File.createTempFile` в `context.cacheDir`, стирайте после использования.
- Изолируйте ключи через `Hardware-backed Keystore` (AES/GCM, key validity).

### 3. Передача (in transit)

- TLS 1.2+ с pinning, избегайте передач без шифрования.
- Учитывайте offline-сценарии: шифруйте payload перед сохранением в очередь отправки.
- Добавьте подпись (HMAC) для целостности.

### 4. Контролируемое кеширование

- Network layer: отключайте HTTP caching для содержимого с PII (`Cache-Control: no-store`).
- Glide/Picasso: используйте `DiskCacheStrategy.NONE` для аватаров чувствительных пользователей.
- Room: разделяйте таблицы с PII и нефинансовыми данными (column-level encryption).

### 5. Удаление и ретенция

- Имплементируйте retention policy (в днях). Используйте `WorkManager` для периодической чистки.
- Безопасное удаление: перезаписывать файл (или удалять key, если данные зашифрованы → crypto-shredding).
- Учитывайте backup: исключите файлы из Auto Backup (`android:allowBackup="false"` или `fullBackupContent`).

### 6. Аудит и мониторинг

- Ведите audit log: кто запросил/изменил данные (анонимизируйте ID).
- Настройте риск-алерты (много запросов подряд, необычные IP).
- Храните доказательства (evidence) для compliance review.

### 7. Инструменты и тестирование

- Security unit tests: проверяют, что данные не попадают в intents/logcat.
- Static анализ: checkstyle/Detekt rules -> запрет `Log.d` с PII.
- Penetration testing/OWASP MSTG: проверка кешей, backup, debug builds.

---

## Answer (EN)

- Classify sensitive data, minimize collection, and document use cases; keep the taxonomy up to date with schema changes.
- Protect data at rest with encrypted storage (Jetpack Security, SQLCipher) and store keys in hardware-backed keystore.
- Secure data in transit with TLS and optional payload encryption/HMAC for offline queues.
- Control caching layers (HTTP, image loaders, Room) to prevent unintended persistence of PII.
- Enforce retention policies, automate secure deletion (or crypto-shredding), and exclude sensitive files from backups.
- Maintain audit logs, monitor for anomalies, and provide evidence for compliance reviews.
- Add automated tests and static analysis to prevent leaks in logs, intents, or backups.

---

## Follow-ups
- Как реализовать пользовательское \"забыть меня\" (GDPR) с полным удалением и отчетом?
- Как обеспечить безопасную передачу данных между приложением и Wear/IoT устройствами?
- Какие подходы для secret management в рантайме (remote config, key rotation)?

## References
- [[c-security-hardening]]
- https://developer.android.com/topic/security/data

## Related Questions

- [[c-security-hardening]]
