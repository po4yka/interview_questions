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
related: [q-viewmodel-vs-onsavedinstancestate--android--medium, q-what-is-intent--android--easy, q-why-user-data-may-disappear-on-screen-rotation--android--hard]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/intents-deeplinks, android/lifecycle, android/performance-memory, binder, difficulty/medium, exceptions, intent, savedinstancestate]

---

# Вопрос (RU)

> Что такое TransactionTooLargeException и как его избежать?

# Question (EN)

> What is TransactionTooLargeException and how to avoid it?

---

## Ответ (RU)

**TransactionTooLargeException** — исключение при превышении лимита **1MB в Binder** — IPC-механизме Android для передачи данных между процессами.

**Типичные ситуации:**
- Передача больших объектов через `Intent`/`Bundle`
- Сохранение крупных данных в onSaveInstanceState
- Передача bitmap или списков между `Activity`/`Fragment`

### Основные Решения

**1. Передавать ID вместо объекта**

```kotlin
// ❌ Передача всего объекта
intent.putExtra("user", largeUser) // может превысить 1MB

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

// Во Fragment - без Bundle
private val sharedViewModel: SharedViewModel by activityViewModels()
```

**4. Минимизация onSaveInstanceState**

```kotlin
// ✅ Сохранять только критичное состояние
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("scroll_position", recyclerView.scrollY) // только позиция
    outState.putInt("selected_id", selectedUser?.id ?: -1)    // только ID
}
```

### Лимиты Binder

- **1 MB** — общий буфер на процесс для всех транзакций
- Размер `Bundle` измеряется через Parcel serialization
- Лимит разделяется между всеми активными IPC-вызовами

## Answer (EN)

**TransactionTooLargeException** occurs when data exceeds the **1MB Binder limit** — Android's IPC mechanism for inter-process communication.

**Common scenarios:**
- Passing large objects via `Intent`/`Bundle`
- Saving large data in onSaveInstanceState
- Transferring bitmaps or lists between `Activity`/`Fragment`

### Primary Solutions

**1. Pass ID instead of object**

```kotlin
// ❌ Passing entire object
intent.putExtra("user", largeUser) // may exceed 1MB

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
// ✅ Save only critical state
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("scroll_position", recyclerView.scrollY) // position only
    outState.putInt("selected_id", selectedUser?.id ?: -1)    // ID only
}
```

### Binder Limits

- **1 MB** — total per-process buffer for all transactions
- `Bundle` size measured via Parcel serialization
- Limit shared across all active IPC calls

---

## Follow-ups

- How does Binder transaction buffer work across multiple concurrent IPC calls?
- What's the difference between process death and configuration change regarding state restoration?
- When should you use `ContentProvider` vs file-based approach for large data sharing?
- How do you measure `Bundle` size in production to prevent TransactionTooLargeException?

## References

- 
- [[c-intent]]
- [[c-viewmodel]]
- 

## Related Questions

### Prerequisites
- [[q-what-is-intent--android--easy]]
- [[q-what-is-viewmodel--android--medium]]

### Related
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]]
- [[q-what-is-workmanager--android--medium]]

### Advanced
- [[q-why-user-data-may-disappear-on-screen-rotation--android--hard]]
