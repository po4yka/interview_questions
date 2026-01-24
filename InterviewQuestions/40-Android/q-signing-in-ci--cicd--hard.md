---
id: android-cicd-006
title: "Secure Signing in CI / Безопасное Подписание в CI"
aliases: ["Secure Signing in CI", "Безопасное Подписание в CI"]
topic: android
subtopics: [cicd, security, signing]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-github-actions-android--cicd--medium, q-play-store-deployment--cicd--medium, q-build-variants-flavors--cicd--medium]
created: 2026-01-23
updated: 2026-01-23
sources: ["https://developer.android.com/studio/publish/app-signing", "https://docs.github.com/en/actions/security-guides/encrypted-secrets"]
tags: [android/cicd, android/security, difficulty/hard, signing, secrets-management]

---
# Вопрос (RU)

> Как безопасно организовать подписание Android-приложения в CI/CD pipeline?

# Question (EN)

> How do you securely sign Android applications in a CI/CD pipeline?

## Ответ (RU)

Безопасное подписание в CI требует защиты ключей подписи, паролей и сертификатов. Основные принципы: **никогда не коммитить ключи в git**, **использовать секреты CI**, **разделять upload key и signing key**.

### Типы Ключей

| Ключ | Назначение | Где Хранить |
|------|------------|-------------|
| Signing Key | Подпись для Play Store | Google (Play App Signing) |
| Upload Key | Загрузка в Play Console | CI Secrets |
| Debug Key | Отладочные сборки | Автогенерация |

### Play App Signing (Рекомендуемый Подход)

Google управляет signing key, вы управляете upload key:

```
Developer           Google Play
    |                    |
Upload Key ------>  Play App Signing
(в CI)                   |
    |               Signing Key
    |               (у Google)
    +--- AAB ----------->|
                         |
                    APK (signed)
                         |
                    Users
```

**Преимущества**:
- Signing key никогда не покидает Google
- При утере upload key можно получить новый
- Защита от компромиссии ключа

### Хранение Секретов

#### GitHub Actions Secrets

```yaml
# Секреты в Repository Settings -> Secrets and variables -> Actions

# 1. Keystore закодированный в base64
KEYSTORE_BASE64: <base64-encoded-keystore>

# 2. Пароли
KEYSTORE_PASSWORD: <password>
KEY_ALIAS: <alias>
KEY_PASSWORD: <key-password>

# 3. Service Account для Play Store
PLAY_STORE_CREDENTIALS: <base64-encoded-json>
```

#### Кодирование Keystore

```bash
# Кодирование в base64
base64 -i release.keystore -o keystore.base64

# Или одной строкой
cat release.keystore | base64

# Декодирование
echo $KEYSTORE_BASE64 | base64 -d > release.keystore
```

### Конфигурация Gradle

```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            // Получение из environment variables
            val keystorePath = System.getenv("KEYSTORE_PATH")
            val keystorePassword = System.getenv("KEYSTORE_PASSWORD")
            val keyAliasValue = System.getenv("KEY_ALIAS")
            val keyPasswordValue = System.getenv("KEY_PASSWORD")

            if (keystorePath != null && File(keystorePath).exists()) {
                storeFile = file(keystorePath)
                storePassword = keystorePassword
                keyAlias = keyAliasValue
                keyPassword = keyPasswordValue
            } else {
                // Fallback для локальной разработки
                val localProps = Properties().apply {
                    val file = rootProject.file("local.properties")
                    if (file.exists()) load(file.inputStream())
                }
                storeFile = file(localProps.getProperty("signing.storeFile") ?: "debug.keystore")
                storePassword = localProps.getProperty("signing.storePassword") ?: ""
                keyAlias = localProps.getProperty("signing.keyAlias") ?: ""
                keyPassword = localProps.getProperty("signing.keyPassword") ?: ""
            }
        }
    }

    buildTypes {
        release {
            signingConfig = try {
                signingConfigs.getByName("release")
            } catch (e: Exception) {
                null  // Не падать, если нет ключей
            }
        }
    }
}
```

### GitHub Actions Workflow

```yaml
name: Release Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      # КРИТИЧНО: Декодирование keystore из секрета
      - name: Decode Keystore
        env:
          ENCODED_KEYSTORE: ${{ secrets.KEYSTORE_BASE64 }}
        run: |
          echo $ENCODED_KEYSTORE | base64 -d > ${{ github.workspace }}/release.keystore
          # Проверка, что файл создан
          ls -la ${{ github.workspace }}/release.keystore

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      # Передача секретов через environment
      - name: Build Release Bundle
        env:
          KEYSTORE_PATH: ${{ github.workspace }}/release.keystore
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      # Удаление keystore после сборки
      - name: Cleanup Keystore
        if: always()
        run: rm -f ${{ github.workspace }}/release.keystore

      - name: Upload Bundle
        uses: actions/upload-artifact@v4
        with:
          name: release-bundle
          path: app/build/outputs/bundle/release/*.aab
```

### Продвинутые Практики

#### 1. Environment-specific Secrets

```yaml
# Разные секреты для разных окружений
jobs:
  build-staging:
    environment: staging
    # Использует секреты из environment 'staging'

  build-production:
    environment: production
    # Использует секреты из environment 'production'
```

#### 2. OIDC для Беспарольной Аутентификации

```yaml
# Без долгоживущих секретов
permissions:
  id-token: write
  contents: read

- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/123456/locations/global/workloadIdentityPools/my-pool/providers/my-provider'
    service_account: 'my-service-account@my-project.iam.gserviceaccount.com'
```

#### 3. HashiCorp Vault Integration

```yaml
- name: Import Secrets from Vault
  uses: hashicorp/vault-action@v2
  with:
    url: https://vault.example.com
    method: jwt
    role: android-signer
    secrets: |
      secret/data/android/signing keystore | KEYSTORE_BASE64 ;
      secret/data/android/signing password | KEYSTORE_PASSWORD ;
      secret/data/android/signing alias | KEY_ALIAS ;
      secret/data/android/signing key_password | KEY_PASSWORD
```

#### 4. Временные Файлы в Памяти

```yaml
# Использование tmpfs для секретов (не записывается на диск)
- name: Create secure temp directory
  run: |
    mkdir -p /dev/shm/signing
    chmod 700 /dev/shm/signing

- name: Decode Keystore to memory
  run: echo ${{ secrets.KEYSTORE_BASE64 }} | base64 -d > /dev/shm/signing/release.keystore

- name: Build
  env:
    KEYSTORE_PATH: /dev/shm/signing/release.keystore
  run: ./gradlew bundleRelease

- name: Cleanup
  if: always()
  run: rm -rf /dev/shm/signing
```

### Ротация Ключей

#### Upload Key Rotation

```bash
# 1. Генерация нового upload key
keytool -genkeypair -v \
  -keystore new-upload.keystore \
  -keyalg RSA -keysize 2048 \
  -validity 10000 \
  -alias upload

# 2. Экспорт сертификата
keytool -export -rfc \
  -keystore new-upload.keystore \
  -alias upload \
  -file upload_certificate.pem

# 3. Загрузка в Play Console
# Play Console -> Release -> Setup -> App signing -> Request upload key reset
```

#### Авто-ротация в CI

```yaml
# Ежемесячная проверка срока действия
- name: Check Certificate Expiry
  run: |
    EXPIRY=$(keytool -list -v -keystore release.keystore -storepass ${{ secrets.KEYSTORE_PASSWORD }} | grep "Valid from" | head -1)
    echo "Certificate validity: $EXPIRY"
    # Проверить и уведомить если менее 90 дней
```

### Безопасность Проверки

#### 1. Аудитирование Доступа к Секретам

```yaml
- name: Log Secret Access
  run: |
    echo "Secrets accessed by workflow: ${{ github.workflow }}"
    echo "Triggered by: ${{ github.actor }}"
    echo "Ref: ${{ github.ref }}"
    # Логировать в SIEM/audit system
```

#### 2. Ограничение Доступа

```yaml
# Только для main/release branches
on:
  push:
    branches: [main]
    tags: ['v*']

# Требует approval для production
jobs:
  deploy:
    environment:
      name: production
      # Требует manual approval
```

#### 3. Проверка Артефактов

```yaml
- name: Verify APK Signature
  run: |
    apksigner verify --print-certs app/build/outputs/apk/release/app-release.apk
    # Проверить, что подпись соответствует ожидаемому сертификату
```

### Антипаттерны (Чего Избегать)

| Плохо | Почему | Как Правильно |
|-------|--------|---------------|
| Keystore в git | Утечка ключей | GitHub Secrets |
| Пароли в build.gradle | Видны в логах | Environment variables |
| Один ключ на всё | Нет разделения | Upload + Signing keys |
| Бесконечная валидность | Нет ротации | Ротация каждые 1-2 года |
| Без cleanup | Ключ остаётся | `if: always()` cleanup |

### Чеклист Безопасности

- [ ] Keystore НЕ в git (добавлен в .gitignore)
- [ ] Пароли в CI Secrets, не в коде
- [ ] Play App Signing включён
- [ ] Upload key отделён от signing key
- [ ] Keystore удаляется после сборки
- [ ] Доступ к секретам ограничен
- [ ] Ротация ключей запланирована
- [ ] Audit log включён
- [ ] Environment separation (staging/prod)

### Резюме

| Аспект | Рекомендация |
|--------|--------------|
| Хранение ключей | CI Secrets + Play App Signing |
| Передача в Gradle | Environment variables |
| Cleanup | `if: always()` удаление |
| Ротация | Каждые 1-2 года для upload key |
| Аудит | Логирование доступа к секретам |

## Answer (EN)

Secure signing in CI requires protecting signing keys, passwords, and certificates. Core principles: **never commit keys to git**, **use CI secrets**, **separate upload key from signing key**.

### Key Types

| Key | Purpose | Where to Store |
|-----|---------|----------------|
| Signing Key | Play Store signature | Google (Play App Signing) |
| Upload Key | Upload to Play Console | CI Secrets |
| Debug Key | Debug builds | Auto-generated |

### Play App Signing (Recommended Approach)

Google manages the signing key, you manage the upload key:

```
Developer           Google Play
    |                    |
Upload Key ------>  Play App Signing
(in CI)                  |
    |               Signing Key
    |               (at Google)
    +--- AAB ----------->|
                         |
                    APK (signed)
                         |
                    Users
```

**Benefits**:
- Signing key never leaves Google
- Can get new upload key if lost
- Protection against key compromise

### Secret Storage

#### GitHub Actions Secrets

```yaml
# Secrets in Repository Settings -> Secrets and variables -> Actions

# 1. Base64-encoded keystore
KEYSTORE_BASE64: <base64-encoded-keystore>

# 2. Passwords
KEYSTORE_PASSWORD: <password>
KEY_ALIAS: <alias>
KEY_PASSWORD: <key-password>

# 3. Service Account for Play Store
PLAY_STORE_CREDENTIALS: <base64-encoded-json>
```

#### Encoding Keystore

```bash
# Encode to base64
base64 -i release.keystore -o keystore.base64

# Or single line
cat release.keystore | base64

# Decode
echo $KEYSTORE_BASE64 | base64 -d > release.keystore
```

### Gradle Configuration

```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            // Get from environment variables
            val keystorePath = System.getenv("KEYSTORE_PATH")
            val keystorePassword = System.getenv("KEYSTORE_PASSWORD")
            val keyAliasValue = System.getenv("KEY_ALIAS")
            val keyPasswordValue = System.getenv("KEY_PASSWORD")

            if (keystorePath != null && File(keystorePath).exists()) {
                storeFile = file(keystorePath)
                storePassword = keystorePassword
                keyAlias = keyAliasValue
                keyPassword = keyPasswordValue
            } else {
                // Fallback for local development
                val localProps = Properties().apply {
                    val file = rootProject.file("local.properties")
                    if (file.exists()) load(file.inputStream())
                }
                storeFile = file(localProps.getProperty("signing.storeFile") ?: "debug.keystore")
                storePassword = localProps.getProperty("signing.storePassword") ?: ""
                keyAlias = localProps.getProperty("signing.keyAlias") ?: ""
                keyPassword = localProps.getProperty("signing.keyPassword") ?: ""
            }
        }
    }

    buildTypes {
        release {
            signingConfig = try {
                signingConfigs.getByName("release")
            } catch (e: Exception) {
                null  // Don't fail if no keys
            }
        }
    }
}
```

### GitHub Actions Workflow

```yaml
name: Release Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      # CRITICAL: Decode keystore from secret
      - name: Decode Keystore
        env:
          ENCODED_KEYSTORE: ${{ secrets.KEYSTORE_BASE64 }}
        run: |
          echo $ENCODED_KEYSTORE | base64 -d > ${{ github.workspace }}/release.keystore
          # Verify file was created
          ls -la ${{ github.workspace }}/release.keystore

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      # Pass secrets via environment
      - name: Build Release Bundle
        env:
          KEYSTORE_PATH: ${{ github.workspace }}/release.keystore
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      # Delete keystore after build
      - name: Cleanup Keystore
        if: always()
        run: rm -f ${{ github.workspace }}/release.keystore

      - name: Upload Bundle
        uses: actions/upload-artifact@v4
        with:
          name: release-bundle
          path: app/build/outputs/bundle/release/*.aab
```

### Advanced Practices

#### 1. Environment-specific Secrets

```yaml
# Different secrets for different environments
jobs:
  build-staging:
    environment: staging
    # Uses secrets from 'staging' environment

  build-production:
    environment: production
    # Uses secrets from 'production' environment
```

#### 2. OIDC for Passwordless Authentication

```yaml
# No long-lived secrets
permissions:
  id-token: write
  contents: read

- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/123456/locations/global/workloadIdentityPools/my-pool/providers/my-provider'
    service_account: 'my-service-account@my-project.iam.gserviceaccount.com'
```

#### 3. HashiCorp Vault Integration

```yaml
- name: Import Secrets from Vault
  uses: hashicorp/vault-action@v2
  with:
    url: https://vault.example.com
    method: jwt
    role: android-signer
    secrets: |
      secret/data/android/signing keystore | KEYSTORE_BASE64 ;
      secret/data/android/signing password | KEYSTORE_PASSWORD ;
      secret/data/android/signing alias | KEY_ALIAS ;
      secret/data/android/signing key_password | KEY_PASSWORD
```

#### 4. Temporary Files in Memory

```yaml
# Use tmpfs for secrets (not written to disk)
- name: Create secure temp directory
  run: |
    mkdir -p /dev/shm/signing
    chmod 700 /dev/shm/signing

- name: Decode Keystore to memory
  run: echo ${{ secrets.KEYSTORE_BASE64 }} | base64 -d > /dev/shm/signing/release.keystore

- name: Build
  env:
    KEYSTORE_PATH: /dev/shm/signing/release.keystore
  run: ./gradlew bundleRelease

- name: Cleanup
  if: always()
  run: rm -rf /dev/shm/signing
```

### Key Rotation

#### Upload Key Rotation

```bash
# 1. Generate new upload key
keytool -genkeypair -v \
  -keystore new-upload.keystore \
  -keyalg RSA -keysize 2048 \
  -validity 10000 \
  -alias upload

# 2. Export certificate
keytool -export -rfc \
  -keystore new-upload.keystore \
  -alias upload \
  -file upload_certificate.pem

# 3. Upload to Play Console
# Play Console -> Release -> Setup -> App signing -> Request upload key reset
```

#### Auto-rotation in CI

```yaml
# Monthly expiry check
- name: Check Certificate Expiry
  run: |
    EXPIRY=$(keytool -list -v -keystore release.keystore -storepass ${{ secrets.KEYSTORE_PASSWORD }} | grep "Valid from" | head -1)
    echo "Certificate validity: $EXPIRY"
    # Check and notify if less than 90 days
```

### Security Verification

#### 1. Secret Access Auditing

```yaml
- name: Log Secret Access
  run: |
    echo "Secrets accessed by workflow: ${{ github.workflow }}"
    echo "Triggered by: ${{ github.actor }}"
    echo "Ref: ${{ github.ref }}"
    # Log to SIEM/audit system
```

#### 2. Access Restriction

```yaml
# Only for main/release branches
on:
  push:
    branches: [main]
    tags: ['v*']

# Require approval for production
jobs:
  deploy:
    environment:
      name: production
      # Requires manual approval
```

#### 3. Artifact Verification

```yaml
- name: Verify APK Signature
  run: |
    apksigner verify --print-certs app/build/outputs/apk/release/app-release.apk
    # Verify signature matches expected certificate
```

### Anti-patterns (What to Avoid)

| Bad | Why | Correct Way |
|-----|-----|-------------|
| Keystore in git | Key leak | GitHub Secrets |
| Passwords in build.gradle | Visible in logs | Environment variables |
| One key for all | No separation | Upload + Signing keys |
| Infinite validity | No rotation | Rotate every 1-2 years |
| No cleanup | Key remains | `if: always()` cleanup |

### Security Checklist

- [ ] Keystore NOT in git (added to .gitignore)
- [ ] Passwords in CI Secrets, not in code
- [ ] Play App Signing enabled
- [ ] Upload key separate from signing key
- [ ] Keystore deleted after build
- [ ] Secret access restricted
- [ ] Key rotation scheduled
- [ ] Audit log enabled
- [ ] Environment separation (staging/prod)

### Summary

| Aspect | Recommendation |
|--------|----------------|
| Key storage | CI Secrets + Play App Signing |
| Pass to Gradle | Environment variables |
| Cleanup | `if: always()` deletion |
| Rotation | Every 1-2 years for upload key |
| Audit | Log secret access |

## Дополнительные Вопросы (RU)

1. Как обрабатывать компромиссию ключа в экстренной ситуации?
2. Каковы компромиссы между самостоятельным подписанием и Play App Signing?
3. Как реализовать мультирегиональное подписание для соответствия требованиям?
4. Как защитить debug signing keys в командной среде?

## Follow-ups

1. How do you handle key compromise in an emergency?
2. What are the trade-offs between self-signing and Play App Signing?
3. How do you implement multi-region signing for compliance?
4. How do you secure debug signing keys in a team environment?

## Ссылки (RU)

- [Подписание приложений](https://developer.android.com/studio/publish/app-signing)
- [Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756)
- [GitHub Actions Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

## References

- [App Signing](https://developer.android.com/studio/publish/app-signing)
- [Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756)
- [GitHub Actions Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Keytool Documentation](https://docs.oracle.com/en/java/javase/17/docs/specs/man/keytool.html)

## Связанные Вопросы (RU)

### Предпосылки
- [[q-github-actions-android--cicd--medium]] — Настройка GitHub Actions
- [[q-build-variants-flavors--cicd--medium]] — Варианты сборки

### Похожие
- [[q-play-store-deployment--cicd--medium]] — Публикация в Play Store
- [[q-app-distribution--cicd--medium]] — Распределение приложений

### Продвинутое
- [[q-gradle-build-cache--cicd--medium]] — Оптимизация сборки

## Related Questions

### Prerequisites
- [[q-github-actions-android--cicd--medium]] - GitHub Actions setup
- [[q-build-variants-flavors--cicd--medium]] - Build variants

### Related
- [[q-play-store-deployment--cicd--medium]] - Play Store deployment
- [[q-app-distribution--cicd--medium]] - App distribution

### Advanced
- [[q-gradle-build-cache--cicd--medium]] - Build optimization
