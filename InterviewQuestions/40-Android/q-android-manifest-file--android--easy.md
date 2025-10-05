---
id: android-manifest-file-1730794000000
title: AndroidManifest.xml / AndroidManifest.xml
language_tags:
  - en
  - ru
original_language: en
status: draft
moc: moc-android
tags:
  - android
  - manifest
  - androidmanifest
  - configuration
  - app-structure
  - difficulty/easy
subtopics:
  - app-startup
  - permissions
  - activity
difficulty: easy
source: https://github.com/Kirchhoff-/Android-Interview-Questions
---

# AndroidManifest.xml / AndroidManifest.xml

**English**: What is AndroidManifest?

**Русский**: Что такое AndroidManifest?

## Answer

**English**:

The **AndroidManifest.xml** file contains information of your package, including components of the application such as activities, services, broadcast receivers, content providers, etc.

### Responsibilities

The AndroidManifest.xml file has several important responsibilities:

- **Protect the application** to access any protected parts by providing the permissions.
- **Declares the Android API** that the application is going to use.
- **Declares lists the instrumentation classes**. The instrumentation classes provide profiling and other information.
- **Specify whether app should be installed** on an SD card or the internal memory.

### Important Nodes

#### uses-sdk

It is used to define a minimum and maximum SDK version that must be available on a device so that our application functions properly. However, beware that attributes in the `<uses-sdk>` element are overridden by corresponding properties in the `build.gradle` file.

```xml
<uses-sdk
    android:minSdkVersion="21"
    android:targetSdkVersion="33" />
```

#### uses-configuration

The uses-configuration nodes are used to specify the combination of input mechanisms that are supported by our application.

```xml
<uses-configuration
    android:reqHardKeyboard="true"
    android:reqKeyboardType="qwerty" />
```

#### uses-features

It is used to specify which hardware and software features your app needs.

```xml
<uses-feature
    android:name="android.hardware.camera"
    android:required="true" />
```

#### supports-screens

It is used to describe the screen support for application.

```xml
<supports-screens
    android:smallScreens="true"
    android:normalScreens="true"
    android:largeScreens="true"
    android:xlargeScreens="true" />
```

#### permission

It is used to create permissions to restrict access to shared application components. Also used the existing platform permissions for this purpose or define your own permissions in the manifest.

```xml
<permission
    android:name="com.example.app.CUSTOM_PERMISSION"
    android:protectionLevel="signature" />

<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.CAMERA" />
```

#### application

The declaration of the application. This element contains subelements that declare each of the application's components (such as Activity, Service, Content Provider, and Broadcast Receiver) and has attributes that can affect all the components.

```xml
<application
    android:allowBackup="true"
    android:icon="@mipmap/ic_launcher"
    android:label="@string/app_name"
    android:theme="@style/AppTheme">

    <activity
        android:name=".MainActivity"
        android:exported="true">
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>

    <service android:name=".MyService" />

    <receiver android:name=".MyBroadcastReceiver" />

    <provider
        android:name=".MyContentProvider"
        android:authorities="com.example.app.provider" />
</application>
```

**Русский**:

Файл **AndroidManifest.xml** содержит информацию о вашем пакете, включая компоненты приложения, такие как activities, services, broadcast receivers, content providers и т.д.

### Обязанности

Файл AndroidManifest.xml имеет несколько важных обязанностей:

- **Защита приложения** для доступа к любым защищенным частям путем предоставления разрешений.
- **Объявляет Android API**, который приложение собирается использовать.
- **Объявляет классы инструментирования**. Классы инструментирования предоставляют профилирование и другую информацию.
- **Указывает, следует ли устанавливать приложение** на SD-карту или во внутреннюю память.

### Важные узлы

#### uses-sdk

Используется для определения минимальной и максимальной версии SDK, которая должна быть доступна на устройстве, чтобы наше приложение функционировало правильно. Однако имейте в виду, что атрибуты в элементе `<uses-sdk>` переопределяются соответствующими свойствами в файле `build.gradle`.

```xml
<uses-sdk
    android:minSdkVersion="21"
    android:targetSdkVersion="33" />
```

#### uses-configuration

Узлы uses-configuration используются для указания комбинации механизмов ввода, которые поддерживаются нашим приложением.

```xml
<uses-configuration
    android:reqHardKeyboard="true"
    android:reqKeyboardType="qwerty" />
```

#### uses-features

Используется для указания, какие аппаратные и программные функции нужны вашему приложению.

```xml
<uses-feature
    android:name="android.hardware.camera"
    android:required="true" />
```

#### supports-screens

Используется для описания поддержки экранов для приложения.

```xml
<supports-screens
    android:smallScreens="true"
    android:normalScreens="true"
    android:largeScreens="true"
    android:xlargeScreens="true" />
```

#### permission

Используется для создания разрешений для ограничения доступа к общим компонентам приложения. Также используются существующие разрешения платформы для этой цели или определите свои собственные разрешения в манифесте.

```xml
<permission
    android:name="com.example.app.CUSTOM_PERMISSION"
    android:protectionLevel="signature" />

<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.CAMERA" />
```

#### application

Объявление приложения. Этот элемент содержит подэлементы, которые объявляют каждый из компонентов приложения (таких как Activity, Service, Content Provider и Broadcast Receiver) и имеет атрибуты, которые могут влиять на все компоненты.

```xml
<application
    android:allowBackup="true"
    android:icon="@mipmap/ic_launcher"
    android:label="@string/app_name"
    android:theme="@style/AppTheme">

    <activity
        android:name=".MainActivity"
        android:exported="true">
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>

    <service android:name=".MyService" />

    <receiver android:name=".MyBroadcastReceiver" />

    <provider
        android:name=".MyContentProvider"
        android:authorities="com.example.app.provider" />
</application>
```

## References

- [App Manifest Overview](https://developer.android.com/guide/topics/manifest/manifest-intro)
- [Application Manifest File Android](https://www.geeksforgeeks.org/application-manifest-file-android/)
