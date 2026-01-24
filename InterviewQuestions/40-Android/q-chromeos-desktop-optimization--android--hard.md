---
id: android-633
title: ChromeOS Desktop Optimization / Оптимизация Android-приложения под ChromeOS
aliases:
- ChromeOS Desktop Optimization
- Оптимизация Android-приложения под ChromeOS
topic: android
subtopics:
- foldables-chromeos
- ui-state
- ui-views
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-chromeos-desktop
- moc-android
- q-optimize-memory-usage-android--android--medium
- q-parsing-optimization-android--android--medium
- q-performance-optimization-android--android--medium
created: 2024-11-02
updated: 2025-11-10
tags:
- android/foldables-chromeos
- android/ui-state
- android/ui-views
- difficulty/hard
sources:
- https://developer.android.com/games/playgamespc
- https://developer.android.com/large-screens/chromeos
anki_synced: true
anki_slugs:
- 40-android-q-chromeos-desktop-optimization-android-hard-p01-en
- 40-android-q-chromeos-desktop-optimization-android-hard-p01-ru
anki_last_sync: '2025-11-27T09:56:33.839728'
anki_cards:
- slug: android-633-0-en
  language: en
  anki_id: 1768365309625
  synced_at: '2026-01-23T16:45:06.188488'
- slug: android-633-0-ru
  language: ru
  anki_id: 1768365309648
  synced_at: '2026-01-23T16:45:06.189170'
---
# Вопрос (RU)
> Как адаптировать Android-приложение для ChromeOS/Desktop: поддержать resizeable окна, клавиатуру/мышь, drag-and-drop, файловые диалоги и Play Games on PC требования?

# Question (EN)
> How do you adapt an Android app for ChromeOS/desktop environments, covering resizable windows, keyboard/mouse UX, drag-and-drop, file pickers, and Play Games on PC requirements?

---

## Ответ (RU)

### Краткая Версия
- Разрешите изменяемые окна и multi-window (`android:resizeableActivity="true"` на уровне приложения/`Activity`), корректную работу PiP и multi-instance.
- Реализуйте полноценную поддержку клавиатуры, мыши, трекпада и геймпада.
- Добавьте drag-and-drop, работу с буфером обмена и SAF-файловые диалоги.
- Оптимизируйте UI под большие экраны и ChromeOS (адаптивные макеты, multi-pane, master/detail, `Activity` Embedding через Jetpack WindowManager).
- Для игр соблюдайте требования Play Games on PC (x86-64, производительность, поддержка контроллеров, совместимость с Play Games Services, где требуется).

### Подробная Версия
#### Требования

- Функциональные:
  - Поддержка изменяемых окон, multi-window и multi-instance.
  - Корректный ввод с клавиатуры, мыши, трекпада, геймпада.
  - Поддержка drag-and-drop и буфера обмена между окнами.
  - Работа с файлами через системные диалоги и SAF.
  - Для игр: соответствие требованиям Play Games on PC (архитектура, ввод, производительность, сервисы по чеклисту).
- Нефункциональные:
  - Производительность и стабильность на больших экранах и десктопных GPU.
  - Предсказуемое поведение навигации (включая Back и predictive back) и окон.
  - Соответствие UX-ожиданиям desktop/ChromeOS.

#### Архитектура

- Используйте адаптивный UI-слой (responsive layouts), основанный на `WindowMetrics`/`WindowSizeClass`.
- Стройте layout как набор панелей/фрагментов, чтобы легко поддерживать одиночное окно, multi-pane и `Activity` Embedding (Jetpack WindowManager).
- Изолируйте работу с вводом, файлами и drag-and-drop в отдельные слои/сервисы, чтобы переиспользовать их между phone/ChromeOS.
- Для игр/графических приложений учитывайте разные ABI и устройства ввода в абстрактном input-слое.

#### 1. Окна И Макеты

- Убедитесь, что `android:resizeableActivity="true"` задано для приложения или нужных `activity`, чтобы разрешить изменение размера окна на ChromeOS.
- При необходимости включите PiP: `android:supportsPictureInPicture="true"` + корректно обрабатывайте жизненный цикл.
- Используйте `WindowMetrics` и `WindowSizeClass` для адаптивного UI под разные размеры и ориентации окон.
- Используйте Embedding правил `Activity` (Jetpack WindowManager `Activity` Embedding) для мастер/деталь и multi-pane UI на больших экранах/desktop.
- Поддержите multi-window и multi-instance: не запрещайте многократные инстансы (используйте стандартный `launchMode`/значение по умолчанию) и убедитесь, что состояние корректно обрабатывается при нескольких окнах/тасках.

#### 2. Ввод

- Клавиатура: обрабатывайте `KeyEvent` (включая стрелки, PageUp/PageDown, Delete, Enter), добавляйте сочетания клавиш (например, Ctrl+N, Ctrl+S) через обработку key events; избегайте перехвата системных шорткатов и следуйте desktop-конвенциям. Для ярлыков лаунчера используйте `ShortcutManager` (static/dynamic shortcuts).
- Мышь/trackpad: используйте `onGenericMotionEvent` для скролла, `onHoverEvent` для hover-состояний, поддерживайте right-click (context menu) через `showContextMenuForChild`/`onCreateContextMenu` и соответствующие обработчики.
- Touchpad / pointer gestures: полагайтесь на стандартные события скролла и мыши; `ViewConfiguration.getScaledTouchSlop` используйте только для чувствительности drag/scroll, а не как API жестов.

#### 3. Drag-and-drop, Clipboard

```kotlin
view.setOnDragListener { _, event ->
    when (event.action) {
        DragEvent.ACTION_DROP -> {
            val clipData = event.clipData
            for (i in 0 until (clipData?.itemCount ?: 0)) {
                val item = clipData?.getItemAt(i)
                item?.uri?.let { handleUri(it) }
                item?.text?.let { handleText(it) }
            }
            true
        }
        DragEvent.ACTION_DRAG_STARTED,
        DragEvent.ACTION_DRAG_ENTERED,
        DragEvent.ACTION_DRAG_LOCATION,
        DragEvent.ACTION_DRAG_EXITED,
        DragEvent.ACTION_DRAG_ENDED -> true
        else -> false
    }
}
```

- Поддержите drag & drop из/в другие окна через `ClipData` (URI, текст и др.) и корректную проверку/предоставление пермишенов.
- Используйте `ClipboardManager` для copy/paste.
- Для rich content используйте соответствующие API ввода, такие как `InputConnection.commitContent`/`InputContentInfo` (или совместимые методы), вместо прямой передачи файловых путей.

#### 4. Файлы И SAF

- Применяйте `ACTION_OPEN_DOCUMENT` / `ACTION_CREATE_DOCUMENT` / `ACTION_OPEN_DOCUMENT_TREE`; пользователи ChromeOS ожидают полнофункциональные системные диалоги.
- Используйте `DocumentFile` для операций над файлами/директориями, полученными через SAF.
- Уважайте scoped storage: работайте через URI и предоставленные пермишены, не обращайтесь к файловой системе по прямым путям.

#### 5. Play Games on PC (если игра)

- Соберите бинарь с поддержкой x86-64 ABI (в соответствии с актуальными требованиями Play Games on PC).
- Поддержите gamepad/контроллеры: корректно обрабатывайте `InputDevice`, `KeyEvent` и оси (`MotionEvent`) согласно рекомендациям.
- Обеспечьте стабильную производительность (например, 60+ FPS при возможности, адаптацию под Desktop GPU и различные DPI/частоты), корректную работу в окнах и при смене размера.
- Интегрируйте необходимые компоненты Google Play Games Services (sign-in, achievements, cloud saves и др.) и следуйте официальным требованиям Play Games on PC и их чеклисту совместимости; избегайте неофициальных или нестабильных PC-specific overlay решений.
- Для современных targetSdk обеспечьте предсказуемое поведение кнопки "Назад" (например, `android:enableOnBackInvokedCallback="true"` и обработку on-back-invoked callbacks) и адаптацию под predictive back как часть общих требований, не только для игр.

#### 6. QA & Дистрибуция

- Тестируйте на ChromeOS emulator и на физических Chromebook-устройствах, включая различные форм-факторы.
- В Play Console используйте ChromeOS-специфичные скриншоты и указывайте поддержку больших экранов/desktop где требуется.
- Убедитесь, что в манифесте указана корректная поддержка изменяемого размера окон (`android:resizeableActivity="true"`), так как это влияет на совместимость и отображение в каталоге.

---

## Answer (EN)

### Short Version
- Enable resizable windows and multi-window (`android:resizeableActivity="true"` at app/activity level), and ensure correct PiP and multi-instance behavior.
- Implement full keyboard, mouse, trackpad, and gamepad support.
- Add drag-and-drop, clipboard integration, and SAF-based file dialogs.
- Optimize UI for large screens and ChromeOS with adaptive, multi-pane layouts and `Activity` Embedding (Jetpack WindowManager).
- For games, comply with Play Games on PC requirements (x86-64, performance, controller support, and required Play Games Services integration).

### Detailed Version
#### Requirements

- Functional:
  - Support resizable windows, multi-window, and multi-instance behavior.
  - Proper handling of keyboard, mouse, trackpad, and gamepad input.
  - Drag-and-drop and clipboard operations across windows.
  - File handling via system file pickers and SAF.
  - For games: compliance with Play Games on PC requirements (ABI, input, performance, and services per their checklist).
- Non-functional:
  - Good performance and stability on large screens and desktop-class GPUs.
  - Predictable navigation (including Back and predictive back) and window behavior.
  - Desktop/ChromeOS-friendly UX.

#### Architecture

- Use an adaptive UI layer driven by `WindowMetrics`/`WindowSizeClass`.
- Structure UI as reusable panes/fragments to support single-pane, multi-pane, and `Activity` Embedding (Jetpack WindowManager) layouts.
- Isolate input, file access, and drag-and-drop into dedicated modules/services shared between phone and ChromeOS builds.
- For games/graphics apps, abstract input handling to support multiple device types and ABIs cleanly.

### 1. Windows and Layouts

- Ensure `android:resizeableActivity="true"` is set for the app or relevant activities so windows can be resized on ChromeOS.
- Enable Picture-in-Picture where appropriate via `android:supportsPictureInPicture="true"` and handle PiP lifecycle correctly.
- Use `WindowMetrics` and `WindowSizeClass` to build adaptive layouts for different window sizes and orientations.
- Use `Activity` Embedding rules (Jetpack WindowManager `Activity` Embedding) to implement master-detail and multi-pane UIs on large screens/desktop.
- Support multi-window and multi-instance by allowing multiple task instances (keep the default `launchMode`/standard) and ensuring state handling works correctly with multiple windows/tasks.

### 2. Input

- Keyboard: handle `KeyEvent`s for navigation and editing keys; implement keyboard shortcuts (e.g., Ctrl+N, Ctrl+S) via key event handling; avoid overriding system-level shortcuts and follow desktop conventions. Use `ShortcutManager` for launcher/app shortcuts where appropriate.
- Mouse/trackpad: use `onGenericMotionEvent` for scrolling, `onHoverEvent` for hover states, and support right-click context menus via `onCreateContextMenu`/`showContextMenuForChild` and related APIs.
- Touchpad/pointer gestures: rely on translated scroll and mouse events; use `ViewConfiguration.getScaledTouchSlop` only for tuning drag/scroll sensitivity, not as a generic gesture API.

### 3. Drag-and-drop, Clipboard

```kotlin
view.setOnDragListener { _, event ->
    when (event.action) {
        DragEvent.ACTION_DROP -> {
            val clipData = event.clipData
            for (i in 0 until (clipData?.itemCount ?: 0)) {
                val item = clipData?.getItemAt(i)
                item?.uri?.let { handleUri(it) }
                item?.text?.let { handleText(it) }
            }
            true
        }
        DragEvent.ACTION_DRAG_STARTED,
        DragEvent.ACTION_DRAG_ENTERED,
        DragEvent.ACTION_DRAG_LOCATION,
        DragEvent.ACTION_DRAG_EXITED,
        DragEvent.ACTION_DRAG_ENDED -> true
        else -> false
    }
}
```

- Support drag & drop to/from other windows using `ClipData` (URIs, text, etc.) with correct permission granting and validation.
- Use `ClipboardManager` for copy/paste.
- For rich content, use input APIs such as `InputConnection.commitContent`/`InputContentInfo` (or compat equivalents) instead of relying on raw file paths.

### 4. Files and SAF

- Use `ACTION_OPEN_DOCUMENT`, `ACTION_CREATE_DOCUMENT`, and `ACTION_OPEN_DOCUMENT_TREE` for file workflows; ChromeOS users expect full-featured system file dialogs.
- Use `DocumentFile` for file/directory operations based on SAF URIs.
- Respect scoped storage: operate on URIs with granted permissions and avoid direct filesystem paths.

### 5. Play Games on PC (if a game)

- Ship builds with x86-64 ABI support according to current Play Games on PC requirements.
- Fully support controllers: handle `InputDevice`, `KeyEvent`, and `MotionEvent` axes per official guidelines.
- Optimize performance for desktop-class GPUs and various DPI/refresh rates; ensure stable frame rates (e.g., 60+ FPS when feasible) and correct behavior in resizable windows.
- Integrate the required Google Play Games Services components (sign-in, achievements, cloud saves, etc., as applicable) and follow the official Play Games on PC compatibility checklist; avoid undocumented PC-only overlays.
- For modern targetSdk, correctly support predictive/back-invoked behavior (e.g., `android:enableOnBackInvokedCallback="true"` and callback handling) as a general requirement, not only for games.

### 6. QA & Distribution

- Test on the ChromeOS emulator and on physical Chromebooks across multiple form factors.
- In Play Console, provide ChromeOS-specific screenshots and declare support for large screens/desktop form factors where applicable.
- Ensure the manifest correctly advertises resizable window support (`android:resizeableActivity="true"`), as this affects compatibility and store listing exposure.

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
