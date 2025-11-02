---
id: android-193
title: "Home Screen Widgets / Виджеты домашнего экрана"
aliases: [Home Screen Widgets, Виджеты домашнего экрана]
topic: android
subtopics: [ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-recyclerview-viewtypes-delegation--android--medium, q-what-is-broadcastreceiver--android--easy, q-what-is-known-about-recyclerview--android--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [android/ui-views, difficulty/medium, widgets]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Android Home Screen Widgets / Виджеты Главного Экрана Android

**English**: What's a Widget?

## Answer (EN)
**Home screen widgets** are broadcast receivers that provide **interactive components** primarily used on the Android home screen. They typically display some kind of data and allow the user to perform actions with them.

Widgets are mini app views that can be embedded in other applications (like the home screen) and receive periodic updates. They provide users with quick access to app functionality without opening the full app.

**Widget Categories:**

Widgets typically fall into one of the following categories:

**1. Information widgets:**

Typically display a few crucial information elements that are important to a user and track how that information changes over time.

Examples:
- Weather widgets
- Clock widgets
- Sports score trackers
- Stock price widgets
- Calendar widgets

**2. Collection widgets:**

Specialize in displaying multitude elements of the same type, such as a collection of pictures, articles, emails, or messages.

Examples:
- Gallery app widget (photos)
- News app widget (articles)
- Email/messaging widget (messages)
- Music playlist widget

**3. Control widgets:**

The main purpose is to display often-used functions that the user can trigger right from the home screen without opening the app.

Examples:
- Music player controls (play, pause, skip)
- Flashlight toggle
- WiFi/Bluetooth toggles
- Camera shortcut

**4. Hybrid widgets:**

Combine elements of different types. For example, a music player widget is primarily a control widget but also keeps the user informed about the currently playing track (information widget).

**Steps to Create a Widget:**

**1. Define a layout file:**

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

This file describes the properties of the widget (size, update frequency, etc.):

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

**3. Create a BroadcastReceiver (AppWidgetProvider):**

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

    private fun updateWidget(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int
    ) {
        // Create RemoteViews
        val views = RemoteViews(context.packageName, R.layout.widget_layout)

        // Update content
        views.setTextViewText(R.id.widget_title, "Updated Title")
        views.setTextViewText(R.id.widget_content, "Updated at ${System.currentTimeMillis()}")

        // Set click listener
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

        // Update widget
        appWidgetManager.updateAppWidget(appWidgetId, views)
    }
}
```

**4. Declare widget in AndroidManifest.xml:**

```xml
<receiver
    android:name=".MyWidgetProvider"
    android:exported="true">
    <intent-filter>
        <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
    </intent-filter>
    <meta-data
        android:name="android.appwidget.provider"
        android:resource="@xml/widget_info" />
</receiver>
```

**Widget Lifecycle Methods:**

| Method | Description |
|--------|-------------|
| `onEnabled()` | Called the **first time** an instance of your widget is added to the home screen |
| `onDisabled()` | Called once the **last instance** of your widget is removed from the home screen |
| `onUpdate()` | Called for **every update** of the widget. Contains the ids of appWidgetIds for which an update is needed |
| `onDeleted()` | Called when widget **instance is removed** from the home screen |
| `onReceive()` | Called for **every broadcast** and before each of the above callback methods. You normally don't need to implement this |

**RemoteViews - Building Widget UI:**

Since widgets don't run in your app's process, you can't directly access UI elements. You must use `RemoteViews`:

```kotlin
val views = RemoteViews(context.packageName, R.layout.widget_layout)

// Set text
views.setTextViewText(R.id.widget_title, "New Title")

// Set image
views.setImageViewResource(R.id.widget_icon, R.drawable.ic_icon)

// Set visibility
views.setViewVisibility(R.id.widget_content, View.VISIBLE)

// Set click handler
val intent = Intent(context, MainActivity::class.java)
val pendingIntent = PendingIntent.getActivity(
    context,
    0,
    intent,
    PendingIntent.FLAG_IMMUTABLE
)
views.setOnClickPendingIntent(R.id.widget_button, pendingIntent)

// Update widget
appWidgetManager.updateAppWidget(appWidgetId, views)
```

**Widget Limitations:**

**1. Limited Gesture Support:**

Because widgets live on the home screen, they have to co-exist with navigation. Only these gestures are available:
- **Touch** (click)
- **Vertical swipe**

**2. Limited Layout and View Support:**

RemoteViews support only specific layouts and widgets:

**Supported Layouts:**
- `FrameLayout`
- `LinearLayout`
- `RelativeLayout`
- `GridLayout`

**Supported Widgets:**
- `AnalogClock`
- `Button`
- `Chronometer`
- `ImageButton`
- `ImageView`
- `ProgressBar`
- `TextView`
- `ViewFlipper`
- `ListView`
- `GridView`
- `StackView`
- `AdapterViewFlipper`

**3. Runtime Restrictions:**

A widget has the same runtime restrictions as a normal broadcast receiver:
- **5 seconds** to finish processing
- Time-consuming operations should be performed in a **Service**
- Update widgets from the service

**Advanced Widget Features:**

**1. Widget with ListView (Collection Widget):**

```kotlin
// Widget provider
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

// RemoteViewsService
class WidgetService : RemoteViewsService() {
    override fun onGetViewFactory(intent: Intent): RemoteViewsFactory {
        return WidgetRemoteViewsFactory(applicationContext, intent)
    }
}

// RemoteViewsFactory
class WidgetRemoteViewsFactory(
    private val context: Context,
    intent: Intent
) : RemoteViewsService.RemoteViewsFactory {

    private val items = mutableListOf<String>()

    override fun onCreate() {
        // Initialize data
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
    override fun onDataSetChanged() {
        // Refresh data
    }
    override fun onDestroy() {
        items.clear()
    }
}
```

**2. Configuration Activity:**

Optional activity launched when user adds the widget:

```kotlin
class WidgetConfigActivity : AppCompatActivity() {
    private var appWidgetId = AppWidgetManager.INVALID_APPWIDGET_ID

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_widget_config)

        // Set result to CANCELED initially
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

        // Setup UI and save configuration
        saveButton.setOnClickListener {
            saveConfiguration()

            // Update widget
            val appWidgetManager = AppWidgetManager.getInstance(this)
            MyWidgetProvider.updateWidget(this, appWidgetManager, appWidgetId)

            // Return result
            val resultValue = Intent().apply {
                putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
            }
            setResult(RESULT_OK, resultValue)
            finish()
        }
    }

    private fun saveConfiguration() {
        // Save widget configuration to SharedPreferences
        val prefs = getSharedPreferences("widget_prefs", Context.MODE_PRIVATE)
        prefs.edit()
            .putString("widget_$appWidgetId", configValue)
            .apply()
    }
}
```

Declare in `widget_info.xml`:

```xml
<appwidget-provider
    ...
    android:configure="com.example.WidgetConfigActivity" />
```

**3. Updating Widget from Service:**

```kotlin
class WidgetUpdateService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Perform long-running operation
        updateWidgetData()

        // Update all widgets
        val appWidgetManager = AppWidgetManager.getInstance(this)
        val componentName = ComponentName(this, MyWidgetProvider::class.java)
        val appWidgetIds = appWidgetManager.getAppWidgetIds(componentName)

        MyWidgetProvider().onUpdate(this, appWidgetManager, appWidgetIds)

        stopSelf()
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun updateWidgetData() {
        // Fetch data, perform calculations, etc.
    }
}
```

**Best Practices:**

1. **Keep widgets lightweight** — don't perform heavy operations
2. **Use Services for updates** — avoid blocking the broadcast receiver
3. **Optimize update frequency** — don't update too often (battery drain)
4. **Provide meaningful preview** — use `previewImage` in widget metadata
5. **Handle configuration changes** — support different screen sizes
6. **Use PendingIntent.FLAG_IMMUTABLE** — for Android 12+ security
7. **Test on different launchers** — widgets may behave differently
8. **Provide fallback** — empty view for collection widgets

**Summary:**

- **Widgets**: Interactive components on home screen
- **Categories**: Information, Collection, Control, Hybrid
- **Components**: Layout, metadata XML, AppWidgetProvider, manifest entry
- **Lifecycle**: onEnabled, onUpdate, onDeleted, onDisabled
- **RemoteViews**: Build UI for widgets (limited view support)
- **Limitations**: Gesture support, view types, 5-second execution limit
- **Advanced**: Collection widgets (ListView), configuration activity, service updates

**Sources:**
- [App widgets overview](https://developer.android.com/guide/topics/appwidgets/overview)
- [Android widgets tutorial](https://www.vogella.com/tutorials/AndroidWidgets/article.html)

## Ответ (RU)
**Виджеты главного экрана** — это broadcast receivers, которые предоставляют **интерактивные компоненты**, в основном используемые на главном экране Android. Они обычно отображают какие-то данные и позволяют пользователю выполнять с ними действия.

Виджеты — это мини-представления приложений, которые могут быть встроены в другие приложения (например, главный экран) и получать периодические обновления. Они предоставляют пользователям быстрый доступ к функциональности приложения без открытия полного приложения.

**Категории виджетов:**

**1. Information widgets (информационные виджеты):**

Отображают несколько важных элементов информации и отслеживают их изменения.

Примеры: виджеты погоды, часов, спортивных результатов, цен акций, календаря

**2. Collection widgets (виджеты коллекций):**

Специализируются на отображении множества элементов одного типа.

Примеры: виджет галереи (фотографии), виджет новостей (статьи), виджет электронной почты/сообщений

**3. Control widgets (виджеты управления):**

Основная цель — отображать часто используемые функции, которые пользователь может активировать прямо с главного экрана.

Примеры: управление музыкальным плеером (воспроизведение, пауза, пропуск), переключение фонарика, WiFi/Bluetooth

**4. Hybrid widgets (гибридные виджеты):**

Объединяют элементы разных типов. Например, виджет музыкального плеера — это прежде всего виджет управления, но он также информирует пользователя о текущем треке.

**Шаги создания виджета:**

**1. Определить layout файл:**

```xml
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <TextView
        android:id="@+id/widget_title"
        android:text="My Widget" />

    <Button
        android:id="@+id/widget_button"
        android:text="Update" />
</LinearLayout>
```

**2. Создать XML файл метаданных:**

```xml
<!-- res/xml/widget_info.xml -->
<appwidget-provider
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="250dp"
    android:minHeight="110dp"
    android:updatePeriodMillis="1800000"
    android:initialLayout="@layout/widget_layout"
    android:resizeMode="horizontal|vertical" />
```

**3. Создать BroadcastReceiver (AppWidgetProvider):**

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

    private fun updateWidget(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int
    ) {
        val views = RemoteViews(context.packageName, R.layout.widget_layout)
        views.setTextViewText(R.id.widget_title, "Updated Title")
        appWidgetManager.updateAppWidget(appWidgetId, views)
    }
}
```

**4. Объявить виджет в AndroidManifest.xml:**

```xml
<receiver
    android:name=".MyWidgetProvider"
    android:exported="true">
    <intent-filter>
        <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
    </intent-filter>
    <meta-data
        android:name="android.appwidget.provider"
        android:resource="@xml/widget_info" />
</receiver>
```

**Методы жизненного цикла виджета:**

| Метод | Описание |
|-------|----------|
| `onEnabled()` | Вызывается при добавлении **первого** экземпляра виджета на главный экран |
| `onDisabled()` | Вызывается при удалении **последнего** экземпляра виджета |
| `onUpdate()` | Вызывается для **каждого обновления** виджета |
| `onDeleted()` | Вызывается при **удалении экземпляра** виджета |
| `onReceive()` | Вызывается для **каждого broadcast** перед методами выше |

**Ограничения виджетов:**

**1. Ограниченная поддержка жестов:**
- Только нажатие (touch) и вертикальный свайп

**2. Ограниченная поддержка Layout и View:**

RemoteViews поддерживает только определённые layouts и widgets:

**Поддерживаемые layouts:**
- FrameLayout, LinearLayout, RelativeLayout, GridLayout

**Поддерживаемые widgets:**
- Button, ImageButton, ImageView, ProgressBar, TextView, ListView, GridView и др.

**3. Ограничения времени выполнения:**
- **5 секунд** на завершение обработки
- Длительные операции должны выполняться в Service

**Лучшие практики:**

1. Держите виджеты лёгкими — не выполняйте тяжёлые операции
2. Используйте Service для обновлений
3. Оптимизируйте частоту обновлений
4. Предоставляйте содержательный preview
5. Используйте PendingIntent.FLAG_IMMUTABLE для Android 12+
6. Тестируйте на разных лончерах

**Резюме:**

Виджеты — это интерактивные компоненты на главном экране Android. Существует четыре категории: информационные, коллекций, управления и гибридные. Для создания виджета необходимы: layout, XML метаданных, AppWidgetProvider и запись в manifest. Жизненный цикл включает onEnabled, onUpdate, onDeleted, onDisabled. RemoteViews используется для построения UI с ограниченной поддержкой view. Основные ограничения: поддержка жестов, типы view, лимит выполнения 5 секунд.

## Related Questions

- [[q-recyclerview-viewtypes-delegation--android--medium]]
- [[q-what-is-broadcastreceiver--android--easy]]
- [[q-what-is-known-about-recyclerview--android--easy]]
