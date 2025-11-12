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
// AndroidManifest.xml:
// <service
//     android:name=".SyncTileService"
//     android:label="@string/tile_label"
//     android:permission="android.permission.BIND_QUICK_SETTINGS_TILE"
//     android:exported="false">
//     <intent-filter>
//         <action android:name="android.service.quicksettings.action.QS_TILE" />
//     </intent-filter>
// </service>

class SyncTileService : TileService() {

    override fun onStartListening() {
        super.onStartListening()
        // Обновляем состояние тайла из общего источника данных (source of truth)
        qsTile?.apply {
            state = if (isSyncEnabled()) Tile.STATE_ACTIVE else Tile.STATE_INACTIVE
            label = getString(R.string.tile_label)
            updateTile()
        }
    }

    override fun onClick() {
        super.onClick()
        // Обрабатываем нажатие: при заблокированном устройстве используем unlockAndRun,
        // чтобы выполнить действие после снятия блокировки при необходимости взаимодействия с UI.
        if (!isLocked) {
            toggleSync()
        } else {
            unlockAndRun { toggleSync() }
        }
    }

    override fun onTileAdded() {
        super.onTileAdded()
        // Инициализируем начальное состояние из общего источника данных,
        // чтобы тайл не был в неопределённом состоянии до onStartListening()
        qsTile?.apply {
            state = if (isSyncEnabled()) Tile.STATE_ACTIVE else Tile.STATE_INACTIVE
            label = getString(R.string.tile_label)
            updateTile()
        }
    }

    override fun onStopListening() {
        super.onStopListening()
        // Отписываемся от наблюдений/очищаем ресурсы, связанные с onStartListening()
    }
}
```

- `onStartListening()` синхронизирует визуальное состояние тайла с общим состоянием приложения и вызывает `updateTile()`.
- `onTileAdded()` гарантирует корректное начальное состояние тайла на базе того же источника истины.
- `onStopListening()` используется для отписок и очистки ресурсов; важно не держать долгоживущих ссылок на контекст `TileService`.
- В `onClick()` реализуйте переключение; при заблокированном устройстве используйте `unlockAndRun { ... }` для действий, требующих разблокировки.

### Фоновая работа

- Держите `onClick()`/`onStartListening()` лёгкими: долгие операции выносите в `ForegroundService` с подходящим типом или `WorkManager` (включая expedited work при необходимости), вместо прямых блокирующих вызовов.
- Для открытия UI используйте `startActivityAndCollapse()` из `TileService`, чтобы свернуть шторку и показать нужный экран.

### Состояние и синхронизация

- Храните состояние в общем источнике (`DataStore`/`Room` или иной single source of truth), чтобы и приложение, и `TileService` работали с одним state.
- Наблюдайте изменения через `Flow`/другие реактивные механизмы, создавая `CoroutineScope`, привязанный к жизненному циклу тайла (подписка в `onStartListening()`, отписка в `onStopListening()`), чтобы избежать утечек.
- При изменении состояния из приложения вызывайте `TileService.requestListeningState(context, componentName)`, чтобы система триггерила `onStartListening()` и вы могли обновить `qsTile`.

### App Shortcuts и виджеты

- Используйте `ShortcutManager` для App Shortcuts, которые отражают те же действия/режимы, что и тайл, с явными `Intent`.
- Обновляйте dynamic shortcuts при включении/выключении функциональности, связанной с тайлом, чтобы пользователь видел актуальные действия.
- Для shortcuts/виджетов применяйте явные `Intent` и `PendingIntent` с корректной изменяемостью:
  - используйте `FLAG_IMMUTABLE`, когда extras не должны меняться извне;
  - дополняйте `FLAG_UPDATE_CURRENT`, если нужно обновлять extras при переиспользовании `PendingIntent`;
  - это помогает избежать подмены данных и соответствует требованиям безопасности современных API.

### Безопасность, приватность и UX

- Проверяйте и запрашивайте необходимые разрешения (например, связанные с VPN/hotspot/location) через обычные механизмы приложения; сам `TileService` не даёт дополнительных привилегий.
- Не запускайте чувствительные потоки с заблокированного экрана без необходимости; для действий, требующих взаимодействия пользователя или разблокировки, используйте `unlockAndRun { ... }` или открывайте Activity через `startActivityAndCollapse()`.
- Проектируйте UX тайла понятно: мгновенный отклик (optimistic UI при необходимости), корректные состояния, отсутствие неожиданных сайд-эффектов.

---

## Answer (EN)

- Implement a `TileService` (declared in the manifest with `android.permission.BIND_QUICK_SETTINGS_TILE` and the QS_TILE intent-filter) and handle its lifecycle callbacks:
  - in `onStartListening()`, refresh the tile state from the shared app state (single source of truth) and call `qsTile.updateTile()`;
  - in `onTileAdded()`, initialize the tile label and state from the same shared source so the initial tile is consistent;
  - in `onStopListening()`, stop observations and release resources tied to the listening lifecycle; avoid holding long-lived references to the `TileService` context;
  - in `onClick()`, toggle behavior; when the device is locked, use `unlockAndRun { ... }` for work that should happen after keyguard dismissal.
- Keep `onClick()`/`onStartListening()` light; offload long-running or network work to:
  - a `ForegroundService` with the appropriate foreground service type; or
  - `WorkManager` (including expedited work when appropriate), instead of blocking inside the tile callbacks.
- Use `startActivityAndCollapse()` when you need to open UI from the tile while collapsing the shade.
- Persist tile/app state in shared storage (e.g., `DataStore`/`Room` or another single source of truth) so both the app and `TileService` read/write the same state.
- When state changes from the app side, call `TileService.requestListeningState(context, componentName)` so the system invokes `onStartListening()` for that tile and you can update `qsTile` accordingly.
- For App Shortcuts and widgets:
  - use `ShortcutManager` for actions aligned with the tile, with explicit `Intent`s that map to the same features;
  - update dynamic shortcuts when the related feature is enabled/disabled so shortcuts stay in sync;
  - for shortcuts/widgets `PendingIntent`s, use correct mutability flags:
    - prefer `FLAG_IMMUTABLE` when extras should not be modifiable by other apps;
    - add `FLAG_UPDATE_CURRENT` when you need to update extras on an existing `PendingIntent`;
    - this prevents tampering and complies with modern Android security requirements.
- Security, privacy, and UX:
  - validate and request appropriate permissions (e.g., VPN, hotspot, location) via normal app flows; the tile itself does not bypass permission models;
  - avoid launching sensitive flows from a locked device unless gated via `unlockAndRun` or appropriate UX; use `startActivityAndCollapse()` for explicit navigation;
  - ensure clear, responsive UX with accurate tile states, fast feedback, and no surprising side effects.

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
