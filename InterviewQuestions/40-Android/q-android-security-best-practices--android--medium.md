---
topic: android
tags:
  - android
  - security
  - best-practices
  - encryption
  - ssl
  - webview
  - difficulty/medium
subtopics:
  - permissions
  - keystore-crypto
  - network-security-config
difficulty: medium
status: reviewed
source: https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20security%20best%20practices%20you%20know.md
---

# Android Security Best Practices / Лучшие практики безопасности Android

**English**: What security best practices do you know?

**Russian**: Какие лучшие практики безопасности вы знаете?

## Answer

## Show an app chooser

If an implicit intent can launch at least two possible apps on a user's device, explicitly show an app chooser. This interaction strategy allows users to transfer sensitive information to an app that they trust.

```kotlin
val intent = Intent(ACTION_SEND)
val possibleActivitiesList: List<ResolveInfo> =
        queryIntentActivities(intent, PackageManager.MATCH_ALL)

// Verify that an activity in at least two apps on the user's device
// can handle the intent. Otherwise, start the intent only if an app
// on the user's device can handle the intent.
if (possibleActivitiesList.size > 1) {

    // Create intent to show chooser.
    // Title is something similar to "Share this photo with".

    val chooser = resources.getString(R.string.chooser_title).let { title ->
        Intent.createChooser(intent, title)
    }
    startActivity(chooser)
} else if (intent.resolveActivity(packageManager) != null) {
    startActivity(intent)
}
```

## Apply signature-based permissions

When sharing data between two apps that you control or own, use *signature-based* permissions. These permissions don't require user confirmation and instead check that the apps accessing the data are signed using the same signing key. Therefore, these permissions offer a more streamlined, secure user experience.

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">
    <permission android:name="my_custom_permission_name"
                android:protectionLevel="signature" />
</manifest>
```

## Disallow access to your app's content providers

Unless you intend to send data from your app to a different app that you don't own, you should explicitly disallow other developers' apps from accessing the `ContentProvider` objects that your app contains. This setting is particularly important if your app can be installed on devices running Android 4.1.1 (API level 16) or lower, as the `android:exported` attribute of the `<provider>` element is `true` by default on those versions of Android.

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">
    <application ... >
        <provider
            android:name="android.support.v4.content.FileProvider"
            android:authorities="com.example.myapp.fileprovider"
            ...
            android:exported="false">
            <!-- Place child elements of <provider> here. -->
        </provider>
        ...
    </application>
</manifest>
```

## Use SSL traffic

If your app communicates with a web server that has a certificate issued by a well-known, trusted CA, the HTTPS request is very simple:

```kotlin
val url = URL("https://www.google.com")
val urlConnection = url.openConnection() as HttpsURLConnection
urlConnection.connect()
urlConnection.inputStream.use {
    ...
}
```

## Add a network security configuration

If your app uses new or custom CAs, you can declare your network's security settings in a configuration file. This process allows you to create the configuration without modifying any app code.

To add a network security configuration file to your app, follow these steps:

### 1. Declare the configuration in your app's manifest:

```xml
<manifest ... >
    <application
        android:networkSecurityConfig="@xml/network_security_config"
        ... >
        <!-- Place child elements of <application> element here. -->
    </application>
</manifest>
```

### 2. Add an XML resource file

Located at `res/xml/network_security_config.xml`. Specify that all traffic to particular domains should use HTTPS by disabling clear-text:

```xml
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">secure.example.com</domain>
        ...
    </domain-config>
</network-security-config>
```

## Create your own trust manager

Your SSL checker shouldn't accept every certificate. You may need to set up a trust manager and handle all SSL warnings that occur if one of the following conditions applies to your use case:

- You're communicating with a web server that has a certificate signed by a new or custom CA.
- That CA isn't trusted by the device you're using.
- You cannot use a network security configuration.

## WebView

Whenever possible, load only allowlisted content in `WebView` objects. In other words, the `WebView` objects in your app shouldn't allow users to navigate to sites that are outside of your control.

In addition, you should never enable JavaScript interface support unless you completely control and trust the content in your app's `WebView` objects.

If your app must use JavaScript interface support on devices running Android 6.0 (API level 23) and higher, use HTML message channels instead to communicate between a website and your app, as shown in the following code snippet:

```kotlin
val myWebView: WebView = findViewById(R.id.webview)

// messagePorts[0] and messagePorts[1] represent the two ports.
// They are already tangled to each other and have been started.
val channel: Array<out WebMessagePort> = myWebView.createWebMessageChannel()

// Create handler for channel[0] to receive messages.
channel[0].setWebMessageCallback(object : WebMessagePort.WebMessageCallback() {

    override fun onMessage(port: WebMessagePort, message: WebMessage) {
        Log.d(TAG, "On port $port, received this message: $message")
    }
})

// Send a message from channel[1] to channel[0].
channel[1].postMessage(WebMessage("My secure message"))
```

## User data

### Store private data within internal storage

Store all private user data within the device's internal storage, which is sandboxed per app. Your app doesn't need to request permission to view these files, and other apps cannot access the files. As an added security measure, when the user uninstalls an app, the device deletes all files that the app saved within internal storage.

### Store data in external storage based on use case

Use external storage for large, non-sensitive files that are specific to your app, as well as files that your app shares with other apps.

### Check validity of data

If your app uses data from external storage, make sure that the contents of the data haven't been corrupted or modified. Your app should also include logic to handle files that are no longer in a stable format.

### Store only non-sensitive data in cache files

To provide quicker access to non-sensitive app data, store it in the device's cache. For caches larger than 1 MB in size, use `getExternalCacheDir()`; otherwise, use `getCacheDir()`. Each method provides you with the `File` object that contains your app's cached data.

### Use SharedPreferences in private mode

When using `getSharedPreferences()` to create or access your app's `SharedPreferences` objects, use `MODE_PRIVATE`. That way, only your app can access the information within the shared preferences file.

## Other Best Practices

### Code Obfuscation

Protect the source code by making it unintelligible for both humans and decompiler. All this, while preserving its entire operations during the compilation. The purpose of the obfuscation process is to give an impenetrable code. It promotes the confidentiality of all intellectual properties against reverse engineering.

### Data encryption

Mobile app security involves securing all kinds of stored data on the mobile device. It includes the source code as well as the data transmitted between the application and the back-end server. The execution of certificate pinning helps affirm the backend Web service certificate for the application. High-level data encryption is one of the best android mobile app security practices. It protects the valuable data from hackers.

### Regular Updation And Testing

Hackers detect vulnerabilities in software and exploit, while developers repair the breach, which causes hackers to discover another weakness. Although Google cannot avoid the development of these vulnerabilities, it effectively updates the Android OS to counter the detected problems. However, these measures will not be useful if the software is not up-to-date. Penetration testing is another method for server-side checks.

## Ответ

## Показать выбор приложения

Если неявный intent может запустить как минимум два возможных приложения на устройстве пользователя, явно покажите выбор приложения. Эта стратегия взаимодействия позволяет пользователям передавать конфиденциальную информацию в приложение, которому они доверяют.

```kotlin
val intent = Intent(ACTION_SEND)
val possibleActivitiesList: List<ResolveInfo> =
        queryIntentActivities(intent, PackageManager.MATCH_ALL)

if (possibleActivitiesList.size > 1) {
    val chooser = resources.getString(R.string.chooser_title).let { title ->
        Intent.createChooser(intent, title)
    }
    startActivity(chooser)
} else if (intent.resolveActivity(packageManager) != null) {
    startActivity(intent)
}
```

## Применение разрешений на основе подписи

При обмене данными между двумя приложениями, которыми вы управляете или владеете, используйте разрешения на основе *подписи*. Эти разрешения не требуют подтверждения пользователя и вместо этого проверяют, что приложения, получающие доступ к данным, подписаны одним и тем же ключом подписи.

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">
    <permission android:name="my_custom_permission_name"
                android:protectionLevel="signature" />
</manifest>
```

## Запрет доступа к контент-провайдерам приложения

Если вы не собираетесь отправлять данные из своего приложения в другое приложение, которым вы не владеете, вы должны явно запретить другим приложениям разработчиков доступ к объектам `ContentProvider`, которые содержит ваше приложение.

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">
    <application ... >
        <provider
            android:name="android.support.v4.content.FileProvider"
            android:authorities="com.example.myapp.fileprovider"
            ...
            android:exported="false">
        </provider>
        ...
    </application>
</manifest>
```

## Использование SSL трафика

Если ваше приложение взаимодействует с веб-сервером, имеющим сертификат, выданный известным, доверенным CA, HTTPS запрос очень прост:

```kotlin
val url = URL("https://www.google.com")
val urlConnection = url.openConnection() as HttpsURLConnection
urlConnection.connect()
urlConnection.inputStream.use {
    ...
}
```

## Добавление конфигурации сетевой безопасности

Если ваше приложение использует новые или пользовательские CA, вы можете объявить настройки безопасности сети в файле конфигурации.

### 1. Объявите конфигурацию в манифесте:

```xml
<manifest ... >
    <application
        android:networkSecurityConfig="@xml/network_security_config"
        ... >
    </application>
</manifest>
```

### 2. Добавьте XML файл ресурсов

Расположенный в `res/xml/network_security_config.xml`:

```xml
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">secure.example.com</domain>
        ...
    </domain-config>
</network-security-config>
```

## WebView

По возможности загружайте в объекты `WebView` только разрешенный контент. Другими словами, объекты `WebView` в вашем приложении не должны позволять пользователям переходить на сайты, которые находятся вне вашего контроля.

Кроме того, вы никогда не должны включать поддержку интерфейса JavaScript, если вы полностью не контролируете и не доверяете контенту в объектах `WebView` вашего приложения.

Для устройств на Android 6.0 (API уровень 23) и выше используйте HTML каналы сообщений для связи между веб-сайтом и вашим приложением:

```kotlin
val myWebView: WebView = findViewById(R.id.webview)
val channel: Array<out WebMessagePort> = myWebView.createWebMessageChannel()

channel[0].setWebMessageCallback(object : WebMessagePort.WebMessageCallback() {
    override fun onMessage(port: WebMessagePort, message: WebMessage) {
        Log.d(TAG, "On port $port, received this message: $message")
    }
})

channel[1].postMessage(WebMessage("My secure message"))
```

## Пользовательские данные

### Хранение приватных данных во внутреннем хранилище

Храните все приватные пользовательские данные во внутреннем хранилище устройства, которое изолировано для каждого приложения. Вашему приложению не нужно запрашивать разрешение для просмотра этих файлов, и другие приложения не могут получить доступ к файлам.

### Хранение данных во внешнем хранилище в зависимости от варианта использования

Используйте внешнее хранилище для больших, неконфиденциальных файлов, специфичных для вашего приложения, а также для файлов, которыми ваше приложение делится с другими приложениями.

### Проверка достоверности данных

Если ваше приложение использует данные из внешнего хранилища, убедитесь, что содержимое данных не было повреждено или изменено.

### Хранение только неконфиденциальных данных в файлах кеша

Для быстрого доступа к неконфиденциальным данным приложения храните их в кеше устройства. Для кешей размером более 1 МБ используйте `getExternalCacheDir()`; в противном случае используйте `getCacheDir()`.

### Использование SharedPreferences в приватном режиме

При использовании `getSharedPreferences()` для создания или доступа к объектам `SharedPreferences` вашего приложения используйте `MODE_PRIVATE`. Таким образом, только ваше приложение может получить доступ к информации в файле общих настроек.

## Другие лучшие практики

### Обфускация кода

Защитите исходный код, сделав его непонятным как для людей, так и для декомпилятора, сохраняя при этом все его операции во время компиляции. Цель процесса обфускации - дать непроницаемый код. Это способствует конфиденциальности всей интеллектуальной собственности от обратной разработки.

### Шифрование данных

Безопасность мобильного приложения включает защиту всех видов сохраненных данных на мобильном устройстве. Это включает исходный код, а также данные, передаваемые между приложением и серверной частью. Высокоуровневое шифрование данных - одна из лучших практик безопасности мобильных приложений Android.

### Регулярное обновление и тестирование

Хакеры обнаруживают уязвимости в программном обеспечении и эксплуатируют их, в то время как разработчики исправляют брешь, что заставляет хакеров обнаруживать другую слабость. Тестирование на проникновение - еще один метод для проверок на стороне сервера.

## Links

- [Android Security Best Practices](https://developer.android.com/topic/security/best-practices)
- [Security Tips](https://developer.android.com/training/articles/security-tips)
- [Android App Security Best Practices - RishabhSoft](https://www.rishabhsoft.com/blog/android-app-security-best-practices)
- [Android App Security Best Practices - QuickBird Studios](https://quickbirdstudios.com/blog/android-app-security-best-practices/)
