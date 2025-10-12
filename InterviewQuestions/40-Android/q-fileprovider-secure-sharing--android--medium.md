---
id: q-fileprovider-secure-sharing--android--medium--1728115200000
title: "FileProvider for Secure File Sharing / FileProvider для безопасного обмена файлами"
topic: android
aliases:
  - FileProvider for Secure File Sharing
  - FileProvider для безопасного обмена файлами
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
  - content-provider
  - permissions
  - files-media
tags:
  - android
  - fileprovider
  - content-provider
  - file-sharing
  - security
  - difficulty/medium
moc: moc-android
source: "https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20FileProvider.md"
---

# FileProvider for Secure File Sharing / FileProvider для безопасного обмена файлами

# Question (EN)
> 

What do you know about FileProvider?

## Answer (EN)
`FileProvider` is a special subclass of `ContentProvider` that facilitates secure sharing of files associated with an app by creating a `content://` `Uri` for a file instead of a `file:///` `Uri`.

A content URI allows you to grant read and write access using temporary access permissions. When you create an `Intent` containing a content URI, in order to send the content URI to a client app, you can also call `Intent.setFlags()` to add permissions. These permissions are available to the client app for as long as the stack for a receiving `Activity` is active. For an `Intent` going to a `Service`, the permissions are available as long as the `Service` is running.

In comparison, to control access to a `file:///` `Uri` you have to modify the file system permissions of the underlying file. The permissions you provide become available to *any* app, and remain in effect until you change them. This level of access is fundamentally insecure.

The increased level of file access security offered by a content URI makes `FileProvider` a key part of Android's security infrastructure.

### Defining a FileProvider

Since the default functionality of `FileProvider` includes content URI generation for files, you don't need to define a subclass in code. Instead, you can include a `FileProvider` in your app by specifying it entirely in XML. To specify the `FileProvider` component itself, add a `<provider>` element to your app manifest. Set the `android:name` attribute to `androidx.core.content.FileProvider`. Set the `android:authorities` attribute to a URI authority based on a domain you control; for example, if you control the domain `mydomain.com` you should use the authority `com.mydomain.fileprovider`. Set the `android:exported` attribute to `false`; the `FileProvider` does not need to be public. Set the `android:grantUriPermissions` attribute to `true`, to allow you to grant temporary access to files.

Example:

```xml
<manifest>
    ...
    <application>
        ...
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="com.mydomain.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            ...
        </provider>
        ...
    </application>
</manifest>
```

### Specifying Available Files

A `FileProvider` can only generate a content `URI` for files in directories that you specify beforehand. To specify a directory, specify its storage area and path in XML, using child elements of the `<paths>` element. For example, the following `paths` element tells FileProvider that you intend to request content URIs for the `images/` subdirectory of your private file area.

```xml
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <files-path name="my_images" path="images/"/>
    ...
</paths>
```

The `<paths>` element must contain one or more of the following child elements:

```xml
<files-path name="name" path="path" />
```

These child elements all use the same attributes:

- `name="name"` - A URI path segment. To enforce security, this value hides the name of the subdirectory you're sharing. The subdirectory name for this value is contained in the `path` attribute.
- `path="path"` - The subdirectory you're sharing. While the `name` attribute is a URI path segment, the `path` value is an actual subdirectory name. Notice that the value refers to a **subdirectory**, not an individual file or files. You can't share a single file by its file name, nor can you specify a subset of files using wildcards.

You must specify a child element of `<paths>` for each directory that contains files for which you want content URIs.

### Generating the Content URI for a File

To share a file with another app using a content URI, your app has to generate the content URI. To generate the content URI, create a new `File` for the file, then pass the `File` to `getUriForFile()`. You can send the content URI returned by `getUriForFile()` to another app in an `Intent`. The client app that receives the content URI can open the file and access its contents by calling `ContentResolver.openFileDescriptor` to get a `ParcelFileDescriptor`.

For example, suppose your app is offering files to other apps with a `FileProvider` that has the authority `com.mydomain.fileprovider`. To get a content URI for the file `default_image.jpg` in the `images/` subdirectory of your internal storage:

```kotlin
File imagePath = new File(Context.getFilesDir(), "images");
File newFile = new File(imagePath, "default_image.jpg");
Uri contentUri = getUriForFile(getContext(), "com.mydomain.fileprovider", newFile);
```

As a result of the previous snippet, `getUriForFile()` returns the content URI `content://com.mydomain.fileprovider/my_images/default_image.jpg`.

### Granting Temporary Permissions to a URI

To grant an access permission to a content URI returned from `getUriForFile()`, you can either grant the permission to a specific package or include the permission in an intent.

#### Grant Permission to a Specific Package

Call the method `Context.grantUriPermission(package, Uri, mode_flags)` for the `content://` `Uri`, using the desired mode flags. This grants temporary access permission for the content URI to the specified package, according to the value of the the `mode_flags` parameter, which you can set to `Intent.FLAG_GRANT_READ_URI_PERMISSION`, `Intent.FLAG_GRANT_WRITE_URI_PERMISSION` or both. The permission remains in effect until you revoke it by calling `revokeUriPermission()` or until the device reboots.

#### Include the Permission in an Intent

To allow the user to choose which app receives the intent, and the permission to access the content, do the following:

- Put the content URI in an `Intent` by calling `setData()`
- Call the method `Intent.setFlags()` with either `Intent.FLAG_GRANT_READ_URI_PERMISSION` or `Intent.FLAG_GRANT_WRITE_URI_PERMISSION` or both
- Send the `Intent` to another app. Most often, you do this by calling `setResult()`

Permissions granted in an `Intent` remain in effect while the stack of the receiving `Activity` is active. When the stack finishes, the permissions are automatically removed. Permissions granted to one `Activity` in a client app are automatically extended to other components of that app.

---

# Вопрос (RU)
> 

Что вы знаете о FileProvider?

## Ответ (RU)
`FileProvider` - это специальный подкласс `ContentProvider`, который облегчает безопасный обмен файлами, связанными с приложением, путем создания `content://` `Uri` для файла вместо `file:///` `Uri`.

Content URI позволяет предоставлять доступ на чтение и запись с использованием временных разрешений доступа. Когда вы создаете `Intent`, содержащий content URI, для отправки content URI клиентскому приложению, вы также можете вызвать `Intent.setFlags()` для добавления разрешений. Эти разрешения доступны клиентскому приложению до тех пор, пока активен стек принимающей `Activity`. Для `Intent`, направленного в `Service`, разрешения доступны до тех пор, пока работает `Service`.

Для сравнения, чтобы управлять доступом к `file:///` `Uri`, вам необходимо изменить права доступа файловой системы базового файла. Предоставленные вами разрешения становятся доступными *любому* приложению и остаются в силе до тех пор, пока вы их не измените. Такой уровень доступа по своей сути небезопасен.

Повышенный уровень безопасности доступа к файлам, обеспечиваемый content URI, делает `FileProvider` ключевой частью инфраструктуры безопасности Android.

### Определение FileProvider

Поскольку функциональность `FileProvider` по умолчанию включает генерацию content URI для файлов, вам не нужно определять подкласс в коде. Вместо этого вы можете включить `FileProvider` в свое приложение, полностью определив его в XML. Чтобы указать сам компонент `FileProvider`, добавьте элемент `<provider>` в манифест вашего приложения. Установите атрибут `android:name` в `androidx.core.content.FileProvider`. Установите атрибут `android:authorities` в URI authority на основе контролируемого вами домена; например, если вы контролируете домен `mydomain.com`, вы должны использовать authority `com.mydomain.fileprovider`. Установите атрибут `android:exported` в `false`; `FileProvider` не должен быть публичным. Установите атрибут `android:grantUriPermissions` в `true`, чтобы иметь возможность предоставлять временный доступ к файлам.

Пример:

```xml
<manifest>
    ...
    <application>
        ...
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="com.mydomain.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            ...
        </provider>
        ...
    </application>
</manifest>
```

### Указание доступных файлов

`FileProvider` может генерировать content `URI` только для файлов в каталогах, которые вы заранее указали. Чтобы указать каталог, укажите его область хранения и путь в XML, используя дочерние элементы элемента `<paths>`. Например, следующий элемент `paths` сообщает FileProvider, что вы намерены запрашивать content URI для подкаталога `images/` вашей частной файловой области.

```xml
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <files-path name="my_images" path="images/"/>
    ...
</paths>
```

Элемент `<paths>` должен содержать один или несколько следующих дочерних элементов:

```xml
<files-path name="name" path="path" />
```

Эти дочерние элементы используют одинаковые атрибуты:

- `name="name"` - Сегмент пути URI. Для обеспечения безопасности это значение скрывает имя подкаталога, которым вы делитесь. Имя подкаталога для этого значения содержится в атрибуте `path`.
- `path="path"` - Подкаталог, которым вы делитесь. Хотя атрибут `name` является сегментом пути URI, значение `path` - это фактическое имя подкаталога. Обратите внимание, что значение относится к **подкаталогу**, а не к отдельному файлу или файлам. Вы не можете поделиться одним файлом по его имени и не можете указать подмножество файлов с использованием подстановочных знаков.

Вы должны указать дочерний элемент `<paths>` для каждого каталога, содержащего файлы, для которых вам нужны content URI.

### Генерация Content URI для файла

Чтобы поделиться файлом с другим приложением с использованием content URI, ваше приложение должно сгенерировать content URI. Чтобы сгенерировать content URI, создайте новый `File` для файла, затем передайте `File` в `getUriForFile()`. Вы можете отправить content URI, возвращенный `getUriForFile()`, другому приложению в `Intent`. Клиентское приложение, получившее content URI, может открыть файл и получить доступ к его содержимому, вызвав `ContentResolver.openFileDescriptor` для получения `ParcelFileDescriptor`.

Например, предположим, что ваше приложение предлагает файлы другим приложениям с `FileProvider`, имеющим authority `com.mydomain.fileprovider`. Чтобы получить content URI для файла `default_image.jpg` в подкаталоге `images/` вашего внутреннего хранилища:

```kotlin
File imagePath = new File(Context.getFilesDir(), "images");
File newFile = new File(imagePath, "default_image.jpg");
Uri contentUri = getUriForFile(getContext(), "com.mydomain.fileprovider", newFile);
```

В результате предыдущего фрагмента `getUriForFile()` возвращает content URI `content://com.mydomain.fileprovider/my_images/default_image.jpg`.

### Предоставление временных разрешений для URI

Чтобы предоставить разрешение на доступ к content URI, возвращенному из `getUriForFile()`, вы можете либо предоставить разрешение конкретному пакету, либо включить разрешение в intent.

#### Предоставление разрешения конкретному пакету

Вызовите метод `Context.grantUriPermission(package, Uri, mode_flags)` для `content://` `Uri`, используя желаемые флаги режима. Это предоставляет временное разрешение на доступ для content URI указанному пакету в соответствии со значением параметра `mode_flags`, который вы можете установить в `Intent.FLAG_GRANT_READ_URI_PERMISSION`, `Intent.FLAG_GRANT_WRITE_URI_PERMISSION` или оба. Разрешение остается в силе до тех пор, пока вы не отзовете его, вызвав `revokeUriPermission()`, или пока устройство не перезагрузится.

#### Включение разрешения в Intent

Чтобы позволить пользователю выбрать, какое приложение получит intent и разрешение на доступ к контенту, сделайте следующее:

- Поместите content URI в `Intent`, вызвав `setData()`
- Вызовите метод `Intent.setFlags()` с `Intent.FLAG_GRANT_READ_URI_PERMISSION` или `Intent.FLAG_GRANT_WRITE_URI_PERMISSION` или обоими
- Отправьте `Intent` другому приложению. Чаще всего это делается путем вызова `setResult()`

Разрешения, предоставленные в `Intent`, остаются в силе, пока активен стек принимающей `Activity`. Когда стек завершается, разрешения автоматически удаляются. Разрешения, предоставленные одной `Activity` в клиентском приложении, автоматически распространяются на другие компоненты этого приложения.
