---
id: 20251006-100004
title: "How to implement pagination in RecyclerView using RxJava? / Как реализовать пагинацию в RecyclerView с помощью RxJava?"
aliases: []

# Classification
topic: android
subtopics: [rxjava, recyclerview, pagination, infinite-scroll]
question_kind: pattern
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: [recyclerview, rxjava, pagination, paging-library]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android, rxjava, recyclerview, pagination, infinite-scroll, difficulty/medium]
---
# Question (EN)
> How do you implement pagination/infinite scrolling in RecyclerView using RxJava?
# Вопрос (RU)
> Как реализовать пагинацию/бесконечную прокрутку в RecyclerView с помощью RxJava?

---

## Answer (EN)

Implementing pagination with RxJava in RecyclerView involves combining RxJava operators with RecyclerView scroll listeners to load data incrementally as the user scrolls.

**Note**: For modern Android development, consider using **Paging 3 library** with Kotlin Flow instead. This example shows the RxJava approach for legacy projects.

### 1. Basic Pagination with RxJava

```kotlin
import io.reactivex.rxjava3.core.Observable
import io.reactivex.rxjava3.subjects.PublishSubject
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class PaginatedListViewModel {
    private val pageSubject = PublishSubject.create<Int>()
    private var currentPage = 1
    private val pageSize = 20

    val items: Observable<List<Item>> = pageSubject
        .startWith(1) // Load first page
        .flatMap { page ->
            apiService.getItems(page, pageSize)
                .toObservable()
                .onErrorReturn { emptyList() }
        }
        .scan(mutableListOf<Item>()) { accumulated, newItems ->
            accumulated.apply { addAll(newItems) }
        }
        .share()

    fun loadNextPage() {
        currentPage++
        pageSubject.onNext(currentPage)
    }
}

class PaginationScrollListener(
    private val layoutManager: LinearLayoutManager,
    private val onLoadMore: () -> Unit
) : RecyclerView.OnScrollListener() {

    private var isLoading = false
    private var isLastPage = false

    override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
        super.onScrolled(recyclerView, dx, dy)

        if (dy <= 0) return // Not scrolling down

        val visibleItemCount = layoutManager.childCount
        val totalItemCount = layoutManager.itemCount
        val firstVisibleItemPosition = layoutManager.findFirstVisibleItemPosition()

        if (!isLoading && !isLastPage) {
            if ((visibleItemCount + firstVisibleItemPosition) >= totalItemCount
                && firstVisibleItemPosition >= 0
            ) {
                onLoadMore()
            }
        }
    }

    fun setLoading(loading: Boolean) {
        isLoading = loading
    }

    fun setLastPage(lastPage: Boolean) {
        isLastPage = lastPage
    }
}
```

### 2. Complete Implementation with States

```kotlin
sealed class PaginationState {
    object Idle : PaginationState()
    object Loading : PaginationState()
    object LoadingMore : PaginationState()
    data class Success(val items: List<Item>, val hasMore: Boolean) : PaginationState()
    data class Error(val message: String) : PaginationState()
}

class PaginationRepository @Inject constructor(
    private val apiService: ApiService
) {
    private val pageSubject = BehaviorSubject.createDefault(1)
    private val allItems = mutableListOf<Item>()

    fun observePaginatedData(): Observable<PaginationState> {
        return pageSubject
            .flatMap { page ->
                apiService.getItems(page, PAGE_SIZE)
                    .toObservable()
                    .map { response ->
                        if (page == 1) {
                            allItems.clear()
                        }
                        allItems.addAll(response.items)
                        PaginationState.Success(
                            items = allItems.toList(),
                            hasMore = response.hasMore
                        ) as PaginationState
                    }
                    .startWith(
                        if (page == 1) PaginationState.Loading
                        else PaginationState.LoadingMore
                    )
                    .onErrorReturn { error ->
                        PaginationState.Error(error.message ?: "Unknown error")
                    }
            }
            .distinctUntilChanged()
    }

    fun loadMore() {
        val currentPage = pageSubject.value ?: 1
        pageSubject.onNext(currentPage + 1)
    }

    fun refresh() {
        allItems.clear()
        pageSubject.onNext(1)
    }

    companion object {
        private const val PAGE_SIZE = 20
    }
}
```

### 3. ViewModel Integration

```kotlin
class ItemListViewModel @Inject constructor(
    private val repository: PaginationRepository
) : ViewModel() {

    private val compositeDisposable = CompositeDisposable()

    private val _uiState = MutableLiveData<PaginationState>(PaginationState.Idle)
    val uiState: LiveData<PaginationState> = _uiState

    init {
        loadItems()
    }

    fun loadItems() {
        repository.observePaginatedData()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe { state ->
                _uiState.value = state
            }
            .addTo(compositeDisposable)
    }

    fun loadMore() {
        val currentState = _uiState.value
        if (currentState is PaginationState.Success && currentState.hasMore) {
            repository.loadMore()
        }
    }

    fun refresh() {
        repository.refresh()
    }

    override fun onCleared() {
        super.onCleared()
        compositeDisposable.clear()
    }
}
```

### 4. RecyclerView Adapter with Loading Footer

```kotlin
class PaginatedAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    private val items = mutableListOf<Item>()
    private var isLoadingMore = false

    fun setItems(newItems: List<Item>) {
        val oldSize = items.size
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    fun showLoadingFooter(show: Boolean) {
        if (isLoadingMore == show) return

        isLoadingMore = show
        if (show) {
            notifyItemInserted(items.size)
        } else {
            notifyItemRemoved(items.size)
        }
    }

    override fun getItemCount(): Int {
        return items.size + if (isLoadingMore) 1 else 0
    }

    override fun getItemViewType(position: Int): Int {
        return if (position == items.size) VIEW_TYPE_LOADING else VIEW_TYPE_ITEM
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            VIEW_TYPE_ITEM -> ItemViewHolder(
                ItemBinding.inflate(LayoutInflater.from(parent.context), parent, false)
            )
            VIEW_TYPE_LOADING -> LoadingViewHolder(
                LoadingBinding.inflate(LayoutInflater.from(parent.context), parent, false)
            )
            else -> throw IllegalArgumentException("Unknown view type: $viewType")
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (holder) {
            is ItemViewHolder -> holder.bind(items[position])
            is LoadingViewHolder -> {
                // Loading indicator is shown automatically
            }
        }
    }

    companion object {
        private const val VIEW_TYPE_ITEM = 0
        private const val VIEW_TYPE_LOADING = 1
    }
}
```

### 5. Fragment/Activity Integration

```kotlin
class ItemListFragment : Fragment() {

    private val viewModel: ItemListViewModel by viewModels()
    private lateinit var adapter: PaginatedAdapter
    private lateinit var scrollListener: PaginationScrollListener

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        observeViewModel()
    }

    private fun setupRecyclerView() {
        adapter = PaginatedAdapter()
        val layoutManager = LinearLayoutManager(requireContext())

        binding.recyclerView.apply {
            this.layoutManager = layoutManager
            this.adapter = this@ItemListFragment.adapter
        }

        scrollListener = PaginationScrollListener(layoutManager) {
            viewModel.loadMore()
        }

        binding.recyclerView.addOnScrollListener(scrollListener)

        // Pull to refresh
        binding.swipeRefresh.setOnRefreshListener {
            viewModel.refresh()
        }
    }

    private fun observeViewModel() {
        viewModel.uiState.observe(viewLifecycleOwner) { state ->
            binding.swipeRefresh.isRefreshing = false

            when (state) {
                is PaginationState.Loading -> {
                    binding.progressBar.isVisible = true
                    adapter.showLoadingFooter(false)
                    scrollListener.setLoading(true)
                }
                is PaginationState.LoadingMore -> {
                    adapter.showLoadingFooter(true)
                    scrollListener.setLoading(true)
                }
                is PaginationState.Success -> {
                    binding.progressBar.isVisible = false
                    adapter.setItems(state.items)
                    adapter.showLoadingFooter(false)
                    scrollListener.setLoading(false)
                    scrollListener.setLastPage(!state.hasMore)
                }
                is PaginationState.Error -> {
                    binding.progressBar.isVisible = false
                    adapter.showLoadingFooter(false)
                    scrollListener.setLoading(false)
                    Toast.makeText(context, state.message, Toast.LENGTH_SHORT).show()
                }
                else -> {}
            }
        }
    }
}
```

### 6. Advanced: Retry Failed Page Loads

```kotlin
class RetryablePaginationRepository @Inject constructor(
    private val apiService: ApiService
) {
    private val pageSubject = BehaviorSubject.createDefault(1)
    private val retrySubject = PublishSubject.create<Unit>()

    fun observePaginatedData(): Observable<PaginationState> {
        return Observable.merge(
            pageSubject.map { it to false },
            retrySubject.map { (pageSubject.value ?: 1) to true }
        )
            .flatMap { (page, isRetry) ->
                apiService.getItems(page, PAGE_SIZE)
                    .toObservable()
                    .retryWhen { errors ->
                        errors.flatMap { error ->
                            if (isNetworkError(error)) {
                                Observable.timer(2, TimeUnit.SECONDS)
                            } else {
                                Observable.error(error)
                            }
                        }
                    }
                    .map { response ->
                        PaginationState.Success(
                            items = response.items,
                            hasMore = response.hasMore
                        ) as PaginationState
                    }
                    .startWith(PaginationState.LoadingMore)
                    .onErrorReturn { error ->
                        PaginationState.Error(error.message ?: "Unknown error")
                    }
            }
    }

    fun retryLastPage() {
        retrySubject.onNext(Unit)
    }

    private fun isNetworkError(error: Throwable): Boolean {
        return error is IOException
    }
}
```

### 7. Best Practices

#### - DO:

```kotlin
// Use proper dispose management
override fun onCleared() {
    compositeDisposable.clear()
}

// Handle loading states
when (state) {
    is Loading -> showProgress()
    is LoadingMore -> showFooterProgress()
    is Success -> updateList(state.items)
}

// Implement pull-to-refresh
swipeRefresh.setOnRefreshListener {
    viewModel.refresh()
}

// Add empty state
if (items.isEmpty() && !isLoading) {
    showEmptyState()
}
```

#### - DON'T:

```kotlin
// Don't forget to dispose
// Missing compositeDisposable.clear() → Memory leak

// Don't load more when already loading
fun loadMore() {
    repository.loadMore() // Should check if already loading
}

// Don't ignore pagination metadata
// Missing hasMore check → Infinite failed requests

// Don't use nested subscriptions
repository.getData()
    .subscribe { result ->
        repository.getMore() // DON'T DO THIS
            .subscribe { }
    }
```

### 8. Modern Alternative: Paging 3 with Flow

```kotlin
// For new projects, use Paging 3 instead
class ItemPagingSource : PagingSource<Int, Item>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Item> {
        val page = params.key ?: 1
        return try {
            val response = apiService.getItems(page, params.loadSize)
            LoadResult.Page(
                data = response.items,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (response.hasMore) page + 1 else null
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }
}
```

---

## Ответ (RU)

Реализация пагинации с RxJava в RecyclerView включает комбинацию операторов RxJava со слушателями прокрутки RecyclerView.

**Примечание**: Для современной разработки рекомендуется использовать **Paging 3 library** с Kotlin Flow.

### Базовая реализация

```kotlin
val items: Observable<List<Item>> = pageSubject
    .startWith(1)
    .flatMap { page ->
        apiService.getItems(page, pageSize)
            .toObservable()
    }
    .scan(mutableListOf<Item>()) { accumulated, newItems ->
        accumulated.apply { addAll(newItems) }
    }
```

### Слушатель прокрутки

```kotlin
class PaginationScrollListener(
    private val layoutManager: LinearLayoutManager,
    private val onLoadMore: () -> Unit
) : RecyclerView.OnScrollListener() {
    override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
        if ((visibleItemCount + firstVisibleItemPosition) >= totalItemCount) {
            onLoadMore()
        }
    }
}
```

### Лучшие практики

#### - ДЕЛАЙТЕ:

- Управляйте подписками через CompositeDisposable
- Обрабатывайте состояния загрузки
- Реализуйте pull-to-refresh
- Добавляйте индикаторы загрузки

#### - НЕ ДЕЛАЙТЕ:

- Не забывайте dispose подписки
- Не загружайте когда уже идет загрузка
- Не игнорируйте метаданные пагинации

---

## Related Questions
- What is Paging 3 library?
- How to implement pagination with Flow?
- What is RxJava scan operator?
- How to handle RecyclerView scroll events?

## References
- [RxJava Documentation](https://github.com/ReactiveX/RxJava)
- [Paging 3 Library](https://developer.android.com/topic/libraries/architecture/paging/v3-overview)
