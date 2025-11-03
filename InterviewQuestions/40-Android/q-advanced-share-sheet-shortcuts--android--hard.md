---
id: android-646
title: Advanced ShareSheet & Shortcuts / Расширенный ShareSheet и ярлыки
aliases:
  - Advanced ShareSheet & Shortcuts
  - Расширенный ShareSheet и ярлыки
topic: android
subtopics:
  - communication
  - sharing
  - shortcuts
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-communication-surfaces
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/sharing
  - android/shortcuts
  - communication
  - difficulty/hard
sources:
  - url: https://developer.android.com/develop/ui/views/sharing/send
    note: ShareSheet user experience
  - url: https://developer.android.com/develop/ui/views/shortcuts
    note: Shortcuts guide
  - url: https://developer.android.com/about/versions/13/features/predictive-back
    note: Predictive back integration
---

# Вопрос (RU)
> Как построить продвинутую интеграцию с ShareSheet: direct share, ChooserTargets, динамические ярлыки, персонализация, аналитика и соответствие политикам?

# Question (EN)
> How do you build an advanced ShareSheet experience with direct share, ChooserTargets, dynamic shortcuts, personalization, analytics, and policy compliance?

---

## Ответ (RU)

### 1. Direct share (ChooserTargetService)

- Реализуйте `ChooserTargetService` → возвращайте top conversations/contacts.
- Используйте `ShortcutManagerCompat` для синхронизации данных (conversation shortcuts).
- Ограничьте кол-во target (<= 4) и ESG (privacy: не показывать, если контакт скрыт).

### 2. Dynamic & Pinned Shortcuts

- Создайте dynamic shortcut (user recents):

```kotlin
val shortcut = ShortcutInfoCompat.Builder(context, id)
    .setShortLabel("Share to Alex")
    .setLongLabel("Share latest article to Alex")
    .setIcon(IconCompat.createWithBitmap(bitmap))
    .setIntent(Intent(context, ShareProxyActivity::class.java).apply { action = ACTION_SHARE })
    .setCategories(setOf("com.example.category.SHARE_TARGET"))
    .build()
ShortcutManagerCompat.pushDynamicShortcut(context, shortcut)
```

- Поддерживайте pinned shortcuts (user choice) → `requestPinShortcut`.

### 3. Custom ShareSheet

- Используйте `ShareCompat.IntentBuilder`.
- Для собственных UI (in-app share) → соблюдайте Material guidelines, предоставьте быстрый выбор последних контактов.
- Предоставьте \"Copy link\", \"Share to self\" как быстрые действия.

### 4. Predictive back & UX

- Android 13/14: интегрируйте predictive back → `OnBackInvokedCallback` при кастомном share UI.
- Add animations consistent с system share sheet.
- Respect `ACTION_CHOOSER` → allow user to pick default.

### 5. Privacy & policy

- Не отправляйте контактные данные на сервер без opt-in.
- Filter content types: MIME type restrictions, avoid leaking sensitive data.
- Provide clear labeling (photo vs link).

### 6. Analytics

- Логируйте: share initiated, target selected, completion/failure.
- Разделяйте in-app vs system share; измеряйте conversion/attrition.
- A/B тестирование: order of targets, suggestions (ML ranking).

### 7. Testing

- CTS / unit tests: ensure shortcuts exist, per contact limit respected.
- Espresso: launch share flow → verify UI.
- Accessibility: ensure talkback labels, touch targets >= 48dp.

---

## Answer (EN)

- Implement `ChooserTargetService` for direct share targets backed by dynamic shortcuts synced via `ShortcutManager`.
- Manage dynamic/pinned shortcuts with rich metadata, icons, and intents routed through a share proxy.
- Complement system ShareSheet with an in-app share UI for recent contacts, keeping Material design guidance.
- Integrate predictive back for custom share flows and let users fall back to system choosers.
- Respect privacy policies, filter MIME types, and avoid exposing sensitive data without consent.
- Instrument analytics (initiation, target selection, success/failure) and experiment with target ranking to improve engagement.
- Test shortcuts/targets via CTS and Espresso, validating accessibility compliance.

---

## Follow-ups
- Как персонализировать выдачу targets с ML (on-device ranking)?
- Как синхронизировать share history между устройствами (Cloud sync)?
- Какие UX паттерны для совместного редактирования (share + collaboration links)?

## References
- [[c-communication-surfaces]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/develop/ui/views/sharing/send
