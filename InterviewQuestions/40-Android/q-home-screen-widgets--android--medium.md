---
id: android-193
title: Home Screen Widgets / Виджеты домашнего экрана
aliases: [Home Screen Widgets, Виджеты домашнего экрана]
topic: android
subtopics:
  - ui-views
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android-components
  - q-how-compose-draws-on-screen--android--hard
  - q-how-to-break-text-by-screen-width--android--easy
  - q-recyclerview-viewtypes-delegation--android--medium
  - q-what-is-broadcastreceiver--android--easy
  - q-what-is-known-about-recyclerview--android--easy
  - q-which-event-is-called-when-user-touches-screen--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-views, difficulty/medium, widgets]
date created: Saturday, November 1st 2025, 12:46:51 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---

# Вопрос (RU)
> Виджеты домашнего экрана

# Question (EN)
> Home Screen Widgets

## Ответ (RU)
**Виджеты домашнего экрана** в Android реализуются через App Widget framework, основным компонентом которого является `AppWidgetProvider` (наследник `BroadcastReceiver`). Виджет отображается в приложении-хосте (чаще всего лаунчер) и позволяет показывать данные и выполнять действия без открытия полного приложения.

Ключевые моменты:
- Виджет — это мини-интерфейс приложения, размещённый в другом процессе (host app).
- Разметка виджета отрисовывается через `RemoteViews`.
- Обновления приходят через broadcast-ы и управляются `AppWidgetManager`.

**Категории виджетов:**

**1. Информационные (Information widgets):**
Показывают важные данные и обновляют их по мере изменения.
Примеры: погода, часы, курсы акций, спорт, календарь.

**2. Коллекции (Collection widgets):**
Отображают список/набор однотипных элементов (новости, письма, сообщения, фото и т.п.).

**3. Управляющие (Control widgets):**
Предоставляют быстрый доступ к действиям: управление плеером, переключатели и т.п.

**4. Гибридные (Hybrid widgets):**
Сочетают данные и управление (например, плеер с названием трека и кнопками).

**Шаги создания виджета:**

**1. Разметка (layout):**

```xml
<!-- res/layout/widget_layout.xml -->
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="8dp">

    <TextView
        android:id="@+id/widget_title"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="My Widget"
        android:textSize="16sp"
        android:textStyle="bold" />

    <TextView
        android:id="@+id/widget_content"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Content here" />

    <Button
        android:id="@+id/widget_button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Update" />
</LinearLayout>
```

(Используются только `View`, поддерживаемые `RemoteViews`.)

**2. XML метаданные виджета:**

```xml
<!-- res/xml/widget_info.xml -->
<appwidget-provider
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="250dp"
    android:minHeight="110dp"
    android:updatePeriodMillis="1800000"
    android:initialLayout="@layout/widget_layout"
    android:resizeMode="horizontal|vertical"
    android:widgetCategory="home_screen"
    android:previewImage="@drawable/widget_preview" />
```

(На современных версиях Android значения `android:updatePeriodMillis` меньше 30 минут, как правило, не используются системой для периодических обновлений; 0 отключает автоматическое периодическое обновление.)

**3. AppWidgetProvider:**

```kotlin
class MyWidgetProvider : AppWidgetProvider() {

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        appWidgetIds.forEach { appWidgetId ->
            updateWidget(context, appWidgetManager, appWidgetId)
        }
    }

    override fun onEnabled(context: Context) {
        // Вызывается при добавлении первого экземпляра виджета
        super.onEnabled(context)
    }

    override fun onDisabled(context: Context) {
        // Вызывается при удалении последнего экземпляра виджета
        super.onDisabled(context)
    }

    override fun onDeleted(context: Context, appWidgetIds: IntArray) {
        // Вызывается при удалении конкретных экземпляров виджета
        super.onDeleted(context, appWidgetIds)
    }

    internal fun updateWidget(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int
    ) {
        // Создаём RemoteViews (рендерится в процессе хоста)
        val views = RemoteViews(context.packageName, R.layout.widget_layout)

        // Обновляем содержимое
        views.setTextViewText(R.id.widget_title, "Updated Title")
        views.setTextViewText(
            R.id.widget_content,
            "Updated at ${System.currentTimeMillis()}"
        )

        // Клик по кнопке инициирует обновление
        val intent = Intent(context, MyWidgetProvider::class.java).apply {
            action = AppWidgetManager.ACTION_APPWIDGET_UPDATE
            putExtra(AppWidgetManager.EXTRA_APPWIDGET_IDS, intArrayOf(appWidgetId))
        }
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        views.setOnClickPendingIntent(R.id.widget_button, pendingIntent)

        // Применяем обновление
        appWidgetManager.updateAppWidget(appWidgetId, views)
    }
}
```

**4. Объявление в AndroidManifest.xml:**

```xml
<receiver
    android:name=".MyWidgetProvider"
    android:exported="false">
    <intent-filter>
        <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
    </intent-filter>
    <meta-data
        android:name="android.appwidget.provider"
        android:resource="@xml/widget_info" />
</receiver>
```

(Использование `android:exported="false"` безопасно для современных конфигураций: хосты используют явные intent-ы к конкретному компоненту. Учитывайте требования целевой версии SDK и документацию.)

**Методы жизненного цикла виджета:**

| Метод | Описание |
|-------|----------|
| `onEnabled()` | Вызывается при добавлении первого экземпляра виджета на экран |
| `onDisabled()` | Вызывается при удалении последнего экземпляра виджета |
| `onUpdate()` | Вызывается при обновлении; содержит массив `appWidgetIds` для обновления |
| `onDeleted()` | Вызывается при удалении отдельных экземпляров виджета |
| `onReceive()` | Вызывается для каждого broadcast; обычно делегируем в super и обрабатываем только нужные action-ы |

**RemoteViews для UI виджета:**

Так как разметка виджета исполняется в процессе хоста, прямой доступ к `View` невозможен — используются `RemoteViews` и набор допустимых операций:

```kotlin
val views = RemoteViews(context.packageName, R.layout.widget_layout)

// Установка текста
views.setTextViewText(R.id.widget_title, "New Title")

// Установка изображения
views.setImageViewResource(R.id.widget_icon, R.drawable.ic_icon)

// Управление видимостью
views.setViewVisibility(R.id.widget_content, View.VISIBLE)

// Обработчик клика для открытия Activity
val intent = Intent(context, MainActivity::class.java)
val pendingIntent = PendingIntent.getActivity(
    context,
    0,
    intent,
    PendingIntent.FLAG_IMMUTABLE
)
views.setOnClickPendingIntent(R.id.widget_button, pendingIntent)

// Применение обновления
appWidgetManager.updateAppWidget(appWidgetId, views)
```

Список поддерживаемых layout-ов и `View` в `RemoteViews` ограничен; использование неподдерживаемых элементов приведёт к ошибкам.

**Ограничения виджетов:**

**1. Жесты:**
- Поддерживаются нажатия через `setOnClickPendingIntent`.
- Прокрутка поддерживается опосредованно через коллекции/скроллируемые `View`, такие как `ListView`, `GridView`, `StackView` при использовании с `RemoteViewsService`.
- Произвольные сложные жесты недоступны.

**2. Layout и `View`:**
- Типично поддерживаются: `FrameLayout`, `LinearLayout`, `RelativeLayout`, `GridLayout`.
- Типично поддерживаемые виджеты: `TextView`, `Button`, `ImageView`, `ImageButton`, `ProgressBar`,
  `ListView`, `GridView`, `StackView`, `AdapterViewFlipper`, `ViewFlipper`, `Chronometer`, `AnalogClock` (часть устарела или зависит от хоста).
- Точный список см. в актуальной документации; неподдерживаемые элементы приводят к ошибкам в рантайме.

**3. Ограничения по времени и ресурсам:**
- Код в `onReceive`/`onUpdate` должен выполняться быстро: действуют ограничения на время выполнения broadcast receiver-ов (при превышении возможен ANR или завершение процесса).
- Длительные операции (сеть, БД и т.п.) нужно выносить в `Service`, `JobIntentService` или `WorkManager` и после завершения обновлять виджет через `AppWidgetManager`.
- Частые обновления расходуют батарею; используйте разумные интервалы и по возможности push-стиль обновлений (события/уведомления вместо постоянного опроса).

**Продвинутые возможности:**

**1. Виджет-коллекция (пример с ListView):**

```kotlin
class CollectionWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        appWidgetIds.forEach { appWidgetId ->
            val intent = Intent(context, WidgetService::class.java).apply {
                putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
                data = Uri.parse(toUri(Intent.URI_INTENT_SCHEME))
            }

            val views = RemoteViews(context.packageName, R.layout.widget_collection)
            views.setRemoteAdapter(R.id.widget_list, intent)
            views.setEmptyView(R.id.widget_list, R.id.empty_view)

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }
}

class WidgetService : RemoteViewsService() {
    override fun onGetViewFactory(intent: Intent): RemoteViewsFactory {
        return WidgetRemoteViewsFactory(applicationContext)
    }
}

class WidgetRemoteViewsFactory(
    private val context: Context
) : RemoteViewsService.RemoteViewsFactory {

    private val items = mutableListOf<String>()

    override fun onCreate() {
        items.addAll(listOf("Item 1", "Item 2", "Item 3"))
    }

    override fun getCount(): Int = items.size

    override fun getViewAt(position: Int): RemoteViews {
        return RemoteViews(context.packageName, R.layout.widget_list_item).apply {
            setTextViewText(R.id.item_text, items[position])
        }
    }

    override fun getLoadingView(): RemoteViews? = null
    override fun getViewTypeCount(): Int = 1
    override fun getItemId(position: Int): Long = position.toLong()
    override fun hasStableIds(): Boolean = true
    override fun onDataSetChanged() { /* Перезагрузить данные при необходимости */ }
    override fun onDestroy() { items.clear() }
}
```

**2. Конфигурационная `Activity`:**

`Activity`, которая может быть запущена при добавлении виджета для настройки параметров.

```kotlin
class WidgetConfigActivity : AppCompatActivity() {
    private var appWidgetId = AppWidgetManager.INVALID_APPWIDGET_ID

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_widget_config)

        // Результат по умолчанию — CANCELED
        setResult(RESULT_CANCELED)

        // Получаем ID виджета из Intent
        appWidgetId = intent?.extras?.getInt(
            AppWidgetManager.EXTRA_APPWIDGET_ID,
            AppWidgetManager.INVALID_APPWIDGET_ID
        ) ?: AppWidgetManager.INVALID_APPWIDGET_ID

        if (appWidgetId == AppWidgetManager.INVALID_APPWIDGET_ID) {
            finish()
            return
        }

        val saveButton = findViewById<Button>(R.id.save_button)

        saveButton.setOnClickListener {
            val configValue = "some_value" // получить из UI
            saveConfiguration(configValue)

            // Обновляем виджет
            val appWidgetManager = AppWidgetManager.getInstance(this)
            MyWidgetProvider().updateWidget(this, appWidgetManager, appWidgetId)

            // Возвращаем результат
            val resultValue = Intent().apply {
                putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
            }
            setResult(RESULT_OK, resultValue)
            finish()
        }
    }

    private fun saveConfiguration(configValue: String) {
        val prefs = getSharedPreferences("widget_prefs", Context.MODE_PRIVATE)
        prefs.edit()
            .putString("widget_$appWidgetId", configValue)
            .apply()
    }
}
```

Во `widget_info.xml`:

```xml
<appwidget-provider
    ...
    android:configure="com.example.WidgetConfigActivity" />
```

**3. Обновление виджета из `Service`:**

```kotlin
class WidgetUpdateService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Выполнить долгую операцию не в главном потоке при необходимости
        updateWidgetData()

        val appWidgetManager = AppWidgetManager.getInstance(this)
        val componentName = ComponentName(this, MyWidgetProvider::class.java)
        val appWidgetIds = appWidgetManager.getAppWidgetIds(componentName)

        // Обновляем виджеты напрямую через AppWidgetManager / логику провайдера
        MyWidgetProvider().onUpdate(this, appWidgetManager, appWidgetIds)

        stopSelf()
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun updateWidgetData() {
        // Загрузка данных, вычисления и т.п. (в фоне)
    }
}
```

(В реальном коде долгие операции должны выполняться в фоновом потоке; вызов `onUpdate` экземпляра провайдера из `Service` допустим как переиспользование логики, но ключевым является обновление через `AppWidgetManager`.)

**Лучшие практики:**

1. Держите виджет лёгким; не блокируйте `onReceive`/`onUpdate`.
2. Используйте фоновые механизмы (`Service`, `WorkManager` и др.) для долгих или сетевых операций.
3. Оптимизируйте частоту обновлений; избегайте слишком частых периодических обновлений, по возможности используйте push-обновления.
4. Добавляйте информативный `android:previewImage`.
5. Обрабатывайте разные размеры с помощью адаптивной разметки и `resizeMode`.
6. Используйте корректные флаги `PendingIntent`, включая `FLAG_IMMUTABLE` (и `FLAG_MUTABLE`, когда это требуется) для Android 12+.
7. Тестируйте на разных лаунчерах/хостах.
8. Для коллекций предоставляйте empty view.

## Answer (EN)
**Home screen widgets** are implemented via the App Widget framework, primarily using a specialized `BroadcastReceiver` subclass called `AppWidgetProvider`. They expose interactive components that appear on the home screen (and sometimes on other host apps) to show data and trigger actions without fully opening the app.

Widgets are mini app views that:
- are hosted by another app (home screen / launcher / host),
- are rendered via `RemoteViews` in the host process,
- are driven by broadcasts and updates from your app.

**Widget Categories:**

Typical conceptual categories:

**1. Information widgets:**

Show a few key pieces of information and keep them up to date.

Examples:
- Weather widgets
- Clock widgets
- Sports score trackers
- Stock price widgets
- Calendar widgets

**2. Collection widgets:**

Display multiple items of the same type (emails, messages, articles, photos, etc.).

Examples:
- Gallery app widget (photos)
- News app widget (articles)
- Email/messaging widget (messages)
- Music playlist widget

**3. Control widgets:**

Expose frequently used actions/controls directly on the home screen.

Examples:
- Music player controls (play, pause, skip)
- Flashlight toggle
- WiFi/Bluetooth toggles
- Camera shortcut

**4. Hybrid widgets:**

Combine information and controls (for example, a music player widget that shows track info and playback controls).

**Steps to Create a Widget:**

**1. Define a layout file:**

Note: You must use views supported by `RemoteViews`.

```xml
<!-- res/layout/widget_layout.xml -->
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="8dp">

    <TextView
        android:id="@+id/widget_title"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="My Widget"
        android:textSize="16sp"
        android:textStyle="bold" />

    <TextView
        android:id="@+id/widget_content"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Content here" />

    <Button
        android:id="@+id/widget_button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Update" />
</LinearLayout>
```

**2. Create XML metadata file:**

Describes widget properties (size, update behavior, etc.). On modern Android, `android:updatePeriodMillis` values below 30 minutes are generally not used by the system for periodic updates; `0` disables periodic updates entirely.

```xml
<!-- res/xml/widget_info.xml -->
<appwidget-provider
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="250dp"
    android:minHeight="110dp"
    android:updatePeriodMillis="1800000"
    android:initialLayout="@layout/widget_layout"
    android:resizeMode="horizontal|vertical"
    android:widgetCategory="home_screen"
    android:previewImage="@drawable/widget_preview" />
```

**3. Create an AppWidgetProvider (`BroadcastReceiver`):**

```kotlin
class MyWidgetProvider : AppWidgetProvider() {

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        // Called for every update of the widget
        appWidgetIds.forEach { appWidgetId ->
            updateWidget(context, appWidgetManager, appWidgetId)
        }
    }

    override fun onEnabled(context: Context) {
        // Called when the first instance is added to home screen
        super.onEnabled(context)
    }

    override fun onDisabled(context: Context) {
        // Called when the last instance is removed from home screen
        super.onDisabled(context)
    }

    override fun onDeleted(context: Context, appWidgetIds: IntArray) {
        // Called when widget instances are removed
        super.onDeleted(context, appWidgetIds)
    }

    internal fun updateWidget(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int
    ) {
        // Create RemoteViews (inflated in the host process)
        val views = RemoteViews(context.packageName, R.layout.widget_layout)

        // Update content
        views.setTextViewText(R.id.widget_title, "Updated Title")
        views.setTextViewText(
            R.id.widget_content,
            "Updated at ${System.currentTimeMillis()}"
        )

        // Set click listener to request an update
        val intent = Intent(context, MyWidgetProvider::class.java).apply {
            action = AppWidgetManager.ACTION_APPWIDGET_UPDATE
            putExtra(AppWidgetManager.EXTRA_APPWIDGET_IDS, intArrayOf(appWidgetId))
        }
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        views.setOnClickPendingIntent(R.id.widget_button, pendingIntent)

        // Push update to this widget instance
        appWidgetManager.updateAppWidget(appWidgetId, views)
    }
}
```

**4. Declare widget in AndroidManifest.xml:**

```xml
<receiver
    android:name=".MyWidgetProvider"
    android:exported="false">
    <intent-filter>
        <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
    </intent-filter>
    <meta-data
        android:name="android.appwidget.provider"
        android:resource="@xml/widget_info" />
</receiver>
```

(Using `android:exported="false"` is a safe default for modern Android: app widget hosts send explicit broadcasts to your provider. Always verify against the current SDK level requirements.)

**Widget Lifecycle Methods:**

| Method | Description |
|--------|-------------|
| `onEnabled()` | Called the first time an instance of your widget is added to the home screen |
| `onDisabled()` | Called when the last instance of your widget is removed |
| `onUpdate()` | Called for updates of the widget; receives the IDs of widgets that should be updated |
| `onDeleted()` | Called when specific widget instances are removed from the home screen |
| `onReceive()` | Called for every broadcast; typically delegate to super and handle only relevant actions |

**RemoteViews - Building Widget UI:**

Widget views are hosted in another app's process. You cannot call `findViewById` or manipulate views directly. Instead, you describe operations via `RemoteViews`:

```kotlin
val views = RemoteViews(context.packageName, R.layout.widget_layout)

// Set text
views.setTextViewText(R.id.widget_title, "New Title")

// Set image
views.setImageViewResource(R.id.widget_icon, R.drawable.ic_icon)

// Set visibility
views.setViewVisibility(R.id.widget_content, View.VISIBLE)

// Set click handler to open Activity
val intent = Intent(context, MainActivity::class.java)
val pendingIntent = PendingIntent.getActivity(
    context,
    0,
    intent,
    PendingIntent.FLAG_IMMUTABLE
)
views.setOnClickPendingIntent(R.id.widget_button, pendingIntent)

// Apply update
appWidgetManager.updateAppWidget(appWidgetId, views)
```

Only a limited, documented set of layouts and views are supported by `RemoteViews`; unsupported ones will cause runtime errors.

**Widget Limitations:**

**1. Limited Gesture Support:**

Because widgets coexist with launcher navigation and rely on supported views:
- Clicks (via `setOnClickPendingIntent`) are supported.
- Scroll is supported indirectly through collection/scrollable views like `ListView`, `GridView`, `StackView` when used with `RemoteViewsService`.
- Arbitrary complex gestures are not supported.

**2. Limited Layout and `View` Support:**

Common supported layouts:
- `FrameLayout`
- `LinearLayout`
- `RelativeLayout`
- `GridLayout`

Common supported widgets:
- `TextView`, `Button`, `ImageView`, `ImageButton`, `ProgressBar`
- `ListView`, `GridView`, `StackView`, `AdapterViewFlipper`, `ViewFlipper`
- `Chronometer`, `AnalogClock` (deprecated / host-dependent)

(This list is not exhaustive; always check the latest documentation.)

**3. Runtime Restrictions:**

Widget updates are delivered via broadcasts, subject to receiver execution limits:
- Code in `onReceive`/`onUpdate` must complete quickly; long work risks ANR or the process being killed.
- Offload long-running or network work to a `Service`, `JobIntentService`, or `WorkManager` and then update the widget via `AppWidgetManager`.

Additionally:
- Frequent updates drain battery; use reasonable intervals or push-style events.

**Advanced Widget Features:**

**1. Collection Widget (ListView example):**

```kotlin
class CollectionWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        appWidgetIds.forEach { appWidgetId ->
            val intent = Intent(context, WidgetService::class.java).apply {
                putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
                data = Uri.parse(toUri(Intent.URI_INTENT_SCHEME))
            }

            val views = RemoteViews(context.packageName, R.layout.widget_collection)
            views.setRemoteAdapter(R.id.widget_list, intent)
            views.setEmptyView(R.id.widget_list, R.id.empty_view)

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }
}

class WidgetService : RemoteViewsService() {
    override fun onGetViewFactory(intent: Intent): RemoteViewsFactory {
        return WidgetRemoteViewsFactory(applicationContext)
    }
}

class WidgetRemoteViewsFactory(
    private val context: Context
) : RemoteViewsService.RemoteViewsFactory {

    private val items = mutableListOf<String>()

    override fun onCreate() {
        items.addAll(listOf("Item 1", "Item 2", "Item 3"))
    }

    override fun getCount(): Int = items.size

    override fun getViewAt(position: Int): RemoteViews {
        return RemoteViews(context.packageName, R.layout.widget_list_item).apply {
            setTextViewText(R.id.item_text, items[position])
        }
    }

    override fun getLoadingView(): RemoteViews? = null
    override fun getViewTypeCount(): Int = 1
    override fun getItemId(position: Int): Long = position.toLong()
    override fun hasStableIds(): Boolean = true
    override fun onDataSetChanged() { /* Reload data if needed */ }
    override fun onDestroy() { items.clear() }
}
```

**2. Configuration `Activity`:**

Optional activity launched when the user adds the widget.

```kotlin
class WidgetConfigActivity : AppCompatActivity() {
    private var appWidgetId = AppWidgetManager.INVALID_APPWIDGET_ID

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_widget_config)

        // Result is CANCELED by default
        setResult(RESULT_CANCELED)

        // Get widget ID from intent
        appWidgetId = intent?.extras?.getInt(
            AppWidgetManager.EXTRA_APPWIDGET_ID,
            AppWidgetManager.INVALID_APPWIDGET_ID
        ) ?: AppWidgetManager.INVALID_APPWIDGET_ID

        if (appWidgetId == AppWidgetManager.INVALID_APPWIDGET_ID) {
            finish()
            return
        }

        val saveButton = findViewById<Button>(R.id.save_button)

        saveButton.setOnClickListener {
            val configValue = "some_value" // get from UI
            saveConfiguration(configValue)

            // Update widget
            val appWidgetManager = AppWidgetManager.getInstance(this)
            MyWidgetProvider().updateWidget(this, appWidgetManager, appWidgetId)

            // Return result
            val resultValue = Intent().apply {
                putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
            }
            setResult(RESULT_OK, resultValue)
            finish()
        }
    }

    private fun saveConfiguration(configValue: String) {
        val prefs = getSharedPreferences("widget_prefs", Context.MODE_PRIVATE)
        prefs.edit()
            .putString("widget_$appWidgetId", configValue)
            .apply()
    }
}
```

In `widget_info.xml`:

```xml
<appwidget-provider
    ...
    android:configure="com.example.WidgetConfigActivity" />
```

**3. Updating Widget from `Service`:**

```kotlin
class WidgetUpdateService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Perform long-running operation off main thread if needed
        updateWidgetData()

        val appWidgetManager = AppWidgetManager.getInstance(this)
        val componentName = ComponentName(this, MyWidgetProvider::class.java)
        val appWidgetIds = appWidgetManager.getAppWidgetIds(componentName)

        // Reuse provider logic or call AppWidgetManager directly to push updates
        MyWidgetProvider().onUpdate(this, appWidgetManager, appWidgetIds)

        stopSelf()
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun updateWidgetData() {
        // Fetch data, perform calculations, etc. on a background thread
    }
}
```

(Real implementations must ensure long work happens off the main thread; the key mechanism is updating via `AppWidgetManager`.)

**Best Practices:**

1. Keep widgets lightweight; do not block `onReceive`/`onUpdate`.
2. Use background work mechanisms (`Service`, `WorkManager`, etc.) for long or network operations.
3. Optimize update frequency; avoid very frequent periodic updates and prefer push-style updates where possible.
4. Provide a meaningful preview (`android:previewImage`).
5. Handle different sizes with responsive layouts and `resizeMode`.
6. Use appropriate `PendingIntent` flags, including `FLAG_IMMUTABLE` (and `FLAG_MUTABLE` where required) for Android 12+.
7. Test on different launchers/hosts.
8. Provide an empty view for collection widgets.

## Follow-ups

- [[q-recyclerview-viewtypes-delegation--android--medium]]
- [[q-what-is-broadcastreceiver--android--easy]]
- [[q-what-is-known-about-recyclerview--android--easy]]

## References

- https://developer.android.com/develop/ui/views
- https://developer.android.com/docs
- https://developer.android.com/guide/topics/appwidgets/overview

## Related Questions

### Prerequisites / Concepts

- [[c-android-components]]
- [[q-recyclerview-viewtypes-delegation--android--medium]]
- [[q-what-is-broadcastreceiver--android--easy]]
- [[q-what-is-known-about-recyclerview--android--easy]]
