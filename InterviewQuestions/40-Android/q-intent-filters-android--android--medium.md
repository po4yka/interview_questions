---
id: android-178
title: Intent Filters / Intent Фильтры
aliases: [Intent Filters, Intent Фильтры, Фильтры намерений]
topic: android
subtopics: [activity, intents-deeplinks]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity, c-intent, q-dagger-build-time-optimization--android--medium, q-what-are-intents-for--android--medium, q-what-is-intent--android--easy]
created: 2025-10-15
updated: 2025-11-10
tags: [android/activity, android/intents-deeplinks, deep-linking, difficulty/medium, intent-filter]
sources: []
anki_cards:
  - slug: android-178-0-en
    front: "What are Intent Filters in Android and how do they work?"
    back: |
      **Intent Filter** declares which implicit intents a component can handle.

      **Three matching criteria:**
      1. **action** - `ACTION_VIEW`, `ACTION_SEND`, etc.
      2. **data** - URI scheme, host, MIME type
      3. **category** - `DEFAULT`, `BROWSABLE`, `LAUNCHER`

      ```xml
      <intent-filter>
          <action android:name="android.intent.action.VIEW"/>
          <category android:name="android.intent.category.DEFAULT"/>
          <data android:scheme="https" android:host="example.com"/>
      </intent-filter>
      ```
    tags:
      - android_intents
      - difficulty::medium
  - slug: android-178-0-ru
    front: "Что такое Intent Filters в Android и как они работают?"
    back: |
      **Intent Filter** объявляет, какие неявные интенты может обрабатывать компонент.

      **Три критерия соответствия:**
      1. **action** - `ACTION_VIEW`, `ACTION_SEND` и др.
      2. **data** - URI схема, хост, MIME тип
      3. **category** - `DEFAULT`, `BROWSABLE`, `LAUNCHER`

      ```xml
      <intent-filter>
          <action android:name="android.intent.action.VIEW"/>
          <category android:name="android.intent.category.DEFAULT"/>
          <data android:scheme="https" android:host="example.com"/>
      </intent-filter>
      ```
    tags:
      - android_intents
      - difficulty::medium

---
# Вопрос (RU)

> Что такое `Intent` Filters в Android и как они работают?

# Question (EN)

> What are `Intent` Filters in Android and how do they work?

## Ответ (RU)

**`Intent` Filter** — это выражение в манифесте приложения, определяющее типы интентов, которые компонент готов принимать. Фильтры позволяют объявлять возможности компонентов и обеспечивают разрешение неявных намерений.

### Основные Компоненты

Фильтр состоит из трёх элементов:

**`<action>`** (обязательный) — действие, которое компонент может выполнить:
```xml
<!-- Standard actions -->
<action android:name="android.intent.action.MAIN" />
<action android:name="android.intent.action.SEND" />

<!-- Custom actions with package prefix -->
<action android:name="com.example.project.CUSTOM_ACTION" />
```

**`<category>`** (опционально) — дополнительная категоризация:
```xml
<category android:name="android.intent.category.LAUNCHER" />
<category android:name="android.intent.category.DEFAULT" />
<category android:name="android.intent.category.BROWSABLE" />
```

**`<data>`** (опционально) — спецификация данных (MIME-тип или URI):
```xml
<!-- MIME type -->
<data android:mimeType="text/plain" />

<!-- URI scheme -->
<data android:scheme="https"
      android:host="example.com"
      android:pathPrefix="/products" />
```

### Примеры Использования

**Launcher активность**:
```xml
<activity android:name=".MainActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
```

**Deep linking**:
```xml
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data
        android:scheme="https"
        android:host="myapp.com"
        android:pathPrefix="/product" />
</intent-filter>
```

**Share активность**:
```xml
<intent-filter>
    <action android:name="android.intent.action.SEND" />
    <!-- DEFAULT обязателен для неявных интентов -->
    <category android:name="android.intent.category.DEFAULT" />
    <data android:mimeType="text/plain" />
</intent-filter>
```

### Ключевые Правила

1. `CATEGORY_DEFAULT` обязателен для активностей, принимающих неявные интенты
2. `android:exported` должен быть указан явно (обязательно с API 31+)
3. `android:autoVerify="true"` используется для App Links (HTTPS URL)
4. Один компонент может иметь несколько фильтров, каждый описывает отдельную возможность

## Answer (EN)

**`Intent` Filter** is an expression in the app's manifest that specifies the types of intents a component can receive. Filters allow components to declare their capabilities and enable implicit intent resolution.

### Core Components

A filter consists of three elements:

**`<action>`** (required) — action the component can perform:
```xml
<!-- Standard actions -->
<action android:name="android.intent.action.MAIN" />
<action android:name="android.intent.action.SEND" />

<!-- Custom actions with package prefix -->
<action android:name="com.example.project.CUSTOM_ACTION" />
```

**`<category>`** (optional) — additional categorization:
```xml
<category android:name="android.intent.category.LAUNCHER" />
<category android:name="android.intent.category.DEFAULT" />
<category android:name="android.intent.category.BROWSABLE" />
```

**`<data>`** (optional) — data specification (MIME type or URI):
```xml
<!-- MIME type -->
<data android:mimeType="text/plain" />

<!-- URI scheme -->
<data android:scheme="https"
      android:host="example.com"
      android:pathPrefix="/products" />
```

### Usage Examples

**Launcher activity**:
```xml
<activity android:name=".MainActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
```

**Deep linking**:
```xml
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data
        android:scheme="https"
        android:host="myapp.com"
        android:pathPrefix="/product" />
</intent-filter>
```

**Share activity**:
```xml
<intent-filter>
    <action android:name="android.intent.action.SEND" />
    <!-- DEFAULT required for implicit intents -->
    <category android:name="android.intent.category.DEFAULT" />
    <data android:mimeType="text/plain" />
</intent-filter>
```

### Key Rules

1. `CATEGORY_DEFAULT` required for activities receiving implicit intents
2. `android:exported` must be explicit (mandatory from API 31+)
3. `android:autoVerify="true"` for App Links (HTTPS URLs)
4. One component can have multiple filters, each describing a separate capability

## Дополнительные Вопросы (RU)

- Как Android разрешает конфликты, когда несколько приложений объявляют фильтры намерений для одного и того же действия?
- В чем разница между неявными и явными интентами с точки зрения безопасности?
- Как программно тестировать deep links и App Links?
- Каковы последствия для производительности при наличии большого количества intent filters?

## Follow-ups

- How does Android resolve conflicts when multiple apps declare intent filters for the same action?
- What is the difference between implicit and explicit intents regarding security?
- How do you test deep links and App Links programmatically?
- What are the performance implications of having many intent filters?

## Ссылки (RU)

- Официальная документация Android: `Intent` Filters
- Официальная документация Android: проверка и настройка App Links

## References

- Android Developer Documentation: `Intent` Filters
- Android Developer Documentation: App Links verification

## Связанные Вопросы (RU)

### Предпосылки / Концепты

- [[c-intent]]
- [[c-activity]]

### Предпосылки (проще)

- [[q-what-is-intent--android--easy]] — Базовые концепции `Intent`
- Основы `Activity` и ее жизненного цикла

### Связанные (того Же уровня)

- [[q-what-are-intents-for--android--medium]] — Сценарии использования `Intent`
- Сравнение неявных и явных интентов

### Продвинутые (сложнее)

- Реализация и верификация App Links
- Вопросы безопасности при работе с интентами

## Related Questions

### Prerequisites / Concepts

- [[c-intent]]
- [[c-activity]]

### Prerequisites (Easier)

- [[q-what-is-intent--android--easy]] — Basic intent concepts
- `Activity` fundamentals and lifecycle

### Related (Same Level)

- [[q-what-are-intents-for--android--medium]] — `Intent` use cases
- Implicit vs explicit intents comparison

### Advanced (Harder)

- App Links verification and implementation
- Security considerations for intents
