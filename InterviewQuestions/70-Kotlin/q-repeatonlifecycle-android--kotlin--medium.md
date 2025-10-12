---
id: 20251012-140014
title: "repeatOnLifecycle in Android / repeatOnLifecycle в Android"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, android, lifecycle, repeatonlifecycle, flow]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Android repeatOnLifecycle Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-lifecyclescope-viewmodelscope--kotlin--medium, q-stateflow-sharedflow-android--kotlin--medium, q-lifecycle-aware-coroutines--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, coroutines, android, lifecycle, repeatonlifecycle, flow, difficulty/medium]
---
# Question (EN)
> What is repeatOnLifecycle and why is it important? Explain how it prevents memory leaks when collecting Flows, comparison with launchWhenStarted, and best practices.

# Вопрос (RU)
> Что такое repeatOnLifecycle и почему это важно? Объясните как он предотвращает утечки памяти при подписке на Flow, сравнение с launchWhenStarted и лучшие практики.

---

## Answer (EN)

`repeatOnLifecycle` is a lifecycle-aware API that automatically starts and cancels coroutines based on lifecycle state, preventing memory leaks when collecting Flows in Android.

### The Problem: Memory Leaks with Flows

```kotlin
// ❌ BAD: Potential memory leak
class BadFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                // Keeps collecting even when Fragment is in background!
                // Memory leak - UI updates while not visible
                updateUI(state)
            }
        }
    }
    
    private fun updateUI(state: String) {
        // Potential crash if view is destroyed
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

### Solution: repeatOnLifecycle

```kotlin
// ✅ GOOD: Safe Flow collection
class GoodFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    // Only collects when STARTED or RESUMED
                    // Automatically cancels when STOPPED
                    updateUI(state)
                }
            }
        }
    }
    
    private fun updateUI(state: String) {}
    
    class MyViewModel : ViewModel() {
        val uiState = flow {
            while (true) {
                emit("state-${System.currentTimeMillis()}")
                delay(1000)
            }
        }
    }
}
```

### How repeatOnLifecycle Works

```kotlin
/**
 * repeatOnLifecycle behavior:
 * 
 * 1. When lifecycle reaches target state (e.g., STARTED):
 *    - Launches block
 *    - Starts collecting
 * 
 * 2. When lifecycle goes below target state:
 *    - Cancels block
 *    - Stops collecting
 * 
 * 3. When lifecycle returns to target state:
 *    - Launches block again
 *    - Restarts collecting
 * 
 * Lifecycle states:
 * INITIALIZED → CREATED → STARTED → RESUMED
 *                  ↓         ↓         ↓
 *              DESTROYED ← STARTED ← RESUMED
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
        
        // Log output:
        // onStart → "Block started"
        // onStop → "Block cancelled"
        // onStart → "Block started"
        // onStop → "Block cancelled"
    }
}
```

### Comparison: repeatOnLifecycle vs launchWhenStarted

```kotlin
class ComparisonExample : Fragment() {
    private val viewModel: FlowViewModel by viewModels()
    
    // ❌ launchWhenStarted (DEPRECATED)
    fun withLaunchWhenStarted() {
        viewLifecycleOwner.lifecycleScope.launchWhenStarted {
            viewModel.dataFlow.collect { data ->
                // PROBLEM: Suspends when STOPPED, doesn't cancel
                // Flow producer keeps running
                // Memory leak!
                updateUI(data)
            }
        }
    }
    
    // ✅ repeatOnLifecycle (RECOMMENDED)
    fun withRepeatOnLifecycle() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.dataFlow.collect { data ->
                    // Fully cancelled when STOPPED
                    // Flow producer stops
                    // No leak!
                    updateUI(data)
                }
            }
        }
    }
    
    private fun updateUI(data: String) {}
    
    class FlowViewModel : ViewModel() {
        val dataFlow = flow {
            var i = 0
            while (true) {
                println("Emitting $i")
                emit("Data ${i++}")
                delay(1000)
            }
        }
    }
}

/**
 * launchWhenStarted output:
 * onStart → Emitting 0, 1, 2...
 * onStop → Still emitting! 10, 11, 12... (LEAK)
 * onStart → Receives buffered values
 * 
 * repeatOnLifecycle output:
 * onStart → Emitting 0, 1, 2...
 * onStop → Emission stopped (GOOD)
 * onStart → Emission starts fresh from 0
 */
```

### Multiple Flow Collections

```kotlin
class MultipleFlowsExample : Fragment() {
    private val viewModel: MultiViewModel by viewModels()
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Collect multiple flows in parallel
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
    
    // ✅ Use STARTED for UI updates
    class UIUpdateFragment : Fragment() {
        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            viewLifecycleOwner.lifecycleScope.launch {
                repeatOnLifecycle(Lifecycle.State.STARTED) {
                    // UI is visible, safe to update
                }
            }
        }
    }
    
    // ✅ Use CREATED for data that survives backgrounding
    class DataFragment : Fragment() {
        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            viewLifecycleOwner.lifecycleScope.launch {
                repeatOnLifecycle(Lifecycle.State.CREATED) {
                    // Keeps running when app is backgrounded
                }
            }
        }
    }
    
    // ✅ Use viewLifecycleOwner in Fragments
    class CorrectLifecycleOwner : Fragment() {
        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            // GOOD: viewLifecycleOwner
            viewLifecycleOwner.lifecycleScope.launch {
                viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                    // Cancelled when view is destroyed
                }
            }
            
            // BAD: this (Fragment lifecycle)
            lifecycleScope.launch {
                repeatOnLifecycle(Lifecycle.State.STARTED) {
                    // Survives view destruction - potential crash!
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
            try {
                saveToCart(_product.value!!)
                _events.emit(Event.AddedToCart)
            } catch (e: Exception) {
                _events.emit(Event.ShowError(e.message ?: "Error"))
            }
        }
    }
    
    private suspend fun fetchProduct(id: Int): Product {
        delay(500)
        return Product(id, "Product $id", 99.99)
    }
    
    private suspend fun fetchRelatedProducts(id: Int): List<Product> {
        delay(500)
        return List(5) { Product(it, "Related $it", 49.99) }
    }
    
    private suspend fun saveToCart(product: Product) {
        delay(200)
    }
}

// Fragment
class ProductDetailFragment : Fragment() {
    private val viewModel: ProductDetailViewModel by viewModels()
    
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
    
    private val productId = 1
    private fun displayProduct(product: ProductDetailViewModel.Product) {}
    private fun displayRelatedProducts(products: List<ProductDetailViewModel.Product>) {}
    private fun showError(message: String) {}
    private fun showSuccessMessage() {}
}
```

---

## Ответ (RU)

`repeatOnLifecycle` - API для безопасной подписки на Flow с учетом жизненного цикла Android.

### Проблема

Обычная подписка на Flow продолжает работать даже когда Fragment/Activity не виден, что приводит к:
- Утечкам памяти
- Ненужной работе в фоне
- Потенциальным крашам

### Решение

```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        flow.collect { /* Безопасно */ }
    }
}
```

### Преимущества

- Автоматическая отмена при onStop
- Автоматический перезапуск при onStart
- Предотвращение утечек памяти
- Безопасное обновление UI

---

## Follow-ups

1. **When to use STARTED vs CREATED state?**
2. **How does repeatOnLifecycle differ from launchWhenStarted?**
3. **Can you use repeatOnLifecycle in Activity?**
4. **How to test code using repeatOnLifecycle?**

---

## References

- [repeatOnLifecycle Documentation](https://developer.android.com/topic/libraries/architecture/coroutines#lifecycle-aware)

---

## Related Questions

- [[q-lifecyclescope-viewmodelscope--kotlin--medium]]
- [[q-stateflow-sharedflow-android--kotlin--medium]]
- [[q-lifecycle-aware-coroutines--kotlin--hard]]
