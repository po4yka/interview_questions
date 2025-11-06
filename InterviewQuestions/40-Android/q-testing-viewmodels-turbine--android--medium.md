---
id: android-491
title: Testing ViewModels with Turbine / Тестирование ViewModels с Turbine
aliases:
- Testing ViewModels
- Turbine
- Turbine Library
- Тестирование ViewModels
topic: android
subtopics:
- coroutines
- testing-unit
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-flow
- c-viewmodel
created: 2025-10-15
updated: 2025-11-01
tags:
- android/coroutines
- android/testing-unit
- coroutines
- difficulty/medium
- flow
- testing
- turbine
---

# Вопрос (RU)
> Тестирование ViewModels с Turbine

# Question (EN)
> How do you test ViewModels that emit `Flow`/`StateFlow` using the Turbine library?

---

## Answer (EN)

**Approach**: Turbine is a testing library that simplifies testing Kotlin Flows by providing a readable API for asserting `Flow` emissions over time.

**Key Concepts**:
- Turbine allows you to test `Flow` emissions sequentially
- Provides `test {}` extension function for Flows
- Supports testing multiple emissions, errors, and completion
- Works well with coroutine test dispatchers

**Code**:

```kotlin
// Example ViewModel
class UserViewModel(
 private val repository: UserRepository
) : ViewModel() {
 private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
 val uiState: StateFlow<UiState> = _uiState.asStateFlow()

 fun loadUser(userId: String) {
 viewModelScope.launch {
 _uiState.value = UiState.Loading
 try {
 val user = repository.getUser(userId)
 _uiState.value = UiState.Success(user)
 } catch (e: Exception) {
 _uiState.value = UiState.Error(e.message)
 }
 }
 }
}

// Test with Turbine
@Test
fun `loadUser emits Loading then Success states`() = runTest {
 // Given
 val mockUser = User("123", "John Doe")
 val repository = FakeUserRepository(mockUser)
 val viewModel = UserViewModel(repository)

 // When/Then
 viewModel.uiState.test {
 // Initial state
 assertEquals(UiState.Loading, awaitItem())

 // Trigger action
 viewModel.loadUser("123")

 // Loading state
 assertEquals(UiState.Loading, awaitItem())

 // Success state
 val successItem = awaitItem()
 assertTrue(successItem is UiState.Success)
 assertEquals(mockUser, (successItem as UiState.Success).user)

 // No more emissions
 expectNoEvents()
 }
}

@Test
fun `loadUser emits Error when repository fails`() = runTest {
 // Given
 val repository = FakeUserRepository(shouldFail = true)
 val viewModel = UserViewModel(repository)

 // When/Then
 viewModel.uiState.test {
 awaitItem() // Initial Loading

 viewModel.loadUser("123")

 awaitItem() // Loading state

 val errorItem = awaitItem()
 assertTrue(errorItem is UiState.Error)

 cancelAndIgnoreRemainingEvents()
 }
}
```

**Explanation**:
1. **test {}** - Turbine's main extension function that collects `Flow` emissions
2. **awaitItem()** - Suspends until next emission and returns it
3. **expectNoEvents()** - Asserts that no more events are emitted
4. **cancelAndIgnoreRemainingEvents()** - Cancels collection when you don't care about remaining emissions
5. **runTest** - `Coroutine` test dispatcher for controlling virtual time

**Benefits**:
- More readable than manual `Flow` collection
- Built-in timeout handling
- Clear assertion API
- Works with `StateFlow`, `SharedFlow`, and regular Flows

## Ответ (RU)

**Подход**: Turbine - это библиотека для тестирования, которая упрощает тестирование Kotlin `Flow`, предоставляя читаемый API для проверки эмиссий `Flow` во времени.

**Ключевые концепции**:
- Turbine позволяет тестировать эмиссии `Flow` последовательно
- Предоставляет расширение `test {}` для `Flow`
- Поддерживает тестирование множественных эмиссий, ошибок и завершения
- Хорошо работает с тестовыми диспетчерами корутин

**Код**: (см. выше в английской секции)

**Объяснение**:
1. **test {}** - основная функция-расширение Turbine, которая собирает эмиссии `Flow`
2. **awaitItem()** - приостанавливается до следующей эмиссии и возвращает её
3. **expectNoEvents()** - проверяет, что больше нет событий
4. **cancelAndIgnoreRemainingEvents()** - отменяет сбор, когда остальные эмиссии не важны
5. **runTest** - тестовый диспетчер корутин для управления виртуальным временем

**Преимущества**:
- Более читаемо, чем ручной сбор `Flow`
- Встроенная обработка таймаутов
- Понятный API для проверок
- Работает с `StateFlow`, `SharedFlow` и обычными `Flow`

---

## Follow-ups

- How do you test multiple Flows simultaneously with Turbine?
- What's the difference between `awaitItem()` and `expectMostRecentItem()`?
- How do you handle timeouts in Turbine tests?
- Can Turbine be used with `SharedFlow` and hot Flows?

## References

- [[c-viewmodel]]
- [[q-what-is-viewmodel--android--medium]]
- [[q-testing-viewmodels-coroutines--kotlin--medium]]
- https://github.com/cashapp/turbine
- https://developer.android.com/kotlin/flow/test

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]]
- [[q-what-is-viewmodel--android--medium]]

### Related (Same Level)
- [[q-testing-viewmodels-coroutines--kotlin--medium]]
- [[q-viewmodel-coroutines-lifecycle--kotlin--medium]]
- [[q-android-testing-strategies--android--medium]]

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]]
- 
