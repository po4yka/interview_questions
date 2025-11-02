---
id: android-130
title: "Parsing Optimization Android / Оптимизация парсинга Android"
aliases: ["Parsing Optimization Android", "Оптимизация парсинга Android"]
topic: android
subtopics: [performance-memory, serialization]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-how-to-tell-adapter-to-redraw-list-when-item-removed--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/performance-memory, android/serialization, difficulty/medium, json, optimization, xml]
date created: Monday, October 27th 2025, 3:43:24 pm
date modified: Saturday, November 1st 2025, 5:43:33 pm
---

# Вопрос (RU)

> Где можно оптимизировать парсинг в Android-приложениях?

# Question (EN)

> Where can parsing be optimized in Android applications?

---

## Ответ (RU)

**1. Потоковый парсинг (Streaming)**

Используйте XmlPullParser вместо DOM для обработки XML. Потоковый парсинг обрабатывает документ последовательно, не загружая всё в память.

```kotlin
// ❌ Плохо - DOM загружает весь документ в память
val factory = DocumentBuilderFactory.newInstance()
val doc = factory.newDocumentBuilder().parse(inputStream)

// ✅ Хорошо - потоковый парсер
val parser = Xml.newPullParser().apply { setInput(inputStream, null) }
while (parser.next() != XmlPullParser.END_DOCUMENT) {
    if (parser.eventType == XmlPullParser.START_TAG && parser.name == "item") {
        parseItem(parser)
    }
}
```

**2. Минимизация преобразований строк**

Избегайте множественных конвертаций между форматами - парсите напрямую из потока.

```kotlin
// ❌ Плохо - несколько преобразований
val jsonString = response.body?.string()
val data = JSONObject(jsonString)

// ✅ Хорошо - прямой парсинг из потока
val data = JSONObject(response.body?.charStream())
```

**3. Кеширование результатов**

Кешируйте распарсенные данные для повторного использования, особенно если данные запрашиваются часто.

**4. Специализированные библиотеки**

Производительность (1000 объектов):
- **Moshi**: ~15ms (самая быстрая)
- **kotlinx.serialization**: ~18ms (нативная для Kotlin)
- **Gson**: ~25ms (универсальная)
- **org.json**: ~45ms (стандартная Android API)

**Moshi** - лучший выбор для производительности:
```kotlin
@JsonClass(generateAdapter = true)
data class User(val id: Int, val name: String)

val moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
val user = moshi.adapter(User::class.java).fromJson(jsonString)
```

**kotlinx.serialization** - для Kotlin-first проектов:
```kotlin
@Serializable
data class User(val id: Int, val name: String)

val user = Json.decodeFromString<User>(jsonString)
```

**5. Ленивый парсинг больших списков**

Используйте Sequence для обработки только необходимых элементов:

```kotlin
// ❌ Плохо - парсит весь список сразу
fun parseAll(json: String): List<User> {
    val array = JSONArray(json)
    return (0 until array.length()).map { parseUser(array.getJSONObject(it)) }
}

// ✅ Хорошо - ленивый парсинг
fun parseLazy(json: String): Sequence<User> = sequence {
    val array = JSONArray(json)
    for (i in 0 until array.length()) yield(parseUser(array.getJSONObject(i)))
}

parseLazy(json).take(10).toList()  // Парсит только первые 10
```

**6. Фоновые потоки**

Выполняйте парсинг в фоновом потоке для сохранения отзывчивости UI:

```kotlin
viewModelScope.launch(Dispatchers.Default) {
    val data = parseData(jsonString)  // ✅ Парсинг в фоне
    withContext(Dispatchers.Main) { _dataLiveData.value = data }
}
```

**7. Инкрементальный парсинг**

Для больших JSON-потоков используйте JsonReader:

```kotlin
fun parseStream(stream: InputStream) = flow {
    JsonReader(stream.reader()).use { reader ->
        reader.beginArray()
        while (reader.hasNext()) emit(parseItem(reader))  // ✅ По элементу
        reader.endArray()
    }
}
```

**Таблица оптимизаций:**

| Техника | Выгода | Применение |
|---------|--------|-----------|
| Streaming | Меньше памяти | Большие XML/JSON |
| Меньше конвертаций | Быстрее | Строковые данные |
| Кеширование | Избегаем повторного парсинга | Частый доступ |
| Moshi/kotlinx | Скорость | JSON-парсинг |
| Lazy парсинг | Эффективность памяти | Большие списки |
| Фоновые потоки | Отзывчивость UI | Тяжелый парсинг |

## Answer (EN)

**1. Streaming Processing**

Use XmlPullParser instead of DOM for XML parsing. Streaming parsers process documents sequentially without loading everything into memory.

```kotlin
// ❌ Bad - DOM loads entire document
val factory = DocumentBuilderFactory.newInstance()
val doc = factory.newDocumentBuilder().parse(inputStream)

// ✅ Good - streaming parser
val parser = Xml.newPullParser().apply { setInput(inputStream, null) }
while (parser.next() != XmlPullParser.END_DOCUMENT) {
    if (parser.eventType == XmlPullParser.START_TAG && parser.name == "item") {
        parseItem(parser)
    }
}
```

**2. Reduce String Conversions**

Avoid multiple conversions between formats - parse directly from streams.

```kotlin
// ❌ Bad - multiple conversions
val jsonString = response.body?.string()
val data = JSONObject(jsonString)

// ✅ Good - direct stream parsing
val data = JSONObject(response.body?.charStream())
```

**3. Cache Parsing Results**

Cache parsed data for reuse, especially for frequently accessed data.

**4. Use Specialized Libraries**

Performance comparison (1000 objects):
- **Moshi**: ~15ms (fastest)
- **kotlinx.serialization**: ~18ms (Kotlin-native)
- **Gson**: ~25ms (flexible)
- **org.json**: ~45ms (standard Android API)

**Moshi** - best for performance:
```kotlin
@JsonClass(generateAdapter = true)
data class User(val id: Int, val name: String)

val moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
val user = moshi.adapter(User::class.java).fromJson(jsonString)
```

**kotlinx.serialization** - for Kotlin-first projects:
```kotlin
@Serializable
data class User(val id: Int, val name: String)

val user = Json.decodeFromString<User>(jsonString)
```

**5. Lazy Parse Large Lists**

Use Sequence to process only needed elements:

```kotlin
// ❌ Bad - parses entire list
fun parseAll(json: String): List<User> {
    val array = JSONArray(json)
    return (0 until array.length()).map { parseUser(array.getJSONObject(it)) }
}

// ✅ Good - lazy parsing
fun parseLazy(json: String): Sequence<User> = sequence {
    val array = JSONArray(json)
    for (i in 0 until array.length()) yield(parseUser(array.getJSONObject(i)))
}

parseLazy(json).take(10).toList()  // Parses only first 10
```

**6. Background Threads**

Parse data on background threads to keep UI responsive:

```kotlin
viewModelScope.launch(Dispatchers.Default) {
    val data = parseData(jsonString)  // ✅ Parse in background
    withContext(Dispatchers.Main) { _dataLiveData.value = data }
}
```

**7. Incremental Parsing**

For large JSON streams use JsonReader:

```kotlin
fun parseStream(stream: InputStream) = flow {
    JsonReader(stream.reader()).use { reader ->
        reader.beginArray()
        while (reader.hasNext()) emit(parseItem(reader))  // ✅ Item by item
        reader.endArray()
    }
}
```

**Optimization Summary:**

| Technique | Benefit | Use Case |
|-----------|---------|----------|
| Streaming | Lower memory | Large XML/JSON |
| Fewer conversions | Faster | String data |
| Caching | Avoid re-parsing | Frequent access |
| Moshi/kotlinx | Speed | JSON parsing |
| Lazy parsing | Memory efficient | Large lists |
| Background threads | UI responsive | Heavy parsing |

---

## Follow-ups

- How would you benchmark parsing performance for different JSON libraries in your production app?
- What trade-offs exist between Moshi's compile-time code generation and Gson's reflection-based approach?
- How do you handle parsing errors and partial data in streaming parsers?
- When should you use JsonReader directly instead of higher-level libraries like Moshi or Gson?

## References

- https://github.com/square/moshi - Moshi JSON library
- https://github.com/google/gson - Gson library
- https://developer.android.com/topic/performance - Android performance guide

## Related Questions

### Prerequisites (Easier)
- [[q-how-to-tell-adapter-to-redraw-list-when-item-removed--android--medium]] - UI updates after data changes

### Related (Same Level)
- Android performance optimization patterns
- Memory profiling techniques for data-heavy applications

### Advanced (Harder)
- Custom serialization adapters for complex data structures
- Protocol buffer alternatives for binary serialization
