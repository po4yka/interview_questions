---
id: android-633
title: ChromeOS Desktop Optimization / Оптимизация Android-приложения под ChromeOS
aliases:
  - ChromeOS Desktop Optimization
  - Оптимизация Android-приложения под ChromeOS
topic: android
subtopics:
  - chromeos
  - desktop
  - adaptive-ui
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-chromeos-desktop
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/chromeos
  - android/desktop
  - adaptive-ui
  - difficulty/hard
sources:
  - url: https://developer.android.com/large-screens/chromeos
    note: ChromeOS adaptation guide
  - url: https://developer.android.com/games/playgamespc
    note: Play Games on PC requirements
---

# Вопрос (RU)
> Как адаптировать Android-приложение для ChromeOS/Desktop: поддержать resizeable окна, клавиатуру/мышь, drag-and-drop, файловые диалоги и Play Games on PC требования?

# Question (EN)
> How do you adapt an Android app for ChromeOS/desktop environments, covering resizable windows, keyboard/mouse UX, drag-and-drop, file pickers, and Play Games on PC requirements?

---

## Ответ (RU)

### 1. Окна и макеты

- Убедитесь, что `android:resizeableActivity="true"` и `supportsPictureInPicture`.
- Используйте `WindowMetrics` и `WindowSizeClass` для адаптивного UI.
- ActivityEmbedding для мастер/деталь, multi-paned UI.
- Поддержите multi-window multi-instance (`android:exportedActivity` + `launchMode=multiple`).

### 2. Ввод

- Клавиатура: shortcuts (`addOnUnhandledKeyEventListener`), `ShortcutManager`.
- Мышь: `onGenericMotionEvent` (scroll), `onHoverEvent`, контекстное меню (right-click).
- Touchpad gestures: используйте `ViewConfiguration.getScaledTouchSlop`.

### 3. Drag-and-drop, Clipboard

```kotlin
view.setOnDragListener { _, event ->
    when (event.action) {
        DragEvent.ACTION_DROP -> {
            val item = event.clipData.getItemAt(0)
            handleUri(item.uri)
            true
        }
        else -> true
    }
}
```

- Поддержите drag из/в другие окна (ClipData).
- ClipboardManager для copy/paste; поддержите rich content (`CommitContent`).

### 4. Файлы и SAF

- Применяйте `ACTION_OPEN_DOCUMENT`/`CREATE_DOCUMENT`; ChromeOS пользователи ожидают полноценные диалоги.
- Поддержите `DocumentFile` операции на внешних хранилищах.
- Уважайте scoped storage — не обращаться к путям напрямую.

### 5. Play Games on PC (если игра)

- Соберите x86/x86_64 ABI, включите `android:enableOnBackInvokedCallback`.
- Поддержите gamepad (InputDevice, `KeyEvent` mapping).
- Цели: 60+ FPS, адаптируйте графику (Desktop GPU).
- Интегрируйте Play Games Services PC overlay (в разработке).

### 6. QA & дистрибуция

- Тестируйте на ChromeOS emulator, физическом Chromebook.
- Используйте Play Console ChromeOS-specific screenshots/requirements.
- Сигнализируйте `isResizeableActivity` в manifest (required for listing).

---

## Answer (EN)

- Ensure activities are resizable, use window metrics for adaptive layouts, and support multi-window/multi-instance scenarios.
- Handle keyboard shortcuts, mouse hover/right-click, and pointer scrolling; provide desktop-like UX.
- Implement drag-and-drop and clipboard integration with SAF-backed URI handling.
- Use document pickers for file workflows and respect scoped storage security.
- For games, ship x86 builds, optimize frame rates, and fully support controllers per Play Games on PC guidelines.

---

## Follow-ups
- Как реализовать custom window shortcuts / menu bar для ChromeOS?
- Как адаптировать notifications/bubbles для desktop UX?
- Какие метрики собирать для desktop пользователей (input method, window size)?

## References
- [[c-chromeos-desktop]]
- https://developer.android.com/large-screens/chromeos

## Related Questions

- [[c-chromeos-desktop]]
