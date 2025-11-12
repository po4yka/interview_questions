---
id: android-168
title: "TransactionTooLargeException / Исключение TransactionTooLargeException"
aliases: ["TransactionTooLargeException", "Исключение TransactionTooLargeException"]
topic: android
subtopics: [intents-deeplinks, lifecycle, performance-memory]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, q-viewmodel-vs-onsavedinstancestate--android--medium, q-what-is-intent--android--easy, q-why-user-data-may-disappear-on-screen-rotation--android--hard]
created: 2024-10-15
updated: 2025-11-11
sources: []
tags: [android/intents-deeplinks, android/lifecycle, android/performance-memory, binder, difficulty/medium, exceptions, intent, savedinstancestate]

---

# Вопрос (RU)

> Что такое TransactionTooLargeException и как его избежать?

# Question (EN)

> What is TransactionTooLargeException and how to avoid it?

---

## Ответ (RU)

**TransactionTooLargeException** — исключение, возникающее при превышении допустимого размера данных в Binder-транзакции (ориентировочно около **1MB на транзакцию**), используемой Android для IPC и взаимодействия компонентов (даже внутри одного процесса).

**Типичные ситуации:**
- Передача больших объектов через `Intent`/`Bundle` (между `Activity`, `Fragment`, `Service`, в том числе внутри одного процесса)
- Сохранение крупных данных в onSaveInstanceState
- Передача bitmap или больших списков между `Activity`/`Fragment`

### Основные Решения

**1. Передавать ID вместо объекта**

```kotlin
// ❌ Передача всего объекта
intent.putExtra("user", largeUser) // может превысить лимит Binder-транзакции

// ✅ Передача только ID
intent.putExtra("user_id", userId)
val user = repository.getUserById(userId)
```

**2. Использовать файловое хранилище**

```kotlin
// ✅ Сохранение bitmap в файл
val imageFile = File(cacheDir, "temp.jpg")
bitmap.compress(CompressFormat.JPEG, 90, FileOutputStream(imageFile))
intent.putExtra("image_path", imageFile.absolutePath)
```

**3. `ViewModel` для `Fragment`**

```kotlin
// ✅ Разделяемые данные через ViewModel
class SharedViewModel : ViewModel() {
    val userData = MutableLiveData<List<User>>()
}

// В Activity
sharedViewModel.userData.value = largeList

// Во Fragment - без передачи через Bundle
private val sharedViewModel: SharedViewModel by activityViewModels()
```

**4. Минимизация onSaveInstanceState**

```kotlin
// ✅ Сохранять только критичное и компактное состояние
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    val layoutManager = recyclerView.layoutManager as? LinearLayoutManager
    val firstVisible = layoutManager?.findFirstVisibleItemPosition() ?: 0
    outState.putInt("scroll_position", firstVisible) // позиция элемента, а не пиксели
    outState.putInt("selected_id", selectedUser?.id ?: -1) // только ID
}
```

### Лимиты Binder

- Практический предел — около **1 MB на одну Binder-транзакцию** (включая служебные данные сериализации через Parcel)
- Также существует общий пул буфера Binder, разделяемый между транзакциями процесса; крупные или параллельные транзакции могут привести к ошибке до достижения номинального предела
- Поэтому следует избегать передачи крупных структур данных через `Intent`/`Bundle` и onSaveInstanceState

## Answer (EN)

**TransactionTooLargeException** is thrown when the data sent in a Binder transaction exceeds the allowed size (approximately **1 MB per transaction**), used by Android for IPC and component communication (including within the same process).

**Common scenarios:**
- Passing large objects via `Intent`/`Bundle` (between `Activity`, `Fragment`, `Service`, including in-process)
- Saving large data in onSaveInstanceState
- Transferring bitmaps or large lists between `Activity`/`Fragment`

### Primary Solutions

**1. Pass ID instead of object**

```kotlin
// ❌ Passing entire object
intent.putExtra("user", largeUser) // may exceed Binder transaction limit

// ✅ Pass ID only
intent.putExtra("user_id", userId)
val user = repository.getUserById(userId)
```

**2. Use file storage**

```kotlin
// ✅ Save bitmap to file
val imageFile = File(cacheDir, "temp.jpg")
bitmap.compress(CompressFormat.JPEG, 90, FileOutputStream(imageFile))
intent.putExtra("image_path", imageFile.absolutePath)
```

**3. `ViewModel` for fragments**

```kotlin
// ✅ Share data via ViewModel
class SharedViewModel : ViewModel() {
    val userData = MutableLiveData<List<User>>()
}

// In Activity
sharedViewModel.userData.value = largeList

// In Fragment - no Bundle needed
private val sharedViewModel: SharedViewModel by activityViewModels()
```

**4. Minimize onSaveInstanceState**

```kotlin
// ✅ Save only critical and compact state
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    val layoutManager = recyclerView.layoutManager as? LinearLayoutManager
    val firstVisible = layoutManager?.findFirstVisibleItemPosition() ?: 0
    outState.putInt("scroll_position", firstVisible) // item position, not pixel offset
    outState.putInt("selected_id", selectedUser?.id ?: -1) // ID only
}
```

### Binder Limits

- Practical cap is about **1 MB per Binder transaction** (including Parcel overhead)
- There is also a shared Binder buffer pool used by transactions in the process; large or concurrent transactions can fail before the nominal cap is reached
- Therefore avoid sending large data structures via `Intent`/`Bundle` and onSaveInstanceState

---

## Дополнительные вопросы (RU)

- Как работает буфер Binder-транзакций при нескольких одновременных IPC-вызовах?
- В чем разница между смертью процесса и изменением конфигурации с точки зрения восстановления состояния?
- Когда стоит использовать `ContentProvider` вместо файлового подхода для обмена большими данными?
- Как измерять размер `Bundle` в продакшене, чтобы предотвратить TransactionTooLargeException?

## Follow-ups

- How does Binder transaction buffer work across multiple concurrent IPC calls?
- What's the difference between process death and configuration change regarding state restoration?
- When should you use `ContentProvider` vs file-based approach for large data sharing?
- How do you measure `Bundle` size in production to prevent TransactionTooLargeException?

## Ссылки (RU)

- [[c-android]]

## References

- [[c-android]]

## Связанные вопросы (RU)

### Предварительные
- [[q-what-is-intent--android--easy]]

### Связанные
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]]
- [[q-why-user-data-may-disappear-on-screen-rotation--android--hard]]

### Продвинутые
- [[q-why-user-data-may-disappear-on-screen-rotation--android--hard]]

## Related Questions

### Prerequisites
- [[q-what-is-intent--android--easy]]

### Related
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]]
- [[q-why-user-data-may-disappear-on-screen-rotation--android--hard]]

### Advanced
- [[q-why-user-data-may-disappear-on-screen-rotation--android--hard]]
