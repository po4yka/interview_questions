---
tags:
  - recyclerview
  - delegates
  - easy_kotlin
  - android/recyclerview
  - android
  - ui
difficulty: easy
---

# Как организовать работу с текстом и картинками в делегате?

**English**: How to organize work with text and images in a delegate?

## Answer

For managing text and images in RecyclerView, use **delegates** (also known as Adapter Delegates) which separate display logic for different data types. This simplifies code and improves maintainability.

### What are Adapter Delegates?

Adapter Delegates is a pattern that allows you to split complex RecyclerView adapters into smaller, reusable pieces. Each delegate handles a specific item type (e.g., text items, image items, mixed items).

### Basic Implementation

#### 1. Define Data Models

```kotlin
// Base interface for list items
sealed class ListItem

data class TextItem(
    val id: String,
    val title: String,
    val description: String
) : ListItem()

data class ImageItem(
    val id: String,
    val imageUrl: String,
    val caption: String
) : ListItem()

data class TextImageItem(
    val id: String,
    val title: String,
    val imageUrl: String,
    val description: String
) : ListItem()
```

#### 2. Create ViewHolders for Each Type

```kotlin
// ViewHolder for text items
class TextViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    private val titleTextView: TextView = itemView.findViewById(R.id.titleText)
    private val descriptionTextView: TextView = itemView.findViewById(R.id.descriptionText)

    fun bind(item: TextItem) {
        titleTextView.text = item.title
        descriptionTextView.text = item.description
    }
}

// ViewHolder for image items
class ImageViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    private val imageView: ImageView = itemView.findViewById(R.id.image)
    private val captionTextView: TextView = itemView.findViewById(R.id.caption)

    fun bind(item: ImageItem) {
        Glide.with(itemView.context)
            .load(item.imageUrl)
            .into(imageView)
        captionTextView.text = item.caption
    }
}

// ViewHolder for text + image items
class TextImageViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    private val titleTextView: TextView = itemView.findViewById(R.id.title)
    private val imageView: ImageView = itemView.findViewById(R.id.image)
    private val descriptionTextView: TextView = itemView.findViewById(R.id.description)

    fun bind(item: TextImageItem) {
        titleTextView.text = item.title
        descriptionTextView.text = item.description
        Glide.with(itemView.context)
            .load(item.imageUrl)
            .placeholder(R.drawable.placeholder)
            .error(R.drawable.error_image)
            .into(imageView)
    }
}
```

#### 3. Create Adapter with Delegates

```kotlin
class MultiTypeAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    private val items = mutableListOf<ListItem>()

    companion object {
        private const val TYPE_TEXT = 0
        private const val TYPE_IMAGE = 1
        private const val TYPE_TEXT_IMAGE = 2
    }

    override fun getItemViewType(position: Int): Int {
        return when (items[position]) {
            is TextItem -> TYPE_TEXT
            is ImageItem -> TYPE_IMAGE
            is TextImageItem -> TYPE_TEXT_IMAGE
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        val inflater = LayoutInflater.from(parent.context)
        return when (viewType) {
            TYPE_TEXT -> {
                val view = inflater.inflate(R.layout.item_text, parent, false)
                TextViewHolder(view)
            }
            TYPE_IMAGE -> {
                val view = inflater.inflate(R.layout.item_image, parent, false)
                ImageViewHolder(view)
            }
            TYPE_TEXT_IMAGE -> {
                val view = inflater.inflate(R.layout.item_text_image, parent, false)
                TextImageViewHolder(view)
            }
            else -> throw IllegalArgumentException("Unknown view type: $viewType")
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (val item = items[position]) {
            is TextItem -> (holder as TextViewHolder).bind(item)
            is ImageItem -> (holder as ImageViewHolder).bind(item)
            is TextImageItem -> (holder as TextImageViewHolder).bind(item)
        }
    }

    override fun getItemCount() = items.size

    fun submitList(newItems: List<ListItem>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }
}
```

### Using Adapter Delegates Library

For more complex scenarios, use the **AdapterDelegates** library by Hannes Dorfmann:

```kotlin
// build.gradle
dependencies {
    implementation 'com.hannesdorfmann:adapterdelegates4:4.3.2'
}
```

```kotlin
// Text delegate
class TextAdapterDelegate : AdapterDelegate<List<ListItem>>() {

    override fun isForViewType(items: List<ListItem>, position: Int): Boolean {
        return items[position] is TextItem
    }

    override fun onCreateViewHolder(parent: ViewGroup): RecyclerView.ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_text, parent, false)
        return TextViewHolder(view)
    }

    override fun onBindViewHolder(
        items: List<ListItem>,
        position: Int,
        holder: RecyclerView.ViewHolder,
        payloads: List<Any>
    ) {
        val item = items[position] as TextItem
        (holder as TextViewHolder).bind(item)
    }

    class TextViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: TextItem) {
            // Bind text
        }
    }
}

// Image delegate
class ImageAdapterDelegate : AdapterDelegate<List<ListItem>>() {
    // Similar implementation for images
}

// Adapter using delegates
class DelegateAdapter : ListDelegationAdapter<List<ListItem>>() {
    init {
        delegatesManager.addDelegate(TextAdapterDelegate())
        delegatesManager.addDelegate(ImageAdapterDelegate())
        delegatesManager.addDelegate(TextImageAdapterDelegate())
    }
}
```

### Best Practices for Text and Images

#### 1. Efficient Image Loading

```kotlin
class ImageViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    private val imageView: ImageView = itemView.findViewById(R.id.image)

    fun bind(item: ImageItem) {
        // Use Glide or Coil for efficient image loading
        Glide.with(itemView.context)
            .load(item.imageUrl)
            .placeholder(R.drawable.placeholder)
            .error(R.drawable.error_image)
            .centerCrop()
            .into(imageView)
    }
}
```

#### 2. Text Optimization

```kotlin
class TextViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
    private val titleTextView: TextView = itemView.findViewById(R.id.title)

    fun bind(item: TextItem) {
        // Set text efficiently
        titleTextView.text = item.title

        // Use spans for styled text
        val spannableString = SpannableString(item.description)
        spannableString.setSpan(
            StyleSpan(Typeface.BOLD),
            0, 5,
            Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
        )
        titleTextView.text = spannableString
    }
}
```

#### 3. ViewBinding for Type Safety

```kotlin
class TextImageViewHolder(
    private val binding: ItemTextImageBinding
) : RecyclerView.ViewHolder(binding.root) {

    fun bind(item: TextImageItem) {
        binding.apply {
            title.text = item.title
            description.text = item.description

            Glide.with(root.context)
                .load(item.imageUrl)
                .into(image)
        }
    }
}
```

### Benefits of Delegate Pattern

1. **Separation of Concerns** - Each delegate handles one item type
2. **Reusability** - Delegates can be reused across different adapters
3. **Maintainability** - Easier to modify and test individual delegates
4. **Scalability** - Easy to add new item types without modifying existing code
5. **Type Safety** - Clear type handling with sealed classes

## Ответ

Для управления текстом и картинками в RecyclerView используйте делегаты, которые разделяют логику отображения разных типов данных. Это упрощает код и улучшает его поддержку.

