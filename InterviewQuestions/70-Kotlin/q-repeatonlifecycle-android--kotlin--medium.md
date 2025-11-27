---
id: kotlin-118
title: "repeatOnLifecycle in Android / repeatOnLifecycle в Android"
aliases: ["repeatOnLifecycle in Android", "repeatOnLifecycle в Android"]
topic: kotlin
subtopics: [coroutines, flow, lifecycle]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Android repeatOnLifecycle Guide
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-lifecycle-aware-coroutines--kotlin--hard, q-lifecyclescope-viewmodelscope--kotlin--medium]
created: 2025-10-12
updated: 2025-11-09
tags: [android, coroutines, difficulty/medium, flow, kotlin, lifecycle, repeatonlifecycle]

date created: Sunday, October 12th 2025, 3:39:19 pm
date modified: Tuesday, November 25th 2025, 8:53:49 pm
---
# Вопрос (RU)
> Что такое `repeatOnLifecycle` и почему это важно? Объясните как он предотвращает утечки памяти при подписке на `Flow`, сравнение с `launchWhenStarted` и лучшие практики.

## Question (EN)
> What is `repeatOnLifecycle` and why is it important? Explain how it prevents memory leaks when collecting `Flow`s, comparison with `launchWhenStarted`, and best practices.

---

## Ответ (RU)

`repeatOnLifecycle` — это lifecycle-aware API из AndroidX Lifecycle (lifecycle-runtime-ktx), которое автоматически запускает и отменяет корутины/подписки на `Flow` в зависимости от состояния жизненного цикла `LifecycleOwner`. Это помогает избежать утечек памяти и обращения к уничтоженным `View` при сборе `Flow` в Android.

### Проблема: Утечки Памяти При Сборе `Flow`

```kotlin
// ПЛОХО: возможна утечка / некорректный доступ к UI
class BadFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                // Коллекция связана с lifecycle `Fragment`,
                // продолжается даже после уничтожения view.
                updateUI(state)
            }
        }
    }

    private fun updateUI(state: String) {
        // Возможен краш, если вызывается после уничтожения view
    }

    class MyViewModel : ViewModel() {
        val uiState = flow {
            while (true) {
                emit("state")
                delay(1000)
            }
        }
    }
}
```

Здесь коллекция привязана к `lifecycleScope` `Fragment`, а не к `viewLifecycleOwner`. В результате сбор может продолжаться после уничтожения `view`, а ссылки на старое дерево `View` могут привести к утечкам и крашам.

### Решение: `repeatOnLifecycle`

```kotlin
// ХОРОШО: безопасный сбор Flow
class GoodFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    // Сбор только в состояниях STARTED или RESUMED
                    // Автоматическая отмена, когда STOPPED
                    updateUI(state)
                }
            }
        }
    }

    private fun updateUI(state: String) {}

    class MyViewModel : ViewModel() {
        val uiState = flow {
            while (true) {
                emit("state-${'$'}{System.currentTimeMillis()}")
                delay(1000)
            }
        }
    }
}
```

Коллекция:
- запускается, когда lifecycle владельца view достигает `STARTED`;
- отменяется при переходе ниже `STARTED`, освобождая ссылки и останавливая связанное с коллекцией вычисление;
- при повторном входе в состояние снова запускается.

### Как Работает `repeatOnLifecycle`

```kotlin
/**
 * Поведение repeatOnLifecycle:
 *
 * 1. Когда lifecycle достигает целевого состояния (например, STARTED):
 *    - запускается переданный блок в новой coroutine scope.
 *
 * 2. Когда lifecycle опускается ниже целевого состояния:
 *    - эта scope отменяется, отменяя дочерние корутины и их коллекции.
 *
 * 3. Когда lifecycle снова достигает целевого состояния:
 *    - блок запускается снова в новой scope.
 *
 * Упрощенный путь жизненного цикла:
 * INITIALIZED → CREATED → STARTED → RESUMED → (обратно через) STARTED → CREATED → DESTROYED
 */

class LifecycleExample : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                println("Block started")
                try {
                    // Ваш код коллекции
                    delay(Long.MAX_VALUE)
                } finally {
                    println("Block cancelled")
                }
            }
        }

        // Пример логов:
        // onStart → "Block started"
        // onStop → "Block cancelled"
        // onStart → "Block started"
        // onStop → "Block cancelled"
    }
}
```

### Сравнение: `repeatOnLifecycle` Vs `launchWhenStarted`

```kotlin
class ComparisonExample : Fragment() {
    private val viewModel: FlowViewModel by viewModels()

    // launchWhenStarted (НЕ РЕКОМЕНДУЕТСЯ для этого кейса)
    fun withLaunchWhenStarted() {
        viewLifecycleOwner.lifecycleScope.launchWhenStarted {
            viewModel.dataFlow.collect { data ->
                // При STOPPED эта корутина приостанавливается, но не полностью отменяется.
                // Если upstream не привязан к этому Job, он может продолжать работу в фоне.
                updateUI(data)
            }
        }
    }

    // repeatOnLifecycle (РЕКОМЕНДУЕТСЯ)
    fun withRepeatOnLifecycle() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.dataFlow.collect { data ->
                    // При уходе ниже STARTED коллекция отменяется.
                    // Upstream, завязанный на этот Job, тоже корректно отменяется.
                    updateUI(data)
                }
            }
        }
    }

    private fun updateUI(data: String) {}

    class FlowViewModel : ViewModel() {
        // Пример холодного Flow для демонстрации поведения отмены
        val dataFlow = flow {
            var i = 0
            while (true) {
                println("Emitting ${'$'}i")
                emit("Data ${'$'}{i++}")
                delay(1000)
            }
        }
    }
}

/**
 * launchWhenStarted:
 * - При STOPPED: корутина приостановлена; upstream, завязанный на этот collector, тоже приостанавливается.
 * - Но работа, не связанная с этим Job, может продолжаться, что делает ошибки менее очевидными.
 *
 * repeatOnLifecycle:
 * - При STOPPED: scope отменяется; корректно построенные холодные потоки и upstream, завязанный на этот Job,
 *   завершаются и будут перезапущены при следующем входе в целевое состояние.
 */
```

Важно: для горячих потоков (`StateFlow`, `SharedFlow`) продюсер обычно живет дольше коллектора и не останавливается при отмене одной корутины. `repeatOnLifecycle` гарантирует безопасную коллекцию и обновление UI в валидных состояниях, но не обязан останавливать глобальный источник.

### Множественный Сбор `Flow`

```kotlin
class MultipleFlowsExample : Fragment() {
    private val viewModel: MultiViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Параллельный сбор нескольких Flow в рамках lifecycle-aware scope
                launch {
                    viewModel.uiState.collect { state ->
                        updateState(state)
                    }
                }

                launch {
                    viewModel.events.collect { event ->
                        handleEvent(event)
                    }
                }

                launch {
                    viewModel.loading.collect { isLoading ->
                        showLoading(isLoading)
                    }
                }
            }
        }
    }

    private fun updateState(state: String) {}
    private fun handleEvent(event: String) {}
    private fun showLoading(isLoading: Boolean) {}

    class MultiViewModel : ViewModel() {
        val uiState = MutableStateFlow("state")
        val events = MutableSharedFlow<String>()
        val loading = MutableStateFlow(false)
    }
}
```

### Лучшие Практики

```kotlin
class BestPractices {

    // Используйте STARTED для обновления UI (view существует и достаточно "видим")
    class UIUpdateFragment : Fragment() {
        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            viewLifecycleOwner.lifecycleScope.launch {
                viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                    // UI видим: безопасно обновлять View
                }
            }
        }
    }

    // Используйте CREATED для задач, которые должны работать, пока владелец существует
    // и находится как минимум в состоянии CREATED; обычно не для привязанных к видимости UI обновлений.
    class DataFragment : Fragment() {
        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            viewLifecycleOwner.lifecycleScope.launch {
                viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.CREATED) {
                    // Работает, пока viewLifecycleOwner как минимум в CREATED,
                    // и останавливается при уничтожении.
                }
            }
        }
    }

    // В `Fragment` для UI-потоков используйте `viewLifecycleOwner`
    class CorrectLifecycleOwner : Fragment() {
        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            // ХОРОШО: привязано к жизненному циклу view
            viewLifecycleOwner.lifecycleScope.launch {
                viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                    // Отменяется при уничтожении view -> нет устаревших ссылок на View
                }
            }

            // ПЛОХО (для UI/Flow, завязанных на View): привязано к lifecycle `Fragment`
            lifecycleScope.launch {
                repeatOnLifecycle(Lifecycle.State.STARTED) {
                    // Переживает уничтожение view; при работе с View возможны утечки/краши.
                    // Использовать `Fragment.lifecycleScope` только для задач, не связанных с View.
                }
            }
        }
    }
}
```

### Реальный Пример

```kotlin
// ViewModel
class ProductDetailViewModel : ViewModel() {
    private val _product = MutableStateFlow<Product?>(null)
    val product: StateFlow<Product?> = _product.asStateFlow()

    private val _relatedProducts = MutableStateFlow<List<Product>>(emptyList())
    val relatedProducts: StateFlow<List<Product>> = _relatedProducts.asStateFlow()

    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    data class Product(val id: Int, val name: String, val price: Double)

    sealed class Event {
        data class ShowError(val message: String) : Event()
        object AddedToCart : Event()
    }

    fun loadProduct(id: Int) {
        viewModelScope.launch {
            // Параллельная загрузка товара и связанных товаров
            launch {
                _product.value = fetchProduct(id)
            }
            launch {
                _relatedProducts.value = fetchRelatedProducts(id)
            }
        }
    }

    fun addToCart() {
        viewModelScope.launch {
            val product = _product.value ?: return@launch
            try {
                saveToCart(product)
                _events.emit(Event.AddedToCart)
            } catch (e: Exception) {
                _events.emit(Event.ShowError(e.message ?: "Error"))
            }
        }
    }

    private suspend fun fetchProduct(id: Int): Product {
        delay(500)
        return Product(id, "Product ${'$'}id", 99.99)
    }

    private suspend fun fetchRelatedProducts(id: Int): List<Product> {
        delay(500)
        return List(5) { index -> Product(index, "Related ${'$'}index", 49.99) }
    }

    private suspend fun saveToCart(product: Product) {
        delay(200)
    }
}

// Fragment
class ProductDetailFragment : Fragment() {
    private val viewModel: ProductDetailViewModel by viewModels()

    private val productId = 1

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Сбор всех потоков с repeatOnLifecycle
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Детали товара
                launch {
                    viewModel.product.collect { product ->
                        product?.let { displayProduct(it) }
                    }
                }

                // Связанные товары
                launch {
                    viewModel.relatedProducts.collect { products ->
                        displayRelatedProducts(products)
                    }
                }

                // Одноразовые события
                launch {
                    viewModel.events.collect { event ->
                        when (event) {
                            is ProductDetailViewModel.Event.ShowError -> {
                                showError(event.message)
                            }
                            is ProductDetailViewModel.Event.AddedToCart -> {
                                showSuccessMessage()
                            }
                        }
                    }
                }
            }
        }

        // Загрузка данных
        viewModel.loadProduct(productId)
    }

    private fun displayProduct(product: ProductDetailViewModel.Product) {}
    private fun displayRelatedProducts(products: List<ProductDetailViewModel.Product>) {}
    private fun showError(message: String) {}
    private fun showSuccessMessage() {}
}
```

Также см. [[c-kotlin]] и [[c-coroutines]] для фундаментальных концепций.

---

## Answer (EN)

`repeatOnLifecycle` is a lifecycle-aware API from AndroidX Lifecycle (lifecycle-runtime-ktx) that automatically starts and cancels coroutines based on the `LifecycleOwner`'s state. It helps prevent leaks and invalid UI access when collecting `Flow`s in Android.

### The Problem: Memory Leaks with `Flow`s

```kotlin
// BAD: Potential leak / invalid UI access
class BadFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                // Collection continues with `Fragment` lifecycle
                // even when the view is destroyed.
                updateUI(state)
            }
        }
    }

    private fun updateUI(state: String) {
        // Potential crash if called after view is destroyed
    }

    class MyViewModel : ViewModel() {
        val uiState = flow {
            while (true) {
                emit("state")
                delay(1000)
            }
        }
    }
}
```

Because this collection is tied to `Fragment.lifecycleScope` instead of the `viewLifecycleOwner`, it may keep collecting after the view is destroyed, and any references to the old view tree can cause leaks or crashes.

### Solution: `repeatOnLifecycle`

```kotlin
// GOOD: Safe Flow collection
class GoodFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    // Only collects when STARTED or RESUMED
                    // Automatically cancelled when STOPPED
                    updateUI(state)
                }
            }
        }
    }

    private fun updateUI(state: String) {}

    class MyViewModel : ViewModel() {
        val uiState = flow {
            while (true) {
                emit("state-${'$'}{System.currentTimeMillis()}")
                delay(1000)
            }
        }
    }
}
```

Here, the collection:
- runs only when the `Fragment`'s view lifecycle is at least `STARTED`;
- is cancelled when the view falls below `STARTED` (e.g., `STOPPED`/`DESTROYED`), releasing references and cancelling upstream work tied to the collector coroutine;
- restarts when the lifecycle returns to the target state.

### How `repeatOnLifecycle` Works

```kotlin
/**
 * repeatOnLifecycle behavior:
 *
 * 1. When lifecycle reaches the target state (e.g., STARTED):
 *    - Launches the provided block in a new coroutine scope.
 *
 * 2. When lifecycle falls below the target state:
 *    - Cancels that scope, which cancels child coroutines and their collections.
 *
 * 3. When lifecycle returns to the target state:
 *    - Launches the block again in a new scope.
 *
 * Lifecycle (simplified forward path):
 * INITIALIZED → CREATED → STARTED → RESUMED → (backwards via) STARTED → CREATED → DESTROYED
 */

class LifecycleExample : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                println("Block started")
                try {
                    // Your collection code
                    delay(Long.MAX_VALUE)
                } finally {
                    println("Block cancelled")
                }
            }
        }

        // Log output example:
        // onStart → "Block started"
        // onStop → "Block cancelled"
        // onStart → "Block started"
        // onStop → "Block cancelled"
    }
}
```

### Comparison: `repeatOnLifecycle` Vs `launchWhenStarted`

```kotlin
class ComparisonExample : Fragment() {
    private val viewModel: FlowViewModel by viewModels()

    // launchWhenStarted (NOT RECOMMENDED for this use case)
    fun withLaunchWhenStarted() {
        viewLifecycleOwner.lifecycleScope.launchWhenStarted {
            viewModel.dataFlow.collect { data ->
                // When STOPPED, this coroutine is suspended, not fully cancelled.
                // If dataFlow's upstream work is not tied to this Job,
                // it may continue producing in the background.
                updateUI(data)
            }
        }
    }

    // repeatOnLifecycle (RECOMMENDED)
    fun withRepeatOnLifecycle() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.dataFlow.collect { data ->
                    // Collection is cancelled when falling below STARTED.
                    // Upstream that depends on this coroutine's Job is cancelled too.
                    updateUI(data)
                }
            }
        }
    }

    private fun updateUI(data: String) {}

    class FlowViewModel : ViewModel() {
        // Cold flow example to illustrate cancellation behavior
        val dataFlow = flow {
            var i = 0
            while (true) {
                println("Emitting ${'$'}i")
                emit("Data ${'$'}{i++}")
                delay(1000)
            }
        }
    }
}

/**
 * With launchWhenStarted:
 * - On STOPPED: collection is suspended; upstream tied directly to this collector is also suspended.
 * - But work not bound to this Job can continue, making issues less obvious.
 *
 * With repeatOnLifecycle:
 * - On STOPPED: the collection scope is cancelled; well-structured cold flows and upstream coroutines
 *   depending on this Job complete and will be restarted on the next entry into the target state.
 */
```

Note: For hot flows (e.g., `StateFlow`, `SharedFlow`), producers typically outlive collectors and are not "stopped" by cancelling a single collector; `repeatOnLifecycle` ensures safe collection and UI updates in valid states, not global producer shutdown.

### Multiple `Flow` Collections

```kotlin
class MultipleFlowsExample : Fragment() {
    private val viewModel: MultiViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Collect multiple flows in parallel within this lifecycle-aware scope
                launch {
                    viewModel.uiState.collect { state ->
                        updateState(state)
                    }
                }

                launch {
                    viewModel.events.collect { event ->
                        handleEvent(event)
                    }
                }

                launch {
                    viewModel.loading.collect { isLoading ->
                        showLoading(isLoading)
                    }
                }
            }
        }
    }

    private fun updateState(state: String) {}
    private fun handleEvent(event: String) {}
    private fun showLoading(isLoading: Boolean) {}

    class MultiViewModel : ViewModel() {
        val uiState = MutableStateFlow("state")
        val events = MutableSharedFlow<String>()
        val loading = MutableStateFlow(false)
    }
}
```

### Best Practices

```kotlin
class BestPractices {

    // Use STARTED for UI updates (view must exist and be visible enough)
    class UIUpdateFragment : Fragment() {
        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            viewLifecycleOwner.lifecycleScope.launch {
                viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                    // UI is visible: safe to update views
                }
            }
        }
    }

    // Use CREATED for work that should run while the owner is at least CREATED
    // and not tied to UI visibility-sensitive updates.
    class DataFragment : Fragment() {
        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            viewLifecycleOwner.lifecycleScope.launch {
                viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.CREATED) {
                    // Runs while viewLifecycleOwner is at least CREATED
                    // and stops when it's destroyed.
                }
            }
        }
    }

    // Use viewLifecycleOwner in Fragments for UI-related flows
    class CorrectLifecycleOwner : Fragment() {
        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            // GOOD: tied to view lifecycle
            viewLifecycleOwner.lifecycleScope.launch {
                viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                    // Cancelled when view is destroyed -> avoids stale view references
                }
            }

            // BAD (for view/UI flows): tied to `Fragment` lifecycle
            lifecycleScope.launch {
                repeatOnLifecycle(Lifecycle.State.STARTED) {
                    // Survives view destruction; if you touch views here,
                    // you risk crashes or leaks. Only use Fragment.lifecycleScope
                    // for work not bound to the view hierarchy.
                }
            }
        }
    }
}
```

### Real-world Example

```kotlin
// ViewModel
class ProductDetailViewModel : ViewModel() {
    private val _product = MutableStateFlow<Product?>(null)
    val product: StateFlow<Product?> = _product.asStateFlow()

    private val _relatedProducts = MutableStateFlow<List<Product>>(emptyList())
    val relatedProducts: StateFlow<List<Product>> = _relatedProducts.asStateFlow()

    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    data class Product(val id: Int, val name: String, val price: Double)

    sealed class Event {
        data class ShowError(val message: String) : Event()
        object AddedToCart : Event()
    }

    fun loadProduct(id: Int) {
        viewModelScope.launch {
            // Load product and related products in parallel
            launch {
                _product.value = fetchProduct(id)
            }
            launch {
                _relatedProducts.value = fetchRelatedProducts(id)
            }
        }
    }

    fun addToCart() {
        viewModelScope.launch {
            val product = _product.value ?: return@launch
            try {
                saveToCart(product)
                _events.emit(Event.AddedToCart)
            } catch (e: Exception) {
                _events.emit(Event.ShowError(e.message ?: "Error"))
            }
        }
    }

    private suspend fun fetchProduct(id: Int): Product {
        delay(500)
        return Product(id, "Product ${'$'}id", 99.99)
    }

    private suspend fun fetchRelatedProducts(id: Int): List<Product> {
        delay(500)
        return List(5) { index -> Product(index, "Related ${'$'}index", 49.99) }
    }

    private suspend fun saveToCart(product: Product) {
        delay(200)
    }
}

// Fragment
class ProductDetailFragment : Fragment() {
    private val viewModel: ProductDetailViewModel by viewModels()

    private val productId = 1

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Collect all flows with repeatOnLifecycle
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Product details
                launch {
                    viewModel.product.collect { product ->
                        product?.let { displayProduct(it) }
                    }
                }

                // Related products
                launch {
                    viewModel.relatedProducts.collect { products ->
                        displayRelatedProducts(products)
                    }
                }

                // One-time events
                launch {
                    viewModel.events.collect { event ->
                        when (event) {
                            is ProductDetailViewModel.Event.ShowError -> {
                                showError(event.message)
                            }
                            is ProductDetailViewModel.Event.AddedToCart -> {
                                showSuccessMessage()
                            }
                        }
                    }
                }
            }
        }

        // Load data
        viewModel.loadProduct(productId)
    }

    private fun displayProduct(product: ProductDetailViewModel.Product) {}
    private fun displayRelatedProducts(products: List<ProductDetailViewModel.Product>) {}
    private fun showError(message: String) {}
    private fun showSuccessMessage() {}
}
```

Also see [[c-kotlin]] and [[c-coroutines]] for foundational concepts.

---

## Related Questions

- [[q-lifecycle-aware-coroutines--kotlin--hard]]
- [[q-lifecyclescope-viewmodelscope--kotlin--medium]]

## References

- Official documentation: "repeatOnLifecycle" in AndroidX Lifecycle KTX (lifecycle-runtime-ktx)
- [[c-kotlin]]
- [[c-coroutines]]

## Follow-ups

1. When should you prefer `Lifecycle.State.STARTED` over `Lifecycle.State.CREATED` when using `repeatOnLifecycle` to collect UI-related `Flow`s, and how does this choice affect when work starts and stops relative to visibility of the `Activity` or `Fragment`?
2. In detail, how do the suspension semantics of `launchWhenStarted` differ from the cancellation-and-relaunch behavior of `repeatOnLifecycle`, and how can this impact upstream `Flow` producers and potential background work leaks?
3. How would you design `repeatOnLifecycle`-based `Flow` collection in an `Activity` that manages multiple UI components (e.g., fragments or custom views) to ensure each stream is cancelled correctly on `onStop` without manual bookkeeping?
4. How should you structure your `ViewModel` `Flow`s (choice of cold vs hot streams, sharing strategies) to align with `repeatOnLifecycle` so that expensive work does not continue unnecessarily when the UI is stopped?
5. What practical techniques (e.g., `TestCoroutineScheduler`, `LifecycleRegistry`, Robolectric or instrumentation hooks) can you use to reliably unit-test and instrumentation-test code paths that depend on `repeatOnLifecycle` lifecycle-aware collection?
