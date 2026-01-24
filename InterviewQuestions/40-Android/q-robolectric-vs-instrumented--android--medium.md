---
id: android-323
anki_cards:
- slug: android-323-0-en
  language: en
  anki_id: 1768420266214
  synced_at: '2026-01-23T16:45:06.138109'
- slug: android-323-0-ru
  language: ru
  anki_id: 1768420266240
  synced_at: '2026-01-23T16:45:06.139076'
title: Robolectric Vs Instrumented / Robolectric против Instrumented
aliases:
- Robolectric Vs Instrumented
- Robolectric против Instrumented
topic: android
subtopics:
- testing-instrumented
- testing-unit
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
sources:
- https://developer.android.com/training/testing/fundamentals
- https://developer.android.com/training/testing/instrumented-tests
- https://robolectric.org/
status: draft
moc: moc-android
related:
- c-android
- q-testing-compose-ui--android--medium
- q-testing-viewmodels-turbine--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/testing-instrumented
- android/testing-unit
- comparison
- difficulty/medium
- robolectric
- strategy
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
- Симулирует части Android Framework на JVM
- Быстрые (обычно ощутимо быстрее инструментальных)
- Не требуют устройство или эмулятор
- Легко интегрируются в CI/CD
- Могут иметь тонкие отличия от поведения на реальном устройстве

**Инструментальные тесты** (реальные устройства):
- Выполняются на настоящем Android (эмулятор или реальное устройство)
- Медленнее из-за запуска приложения, среды и взаимодействия с устройством
- Тестируют реальное поведение устройства и фреймворка
- Требуют эмулятор/устройство
- Могут быть нестабильными (flaky) из-за окружения, производительности и асинхронности

### Когда Использовать Robolectric

**Подходит для:**
- Тестирование `ViewModel` или другой логики с Android-зависимостями (`Context`, Resources и т.п.)
- Проверка жизненного цикла `Activity`/`Fragment` на JVM
- Тестирование Resources, `Context`, `SharedPreferences`
- Создание `Intent` и навигации на уровне компонентов
- Быстрая обратная связь в CI

```kotlin
@RunWith(RobolectricTestRunner::class)
class UserViewModelTest {
    @Test
    fun loadUser_updatesState() = runTest {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val viewModel = UserViewModel(context)

        viewModel.loadUser(1)

        // Быстрая проверка состояния
        assertTrue(viewModel.uiState.value is UiState.Success)
    }
}
```

### Когда Использовать Инструментальные Тесты

**Подходит для:**
- Сложные UI-взаимодействия (swipe, drag, animations)
- Работа с hardware (камера, GPS, сенсоры)
- Тестирование производительности и поведения под нагрузкой
- Интеграция с SDK третьих сторон (Firebase, Google Maps и т.п.)
- Pixel-perfect скриншотные тесты

```kotlin
@RunWith(AndroidJUnit4::class)
class ComplexUiTest {
    @get:Rule
    val composeTestRule = createAndroidComposeRule<YourActivity>()

    @Test
    fun swipeToDelete_removesItem() {
        composeTestRule
            .onNodeWithText("Item 1")
            .performTouchInput { swipeLeft() }

        // Реальное поведение жестов
        composeTestRule
            .onNodeWithText("Item 1")
            .assertDoesNotExist()
    }
}
```

### Сравнение

| Аспект | Robolectric | Инструментальные |
|--------|-------------|------------------|
| Скорость | Быстрее, JVM | Медленнее, запуск на устройстве |
| Устройство | Не требуется | Требуется |
| CI/CD | Проще запускать | Нужен эмулятор/устройство |
| Надежность | Более стабильные (предсказуемая JVM-среда) | Могут быть flaky |
| Реальность | Симуляция фреймворка | Настоящий Android стек |
| Hardware | Обычно через mock/fake | Реальные сенсоры и сервисы |

### Пирамида Тестирования

Рекомендуемый ориентир (может варьироваться по проекту):
- 70% - Unit-тесты (чистый JVM)
- ~20% - Интеграционные (в т.ч. с Robolectric или аналогами)
- ~10% - E2E (инструментальные / UI)

```kotlin
// 70% - Unit-тесты
class CalculatorTest {
    @Test
    fun add_returnsSum() {
        assertEquals(5, Calculator().add(2, 3))
    }
}

// ~20% - Интеграционные с Robolectric
@RunWith(RobolectricTestRunner::class)
class ViewModelIntegrationTest {
    @Test
    fun loadData_updatesState() = runTest {
        // Проверка интеграции с Android-зависимостями на JVM
    }
}

// ~10% - Инструментальные E2E
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {
    @Test
    fun login_navigatesToHome() {
        // Полный путь пользователя
    }
}
```

### Лучшие Практики

1. Начинайте с unit-тестов для бизнес-логики.
2. Используйте Robolectric (при необходимости) для интеграционных тестов с Android API без запуска на устройстве.
3. Оставьте инструментальные тесты для критических, UI-интенсивных и средозависимых сценариев.
4. Комбинируйте подходы для оптимального покрытия и времени прогона.

**Гибридный подход:**

```kotlin
// Robolectric: бизнес-логика + простой UI/жизненный цикл
@RunWith(RobolectricTestRunner::class)
class UserProfileFragmentTest {
    @Test
    fun loadProfile_displaysInfo() {
        val fragment = launchFragment<UserProfileFragment>()
        // Быстрая проверка
    }
}

// Инструментальные: критические end-to-end сценарии
@RunWith(AndroidJUnit4::class)
class UserProfileE2ETest {
    @Test
    fun editProfile_syncsToBackend() {
        // Полная интеграция
    }
}
```

---

## Answer (EN)

**Robolectric** runs Android tests on the JVM without a device/emulator, while **Instrumented tests** run on actual Android devices (emulator or physical). Each has distinct advantages and tradeoffs.

### Key Differences

**Robolectric** (JVM tests):
- Simulates parts of the Android Framework on the JVM
- Fast (typically much faster than instrumented tests)
- No device/emulator needed
- Easy CI/CD integration
- May have subtle differences from real device behavior

**Instrumented tests** (real devices):
- Run on real Android (emulator or device)
- Slower due to full app/runtime startup and device interaction
- Test real framework and device behavior
- Require emulator/device
- Can be flaky due to environment, performance, and async behavior

### When to Use Robolectric

**Good for:**
- Testing ViewModels or other logic that depends on Android APIs (`Context`, Resources, etc.)
- Verifying `Activity`/`Fragment` lifecycle behavior on the JVM
- Testing Resources, `Context`, `SharedPreferences`
- `Intent` creation and component-level navigation
- Fast feedback in CI

```kotlin
@RunWith(RobolectricTestRunner::class)
class UserViewModelTest {
    @Test
    fun loadUser_updatesState() = runTest {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val viewModel = UserViewModel(context)

        viewModel.loadUser(1)

        // Fast state verification
        assertTrue(viewModel.uiState.value is UiState.Success)
    }
}
```

### When to Use Instrumented Tests

**Good for:**
- Complex UI interactions (swipe, drag, animations)
- Hardware integration (camera, GPS, sensors)
- Performance and load-related behavior
- Third-party SDK integration (Firebase, Google Maps, etc.)
- Pixel-perfect screenshot tests

```kotlin
@RunWith(AndroidJUnit4::class)
class ComplexUiTest {
    @get:Rule
    val composeTestRule = createAndroidComposeRule<YourActivity>()

    @Test
    fun swipeToDelete_removesItem() {
        composeTestRule
            .onNodeWithText("Item 1")
            .performTouchInput { swipeLeft() }

        // Real gesture behavior
        composeTestRule
            .onNodeWithText("Item 1")
            .assertDoesNotExist()
    }
}
```

### Comparison

| Aspect | Robolectric | Instrumented |
|--------|-------------|--------------|
| Speed | Faster, JVM | Slower, runs on device |
| Device | Not required | Required |
| CI/CD | Easier to run | Needs emulator/device |
| Reliability | More stable (predictable JVM) | Can be flaky |
| Reality | Simulated framework | Real Android stack |
| Hardware | Typically mocked/faked | Real sensors/services |

### Testing Pyramid

Recommended guideline (varies by team/system):
- 70% - Unit tests (pure JVM)
- ~20% - Integration tests (including Robolectric or similar)
- ~10% - E2E/UI (instrumented)

```kotlin
// 70% - Unit tests
class CalculatorTest {
    @Test
    fun add_returnsSum() {
        assertEquals(5, Calculator().add(2, 3))
    }
}

// ~20% - Integration with Robolectric
@RunWith(RobolectricTestRunner::class)
class ViewModelIntegrationTest {
    @Test
    fun loadData_updatesState() = runTest {
        // Integration with Android-dependent components on JVM
    }
}

// ~10% - Instrumented E2E
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {
    @Test
    fun login_navigatesToHome() {
        // Full user journey
    }
}
```

### Best Practices

1. Start with unit tests for business logic.
2. Use Robolectric (when beneficial) for integration tests that need Android APIs without device costs.
3. Reserve instrumented tests for critical, UI-heavy, and environment-sensitive scenarios.
4. Combine approaches to balance coverage and execution time.

**Hybrid approach:**

```kotlin
// Robolectric: business logic + simple UI / lifecycle
@RunWith(RobolectricTestRunner::class)
class UserProfileFragmentTest {
    @Test
    fun loadProfile_displaysInfo() {
        val fragment = launchFragment<UserProfileFragment>()
        // Fast verification
    }
}

// Instrumented: critical end-to-end scenarios
@RunWith(AndroidJUnit4::class)
class UserProfileE2ETest {
    @Test
    fun editProfile_syncsToBackend() {
        // Full integration
    }
}
```

---

## Дополнительные Вопросы (RU)

- Как настроить CI/CD, чтобы эффективно запускать оба типа тестов?
- Какие стратегии помогают уменьшить нестабильность (flakiness) инструментальных тестов?
- Как мокать внешние зависимости в тестах Robolectric?
- Когда в Android-тестировании использовать Fakes против Mocks?
- Как подходить к тестированию Compose в Robolectric и инструментальных тестах?

## Follow-ups

- How do you set up CI/CD pipelines to run both test types efficiently?
- What strategies help reduce flakiness in instrumented tests?
- How do you mock external dependencies in Robolectric tests?
- When should you use Fakes vs Mocks in Android testing?
- How do you handle Compose testing in Robolectric vs instrumented tests?

## Ссылки (RU)

- [[c-android]]
- https://robolectric.org/ - Документация Robolectric
- https://developer.android.com/training/testing/instrumented-tests - Руководство по инструментальным тестам
- https://developer.android.com/training/testing/fundamentals - Основы тестирования Android

## References

- [[c-android]]
- https://robolectric.org/ - Robolectric documentation
- https://developer.android.com/training/testing/instrumented-tests - Instrumented testing guide
- https://developer.android.com/training/testing/fundamentals - Android testing fundamentals

## Связанные Вопросы (RU)

### База (проще)
- [[q-testing-viewmodels-turbine--android--medium]] - Тестирование `ViewModel`
- [[q-testing-compose-ui--android--medium]] - Тестирование Compose UI

### Смежные (Medium)
- [[q-fakes-vs-mocks-testing--android--medium]] - Test doubles
- [[q-screenshot-snapshot-testing--android--medium]] - Скриншотное тестирование

### Продвинутые (сложнее)
- [[q-testing-coroutines-flow--android--hard]] - Тестирование асинхронного кода

## Related Questions

### Prerequisites (Easier)
- [[q-testing-viewmodels-turbine--android--medium]] - Testing ViewModels
- [[q-testing-compose-ui--android--medium]] - Compose UI testing

### Related (Medium)
- [[q-fakes-vs-mocks-testing--android--medium]] - Test doubles
- [[q-screenshot-snapshot-testing--android--medium]] - Screenshot testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--android--hard]] - Testing async code
