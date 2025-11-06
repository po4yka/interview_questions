---
id: "20251025-140400"
title: "ContentProvider / ContentProvider"
aliases: ["Android Data Sharing", "Content Provider", "Content Resolver", "ContentProvider", "Поставщик контента", "Провайдер контента"]
summary: "Android component for managing and sharing structured data between applications"
topic: "android"
subtopics: ["content-provider", "data-sharing", "ipc"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-25"
updated: "2025-10-25"
tags: ["android", "concept", "content-provider", "crud", "data-sharing", "difficulty/medium", "ipc", "uri"]
---

# ContentProvider / ContentProvider

## Summary (EN)

ContentProvider is one of Android's four fundamental components that manages access to a structured set of data and provides a standard interface for data sharing between applications. It acts as an abstraction layer between the data source (database, files, network) and the rest of the application or other applications. ContentProviders use content URIs to identify data, support CRUD operations (Create, Read, Update, Delete), and can enforce permissions to control data access. Common examples include ContactsContract, MediaStore, and CalendarContract.

## Краткое Описание (RU)

ContentProvider - один из четырёх фундаментальных компонентов Android, который управляет доступом к структурированному набору данных и предоставляет стандартный интерфейс для обмена данными между приложениями. Выступает в качестве слоя абстракции между источником данных (база данных, файлы, сеть) и остальной частью приложения или другими приложениями. ContentProvider использует URI контента для идентификации данных, поддерживает CRUD операции (Create, Read, Update, Delete) и может применять разрешения для контроля доступа к данным. Распространённые примеры: ContactsContract, MediaStore, CalendarContract.

## Key Points (EN)

- **Data Abstraction**: Hides underlying data storage implementation
- **Inter-Process Communication (IPC)**: Shares data between apps securely
- **Content URIs**: Uses URI scheme to identify data (content://authority/path)
- **CRUD Operations**: query(), insert(), update(), delete()
- **Permission-based**: Controls access with read/write permissions
- **Type System**: Returns MIME types for data
- **Batch Operations**: applyBatch() for multiple operations
- **Content Observers**: Notifies listeners of data changes
- **File Descriptors**: openFile() for sharing files
- **Synchronous**: Operations run on caller's thread (use async methods)

## Ключевые Моменты (RU)

- **Абстракция данных**: Скрывает реализацию хранилища данных
- **Межпроцессное взаимодействие (IPC)**: Безопасный обмен данными между приложениями
- **URI контента**: Использует схему URI для идентификации данных (content://authority/path)
- **CRUD операции**: query(), insert(), update(), delete()
- **На основе разрешений**: Контролирует доступ с разрешениями на чтение/запись
- **Система типов**: Возвращает MIME-типы для данных
- **Пакетные операции**: applyBatch() для множественных операций
- **Content Observers**: Уведомляет слушателей об изменениях данных
- **Файловые дескрипторы**: openFile() для обмена файлами
- **Синхронность**: Операции выполняются в потоке вызывающего (используйте асинхронные методы)

## Use Cases

### When to Use

- **Sharing data between apps**: Contacts, calendar, media files
- **Exposing app data**: Allow other apps to read/write your data
- **Centralizing data access**: Single point of access for complex data
- **File sharing**: Share files securely with FileProvider
- **System integration**: Integration with sync adapters, search
- **Permission enforcement**: Fine-grained access control
- **Data abstraction**: Hide implementation details (SQLite, files, network)

### When to Avoid

- **Internal app data only**: Use Repository pattern, Room directly
- **Simple data sharing**: Use Intent extras for simple data
- **Real-time updates**: Use broadcasts, callbacks, or Flow
- **Large file transfers**: Use FileProvider or direct file sharing
- **Performance-critical**: Direct database access is faster for internal use
- **Complex queries**: ContentProvider has limited query capabilities

## Trade-offs

**Pros**:
- **Standardized interface**: Consistent CRUD operations
- **Security**: Permission-based access control
- **Abstraction**: Change storage without affecting clients
- **IPC support**: Built-in cross-process communication
- **Content Observers**: Reactive data updates
- **System integration**: Works with sync adapters, loaders
- **MIME types**: Type information for data
- **Batch operations**: Efficient bulk updates

**Cons**:
- **Complexity**: Overhead for simple internal data access
- **Performance**: Slower than direct database access
- **Limited queries**: Cannot express complex SQL queries
- **Synchronous by default**: Must handle threading manually
- **Boilerplate**: Requires manifest registration, permissions
- **Learning curve**: URI matching, projection maps, MIME types
- **Testing complexity**: Harder to test than repositories

## Creating a ContentProvider

### Basic Implementation

```kotlin
class MyContentProvider : ContentProvider() {

    companion object {
        const val AUTHORITY = "com.example.myapp.provider"
        val CONTENT_URI: Uri = Uri.parse("content://$AUTHORITY/items")

        private const val ITEMS = 1
        private const val ITEM_ID = 2

        private val uriMatcher = UriMatcher(UriMatcher.NO_MATCH).apply {
            addURI(AUTHORITY, "items", ITEMS)
            addURI(AUTHORITY, "items/#", ITEM_ID)
        }
    }

    private lateinit var database: AppDatabase

    override fun onCreate(): Boolean {
        database = Room.databaseBuilder(
            context!!,
            AppDatabase::class.java,
            "app_database"
        ).build()
        return true
    }

    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        return when (uriMatcher.match(uri)) {
            ITEMS -> {
                database.itemDao().getAllCursor()
            }
            ITEM_ID -> {
                val id = uri.lastPathSegment?.toLongOrNull() ?: return null
                database.itemDao().getByIdCursor(id)
            }
            else -> null
        }
    }

    override fun getType(uri: Uri): String? {
        return when (uriMatcher.match(uri)) {
            ITEMS -> "vnd.android.cursor.dir/vnd.$AUTHORITY.items"
            ITEM_ID -> "vnd.android.cursor.item/vnd.$AUTHORITY.item"
            else -> null
        }
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        if (uriMatcher.match(uri) != ITEMS) return null
        values ?: return null

        val item = Item(
            name = values.getAsString("name"),
            description = values.getAsString("description")
        )

        val id = database.itemDao().insert(item)
        context?.contentResolver?.notifyChange(uri, null)

        return ContentUris.withAppendedId(CONTENT_URI, id)
    }

    override fun update(
        uri: Uri,
        values: ContentValues?,
        selection: String?,
        selectionArgs: Array<String>?
    ): Int {
        val count = when (uriMatcher.match(uri)) {
            ITEMS -> {
                // Update multiple rows
                database.itemDao().updateWithSelection(values, selection, selectionArgs)
            }
            ITEM_ID -> {
                val id = uri.lastPathSegment?.toLongOrNull() ?: return 0
                database.itemDao().updateById(id, values)
            }
            else -> 0
        }

        if (count > 0) {
            context?.contentResolver?.notifyChange(uri, null)
        }

        return count
    }

    override fun delete(
        uri: Uri,
        selection: String?,
        selectionArgs: Array<String>?
    ): Int {
        val count = when (uriMatcher.match(uri)) {
            ITEMS -> {
                database.itemDao().deleteWithSelection(selection, selectionArgs)
            }
            ITEM_ID -> {
                val id = uri.lastPathSegment?.toLongOrNull() ?: return 0
                database.itemDao().deleteById(id)
            }
            else -> 0
        }

        if (count > 0) {
            context?.contentResolver?.notifyChange(uri, null)
        }

        return count
    }
}
```

### Manifest Registration

```xml
<provider
    android:name=".MyContentProvider"
    android:authorities="com.example.myapp.provider"
    android:exported="true"
    android:readPermission="com.example.myapp.permission.READ_ITEMS"
    android:writePermission="com.example.myapp.permission.WRITE_ITEMS" />

<!-- Define custom permissions -->
<permission
    android:name="com.example.myapp.permission.READ_ITEMS"
    android:protectionLevel="normal" />

<permission
    android:name="com.example.myapp.permission.WRITE_ITEMS"
    android:protectionLevel="normal" />
```

## Accessing ContentProvider

### Query Data

```kotlin
// Query all items
val cursor = contentResolver.query(
    uri = MyContentProvider.CONTENT_URI,
    projection = arrayOf("_id", "name", "description"),
    selection = null,
    selectionArgs = null,
    sortOrder = "name ASC"
)

cursor?.use { cursor ->
    val idColumn = cursor.getColumnIndex("_id")
    val nameColumn = cursor.getColumnIndex("name")

    while (cursor.moveToNext()) {
        val id = cursor.getLong(idColumn)
        val name = cursor.getString(nameColumn)
        println("Item: $id - $name")
    }
}

// Query single item
val itemUri = ContentUris.withAppendedId(MyContentProvider.CONTENT_URI, 1)
val cursor = contentResolver.query(itemUri, null, null, null, null)
```

### Insert Data

```kotlin
val values = ContentValues().apply {
    put("name", "New Item")
    put("description", "Item description")
}

val newUri = contentResolver.insert(MyContentProvider.CONTENT_URI, values)
val newId = ContentUris.parseId(newUri!!)
println("Inserted item with ID: $newId")
```

### Update Data

```kotlin
val values = ContentValues().apply {
    put("description", "Updated description")
}

// Update specific item
val itemUri = ContentUris.withAppendedId(MyContentProvider.CONTENT_URI, 1)
val count = contentResolver.update(itemUri, values, null, null)

// Update with selection
val count = contentResolver.update(
    MyContentProvider.CONTENT_URI,
    values,
    "name = ?",
    arrayOf("Item 1")
)
```

### Delete Data

```kotlin
// Delete specific item
val itemUri = ContentUris.withAppendedId(MyContentProvider.CONTENT_URI, 1)
val count = contentResolver.delete(itemUri, null, null)

// Delete with selection
val count = contentResolver.delete(
    MyContentProvider.CONTENT_URI,
    "created_date < ?",
    arrayOf("2024-01-01")
)
```

## Content Observers

### Register Observer

```kotlin
class MyActivity : AppCompatActivity() {

    private val contentObserver = object : ContentObserver(Handler(Looper.getMainLooper())) {
        override fun onChange(selfChange: Boolean) {
            super.onChange(selfChange)
            // Reload data
            loadData()
        }
    }

    override fun onStart() {
        super.onStart()
        contentResolver.registerContentObserver(
            MyContentProvider.CONTENT_URI,
            true, // notify for descendants
            contentObserver
        )
    }

    override fun onStop() {
        super.onStop()
        contentResolver.unregisterContentObserver(contentObserver)
    }

    private fun loadData() {
        // Reload data from ContentProvider
    }
}
```

### Notify Changes

```kotlin
// In ContentProvider
override fun insert(uri: Uri, values: ContentValues?): Uri? {
    // ... insert logic ...

    // Notify observers
    context?.contentResolver?.notifyChange(uri, null)

    return newUri
}
```

## Batch Operations

```kotlin
val operations = ArrayList<ContentProviderOperation>()

// Insert
operations.add(
    ContentProviderOperation.newInsert(MyContentProvider.CONTENT_URI)
        .withValue("name", "Item 1")
        .build()
)

// Update
operations.add(
    ContentProviderOperation.newUpdate(itemUri)
        .withValue("description", "Updated")
        .build()
)

// Delete
operations.add(
    ContentProviderOperation.newDelete(oldItemUri)
        .build()
)

// Execute batch
try {
    val results = contentResolver.applyBatch(
        MyContentProvider.AUTHORITY,
        operations
    )
    println("Batch completed: ${results.size} operations")
} catch (e: Exception) {
    Log.e("ContentProvider", "Batch failed", e)
}
```

## FileProvider (File Sharing)

### FileProvider Setup

```xml
<!-- AndroidManifest.xml -->
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>
```

### File Paths Configuration

```xml
<!-- res/xml/file_paths.xml -->
<paths>
    <files-path name="my_files" path="/" />
    <cache-path name="my_cache" path="/" />
    <external-path name="external_files" path="." />
    <external-files-path name="app_files" path="." />
    <external-cache-path name="app_cache" path="." />
</paths>
```

### Share File

```kotlin
val file = File(context.filesDir, "shared_document.pdf")

val uri = FileProvider.getUriForFile(
    context,
    "${context.packageName}.fileprovider",
    file
)

val intent = Intent(Intent.ACTION_VIEW).apply {
    setDataAndType(uri, "application/pdf")
    flags = Intent.FLAG_GRANT_READ_URI_PERMISSION
}

startActivity(intent)
```

## System ContentProviders

### Contacts

```kotlin
// Query contacts
val cursor = contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    arrayOf(
        ContactsContract.Contacts._ID,
        ContactsContract.Contacts.DISPLAY_NAME
    ),
    null,
    null,
    ContactsContract.Contacts.DISPLAY_NAME + " ASC"
)

cursor?.use {
    while (it.moveToNext()) {
        val id = it.getLong(it.getColumnIndex(ContactsContract.Contacts._ID))
        val name = it.getString(it.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME))
        println("Contact: $name")
    }
}
```

### MediaStore (Images)

```kotlin
// Query images
val projection = arrayOf(
    MediaStore.Images.Media._ID,
    MediaStore.Images.Media.DISPLAY_NAME,
    MediaStore.Images.Media.DATE_ADDED
)

val cursor = contentResolver.query(
    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
    projection,
    null,
    null,
    "${MediaStore.Images.Media.DATE_ADDED} DESC"
)

cursor?.use {
    val idColumn = it.getColumnIndexOrThrow(MediaStore.Images.Media._ID)
    val nameColumn = it.getColumnIndexOrThrow(MediaStore.Images.Media.DISPLAY_NAME)

    while (it.moveToNext()) {
        val id = it.getLong(idColumn)
        val name = it.getString(nameColumn)
        val uri = ContentUris.withAppendedId(
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
            id
        )
        println("Image: $name, URI: $uri")
    }
}
```

### Calendar

```kotlin
// Requires READ_CALENDAR permission
val projection = arrayOf(
    CalendarContract.Calendars._ID,
    CalendarContract.Calendars.CALENDAR_DISPLAY_NAME
)

val cursor = contentResolver.query(
    CalendarContract.Calendars.CONTENT_URI,
    projection,
    null,
    null,
    null
)
```

## Permissions

### Requesting Permissions

```xml
<!-- AndroidManifest.xml -->
<uses-permission android:name="android.permission.READ_CONTACTS" />
<uses-permission android:name="android.permission.WRITE_CONTACTS" />
<uses-permission android:name="android.permission.READ_CALENDAR" />
```

```kotlin
// Runtime permission request
if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_CONTACTS)
    != PackageManager.PERMISSION_GRANTED
) {
    ActivityCompat.requestPermissions(
        this,
        arrayOf(Manifest.permission.READ_CONTACTS),
        REQUEST_CODE_READ_CONTACTS
    )
}
```

### Granting URI Permissions

```kotlin
// Grant temporary access to specific URI
val intent = Intent(Intent.ACTION_VIEW).apply {
    data = uri
    flags = Intent.FLAG_GRANT_READ_URI_PERMISSION or
            Intent.FLAG_GRANT_WRITE_URI_PERMISSION
}

startActivity(intent)
```

## Best Practices

1. **Use URI matcher** - Efficiently match content URIs
2. **Handle threading** - Operations are synchronous, use coroutines/executors
3. **Close cursors** - Use `use {}` or close manually to avoid leaks
4. **Notify changes** - Call `notifyChange()` after modifications
5. **Use batch operations** - More efficient than individual operations
6. **Implement getType()** - Return proper MIME types
7. **Validate input** - Check URIs and ContentValues before processing
8. **Use FileProvider** - For secure file sharing
9. **Enforce permissions** - Protect sensitive data with permissions
10. **Consider alternatives** - ContentProvider may be overkill for simple cases

## Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class MyContentProviderTest {

    private lateinit var contentResolver: ContentResolver

    @Before
    fun setUp() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val providerInfo = ProviderInfo().apply {
            authority = MyContentProvider.AUTHORITY
        }

        val provider = MyContentProvider()
        provider.attachInfo(context, providerInfo)

        contentResolver = context.contentResolver
    }

    @Test
    fun testInsert() {
        val values = ContentValues().apply {
            put("name", "Test Item")
        }

        val uri = contentResolver.insert(MyContentProvider.CONTENT_URI, values)
        assertNotNull(uri)

        val cursor = contentResolver.query(uri!!, null, null, null, null)
        assertNotNull(cursor)
        assertTrue(cursor!!.moveToFirst())
        assertEquals("Test Item", cursor.getString(cursor.getColumnIndex("name")))
        cursor.close()
    }
}
```

## Common Patterns

### URI Builder

```kotlin
object ItemsContract {
    const val AUTHORITY = "com.example.myapp.provider"

    object Items {
        val CONTENT_URI: Uri = Uri.parse("content://$AUTHORITY/items")

        const val CONTENT_TYPE = "vnd.android.cursor.dir/vnd.$AUTHORITY.items"
        const val CONTENT_ITEM_TYPE = "vnd.android.cursor.item/vnd.$AUTHORITY.item"

        object Columns {
            const val ID = "_id"
            const val NAME = "name"
            const val DESCRIPTION = "description"
            const val CREATED_DATE = "created_date"
        }
    }
}
```

## Related Concepts

- [[c-room]] - Modern alternative for internal data storage
- [[c-sqlite]] - Underlying database used by ContentProviders
- [[c-permissions]] - Runtime permissions for ContentProvider access
- [[c-ipc]] - Inter-process communication concepts
- [[c-cursor]] - Cursor-based data access
- [[c-repository-pattern]] - Modern data access pattern
- [[c-file-storage]] - File storage and FileProvider

## References

- [ContentProvider Documentation](https://developer.android.com/guide/topics/providers/content-providers)
- [Content Provider Basics](https://developer.android.com/guide/topics/providers/content-provider-basics)
- [Creating a ContentProvider](https://developer.android.com/guide/topics/providers/content-provider-creating)
- [FileProvider](https://developer.android.com/reference/androidx/core/content/FileProvider)
- [ContactsContract](https://developer.android.com/reference/android/provider/ContactsContract)
- [MediaStore](https://developer.android.com/reference/android/provider/MediaStore)
- [CalendarContract](https://developer.android.com/reference/android/provider/CalendarContract)
