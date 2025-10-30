---
id: 20251012-12271164
title: "Play App Signing / Подписание приложений Play"
aliases: ["Play App Signing", "Подписание приложений Play", "App Signing Key", "Upload Key"]
topic: android
subtopics: [app-bundle, play-console, keystore-crypto, gradle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-app-bundle, c-android-keystore, c-gradle, q-android-app-bundles--android--easy, q-gradle-build-system--android--medium, q-android-security-best-practices--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android/app-bundle, android/play-console, android/keystore-crypto, android/gradle, play-app-signing, security, signing, difficulty/medium]
sources: [https://developer.android.com/studio/publish/app-signing#app-signing-google-play, https://support.google.com/googleplay/android-developer/answer/9842756]
---

# Вопрос (RU)

> Что такое Play App Signing и как он работает?

# Question (EN)

> What is Play App Signing and how does it work?

---

## Ответ (RU)

**Play App Signing** — это сервис Google, который управляет ключом подписи приложения и использует его для подписи APK, распространяемых пользователям. Ключ хранится в защищённой инфраструктуре Google, что повышает безопасность и упрощает управление ключами.

### Система двух ключей

Play App Signing использует **app signing key** (ключ подписи) и **upload key** (ключ загрузки):

**App Signing Key:**
- Хранится в инфраструктуре Google
- Используется для подписи APK, распространяемых пользователям
- Неизменен в течение жизни приложения (Android требует одинаковый ключ для обновлений)
- Не доступен разработчику после передачи Google

**Upload Key:**
- Хранится у разработчика
- Используется для подписи app bundle/APK перед загрузкой в Play Console
- Может быть сброшен при компрометации через Play Console
- Верифицирует идентичность разработчика

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

### Настройка для новых приложений

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
            storePassword = System.getenv("KEYSTORE_PASSWORD")  # ✅ Секреты в env
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

**2. Android App Bundle:**
- Требуется для публикации AAB (обязательно с августа 2021)
- Уменьшает размер приложения на 15-35% через split APKs
- Динамическая доставка модулей

**3. Key Upgrade:**
- Однократное обновление app signing key для новых установок
- Возможность миграции на более сильный криптографический ключ
- Не влияет на обновления существующих пользователей

### Интеграция с сервисами

**Google APIs / Firebase:**
```bash
# Получение SHA-256 fingerprint upload key
keytool -list -v -keystore upload.jks -alias upload

# Получение app signing key certificate:
# Play Console → App → Setup → App Signing → App signing key certificate
# Регистрация обоих в Google Cloud Console / Firebase
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
      "AA:BB:CC:...",  // app signing key fingerprint
      "DD:EE:FF:..."   // upload key fingerprint (optional)
    ]
  }
}]
```

### Best Practices

✅ **DO:**
- Используйте Play App Signing для всех новых приложений
- Храните upload key в безопасном месте (password manager, secrets vault)
- Используйте переменные окружения для паролей в Gradle
- Включите 2FA на аккаунте Play Console
- Регистрируйте оба ключа (app signing + upload) в Google Cloud Console

❌ **DON'T:**
- Не коммитьте keystores и пароли в git
- Не используйте один keystore для нескольких приложений
- Не храните пароли в gradle.properties (если он в git)
- Не игнорируйте предупреждения о компрометации ключа

## Answer (EN)

**Play App Signing** is a Google service that manages your app's signing key and uses it to sign APKs distributed to users. The key is stored in Google's secure infrastructure, improving security and simplifying key management.

### Two-Key System

Play App Signing uses an **app signing key** and an **upload key**:

**App Signing Key:**
- Stored in Google's infrastructure
- Used to sign APKs distributed to users
- Immutable throughout app lifetime (Android requires same key for updates)
- Not accessible to developer after transferring to Google

**Upload Key:**
- Stored by developer
- Used to sign app bundles/APKs before uploading to Play Console
- Can be reset if compromised via Play Console
- Verifies developer identity

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

**Recommended: Let Google generate app signing key**

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
            storePassword = System.getenv("KEYSTORE_PASSWORD")  # ✅ Secrets in env
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
# Optional: create separate upload key for security
```

### Advantages

**1. Security:**
- App signing key protected by Google infrastructure
- Upload key can be reset if compromised
- App signing key remains safe even if upload key leaks

**2. Android App Bundle:**
- Required for AAB publishing (mandatory since August 2021)
- Reduces app size by 15-35% through split APKs
- Dynamic delivery of modules

**3. Key Upgrade:**
- One-time app signing key upgrade for new installs
- Ability to migrate to stronger cryptographic key
- Does not affect updates for existing users

### Service Integration

**Google APIs / Firebase:**
```bash
# Get SHA-256 fingerprint of upload key
keytool -list -v -keystore upload.jks -alias upload

# Get app signing key certificate:
# Play Console → App → Setup → App Signing → App signing key certificate
# Register both in Google Cloud Console / Firebase
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
      "AA:BB:CC:...",  // app signing key fingerprint
      "DD:EE:FF:..."   // upload key fingerprint (optional)
    ]
  }
}]
```

### Best Practices

✅ **DO:**
- Use Play App Signing for all new apps
- Store upload key in secure location (password manager, secrets vault)
- Use environment variables for passwords in Gradle
- Enable 2FA on Play Console account
- Register both keys (app signing + upload) in Google Cloud Console

❌ **DON'T:**
- Don't commit keystores and passwords to git
- Don't use one keystore for multiple apps
- Don't store passwords in gradle.properties (if in git)
- Don't ignore warnings about key compromise

---

## Follow-ups

- How do you reset an upload key if it's compromised?
- What happens if you lose the app signing key before enrolling in Play App Signing?
- Can you migrate an existing app to Play App Signing?
- How does key rotation affect Android App Links and deep linking?
- What's the difference between debug and release signing configurations?

## References

- [[c-app-bundle|Android App Bundle]]
- [[c-android-keystore|Android Keystore System]]
- [[c-gradle|Gradle Build System]]
- [Play App Signing documentation](https://developer.android.com/studio/publish/app-signing#app-signing-google-play)
- [Use Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-bundles--android--easy|What is Android App Bundle?]]
- [[q-gradle-basics--android--easy|Gradle basics]]

### Related (Same Level)
- [[q-gradle-build-system--android--medium|Gradle build system configuration]]
- [[q-android-security-best-practices--android--medium|Android security best practices]]
- [[q-alternative-distribution--android--medium|Alternative app distribution methods]]

### Advanced (Harder)
- [[q-internal-app-distribution--android--medium|Internal app distribution strategies]]
