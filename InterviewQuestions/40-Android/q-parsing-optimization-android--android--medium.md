---
topic: android
tags:
  - android
  - android/performance
  - gson
  - json
  - moshi
  - optimization
  - parsing
  - performance
  - xml
difficulty: medium
---

# Где можно оптимизировать парсинг?

**English**: Where can parsing be optimized?

## Answer

**1. Use Streaming Processing**

Use XmlPullParser instead of DOM for XML.

```kotlin
// ❌ BAD - DOM loads entire document
val factory = DocumentBuilderFactory.newInstance()
val builder = factory.newDocumentBuilder()
val doc = builder.parse(inputStream)  // Loads all in memory

// ✅ GOOD - Streaming parser
val parser = Xml.newPullParser()
parser.setInput(inputStream, null)

while (parser.next() != XmlPullParser.END_DOCUMENT) {
    if (parser.eventType == XmlPullParser.START_TAG) {
        when (parser.name) {
            "item" -> parseItem(parser)
        }
    }
}
```

**2. Reduce String Conversions**

```kotlin
// ❌ BAD - Multiple conversions
val jsonString = response.body?.string()
val data = jsonString?.let { JSONObject(it) }
val value = data?.getString("key")

// ✅ GOOD - Direct stream parsing
val data = JSONObject(response.body?.charStream())
```

**3. Cache Parsing Results**

```kotlin
class DataRepository {
    private var cachedData: List<Item>? = null
    private var cacheTimestamp: Long = 0
    private val CACHE_DURATION = 5 * 60 * 1000  // 5 minutes

    suspend fun getData(): List<Item> {
        // Return cached if fresh
        if (cachedData != null &&
            System.currentTimeMillis() - cacheTimestamp < CACHE_DURATION) {
            return cachedData!!
        }

        // Parse and cache
        val data = api.fetchData()
        cachedData = parseData(data)
        cacheTimestamp = System.currentTimeMillis()

        return cachedData!!
    }
}
```

**4. Use Specialized Libraries**

**Moshi - Fast and efficient:**

```kotlin
// build.gradle
implementation 'com.squareup.moshi:moshi:1.15.0'
implementation 'com.squareup.moshi:moshi-kotlin:1.15.0'

@JsonClass(generateAdapter = true)
data class User(
    val id: Int,
    val name: String,
    val email: String
)

val moshi = Moshi.Builder()
    .add(KotlinJsonAdapterFactory())
    .build()

val adapter = moshi.adapter(User::class.java)
val user = adapter.fromJson(jsonString)
```

**Gson - Flexible:**

```kotlin
implementation 'com.google.code.gson:gson:2.10.1'

data class User(val id: Int, val name: String)

val gson = Gson()
val user = gson.fromJson(jsonString, User::class.java)
```

**kotlinx.serialization - Native Kotlin:**

```kotlin
@Serializable
data class User(val id: Int, val name: String)

val json = Json { ignoreUnknownKeys = true }
val user = json.decodeFromString<User>(jsonString)
```

**Performance Comparison:**

```kotlin
// Benchmark results (1000 objects)
// Moshi:                 ~15ms
// kotlinx.serialization: ~18ms
// Gson:                  ~25ms
// org.json:              ~45ms
// Jackson:               ~30ms
```

**5. Optimize Large Lists:**

```kotlin
// ❌ BAD - Parse all at once
fun parseAllUsers(json: String): List<User> {
    val array = JSONArray(json)
    return (0 until array.length()).map {
        parseUser(array.getJSONObject(it))
    }
}

// ✅ GOOD - Lazy parsing with sequence
fun parseUsersLazy(json: String): Sequence<User> = sequence {
    val array = JSONArray(json)
    for (i in 0 until array.length()) {
        yield(parseUser(array.getJSONObject(i)))
    }
}

// Use only what you need
parseUsersLazy(json).take(10).toList()
```

**6. Background Parsing:**

```kotlin
class DataViewModel : ViewModel() {
    fun loadData(jsonString: String) {
        viewModelScope.launch(Dispatchers.Default) {
            // Parse on background thread
            val data = parseData(jsonString)

            withContext(Dispatchers.Main) {
                // Update UI on main thread
                _dataLiveData.value = data
            }
        }
    }
}
```

**7. Incremental Parsing:**

```kotlin
// For large JSON streams
class IncrementalParser {
    fun parseStream(inputStream: InputStream) = flow {
        JsonReader(inputStream.reader()).use { reader ->
            reader.beginArray()
            while (reader.hasNext()) {
                val item = parseItem(reader)
                emit(item)  // Emit one by one
            }
            reader.endArray()
        }
    }
}

// Usage
parserparseStream(stream).collect { item ->
    // Process items as they arrive
    displayItem(item)
}
```

**Optimization Summary:**

| Optimization | Benefit | Use Case |
|--------------|---------|----------|
| **Streaming** | Lower memory | Large documents |
| **Reduce conversions** | Faster parsing | String heavy |
| **Caching** | Avoid re-parsing | Frequently accessed |
| **Moshi/kotlinx** | Speed | JSON parsing |
| **Lazy parsing** | Memory efficient | Large lists |
| **Background** | UI responsive | Heavy parsing |

**Summary:**

1. Use streaming (XmlPullParser vs DOM)
2. Reduce string conversions
3. Cache parsing results for reuse
4. Use specialized libraries (Moshi, Gson, kotlinx.serialization)
5. Parse large lists lazily
6. Parse on background thread

## Ответ

1. Использовать потоковую обработку (например, XmlPullParser вместо DOM)
2. Уменьшить количество преобразований строк
3. Кешировать результаты парсинга для повторного использования
4. Использовать специализированные библиотеки (Moshi, Gson)

