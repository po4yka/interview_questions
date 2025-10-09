---
topic: android
tags:
  - android
  - play-app-signing
  - security
  - signing
  - keystore
  - google-play
  - app-bundle
  - difficulty/medium
difficulty: medium
status: reviewed
---

# What is Play App Signing? / Что такое Play App Signing?

**English**: What's Play App Signing?

## Answer

**Play App Signing** is a service where Google manages and protects your app's signing key and uses it to sign optimized, distribution APKs that are generated from your app bundles. Play App Signing stores your app signing key on Google's secure infrastructure and offers upgrade options to increase security.

## Key Concepts

### Two-Key System

Play App Signing uses **two keys**: the **app signing key** and the **upload key**.

**App Signing Key:**
- Managed and stored by Google on secure infrastructure
- Used to sign APKs that are distributed to users
- Never changes during the lifetime of your app (part of Android's secure update model)
- Private key must be kept secret, but you can share the certificate

**Upload Key:**
- Kept by the developer
- Used to sign app bundles or APKs before uploading to Google Play Store
- Google uses the upload certificate to verify your identity
- Can be reset if lost or compromised
- Must be kept secret, but you can share the certificate

**Flow Diagram:**

```
Developer → [Sign with Upload Key] → Upload to Play Store
                                           ↓
                              Google verifies with Upload Certificate
                                           ↓
                              Google signs with App Signing Key
                                           ↓
                              Distribution to Users
```

## Keystores, Keys, and Certificates

### Java Keystores
- Binary files (.jks or .keystore)
- Serve as repositories of certificates and private keys

### Public Key Certificate
- Also known as digital certificate or identity certificate
- Files: .der or .pem
- Contains:
  - Public key of a public/private key pair
  - Metadata identifying the owner (name, location)
  - Owner holds the corresponding private key

### Types of Keys

**1. App Signing Key:**
- Used to sign APKs installed on user's device
- Never changes during app's lifetime (Android's secure update model)
- Private and must be kept secret
- Certificate can be shared

**2. Upload Key:**
- Used to sign app bundle or APK before uploading to Play Store
- Must be kept secret
- Certificate can be shared
- Generated in three ways:
  1. **Google generates app signing key**: Your release signing key becomes upload key
  2. **You provide app signing key**: Option to generate new upload key for increased security
  3. **No new upload key**: Continue using app signing key as upload key

## Setting Up Play App Signing

### For New Apps

**Option 1: Let Google Create App Signing Key (Recommended)**
```bash
# 1. Create upload keystore
keytool -genkey -v -keystore upload-keystore.jks \
  -alias upload -keyalg RSA -keysize 2048 -validity 10000

# 2. Sign your app bundle
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore upload-keystore.jks app-release.aab upload

# 3. Upload to Play Console - Google creates app signing key
```

**Option 2: Use Existing Signing Key**
```bash
# 1. Export existing key certificate
keytool -export -rfc -keystore existing-keystore.jks \
  -alias existing-key -file certificate.pem

# 2. Upload certificate to Play Console

# 3. Optionally create new upload key for security
keytool -genkey -v -keystore upload-keystore.jks \
  -alias upload -keyalg RSA -keysize 2048 -validity 10000
```

### Gradle Configuration

**app/build.gradle.kts (Kotlin DSL):**
```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("path/to/upload-keystore.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
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
```

**Security Best Practice: Use Environment Variables**
```bash
# Set in CI/CD or local environment
export KEYSTORE_PASSWORD="your_keystore_password"
export KEY_PASSWORD="your_key_password"

# Or use gradle.properties (add to .gitignore!)
# ~/.gradle/gradle.properties
KEYSTORE_PASSWORD=your_keystore_password
KEY_PASSWORD=your_key_password
```

## Best Practices

### 1. Distribution Strategy

**If distributing outside Google Play:**
- **Option A (Recommended)**: Let Google generate the key, then download signed universal APK from App Bundle Explorer to distribute outside Play Store
- **Option B**: Generate the app signing key for all app stores, then transfer a copy to Google when configuring Play App Signing

### 2. Security Measures

**Enable 2-Step Verification:**
- Turn on 2-Step Verification for accounts with Play Console access
- Protects your account and signing keys

**Generate Separate Upload Key:**
- For increased security, generate a new upload key different from app signing key
- If upload key is compromised, you can reset it
- App signing key remains safe with Google

### 3. API Integration

**Google APIs:**
- Register both upload key and app signing key certificates in Google Cloud Console
- Ensures APIs work correctly after key rotation

**Android App Links:**
- Update keys in Digital Asset Links JSON file on your website
- Required for deep linking to work properly

```json
// assetlinks.json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.example.app",
    "sha256_cert_fingerprints": [
      "14:6D:E9:83:C5:73:06:50:D8:EE:B9:95:2F:34:FC:64:16:A0:83:42:E6:1D:BE:A8:8A:04:96:B2:3F:CF:44:E5",
      "ANOTHER_FINGERPRINT_FOR_UPLOAD_KEY"
    ]
  }
}]
```

### 4. Testing and Distribution

**App Bundle Explorer Features:**
- **Internal app sharing links**: Test app bundle on different devices with single tap
- **Download signed universal APK**: Get APK signed with app signing key for any device
- **Download device-specific APKs**: Get ZIP with APKs for specific device

**Install device-specific APKs:**
```bash
# Extract ZIP and install all APKs
unzip device-specific-apks.zip
adb install-multiple *.apk
```

## Advantages

### 1. Android App Bundle Support
- Makes app much smaller
- Simplifies releases
- Enables feature modules
- Supports instant experiences
- Dynamic delivery based on device configuration

### 2. Increased Security
- App signing key stored in Google's secure infrastructure
- Separate upload key for daily operations
- Can reset upload key if compromised
- App signing key never exposed

### 3. Key Upgrade
- **One-time key upgrade** for new installs
- Can change app signing key if:
  - Existing one is compromised
  - Need to migrate to cryptographically stronger key
- Only affects new installs, not updates

## Certificate Fingerprints

**Get Upload Key Fingerprint:**
```bash
keytool -list -v -keystore upload-keystore.jks -alias upload
```

**Get App Signing Key Certificate from Play Console:**
1. Go to Play Console → Your App → Setup → App Signing
2. Copy SHA-256 certificate fingerprint
3. Use for Google APIs, Firebase, or App Links configuration

## Migration from Legacy Signing

**For Existing Apps:**
1. Enroll in Play App Signing in Play Console
2. Choose to let Google manage app signing key
3. Optionally generate new upload key
4. Update build configuration to use upload key
5. Update API configurations with new certificates

## Conclusion

Play App Signing is essential for modern Android app distribution:

✅ **Security**: Google manages app signing key securely
✅ **Flexibility**: Separate upload key can be reset
✅ **App Bundle**: Required for Android App Bundle features
✅ **Key Upgrade**: Can upgrade to stronger cryptographic keys
✅ **Peace of Mind**: Google's infrastructure protects signing key

**Always use Play App Signing for new apps, and migrate existing apps when possible.**

**Sources**:
- [Play App Signing](https://developer.android.com/studio/publish/app-signing#app-signing-google-play)
- [Use Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756)

## Ответ

**Play App Signing** — это сервис, в котором Google управляет и защищает ключ подписи вашего приложения и использует его для подписи оптимизированных дистрибутивных APK, которые генерируются из ваших app bundle. Play App Signing хранит ключ подписи приложения в защищённой инфраструктуре Google и предлагает варианты обновления для повышения безопасности.

## Ключевые концепции

### Система двух ключей

Play App Signing использует **два ключа**: **ключ подписи приложения** (app signing key) и **ключ загрузки** (upload key).

**Ключ подписи приложения (App Signing Key):**
- Управляется и хранится Google в защищённой инфраструктуре
- Используется для подписи APK, которые распространяются пользователям
- Никогда не меняется в течение жизни приложения (часть модели безопасного обновления Android)
- Приватный ключ должен храниться в секрете, но можно делиться сертификатом

**Ключ загрузки (Upload Key):**
- Хранится у разработчика
- Используется для подписи app bundle или APK перед загрузкой в Google Play Store
- Google использует сертификат загрузки для проверки вашей личности
- Может быть сброшен, если утерян или скомпрометирован
- Должен храниться в секрете, но можно делиться сертификатом

**Схема потока:**

```
Разработчик → [Подпись ключом загрузки] → Загрузка в Play Store
                                                ↓
                                  Google проверяет сертификат загрузки
                                                ↓
                                  Google подписывает ключом подписи приложения
                                                ↓
                                  Распространение пользователям
```

## Хранилища ключей, ключи и сертификаты

### Java Keystores (Хранилища ключей)
- Бинарные файлы (.jks или .keystore)
- Служат хранилищами сертификатов и приватных ключей

### Сертификат публичного ключа
- Также известен как цифровой сертификат или сертификат идентичности
- Файлы: .der или .pem
- Содержит:
  - Публичный ключ пары публичный/приватный ключ
  - Метаданные, идентифицирующие владельца (имя, местоположение)
  - Владелец хранит соответствующий приватный ключ

## Лучшие практики

### 1. Стратегия распространения

**При распространении вне Google Play:**
- **Вариант A (Рекомендуется)**: Позвольте Google сгенерировать ключ, затем загрузите подписанный универсальный APK из App Bundle Explorer для распространения вне Play Store
- **Вариант B**: Сгенерируйте ключ подписи приложения для всех магазинов приложений, затем передайте копию Google при настройке Play App Signing

### 2. Меры безопасности

**Включите двухфакторную аутентификацию:**
- Включите 2-Step Verification для учётных записей с доступом к Play Console
- Защищает вашу учётную запись и ключи подписи

**Сгенерируйте отдельный ключ загрузки:**
- Для повышения безопасности сгенерируйте новый ключ загрузки, отличный от ключа подписи приложения
- Если ключ загрузки скомпрометирован, вы можете сбросить его
- Ключ подписи приложения остаётся в безопасности у Google

### 3. Интеграция API

**Google APIs:**
- Зарегистрируйте сертификаты как ключа загрузки, так и ключа подписи приложения в Google Cloud Console
- Обеспечивает правильную работу API после ротации ключей

**Android App Links:**
- Обновите ключи в файле Digital Asset Links JSON на вашем веб-сайте
- Требуется для правильной работы deep linking

### 4. Тестирование и распространение

**Возможности App Bundle Explorer:**
- **Ссылки для внутреннего обмена приложениями**: Тестируйте app bundle на разных устройствах одним касанием
- **Загрузка подписанного универсального APK**: Получите APK, подписанный ключом подписи приложения для любого устройства
- **Загрузка APK для конкретного устройства**: Получите ZIP с APK для конкретного устройства

## Преимущества

### 1. Поддержка Android App Bundle
- Делает приложение намного меньше
- Упрощает релизы
- Позволяет использовать модули функций
- Поддерживает мгновенные впечатления
- Динамическая доставка на основе конфигурации устройства

### 2. Повышенная безопасность
- Ключ подписи приложения хранится в защищённой инфраструктуре Google
- Отдельный ключ загрузки для ежедневных операций
- Можно сбросить ключ загрузки, если он скомпрометирован
- Ключ подписи приложения никогда не раскрывается

### 3. Обновление ключа
- **Однократное обновление ключа** для новых установок
- Можно изменить ключ подписи приложения, если:
  - Существующий скомпрометирован
  - Необходимо перейти на криптографически более сильный ключ
- Затрагивает только новые установки, а не обновления

## Заключение

Play App Signing необходим для современного распространения приложений Android:

✅ **Безопасность**: Google безопасно управляет ключом подписи приложения
✅ **Гибкость**: Отдельный ключ загрузки может быть сброшен
✅ **App Bundle**: Требуется для функций Android App Bundle
✅ **Обновление ключа**: Можно обновить до более сильных криптографических ключей
✅ **Спокойствие**: Инфраструктура Google защищает ключ подписи

**Всегда используйте Play App Signing для новых приложений и мигрируйте существующие приложения, когда это возможно.**
