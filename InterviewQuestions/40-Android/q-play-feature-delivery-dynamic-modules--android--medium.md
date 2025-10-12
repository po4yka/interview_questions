---
id: q-play-feature-delivery-dynamic-modules--android--medium--1728115380000
title: "Play Feature Delivery and Dynamic Modules / Play Feature Delivery и динамические модули"
topic: android
aliases:
  - Play Feature Delivery and Dynamic Modules
  - Play Feature Delivery и динамические модули
date_created: 2025-10-05
date_modified: 2025-10-05
status: draft
original_language: en
language_tags:
  - en
  - ru
type: question
category: android
difficulty: medium
subtopics:
  - app-bundle
  - play-console
  - architecture-modularization
tags:
  - android
  - play-feature-delivery
  - dynamic-modules
  - app-bundle
  - modularization
  - difficulty/medium
moc: moc-android
source: "https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20Play%20Feature%20Delivery.md"
---

# Play Feature Delivery and Dynamic Modules / Play Feature Delivery и динамические модули

# Question (EN)
> 

What do you know about Play Feature Delivery?

## Answer (EN)
Google Play's app serving model uses Android App Bundles to generate and serve optimized APKs for each user's device configuration, so users download only the code and resources they need to run your app.

Play Feature Delivery uses advanced capabilities of app bundles, allowing certain features of your app to be delivered conditionally or downloaded on demand. To do that, first you need to separate these features from your base app into feature modules.

### Feature Module Build Configuration

When you create a new feature module using Android Studio, the IDE applies the following Gradle plugin to the module's `build.gradle` file:

```groovy
// The following applies the dynamic-feature plugin to your feature module.
// The plugin includes the Gradle tasks and properties required to configure and build
// an app bundle that includes your feature module.

plugins {
  id 'com.android.dynamic-feature'
}
```

Many of the properties available to the standard application plugin are also available to your feature module.

#### What not to include in the feature module build configuration

Because each feature module depends on the base module, it also inherits certain configurations. So, you should omit the following in the feature module's `build.gradle` file:

- **Signing configurations**: App bundles are signed using signing configurations that you specify in the base module
- **The `minifyEnabled` property**: You can enable code shrinking for your entire app project from only the base module's build configuration. So, you should omit this property from feature modules. You can, however, specify additional ProGuard rules for each feature module
- **`versionCode` and `versionName`**: When building your app bundle, Gradle uses app version information that the base module provides. You should omit these properties from your feature module's `build.gradle` file

#### Establish a relationship to the base module

When Android Studio creates your feature module, it makes it visible to the base module by adding the `android.dynamicFeatures` property to the base module's `build.gradle` file:

```groovy
// In the base module's build.gradle file.
android {
    ...
    // Specifies feature modules that have a dependency on
    // this base module.
    dynamicFeatures = [":dynamic_feature", ":dynamic_feature2"]
}
```

Additionally, Android Studio includes the base module as a dependency of the feature module:

```groovy
// In the feature module's build.gradle file:
...
dependencies {
    ...
    // Declares a dependency on the base module, ':app'.
    implementation project(':app')
}
```

### Use Feature Modules for Custom Delivery

A unique benefit of feature modules is the ability to customize how and when different features of your app are downloaded onto devices running Android 5.0 (API level 21) or higher. For example, to reduce the initial download size of your app, you can configure certain features to be either downloaded as needed on demand or only by devices that support certain capabilities, such as the ability to take pictures or support augmented reality features.

Although you get highly optimized downloads by default when you upload your app as an app bundle, the more advanced and customizable feature delivery options require additional configuration and modularization of your app's features using feature modules. That is, feature modules provide the building blocks for creating modular features that you can configure to each be downloaded as needed.

### Example Use Cases

Consider an app that allows your users to buy and sell goods in an online marketplace. You can reasonably modularize each of the following functionalities of the app into separate feature modules:

- Account login and creation
- Browsing the marketplace
- Placing an item for sale
- Processing payments

### Considerations for Feature Modules

With feature modules, you can improve build speed and engineering velocity and extensively customize delivery of your app's features to reduce your app's size. However, there are some constraints and edge cases to keep in mind when using feature modules:

- Installing 50 or more feature modules on a single device, via conditional or on-demand delivery, might lead to performance issues. Install-time modules, which are not configured as removable, are automatically included in the base module and only count as one feature module on each device

- Limit the number of modules you configure as removable for install-time delivery to 10 or fewer. Otherwise, the download and install time of your app might increase

- Only devices running Android 5.0 (API level 21) and higher support downloading and installing features on demand. To make your feature available to earlier versions of Android, enable **Fusing** when you create a feature module

- Enable SplitCompat, so that your app has access to downloaded feature modules that are delivered on demand

- Feature modules should not specify activities in their manifest with `android:exported` set to `true`. That's because there's no guarantee that the device has downloaded the feature module when another app tries to launch the activity. Additionally, your app should confirm that a feature is downloaded before trying to access its code and resources

- Because Play Feature Delivery requires you to publish your app using an app bundle, make sure that you're aware of app bundle known issues

---

# Вопрос (RU)
> 

Что вы знаете о Play Feature Delivery?

## Ответ (RU)
Модель обслуживания приложений Google Play использует Android App Bundles для генерации и предоставления оптимизированных APK для конфигурации устройства каждого пользователя, поэтому пользователи загружают только код и ресурсы, необходимые для запуска вашего приложения.

Play Feature Delivery использует расширенные возможности app bundles, позволяя определенным функциям вашего приложения доставляться условно или загружаться по требованию. Для этого сначала необходимо отделить эти функции от базового приложения в модули функций.

### Конфигурация сборки модуля функций

Когда вы создаете новый модуль функций с помощью Android Studio, IDE применяет следующий плагин Gradle к файлу `build.gradle` модуля:

```groovy
// Следующее применяет плагин dynamic-feature к вашему модулю функций.
// Плагин включает задачи Gradle и свойства, необходимые для настройки и сборки
// app bundle, который включает ваш модуль функций.

plugins {
  id 'com.android.dynamic-feature'
}
```

Многие свойства, доступные для стандартного плагина приложения, также доступны для вашего модуля функций.

#### Что не следует включать в конфигурацию сборки модуля функций

Поскольку каждый модуль функций зависит от базового модуля, он также наследует определенные конфигурации. Поэтому вы должны опустить следующее в файле `build.gradle` модуля функций:

- **Конфигурации подписи**: App bundles подписываются с использованием конфигураций подписи, которые вы указываете в базовом модуле
- **Свойство `minifyEnabled`**: Вы можете включить сокращение кода для всего проекта приложения только из конфигурации сборки базового модуля. Поэтому вы должны опустить это свойство из модулей функций. Однако вы можете указать дополнительные правила ProGuard для каждого модуля функций
- **`versionCode` и `versionName`**: При сборке вашего app bundle Gradle использует информацию о версии приложения, которую предоставляет базовый модуль. Вы должны опустить эти свойства из файла `build.gradle` вашего модуля функций

#### Установка связи с базовым модулем

Когда Android Studio создает ваш модуль функций, он делает его видимым для базового модуля, добавляя свойство `android.dynamicFeatures` в файл `build.gradle` базового модуля:

```groovy
// В файле build.gradle базового модуля.
android {
    ...
    // Указывает модули функций, которые имеют зависимость от
    // этого базового модуля.
    dynamicFeatures = [":dynamic_feature", ":dynamic_feature2"]
}
```

Кроме того, Android Studio включает базовый модуль в качестве зависимости модуля функций:

```groovy
// В файле build.gradle модуля функций:
...
dependencies {
    ...
    // Объявляет зависимость от базового модуля ':app'.
    implementation project(':app')
}
```

### Использование модулей функций для пользовательской доставки

Уникальное преимущество модулей функций - это возможность настраивать, как и когда различные функции вашего приложения загружаются на устройства под управлением Android 5.0 (уровень API 21) или выше. Например, чтобы уменьшить начальный размер загрузки вашего приложения, вы можете настроить определенные функции для загрузки по требованию или только устройствами, которые поддерживают определенные возможности, такие как возможность фотографировать или поддержка функций дополненной реальности.

Хотя вы получаете высоко оптимизированные загрузки по умолчанию, когда загружаете свое приложение как app bundle, более продвинутые и настраиваемые параметры доставки функций требуют дополнительной конфигурации и модуляризации функций вашего приложения с использованием модулей функций. То есть модули функций предоставляют строительные блоки для создания модульных функций, которые вы можете настроить для загрузки по мере необходимости.

### Примеры использования

Рассмотрим приложение, которое позволяет вашим пользователям покупать и продавать товары на онлайн-рынке. Вы можете разумно модуляризировать каждую из следующих функций приложения в отдельные модули функций:

- Вход в учетную запись и создание
- Просмотр рынка
- Размещение товара на продажу
- Обработка платежей

### Соображения относительно модулей функций

С помощью модулей функций вы можете улучшить скорость сборки и скорость разработки, а также обширно настроить доставку функций вашего приложения для уменьшения размера приложения. Однако есть некоторые ограничения и граничные случаи, которые следует учитывать при использовании модулей функций:

- Установка 50 или более модулей функций на одно устройство через условную доставку или доставку по требованию может привести к проблемам с производительностью. Модули времени установки, которые не настроены как удаляемые, автоматически включаются в базовый модуль и считаются только как один модуль функций на каждом устройстве

- Ограничьте количество модулей, которые вы настраиваете как удаляемые для доставки во время установки, до 10 или меньше. В противном случае время загрузки и установки вашего приложения может увеличиться

- Только устройства под управлением Android 5.0 (уровень API 21) и выше поддерживают загрузку и установку функций по требованию. Чтобы сделать вашу функцию доступной для более ранних версий Android, включите **Fusing** при создании модуля функций

- Включите SplitCompat, чтобы ваше приложение имело доступ к загруженным модулям функций, которые доставляются по требованию

- Модули функций не должны указывать активности в своем манифесте с `android:exported`, установленным в `true`. Это потому, что нет гарантии, что устройство загрузило модуль функций, когда другое приложение пытается запустить активность. Кроме того, ваше приложение должно подтвердить, что функция загружена, прежде чем пытаться получить доступ к ее коду и ресурсам

- Поскольку Play Feature Delivery требует публикации вашего приложения с использованием app bundle, убедитесь, что вы знаете об известных проблемах app bundle
