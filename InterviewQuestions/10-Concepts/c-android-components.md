---
id: concept-android-components
title: Android Components / Компоненты Android
aliases: [Android Components, App Components, Компоненты Android]
kind: concept
summary: The four fundamental building blocks of Android applications
links: []
created: 2025-11-06
updated: 2025-11-06
tags: [android, architecture, components, concept]
---

# Summary (EN)

Android applications are built from four fundamental component types that serve as entry points through which the system or user can interact with your app:

1. **Activities** - UI screens that represent a single screen with a user interface
2. **Services** - Background components that perform long-running operations without UI
3. **Broadcast Receivers** - Components that respond to system-wide broadcast announcements
4. **Content Providers** - Components that manage shared app data and provide data to other apps

Each component type has a distinct purpose and lifecycle, and each is defined in the AndroidManifest.xml file.

# Сводка (RU)

Приложения Android построены из четырёх фундаментальных типов компонентов, которые служат точками входа для взаимодействия системы или пользователя с приложением:

1. **Activities** - Экраны пользовательского интерфейса, представляющие один экран с UI
2. **Services** - Фоновые компоненты для длительных операций без UI
3. **Broadcast Receivers** - Компоненты, реагирующие на системные широковещательные сообщения
4. **Content Providers** - Компоненты для управления общими данными и предоставления данных другим приложениям

Каждый тип компонента имеет свою цель и жизненный цикл, и каждый определяется в файле AndroidManifest.xml.

## Use Cases / Trade-offs

**Activities**:
- Presenting UI to users
- Handling user interactions
- Managing screen transitions

**Services**:
- Playing music in background
- Network operations
- File I/O operations
- Foreground services with notifications

**Broadcast Receivers**:
- Responding to battery low events
- Handling network connectivity changes
- Receiving custom app events
- Scheduled tasks (with WorkManager preferred)

**Content Providers**:
- Sharing data between apps
- Providing structured access to app data
- Implementing sync adapters

## References

- [Android App Components](https://developer.android.com/guide/components/fundamentals)
- [Activities Overview](https://developer.android.com/guide/components/activities/intro-activities)
- [Services Overview](https://developer.android.com/guide/components/services)
- [Broadcast Receivers](https://developer.android.com/guide/components/broadcasts)
- [Content Providers](https://developer.android.com/guide/topics/providers/content-providers)
