---
topic: android
tags:
  - android
difficulty: medium
---

# How to tell adapter to redraw list if an element was deleted?

## EN (expanded)

When an item is removed from a list, you need to update both the data source and notify the adapter to redraw only the affected items.

### Traditional RecyclerView.Adapter

#### Method 1: Specific Item Notification (Best)

```kotlin
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {
    private val items = mutableListOf<String>()

    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
        // Optional: notify about range change if needed
        notifyItemRangeChanged(position, items.size)
    }

    fun removeItem(item: String) {
        val position = items.indexOf(item)
        if (position != -1) {
            items.removeAt(position)
            notifyItemRemoved(position)
            notifyItemRangeChanged(position, items.size)
        }
    }

    // ... rest of adapter
}
```

#### Method 2: Using DiffUtil (Recommended)

```kotlin
class SmartAdapter : RecyclerView.Adapter<SmartAdapter.ViewHolder>() {
    private var items = listOf<Item>()

    fun updateItems(newItems: List<Item>) {
        val diffCallback = ItemDiffCallback(items, newItems)
        val diffResult = DiffUtil.calculateDiff(diffCallback)

        items = newItems
        diffResult.dispatchUpdatesTo(this)
    }

    fun removeItem(position: Int) {
        val newList = items.toMutableList().apply {
            removeAt(position)
        }
        updateItems(newList)
    }

    class ItemDiffCallback(
        private val oldList: List<Item>,
        private val newList: List<Item>
    ) : DiffUtil.Callback() {
        override fun getOldListSize() = oldList.size
        override fun getNewListSize() = newList.size

        override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean {
            return oldList[oldPos].id == newList[newPos].id
        }

        override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
            return oldList[oldPos] == newList[newPos]
        }
    }

    // ... rest of adapter
}
```

### ListAdapter (Modern Approach - Recommended)

```kotlin
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemComparator) {

    fun removeItem(item: Item) {
        val newList = currentList.toMutableList()
        newList.remove(item)
        submitList(newList)
        // ListAdapter handles everything automatically
    }

    fun removeItem(position: Int) {
        val newList = currentList.toMutableList()
        newList.removeAt(position)
        submitList(newList)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemLayoutBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(private val binding: ItemLayoutBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(item: Item) {
            binding.titleText.text = item.title
            binding.descriptionText.text = item.description
        }
    }

    object ItemComparator : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}
```

### Complete Example with Swipe to Delete

```kotlin
class SwipeToDeleteActivity : AppCompatActivity() {
    private lateinit var adapter: ModernAdapter
    private val items = mutableListOf<Item>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        adapter = ModernAdapter()
        recyclerView.adapter = adapter
        recyclerView.layoutManager = LinearLayoutManager(this)

        // Setup swipe to delete
        val itemTouchHelper = ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(
            0,
            ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
        ) {
            override fun onMove(
                recyclerView: RecyclerView,
                viewHolder: RecyclerView.ViewHolder,
                target: RecyclerView.ViewHolder
            ): Boolean = false

            override fun onSwiped(viewHolder: RecyclerView.ViewHolder, direction: Int) {
                val position = viewHolder.adapterPosition
                val item = adapter.currentList[position]

                // Remove item
                val newList = adapter.currentList.toMutableList()
                newList.removeAt(position)
                adapter.submitList(newList)

                // Show undo snackbar
                Snackbar.make(recyclerView, "Item deleted", Snackbar.LENGTH_LONG)
                    .setAction("Undo") {
                        val restoreList = adapter.currentList.toMutableList()
                        restoreList.add(position, item)
                        adapter.submitList(restoreList)
                    }
                    .show()
            }
        })

        itemTouchHelper.attachToRecyclerView(recyclerView)

        // Load initial data
        loadItems()
    }

    private fun loadItems() {
        // Load your items
        adapter.submitList(items)
    }
}
```

### With Click Listener

```kotlin
class ClickableAdapter(
    private val onDeleteClick: (Item, Int) -> Unit
) : ListAdapter<Item, ClickableAdapter.ViewHolder>(ItemComparator) {

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position), onDeleteClick)
    }

    class ViewHolder(private val binding: ItemLayoutBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(item: Item, onDeleteClick: (Item, Int) -> Unit) {
            binding.apply {
                titleText.text = item.title
                deleteButton.setOnClickListener {
                    onDeleteClick(item, adapterPosition)
                }
            }
        }
    }

    // ... comparator
}

// Usage
val adapter = ClickableAdapter { item, position ->
    val newList = adapter.currentList.toMutableList()
    newList.removeAt(position)
    adapter.submitList(newList)
}
```

### Jetpack Compose (LazyColumn)

In Compose, list updates are automatic:

```kotlin
@Composable
fun ItemList() {
    var items by remember {
        mutableStateOf(listOf(
            Item("1", "Item 1"),
            Item("2", "Item 2"),
            Item("3", "Item 3")
        ))
    }

    LazyColumn {
        items(
            items = items,
            key = { it.id } // Important for animations
        ) { item ->
            ItemRow(
                item = item,
                onDelete = {
                    // Remove item - Compose handles updates automatically
                    items = items.filter { it.id != item.id }
                }
            )
        }
    }
}

@Composable
fun ItemRow(item: Item, onDelete: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(text = item.title)
        IconButton(onClick = onDelete) {
            Icon(Icons.Default.Delete, contentDescription = "Delete")
        }
    }
}
```

### Compose with Animation

```kotlin
@Composable
fun AnimatedItemList() {
    var items by remember { mutableStateOf(getSampleItems()) }

    LazyColumn {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            AnimatedVisibility(
                visible = true,
                exit = slideOutHorizontally() + fadeOut()
            ) {
                ItemRow(
                    item = item,
                    onDelete = {
                        items = items.filter { it.id != item.id }
                    }
                )
            }
        }
    }
}
```

### Best Practices

1. **Use ListAdapter** for new code - it handles DiffUtil automatically
2. **Always use stable keys** - helps with animations and performance
3. **Avoid notifyDataSetChanged()** - it's inefficient
4. **Use specific notifications** - `notifyItemRemoved()`, `notifyItemInserted()`, etc.
5. **Consider undo functionality** - improve UX with Snackbar
6. **Animate deletions** - better visual feedback

### Common Notification Methods

```kotlin
// Item removed
notifyItemRemoved(position)

// Item inserted
notifyItemInserted(position)

// Item changed
notifyItemChanged(position)

// Range changed
notifyItemRangeChanged(positionStart, itemCount)

// Range removed
notifyItemRangeRemoved(positionStart, itemCount)

// Item moved
notifyItemMoved(fromPosition, toPosition)

// Everything changed (avoid!)
notifyDataSetChanged()
```

---

## RU (original)

Как сказать адаптеру перерисовать список, если какой-то элемент удалился

Если удалился элемент из списка, нужно: Удалить его из списка данных. Сообщить Adapter, чтобы он перерисовал только изменённые элементы.
