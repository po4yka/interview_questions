---
id: "20251110-143706"
title: "Android Resources / Android Resources"
aliases: ["Android Resources"]
summary: "Foundational concept for interview preparation"
topic: "android"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-android"
related: [c-android-themes, c-drawable, c-dimension-units, c-android-manifest, c-android-basics]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["android", "auto-generated", "concept", "difficulty/medium"]
---

# Summary (EN)

Android resources are externalized application assets (such as strings, layouts, images, colors, dimensions, and styles) stored under the res/ directory and referenced by ID instead of hardcoding values in code. They enable localization, support for multiple screen sizes and densities, themeing, and easier maintenance by separating UI/content from application logic. In interviews, understanding resources is key to explaining how Android handles configuration changes, qualifiers, and efficient asset management.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Android-ресурсы — это вынесенные из исходного кода ресурсы приложения (строки, разметки, изображения, цвета, размеры, стили и др.), хранящиеся в каталоге res/ и используемые по идентификаторам, а не «зашитые» в коде. Они обеспечивают локализацию, поддержку разных экранов и плотностей, темизацию и упрощают сопровождение за счёт разделения логики и представления. На собеседованиях важно понимать, как ресурсы связаны с конфигурациями, квалификаторами и управлением активами.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Resource Types: Include layouts (res/layout), strings (res/values/strings.xml), drawables (res/drawable-*), colors, dimensions, styles, menus, animations, and more, each accessed via the generated R class.
- Resource Qualifiers: Directory qualifiers (e.g., -land, -night, -hdpi, -ru, -sw600dp) let Android auto-select the best resource based on device configuration without manual branching in code.
- Accessing Resources: Resources are referenced via R (e.g., R.string.app_name, R.layout.activity_main) or through Context/Resources APIs (getString, getDrawable, getColor, getDimension, getQuantityString).
- Localization and Theming: Strings, plurals, styles, themes, and color resources make it easy to localize text and apply consistent theming/dark mode across the app.
- Best Practices: Avoid hardcoding values in code/layouts, reuse styles and dimensions, provide density-specific assets, and handle missing/alternative resources to prevent crashes and layout issues.

## Ключевые Моменты (RU)

- Типы ресурсов: Разметки (res/layout), строки (res/values/strings.xml), изображения (res/drawable-*), цвета, размеры, стили, меню, анимации и др., к которым обращаются через сгенерированный класс R.
- Квалификаторы ресурсов: Суффиксы директорий (например, -land, -night, -hdpi, -ru, -sw600dp) позволяют Android автоматически выбирать подходящие ресурсы под конфигурацию устройства без условной логики в коде.
- Доступ к ресурсам: Обращение к ресурсам через R (например, R.string.app_name, R.layout.activity_main) или через Context/Resources (getString, getDrawable, getColor, getDimension, getQuantityString).
- Локализация и темы: Ресурсы строк, плюралов, стилей, тем и цветов упрощают локализацию интерфейса и применение единого оформления/тёмной темы по всему приложению.
- Рекомендации: Не хардкодить значения в коде и разметке, переиспользовать стили и размеры, предоставлять ресурсы под разные плотности экранов и обрабатывать альтернативные/отсутствующие ресурсы для избежания падений и проблем в UI.

## References

- Android Developers: "App resources overview" — https://developer.android.com/guide/topics/resources/overview
- Android Developers: "Providing resources" — https://developer.android.com/guide/topics/resources/providing-resources
