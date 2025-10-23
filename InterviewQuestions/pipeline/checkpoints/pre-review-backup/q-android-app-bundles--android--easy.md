---
id: 20251005-143000
title: Android App Bundles / Android App Bundle (AAB)
aliases:
- Android App Bundles
- Android App Bundle
- AAB
topic: android
subtopics:
- app-bundle
- play-console
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-play-store-publishing--distribution--medium
- q-gradle-basics--android--easy
- q-play-feature-delivery--android--medium
created: 2025-10-05
updated: 2025-10-15
tags:
- android/app-bundle
- android/play-console
- difficulty/easy
source: https://github.com/Kirchhoff-/Android-Interview-Questions
---

## Answer (EN)
[[c-app-bundle|Android App Bundle]] (AAB) is a publishing format that includes compiled code and resources, with [[c-apk-generation|APK generation]] deferred to Google Play. [[c-app-distribution|App distribution]] is optimized through dynamic delivery.

**Key Benefits:**

- **Smaller downloads**: Only device-specific code and resources downloaded
- **Dynamic delivery**: Features can be downloaded on-demand
- **150MB limit**: Increased from 100MB for compressed downloads
- **Google signing**: Automatic APK signing by Google Play

**AAB vs APK:**

| Feature | APK | AAB |
|---------|-----|-----|
| Installation | Direct install | Must be processed to APK |
| Size optimization | No | Yes |
| Dynamic delivery | No | Yes |
| Signing | Developer or Google | Google only |

**Bundle Configuration:**

```kotlin
// build.gradle.kts
android {
    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}
```

**Testing AABs Locally:**

```bash
# Generate universal APK for testing
bundletool build-apks --bundle=app-release.aab --output=app.apks --mode=universal

# Install on device
bundletool install-apks --apks=app.apks
```

**Modern Dependencies:**

```kotlin
// Feature delivery (Play Core is deprecated)
implementation("com.google.android.play:feature-delivery:2.1.0")
implementation("com.google.android.play:feature-delivery-ktx:2.1.0")

// Asset delivery
implementation("com.google.android.play:asset-delivery:2.2.0")
implementation("com.google.android.play:asset-delivery-ktx:2.2.0")
```

**Requirements:**

- **Mandatory**: AAB required for new apps since August 2021
- **APK support**: Only for existing apps and testing tracks
- **Asset packs**: Don't count toward 150MB limit
- **Feature modules**: Optional, downloaded on-demand

## Follow-ups

- How do you test AABs on different device configurations?
- What are the differences between feature modules and asset packs?
- How do you migrate from APK to AAB format?
- What are the limitations of dynamic delivery?
- How do you handle AAB signing and security?

## References

- [Android App Bundle Guide](https://developer.android.com/guide/app-bundle)
- [Play Feature Delivery](https://developer.android.com/guide/playcore/feature-delivery)
- [BundleTool Documentation](https://developer.android.com/studio/command-line/bundletool)

## Related Questions

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]] - Gradle build system
- [[q-android-app-components--android--easy]] - App components

### Related (Medium)
- [[q-play-feature-delivery--android--medium]] - Feature delivery
- [[q-what-is-intent--android--easy]] - Intent system