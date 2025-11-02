---
id: android-491
title: "Testing ViewModels with Turbine / Тестирование ViewModels с Turbine"
aliases: [Testing ViewModels, Turbine, Turbine Library, Тестирование ViewModels]

# Classification
topic: android
subtopics: [coroutines, testing-unit, viewmodel]
question_kind: android
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source:
source_note:

# Workflow & relations
status: draft
moc: moc-android
related: [c-flow, c-viewmodel]

# Timestamps
created: 2025-10-15
updated: 2025-11-01

# Tags (EN only; no leading #)
tags: [android/coroutines, android/testing-unit, android/viewmodel, coroutines, difficulty/medium, flow, testing, turbine]
date created: Saturday, November 1st 2025, 1:24:35 pm
date modified: Saturday, November 1st 2025, 5:43:31 pm
---

# Question (EN)
> How do you test ViewModels that emit Flow/StateFlow using the Turbine library?

# >?@>A (RU)
> 0: B5AB8@>20BL ViewModels, :>B>@K5 8A?>;L7CNB Flow/StateFlow, A ?><>ILN 181;8>B5:8 Turbine?

---

## Answer (EN)

**Approach**: Turbine is a testing library that simplifies testing Kotlin Flows by providing a readable API for asserting Flow emissions over time.

**Key Concepts**:
- Turbine allows you to test Flow emissions sequentially
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
1. **test {}** - Turbine's main extension function that collects Flow emissions
2. **awaitItem()** - Suspends until next emission and returns it
3. **expectNoEvents()** - Asserts that no more events are emitted
4. **cancelAndIgnoreRemainingEvents()** - Cancels collection when you don't care about remaining emissions
5. **runTest** - Coroutine test dispatcher for controlling virtual time

**Benefits**:
- More readable than manual Flow collection
- Built-in timeout handling
- Clear assertion API
- Works with StateFlow, SharedFlow, and regular Flows

## B25B (RU)

**>4E>4**: Turbine - MB> 181;8>B5:0 4;O B5AB8@>20=8O, :>B>@0O C?@>I05B B5AB8@>20=85 Kotlin Flow, ?@54>AB02;OO G8B05<K9 API 4;O ?@>25@:8 M<8AA89 Flow 2> 2@5<5=8.

**;NG52K5 :>=F5?F88**:
- Turbine ?>72>;O5B B5AB8@>20BL M<8AA88 Flow ?>A;54>20B5;L=>
- @54>AB02;O5B @0AH8@5=85 `test {}` 4;O Flow
- >445@68205B B5AB8@>20=85 <=>65AB25==KE M<8AA89, >H81>: 8 7025@H5=8O
- %>@>H> @01>B05B A B5AB>2K<8 48A?5BG5@0<8 :>@CB8=

**>4**: (A<. 2KH5)

**1JOA=5=85**:
1. **test {}** - >A=>2=0O DC=:F8O-@0AH8@5=85 Turbine, :>B>@0O A>18@05B M<8AA88 Flow
2. **awaitItem()** - ?@8>AB0=02;8205BAO 4> A;54CNI59 M<8AA88 8 2>72@0I05B 5Q
3. **expectNoEvents()** - ?@>25@O5B, GB> 1>;LH5 =5B A>1KB89
4. **cancelAndIgnoreRemainingEvents()** - >B<5=O5B A1>@, :>340 >AB0;L=K5 M<8AA88 =5 206=K
5. **runTest** - B5AB>2K9 48A?5BG5@ :>@CB8= 4;O C?@02;5=8O 28@BC0;L=K< 2@5<5=5<

**@58<CI5AB20**:
- >;55 G8B05<>, G5< @CG=>9 A1>@ Flow
- AB@>5==0O >1@01>B:0 B09<0CB>2
- >=OB=K9 API 4;O ?@>25@>:
-  01>B05B A StateFlow, SharedFlow 8 >1KG=K<8 Flow

---

## Follow-ups

- How do you test multiple Flows simultaneously with Turbine?
- What's the difference between `awaitItem()` and `expectMostRecentItem()`?
- How do you handle timeouts in Turbine tests?
- Can Turbine be used with SharedFlow and hot Flows?

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
- [[q-testing-strategies-advanced--android--hard]]
