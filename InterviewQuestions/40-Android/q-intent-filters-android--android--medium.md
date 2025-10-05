---
tags:
  - android
  - intent-filter
  - deep-linking
  - manifest
  - implicit-intent
  - difficulty/medium
  - intents-deeplinks
  - activity
subtopics:
  - intents-deeplinks
  - activity
  - manifest
difficulty: medium
status: draft
source: Kirchhoff-Android-Interview-Questions
---

# Intent Filters in Android / Фильтры намерений в Android

**English**: What do you know about Intent Filters in Android?

**Russian**: Что вы знаете о фильтрах намерений в Android?

## Answer

**Intent Filter** is an expression in an app's manifest file that specifies the type of intents that a component would like to receive. It allows components to declare their capabilities and enables implicit intent resolution in Android.

An app component can have multiple intent filters, each describing different capabilities. Without intent filters, a component can only be started with explicit intents.

---

## Intent Filter Basics

### Definition

An **intent filter** is an expression in an app's manifest file that specifies the type of intents that the component would like to receive. For instance, by declaring an intent filter for an activity, you make it possible for other apps to directly start your activity with a certain kind of intent. Likewise, if you do *not* declare any intent filters for an activity, then it can be started only with an explicit intent.

### Multiple Filters

An app component can have any number of intent filters (defined with the `<intent-filter>` element), each one describing a different capability of that component.

---

## `<intent-filter>` Element

### Syntax

```xml
<intent-filter android:icon="drawable resource"
               android:label="string resource"
               android:priority="integer"
               android:order="integer"
               android:autoVerify="boolean">
    ...
</intent-filter>
```

### Contained In

The `<intent-filter>` element can be placed inside:
- `<activity>`
- `<activity-alias>`
- `<service>`
- `<receiver>`
- `<provider>`

### Required Elements

- **`<action>`** - Must contain at least one action element

### Optional Elements

- **`<category>`** - Categorizes the intent
- **`<data>`** - Specifies data type and URI structure

### Attributes

#### `android:icon`

An icon that represents the parent activity, service, or broadcast receiver when that component is presented to the user as having the capability described by the filter.

This attribute is set as a reference to a drawable resource containing the image definition. The default value is the icon set by the parent component's `icon` attribute. If the parent doesn't specify an icon, the default is the icon set by the `<application>` element.

#### `android:label`

A user-readable label for the parent component. This label, rather than the one set by the parent component, is used when the component is presented to the user as having the capability described by the filter.

The label is set as a reference to a string resource so that it can be localized like other strings in the user interface. However, as a convenience while you're developing the application, it can also be set as a raw string.

The default value is the label set by the parent component. If the parent doesn't specify a label, the default is the label set by the `<application>` element's `label` attribute.

#### `android:priority`

The priority given to the parent component with regard to handling intents of the type described by the filter. This attribute has meaning for both activities and broadcast receivers.

Use this attribute only if you need to impose a specific order in which the broadcasts are received or want to force Android to prefer one activity over others.

#### `android:order`

The order in which the filter is processed when multiple filters match. `order` differs from `priority` in that `priority` applies across apps, while order disambiguates multiple matching filters in a single app. When multiple filters can match, use a directed intent instead.

**Introduced in:** API level 28

#### `android:autoVerify`

Whether Android needs to verify that the Digital Asset Links JSON file from the specified host matches this application. Used for App Links verification.

**Introduced in:** API level 23

---

## `<action>` Element

### Syntax

```xml
<action android:name="string" />
```

### Description

Adds an action to an intent filter. An `<intent-filter>` element must contain one or more `<action>` elements. If there are no `<action>` elements in an intent filter, the filter doesn't accept any Intent objects.

### Attributes

#### `android:name`

The name of the action. Some standard actions are defined in the `Intent` class as `ACTION_*` constants. To assign one of these actions to this attribute, prepend `android.intent.action.` to the string that follows `ACTION_`.

**Examples:**
- For `ACTION_MAIN`, use `android.intent.action.MAIN`
- For `ACTION_WEB_SEARCH`, use `android.intent.action.WEB_SEARCH`
- For `ACTION_SEND`, use `android.intent.action.SEND`

**Custom Actions:**

For actions you define, it's best to use your app's package name as a prefix to help ensure uniqueness:

```xml
<action android:name="com.example.project.TRANSMOGRIFY" />
```

---

## `<category>` Element

### Syntax

```xml
<category android:name="string" />
```

### Attributes

#### `android:name`

The name of the category. Standard categories are defined in the `Intent` class as `CATEGORY_*` constants. The name assigned here is derived from those constants by prefixing `android.intent.category.` to the name that follows `CATEGORY_`.

**Examples:**
- For `CATEGORY_LAUNCHER`, use `android.intent.category.LAUNCHER`
- For `CATEGORY_DEFAULT`, use `android.intent.category.DEFAULT`
- For `CATEGORY_BROWSABLE`, use `android.intent.category.BROWSABLE`

**Custom Categories:**

For custom categories, use the package name as a prefix so that they are unique.

---

## `<data>` Element

### Syntax

```xml
<data android:scheme="string"
      android:host="string"
      android:port="string"
      android:path="string"
      android:pathPattern="string"
      android:pathPrefix="string"
      android:pathSuffix="string"
      android:pathAdvancedPattern="string"
      android:mimeType="string" />
```

### Description

Adds a data specification to an intent filter. The specification can be:
- A data type (using the `mimeType` attribute)
- A URI
- Both a data type and a URI

### URI Structure

A URI is specified by separate attributes for each of its parts:

```
<scheme>://<host>:<port>[<path>|<pathPrefix>|<pathPattern>|<pathAdvancedPattern>|<pathSuffix>]
```

### URI Attribute Dependencies

These attributes that specify the URI format are optional, but also mutually dependent:
- If a `scheme` isn't specified for the intent filter, all the other URI attributes are ignored
- If a `host` isn't specified for the filter, the `port` attribute and all the path attributes are ignored

### Multiple Data Elements

All the `<data>` elements contained within the same `<intent-filter>` element contribute to the same filter.

**Example 1:**
```xml
<intent-filter>
    <data android:scheme="something" android:host="project.example.com" />
</intent-filter>
```

**Example 2 (equivalent):**
```xml
<intent-filter>
    <data android:scheme="something" />
    <data android:host="project.example.com" />
</intent-filter>
```

Both examples are equivalent. You can place any number of `<data>` elements inside an `<intent-filter>` to give it multiple data options. None of its attributes have default values.

---

## Example Intent Filters

### Main Launcher Activity

```xml
<activity android:name="MainActivity" android:exported="true">
    <!-- This activity is the main entry, should appear in app launcher -->
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
```

**Explanation:**
- The `ACTION_MAIN` action indicates this is the main entry point and does not expect any intent data
- The `CATEGORY_LAUNCHER` category indicates that this activity's icon should be placed in the system's app launcher
- These two must be paired together in order for the activity to appear in the app launcher

### Share Activity Example

```xml
<activity android:name="ShareActivity" android:exported="false">
    <!-- This activity handles "SEND" actions with text data -->
    <intent-filter>
        <action android:name="android.intent.action.SEND"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <data android:mimeType="text/plain"/>
    </intent-filter>

    <!-- This activity also handles "SEND" and "SEND_MULTIPLE" with media data -->
    <intent-filter>
        <action android:name="android.intent.action.SEND"/>
        <action android:name="android.intent.action.SEND_MULTIPLE"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <data android:mimeType="application/vnd.google.panorama360+jpg"/>
        <data android:mimeType="image/*"/>
        <data android:mimeType="video/*"/>
    </intent-filter>
</activity>
```

**Explanation:**

The `ShareActivity` is intended to facilitate sharing text and media content. Although users might enter this activity by navigating to it from `MainActivity`, they can also enter `ShareActivity` directly from another app that issues an implicit intent matching one of the two intent filters.

---

## Use Cases of Intent Filters

Intent filters in Android have various use cases that enable your app to interact with other apps, system components, and handle different types of intents:

### 1. Deep Linking

You can use intent filters to enable deep linking into specific activities of your app. By defining a specific URL scheme and associating it with your activity in the intent filter, users can open your app directly from a web link or another app.

**Example:**
```xml
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data
        android:scheme="myapp"
        android:host="product"
        android:pathPrefix="/detail" />
</intent-filter>
```

### 2. Implicit Intent Handling

Intent filters allow your app to respond to implicit intents sent by other apps. For example, if your app can handle the `ACTION_SEND` intent action and `text/plain` data type, users can share text from other apps directly to your app.

### 3. Broadcast Receivers

Intent filters are commonly used with `BroadcastReceiver` to listen for specific broadcast intents and take appropriate actions.

**Example:**
```xml
<receiver android:name=".BatteryReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BATTERY_LOW" />
    </intent-filter>
</receiver>
```

### 4. Opening Specific File Types

By specifying data types in intent filters, your app can handle requests to open specific file types, such as images, videos, or documents. Users can then select your app as the default handler for those file types.

**Example:**
```xml
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <data android:mimeType="image/*" />
</intent-filter>
```

### 5. URL Handling

If your app interacts with specific URLs or web services, you can define an intent filter to handle those URLs, enabling your app to open and process the data accordingly.

### 6. App Widget Configuration

Intent filters can be used to configure app widgets. When users add your app's widget to their home screen, they can customize the widget's behavior through a configuration activity launched via an intent filter.

### 7. Notification Actions

When users interact with a notification, you can use intent filters to define actions that should be triggered when specific buttons in the notification are tapped.

### 8. Implicit App Invocations

Intent filters can enable your app to handle specific system events or actions.

**Example:**
```xml
<receiver android:name=".BootReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

### 9. Sharing Content

Intent filters allow your app to be a content provider for other apps. For instance, if your app has user-generated content, other apps can request that content using a custom intent.

### 10. Voice Actions

Intent filters can be used to handle voice actions initiated by the user, enabling voice interaction with your app.

---

## Best Practices

### 1. Always Include CATEGORY_DEFAULT

For activities that should receive implicit intents, always include the `CATEGORY_DEFAULT` category:

```xml
<intent-filter>
    <action android:name="android.intent.action.SEND" />
    <category android:name="android.intent.category.DEFAULT" />
    <data android:mimeType="text/plain" />
</intent-filter>
```

### 2. Use android:exported Explicitly

Starting from Android 12 (API level 31), you must explicitly declare the `android:exported` attribute for components with intent filters:

```xml
<activity android:name=".MainActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
```

### 3. Be Specific with Data Types

When filtering by MIME type, be as specific as possible to avoid unintended intent matches:

```xml
<!-- Too broad -->
<data android:mimeType="*/*" />

<!-- Better -->
<data android:mimeType="image/jpeg" />
```

### 4. Use autoVerify for App Links

For HTTPS URLs that should open directly in your app, use `android:autoVerify="true"`:

```xml
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data
        android:scheme="https"
        android:host="www.example.com" />
</intent-filter>
```

---

## Summary

**Intent Filters:**
- Declare component capabilities in the manifest
- Enable implicit intent resolution
- Support deep linking and app links
- Can be used with activities, services, broadcast receivers, and content providers
- Must include at least one `<action>` element
- Can include multiple `<category>` and `<data>` elements
- Support various use cases: deep linking, file handling, broadcasts, sharing, etc.

**Key Components:**
- `<action>` - What action the component can perform
- `<category>` - Additional information about the component
- `<data>` - Type of data the component can handle (MIME type and/or URI)

**Important Attributes:**
- `android:priority` - For ordering across apps
- `android:order` - For ordering within single app (API 28+)
- `android:autoVerify` - For App Links verification (API 23+)

---

## Ответ

**Intent Filter** - это выражение в манифесте приложения, которое определяет типы намерений (intents), которые компонент готов принимать. Он позволяет компонентам объявлять свои возможности и обеспечивает разрешение неявных намерений в Android.

Компонент приложения может иметь несколько фильтров намерений, каждый из которых описывает различные возможности. Без фильтров намерений компонент может быть запущен только с помощью явных намерений.

---

## Основы Intent Filter

### Определение

**Фильтр намерений** - это выражение в файле манифеста приложения, которое указывает тип намерений, которые компонент хотел бы получать. Например, объявив фильтр намерений для активности, вы делаете возможным для других приложений напрямую запускать вашу активность с определенным видом намерения. Аналогично, если вы *не* объявляете никаких фильтров намерений для активности, то она может быть запущена только с явным намерением.

### Множественные фильтры

Компонент приложения может иметь любое количество фильтров намерений (определенных элементом `<intent-filter>`), каждый из которых описывает различные возможности этого компонента.

---

## Элемент `<intent-filter>`

### Синтаксис

```xml
<intent-filter android:icon="drawable resource"
               android:label="string resource"
               android:priority="integer"
               android:order="integer"
               android:autoVerify="boolean">
    ...
</intent-filter>
```

### Содержится в

Элемент `<intent-filter>` может быть размещен внутри:
- `<activity>`
- `<activity-alias>`
- `<service>`
- `<receiver>`
- `<provider>`

### Обязательные элементы

- **`<action>`** - Должен содержать хотя бы один элемент action

### Необязательные элементы

- **`<category>`** - Категоризирует намерение
- **`<data>`** - Указывает тип данных и структуру URI

### Атрибуты

#### `android:icon`

Иконка, представляющая родительскую активность, сервис или broadcast receiver, когда этот компонент представляется пользователю как имеющий возможность, описанную фильтром.

Этот атрибут устанавливается как ссылка на drawable ресурс, содержащий определение изображения. Значение по умолчанию - иконка, установленная атрибутом `icon` родительского компонента. Если родитель не указывает иконку, по умолчанию используется иконка элемента `<application>`.

#### `android:label`

Читаемая пользователем метка для родительского компонента. Эта метка, а не установленная родительским компонентом, используется когда компонент представляется пользователю как имеющий возможность, описанную фильтром.

Метка устанавливается как ссылка на строковый ресурс, чтобы её можно было локализовать как другие строки в пользовательском интерфейсе. Однако, для удобства во время разработки приложения, она также может быть установлена как обычная строка.

Значение по умолчанию - метка, установленная родительским компонентом. Если родитель не указывает метку, по умолчанию используется метка атрибута `label` элемента `<application>`.

#### `android:priority`

Приоритет, предоставляемый родительскому компоненту в отношении обработки намерений типа, описанного фильтром. Этот атрибут имеет значение как для активностей, так и для broadcast receivers.

Используйте этот атрибут только если вам нужно установить определенный порядок, в котором получаются broadcasts, или хотите заставить Android предпочесть одну активность другим.

#### `android:order`

Порядок, в котором фильтр обрабатывается, когда совпадает несколько фильтров. `order` отличается от `priority` тем, что `priority` применяется между приложениями, в то время как order устраняет неоднозначность нескольких совпадающих фильтров в одном приложении. Когда могут совпасть несколько фильтров, используйте направленное намерение вместо этого.

**Введен в:** API level 28

#### `android:autoVerify`

Нужно ли Android проверять, что файл Digital Asset Links JSON с указанного хоста соответствует этому приложению. Используется для верификации App Links.

**Введен в:** API level 23

---

## Элемент `<action>`

### Синтаксис

```xml
<action android:name="string" />
```

### Описание

Добавляет действие в фильтр намерений. Элемент `<intent-filter>` должен содержать один или более элементов `<action>`. Если в фильтре намерений нет элементов `<action>`, фильтр не принимает никакие объекты Intent.

### Атрибуты

#### `android:name`

Имя действия. Некоторые стандартные действия определены в классе `Intent` как константы `ACTION_*`. Чтобы назначить одно из этих действий этому атрибуту, добавьте `android.intent.action.` перед строкой, следующей за `ACTION_`.

**Примеры:**
- Для `ACTION_MAIN` используйте `android.intent.action.MAIN`
- Для `ACTION_WEB_SEARCH` используйте `android.intent.action.WEB_SEARCH`
- Для `ACTION_SEND` используйте `android.intent.action.SEND`

**Пользовательские действия:**

Для действий, которые вы определяете, лучше всего использовать имя пакета вашего приложения в качестве префикса для обеспечения уникальности:

```xml
<action android:name="com.example.project.TRANSMOGRIFY" />
```

---

## Элемент `<category>`

### Синтаксис

```xml
<category android:name="string" />
```

### Атрибуты

#### `android:name`

Имя категории. Стандартные категории определены в классе `Intent` как константы `CATEGORY_*`. Имя, назначенное здесь, образуется из этих констант добавлением `android.intent.category.` к имени, следующему за `CATEGORY_`.

**Примеры:**
- Для `CATEGORY_LAUNCHER` используйте `android.intent.category.LAUNCHER`
- Для `CATEGORY_DEFAULT` используйте `android.intent.category.DEFAULT`
- Для `CATEGORY_BROWSABLE` используйте `android.intent.category.BROWSABLE`

**Пользовательские категории:**

Для пользовательских категорий используйте имя пакета в качестве префикса, чтобы они были уникальными.

---

## Элемент `<data>`

### Синтаксис

```xml
<data android:scheme="string"
      android:host="string"
      android:port="string"
      android:path="string"
      android:pathPattern="string"
      android:pathPrefix="string"
      android:pathSuffix="string"
      android:pathAdvancedPattern="string"
      android:mimeType="string" />
```

### Описание

Добавляет спецификацию данных в фильтр намерений. Спецификация может быть:
- Типом данных (используя атрибут `mimeType`)
- URI
- Как типом данных, так и URI

### Структура URI

URI указывается отдельными атрибутами для каждой из его частей:

```
<scheme>://<host>:<port>[<path>|<pathPrefix>|<pathPattern>|<pathAdvancedPattern>|<pathSuffix>]
```

### Зависимости атрибутов URI

Эти атрибуты, которые указывают формат URI, являются необязательными, но также взаимозависимыми:
- Если `scheme` не указана для фильтра намерений, все остальные атрибуты URI игнорируются
- Если `host` не указан для фильтра, атрибут `port` и все атрибуты пути игнорируются

### Множественные элементы данных

Все элементы `<data>`, содержащиеся в одном элементе `<intent-filter>`, вносят вклад в один и тот же фильтр.

**Пример 1:**
```xml
<intent-filter>
    <data android:scheme="something" android:host="project.example.com" />
</intent-filter>
```

**Пример 2 (эквивалентный):**
```xml
<intent-filter>
    <data android:scheme="something" />
    <data android:host="project.example.com" />
</intent-filter>
```

Оба примера эквивалентны. Вы можете разместить любое количество элементов `<data>` внутри `<intent-filter>`, чтобы дать ему несколько вариантов данных. Ни один из его атрибутов не имеет значений по умолчанию.

---

## Примеры фильтров намерений

### Главная активность запуска

```xml
<activity android:name="MainActivity" android:exported="true">
    <!-- Эта активность - основная точка входа, должна появляться в лаунчере приложений -->
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
```

**Объяснение:**
- Действие `ACTION_MAIN` указывает, что это основная точка входа и не ожидает никаких данных намерения
- Категория `CATEGORY_LAUNCHER` указывает, что иконка этой активности должна быть размещена в системном лаунчере приложений
- Эти два элемента должны быть соединены вместе, чтобы активность появилась в лаунчере приложений

### Пример активности Share

```xml
<activity android:name="ShareActivity" android:exported="false">
    <!-- Эта активность обрабатывает действия "SEND" с текстовыми данными -->
    <intent-filter>
        <action android:name="android.intent.action.SEND"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <data android:mimeType="text/plain"/>
    </intent-filter>

    <!-- Эта активность также обрабатывает "SEND" и "SEND_MULTIPLE" с медиа-данными -->
    <intent-filter>
        <action android:name="android.intent.action.SEND"/>
        <action android:name="android.intent.action.SEND_MULTIPLE"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <data android:mimeType="application/vnd.google.panorama360+jpg"/>
        <data android:mimeType="image/*"/>
        <data android:mimeType="video/*"/>
    </intent-filter>
</activity>
```

**Объяснение:**

`ShareActivity` предназначена для облегчения обмена текстовым и медиа-контентом. Хотя пользователи могут войти в эту активность, перейдя к ней из `MainActivity`, они также могут войти в `ShareActivity` напрямую из другого приложения, которое выдает неявное намерение, соответствующее одному из двух фильтров намерений.

---

## Варианты использования Intent Filters

Фильтры намерений в Android имеют различные варианты использования, которые позволяют вашему приложению взаимодействовать с другими приложениями, системными компонентами и обрабатывать различные типы намерений:

### 1. Deep Linking (Глубокие ссылки)

Вы можете использовать фильтры намерений для включения глубоких ссылок в определенные активности вашего приложения. Определив специфическую схему URL и связав её с вашей активностью в фильтре намерений, пользователи могут открыть ваше приложение напрямую из веб-ссылки или другого приложения.

**Пример:**
```xml
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data
        android:scheme="myapp"
        android:host="product"
        android:pathPrefix="/detail" />
</intent-filter>
```

### 2. Обработка неявных намерений

Фильтры намерений позволяют вашему приложению отвечать на неявные намерения, отправленные другими приложениями. Например, если ваше приложение может обрабатывать действие намерения `ACTION_SEND` и тип данных `text/plain`, пользователи могут делиться текстом из других приложений напрямую в ваше приложение.

### 3. Broadcast Receivers (Приемники широковещательных сообщений)

Фильтры намерений обычно используются с `BroadcastReceiver` для прослушивания специфических широковещательных намерений и выполнения соответствующих действий.

**Пример:**
```xml
<receiver android:name=".BatteryReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BATTERY_LOW" />
    </intent-filter>
</receiver>
```

### 4. Открытие специфических типов файлов

Указав типы данных в фильтрах намерений, ваше приложение может обрабатывать запросы на открытие специфических типов файлов, таких как изображения, видео или документы. Пользователи затем могут выбрать ваше приложение в качестве обработчика по умолчанию для этих типов файлов.

**Пример:**
```xml
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <data android:mimeType="image/*" />
</intent-filter>
```

### 5. Обработка URL

Если ваше приложение взаимодействует с специфическими URL или веб-сервисами, вы можете определить фильтр намерений для обработки этих URL, позволяя вашему приложению открывать и обрабатывать данные соответственно.

### 6. Конфигурация виджетов приложения

Фильтры намерений могут использоваться для настройки виджетов приложения. Когда пользователи добавляют виджет вашего приложения на домашний экран, они могут настроить поведение виджета через активность конфигурации, запускаемую через фильтр намерений.

### 7. Действия уведомлений

Когда пользователи взаимодействуют с уведомлением, вы можете использовать фильтры намерений для определения действий, которые должны быть запущены при нажатии на специфические кнопки в уведомлении.

### 8. Неявные вызовы приложения

Фильтры намерений могут позволить вашему приложению обрабатывать специфические системные события или действия.

**Пример:**
```xml
<receiver android:name=".BootReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

### 9. Обмен контентом

Фильтры намерений позволяют вашему приложению быть поставщиком контента для других приложений. Например, если ваше приложение имеет пользовательский контент, другие приложения могут запросить этот контент, используя пользовательское намерение.

### 10. Голосовые действия

Фильтры намерений могут использоваться для обработки голосовых действий, инициированных пользователем, обеспечивая голосовое взаимодействие с вашим приложением.

---

## Лучшие практики

### 1. Всегда включайте CATEGORY_DEFAULT

Для активностей, которые должны получать неявные намерения, всегда включайте категорию `CATEGORY_DEFAULT`:

```xml
<intent-filter>
    <action android:name="android.intent.action.SEND" />
    <category android:name="android.intent.category.DEFAULT" />
    <data android:mimeType="text/plain" />
</intent-filter>
```

### 2. Явно используйте android:exported

Начиная с Android 12 (API level 31), вы должны явно объявлять атрибут `android:exported` для компонентов с фильтрами намерений:

```xml
<activity android:name=".MainActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
```

### 3. Будьте конкретны с типами данных

При фильтрации по MIME-типу будьте максимально конкретны, чтобы избежать непреднамеренных совпадений намерений:

```xml
<!-- Слишком широко -->
<data android:mimeType="*/*" />

<!-- Лучше -->
<data android:mimeType="image/jpeg" />
```

### 4. Используйте autoVerify для App Links

Для HTTPS URL, которые должны открываться напрямую в вашем приложении, используйте `android:autoVerify="true"`:

```xml
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data
        android:scheme="https"
        android:host="www.example.com" />
</intent-filter>
```

---

## Резюме

**Intent Filters (Фильтры намерений):**
- Объявляют возможности компонентов в манифесте
- Обеспечивают разрешение неявных намерений
- Поддерживают глубокие ссылки и app links
- Могут использоваться с активностями, сервисами, broadcast receivers и content providers
- Должны включать хотя бы один элемент `<action>`
- Могут включать несколько элементов `<category>` и `<data>`
- Поддерживают различные варианты использования: глубокие ссылки, обработка файлов, broadcasts, обмен и т.д.

**Ключевые компоненты:**
- `<action>` - Какое действие может выполнять компонент
- `<category>` - Дополнительная информация о компоненте
- `<data>` - Тип данных, которые может обрабатывать компонент (MIME-тип и/или URI)

**Важные атрибуты:**
- `android:priority` - Для упорядочивания между приложениями
- `android:order` - Для упорядочивания внутри одного приложения (API 28+)
- `android:autoVerify` - Для верификации App Links (API 23+)
