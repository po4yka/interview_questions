---
id: android-004
title: "Ways to Reduce Android App Size / Способы уменьшения размера Android приложения"
aliases: []

# Classification
topic: android
subtopics: [app-bundle, gradle, performance-memory]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [android/app-bundles, android/optimization, android/resources, difficulty/medium, en, ru]
source: https://github.com/Kirchhoff-Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: [q-how-to-catch-the-earliest-entry-point-into-the-application--android--medium, q-memory-leak-vs-oom-android--android--medium, q-what-do-you-know-about-modifiers--programming-languages--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [android/app-bundle, android/gradle, android/performance-memory, difficulty/medium, en, ru]
date created: Saturday, November 1st 2025, 12:47:02 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Question (EN)
> What ways do you know to reduce the size of an application?
# Вопрос (RU)
> Какие способы уменьшения размера приложения вы знаете?

---

## Answer (EN)

Small app size is directly related to download success, particularly in emerging markets with poor network device connections or low network speeds. This can result in lower app usage rates, which in turn lowers the scope and reach of your audience.

The main ways to reduce the size of app are:
- Upload your app with Android App Bundles
- Reduce resource count and size
- Reduce native and Java code
- Re-evaluate feature and translation

### Upload Your App with Android App Bundles

Upload your app as an Android App Bundle to immediately save app size when you publish to Google Play. Android App Bundle is an upload format that includes all your app's compiled code and resources but defers APK generation and signing to Google Play.

Google Play's app serving model then uses your app bundle to generate and serve optimized APKs for each user's device configuration so that they download only the code and resources they need to run your app. You don't have to build, sign, and manage multiple APKs to support different devices, and users get smaller, more optimized downloads.

### Reduce Resource Count and Size

The size of your APK has an impact on how fast your app loads, how much memory it uses, and how much power it consumes. You can make your APK smaller by reducing the number and size of the resources it contains. In particular, you can remove resources that your app no longer uses, and you can use scalable `Drawable` objects in place of image files.

#### Remove Unused Resources

The `lint` tool—a static code analyzer included in Android Studio—detects resources in your `res/` folder that your code doesn't reference. When the `lint` tool discovers a potentially unused resource in your project, it prints a message like the following example:

```
res/layout/preferences.xml: Warning: The resource R.layout.preferences appears
    to be unused [UnusedResources]
```

Libraries that you add to your code might include unused resources. Gradle can automatically remove resources on your behalf if you enable `shrinkResources` in your app's `build.gradle.kts` file:

```kotlin
android {
    // Other settings.

    buildTypes {
        getByName("release") {
            minifyEnabled = true
            shrinkResources = true
            proguardFiles(getDefaultProguardFile('proguard-android.txt'), "proguard-rules.pro")
        }
    }
}
```

To use `shrinkResources`, enable code shrinking. During the build process, R8 first removes unused code. Then, the Android Gradle plugin removes the unused resources.

#### Support only Specific Densities

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

If your app needs only scaled images, you can save even more space by having a single variant of an image in `drawable-nodpi/`. We recommend you include at least an `xxhdpi` image variant in your app.

#### Use Drawable Objects

Some images don't require a static image resource. The framework can dynamically draw the image at runtime instead. `Drawable` objects—or `<shape>` in XML — can take up a tiny amount of space in your APK. In addition, XML `Drawable` objects produce monochromatic images compliant with Material Design guidelines.

#### Reuse Resources

You can include a separate resource for variations of an image, such as tinted, shaded, or rotated versions of the same image. However, we recommend that you reuse the same set of resources and customizing them as needed at runtime.

Android provides several utilities to change the color of an asset, either using the `android:tint` and `tintMode` attributes.

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

You can reduce PNG file sizes without losing image quality using tools like [pngcrush](https://pmt.sourceforge.io/pngcrush/), [pngquant](https://pngquant.org/), or [zopflipng](https://github.com/google/zopfli). All of these tools can reduce PNG file size while preserving the perceptive image quality.

The `pngcrush` tool is particularly effective. This tool iterates over PNG filters and zlib (Deflate) parameters, using each combination of filters and parameters to compress the image. It then chooses the configuration that yields the smallest compressed output.

To compress JPEG files, you can use tools like [packJPG](https://github.com/packjpg/packJPG) and [guetzli](https://github.com/google/guetzli).

#### Use WebP File Format

Instead of using PNG or JPEG files, you can also use the [WebP](https://developers.google.com/speed/webp) file format for your images. The WebP format provides lossy compression and transparency, like JPG and PNG, and it can provide better compression than either JPEG or PNG.

You can convert existing BMP, JPG, PNG or static GIF images to WebP format using Android Studio. For more information, see [Create WebP images](https://developer.android.com/studio/write/convert-webp).

#### Use Downloadable Fonts

Since most programs on the Play Store share the same fonts, the App package already includes many of them. Duplication occurs when a user runs multiple apps with the same fonts on the same device. In response to the issue, Google added Downloadable fonts to its Support collection. APIs can now simply request typefaces instead of bundling files.

### Reduce Native and Java Code

You can use the following methods to reduce the size of the Java and native codebase in your app:

- **Remove unnecessary generated code**: Make sure to understand the footprint of any code which is automatically generated. For example, many protocol buffer tools generate an excessive number of methods and classes, which can double or triple the size of your app
- **Avoid enumerations**: A single enum can add about 1.0 to 1.4 KB to your app's `classes.dex` file. These additions can quickly accumulate for complex systems or shared libraries. If possible, consider using the `@IntDef` annotation and code shrinking to strip enumerations out and convert them to integers. This type conversion preserves all of the type safety benefits of enums
- **Reduce the size of native binaries**: If your app uses native code and the Android NDK, you can also reduce the size of the release version of your app by optimizing your code. Two useful techniques are removing debug symbols and not extracting native libraries
- **Remove debug symbols**: Using debug symbols makes sense if your app is in development and still requires debugging. Use the `arm-eabi-strip` tool provided in the Android NDK to remove unnecessary debug symbols from native libraries. Afterwards, you can compile your release build
- **Avoid extracting native libraries**: When building the release version of your app, package uncompressed `.so` files in the APK by setting `useLegacyPackaging` to `false` in your app's `build.gradle.kts` file. Disabling this flag prevents `PackageManager` from copying `.so` files from the APK to the filesystem during installation. This method makes updates of your app smaller

### Re-evaluate Feature and Translation

#### Re-evaluate Infrequently Used Features

Specifically optimize for Android (Go edition) by disabling features that have low daily active user (DAU) metrics. Examples of this include removing complex animations, large GIF files, or any other aesthetic additions not necessary for app success.

#### Utilize Dynamic Delivery

Play Feature Delivery uses advanced capabilities of app bundles, allowing certain features of your app to be delivered conditionally or downloaded on demand. You can use feature modules for custom delivery. A unique benefit of feature modules is the ability to customize how and when different features of your app are downloaded onto devices running Android 5.0 (API level 21) or higher.

#### Reduce Translatable String Size

You can use the Android Gradle `resConfigs` property to remove alternative resource files that your app doesn't need. If you're using a library that includes language resources (such as AppCompat or Google Play Services), then your app includes all translated language strings for library messages, regardless of app translation. If you'd like to keep only the languages that your app officially supports, you can specify those languages using the `resConfig` property. Any resources for languages not specified are removed.

To limit your language resources to just English and French, you can edit `defaultConfig` as shown below:

```kotlin
android {
    defaultConfig {
        ...
        resConfigs "en", "fr"
    }
}
```

#### Use Selective Translation

If a given string isn't visible in the app's UI, then you don't have to translate it. Strings for the purpose of debugging, exception messages, or URLs should be string literals in code, not resources.

For example, don't bother translating URLs:

```xml
<string name="car_frx_device_incompatible_sol_message">
  This device doesn\'t support Android Auto.\n
  &lt;a href="https://support.google.com/androidauto/answer/6395843"&gt;Learn more&lt;/a>
</string>
```

You may recognize `&lt;` and `&gt`, as these are escape characters for `<` and `>`. They're needed here because if you were to put an `<a>` tag inside of a `<string>` tag, then the Android resource compiler drops them since it doesn't recognize the tag. However, this means that you're translating the HTML tags and the URL to 78 languages. Instead, you can remove the HTML:

```xml
<string name="car_frx_device_incompatible_sol_message">
         This device doesn\'t support Android Auto.
</string>
```

## Ответ (RU)

Небольшой размер приложения напрямую связан с успехом загрузки, особенно на развивающихся рынках с плохими сетевыми подключениями устройств или низкими скоростями сети. Это может привести к снижению показателей использования приложения, что в свою очередь снижает охват и досягаемость вашей аудитории.

Основные способы уменьшения размера приложения:
- Загрузка приложения с помощью Android App Bundles
- Уменьшение количества и размера ресурсов
- Уменьшение нативного кода и Java кода
- Переоценка функций и переводов

### Загрузка Приложения С Помощью Android App Bundles

Загрузите свое приложение как Android App Bundle, чтобы немедленно сэкономить размер приложения при публикации в Google Play. Android App Bundle - это формат загрузки, который включает весь скомпилированный код и ресурсы вашего приложения, но откладывает генерацию и подписание APK на Google Play.

Модель обслуживания приложений Google Play затем использует ваш app bundle для генерации и обслуживания оптимизированных APK для конфигурации устройства каждого пользователя, чтобы они загружали только код и ресурсы, необходимые для запуска вашего приложения. Вам не нужно создавать, подписывать и управлять несколькими APK для поддержки различных устройств, а пользователи получают меньшие, более оптимизированные загрузки.

### Уменьшение Количества И Размера Ресурсов

Размер вашего APK влияет на то, насколько быстро загружается ваше приложение, сколько памяти оно использует и сколько энергии потребляет. Вы можете уменьшить размер APK, уменьшив количество и размер содержащихся в нем ресурсов. В частности, вы можете удалить ресурсы, которые ваше приложение больше не использует, и вы можете использовать масштабируемые объекты `Drawable` вместо файлов изображений.

#### Удаление Неиспользуемых Ресурсов

Инструмент `lint` - статический анализатор кода, включенный в Android Studio - обнаруживает ресурсы в вашей папке `res/`, на которые не ссылается ваш код. Когда инструмент `lint` обнаруживает потенциально неиспользуемый ресурс в вашем проекте, он выводит сообщение, подобное следующему примеру:

```
res/layout/preferences.xml: Warning: The resource R.layout.preferences appears
    to be unused [UnusedResources]
```

Библиотеки, которые вы добавляете в свой код, могут включать неиспользуемые ресурсы. Gradle может автоматически удалять ресурсы от вашего имени, если вы включите `shrinkResources` в файле `build.gradle.kts` вашего приложения:

```kotlin
android {
    // Другие настройки.

    buildTypes {
        getByName("release") {
            minifyEnabled = true
            shrinkResources = true
            proguardFiles(getDefaultProguardFile('proguard-android.txt'), "proguard-rules.pro")
        }
    }
}
```

Чтобы использовать `shrinkResources`, включите сжатие кода. Во время процесса сборки R8 сначала удаляет неиспользуемый код. Затем плагин Android Gradle удаляет неиспользуемые ресурсы.

#### Поддержка Только Определенных Плотностей

Android поддерживает различные плотности экрана, такие как следующие:
- `ldpi`
- `mdpi`
- `tvdpi`
- `hdpi`
- `xhdpi`
- `xxhdpi`
- `xxxhdpi`

Хотя Android поддерживает вышеперечисленные плотности, вам не нужно экспортировать свои растровые ассеты для каждой плотности.

Если вы знаете, что только небольой процент ваших пользователей имеет устройства с определенными плотностями, подумайте, нужно ли вам включать эти плотности в ваше приложение. Если вы не включаете ресурсы для определенной плотности экрана, Android автоматически масштабирует существующие ресурсы, первоначально разработанные для других плотностей экрана.

Если вашему приложению нужны только масштабированные изображения, вы можете сэкономить еще больше места, имея один вариант изображения в `drawable-nodpi/`. Мы рекомендуем включить хотя бы вариант изображения `xxhdpi` в ваше приложение.

#### Использование Drawable Объектов

Некоторые изображения не требуют статического ресурса изображения. Фреймворк может динамически нарисовать изображение во время выполнения. Объекты `Drawable` - или `<shape>` в XML - могут занимать крошечное количество места в вашем APK. Кроме того, XML-объекты `Drawable` создают монохромные изображения, соответствующие рекомендациям Material Design.

#### Повторное Использование Ресурсов

Вы можете включить отдельный ресурс для вариаций изображения, таких как тонированные, затененные или повернутые версии одного и того же изображения. Однако мы рекомендуем повторно использовать один и тот же набор ресурсов и настраивать их по мере необходимости во время выполнения.

Android предоставляет несколько утилит для изменения цвета ассета, используя атрибуты `android:tint` и `tintMode`.

Вы также можете опустить ресурсы, которые являются только повернутым эквивалентом другого ресурса. Следующий фрагмент кода представляет пример превращения "большого пальца вверх" в "большой палец вниз" путем поворота в середине изображения и поворота его на 180 градусов:

```xml
<?xml version="1.0" encoding="utf-8"?>
<rotate xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/ic_thumb_up"
    android:pivotX="50%"
    android:pivotY="50%"
    android:fromDegrees="180" />
```

#### Сжатие PNG И JPEG Файлов

Вы можете уменьшить размер файлов PNG без потери качества изображения, используя такие инструменты, как [pngcrush](https://pmt.sourceforge.io/pngcrush/), [pngquant](https://pngquant.org/) или [zopflipng](https://github.com/google/zopfli). Все эти инструменты могут уменьшить размер файла PNG, сохраняя при этом воспринимаемое качество изображения.

Инструмент `pngcrush` особенно эффективен. Этот инструмент перебирает фильтры PNG и параметры zlib (Deflate), используя каждую комбинацию фильтров и параметров для сжатия изображения. Затем он выбирает конфигурацию, которая дает наименьший сжатый вывод.

Для сжатия файлов JPEG вы можете использовать такие инструменты, как [packJPG](https://github.com/packjpg/packJPG) и [guetzli](https://github.com/google/guetzli).

#### Использование Формата Файла WebP

Вместо использования файлов PNG или JPEG вы также можете использовать формат файла [WebP](https://developers.google.com/speed/webp) для ваших изображений. Формат WebP обеспечивает сжатие с потерями и прозрачность, как JPG и PNG, и он может обеспечить лучшее сжатие, чем JPEG или PNG.

Вы можете конвертировать существующие изображения BMP, JPG, PNG или статические GIF в формат WebP с помощью Android Studio. Для получения дополнительной информации см. [Создание изображений WebP](https://developer.android.com/studio/write/convert-webp).

#### Использование Загружаемых Шрифтов

Поскольку большинство программ в Play Store используют одни и те же шрифты, пакет приложения уже включает многие из них. Дублирование происходит, когда пользователь запускает несколько приложений с одинаковыми шрифтами на одном устройстве. В ответ на эту проблему Google добавил загружаемые шрифты в свою коллекцию поддержки. API теперь могут просто запрашивать шрифты вместо объединения файлов.

### Уменьшение Нативного Кода И Java Кода

Вы можете использовать следующие методы для уменьшения размера кодовой базы Java и нативного кода в вашем приложении:

- **Удаление ненужного сгенерированного кода**: Убедитесь, что вы понимаете объем любого автоматически генерируемого кода. Например, многие инструменты protocol buffer генерируют чрезмерное количество методов и классов, что может удвоить или утроить размер вашего приложения
- **Избегайте перечислений**: Одно перечисление может добавить около 1.0-1.4 КБ к файлу `classes.dex` вашего приложения. Эти дополнения могут быстро накапливаться для сложных систем или общих библиотек. Если возможно, рассмотрите возможность использования аннотации `@IntDef` и сжатия кода для удаления перечислений и преобразования их в целые числа. Этот тип преобразования сохраняет все преимущества типобезопасности перечислений
- **Уменьшение размера нативных бинарных файлов**: Если ваше приложение использует нативный код и Android NDK, вы также можете уменьшить размер релизной версии вашего приложения, оптимизируя свой код. Две полезные техники - это удаление отладочных символов и не извлечение нативных библиотек
- **Удаление отладочных символов**: Использование отладочных символов имеет смысл, если ваше приложение находится в разработке и все еще требует отладки. Используйте инструмент `arm-eabi-strip`, предоставляемый в Android NDK, для удаления ненужных отладочных символов из нативных библиотек. После этого вы можете скомпилировать свою релизную сборку
- **Избегайте извлечения нативных библиотек**: При создании релизной версии вашего приложения упакуйте несжатые файлы `.so` в APK, установив `useLegacyPackaging` в `false` в файле `build.gradle.kts` вашего приложения. Отключение этого флага предотвращает копирование `PackageManager` файлов `.so` из APK в файловую систему во время установки. Этот метод делает обновления вашего приложения меньше

### Переоценка Функций И Переводов

#### Переоценка Редко Используемых Функций

Специально оптимизируйте для Android (Go edition), отключая функции, которые имеют низкие показатели ежедневных активных пользователей (DAU). Примеры этого включают удаление сложных анимаций, больших GIF-файлов или любых других эстетических дополнений, не необходимых для успеха приложения.

#### Использование Динамической Доставки

Play Feature Delivery использует расширенные возможности app bundles, позволяя условно доставлять определенные функции вашего приложения или загружать их по требованию. Вы можете использовать модули функций для пользовательской доставки. Уникальное преимущество модулей функций - это возможность настраивать, как и когда различные функции вашего приложения загружаются на устройства под управлением Android 5.0 (API level 21) или выше.

#### Уменьшение Размера Переводимых Строк

Вы можете использовать свойство Android Gradle `resConfigs` для удаления альтернативных файлов ресурсов, которые не нужны вашему приложению. Если вы используете библиотеку, которая включает языковые ресурсы (такие как AppCompat или Google Play Services), то ваше приложение включает все переведенные языковые строки для сообщений библиотеки, независимо от перевода приложения. Если вы хотите сохранить только языки, которые официально поддерживает ваше приложение, вы можете указать эти языки, используя свойство `resConfig`. Любые ресурсы для неуказанных языков удаляются.

Чтобы ограничить ваши языковые ресурсы только английским и французским, вы можете отредактировать `defaultConfig`, как показано ниже:

```kotlin
android {
    defaultConfig {
        ...
        resConfigs "en", "fr"
    }
}
```

#### Использование Выборочного Перевода

Если данная строка не видна в UI приложения, то вам не нужно ее переводить. Строки для целей отладки, сообщения об исключениях или URL должны быть строковыми литералами в коде, а не ресурсами.

Например, не стоит переводить URL:

```xml
<string name="car_frx_device_incompatible_sol_message">
  This device doesn\'t support Android Auto.\n
  &lt;a href="https://support.google.com/androidauto/answer/6395843"&gt;Learn more&lt;/a>
</string>
```

Вы можете распознать `&lt;` и `&gt`, поскольку это escape-символы для `<` и `>`. Они нужны здесь, потому что если бы вы поместили тег `<a>` внутри тега `<string>`, то компилятор ресурсов Android отбросит их, поскольку не распознает тег. Однако это означает, что вы переводите HTML-теги и URL на 78 языков. Вместо этого вы можете удалить HTML:

```xml
<string name="car_frx_device_incompatible_sol_message">
         This device doesn\'t support Android Auto.
</string>
```

---

## References
- [Reduce your app size](https://developer.android.com/topic/performance/reduce-apk-size)
- [Reduce app size](https://developer.android.com/guide/topics/androidgo/optimize-size)
- [8 Ways to Reduce Android App Size During Development Phase?](https://www.elluminatiinc.com/reduce-android-app-size/)
- [8 Best Ways to Reduce Android App Size](https://www.mantralabsglobal.com/blog/reduce-android-app-size/)
- [Minimizing APK Size: Techniques for Shrinking Android App Size](https://diegomarcher.medium.com/minimizing-apk-size-techniques-for-shrinking-android-app-size-7a4c5eefbd46)


## Follow-ups

- [[q-how-to-catch-the-earliest-entry-point-into-the-application--android--medium]]
- [[q-memory-leak-vs-oom-android--android--medium]]
- [[q-what-do-you-know-about-modifiers--programming-languages--medium]]


## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview
### Related (Medium)
- [[q-reduce-apk-size-techniques--android--medium]] - Build Optimization
- [[q-app-size-optimization--android--medium]] - Performance
- [[q-app-startup-optimization--android--medium]] - Performance
- [[q-macrobenchmark-startup--android--medium]] - Performance
### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
