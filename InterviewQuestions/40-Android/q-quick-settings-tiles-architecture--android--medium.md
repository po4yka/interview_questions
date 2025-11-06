---
id: android-631
title: Quick Settings Tiles Architecture / Архитектура плиток Quick Settings
aliases:
  - Quick Settings Tiles Architecture
  - Архитектура плиток Quick Settings
topic: android
subtopics:
  - quick-settings
  - surfaces
  - shortcuts
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-android-surfaces
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/quick-settings
  - android/surfaces
  - android/shortcuts
  - difficulty/medium
sources:
  - url: https://developer.android.com/develop/ui/views/quicksettings
    note: Quick Settings tile guide
  - url: https://developer.android.com/develop/shortcutmanager
    note: App Shortcuts documentation
---

# Вопрос (RU)
> Как спроектировать плитку шторки (Quick Settings tile), синхронизировать её состояние с приложением, поддержать фоновые операции и обеспечить безопасные ярлыки/shortcuts?

# Question (EN)
> How do you architect a Quick Settings tile, keep it synchronized with the app state, support background work safely, and align it with shortcuts integration?

---

## Ответ (RU)

### TileService жизненный цикл

```kotlin
class SyncTileService : TileService() {

    override fun onStartListening() {
        super.onStartListening()
        qsTile.state = if (isSyncEnabled()) Tile.STATE_ACTIVE else Tile.STATE_INACTIVE
        qsTile.label = getString(R.string.tile_label)
        qsTile.updateTile()
    }

    override fun onClick() {
        super.onClick()
        if (!isLocked) {
            toggleSync()
        } else {
            unlockAndRun { toggleSync() }
        }
    }
}
```

- `onStartListening()` вызывается при открытии шторки → обновляйте UI.
- `unlockAndRun` запускает действие после разблокировки устройства.

### Фоновые операции

- Для длинных задач запускайте `ForegroundService` или `WorkManager` (Expedited).
- Используйте `TileService#startActivityAndCollapse` для UI потока.
- Учитывайте ограничения Android 13+: нельзя запускать фоновый сервис из background без разрешений.

### Синхронизация состояния

- Храните состояние в `DataStore`/`Room`; TileService читает напрямую.
- Подписывайтесь на обновления (`Flow`) через `lifecycleScope` + `asLiveData()` (TileService context).
- Отправляйте `sendBroadcast`/`TileService.requestListeningState` для обновления.

### App Shortcuts & Widgets

- Используйте `ShortcutManager` для действий, которые совпадают с плиткой.
- Обновляйте dynamic shortcuts при изменении состояния (например, enable/disable).
- Обеспечьте `PendingIntent` с `FLAG_IMMUTABLE`/`FLAG_UPDATE_CURRENT`.

### Безопасность

- Проверяйте привилегии перед выполнением действия (VPN/Hotspot tile требует разрешений).
- Обрабатывайте `isLocked` (плитка не должна вызывать полномасштабный UI без разблокировки).
- Логируйте использование для аналитики (с разрешением пользователя).

---

## Answer (EN)

- Implement `TileService`, refresh state in `onStartListening`, and toggle behavior in `onClick`, using `unlockAndRun` when necessary.
- Offload long-running work via foreground services or WorkManager; collapse the shade with `startActivityAndCollapse`.
- Persist tile state in shared storage (DataStore) and request listening updates when state changes outside the tile.
- Align with `ShortcutManager` and widgets so shortcuts reflect the same actions; keep intents immutable and secure.
- Handle locked-device scenarios, required permissions, and analytics responsibly.

---

## Follow-ups
- Как поддерживать interactive tiles (Android 14 Tile setResources)?
- Как синхронизировать плитку между несколькими устройствами (phone/tablet)?
- Какие UX best practices для обозначения прогресса (animation, subtitle)?

## References
- [[c-android-surfaces]]
- https://developer.android.com/develop/ui/views/quicksettings

## Related Questions

- [[c-android-surfaces]]
