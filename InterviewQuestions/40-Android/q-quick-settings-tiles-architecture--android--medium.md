---
id: android-631
title: Quick Settings Tiles Architecture / Quick Settings
aliases:
- Quick Settings Tiles Architecture
- Quick Settings
topic: android
subtopics:
- shortcuts-widgets
- background-execution
- ui-state
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- c-android-components
- c-android-surfaces
- q-advanced-share-sheet-shortcuts--android--hard
created: 2025-11-02
updated: 2025-11-10
tags:
- android/shortcuts-widgets
- android/background-execution
- android/ui-state
- difficulty/medium
sources:
- url: "https://developer.android.com/develop/ui/views/quicksettings"
  note: Quick Settings tile guide
- url: "https://developer.android.com/develop/shortcutmanager"
  note: App Shortcuts documentation

---

# Вопрос (RU)
> Как спроектировать архитектуру Quick Settings Tile так, чтобы тайл оставался синхронизирован с состоянием приложения, безопасно поддерживал фоновые операции и был согласован с интеграцией App Shortcuts?

# Question (EN)
> How do you architect a Quick Settings tile, keep it synchronized with the app state, support background work safely, and align it with shortcuts integration?

---

## Ответ (RU)

### TileService

```kotlin
class SyncTileService : TileService() {

    override fun onStartListening() {
        super.onStartListening()
        // Обновляем состояние тайла из общего источника данных
        qsTile?.apply {
            state = if (isSyncEnabled()) Tile.STATE_ACTIVE else Tile.STATE_INACTIVE
            label = getString(R.string.tile_label)
            updateTile()
        }
    }

    override fun onClick() {
        super.onClick()
        // Обрабатываем нажатие: сразу или через unlockAndRun при заблокированном устройстве
        if (!isLocked) {
            toggleSync()
        } else {
            unlockAndRun { toggleSync() }
        }
    }

    override fun onTileAdded() {
        super.onTileAdded()
        // Инициализируем начальное состояние
        qsTile?.updateTile()
    }

    override fun onStopListening() {
        super.onStopListening()
        // Отпишемся/очистим ресурсы, если нужно
    }
}
```

- `onStartListening()` синхронизирует визуальное состояние тайла с общим состоянием приложения.
- `onTileAdded()` инициализирует тайл при добавлении.
- `onStopListening()` используется для отписок/очистки ресурсов.
- В `onClick()` обрабатывайте переключение; при заблокированном устройстве используйте `unlockAndRun { ... }`.

### Фоновая работа

- Держите `onClick()`/`onStartListening()` легкими: долгие операции выносите в `ForegroundService` с подходящим типом или `WorkManager` (включая expedited work при необходимости).
- Используйте `TileService#startActivityAndCollapse` для открытия нужного UI при закрытии шторки.

### Состояние и синхронизация

- Храните состояние в общем источнике (`DataStore`/`Room`), чтобы и приложение, и `TileService` работали с одним state.
- Наблюдайте изменения через `Flow`/другие реактивные механизмы, создавая собственный `CoroutineScope` в рамках `onStartListening()`/`onStopListening()`.
- При изменении состояния из приложения вызывайте `TileService.requestListeningState(context, componentName)`, чтобы система триггерила `onStartListening()` и вы могли обновить `qsTile`.

### App Shortcuts и виджеты

- Используйте `ShortcutManager` для App Shortcuts, которые отражают те же действия/режимы, что и тайл.
- Обновляйте dynamic shortcuts при включении/выключении функциональности, связанной с тайлом.
- Для intent-ориентированных shortcuts/виджетов применяйте явные `Intent` и `PendingIntent` с `FLAG_IMMUTABLE` (и `FLAG_UPDATE_CURRENT` при обновлении extras), чтобы избежать подмены.

### Безопасность, приватность и UX

- Проверяйте и запрашивайте необходимые привилегии (например, VPN/hotspot/location) до выполнения действий тайла.
- Не запускайте чувствительные потоки с заблокированного экрана; оборачивайте в `unlockAndRun`.
- Проектируйте UX тайла понятно: мгновенный отклик, корректные состояния, отсутствие неожиданных side-effects.

---

## Answer (EN)

- Implement a `TileService` and handle its lifecycle callbacks:
  - refresh tile state in `onStartListening()` based on shared app state, and call `qsTile.updateTile()`;
  - initialize on `onTileAdded()`;
  - clean up/stop observation in `onStopListening()`;
  - toggle behavior in `onClick()`, using `unlockAndRun { ... }` when the device is locked.
- Keep `onClick()`/`onStartListening()` light; offload long-running or network work to:
  - a `ForegroundService` with the appropriate foreground service type; or
  - `WorkManager` (including expedited work when appropriate).
- Use `startActivityAndCollapse()` when you need to open UI from the tile while collapsing the shade.
- Persist tile/app state in shared storage (e.g., `DataStore`/`Room`) so both the app and `TileService` read/write the same source of truth.
- When state changes from the app side, call `TileService.requestListeningState(context, componentName)` so the system will invoke `onStartListening()` for that tile and you can update `qsTile` accordingly.
- For App Shortcuts and widgets:
  - use `ShortcutManager` for actions aligned with the tile, with explicit `Intent`s;
  - update dynamic shortcuts when the underlying feature is enabled/disabled;
  - for shortcuts/widgets `PendingIntent`s, prefer `FLAG_IMMUTABLE` (and `FLAG_UPDATE_CURRENT` when updating extras) to avoid tampering.
- Security, privacy, and UX:
  - require and validate appropriate permissions (e.g., VPN, hotspot, location) before executing privileged actions;
  - avoid starting full activities or sensitive flows from a locked device unless wrapped in `unlockAndRun`;
  - ensure clear, responsive UX with accurate tile states and minimal surprise for the user.

---

## Дополнительные вопросы (RU)
- Как вы реализуете более сложные/интерактивные тайлы (например, Android 14 `setResources` и TileService resources API)?
- Как архитектура тайла будет масштабироваться на разные устройства (телефон/планшет)?
- Какие UX best practices вы бы применили для тайлов (анимации, подзаголовок, обратная связь)?

## Follow-ups (EN)
- How would you implement more complex/interactive tiles (e.g., Android 14 `setResources` and the TileService resources API)?
- How would your tile architecture scale across different devices (phone/tablet)?
- Which UX best practices would you apply for tiles (animations, subtitle, feedback)?

## Ссылки (RU)
- [[c-android-surfaces]]
- https://developer.android.com/develop/ui/views/quicksettings

## References (EN)
- [[c-android-surfaces]]
- https://developer.android.com/develop/ui/views/quicksettings

## Связанные вопросы (RU)

- [[c-android-surfaces]]

## Related Questions (EN)

- [[c-android-surfaces]]
