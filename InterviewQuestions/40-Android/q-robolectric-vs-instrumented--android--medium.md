---
id: android-323
title: "Robolectric Vs Instrumented / Robolectric против Instrumented"
aliases: ["Robolectric Vs Instrumented", "Robolectric против Instrumented"]

# Classification
topic: android
subtopics: [testing-instrumented, testing-unit]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: []

# Workflow & relations
status: draft
moc: moc-android
related: [q-junit-basics--android--easy, q-test-flakiness-strategies--android--hard, q-unit-testing-basics--android--easy]

# Timestamps
created: 2025-10-15
updated: 2025-10-28

# Tags (EN only; no leading #)
tags: [android/testing-instrumented, android/testing-unit, comparison, difficulty/medium, robolectric, strategy]
---

# Вопрос (RU)

> Когда следует использовать Robolectric вместо инструментальных тестов? Какие компромиссы в скорости, надежности и покрытии?

# Question (EN)

> When should you use Robolectric vs instrumented tests? What are the tradeoffs in speed, reliability, and coverage?

---

## Ответ (RU)

**Robolectric** выполняет Android-тесты на JVM без устройства/эмулятора, **Инструментальные тесты** работают на реальном Android. У каждого подхода свои преимущества и компромиссы.

### Основные Различия

**Robolectric** (JVM-тесты):
- Симулирует Android Framework на JVM
- Быстрые (1-10 сек)
- Не требуют устройство или эмулятор
- Легко интегрируются в CI/CD
- Могут иметь тонкие различия с реальным устройством

**Инструментальные тесты** (реальные устройства):
- Выполняются на настоящем Android
- Медленные (10-60+ сек)
- Тестируют реальное поведение устройства
- Требуют эмулятор/устройство
- Могут быть нестабильными (flaky)

### Когда Использовать Robolectric

**Подходит для:**
- Тестирование ViewModel с Android-зависимостями
- Проверка жизненного цикла Activity/Fragment
- Тестирование Resources, Context, SharedPreferences
- Создание Intent и навигация
- Быстрая обратная связь в CI

```kotlin
@RunWith(RobolectricTestRunner::class)
class UserViewModelTest {
    @Test
    fun loadUser_updatesState() = runTest {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val viewModel = UserViewModel(context)

        viewModel.loadUser(1)

        // ✅ Быстрая проверка состояния
        assertTrue(viewModel.uiState.value is UiState.Success)
    }
}
```

### Когда Использовать Инструментальные Тесты

**Подходит для:**
- Сложные UI-взаимодействия (swipe, drag, animations)
- Работа с hardware (камера, GPS, сенсоры)
- Тестирование производительности
- Интеграция с SDK третьих сторон (Firebase, Google Maps)
- Pixel-perfect скриншотные тесты

```kotlin
@RunWith(AndroidJUnit4::class)
class ComplexUiTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun swipeToDelete_removesItem() {
        composeTestRule
            .onNodeWithText("Item 1")
            .performTouchInput { swipeLeft() }

        // ✅ Реальное поведение жестов
        composeTestRule
            .onNodeWithText("Item 1")
            .assertDoesNotExist()
    }
}
```

### Сравнение

| Аспект | Robolectric | Инструментальные |
|--------|-------------|------------------|
| Скорость | Быстро (1-10с) | Медленно (10-60с+) |
| Устройство | Не требуется | Требуется |
| CI/CD | Легко | Нужен эмулятор |
| Надежность | Стабильные | Могут быть flaky |
| Реальность | Симуляция | Настоящий Android |
| Hardware | Mock | Реальные сенсоры |

### Пирамида Тестирования

Рекомендуемое распределение:
- **70%** - Unit-тесты (чистый JVM)
- **20%** - Интеграционные (Robolectric)
- **10%** - E2E (Инструментальные)

```kotlin
// 70% - Unit-тесты
class CalculatorTest {
    @Test
    fun add_returnsSum() {
        assertEquals(5, Calculator().add(2, 3))
    }
}

// 20% - Robolectric
@RunWith(RobolectricTestRunner::class)
class ViewModelIntegrationTest {
    @Test
    fun loadData_updatesState() = runTest {
        // ✅ Проверка интеграции с Android
    }
}

// 10% - Инструментальные E2E
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {
    @Test
    fun login_navigatesToHome() {
        // ✅ Полный путь пользователя
    }
}
```

### Лучшие Практики

1. **Начинайте с unit-тестов** для бизнес-логики
2. **Используйте Robolectric** для интеграционных тестов с Android
3. **Оставьте инструментальные** для критических сценариев
4. **Комбинируйте подходы** для оптимального покрытия

**Гибридный подход:**

```kotlin
// Robolectric: бизнес-логика + простой UI
@RunWith(RobolectricTestRunner::class)
class UserProfileFragmentTest {
    @Test
    fun loadProfile_displaysInfo() {
        val fragment = launchFragment<UserProfileFragment>()
        // ✅ Быстрая проверка
    }
}

// Инструментальные: критические сценарии
@RunWith(AndroidJUnit4::class)
class UserProfileE2ETest {
    @Test
    fun editProfile_syncsToBackend() {
        // ✅ Полная интеграция
    }
}
```

---

## Answer (EN)

**Robolectric** runs Android tests on the JVM without a device/emulator, while **Instrumented tests** run on actual Android devices. Each has distinct advantages and tradeoffs.

### Key Differences

**Robolectric** (JVM tests):
- Simulates Android Framework on JVM
- Fast (1-10 seconds)
- No device/emulator needed
- Easy CI/CD integration
- May have subtle differences from real device

**Instrumented tests** (real devices):
- Run on actual Android
- Slow (10-60+ seconds)
- Test real device behavior
- Require emulator/device
- Can be flaky

### When to Use Robolectric

**Good for:**
- Testing ViewModels with Android dependencies
- Verifying Activity/Fragment lifecycle
- Testing Resources, Context, SharedPreferences
- Intent creation and navigation
- Fast CI feedback

```kotlin
@RunWith(RobolectricTestRunner::class)
class UserViewModelTest {
    @Test
    fun loadUser_updatesState() = runTest {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val viewModel = UserViewModel(context)

        viewModel.loadUser(1)

        // ✅ Fast state verification
        assertTrue(viewModel.uiState.value is UiState.Success)
    }
}
```

### When to Use Instrumented Tests

**Good for:**
- Complex UI interactions (swipe, drag, animations)
- Hardware integration (camera, GPS, sensors)
- Performance testing
- Third-party SDK integration (Firebase, Google Maps)
- Pixel-perfect screenshot testing

```kotlin
@RunWith(AndroidJUnit4::class)
class ComplexUiTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun swipeToDelete_removesItem() {
        composeTestRule
            .onNodeWithText("Item 1")
            .performTouchInput { swipeLeft() }

        // ✅ Real gesture behavior
        composeTestRule
            .onNodeWithText("Item 1")
            .assertDoesNotExist()
    }
}
```

### Comparison

| Aspect | Robolectric | Instrumented |
|--------|-------------|--------------|
| Speed | Fast (1-10s) | Slow (10-60s+) |
| Device | Not required | Required |
| CI/CD | Easy | Needs emulator |
| Reliability | Stable | Can be flaky |
| Reality | Simulated | Real Android |
| Hardware | Mocked | Real sensors |

### Testing Pyramid

Recommended distribution:
- **70%** - Unit tests (pure JVM)
- **20%** - Integration (Robolectric)
- **10%** - E2E (Instrumented)

```kotlin
// 70% - Unit tests
class CalculatorTest {
    @Test
    fun add_returnsSum() {
        assertEquals(5, Calculator().add(2, 3))
    }
}

// 20% - Robolectric
@RunWith(RobolectricTestRunner::class)
class ViewModelIntegrationTest {
    @Test
    fun loadData_updatesState() = runTest {
        // ✅ Integration with Android
    }
}

// 10% - Instrumented E2E
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {
    @Test
    fun login_navigatesToHome() {
        // ✅ Full user journey
    }
}
```

### Best Practices

1. **Start with unit tests** for business logic
2. **Use Robolectric** for integration tests with Android
3. **Reserve instrumented** for critical scenarios
4. **Combine approaches** for optimal coverage

**Hybrid approach:**

```kotlin
// Robolectric: business logic + simple UI
@RunWith(RobolectricTestRunner::class)
class UserProfileFragmentTest {
    @Test
    fun loadProfile_displaysInfo() {
        val fragment = launchFragment<UserProfileFragment>()
        // ✅ Fast verification
    }
}

// Instrumented: critical scenarios
@RunWith(AndroidJUnit4::class)
class UserProfileE2ETest {
    @Test
    fun editProfile_syncsToBackend() {
        // ✅ Full integration
    }
}
```

---

## Follow-ups

- How do you set up CI/CD pipelines to run both test types efficiently?
- What strategies help reduce flakiness in instrumented tests?
- How do you mock external dependencies in Robolectric tests?
- When should you use Fakes vs Mocks in Android testing?
- How do you handle Compose testing in Robolectric vs instrumented tests?

## References

- [[c-testing-pyramid]]
- [[c-test-doubles]]
- https://robolectric.org/ - Robolectric documentation
- https://developer.android.com/training/testing/instrumented-tests - Instrumented testing guide
- https://developer.android.com/training/testing/fundamentals - Android testing fundamentals

## Related Questions

### Prerequisites (Easier)
- [[q-unit-testing-basics--android--easy]] - Understanding unit tests
- [[q-fragment-basics--android--easy]] - JUnit framework basics

### Related (Medium)
- [[q-testing-viewmodels-turbine--android--medium]] - Testing ViewModels
- [[q-testing-compose-ui--android--medium]] - Compose UI testing
- [[q-fakes-vs-mocks-testing--android--medium]] - Test doubles
- [[q-screenshot-snapshot-testing--android--medium]] - Screenshot testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Testing async code
- [[q-test-flakiness-strategies--android--hard]] - Reducing flakiness
