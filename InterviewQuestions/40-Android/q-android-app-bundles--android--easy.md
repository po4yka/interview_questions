---
id: 20251005-143000
title: "Android App Bundles / Android App Bundle (AAB)"
original_language: en
language_tags: [en, ru]
moc: moc-android
tags:
  - android
  - app-bundle
  - play-store
  - distribution
  - difficulty/easy
subtopics:
  - app-bundle
  - play-console
status: draft
created: 2025-10-05
modified: 2025-10-05
source: https://github.com/Kirchhoff-/Android-Interview-Questions
---

# Android App Bundles / Android App Bundle (AAB)

## Question (EN)
What do you know about App Bundles?

## Answer (EN)

### App Bundles
An *Android App Bundle* is a publishing format that includes all your app's compiled code and resources, and defers APK generation and signing to Google Play.

Google Play uses your app bundle to generate and serve optimized APKs for each device configuration, so only the code and resources that are needed for a specific device are downloaded to run your app. You no longer have to build, sign, and manage multiple APKs to optimize support for different devices, and users get smaller, more-optimized downloads.

When you use the app bundle format to publish your app, you can also optionally take advantage of [Play Feature Delivery](https://developer.android.com/guide/playcore/feature-delivery), which allows you to add *feature modules* to your app project. These modules contain features and resources that are only included with your app based on conditions that you specify, or are available later at runtime for download [Using the Play Core Library](https://developer.android.com/guide/playcore).

### What's the difference between AABs and APKs?
App bundles are only for publishing and cannot be installed on Android devices. The Android package (APK) is Android's installable, executable format for apps. App bundles must be processed by a distributor into APKs so that they can be installed on devices.

| APK | AAB |
|---|---|
| Upload to Google Play and install directly on devices | Upload to Google Play only |
| No reduction in download size via dynamic delivery | Supports dynamic delivery |
| Supports developer or Google signing | Google signing only |

### Compressed download size restriction
Publishing with Android App Bundles helps your users to install your app with the smallest downloads possible and increases the **compressed download size limit to 150 MB**. That is, when a user downloads your app, the total size of the compressed APKs required to install your app (for example, the base APK + configuration APKs) must be no more than 150 MB. Any subsequent downloads, such as downloading a feature module (and its configuration APKs) on demand, must also meet this compressed download size restriction. Asset packs do not contribute to this size limit, but they do have other [size restrictions](https://developer.android.com/guide/playcore/asset-delivery#size-limits).

### Links
- [About Android App Bundles](https://developer.android.com/guide/app-bundle)
- [Android App Bundle frequently asked questions](https://developer.android.com/guide/app-bundle/faq)
- [Android App Bundle (AAB)](https://gonative.io/docs/android-app-bundle)

### Further Reading
- [Top 7 takeaways for Android App Bundles](https://www.youtube.com/watch?v=st9VZuJNIbw)
- [What a new publishing format means for the future of Android](https://medium.com/googleplaydev/what-a-new-publishing-format-means-for-the-future-of-android-2e34981793a)
- [Building your first app bundle](https://medium.com/androiddevelopers/building-your-first-app-bundle-bbcd228bf631)

### Related Topics
- [What do you know about Play Feature Delivery?](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20Play%20Feature%20Delivery.md)

---

## Вопрос (RU)
Что вы знаете об App Bundles?

## Ответ (RU)

### App Bundles
*Android App Bundle* - это формат публикации, который включает в себя весь скомпилированный код и ресурсы вашего приложения, и делегирует генерацию и подписание APK в Google Play.

Google Play использует ваш app bundle для генерации и предоставления оптимизированных APK для каждой конфигурации устройства, так что только код и ресурсы, необходимые для конкретного устройства, загружаются для запуска вашего приложения. Вам больше не нужно создавать, подписывать и управлять несколькими APK для оптимизации поддержки различных устройств, а пользователи получают меньшие, более оптимизированные загрузки.

Когда вы используете формат app bundle для публикации вашего приложения, вы также можете опционально воспользоваться [Play Feature Delivery](https://developer.android.com/guide/playcore/feature-delivery), который позволяет добавлять *модули функций* в проект вашего приложения. Эти модули содержат функции и ресурсы, которые включаются в ваше приложение только на основе условий, которые вы указываете, или доступны позже во время выполнения для загрузки [используя библиотеку Play Core](https://developer.android.com/guide/playcore).

### В чем разница между AAB и APK?
App bundles предназначены только для публикации и не могут быть установлены на устройства Android. Android package (APK) - это устанавливаемый, исполняемый формат Android для приложений. App bundles должны быть обработаны дистрибьютором в APK, чтобы они могли быть установлены на устройствах.

| APK | AAB |
|---|---|
| Загрузка в Google Play и прямая установка на устройства | Загрузка только в Google Play |
| Нет уменьшения размера загрузки через динамическую доставку | Поддерживает динамическую доставку |
| Поддерживает подписание разработчиком или Google | Только подписание Google |

### Ограничение размера сжатой загрузки
Публикация с помощью Android App Bundles помогает вашим пользователям устанавливать ваше приложение с минимально возможными загрузками и увеличивает **лимит размера сжатой загрузки до 150 МБ**. То есть, когда пользователь загружает ваше приложение, общий размер сжатых APK, необходимых для установки вашего приложения (например, базовый APK + конфигурационные APK), должен быть не более 150 МБ. Любые последующие загрузки, такие как загрузка модуля функций (и его конфигурационных APK) по требованию, также должны соответствовать этому ограничению размера сжатой загрузки. Asset packs не учитываются в этом ограничении размера, но имеют другие [ограничения размера](https://developer.android.com/guide/playcore/asset-delivery#size-limits).

### Ссылки
- [О Android App Bundles](https://developer.android.com/guide/app-bundle)
- [Часто задаваемые вопросы по Android App Bundle](https://developer.android.com/guide/app-bundle/faq)
- [Android App Bundle (AAB)](https://gonative.io/docs/android-app-bundle)

### Дополнительное чтение
- [7 главных выводов об Android App Bundles](https://www.youtube.com/watch?v=st9VZuJNIbw)
- [Что новый формат публикации означает для будущего Android](https://medium.com/googleplaydev/what-a-new-publishing-format-means-for-the-future-of-android-2e34981793a)
- [Создание вашего первого app bundle](https://medium.com/androiddevelopers/building-your-first-app-bundle-bbcd228bf631)

### Связанные темы
- [Что вы знаете о Play Feature Delivery?](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20Play%20Feature%20Delivery.md)
