---
id: android-265
anki_cards:
  - slug: android-265-0-en
    front: "Why do multi-module Android projects have multiple AndroidManifest files?"
    back: |
      **Reasons:**
      1. **Modular independence** - each module declares its own components/permissions
      2. **Component encapsulation** - Activities/Services scoped to module
      3. **Automatic merging** - Gradle combines all into final manifest

      **Priority:** app > feature modules > libraries

      **Conflict resolution:**
      ```xml
      tools:replace="android:screenOrientation"
      tools:node="remove"
      ```

      **Key:** Use `${applicationId}` for authorities, check Merged Manifest tab.
    tags:
      - android_architecture
      - difficulty::medium
  - slug: android-265-0-ru
    front: "Зачем в мультимодульных Android проектах несколько AndroidManifest файлов?"
    back: |
      **Причины:**
      1. **Модульная независимость** - модуль объявляет свои компоненты/permissions
      2. **Инкапсуляция компонентов** - Activity/Service привязаны к модулю
      3. **Автослияние** - Gradle объединяет в итоговый манифест

      **Приоритет:** app > feature modules > libraries

      **Разрешение конфликтов:**
      ```xml
      tools:replace="android:screenOrientation"
      tools:node="remove"
      ```

      **Ключ:** Используйте `${applicationId}` для authorities, проверяйте Merged Manifest.
    tags:
      - android_architecture
      - difficulty::medium
title: "Multiple Manifests Multimodule / Множественные манифесты в мультимодульных проектах"
aliases: ["Android Manifest Merging", "Multiple Manifests Multimodule", "Множественные манифесты в мультимодульных проектах", "Слияние манифестов Android"]
topic: android
subtopics: [architecture-modularization, dependency-management, gradle]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-gradle, q-android-manifest-file--android--easy, q-android-modularization--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/architecture-modularization, android/dependency-management, android/gradle, difficulty/medium, manifest-merging, modularization]
sources: ["https://developer.android.com/build/manage-manifests", "https://developer.android.com/studio/build/manifest-merge"]

---\
# Вопрос (RU)

> Для проектов в которых есть несколько модулей, там может быть много Android Manifest'ов, для чего это делается?

# Question (EN)

> In multi-module projects, there can be many AndroidManifest files. Why is this done?

---

## Ответ (RU)

В многомодульных проектах каждый модуль имеет свой **AndroidManifest.xml** для:

1. **Модульной независимости** - модуль описывает свои компоненты, permissions, intent-filter'ы и требования к среде, не засоряя основной манифест
2. **Инкапсуляции компонентов** - `Activity`/`Service`/Provider локализованы в модуле и явно декларируются там
3. **Автоматического слияния** - build-система (Gradle + manifest merger) объединяет все манифесты в один итоговый

### Принцип Работы

```text
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
    <!-- ✅ Модуль сам объявляет свои требования к платформе -->
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
- Удалили модуль → автоматически удалились его permissions и компоненты из итогового манифеста
- Модуль проще переносить между проектами (минимум правок)
- Ясно, какому модулю нужны какие разрешения и компоненты

### Приоритет Слияния

**app** > **feature modules** > **libraries**

```xml
<!-- feature-login/AndroidManifest.xml -->
<activity android:screenOrientation="portrait" />

<!-- app/AndroidManifest.xml -->
<activity android:screenOrientation="landscape" />  ← Побеждает app
```

### Разрешение Конфликтов

```xml
<manifest xmlns:tools="http://schemas.android.com/tools">
    <activity
        android:name=".LoginActivity"
        tools:replace="android:screenOrientation" />  <!-- Заменить атрибут при конфликте -->
</manifest>
```

**Merge tools (основные):**
- `tools:node="merge"` - поведение слияния по умолчанию (явно указывать обычно не нужно)
- `tools:node="replace"` - заменить узел целиком
- `tools:node="remove"` - удалить узел из итогового манифеста
- `tools:replace="attr"` - заменить конкретный атрибут при конфликте значений

### Best Practices

✅ **DO:**
- Держать app-манифест минимальным: `application`, launcher activity, high-level настройки
- Пусть feature-модули будут самодостаточными: объявляют свои компоненты, permissions, intent-filter'ы
- В library-модулях обычно не определять свой `<application>`, если нет специфической причины

❌ **DON'T:**
- Специально дублировать permissions в app-манифесте, если они уже объявлены в модулях (manifest merger подтянет их автоматически; дубли не ломают сборку, но засоряют файл)
- Хардкодить `android:authorities` (используй `${applicationId}` для уникальности в разных сборках)
- Игнорировать merge conflicts (проверяй вкладку Merged Manifest и логи manifest merger)

### Просмотр Результата

**Android Studio:** `app/AndroidManifest.xml` → вкладка **Merged Manifest**

**CLI:**
```bash
./gradlew :app:processDebugManifest
cat app/build/intermediates/merged_manifests/debug/AndroidManifest.xml
```

---

## Answer (EN)

In multi-module projects, each module has its own **AndroidManifest.xml** for:

1. **Modular independence** - the module describes its own components, permissions, intent filters, and requirements without polluting the main manifest
2. **`Component` encapsulation** - Activities/Services/Providers are declared in and scoped to the module that owns them
3. **Automatic merging** - the build system (Gradle + manifest merger) combines all manifests into a single final manifest

### How it Works

```text
project/
 app/src/main/AndroidManifest.xml          ← Main manifest
 feature-login/src/main/AndroidManifest.xml
 feature-camera/src/main/AndroidManifest.xml
 core-network/src/main/AndroidManifest.xml
                       ↓ Gradle Merge Task
 app/build/intermediates/merged_manifests/debug/AndroidManifest.xml
```

### Example: Camera Feature Module

```xml
<!-- feature-camera/src/main/AndroidManifest.xml -->
<manifest package="com.example.feature.camera">
    <!-- ✅ Module declares its own platform requirements -->
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
- Removing a module → its permissions and components are automatically removed from the final merged manifest
- `Module` is easier to move between projects (minimal changes needed)
- Clear ownership of permissions/components per module

### Merge Priority

**app** > **feature modules** > **libraries**

```xml
<!-- feature-login/AndroidManifest.xml -->
<activity android:screenOrientation="portrait" />

<!-- app/AndroidManifest.xml -->
<activity android:screenOrientation="landscape" />  ← app wins
```

### Conflict Resolution

```xml
<manifest xmlns:tools="http://schemas.android.com/tools">
    <activity
        android:name=".LoginActivity"
        tools:replace="android:screenOrientation" />  <!-- Replace attribute on conflict -->
</manifest>
```

**Merge tools (key ones):**
- `tools:node="merge"` - default merge behavior (usually implicit)
- `tools:node="replace"` - replace entire node
- `tools:node="remove"` - remove node from final manifest
- `tools:replace="attr"` - replace specific attribute value on conflict

### Best Practices

✅ **DO:**
- Keep the app manifest minimal: `application`, launcher activity, high-level configuration
- Make feature modules self-contained: declare their own components, permissions, intent filters
- In library modules, usually avoid defining a dedicated `<application>` unless there is a strong reason

❌ **DON'T:**
- Intentionally duplicate permissions in the app manifest if already declared in modules (manifest merger will bring them into the final manifest; duplicates are allowed but add noise)
- Hardcode `android:authorities` (use `${applicationId}` to keep authorities unique across variants)
- Ignore merge conflicts (review the Merged Manifest tab and manifest merger logs)

### `View` Merged Result

**Android Studio:** `app/AndroidManifest.xml` → **Merged Manifest** tab

**CLI:**
```bash
./gradlew :app:processDebugManifest
cat app/build/intermediates/merged_manifests/debug/AndroidManifest.xml
```

---

## Дополнительные Вопросы (RU)

1. Как в Android Studio анализировать и отлаживать конфликты слияния манифестов (Merged Manifest, логи manifest merger)?
2. Что произойдет, если два модуля объявят одно и то же разрешение с разными атрибутами или protectionLevel?
3. Чем `tools:node="removeAll"` отличается от `tools:node="remove"` при работе с потомками элементов?
4. Могут ли library/feature-модули переопределять атрибуты, определенные в app-манифесте, и в каких случаях это сработает?
5. Как исключить или переопределить конкретные элементы манифеста, приходящие из зависимостей (AAR-библиотек)?

## Follow-ups

1. How can you inspect and debug manifest merge issues in Android Studio (Merged Manifest view, merger logs)?
2. What happens if two modules declare the same permission with different attributes or protection levels?
3. How does `tools:node="removeAll"` differ from `tools:node="remove"` when working with child elements?
4. Can library/feature modules override attributes defined in the app manifest, and in which scenarios will this apply?
5. How can you exclude or override specific manifest entries coming from dependency AARs?

## Ссылки (RU)

- [[c-gradle]]
- [Управление несколькими файлами манифеста](https://developer.android.com/build/manage-manifests)
- [Инструмент слияния манифестов](https://developer.android.com/studio/build/manifest-merge)

## References

- [[c-gradle]]
- [Merge multiple manifest files](https://developer.android.com/build/manage-manifests)
- [Manifest merge tool](https://developer.android.com/studio/build/manifest-merge)

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-android-manifest-file--android--easy]] - Основы файла манифеста
- [[q-android-project-parts--android--easy]] - Структура Android-проекта

### Связанные (такой Же уровень)
- [[q-android-modularization--android--medium]] - Стратегии модульности

### Продвинутые (сложнее)
- [[q-android-release-pipeline-cicd--android--hard]] - CI/CD и релизный пайплайн для мультимодульных проектов

## Related Questions

### Prerequisites (Easier)
- [[q-android-manifest-file--android--easy]] - Manifest file basics
- [[q-android-project-parts--android--easy]] - Android project structure

### Related (Same Level)
- [[q-android-modularization--android--medium]] - Modularization strategies

### Advanced (Harder)
- [[q-android-release-pipeline-cicd--android--hard]] - CI/CD for multi-module setups
