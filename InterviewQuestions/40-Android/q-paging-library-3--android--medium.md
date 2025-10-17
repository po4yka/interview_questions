---
id: 20251017-145100
title: Paging Library 3 / Библиотека Paging 3
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [paging, paging3, pagination, recyclerview, difficulty/medium, android/rendering, android/architecture-clean]
language_tags: [paging, paging3, pagination, recyclerview, difficulty/medium, android/rendering, android/architecture-clean]
moc: moc-android
original_language: en
source: https://github.com/Kirchhoff-/Android-Interview-Questions
subtopics:   - performance-rendering
  - architecture-clean
---
# Paging Library 3 / Библиотека Paging 3

**English**: What do you know about paging library?

**Русский**: Что вы знаете о библиотеке Paging?

## Answer (EN)
**English**:

The **Paging Library** helps you load and display small chunks of data at a time. Loading partial data on demand reduces usage of network bandwidth and system resources.

### Supported Data Architectures

The Paging Library supports the following data architectures:
- Served only from a backend server
- Stored only in an on-device database
- A combination of the other sources, using the on-device database as a cache

In the case of a network-only or database-only solution, the data flows directly to your app's UI model. If you're using a combined approach, data flows from your backend server, into an on-device database, and then to your app's UI model. Every once in a while, the endpoint of each data flow runs out of data to load, at which point it requests more data from the component that provided the data.

### Library Architecture

#### PagedList

The Paging Library's key component is the `PagedList` class, which loads chunks of your app's data, or *pages*. As more data is needed, it's paged into the existing `PagedList` object. If any loaded data changes, a new instance of `PagedList` is emitted to the observable data holder from a `LiveData` or RxJava2-based object. As `PagedList` objects are generated, your app's UI presents their contents, all while respecting your UI controllers' lifecycles.

Example code showing how to configure your app's view model:

```kotlin
class ConcertViewModel(concertDao: ConcertDao) : ViewModel() {
    val concertList: LiveData<PagedList<Concert>> =
            concertDao.concertsByDate().toLiveData(pageSize = 50)
}
```

#### Data Source

Each instance of `PagedList` loads an up-to-date snapshot of your app's data from its corresponding `DataSource` object. Data flows from your app's backend or database into the `PagedList` object.

Example using Room persistence library:

```kotlin
@Dao
interface ConcertDao {
    // The Int type parameter tells Room to use a PositionalDataSource object.
    @Query("SELECT * FROM concerts ORDER BY date DESC")
    fun concertsByDate(): DataSource.Factory<Int, Concert>
}
```

#### UI Layer

The `PagedList` class works with a `PagedListAdapter` to load items into a `RecyclerView`. These classes work together to fetch and display content as it's loaded, prefetching out-of-view content and animating content changes.

### Benefits of Using the Paging Library

- **In-memory caching** for your paged data. This ensures that your app uses system resources efficiently while working with paged data.

- **Built-in request deduplication**, ensuring that your app uses network bandwidth and system resources efficiently.

- **Configurable RecyclerView adapters** that automatically request data as the user scrolls toward the end of the loaded data.

- **First-class support** for Kotlin coroutines and `Flow`, as well as `LiveData` and RxJava.

- **Built-in support for error handling**, including refresh and retry capabilities.

**Русский**:

**Библиотека Paging** помогает загружать и отображать небольшие порции данных за раз. Загрузка частичных данных по требованию снижает использование пропускной способности сети и системных ресурсов.

### Поддерживаемые архитектуры данных

Библиотека Paging поддерживает следующие архитектуры данных:
- Предоставление только с бэкенд-сервера
- Хранение только в локальной базе данных
- Комбинация других источников, использующая локальную базу данных в качестве кэша

В случае решения только для сети или только для базы данных, данные поступают напрямую в UI-модель вашего приложения. Если вы используете комбинированный подход, данные поступают с бэкенд-сервера в локальную базу данных, а затем в UI-модель вашего приложения. Время от времени конечная точка каждого потока данных исчерпывает данные для загрузки, и в этот момент она запрашивает больше данных от компонента, который предоставил данные.

### Архитектура библиотеки

#### PagedList

Ключевым компонентом библиотеки Paging является класс `PagedList`, который загружает фрагменты данных вашего приложения или *страницы*. По мере необходимости в дополнительных данных они добавляются в существующий объект `PagedList`. Если какие-либо загруженные данные изменяются, новый экземпляр `PagedList` отправляется в наблюдаемый держатель данных из объекта на основе `LiveData` или RxJava2. По мере генерации объектов `PagedList` UI вашего приложения представляет их содержимое, соблюдая при этом жизненные циклы UI-контроллеров.

Пример кода, показывающий, как настроить view model вашего приложения:

```kotlin
class ConcertViewModel(concertDao: ConcertDao) : ViewModel() {
    val concertList: LiveData<PagedList<Concert>> =
            concertDao.concertsByDate().toLiveData(pageSize = 50)
}
```

#### Data (Данные)

Каждый экземпляр `PagedList` загружает актуальный снимок данных вашего приложения из соответствующего объекта `DataSource`. Данные поступают из бэкенда вашего приложения или базы данных в объект `PagedList`.

Пример использования библиотеки Room:

```kotlin
@Dao
interface ConcertDao {
    // Параметр типа Int указывает Room использовать объект PositionalDataSource
    @Query("SELECT * FROM concerts ORDER BY date DESC")
    fun concertsByDate(): DataSource.Factory<Int, Concert>
}
```

#### UI (Пользовательский интерфейс)

Класс `PagedList` работает с `PagedListAdapter` для загрузки элементов в `RecyclerView`. Эти классы работают вместе, чтобы получать и отображать контент по мере его загрузки, предварительно загружая контент вне области просмотра и анимируя изменения контента.

### Преимущества использования библиотеки Paging

- **Кэширование в памяти** для ваших страничных данных. Это гарантирует, что ваше приложение эффективно использует системные ресурсы при работе со страничными данными.

- **Встроенная дедупликация запросов**, гарантирующая, что ваше приложение эффективно использует пропускную способность сети и системные ресурсы.

- **Настраиваемые адаптеры RecyclerView**, которые автоматически запрашивают данные, когда пользователь прокручивает до конца загруженных данных.

- **Первоклассная поддержка** Kotlin coroutines и `Flow`, а также `LiveData` и RxJava.

- **Встроенная поддержка обработки ошибок**, включая возможности обновления и повторной попытки.

## References

- [Paging Library Overview](https://developer.android.com/topic/libraries/architecture/paging)
- [Paging 3 Overview](https://developer.android.com/topic/libraries/architecture/paging/v3-overview)
- [Custom DataSource](https://developer.android.com/topic/libraries/architecture/paging/data#custom-data-source)
