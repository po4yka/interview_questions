---
id: android-265
title: "Multiple Manifests Multimodule / Множественные манифесты в мультимодульных проектах"
aliases: [
  "Multiple Manifests Multimodule",
  "Множественные манифесты в мультимодульных проектах",
  "Android Manifest Merging",
  "Слияние манифестов Android"
]
topic: android
subtopics: [architecture-modularization, gradle, dependency-management]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [ru, en]
status: draft
moc: moc-android
related: [c-gradle, c-android-manifest, q-gradle-optimization--android--medium, q-dependency-injection-hilt--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android/architecture-modularization, android/gradle, android/dependency-management, manifest-merging, modularization, difficulty/medium]
sources: [
  "https://developer.android.com/build/manage-manifests",
  "https://developer.android.com/studio/build/manifest-merge"
]
---

# Вопрос (RU)

> Для проектов в которых есть несколько модулей, там может быть много Android Manifest'ов, для чего это делается?

# Question (EN)

> In multi-module projects, there can be many AndroidManifest files. Why is this done?

---

## Ответ (RU)

В многомодульных проектах каждый модуль имеет свой **AndroidManifest.xml** для:

1. **Модульной независимости** - модуль объявляет только свои зависимости
2. **Инкапсуляции компонентов** - Activity/Service/Provider локализованы в модуле
3. **Автоматического слияния** - build система объединяет все манифесты в один

### Принцип работы

```
project/
 app/src/main/AndroidManifest.xml          ← Главный манифест
 feature-login/src/main/AndroidManifest.xml
 feature-camera/src/main/AndroidManifest.xml
 core-network/src/main/AndroidManifest.xml
                       ↓ Gradle Merge Task
 app/build/intermediates/merged_manifests/debug/AndroidManifest.xml
```

### Пример: Feature-модуль Camera

```xml
<!-- feature-camera/src/main/AndroidManifest.xml -->
<manifest package="com.example.feature.camera">
    <!-- ✅ Модуль сам объявляет свои зависимости -->
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-feature android:name="android.hardware.camera" />

    <application>
        <activity android:name=".CameraActivity" />
        <provider
            android:name=".CameraFileProvider"
            android:authorities="${applicationId}.camera.provider" />
    </application>
</manifest>
```

**Преимущества:**
- Удалили модуль → автоматически удалились permissions и компоненты
- Модуль переносится между проектами без изменений
- Ясно, какому модулю нужны какие разрешения

### Приоритет слияния

**app** > **feature modules** > **libraries**

```xml
<!-- feature-login/AndroidManifest.xml -->
<activity android:screenOrientation="portrait" />

<!-- app/AndroidManifest.xml -->
<activity android:screenOrientation="landscape" />  ← Побеждает app
```

### Разрешение конфликтов

```xml
<manifest xmlns:tools="http://schemas.android.com/tools">
    <activity
        android:name=".LoginActivity"
        tools:replace="android:screenOrientation" />  <!-- Заменить атрибут -->
</manifest>
```

**Merge tools:**
- `tools:node="merge"` - слияние (по умолчанию)
- `tools:node="replace"` - замена узла целиком
- `tools:node="remove"` - удаление узла
- `tools:replace="attr"` - замена конкретного атрибута

### Best practices

✅ **DO:**
- App манифест минимален - только launcher activity и Application
- Feature-модули самодостаточны - объявляют всё необходимое
- Library-модули без `<application>` - только permissions

❌ **DON'T:**
- Дублировать permissions в app манифесте (они придут из модулей)
- Хардкодить `android:authorities` (используй `${applicationId}`)
- Игнорировать merge conflicts (проверяй Merged Manifest tab)

### Просмотр результата

**Android Studio:** `app/AndroidManifest.xml` → вкладка **Merged Manifest**

**CLI:**
```bash
./gradlew :app:processDebugManifest
cat app/build/intermediates/merged_manifests/debug/AndroidManifest.xml
```

---

## Answer (EN)

In multi-module projects, each module has its own **AndroidManifest.xml** for:

1. **Modular independence** - module declares only its own dependencies
2. **Component encapsulation** - Activity/Service/Provider scoped to module
3. **Automatic merging** - build system merges all manifests into one

### How it works

```
project/
 app/src/main/AndroidManifest.xml          ← Main manifest
 feature-login/src/main/AndroidManifest.xml
 feature-camera/src/main/AndroidManifest.xml
 core-network/src/main/AndroidManifest.xml
                       ↓ Gradle Merge Task
 app/build/intermediates/merged_manifests/debug/AndroidManifest.xml
```

### Example: Camera feature module

```xml
<!-- feature-camera/src/main/AndroidManifest.xml -->
<manifest package="com.example.feature.camera">
    <!-- ✅ Module declares its own dependencies -->
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-feature android:name="android.hardware.camera" />

    <application>
        <activity android:name=".CameraActivity" />
        <provider
            android:name=".CameraFileProvider"
            android:authorities="${applicationId}.camera.provider" />
    </application>
</manifest>
```

**Benefits:**
- Remove module → permissions and components auto-removed
- Module portable between projects without changes
- Clear ownership of permissions per module

### Merge priority

**app** > **feature modules** > **libraries**

```xml
<!-- feature-login/AndroidManifest.xml -->
<activity android:screenOrientation="portrait" />

<!-- app/AndroidManifest.xml -->
<activity android:screenOrientation="landscape" />  ← app wins
```

### Conflict resolution

```xml
<manifest xmlns:tools="http://schemas.android.com/tools">
    <activity
        android:name=".LoginActivity"
        tools:replace="android:screenOrientation" />  <!-- Replace attribute -->
</manifest>
```

**Merge tools:**
- `tools:node="merge"` - merge nodes (default)
- `tools:node="replace"` - replace entire node
- `tools:node="remove"` - remove node
- `tools:replace="attr"` - replace specific attribute

### Best practices

✅ **DO:**
- Keep app manifest minimal - only launcher activity and Application
- Make feature modules self-contained - declare everything needed
- Library modules without `<application>` - only permissions

❌ **DON'T:**
- Duplicate permissions in app manifest (they come from modules)
- Hardcode `android:authorities` (use `${applicationId}`)
- Ignore merge conflicts (check Merged Manifest tab)

### View merged result

**Android Studio:** `app/AndroidManifest.xml` → **Merged Manifest** tab

**CLI:**
```bash
./gradlew :app:processDebugManifest
cat app/build/intermediates/merged_manifests/debug/AndroidManifest.xml
```

---

## Follow-ups

1. How to debug manifest merge conflicts in Android Studio?
2. What happens when two modules declare the same permission with different protection levels?
3. How does `tools:node="removeAll"` differ from `tools:node="remove"`?
4. Can library modules override attributes in the app manifest?
5. How to exclude specific manifest entries from a dependency module?

## References

- [[c-gradle]]
- [[c-android-manifest]]
- [[c-modularization]]
- [Merge multiple manifest files](https://developer.android.com/build/manage-manifests)
- [Manifest merge tool](https://developer.android.com/studio/build/manifest-merge)

## Related Questions

### Prerequisites (Easier)
- [[q-what-unifies-android-components--android--easy]]
- [[q-android-jetpack-overview--android--easy]]

### Related (Same Level)
- [[q-gradle-optimization--android--medium]]
- [[q-dependency-injection-hilt--android--medium]]
- [[q-intent-filters-android--android--medium]]

### Advanced (Harder)
- [[q-kmm-architecture--multiplatform--hard]]
- [[q-how-application-priority-is-determined-by-the-system--android--hard]]
