---
id: android-365
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
- c-android-ipc
- q-android-ipc-mechanisms--android--hard
- q-android-security-best-practices--android--hard
created: 2025-10-15
updated: 2025-10-30
sources:
- Android Content Provider Documentation
- Android Developers
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

> Как правильно передать большой объем данных (например, изображение) между Activity?

# Question (EN)

> How to properly pass large data (e.g., an image) between Activities?

---

## Ответ (RU)

### Проблема: Ограничение Размера Intent

**❌ Неправильно** - передавать большие данные напрямую:

```kotlin
// TransactionTooLargeException!
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large)
intent.putExtra("image", bitmap)  // Ошибка при размере > 1MB
```

**Причина:** Intent использует Binder IPC с лимитом **~1MB** на всю транзакцию.

**✅ Правильно** - передавать только ссылку:
1. Сохранить данные (файл/БД/кэш)
2. Передать ссылку (URI/ID/путь)
3. Использовать безопасный доступ (FileProvider/ContentProvider)

---

### Решение 1: FileProvider + URI (Рекомендуется)

**Когда использовать:** Изображения, видео, документы между Activity/приложениями.

**Шаг 1:** Настройка FileProvider в `AndroidManifest.xml`:

```kotlin
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
        val uri = Uri.parse(intent.getStringExtra("imageUri"))

        // Загрузить через ContentResolver
        contentResolver.openInputStream(uri)?.use { stream ->
            val bitmap = BitmapFactory.decodeStream(stream)
            imageView.setImageBitmap(bitmap)
        }
    }
}
```

**✅ Преимущества:**
- Безопасность (временные разрешения)
- Работает между приложениями
- Стандартный Android-подход

**❌ Недостатки:**
- Требует настройки FileProvider
- Overhead на файловые операции

---

### Решение 2: Shared ViewModel

**Когда использовать:** Временная передача между Activities в одной задаче.

```kotlin
class SharedImageViewModel : ViewModel() {
    private val _bitmap = MutableLiveData<Bitmap?>()
    val bitmap: LiveData<Bitmap?> = _bitmap

    fun setImage(bitmap: Bitmap) { _bitmap.value = bitmap }

    override fun onCleared() {
        _bitmap.value?.recycle()
    }
}

// Отправитель
class SenderActivity : AppCompatActivity() {
    private val viewModel: SharedImageViewModel by viewModels()

    fun share() {
        viewModel.setImage(loadBitmap())
        startActivity(Intent(this, ReceiverActivity::class.java))
    }
}

// Получатель
class ReceiverActivity : AppCompatActivity() {
    private val viewModel: SharedImageViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.bitmap.observe(this) { bitmap ->
            imageView.setImageBitmap(bitmap)
        }
    }
}
```

**✅ Преимущества:**
- Просто
- Lifecycle-aware

**❌ Недостатки:**
- Только в рамках одного процесса
- Очищается при уничтожении Activity
- Риск утечки памяти

---

### Решение 3: Database + ID

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

    startActivity(Intent(this, ViewActivity::class.java).apply {
        putExtra("imageId", id)
    })
}

// Получатель
lifecycleScope.launch {
    val id = intent.getLongExtra("imageId", -1)
    val entity = database.imageDao().getById(id)
    val bitmap = BitmapFactory.decodeFile(entity?.filePath)
    imageView.setImageBitmap(bitmap)
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

**Когда использовать:** Быстрое прототипирование, мелкие приложения.

```kotlin
object ImageHolder {
    var currentBitmap: Bitmap? = null

    fun clear() {
        currentBitmap?.recycle()
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
    ImageHolder.clear()
}
```

**❌ Внимание:** Высокий риск утечки памяти. Только для временного использования.

---

### Решение 5: Custom ContentProvider

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

    // Остальные методы...
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

### Сравнение Подходов

| Метод | Персистентность | Сложность | Межпроцессный | Рекомендация |
|-------|----------------|-----------|---------------|--------------|
| **FileProvider + URI** | ✅ | Средняя | ✅ | **Лучший выбор** |
| **ViewModel** | ❌ | Низкая | ❌ | Временные данные |
| **Database + ID** | ✅ | Высокая | ❌ | Структурированные данные |
| **Singleton** | ❌ | Низкая | ❌ | Прототипирование |
| **ContentProvider** | ✅ | Очень высокая | ✅ | Межприложенческий обмен |

---

### Best Practices

**✅ DO:**
- Всегда передавать ссылку, а не данные
- Использовать FileProvider для файлов
- Выдавать минимальные разрешения (`FLAG_GRANT_READ_URI_PERMISSION`)
- Очищать временные данные в `onDestroy()`
- Обрабатывать ошибки доступа

**❌ DON'T:**
- Не передавать Bitmap/ByteArray в Intent
- Не использовать Singleton для production
- Не забывать отзывать разрешения URI
- Не хранить большие объекты в памяти дольше необходимого

---

### Архитектурные Особенности

**Binder Transaction Buffer:**
- Общий буфер для всех IPC-транзакций процесса (~1MB)
- Включает все одновременные Intent/AIDL/Binder-вызовы
- Превышение вызывает `TransactionTooLargeException`

**FileProvider Security:**
- Генерирует временные `content://` URI
- Автоматически управляет разрешениями
- Предотвращает `FileUriExposedException` на Android 7.0+

**ViewModel Lifecycle:**
- Переживает configuration changes
- НЕ переживает process death
- Очищается только при финальном уничтожении Activity/Fragment

---

## Answer (EN)

### Problem: Intent Size Limit

**❌ Wrong** - passing large data directly:

```kotlin
// TransactionTooLargeException!
val bitmap = BitmapFactory.decodeResource(resources, R.drawable.large)
intent.putExtra("image", bitmap)  // Fails if size > 1MB
```

**Reason:** Intent uses Binder IPC with **~1MB** limit for entire transaction buffer.

**✅ Correct** - pass reference only:
1. Save data (file/database/cache)
2. Pass reference (URI/ID/path)
3. Use secure access (FileProvider/ContentProvider)

---

### Solution 1: FileProvider + URI (Recommended)

**When to use:** Images, videos, documents between Activities/apps.

**Step 1:** Configure FileProvider in `AndroidManifest.xml`:

```kotlin
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
        val uri = Uri.parse(intent.getStringExtra("imageUri"))

        // Load via ContentResolver
        contentResolver.openInputStream(uri)?.use { stream ->
            val bitmap = BitmapFactory.decodeStream(stream)
            imageView.setImageBitmap(bitmap)
        }
    }
}
```

**✅ Pros:**
- Secure (temporary permissions)
- Works across apps
- Standard Android approach

**❌ Cons:**
- Requires FileProvider setup
- File I/O overhead

---

### Solution 2: Shared ViewModel

**When to use:** Temporary sharing between Activities in same task.

```kotlin
class SharedImageViewModel : ViewModel() {
    private val _bitmap = MutableLiveData<Bitmap?>()
    val bitmap: LiveData<Bitmap?> = _bitmap

    fun setImage(bitmap: Bitmap) { _bitmap.value = bitmap }

    override fun onCleared() {
        _bitmap.value?.recycle()
    }
}

// Sender
class SenderActivity : AppCompatActivity() {
    private val viewModel: SharedImageViewModel by viewModels()

    fun share() {
        viewModel.setImage(loadBitmap())
        startActivity(Intent(this, ReceiverActivity::class.java))
    }
}

// Receiver
class ReceiverActivity : AppCompatActivity() {
    private val viewModel: SharedImageViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.bitmap.observe(this) { bitmap ->
            imageView.setImageBitmap(bitmap)
        }
    }
}
```

**✅ Pros:**
- Simple
- Lifecycle-aware

**❌ Cons:**
- Single process only
- Cleared on Activity destruction
- Memory leak risk

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

    startActivity(Intent(this, ViewActivity::class.java).apply {
        putExtra("imageId", id)
    })
}

// Receiver
lifecycleScope.launch {
    val id = intent.getLongExtra("imageId", -1)
    val entity = database.imageDao().getById(id)
    val bitmap = BitmapFactory.decodeFile(entity?.filePath)
    imageView.setImageBitmap(bitmap)
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

**When to use:** Quick prototyping, small apps.

```kotlin
object ImageHolder {
    var currentBitmap: Bitmap? = null

    fun clear() {
        currentBitmap?.recycle()
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
    ImageHolder.clear()
}
```

**❌ Warning:** High memory leak risk. Temporary use only.

---

### Solution 5: Custom ContentProvider

**When to use:** Cross-app data sharing, complex access logic.

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

    // Other methods...
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

### Comparison Table

| Method | Persistence | Complexity | Cross-Process | Recommendation |
|--------|------------|------------|---------------|----------------|
| **FileProvider + URI** | ✅ | Medium | ✅ | **Best choice** |
| **ViewModel** | ❌ | Low | ❌ | Temporary data |
| **Database + ID** | ✅ | High | ❌ | Structured data |
| **Singleton** | ❌ | Low | ❌ | Prototyping |
| **ContentProvider** | ✅ | Very high | ✅ | Cross-app sharing |

---

### Best Practices

**✅ DO:**
- Always pass reference, not data
- Use FileProvider for files
- Grant minimal permissions (`FLAG_GRANT_READ_URI_PERMISSION`)
- Clean up temporary data in `onDestroy()`
- Handle access errors gracefully

**❌ DON'T:**
- Pass Bitmap/ByteArray in Intent
- Use Singleton for production
- Forget to revoke URI permissions
- Keep large objects in memory longer than needed

---

### Architectural Considerations

**Binder Transaction Buffer:**
- Shared buffer for all process IPC transactions (~1MB)
- Includes all concurrent Intent/AIDL/Binder calls
- Exceeding limit throws `TransactionTooLargeException`

**FileProvider Security:**
- Generates temporary `content://` URIs
- Auto-manages permissions
- Prevents `FileUriExposedException` on Android 7.0+

**ViewModel Lifecycle:**
- Survives configuration changes
- Does NOT survive process death
- Cleared only on final Activity/Fragment destruction

---

## Follow-ups

1. What happens if receiver Activity crashes before consuming the URI? How to handle cleanup?
2. How to pass large data between apps with different signing certificates using ContentProvider?
3. What are memory implications of holding Bitmap in ViewModel across multiple Activities?
4. How to implement streaming large files (>100MB) via ContentProvider without loading into memory?
5. How does Scoped Storage (Android 10+) affect FileProvider implementation? What changes are needed for MediaStore?

---

## References

- Android Developers: [FileProvider](https://developer.android.com/reference/androidx/core/content/FileProvider)
- Android Developers: [Content Provider Basics](https://developer.android.com/guide/topics/providers/content-provider-basics)
- Android Developers: [Share Files](https://developer.android.com/training/secure-file-sharing)
- Android IPC: [Binder Transaction Buffer](https://developer.android.com/topic/performance/memory-overview)

---

## Related Questions

### Prerequisites / Concepts

- [[c-android-ipc]]


### Prerequisites (Medium)
- [[q-how-to-pass-data-from-one-activity-to-another--android--medium]] - Basic data passing
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - Activity lifecycle

### Related (Hard)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Component architecture
- [[q-android-ipc-mechanisms--android--hard]] - Inter-process communication
- [[q-android-security-best-practices--android--medium]] - Secure file sharing
