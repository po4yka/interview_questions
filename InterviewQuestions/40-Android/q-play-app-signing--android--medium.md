---
id: android-302
title: "Play App Signing / Подписание приложений Play"
aliases: ["App Signing Key", "Play App Signing", "Upload Key", "Подписание приложений Play"]
topic: android
subtopics: [app-bundle, keystore-crypto, play-console]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-keystore, c-app-bundle, q-android-app-bundles--android--easy, q-android-security-best-practices--android--medium, q-android-release-pipeline-cicd--android--hard]
created: 2025-10-15
updated: 2025-11-10
tags: [android/app-bundle, android/keystore-crypto, android/play-console, difficulty/medium, play-app-signing, security, signing]
sources: ["https://developer.android.com/studio/publish/app-signing#app-signing-google-play", "https://support.google.com/googleplay/android-developer/answer/9842756"]
---

# Вопрос (RU)

> Что такое Play App Signing и как он работает?

# Question (EN)

> What is Play App Signing and how does it work?

---

## Ответ (RU)

**Play App Signing** — это сервис Google, который управляет ключом подписи приложения и использует его для подписи артефактов (APKs, split APKs, пакетов для старых устройств), которые получают пользователи при установке через Google Play. Ключ хранится в защищённой инфраструктуре Google, что повышает безопасность и упрощает управление ключами.

### Система Двух Ключей

Play App Signing использует **app signing key** (ключ подписи приложения) и **upload key** (ключ загрузки):

**App Signing Key:**
- Хранится в инфраструктуре Google
- Используется для подписи пакетов, распространяемых пользователям
- Должен оставаться стабильным для обеспечения возможности обновления (Android требует совместимость подписи для обновлений)
- После передачи Google приватный ключ не доступен разработчику (доступен только сертификат)

**Upload Key:**
- Хранится у разработчика
- Используется для подписи app bundle/APK перед загрузкой в Play Console
- Может быть сброшен при компрометации через Play Console
- Используется Google для проверки подлинности загрузчика и привязки к учётной записи разработчика

**Процесс:**
```
Разработчик → подпись upload key → загрузка в Play Console
                                           ↓
                            Google верифицирует upload certificate
                                           ↓
                            Google подписывает app signing key
                                           ↓
                            Распространение пользователям
```

### Настройка Для Новых Приложений

**Рекомендуемый способ: Google генерирует app signing key**

```bash
# 1. Создание upload keystore
keytool -genkey -v -keystore upload.jks \
  -alias upload -keyalg RSA -keysize 2048 -validity 10000

# 2. Конфигурация Gradle
# app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file("../upload.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")  # ✅ Секреты из окружения или секрет-хранилища
            keyAlias = "upload"
            keyPassword = System.getenv("KEY_PASSWORD")
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}

# ❌ Не хардкодить пароли в build.gradle
# storePassword = "hardcoded_password"  # FORBIDDEN
```

**Использование существующего ключа:**
```bash
# Экспорт сертификата
keytool -export -rfc -keystore existing.jks \
  -alias key-alias -file certificate.pem

# Загрузка в Play Console → App Signing
# Опционально: создание отдельного upload key для безопасности
```

### Преимущества

**1. Безопасность:**
- App signing key защищён инфраструктурой Google
- Upload key можно сбросить при компрометации
- App signing key остаётся в безопасности даже при утечке upload key

**2. Android App `Bundle`:**
- Требуется для публикации AAB (обязательно с августа 2021)
- Уменьшает размер приложения на ~15–35% за счёт split APKs и конфигурационно-осознанной доставки
- Позволяет динамическую доставку модулей

**3. Key Upgrade (ротация ключа подписи через Google Play):**
- Возможность один раз обновить app signing key для новых установок и поддерживаемых API уровней/треков через Play Console
- Используется для миграции на более сильный криптографический ключ
- Требует обновления интеграций, зависящих от сертификата подписи (App Links, некоторые Google APIs/Firebase конфигурации) на новый сертификат

### Интеграция с Сервисами

**Google APIs / Firebase:**
```bash
# Получение SHA-256 отпечатка upload key (при необходимости для проверок в Play):
keytool -list -v -keystore upload.jks -alias upload

# Получение сертификата app signing key:
# Play Console → App → Setup → App Signing → App signing key certificate
# Для OAuth-клиентов, Firebase и подобных интеграций, как правило, используйте сертификат app signing key.
```

**Android App Links:**
```json
// assetlinks.json на вашем домене
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.example.app",
    "sha256_cert_fingerprints": [
      "AA:BB:CC:..."  // отпечаток сертификата app signing key (ключ, которым подписан релизный билд из Play)
    ]
  }
}]
```

### Best Practices

✅ **DO:**
- Используйте Play App Signing для всех новых приложений
- Храните upload key в безопасном месте (password manager, secrets vault)
- Используйте переменные окружения или защищённые секреты для паролей в Gradle
- Включите 2FA на аккаунте Play Console
- Для интеграций с Google APIs/Firebase опирайтесь на сертификат app signing key (из Play App Signing)

❌ **DON'T:**
- Не коммитьте keystores и пароли в git
- Не используйте один keystore для нескольких приложений
- Не храните пароли в gradle.properties, если этот файл в git без защиты
- Не игнорируйте предупреждения о компрометации ключа

---

## Answer (EN)

**Play App Signing** is a Google service that manages your app's signing key and uses it to sign the artifacts (APKs, split APKs, legacy APKs) that users receive when installing from Google Play. The key is stored in Google's secure infrastructure, improving security and simplifying key management.

### Two-Key System

Play App Signing uses an **app signing key** and an **upload key**:

**App Signing Key:**
- Stored in Google's infrastructure
- Used to sign packages distributed to users
- Must remain stable to allow updates (Android requires compatible signing for updates)
- After transfer to Google, the private key itself is not accessible to the developer (only the certificate is available)

**Upload Key:**
- Stored by the developer
- Used to sign app bundles/APKs before uploading to Play Console
- Can be reset if compromised via Play Console
- Used by Google to verify uploader identity and association with the developer account

**Flow:**
```
Developer → sign with upload key → upload to Play Console
                                          ↓
                          Google verifies upload certificate
                                          ↓
                          Google signs with app signing key
                                          ↓
                          Distribution to users
```

### Setup for New Apps

**Recommended: Let Google generate the app signing key**

```bash
# 1. Create upload keystore
keytool -genkey -v -keystore upload.jks \
  -alias upload -keyalg RSA -keysize 2048 -validity 10000

# 2. Configure Gradle
# app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file("../upload.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")  # ✅ Secrets from env or secret store
            keyAlias = "upload"
            keyPassword = System.getenv("KEY_PASSWORD")
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}

# ❌ Don't hardcode passwords in build.gradle
# storePassword = "hardcoded_password"  # FORBIDDEN
```

**Using existing key:**
```bash
# Export certificate
keytool -export -rfc -keystore existing.jks \
  -alias key-alias -file certificate.pem

# Upload to Play Console → App Signing
# Optional: create a separate upload key for security
```

### Advantages

**1. Security:**
- App signing key protected by Google infrastructure
- Upload key can be reset if compromised
- App signing key remains safe even if upload key leaks

**2. Android App `Bundle`:**
- Required for AAB publishing (mandatory since August 2021)
- Reduces app size by ~15–35% via split APKs and configuration-aware delivery
- Enables dynamic feature/module delivery

**3. Key Upgrade (Google Play signing key rotation):**
- One-time ability to upgrade the app signing key for new installs and eligible API levels/tracks via Play Console
- Used to migrate to a stronger cryptographic key
- Requires updating dependent integrations (App Links, some Google APIs/Firebase configs) to the new certificate

### Service Integration

**Google APIs / Firebase:**
```bash
# Get SHA-256 fingerprint of the upload key (for Play-related verification scenarios if needed):
keytool -list -v -keystore upload.jks -alias upload

# Get app signing key certificate:
# Play Console → App → Setup → App Signing → App signing key certificate
# For OAuth clients, Firebase, and similar integrations, typically use the app signing key certificate.
```

**Android App Links:**
```json
// assetlinks.json on your domain
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.example.app",
    "sha256_cert_fingerprints": [
      "AA:BB:CC:..."  // fingerprint of the app signing key certificate (the key used to sign Play-distributed builds)
    ]
  }
}]
```

### Best Practices

✅ **DO:**
- Use Play App Signing for all new apps
- Store the upload key in a secure location (password manager, secrets vault)
- Use environment variables or protected secrets for passwords in Gradle
- Enable 2FA on your Play Console account
- For Google APIs/Firebase and similar integrations, base configuration on the app signing key certificate from Play

❌ **DON'T:**
- Don't commit keystores and passwords to git
- Don't use one keystore for multiple apps
- Don't store passwords in gradle.properties if that file is in git without proper protection
- Don't ignore warnings about key compromise

---

## Дополнительные вопросы (RU)

- Как сбросить upload key, если он был скомпрометирован?
- Что произойдёт, если вы потеряете app signing key до подключения к Play App Signing?
- Можно ли мигрировать существующее приложение на Play App Signing?
- Как ротация ключа влияет на Android App Links и глубокие ссылки?
- В чём разница между debug и release конфигурациями подписания?

## Follow-ups

- How do you reset an upload key if it's compromised?
- What happens if you lose the app signing key before enrolling in Play App Signing?
- Can you migrate an existing app to Play App Signing?
- How does key rotation affect Android App Links and deep linking?
- What's the difference between debug and release signing configurations?

## Ссылки (RU)

- [[c-app-bundle|Android App `Bundle`]]
- [[c-android-keystore|Android Keystore System]]
- [Документация Play App Signing](https://developer.android.com/studio/publish/app-signing#app-signing-google-play)
- [Использование Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756)

## References

- [[c-app-bundle|Android App `Bundle`]]
- [[c-android-keystore|Android Keystore System]]
- [Play App Signing documentation](https://developer.android.com/studio/publish/app-signing#app-signing-google-play)
- [Use Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756)

## Связанные вопросы (RU)

### Предпосылки (проще)
- [[q-android-app-bundles--android--easy|Что такое Android App `Bundle`?]]

### Связанные (того же уровня)
- [[q-android-release-pipeline-cicd--android--hard|Пайплайн релизов Android и лучшие практики CI/CD]]
- [[q-android-security-best-practices--android--medium|Лучшие практики безопасности Android]]
- [[q-alternative-distribution--android--medium|Альтернативные способы дистрибуции приложений]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-bundles--android--easy|What is Android App `Bundle`?]]

### Related (Same Level)
- [[q-android-release-pipeline-cicd--android--hard|Android release pipeline and CI/CD best practices]]
- [[q-android-security-best-practices--android--medium|Android security best practices]]
- [[q-alternative-distribution--android--medium|Alternative app distribution methods]]
