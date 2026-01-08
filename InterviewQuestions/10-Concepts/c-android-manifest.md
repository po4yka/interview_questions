---\
id: "20251110-151752"
title: "Android Manifest / Android Manifest"
aliases: ["Android Manifest"]
summary: "Foundational concept for interview preparation"
topic: "android"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: ["c-android-basics", "c-permissions", "c-intent", "c-deep-linking", "c-app-signing"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [android, concept, difficulty/medium]
---\

# Summary (EN)

AndroidManifest.xml is the core configuration file of an Android application that declares its package identity, components (activities, services, broadcast receivers, content providers), required permissions, and key system integrations. It tells the Android system how to launch the app, which features it needs (e.g., camera, internet), and how it should be exposed to other apps and system components. A correct and minimal manifest is essential for app installation, security, deep linking, and proper runtime behavior.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

AndroidManifest.xml — это основной конфигурационный файл Android-приложения, в котором определяются идентификатор пакета, компоненты (activity, service, broadcast receiver, content provider), необходимые разрешения и ключевые интеграции с системой. Он сообщает системе Android, как запускать приложение, какие функции и аппаратные возможности ему нужны (например, камера, интернет), и как оно взаимодействует с другими приложениями и системными компонентами. Корректный и минимальный манифест критичен для установки приложения, безопасности, deep linking и правильного поведения во время выполнения.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- `Component` declarations: Lists all app components (`<activity>`, `<service>`, `<receiver>`, `<provider>`) and their intent filters, enabling the system to discover entry points like the launcher activity.
- Permissions and security: Declares permissions the app requests (`<uses-permission>`) and exposes or restricts components, directly impacting app security and access control.
- App identity and metadata: Defines `package`, `applicationId` (via Gradle), app label, icons, themes, `minSdkVersion`, `targetSdkVersion`, and custom `<meta-data>` used by libraries and services.
- System and hardware features: Specifies required hardware and software capabilities (`<uses-feature>`, `<uses-sdk>`), affecting installation eligibility and visibility on Google Play.
- `Intent` filters and deep links: Configures how activities respond to specific actions, data schemes, and URLs, enabling implicit intents and app links.

## Ключевые Моменты (RU)

- Объявление компонентов: Описывает все компоненты приложения (`<activity>`, `<service>`, `<receiver>`, `<provider>`) и их intent-filter'ы, чтобы система могла находить точки входа, включая launcher-activity.
- Разрешения и безопасность: Определяет разрешения, запрашиваемые приложением (`<uses-permission>`), и уровень доступа к компонентам, напрямую влияя на безопасность и контроль взаимодействия.
- Идентичность приложения и метаданные: Задает `package`, связанный `applicationId` (через Gradle), название, иконки, темы, `minSdkVersion`, `targetSdkVersion`, а также `<meta-data>`, используемые библиотеками и сервисами.
- Системные и аппаратные требования: Описывает необходимые функции устройства и системы (`<uses-feature>`, `<uses-sdk>`), что влияет на возможность установки и видимость приложения в Google Play.
- `Intent`-фильтры и deep links: Настраивает реакцию activity на определенные действия, схемы и URL, обеспечивая работу неявных intent'ов и app links.

## References

- Official Android documentation: https://developer.android.com/guide/topics/manifest/manifest-intro
