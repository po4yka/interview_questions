---
id: android-646
title: Advanced ShareSheet & Shortcuts / Расширенный ShareSheet и ярлыки
aliases: [Advanced ShareSheet & Shortcuts, Расширенный ShareSheet и ярлыки]
topic: android
subtopics: [shortcuts-widgets, ui-navigation, ui-views]
question_kind: android
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-communication-surfaces, q-advanced-share-sheet-shortcuts--android--hard, q-camerax-advanced-pipeline--android--hard, q-recyclerview-itemdecoration-advanced--android--medium, q-room-type-converters-advanced--android--medium]
created: 2025-11-02
updated: 2025-11-10
tags: [android/shortcuts-widgets, android/ui-navigation, android/ui-views, difficulty/hard]
sources:
  - url: "https://developer.android.com/develop/ui/views/sharing/send"
    note: "ShareSheet user experience"
  - url: "https://developer.android.com/develop/ui/views/shortcuts"
    note: "Shortcuts guide"
  - url: "https://developer.android.com/about/versions/13/features/predictive-back"
    note: "Predictive back integration"
---
# Вопрос (RU)
> Как построить продвинутую интеграцию с ShareSheet: direct share, динамические ярлыки, персонализация, аналитика и соответствие политикам?

# Question (EN)
> How do you build an advanced ShareSheet experience with direct share, dynamic shortcuts, personalization, analytics, and policy compliance?

---

## Ответ (RU)

### 1. Direct Share (через Shortcuts)

- На современных версиях Android direct share основан на статических/динамических ярлыках (`ShortcutInfo`/`ShortcutInfoCompat`), а не на `ChooserTargetService` (он устарел и удалён в новых API).
- Используйте `ShortcutManager` / `ShortcutManagerCompat` для создания ярлыков под конкретные диалоги/контакты (conversation shortcuts), чтобы система могла предлагать их в системном ShareSheet.
- Ограничивайте количество ярлыков на контакт/диалог и показывайте только актуальные и безопасные цели (privacy: не показывать скрытые/заблокированные контакты, приватные чаты и т.п.).

### 2. Dynamic & Pinned Shortcuts

- Создайте dynamic shortcut (например, "последние контакты"):

```kotlin
val shortcut = ShortcutInfoCompat.Builder(context, id)
    .setShortLabel("Share to Alex")
    .setLongLabel("Share latest article to Alex")
    .setIcon(IconCompat.createWithBitmap(bitmap))
    .setIntent(
        Intent(context, ShareProxyActivity::class.java).apply {
            action = "com.example.action.SHARE_TO_TARGET"
        }
    )
    .setCategories(setOf("com.example.category.SHARE_TARGET"))
    .build()

ShortcutManagerCompat.pushDynamicShortcut(context, shortcut)
```

- Поддерживайте pinned shortcuts (выбор пользователя) через `ShortcutManagerCompat.requestPinShortcut(...)` / `requestPinShortcut(...)` и корректно обновляйте/отзывайте их при изменении контактов или настроек.

### 3. Custom ShareSheet

- Для системного шаринга используйте стандартные intent'ы (`ACTION_SEND`, `ACTION_SEND_MULTIPLE`) и при необходимости `Intent.createChooser(...)`.
- Если нужен собственный UI (in-app share) поверх/в дополнение к системному:
  - соблюдайте Material guidelines;
  - предоставьте быстрый выбор последних контактов/чатов и действий;
  - добавьте быстрые действия вроде "Copy link", "Share to self".
- Не подменяйте полностью системный ShareSheet без веской причины; давайте пользователю понятный путь к системному выбору.

### 4. Predictive back & UX

- Для кастомных экранов шаринга на Android 13+ интегрируйте predictive back через `OnBackInvokedCallback` (API 33+), чтобы анимация и навигация были консистентны с системой.
- Анимации выхода/возврата должны быть согласованы с общим навигационным паттерном приложения и не конфликтовать с системным ShareSheet.
- При использовании `Intent.createChooser` уважайте выбор пользователя и не навязывайте дефолтное приложение в обход системного диалога.

### 5. Privacy & Policy

- Не отправляйте контактные данные, историю шаринга или список targets на сервер без явного opt-in.
- Фильтруйте типы контента: корректно задавайте MIME-типы, избегайте утечки чувствительных данных в другие приложения.
- Обеспечьте ясные подписи (что именно шарится: фото, ссылка, текст и т.п.).

### 6. Analytics

- Логируйте ключевые события: запуск шаринга, выбор цели, успешная отправка/ошибка.
- Разделяйте in-app share vs системный ShareSheet; измеряйте конверсию и отказ (дошёл ли пользователь до фактической отправки).
- A/B-тестируйте порядок и видимость быстрых целей/действий (в рамках политик и без нарушения приватности, предпочтительно on-device).

### 7. Testing

- Unit / instrumentation tests: проверяйте корректность создания/обновления ярлыков, соблюдение лимитов, реакции на удаление контактов.
- UI-тесты (Espresso/UITest): запускайте in-app share и проверяйте наличие нужных элементов и корректную навигацию к системному ShareSheet.
- Accessibility: убедитесь в наличии описательных контент-описаний, корректном фокусе и touch targets ≥ 48dp.

---

## Answer (EN)

### 1. Direct Share (via Shortcuts)

- On modern Android, direct share is based on static/dynamic shortcuts (`ShortcutInfo`/`ShortcutInfoCompat`), not `ChooserTargetService` (deprecated and removed in newer APIs).
- Use `ShortcutManager` / `ShortcutManagerCompat` to create conversation shortcuts for specific chats/contacts so the system can surface them in the system ShareSheet.
- Limit the number of shortcuts per contact/conversation and expose only relevant and safe targets (e.g., exclude hidden/blocked contacts and private chats).

### 2. Dynamic & Pinned Shortcuts

- Create dynamic shortcuts (for example, recent contacts) using `ShortcutInfoCompat`:

```kotlin
val shortcut = ShortcutInfoCompat.Builder(context, id)
    .setShortLabel("Share to Alex")
    .setLongLabel("Share latest article to Alex")
    .setIcon(IconCompat.createWithBitmap(bitmap))
    .setIntent(
        Intent(context, ShareProxyActivity::class.java).apply {
            action = "com.example.action.SHARE_TO_TARGET"
        }
    )
    .setCategories(setOf("com.example.category.SHARE_TARGET"))
    .build()

ShortcutManagerCompat.pushDynamicShortcut(context, shortcut)
```

- Support pinned shortcuts (user-chosen) via `ShortcutManagerCompat.requestPinShortcut(...)` / `requestPinShortcut(...)` and update or disable them when contacts or settings change.

### 3. Custom ShareSheet

- For system-level sharing, use standard intents (`ACTION_SEND`, `ACTION_SEND_MULTIPLE`) and `Intent.createChooser(...)` when needed.
- If you build a custom in-app share UI in addition to the system ShareSheet:
  - follow Material guidelines;
  - provide quick access to recent contacts/chats and relevant actions;
  - include quick actions like "Copy link" or "Share to self".
- Do not fully replace the system ShareSheet without a strong reason; always provide a clear path to the system chooser.

### 4. Predictive back & UX

- For custom share screens on Android 13+, integrate predictive back using `OnBackInvokedCallback` (API 33+) so navigation and animations align with the system behavior.
- Coordinate exit/return animations of your custom share UI with the app navigation pattern and ensure they do not conflict with the system ShareSheet.
- When using `Intent.createChooser`, respect the chooser UX and do not force a default app that bypasses the system dialog.

### 5. Privacy & Policy

- Do not send contact data, share history, or target lists to your servers without explicit opt-in.
- Filter and declare content types correctly with MIME types; avoid leaking sensitive data to other apps.
- Provide clear labels so users understand exactly what is being shared (photo, link, text, etc.).

### 6. Analytics

- Log key events: share initiated, target selected, success/failure.
- Distinguish between in-app share flows and the system ShareSheet; measure conversion and drop-off (whether a share is actually completed).
- Experiment (e.g., A/B tests) with ranking and visibility of in-app quick targets/actions within policy and in a privacy-preserving, preferably on-device, manner.

### 7. Testing

- Use unit and instrumentation tests to verify shortcut creation/updates, limits, and behavior when contacts are removed or changed.
- Use UI tests (Espresso/UITest) to validate in-app share UI elements and navigation to the system ShareSheet.
- Explicitly test accessibility: content descriptions, focus order, semantics, and minimum touch targets of at least 48dp.

---

## Follow-ups
- Как персонализировать выдачу targets с ML (on-device ranking)?
- Как синхронизировать share history между устройствами (Cloud sync)?
- Какие UX паттерны для совместного редактирования (share + collaboration links)?

## References
- [[c-communication-surfaces]]
- https://developer.android.com/develop/ui/views/sharing/send

## Related Questions

- [[c-communication-surfaces]]
