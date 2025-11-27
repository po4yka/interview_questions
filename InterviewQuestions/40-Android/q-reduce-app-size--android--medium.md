---
id: android-004
title: Ways to Reduce Android App Size / Способы уменьшения размера Android приложения
aliases: [Ways to Reduce Android App Size, Способы уменьшения размера Android приложения]
topic: android
subtopics:
  - app-bundle
  - build-variants
  - performance-memory
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
source: "https://github.com/Kirchhoff-Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository
status: draft
moc: moc-android
related:
  - c-app-bundle
  - c-gradle
  - c-memory-management
  - q-app-size-optimization--android--medium
  - q-app-start-types-android--android--medium
  - q-how-to-catch-the-earliest-entry-point-into-the-application--android--medium
  - q-memory-leak-vs-oom-android--android--medium
  - q-reduce-apk-size-techniques--android--medium
created: 2025-10-05
updated: 2025-11-11
tags: [android/app-bundle, android/build-variants, android/performance-memory, difficulty/medium, en, ru]


date created: Saturday, November 1st 2025, 12:47:02 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---
# Вопрос (RU)
> Какие способы уменьшения размера приложения вы знаете?

# Question (EN)
> What ways do you know to reduce the size of an application?

---

## Ответ (RU)

Небольшой размер приложения напрямую связан с успешностью установки, особенно на развивающихся рынках с плохими сетевыми подключениями или низкой скоростью сети. Большие загрузки могут приводить к снижению количества установок и использования, что уменьшает охват вашей аудитории.

Основные способы уменьшения размера приложения:
- Загрузка приложения в формате Android App `Bundle`
- Уменьшение количества и размера ресурсов
- Уменьшение объёма нативного и Java/Kotlin-кода
- Переоценка функциональности и переводов

### Загрузка Приложения В Формате Android App `Bundle`

Загрузите приложение как Android App `Bundle` (AAB), чтобы снизить размер загрузки и установки при публикации в Google Play. Android App `Bundle` — это формат загрузки, который включает весь скомпилированный код и ресурсы приложения, но передаёт генерацию и подписание APK на сторону Google Play.

Модель доставки Google Play использует ваш app bundle для генерации и распространения оптимизированных APK под конфигурацию конкретного устройства, чтобы пользователь загружал только необходимый для работы код и ресурсы. Вам не нужно создавать, подписывать и обслуживать несколько APK для разных устройств, а пользователи получают меньшие и более оптимизированные загрузки.

### Уменьшение Количества И Размера Ресурсов

Размер пакета приложения влияет на скорость запуска, потребление памяти и энергии. Вы можете уменьшить размер, сократив количество и объём ресурсов. В частности, удалите ресурсы, которые больше не используются, и при возможности используйте масштабируемые объекты `Drawable` вместо растровых изображений.

#### Удаление Неиспользуемых Ресурсов

Инструмент `lint` — статический анализатор кода, включённый в Android Studio — обнаруживает ресурсы в папке `res/`, на которые не ссылается ваш код. Когда `lint` находит потенциально неиспользуемый ресурс, он выдаёт сообщение, подобное следующему:

```text
res/layout/preferences.xml: Warning: The resource R.layout.preferences appears
    to be unused [UnusedResources]
```

Библиотеки, которые вы добавляете в проект, могут содержать неиспользуемые ресурсы. Gradle может автоматически удалить их, если включить `shrinkResources` в файле `build.gradle.kts` вашего приложения:

```kotlin
android {
    // Другие настройки.

    buildTypes {
        getByName("release") {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

Для использования `shrinkResources` необходимо включить уменьшение кода. Во время сборки R8 сначала удаляет неиспользуемый код, затем плагин Android Gradle удаляет неиспользуемые ресурсы.

#### Поддержка Только Нужных Плотностей Экрана

Android поддерживает различные плотности экрана:
- `ldpi`
- `mdpi`
- `tvdpi`
- `hdpi`
- `xhdpi`
- `xxhdpi`
- `xxxhdpi`

Хотя перечисленные плотности поддерживаются, вам не обязательно иметь растровые ассеты для каждой из них.

Если вы знаете, что лишь небольшой процент пользователей использует устройства с определёнными плотностями, подумайте, нужно ли включать соответствующие ресурсы. Если ресурсы для конкретной плотности отсутствуют, Android автоматически масштабирует существующие ресурсы, изначально подготовленные для других плотностей.

Если вашему приложению достаточно масштабируемых изображений, вы можете ещё больше сэкономить место, имея один вариант изображения в `drawable-nodpi/`. Обычно рекомендуется включать как минимум вариант `xxhdpi`.

#### Использование Объектов Drawable

Некоторые элементы интерфейса не требуют статического растрового изображения. Фреймворк может нарисовать их динамически во время выполнения. Объекты `Drawable` (в том числе `<shape>` в XML) занимают очень мало места в APK. XML-ресурсы особенно подходят для простых монохромных фигур и хорошо сочетаются с рекомендациями Material Design.

#### Повторное Использование Ресурсов

Вместо создания отдельных ресурсов для каждой вариации изображения (тонированной, затемнённой, повернутой и т.п.) лучше переиспользовать базовый ресурс и настраивать его во время выполнения.

Android предоставляет несколько способов изменить цвет ассета, например, с помощью атрибутов `android:tint` и `tintMode`.

Можно также не добавлять ресурсы, которые являются лишь повернутым вариантом другого. В следующем примере показано превращение иконки «палец вверх» в «палец вниз» путём поворота изображения на 180 градусов относительно центра:

```xml
<?xml version="1.0" encoding="utf-8"?>
<rotate xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/ic_thumb_up"
    android:pivotX="50%"
    android:pivotY="50%"
    android:fromDegrees="180" />
```

#### Сжатие Файлов PNG И JPEG

Размер PNG можно уменьшить без потери визуального качества с помощью инструментов [pngcrush](https://pmt.sourceforge.io/pngcrush/), [pngquant](https://pngquant.org/), [zopflipng](https://github.com/google/zopfli) и других. Эти инструменты снижают размер файла при сохранении воспринимаемого качества изображения.

Инструмент `pngcrush` перебирает различные фильтры PNG и параметры zlib (Deflate), используя разные комбинации для сжатия изображения, и выбирает вариант с наименьшим размером.

Для сжатия JPEG можно использовать, например, [packJPG](https://github.com/packjpg/packJPG) и [guetzli](https://github.com/google/guetzli).

#### Использование Формата WebP

Вместо PNG или JPEG вы можете использовать формат [WebP](https://developers.google.com/speed/webp). WebP поддерживает сжатие с потерями, прозрачность и зачастую обеспечивает лучшее сжатие по сравнению с JPEG и PNG.

Существующие BMP, JPG, PNG и статические GIF можно конвертировать в WebP с помощью Android Studio. Подробнее см. [Create WebP images](https://developer.android.com/studio/write/convert-webp).

#### Использование Загружаемых Шрифтов

Поскольку многие приложения в Play Store используют одинаковые шрифты, их встраивание в каждый APK приводит к дублированию данных на устройстве. Загружаемые шрифты позволяют приложениям запрашивать шрифт из общего провайдера вместо встраивания файлов, что уменьшает размер APK/AAB и избегает дублей на устройстве.

### Уменьшение Объёма Нативного И Java/Kotlin-кода

Для уменьшения размера Java/Kotlin- и нативного кода используйте следующие подходы:

- **Удаляйте ненужный сгенерированный код**: Контролируйте объём автоматически генерируемого кода. Некоторые инструменты (например, генераторы по protocol buffers) могут создавать чрезмерное количество классов и методов, существенно увеличивая размер приложения.
- **Избегайте перечислений при необходимости**: Одно перечисление может добавить около 1,0–1,4 КБ к `classes.dex`. В больших системах это быстро накапливается. По возможности используйте аннотации `@IntDef`/`@StringDef` и shrinker, чтобы заменить enum на примитивы, сохранив большую часть преимуществ типобезопасности.
- **Уменьшайте размер нативных бинарников**: При использовании NDK оптимизируйте нативный код, убирайте неиспользуемые части и лишние ABI, чтобы не поставлять ненужные библиотеки.
- **Удаление отладочных символов**: Оставляйте отладочные символы только в debug-сборках или в отдельном symbol-файле для Crashlytics/Play Console. В релизные библиотеки загружайте версии без лишних символов.
- **Избегайте извлечения нативных библиотек**: В релизной конфигурации отключите устаревшую схему распаковки `.so` (например, `useLegacyPackaging = false` в настройках packaging). Это предотвращает копирование `.so` из APK на файловую систему при установке и помогает уменьшить занимаемое место и размер обновлений.

### Переоценка Функциональности И Переводов

#### Переоценка Редко Используемых Функций

Оптимизируйте приложение для устройств с ограниченными ресурсами (включая Android (Go edition)), отключая или удаляя функции с низким DAU. Например, тяжёлые анимации, большие GIF, неиспользуемые экраны, большие объёмы логирования и прочие неключевые элементы.

#### Использование Динамической Доставки

Play Feature Delivery (динамические feature-модули) использует возможности app bundle для условной или отложенной доставки отдельных функций. Крупные или редко используемые возможности могут загружаться только по требованию, что уменьшает первоначальный размер установки при сохранении функциональности.

#### Уменьшение Объёма Переводимых Строк

Используйте свойство `resConfigs` Android Gradle для удаления ненужных языковых ресурсов. Если подключённая библиотека (например, AppCompat или Google Play Services) содержит набор переводов, по умолчанию все эти строки попадают в приложение.

Чтобы оставить только языки, официально поддерживаемые приложением, перечислите их в `resConfigs`. Ресурсы для остальных языков будут исключены.

Например, чтобы оставить только английский и французский (Kotlin DSL):

```kotlin
android {
    defaultConfig {
        // ...
        resConfigs("en", "fr")
    }
}
```

#### Выборочный Перевод

Строки, которые никогда не отображаются пользователю (отладка, сообщения исключений, URL), можно не локализовать и хранить как литералы в коде.

Например, не стоит переводить URL:

```xml
<string name="car_frx_device_incompatible_sol_message">
  This device doesn\'t support Android Auto.\n
  &lt;a href="https://support.google.com/androidauto/answer/6395843"&gt;Learn more&lt;/a&gt;
</string>
```

`&lt;` и `&gt;` — это escape-символы для `<` и `>`. Они нужны, потому что прямой тег `<a>` внутри `<string>` может быть отброшен компилятором ресурсов. В таком варианте вы фактически локализуете HTML и URL на десятки языков. Вместо этого можно убрать HTML и не делать строку переводимой:

```xml
<string name="car_frx_device_incompatible_sol_message">
    This device doesn\'t support Android Auto.
</string>
```

---

## Answer (EN)

Small app size is directly related to download success, particularly in emerging markets with poor network connections or low network speeds. Larger downloads can result in lower install and usage rates, which in turn reduces the reach of your audience.

The main ways to reduce the size of an app are:
- Upload your app with Android App Bundles
- Reduce resource count and size
- Reduce native and Java/Kotlin code
- Re-evaluate features and translations

### Upload Your App with Android App Bundles

Upload your app as an Android App `Bundle` (AAB) to immediately save download and install size when you publish to Google Play. An Android App `Bundle` is an upload format that includes all your app's compiled code and resources but defers APK generation and signing to Google Play.

Google Play's app serving model then uses your app bundle to generate and serve optimized APKs for each user's device configuration so that they download only the code and resources they need to run your app. You don't have to build, sign, and manage multiple APKs to support different devices, and users get smaller, more optimized downloads.

### Reduce Resource Count and Size

The size of your app package has an impact on how fast your app loads, how much memory it uses, and how much power it consumes. You can make your app smaller by reducing the number and size of the resources it contains. In particular, you can remove resources that your app no longer uses and use scalable `Drawable` objects in place of bitmap image files when appropriate.

#### Remove Unused Resources

The `lint` tool—a static code analyzer included in Android Studio—detects resources in your `res/` folder that your code doesn't reference. When the `lint` tool discovers a potentially unused resource in your project, it prints a message like the following example:

```text
res/layout/preferences.xml: Warning: The resource R.layout.preferences appears
    to be unused [UnusedResources]
```

Libraries that you add to your code might include unused resources. Gradle can automatically remove resources on your behalf if you enable `shrinkResources` in your app's `build.gradle.kts` file:

```kotlin
android {
    // Other settings.

    buildTypes {
        getByName("release") {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

To use `shrinkResources`, you must enable code shrinking. During the build process, R8 first removes unused code. Then, the Android Gradle plugin removes the unused resources.

#### Support Only Specific Densities

Android supports different screen densities, such as the following:
- `ldpi`
- `mdpi`
- `tvdpi`
- `hdpi`
- `xhdpi`
- `xxhdpi`
- `xxxhdpi`

Although Android supports the preceding densities, you don't need to export your rasterized assets to each density.

If you know that only a small percentage of your users have devices with specific densities, consider whether you need to bundle those densities into your app. If you don't include resources for a specific screen density, Android automatically scales existing resources originally designed for other screen densities.

If your app only needs scaled images, you can save even more space by having a single variant of an image in `drawable-nodpi/`. It's usually recommended to include at least an `xxhdpi` image variant.

#### Use Drawable Objects

Some images don't require a static bitmap resource. The framework can dynamically draw the image at runtime instead. `Drawable` objects—or `<shape>` in XML—can take up a tiny amount of space in your APK. In addition, XML `Drawable` objects are well suited for monochromatic and simple shapes, and work well with Material Design guidelines.

#### Reuse Resources

You can include a separate resource for variations of an image, such as tinted, shaded, or rotated versions of the same image. However, it's often better to reuse the same base resources and customize them as needed at runtime.

Android provides several utilities to change the color of an asset, such as the `android:tint` and `tintMode` attributes.

You can also omit resources that are only a rotated equivalent of another resource. The following code snippet provides an example of turning a "thumb up" into a "thumb down" by pivoting at the middle of the image and rotating it 180 degrees:

```xml
<?xml version="1.0" encoding="utf-8"?>
<rotate xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/ic_thumb_up"
    android:pivotX="50%"
    android:pivotY="50%"
    android:fromDegrees="180" />
```

#### Compress PNG and JPEG Files

You can reduce PNG file sizes without losing image quality using tools like [pngcrush](https://pmt.sourceforge.io/pngcrush/), [pngquant](https://pngquant.org/), or [zopflipng](https://github.com/google/zopfli). All of these tools can reduce PNG file size while preserving perceived image quality.

The `pngcrush` tool is particularly effective. This tool iterates over PNG filters and zlib (Deflate) parameters, using each combination of filters and parameters to compress the image. It then chooses the configuration that yields the smallest compressed output.

To compress JPEG files, you can use tools like [packJPG](https://github.com/packjpg/packJPG) and [guetzli](https://github.com/google/guetzli).

#### Use WebP File Format

Instead of using PNG or JPEG files, you can also use the [WebP](https://developers.google.com/speed/webp) file format for your images. The WebP format provides lossy compression and transparency and can often provide better compression than either JPEG or PNG.

You can convert existing BMP, JPG, PNG, or static GIF images to WebP format using Android Studio. For more information, see [Create WebP images](https://developer.android.com/studio/write/convert-webp).

#### Use Downloadable Fonts

Because many apps on the Play Store use the same fonts, bundling font files in every app causes duplication on the device. Downloadable Fonts allow apps to request fonts from a shared provider instead of bundling them, which reduces the APK/AAB size and avoids duplicate copies on the device.

### Reduce Native and Java/Kotlin Code

You can use the following methods to reduce the size of the Java/Kotlin and native codebase in your app:

- **Remove unnecessary generated code**: Understand the footprint of any code that is automatically generated. For example, some protocol buffer tools can generate an excessive number of methods and classes, which can significantly increase your app size.
- **Avoid enumerations where appropriate**: A single enum can add about 1.0 to 1.4 KB to your app's `classes.dex` file. These additions can accumulate for complex systems or shared libraries. If possible, consider using the `@IntDef`/`@StringDef` annotations and code shrinking to strip enums and represent them as primitives. This preserves most of the type-safety benefits while reducing size.
- **Reduce the size of native binaries**: If your app uses native code and the Android NDK, you can reduce the size of the release version of your app by optimizing your code—for example, removing debug symbols and avoiding unnecessary ABIs.
- **Remove debug symbols**: Debug symbols make sense in development builds. For release builds, strip unnecessary debug symbols from native libraries (for example, using `llvm-strip` or appropriate strip tools). Keep a separate symbol file for crash reporting.
- **Avoid extracting native libraries**: When building the release version of your app, package uncompressed `.so` files in the APK / app bundle by setting `useLegacyPackaging = false` for the relevant packaging options in your Gradle config. Disabling legacy packaging prevents `PackageManager` from copying `.so` files from the APK to the filesystem during installation, which can make on-device storage usage and updates smaller.

### Re-evaluate Features and Translations

#### Re-evaluate Infrequently Used Features

Optimize specifically for constrained devices (including Android (Go edition)) by disabling or removing features that have low daily active user (DAU) metrics. Examples include complex animations, large GIF files, heavy debug or logging frameworks, or other non-essential visual and diagnostic assets.

#### Utilize Dynamic Delivery

Play Feature Delivery uses app bundle capabilities to deliver certain features conditionally or on demand. You can use feature modules for custom delivery, which allows you to download large or rarely used features only when needed. This reduces the initial install size while still making those capabilities available.

#### Reduce Translatable `String` Size

You can use the Android Gradle `resConfigs` property to remove alternative resource files that your app doesn't need. If you're using a library that includes language resources (such as AppCompat or Google Play Services), then your app includes all translated language strings for library messages by default, regardless of your app's own supported languages.

If you'd like to keep only the languages that your app officially supports, you can specify those languages using the `resConfigs` property. Any resources for languages not specified are removed.

To limit your language resources to just English and French in Kotlin DSL, you can edit `defaultConfig` as shown below:

```kotlin
android {
    defaultConfig {
        // ...
        resConfigs("en", "fr")
    }
}
```

#### Use Selective Translation

If a given string is never visible in the app's UI, then you don't have to translate it. Strings for debugging, exception messages, or URLs can be string literals in code rather than translatable resources.

For example, don't translate URLs:

```xml
<string name="car_frx_device_incompatible_sol_message">
  This device doesn\'t support Android Auto.\n
  &lt;a href="https://support.google.com/androidauto/answer/6395843"&gt;Learn more&lt;/a&gt;
</string>
```

You may recognize `&lt;` and `&gt;` as escape characters for `<` and `>`. They're needed here because if you were to put an `<a>` tag inside of a `<string>` tag, then the Android resource compiler drops it if it doesn't recognize the tag. However, this also means you're translating the HTML tags and the URL into many languages. Instead, you can remove the HTML so it doesn't need translation:

```xml
<string name="car_frx_device_incompatible_sol_message">
    This device doesn\'t support Android Auto.
</string>
```

---

## Follow-ups

- [[q-how-to-catch-the-earliest-entry-point-into-the-application--android--medium]]
- [[q-memory-leak-vs-oom-android--android--medium]]
- Which parts of the app (code, resources, or libraries) typically contribute most to size in your projects, and how would you measure them?
- How would you integrate R8 configuration and `shrinkResources` into a CI pipeline to ensure size regressions are detected early?
- When would you choose dynamic feature modules over a monolithic app in terms of size, and what trade-offs does this introduce?


## References
- [Reduce your app size](https://developer.android.com/topic/performance/reduce-apk-size)
- [Reduce app size](https://developer.android.com/guide/topics/androidgo/optimize-size)
- [8 Ways to Reduce Android App Size During Development Phase?](https://www.elluminatiinc.com/reduce-android-app-size/)
- [8 Best Ways to Reduce Android App Size](https://www.mantralabsglobal.com/blog/reduce-android-app-size/)
- [Minimizing APK Size: Techniques for Shrinking Android App Size](https://diegomarcher.medium.com/minimizing-apk-size-techniques-for-shrinking-android-app-size-7a4c5eefbd46)


## Related Questions

### Prerequisites / Concepts

- [[c-gradle]]
- [[c-app-bundle]]
- [[c-memory-management]]


### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview
### Related (Medium)
- [[q-reduce-apk-size-techniques--android--medium]] - Build Optimization
- [[q-app-size-optimization--android--medium]] - Performance
- [[q-app-startup-optimization--android--medium]] - Performance
- [[q-macrobenchmark-startup--android--medium]] - Performance
### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose