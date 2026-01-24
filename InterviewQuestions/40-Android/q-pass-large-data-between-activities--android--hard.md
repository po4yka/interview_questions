---
id: android-365
anki_cards:
- slug: android-365-0-en
  language: en
  anki_id: 1768400157920
  synced_at: '2026-01-23T16:45:06.242630'
- slug: android-365-0-ru
  language: ru
  anki_id: 1768400157942
  synced_at: '2026-01-23T16:45:06.243395'
title: Pass Large Data Between Activities / Передача больших данных между Activity
aliases:
- Content URI
- FileProvider
- Large Data Transfer
- Pass Large Data Between Activities
- Передача больших данных между Activity
topic: android
subtopics:
- activity
- content-provider
- intents-deeplinks
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android
- c-binder
- q-android-security-best-practices--android--medium
- q-how-to-pass-data-from-one-activity-to-another--android--medium
- q-how-to-pass-data-from-one-fragment-to-another--android--medium
- q-why-use-fragments-when-we-have-activities--android--medium
created: 2025-10-15
updated: 2025-11-10
sources:
- https://developer.android.com/guide/topics/providers/content-providers
- https://developer.android.com/reference/androidx/core/content/FileProvider
- https://developer.android.com/training/secure-file-sharing
tags:
- android/activity
- android/content-provider
- android/intents-deeplinks
- binder
- difficulty/hard
- file-provider
- ipc
---
# Вопрос (RU)

> Как правильно передать большой объем данных (например, изображение) между `Activity`?

# Question (EN)

> How to properly pass large data (e.g., an image) between Activities?

---

## Ответ (RU)

### Краткая Версия
Крупные данные нельзя передавать напрямую через `Intent` из-за лимита `Binder` (около 1 МБ на транзакцию). Вместо этого:
- сохраняем данные во внешний носитель (файл/БД/кэш),
- передаем только ссылку (`URI`/ID/путь),
- предоставляем доступ через `FileProvider`/`ContentProvider` или другой безопасный механизм.

### Подробная Версия
### Проблема: Ограничение Размера `Intent`

**❌ Неправильно** - передавать большие данные напрямую (особенно `Bitmap`/`ByteArray`):

```kotlin
// Возможен TransactionTooLargeException!
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large)
intent.putExtra("image", bitmap)  // Риск ошибки при большом размере, зависит от общего Binder буфера
```

**Причина:** `Intent` использует `Binder IPC` с лимитом порядка **1MB** на буфер транзакции для процесса. Передача крупных объектов может переполнить буфер и вызвать `TransactionTooLargeException`.

**✅ Правильно** - для больших данных передавать только ссылку:
1. Сохранить данные (файл/БД/кэш)
2. Передать ссылку (`URI`/ID/путь)
3. Использовать безопасный доступ (`FileProvider`/`ContentProvider`)

---

### Решение 1: FileProvider + URI (Рекомендуется)

**Когда использовать:** Изображения, видео, документы между `Activity`/приложениями.

**Шаг 1:** Настройка `FileProvider` в `AndroidManifest.xml`:

```xml
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

**Шаг 2:** Определить пути в `res/xml/file_paths.xml`:

```xml
<paths>
    <cache-path name="cache" path="." />
    <files-path name="files" path="." />
</paths>
```

**Шаг 3:** Передача данных:

```kotlin
class MainActivity : AppCompatActivity() {
    private fun passLargeImage() {
        // 1. Сохранить в файл
        val bitmap = loadBitmap()
        val file = File(cacheDir, "shared_${System.currentTimeMillis()}.jpg")
        FileOutputStream(file).use { bitmap.compress(Bitmap.CompressFormat.JPEG, 90, it) }

        // 2. Получить URI через FileProvider
        val uri = FileProvider.getUriForFile(this, "$packageName.fileprovider", file)

        // 3. Передать URI с разрешением
        val intent = Intent(this, ViewImageActivity::class.java).apply {
            putExtra("imageUri", uri.toString())
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        startActivity(intent)
    }
}
```

**Шаг 4:** Получение данных:

```kotlin
class ViewImageActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val uriString = intent.getStringExtra("imageUri")
        val uri = uriString?.let { Uri.parse(it) } ?: return

        // Загрузить через ContentResolver
        contentResolver.openInputStream(uri)?.use { stream ->
            val bitmap = BitmapFactory.decodeStream(stream)
            imageView.setImageBitmap(bitmap)
        }
    }
}
```

**✅ Преимущества:**
- Безопасность (временные разрешения на чтение)
- Работает между приложениями
- Стандартный Android-подход

**❌ Недостатки:**
- Требует настройки `FileProvider`
- Overhead на файловые операции

---

### Решение 2: Общий `ViewModel` (ограниченно применимо)

**Когда использовать:** Временная передача в рамках одного процесса и контролируемой навигации (чаще для нескольких экранов внутри одной `Activity`/Navigation Graph). Для разных `Activity` классический `by viewModels()` в каждой `Activity` создаст разные `ViewModel` и не будет делиться состоянием.

Для обмена между несколькими экранами предпочтительнее использовать:
- один host `Activity` с shared `ViewModel` между `Fragment`-ами, или
- явный общий holder (DI/Singleton) для прототипов.

Пример (упрощенный, не для меж-`Activity`):

```kotlin
class SharedImageViewModel : ViewModel() {
    private val _bitmap = MutableLiveData<Bitmap?>()
    val bitmap: LiveData<Bitmap?> = _bitmap

    fun setImage(bitmap: Bitmap) { _bitmap.value = bitmap }
}

// Отправитель (на одном хосте с получателем)
class SenderFragment : Fragment() {
    private val viewModel: SharedImageViewModel by activityViewModels()

    fun share() {
        viewModel.setImage(loadBitmap())
        findNavController().navigate(R.id.receiverFragment)
    }
}

// Получатель
class ReceiverFragment : Fragment() {
    private val viewModel: SharedImageViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.bitmap.observe(viewLifecycleOwner) { bitmap ->
            imageView.setImageBitmap(bitmap)
        }
    }
}
```

**✅ Преимущества:**
- Просто для навигации внутри одного host `Activity`
- `Lifecycle`-aware

**❌ Недостатки:**
- Только в рамках одного процесса
- Не подходит для надежной передачи между разными `Activity` и при убийстве процесса
- Риск удержания крупных объектов в памяти (важно явно очищать или использовать слабые ссылки)

---

### Решение 3: База Данных + ID

**Когда использовать:** Персистентные данные, множественный доступ.

```kotlin
@Entity(tableName = "images")
data class ImageEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val filePath: String,
    val timestamp: Long
)

// Отправитель
lifecycleScope.launch {
    val file = saveToFile(bitmap)
    val entity = ImageEntity(filePath = file.path, timestamp = now())
    val id = database.imageDao().insert(entity)

    startActivity(Intent(this@SenderActivity, ViewActivity::class.java).apply {
        putExtra("imageId", id)
    })
}

// Получатель
lifecycleScope.launch {
    val id = intent.getLongExtra("imageId", -1)
    if (id == -1L) return@launch
    val entity = database.imageDao().getById(id)
    val bitmap = entity?.filePath?.let { BitmapFactory.decodeFile(it) }
    bitmap?.let { imageView.setImageBitmap(it) }
}
```

**✅ Преимущества:**
- Персистентность
- Структурированное хранение

**❌ Недостатки:**
- Требует настройки БД
- Overhead на запросы

---

### Решение 4: Singleton Data Holder

**Когда использовать:** Быстрое прототипирование, мелкие приложения, временное хранение между `Activity` в одном процессе.

```kotlin
object ImageHolder {
    var currentBitmap: Bitmap? = null

    fun clear() {
        currentBitmap = null
    }
}

// Отправитель
ImageHolder.currentBitmap = bitmap
startActivity(Intent(this, ViewActivity::class.java))

// Получатель
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    imageView.setImageBitmap(ImageHolder.currentBitmap)
}

override fun onDestroy() {
    super.onDestroy()
    // При необходимости очищать, если Bitmap больше не нужен
    ImageHolder.clear()
}
```

**❌ Внимание:** Высокий риск утечки памяти и зависимости от одного процесса. Только для временного/внутреннего использования.

---

### Решение 5: Пользовательский `ContentProvider`

**Когда использовать:** Обмен данными между приложениями, сложная логика доступа.

```kotlin
class ImageContentProvider : ContentProvider() {
    companion object {
        const val AUTHORITY = "com.example.app.images"
        val CONTENT_URI: Uri = Uri.parse("content://$AUTHORITY/images")
    }

    override fun openFile(uri: Uri, mode: String): ParcelFileDescriptor? {
        val imageId = uri.lastPathSegment?.toLongOrNull() ?: return null
        val file = File(context?.filesDir, "image_$imageId.jpg")
        return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
    }

    // Остальные методы должны быть реализованы при необходимости (query/insert/update/delete)
}

// Манифест
<provider
    android:name=".ImageContentProvider"
    android:authorities="com.example.app.images"
    android:exported="true"
    android:grantUriPermissions="true" />

// Использование
val uri = Uri.withAppendedPath(ImageContentProvider.CONTENT_URI, "$imageId")
intent.putExtra("imageUri", uri.toString())
intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
```

**✅ Преимущества:**
- Межпроцессное взаимодействие
- Гибкий контроль доступа

**❌ Недостатки:**
- Сложная настройка
- Overkill для простых случаев

---

### Архитектурные Особенности

**Binder Transaction Buffer:**
- Общий буфер для всех IPC-транзакций процесса (порядка ~1MB, зависит от устройства/версии)
- Включает все одновременные `Intent`/AIDL/Binder-вызовы
- Превышение лимита вызывает `TransactionTooLargeException`

**Безопасность `FileProvider`:**
- Генерирует `content://` URI, скрывающие реальные пути к файлам
- Управляет временными разрешениями через `FLAG_GRANT_*_URI_PERMISSION`
- Предотвращает `FileUriExposedException` на Android 7.0+

**Жизненный цикл `ViewModel`:**
- Переживает configuration changes в рамках владельца (`Activity`/`Fragment`)
- Не переживает `process death`
- Очищается при финальном уничтожении владельца; не гарантирует долговременное хранение больших данных

---

## Answer (EN)

### Short Version
You must not put large payloads (e.g., `Bitmap`/`ByteArray`) directly into `Intent` extras because of the `Binder` transaction buffer limit (~1 MB). Instead:
- persist data (file/DB/cache),
- pass only a reference (`URI`/ID/path),
- expose it securely via `FileProvider`/`ContentProvider` or similar.

### Detailed Version
### Problem: `Intent` Size Limit

**❌ Wrong** - passing large data directly (especially `Bitmap`/`ByteArray`):

```kotlin
// May cause TransactionTooLargeException!
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large)
intent.putExtra("image", bitmap)  // Risky for large size; depends on total Binder buffer usage
```

**Reason:** `Intent` extras are sent over `Binder IPC` with an approximate **1MB** transaction buffer limit per process. Large objects can overflow this buffer and trigger `TransactionTooLargeException`.

**✅ Correct** - for large data, pass a reference only:
1. Save data (file/database/cache)
2. Pass reference (`URI`/ID/path)
3. Use secure access (`FileProvider`/`ContentProvider`)

---

### Solution 1: FileProvider + URI (Recommended)

**When to use:** Images, videos, documents between Activities/apps.

**Step 1:** Configure `FileProvider` in `AndroidManifest.xml`:

```xml
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

**Step 2:** Define paths in `res/xml/file_paths.xml`:

```xml
<paths>
    <cache-path name="cache" path="." />
    <files-path name="files" path="." />
</paths>
```

**Step 3:** Send data:

```kotlin
class MainActivity : AppCompatActivity() {
    private fun passLargeImage() {
        // 1. Save to file
        val bitmap = loadBitmap()
        val file = File(cacheDir, "shared_${System.currentTimeMillis()}.jpg")
        FileOutputStream(file).use { bitmap.compress(Bitmap.CompressFormat.JPEG, 90, it) }

        // 2. Get URI via FileProvider
        val uri = FileProvider.getUriForFile(this, "$packageName.fileprovider", file)

        // 3. Pass URI with permission
        val intent = Intent(this, ViewImageActivity::class.java).apply {
            putExtra("imageUri", uri.toString())
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        startActivity(intent)
    }
}
```

**Step 4:** Receive data:

```kotlin
class ViewImageActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val uriString = intent.getStringExtra("imageUri")
        val uri = uriString?.let { Uri.parse(it) } ?: return

        // Load via ContentResolver
        contentResolver.openInputStream(uri)?.use { stream ->
            val bitmap = BitmapFactory.decodeStream(stream)
            imageView.setImageBitmap(bitmap)
        }
    }
}
```

**✅ Pros:**
- Secure (temporary read permissions)
- Works across apps
- Standard Android approach

**❌ Cons:**
- Requires `FileProvider` setup
- File I/O overhead

---

### Solution 2: Shared `ViewModel` (narrow use)

**When to use:** Temporary sharing within a single process and controlled navigation, typically between multiple Fragments in the same host `Activity`. For different Activities, `by viewModels()` in each `Activity` will create separate `ViewModel` instances, so it does not share state as-is.

Example (simplified, intra-`Activity`):

```kotlin
class SharedImageViewModel : ViewModel() {
    private val _bitmap = MutableLiveData<Bitmap?>()
    val bitmap: LiveData<Bitmap?> = _bitmap

    fun setImage(bitmap: Bitmap) { _bitmap.value = bitmap }
}

// Sender (within the same host Activity)
class SenderFragment : Fragment() {
    private val viewModel: SharedImageViewModel by activityViewModels()

    fun share() {
        viewModel.setImage(loadBitmap())
        findNavController().navigate(R.id.receiverFragment)
    }
}

// Receiver
class ReceiverFragment : Fragment() {
    private val viewModel: SharedImageViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.bitmap.observe(viewLifecycleOwner) { bitmap ->
            imageView.setImageBitmap(bitmap)
        }
    }
}
```

**✅ Pros:**
- Simple for multiple screens within one host `Activity`
- `Lifecycle`-aware

**❌ Cons:**
- Single-process only
- Not reliable for cross-`Activity` or after process death
- Holding large Bitmaps increases memory pressure; should be cleaned up explicitly when no longer needed

---

### Solution 3: Database + ID

**When to use:** Persistent data, multiple access points.

```kotlin
@Entity(tableName = "images")
data class ImageEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val filePath: String,
    val timestamp: Long
)

// Sender
lifecycleScope.launch {
    val file = saveToFile(bitmap)
    val entity = ImageEntity(filePath = file.path, timestamp = now())
    val id = database.imageDao().insert(entity)

    startActivity(Intent(this@SenderActivity, ViewActivity::class.java).apply {
        putExtra("imageId", id)
    })
}

// Receiver
lifecycleScope.launch {
    val id = intent.getLongExtra("imageId", -1)
    if (id == -1L) return@launch
    val entity = database.imageDao().getById(id)
    val bitmap = entity?.filePath?.let { BitmapFactory.decodeFile(it) }
    bitmap?.let { imageView.setImageBitmap(it) }
}
```

**✅ Pros:**
- Persistence
- Structured storage

**❌ Cons:**
- Requires database setup
- Query overhead

---

### Solution 4: Singleton Data Holder

**When to use:** Quick prototyping, small apps, temporary in-process sharing.

```kotlin
object ImageHolder {
    var currentBitmap: Bitmap? = null

    fun clear() {
        currentBitmap = null
    }
}

// Sender
ImageHolder.currentBitmap = bitmap
startActivity(Intent(this, ViewActivity::class.java))

// Receiver
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    imageView.setImageBitmap(ImageHolder.currentBitmap)
}

override fun onDestroy() {
    super.onDestroy()
    // Clear if not needed anymore
    ImageHolder.clear()
}
```

**❌ Warning:** High risk of memory leaks and tight coupling to a single process. Use only for temporary or internal flows.

---

### Solution 5: Custom `ContentProvider`

**When to use:** Cross-app data sharing, complex access control.

```kotlin
class ImageContentProvider : ContentProvider() {
    companion object {
        const val AUTHORITY = "com.example.app.images"
        val CONTENT_URI: Uri = Uri.parse("content://$AUTHORITY/images")
    }

    override fun openFile(uri: Uri, mode: String): ParcelFileDescriptor? {
        val imageId = uri.lastPathSegment?.toLongOrNull() ?: return null
        val file = File(context?.filesDir, "image_$imageId.jpg")
        return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
    }

    // Other methods (query/insert/update/delete) should be implemented as needed
}

// Manifest
<provider
    android:name=".ImageContentProvider"
    android:authorities="com.example.app.images"
    android:exported="true"
    android:grantUriPermissions="true" />

// Usage
val uri = Uri.withAppendedPath(ImageContentProvider.CONTENT_URI, "$imageId")
intent.putExtra("imageUri", uri.toString())
intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
```

**✅ Pros:**
- Inter-process communication
- Flexible access control

**❌ Cons:**
- Complex setup
- Overkill for simple cases

---

### Architectural Considerations

**Binder Transaction Buffer:**
- Shared buffer for all IPC transactions in a process (~1MB, device/OS-dependent)
- Includes all concurrent `Intent`/AIDL/Binder calls
- Exceeding the limit throws `TransactionTooLargeException`

**FileProvider Security:**
- Generates `content://` URIs that hide real file paths
- Manages temporary permissions via `FLAG_GRANT_*_URI_PERMISSION`
- Prevents `FileUriExposedException` on Android 7.0+

**`ViewModel` `Lifecycle`:**
- Survives configuration changes within its owner (`Activity`/`Fragment`)
- Does not survive process death
- Cleared when the owning scope is finished; not a long-term storage for large data

---

## Follow-ups

1. Что произойдет, если `Activity`-получатель упадет до чтения `URI`, и как организовать уборку временных файлов?
2. Как передавать большие данные между приложениями с разными сертификатами подписи с помощью `ContentProvider` и временных разрешений?
3. Каковы последствия для памяти при хранении `Bitmap` в `ViewModel` или Singleton и как избежать утечек?
4. Как реализовать потоковую передачу крупных файлов (более 100 МБ) через `ContentProvider`, не загружая их полностью в память?
5. Как Scoped Storage (Android 10+) влияет на использование `FileProvider` и какие изменения нужны при работе с `MediaStore`?

---

## References

- [[c-android]]
- [[c-binder]]
- Android Developers: FileProvider
- Android Developers: Content Provider Basics
- Android Developers: Share Files
- Android Developers: Binder and IPC (Binder transaction buffer behavior)

---

## Related Questions

### Prerequisites / Concepts

- [[c-android]]
- [[c-binder]]

### Related (Hard)

- [[q-android-security-best-practices--android--medium]] - Secure file sharing
