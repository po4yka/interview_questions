---
id: 20251012-122750
title: 16kb Dex Page Size / Размер страницы DEX 16KB
aliases:
- 16KB DEX Page Size
- 16 КБ страница DEX
topic: android
subtopics:
- gradle
- performance-memory
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-background-tasks-decision-guide--android--medium
- q-why-fragment-needs-separate-callback-for-ui-creation--android--hard
- q-what-are-fragments-and-why-are-they-more-convenient-to-use-instead-of-multiple-activities--android--hard
created: 2025-10-15
updated: 2025-10-15
tags:
- android/gradle
- android/performance-memory
- difficulty/medium
---

## Answer (EN)
The 16 KB DEX page size issue is a [[c-memory-alignment|memory alignment]] problem affecting Android 6.0+ that causes significant app bloat when apps are optimized with [[c-r8-proguard|R8/ProGuard]]. This affects [[c-gradle|Gradle]] builds and [[c-apk|APK]] sizes.

#### Problem

Android uses 16 KB pages for DEX files. Method IDs must be page-aligned, creating wasted padding space.

```
Without alignment: [Header][Strings][Methods][Code]
With alignment:    [Header][Strings][Padding][Methods][Code]
                                    ^^^^^^^^ Wasted space
```

Impact:
- Small apps (< 5 MB): 20-40% size increase
- Large apps (> 50 MB): 5-15% size increase
- Multi-DEX apps: Multiplied impact

#### Detection

APK Analyzer:
- Tools → APK Analyzer → Select APK
- Check classes.dex size
- Look for unusual growth in optimized builds

Command line:
```bash
unzip app-release.apk
ls -lh *.dex
dexdump -f classes.dex > dex_dump.txt
```

#### Solutions

Upgrade to latest AGP:
```kotlin
plugins {
    id("com.android.application") apply false
}
```

Manual R8 configuration (older AGP):
```properties
android.enableR8.fullMode=true
```

Use App Bundle for automatic optimization.

#### Best Practices

Enable R8 optimization:
```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
        }
    }
}
```

Monitor APK size in CI/CD. Use App Bundle instead of APK.

---

## Follow-ups

- What happens if you use AGP versions older than 8.2?
- How does this issue affect Instant Apps?
- What's the difference between R8 and ProGuard in handling this issue?
- How do App Bundles mitigate the 16KB page size problem?
- What tools can help detect alignment issues in CI/CD?

## References

- [Android Developer Guide: Configure your build](https://developer.android.com/studio/build)
- [R8 Optimization Guide](https://developer.android.com/studio/build/shrink-code)
- [Android App Bundle](https://developer.android.com/guide/app-bundle)
- [APK Analyzer Documentation](https://developer.android.com/studio/build/analyze-apk)

## Related Questions

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]] - Build

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - Build
- [[q-android-build-optimization--android--medium]] - Build
- [[q-proguard-r8--android--medium]] - Build
- [[q-build-optimization-gradle--android--medium]] - Build
- [[q-kapt-ksp-migration--gradle--medium]] - Build

### Advanced (Harder)
- [[q-kotlin-dsl-builders--kotlin--hard]] - Build