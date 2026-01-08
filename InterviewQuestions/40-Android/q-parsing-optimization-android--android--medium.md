---\
id: android-130
title: Parsing Optimization Android / Оптимизация парсинга Android
aliases: [Parsing Optimization Android, Оптимизация парсинга Android]
topic: android
subtopics: [performance-memory, serialization]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-memory-management, q-android-build-optimization--android--medium, q-how-to-tell-adapter-to-redraw-list-when-item-removed--android--medium, q-optimize-memory-usage-android--android--medium, q-performance-optimization-android--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/performance-memory, android/serialization, difficulty/medium, json, optimization, xml]

---\
# Вопрос (RU)

> Где можно оптимизировать парсинг в Android-приложениях?

# Question (EN)

> Where can parsing be optimized in Android applications?

---

## Ответ (RU)

**1. Потоковый парсинг (Streaming)**

Используйте XmlPullParser вместо DOM для обработки XML. Потоковый парсинг обрабатывает документ последовательно, не загружая всё в память целиком.

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

Избегайте множественных конвертаций между форматами и лишнего создания строк — по возможности парсите напрямую из потока / Reader, используя библиотеки, которые это поддерживают.

```kotlin
// ❌ Плохо - несколько преобразований и аллокаций
val jsonString = response.body?.string() // читает всё тело в память
val data = JSONObject(jsonString)

// ✅ Лучше - используем Reader/stream с поддерживающей библиотекой (пример с Gson)
val reader = response.body?.charStream()
val gson = Gson()
val user = gson.fromJson(reader, User::class.java)
```

(Базовый org.json не умеет напрямую парсить из Reader, ему всё равно нужна строка или токенайзер.)

**3. Кеширование результатов**

Кешируйте распарсенные данные для повторного использования, особенно если данные запрашиваются часто.

**4. Специализированные библиотеки**

Чем современнее и менее рефлексивна библиотека, тем лучше с точки зрения производительности и аллокаций.

Иллюстративное сравнение (1000 объектов, условные значения, зависят от окружения и конфигурации):
- **`Moshi`**: ~15ms (часто одна из самых быстрых)
- **kotlinx.serialization**: ~18ms (нативная для Kotlin; особенно эффективна с сгенерированными сериализаторами)
- **`Gson`**: ~25ms (универсальная, основана на рефлексии по умолчанию)
- **org.json**: ~45ms (стандартная Android API, без оптимизаций под большие объёмы)

**`Moshi`** - хороший выбор для производительности:
```kotlin
@JsonClass(generateAdapter = true)
data class User(val id: Int, val name: String)

val moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
val user = moshi.adapter(User::class.java).fromJson(jsonString)
```

**kotlinx.serialization** - для Kotlin-first проектов (с генерацией сериализаторов для максимальной эффективности):
```kotlin
@Serializable
data class User(val id: Int, val name: String)

val user = Json.decodeFromString<User>(jsonString)
```

**5. Ленивый парсинг больших списков**

Используйте Sequence для ленивой обработки коллекции уже загруженных данных, когда не нужны все элементы сразу.

```kotlin
// ❌ Плохо - парсит весь список сразу и создаёт все объекты
fun parseAll(json: String): List<User> {
    val array = JSONArray(json)
    return (0 until array.length()).map { parseUser(array.getJSONObject(it)) }
}

// ✅ Лучше - ленивое создание объектов поверх уже загруженного JSON
fun parseLazy(json: String): Sequence<User> = sequence {
    val array = JSONArray(json)
    for (i in 0 until array.length()) yield(parseUser(array.getJSONObject(i)))
}

parseLazy(json).take(10).toList()  // Создаёт только первые 10 объектов
```

(Обратите внимание: JSONArray всё равно требует иметь весь JSON в памяти; для настоящего стриминга используйте потоковые API: JsonReader (`Gson`), `Moshi` streaming, kotlinx.serialization JSON-streaming и т.п.)

**6. Фоновые потоки**

Выполняйте парсинг в фоновом потоке для сохранения отзывчивости UI:

```kotlin
viewModelScope.launch(Dispatchers.Default) {
    val data = parseData(jsonString)  // ✅ Парсинг в фоне
    withContext(Dispatchers.Main) { _dataLiveData.value = data }
}
```

**7. Инкрементальный парсинг**

Для больших JSON-потоков используйте потоковые API, например JsonReader из `Gson` или аналогичные механизмы в Moshi/kotlinx.serialization.

```kotlin
fun parseStream(stream: InputStream) = flow {
    com.google.gson.stream.JsonReader(InputStreamReader(stream, Charsets.UTF_8)).use { reader ->
        reader.beginArray()
        while (reader.hasNext()) emit(parseItem(reader))  // ✅ По элементу за раз
        reader.endArray()
    }
}
```

**Таблица оптимизаций:**

| Техника | Выгода | Применение |
|---------|--------|-----------|
| Streaming | Меньше памяти | Большие XML/JSON |
| Меньше конвертаций | Быстрее, меньше аллокаций | Ответы HTTP, парсинг из потока |
| Кеширование | Избегаем повторного парсинга | Частый доступ |
| Moshi/kotlinx | Скорость, меньше рефлексии | JSON-парсинг |
| Lazy парсинг | Меньше ненужных объектов | Обработка подмножеств списков |
| Фоновые потоки | Отзывчивость UI | Тяжелый парсинг |
| Инкрементальный парсинг | Стриминг без пиков по памяти | Очень большие массивы / потоки данных |

---

## Answer (EN)

**1. Streaming Processing**

Use XmlPullParser instead of DOM for XML parsing. Streaming parsers process documents sequentially without loading the entire document into memory.

```kotlin
// ❌ Bad - DOM loads entire document in memory
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

**2. Reduce `String` Conversions**

Avoid multiple conversions and unnecessary string allocations. Whenever possible, parse directly from streams/Readers using libraries that support it.

```kotlin
// ❌ Bad - multiple conversions and allocations
val jsonString = response.body?.string() // loads entire body into memory
val data = JSONObject(jsonString)

// ✅ Better - use Reader/stream with a library that supports it (example with Gson)
val reader = response.body?.charStream()
val gson = Gson()
val user = gson.fromJson(reader, User::class.java)
```

(Note: core org.json does not support constructing JSONObject directly from a Reader; it still requires a `String` or a tokenizer.)

**3. Cache Parsing Results**

Cache parsed data for reuse, especially for frequently accessed data.

**4. Use Specialized Libraries**

Prefer modern libraries that minimize reflection and allocations.

Illustrative comparison (1000 objects; rough values, highly environment- and configuration-dependent):
- **`Moshi`**: ~15ms (often among the fastest)
- **kotlinx.serialization**: ~18ms (Kotlin-native; especially efficient with generated serializers)
- **`Gson`**: ~25ms (flexible, reflection-based by default)
- **org.json**: ~45ms (standard Android API, not optimized for large payloads)

**`Moshi`** - strong choice for performance:
```kotlin
@JsonClass(generateAdapter = true)
data class User(val id: Int, val name: String)

val moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
val user = moshi.adapter(User::class.java).fromJson(jsonString)
```

**kotlinx.serialization** - ideal for Kotlin-first projects (with generated serializers for best performance):
```kotlin
@Serializable
data class User(val id: Int, val name: String)

val user = Json.decodeFromString<User>(jsonString)
```

**5. Lazy Parse Large Lists**

Use Sequence for lazy object creation over already-loaded JSON when you only need part of the data.

```kotlin
// ❌ Bad - parses entire list and creates all objects
fun parseAll(json: String): List<User> {
    val array = JSONArray(json)
    return (0 until array.length()).map { parseUser(array.getJSONObject(it)) }
}

// ✅ Better - lazy object creation over existing JSON
fun parseLazy(json: String): Sequence<User> = sequence {
    val array = JSONArray(json)
    for (i in 0 until array.length()) yield(parseUser(array.getJSONObject(i)))
}

parseLazy(json).take(10).toList()  // Only creates first 10 objects
```

(Note: JSONArray still requires the full JSON string in memory; for true streaming use streaming APIs such as JsonReader (`Gson`), `Moshi` streaming adapters, or kotlinx.serialization streaming.)

**6. Background Threads**

Parse data on background threads to keep the UI responsive:

```kotlin
viewModelScope.launch(Dispatchers.Default) {
    val data = parseData(jsonString)  // ✅ Parse in background
    withContext(Dispatchers.Main) { _dataLiveData.value = data }
}
```

**7. Incremental Parsing**

For large JSON streams, use streaming APIs such as JsonReader from `Gson` or equivalent mechanisms in Moshi/kotlinx.serialization.

```kotlin
fun parseStream(stream: InputStream) = flow {
    com.google.gson.stream.JsonReader(InputStreamReader(stream, Charsets.UTF_8)).use { reader ->
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
| Fewer conversions | Faster, fewer allocations | HTTP responses, stream parsing |
| Caching | Avoid re-parsing | Frequent access |
| Moshi/kotlinx | Speed, less reflection | JSON parsing |
| Lazy parsing | Avoid unnecessary objects | Subsets of large lists |
| Background threads | UI responsive | Heavy parsing |
| Incremental parsing | Streaming without memory spikes | Very large arrays/data streams |

---

## Дополнительные Вопросы (RU)

- Как бы вы измеряли производительность парсинга для разных JSON-библиотек в боевом приложении?
- Какие трейд-оффы существуют между компиляционной генерацией кода в Moshi/kotlinx.serialization и рефлексивным подходом `Gson`?
- Как вы обрабатываете ошибки парсинга и частичные данные при потоковом парсинге?
- В каких случаях стоит использовать JsonReader напрямую вместо более высокоуровневых библиотек вроде `Moshi` или `Gson`?

## Follow-ups

- How would you benchmark parsing performance for different JSON libraries in your production app?
- What trade-offs exist between `Moshi`'s/kotlinx.serialization's compile-time code generation and `Gson`'s reflection-based approach?
- How do you handle parsing errors and partial data in streaming parsers?
- When should you use JsonReader directly instead of higher-level libraries like `Moshi` or `Gson`?

---

## Ссылки (RU)

- https://github.com/square/moshi - библиотека `Moshi` для JSON
- https://github.com/google/gson - библиотека `Gson`
- https://developer.android.com/topic/performance - руководство по производительности Android

## References

- https://github.com/square/moshi - `Moshi` JSON library
- https://github.com/google/gson - `Gson` library
- https://developer.android.com/topic/performance - Android performance guide

---

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-memory-management]]

### Предпосылки (Проще)

- [[q-how-to-tell-adapter-to-redraw-list-when-item-removed--android--medium]] - Обновление UI после изменения данных

### Похожие (Тот Же уровень)

- Паттерны оптимизации производительности Android
- Подходы к профилированию памяти для приложений с интенсивным использованием данных

### Продвинутые (Сложнее)

- Пользовательские адаптеры сериализации для сложных структур данных
- Альтернативы в виде Protocol Buffers для бинарной сериализации

## Related Questions

### Prerequisites / Concepts

- [[c-memory-management]]

### Prerequisites (Easier)

- [[q-how-to-tell-adapter-to-redraw-list-when-item-removed--android--medium]] - UI updates after data changes

### Related (Same Level)

- Android performance optimization patterns
- Memory profiling techniques for data-heavy applications

### Advanced (Harder)

- Custom serialization adapters for complex data structures
- Protocol buffer alternatives for binary serialization
