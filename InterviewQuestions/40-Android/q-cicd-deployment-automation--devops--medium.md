---
tags:
  - android
  - ci-cd
  - deployment
  - play-store
  - fastlane
  - automation
difficulty: medium
status: draft
related:
  - q-cicd-pipeline-setup--devops--medium
  - q-app-bundle-optimization--distribution--medium
  - q-app-versioning-release--distribution--medium
created: 2025-10-11
---

# Question (EN)
How do you automate Android app deployment to the Play Store? Explain the process of signing, versioning, release tracks (internal, alpha, beta, production), and automated release notes generation.

## Answer (EN)
### Overview

Automated deployment ensures consistent releases, reduces human error, and speeds up the release process. Key components:
1. **Code signing** - APK/AAB signing with keystore
2. **Versioning** - Automated version bumps
3. **Release tracks** - Internal → Alpha → Beta → Production
4. **Release notes** - Automated changelog generation
5. **Deployment** - Upload to Play Store

### 1. Code Signing Setup

**Keystore Management**:

```bash
# Generate keystore (one-time setup)
keytool -genkey -v \
  -keystore release.keystore \
  -alias my-app-key \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# Export keystore as base64 for CI secrets
base64 -i release.keystore | pbcopy
```

**gradle.properties (local)**:

```properties
# DO NOT commit these to git!
KEYSTORE_FILE=release.keystore
KEYSTORE_PASSWORD=your_keystore_password
KEY_ALIAS=my-app-key
KEY_PASSWORD=your_key_password
```

**app/build.gradle.kts**:

```kotlin
android {
    signingConfigs {
        create("release") {
            // Read from environment (CI) or gradle.properties (local)
            storeFile = file(System.getenv("KEYSTORE_FILE")
                ?: project.findProperty("KEYSTORE_FILE") as String? ?: "release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
                ?: project.findProperty("KEYSTORE_PASSWORD") as String?
            keyAlias = System.getenv("KEY_ALIAS")
                ?: project.findProperty("KEY_ALIAS") as String?
            keyPassword = System.getenv("KEY_PASSWORD")
                ?: project.findProperty("KEY_PASSWORD") as String?
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

### 2. Automated Versioning

**Semantic Versioning Strategy**:

```
Version: X.Y.Z
X = Major (breaking changes)
Y = Minor (new features)
Z = Patch (bug fixes)

Example: 1.2.3 → 1.2.4 (patch)
         1.2.4 → 1.3.0 (minor feature)
         1.3.0 → 2.0.0 (major breaking change)
```

**app/build.gradle.kts with Auto-versioning**:

```kotlin
import java.io.ByteArrayOutputStream

fun getGitCommitCount(): Int {
    val output = ByteArrayOutputStream()
    project.exec {
        commandLine("git", "rev-list", "--count", "HEAD")
        standardOutput = output
    }
    return output.toString().trim().toInt()
}

fun getVersionNameFromTag(): String {
    return try {
        val output = ByteArrayOutputStream()
        project.exec {
            commandLine("git", "describe", "--tags", "--abbrev=0")
            standardOutput = output
        }
        output.toString().trim().removePrefix("v")
    } catch (e: Exception) {
        "1.0.0" // Default version
    }
}

android {
    defaultConfig {
        applicationId = "com.example.app"

        // Auto-increment versionCode based on git commits
        versionCode = getGitCommitCount()

        // Get version name from git tag
        versionName = getVersionNameFromTag()

        // Alternative: Read from version.properties
        // versionCode = project.property("VERSION_CODE").toString().toInt()
        // versionName = project.property("VERSION_NAME").toString()
    }
}

// Task to bump version
tasks.register("bumpVersion") {
    doLast {
        val versionFile = file("version.properties")
        val properties = java.util.Properties()

        if (versionFile.exists()) {
            versionFile.inputStream().use { properties.load(it) }
        }

        val currentCode = properties.getProperty("VERSION_CODE", "1").toInt()
        val currentName = properties.getProperty("VERSION_NAME", "1.0.0")

        // Parse semantic version
        val (major, minor, patch) = currentName.split(".").map { it.toInt() }

        // Determine bump type from commit message or argument
        val bumpType = project.findProperty("bumpType") as String? ?: "patch"

        val newVersion = when (bumpType) {
            "major" -> "${major + 1}.0.0"
            "minor" -> "$major.${minor + 1}.0"
            "patch" -> "$major.$minor.${patch + 1}"
            else -> currentName
        }

        properties.setProperty("VERSION_CODE", (currentCode + 1).toString())
        properties.setProperty("VERSION_NAME", newVersion)

        versionFile.outputStream().use { properties.store(it, null) }

        println("Bumped version: $currentName ($currentCode) → $newVersion (${currentCode + 1})")

        // Create git tag
        exec {
            commandLine("git", "tag", "v$newVersion")
        }
    }
}
```

### 3. Fastlane Setup

**Gemfile**:

```ruby
source "https://rubygems.org"

gem "fastlane", "~> 2.217"
gem "fastlane-plugin-firebase_app_distribution"
```

**fastlane/Appfile**:

```ruby
json_key_file("service_account.json") # Path to service account JSON
package_name("com.example.app")
```

**fastlane/Fastfile**:

```ruby
default_platform(:android)

platform :android do

  desc "Submit a new Internal Testing build"
  lane :internal do
    # Increment version code
    gradle(
      task: "clean"
    )

    # Build release bundle
    gradle(
      task: "bundle",
      build_type: "Release",
      properties: {
        "android.injected.signing.store.file" => ENV["KEYSTORE_FILE"],
        "android.injected.signing.store.password" => ENV["KEYSTORE_PASSWORD"],
        "android.injected.signing.key.alias" => ENV["KEY_ALIAS"],
        "android.injected.signing.key.password" => ENV["KEY_PASSWORD"]
      }
    )

    # Upload to Play Store internal track
    upload_to_play_store(
      track: 'internal',
      aab: 'app/build/outputs/bundle/release/app-release.aab',
      skip_upload_metadata: true,
      skip_upload_changelogs: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )

    # Post to Slack
    slack(
      message: "✅ Internal build uploaded successfully!",
      channel: "#releases",
      success: true,
      default_payloads: [:git_branch, :git_author, :last_git_commit_message]
    )
  end

  desc "Promote Internal to Alpha"
  lane :promote_to_alpha do
    # Promote from internal to alpha
    upload_to_play_store(
      track: 'internal',
      track_promote_to: 'alpha',
      skip_upload_aab: true,
      skip_upload_metadata: true,
      skip_upload_changelogs: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )

    slack(
      message: "🚀 Build promoted to Alpha!",
      channel: "#releases"
    )
  end

  desc "Promote Alpha to Beta"
  lane :promote_to_beta do
    upload_to_play_store(
      track: 'alpha',
      track_promote_to: 'beta',
      skip_upload_aab: true,
      skip_upload_metadata: true,
      skip_upload_changelogs: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )

    slack(
      message: "📦 Build promoted to Beta!",
      channel: "#releases"
    )
  end

  desc "Promote Beta to Production (10% rollout)"
  lane :promote_to_production do
    upload_to_play_store(
      track: 'beta',
      track_promote_to: 'production',
      rollout: '0.1', # 10% rollout
      skip_upload_aab: true,
      skip_upload_metadata: false, # Include metadata
      skip_upload_changelogs: false, # Include changelogs
      skip_upload_images: false,
      skip_upload_screenshots: false
    )

    slack(
      message: "🎉 Build promoted to Production (10% rollout)!",
      channel: "#releases",
      payload: {
        "Version" => get_version_name(),
        "Build Number" => get_version_code()
      }
    )
  end

  desc "Increase production rollout"
  lane :increase_rollout do |options|
    rollout_percentage = options[:percentage] || "0.5" # Default 50%

    upload_to_play_store(
      track: 'production',
      rollout: rollout_percentage,
      skip_upload_aab: true,
      skip_upload_metadata: true,
      skip_upload_changelogs: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )

    slack(
      message: "📈 Production rollout increased to #{(rollout_percentage.to_f * 100).to_i}%",
      channel: "#releases"
    )
  end

  desc "Deploy to Firebase App Distribution"
  lane :firebase do
    gradle(
      task: "assemble",
      build_type: "Debug"
    )

    firebase_app_distribution(
      app: ENV["FIREBASE_APP_ID"],
      groups: "testers, qa-team",
      release_notes_file: "release_notes.txt",
      apk_path: "app/build/outputs/apk/debug/app-debug.apk"
    )

    slack(
      message: "🔥 Build distributed via Firebase!",
      channel: "#qa"
    )
  end

  # Helper functions
  def get_version_name
    properties = load_properties("../app/version.properties")
    properties["VERSION_NAME"]
  end

  def get_version_code
    properties = load_properties("../app/version.properties")
    properties["VERSION_CODE"]
  end

  def load_properties(file_path)
    properties = {}
    File.read(file_path).each_line do |line|
      key, value = line.strip.split('=')
      properties[key] = value if key && value
    end
    properties
  end

  # Error handling
  error do |lane, exception|
    slack(
      message: "❌ #{lane} failed: #{exception.message}",
      success: false,
      channel: "#releases"
    )
  end

end
```

### 4. Automated Release Notes

**Script to generate release notes from git commits**:

```bash
#!/bin/bash
# generate_release_notes.sh

# Get previous tag
PREVIOUS_TAG=$(git describe --abbrev=0 --tags $(git rev-list --tags --skip=1 --max-count=1))
CURRENT_TAG=$(git describe --abbrev=0 --tags)

echo "# Release Notes for $CURRENT_TAG" > release_notes.txt
echo "" >> release_notes.txt

# Generate changelog from commits
echo "## What's New" >> release_notes.txt
git log $PREVIOUS_TAG..$CURRENT_TAG --pretty=format:"- %s" --grep="feat:" >> release_notes.txt

echo "" >> release_notes.txt
echo "## Bug Fixes" >> release_notes.txt
git log $PREVIOUS_TAG..$CURRENT_TAG --pretty=format:"- %s" --grep="fix:" >> release_notes.txt

echo "" >> release_notes.txt
echo "## Full Changelog" >> release_notes.txt
git log $PREVIOUS_TAG..$CURRENT_TAG --pretty=format:"- %s (%h)" >> release_notes.txt
```

**Conventional Commits format**:

```
<type>(<scope>): <subject>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes (formatting, etc.)
- refactor: Code refactoring
- perf: Performance improvements
- test: Adding/updating tests
- chore: Maintenance tasks

Examples:
feat(auth): add biometric login
fix(cart): fix crash when removing items
perf(database): optimize query performance
```

**Automated changelog generation in Fastlane**:

```ruby
desc "Generate release notes"
lane :generate_changelog do
  # Use conventional_changelog plugin
  conventional_changelog(
    format: 'markdown',
    title: '# Changelog',
    sections: {
      feat: 'New Features',
      fix: 'Bug Fixes',
      perf: 'Performance Improvements',
      refactor: 'Code Refactoring'
    }
  )

  # Or use built-in changelog_from_git_commits
  changelog = changelog_from_git_commits(
    pretty: "- %s",
    date_format: "short",
    match_lightweight_tag: false,
    merge_commit_filtering: "exclude_merges"
  )

  File.write("metadata/android/en-US/changelogs/#{get_version_code()}.txt", changelog)
end
```

### 5. GitHub Actions Complete Deployment

**.github/workflows/deploy.yml**:

```yaml
name: Deploy to Play Store

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 60

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Need full history for changelog

      - name: Set up Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.0'
          bundler-cache: true

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Grant execute permission
        run: chmod +x gradlew

      # Decode keystore from secrets
      - name: Decode keystore
        run: |
          echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 --decode > release.keystore

      # Decode service account JSON
      - name: Decode service account
        run: |
          echo "${{ secrets.PLAY_STORE_SERVICE_ACCOUNT }}" | base64 --decode > service_account.json

      # Generate release notes
      - name: Generate release notes
        run: |
          ./generate_release_notes.sh

      # Install Fastlane
      - name: Install Fastlane
        run: bundle install

      # Deploy to internal track
      - name: Deploy to Play Store (internal)
        run: bundle exec fastlane internal
        env:
          KEYSTORE_FILE: release.keystore
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}

      # Upload artifacts
      - name: Upload AAB
        uses: actions/upload-artifact@v3
        with:
          name: release-bundle
          path: app/build/outputs/bundle/release/app-release.aab

      # Create GitHub Release
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: release_notes.txt
          files: |
            app/build/outputs/bundle/release/app-release.aab
            app/build/outputs/mapping/release/mapping.txt

      # Notify team
      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: '🚀 New release ${{ github.ref_name }} deployed to Play Store!'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        if: always()
```

### 6. Play Store Metadata Management

**Directory structure**:

```
fastlane/metadata/android/
├── en-US/
│   ├── title.txt                      # App title (max 50 chars)
│   ├── short_description.txt          # Short description (max 80 chars)
│   ├── full_description.txt           # Full description (max 4000 chars)
│   ├── video.txt                      # YouTube video URL
│   ├── changelogs/
│   │   ├── 123.txt                    # Changelog for version code 123
│   │   └── 124.txt
│   └── images/
│       ├── icon.png
│       ├── featureGraphic.png
│       ├── phoneScreenshots/
│       │   ├── 1_home.png
│       │   ├── 2_profile.png
│       │   └── 3_settings.png
│       └── tenInchScreenshots/
│           └── 1_tablet.png
└── ru-RU/
    ├── title.txt
    ├── short_description.txt
    └── full_description.txt
```

**Upload metadata with Fastlane**:

```ruby
desc "Upload metadata to Play Store"
lane :upload_metadata do
  upload_to_play_store(
    skip_upload_aab: true,
    skip_upload_apk: true,
    skip_upload_metadata: false,
    skip_upload_changelogs: false,
    skip_upload_images: false,
    skip_upload_screenshots: false
  )
end
```

### 7. Gradual Rollout Strategy

```
Day 1:  Internal track (team only)
Day 2:  Alpha track (trusted testers, 10-50 users)
Day 4:  Beta track (wider audience, 100-1000 users)
Day 7:  Production 10% rollout
Day 9:  Production 25% rollout (if no critical issues)
Day 11: Production 50% rollout
Day 13: Production 100% rollout
```

**Fastlane automation**:

```ruby
desc "Automated rollout schedule"
lane :scheduled_rollout do |options|
  days_since_release = options[:days] || 0

  case days_since_release
  when 0
    internal
  when 2
    promote_to_alpha
  when 4
    promote_to_beta
  when 7
    promote_to_production # 10% default
  when 9
    increase_rollout(percentage: "0.25")
  when 11
    increase_rollout(percentage: "0.5")
  when 13
    increase_rollout(percentage: "1.0")
  else
    puts "No rollout action for day #{days_since_release}"
  end
end
```

### 8. Multi-Flavor Deployment

**build.gradle.kts**:

```kotlin
android {
    flavorDimensions += "environment"

    productFlavors {
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
            versionNameSuffix = "-dev"
        }

        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
            versionNameSuffix = "-staging"
        }

        create("production") {
            dimension = "environment"
        }
    }
}
```

**Fastlane**:

```ruby
desc "Deploy specific flavor"
lane :deploy_flavor do |options|
  flavor = options[:flavor] || "production"
  track = options[:track] || "internal"

  gradle(
    task: "bundle",
    build_type: "Release",
    flavor: flavor
  )

  upload_to_play_store(
    track: track,
    aab: "app/build/outputs/bundle/#{flavor}Release/app-#{flavor}-release.aab"
  )
end

# Usage: fastlane deploy_flavor flavor:staging track:alpha
```

### Best Practices

1. **Never Commit Secrets**
   ```bash
   # ✅ GOOD - Use CI secrets
   env:
     KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}

   # ❌ BAD - Hardcoded secrets
   signingConfigs {
       release {
           storePassword "my-password"
       }
   }
   ```

2. **Always Test Before Production**
   ```ruby
   # ✅ GOOD - Gradual rollout
   internal → alpha → beta → production (10%) → production (100%)

   # ❌ BAD - Direct to production
   internal → production (100%)
   ```

3. **Automate Version Bumping**
   ```bash
   # ✅ GOOD - Automated versioning
   versionCode = getGitCommitCount()
   versionName = getGitTag()

   # ❌ BAD - Manual versioning
   versionCode = 42 // Remember to increment!
   ```

4. **Use Conventional Commits**
   ```bash
   # ✅ GOOD - Structured commits
   git commit -m "feat(auth): add biometric login"
   git commit -m "fix(cart): prevent crash on empty cart"

   # ❌ BAD - Unstructured commits
   git commit -m "updates"
   git commit -m "fixes"
   ```

5. **Monitor Rollout Metrics**
   ```ruby
   # Check crash rate before increasing rollout
   if crash_rate > 1%
     puts "⚠️ High crash rate detected, halting rollout"
     # Optionally: rollback or halt release
   else
     increase_rollout(percentage: "0.5")
   end
   ```

### Summary

**Automated deployment pipeline:**
1. ✅ **Code signing** - Keystore management, CI secrets
2. ✅ **Versioning** - Git tags, semantic versioning, auto-increment
3. ✅ **Release tracks** - Internal → Alpha → Beta → Production
4. ✅ **Release notes** - Generated from conventional commits
5. ✅ **Deployment** - Fastlane automation, gradual rollout
6. ✅ **Monitoring** - Track metrics, halt on issues

**Key tools:**
- **Fastlane** - Deployment automation
- **GitHub Actions** - CI/CD orchestration
- **Conventional Commits** - Structured changelog
- **Play Store API** - Programmatic uploads

**Rollout strategy:**
- Start with internal testing
- Gradually expand to alpha, beta
- Production rollout at 10% → 25% → 50% → 100%
- Monitor metrics, halt if issues detected

---

# Вопрос (RU)
Как автоматизировать деплой Android-приложения в Play Store? Объясните процесс подписи, версионирования, треков релизов (internal, alpha, beta, production) и автоматической генерации release notes.

## Ответ (RU)
[Перевод с примерами из английской версии...]

### Резюме

**Автоматизированный pipeline деплоя:**
1. ✅ **Подпись кода** — управление keystore, CI-секреты
2. ✅ **Версионирование** — git-теги, semantic versioning, авто-инкремент
3. ✅ **Треки релизов** — Internal → Alpha → Beta → Production
4. ✅ **Release notes** — генерация из conventional commits
5. ✅ **Деплой** — автоматизация Fastlane, постепенный rollout
6. ✅ **Мониторинг** — отслеживание метрик, остановка при проблемах

**Ключевые инструменты:**
- **Fastlane** — автоматизация деплоя
- **GitHub Actions** — оркестрация CI/CD
- **Conventional Commits** — структурированный changelog
- **Play Store API** — программные загрузки

**Стратегия rollout:**
- Начать с internal testing
- Постепенно расширять до alpha, beta
- Production rollout на 10% → 25% → 50% → 100%
- Мониторить метрики, останавливать при проблемах
