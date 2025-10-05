---
tags:
  - viewgroup
  - inheritance
  - android
  - ui
  - views
difficulty: medium
---

# What does ViewGroup inherit from?

## Question (RU)

От кого наследуются ViewGroup

## Answer

`ViewGroup` is a subclass of the `View` class, which serves as the base for all user interface elements in Android. Understanding this inheritance hierarchy is fundamental to Android UI development.

### Inheritance Hierarchy

```
Object
  ↓
View (base class for all UI elements)
  ↓
ViewGroup (container for other Views)
  ↓
Specific Layout Classes (LinearLayout, RelativeLayout, etc.)
```

### View Class - The Base

The `View` class is the fundamental building block for all UI components:

```kotlin
// Simplified View class structure
abstract class View {
    // Basic properties
    var visibility: Int
    var isEnabled: Boolean
    var isClickable: Boolean

    // Layout parameters
    var layoutParams: ViewGroup.LayoutParams

    // Drawing
    protected open fun onDraw(canvas: Canvas)

    // Measurement
    protected open fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int)

    // Layout
    protected open fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int)

    // Touch events
    open fun onTouchEvent(event: MotionEvent): Boolean

    // Lifecycle
    protected open fun onAttachedToWindow()
    protected open fun onDetachedFromWindow()
}
```

### ViewGroup - The Container

`ViewGroup` extends `View` and adds functionality for managing child views:

```kotlin
// Simplified ViewGroup class structure
abstract class ViewGroup : View {
    // Child management
    fun addView(child: View)
    fun removeView(child: View)
    fun removeAllViews()
    fun getChildAt(index: Int): View
    fun getChildCount(): Int

    // Layout management
    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int)

    // Measurement of children
    fun measureChild(child: View, parentWidthMeasureSpec: Int, parentHeightMeasureSpec: Int)
    fun measureChildren(widthMeasureSpec: Int, heightMeasureSpec: Int)

    // Touch event distribution
    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean
    fun requestDisallowInterceptTouchEvent(disallowIntercept: Boolean)
}
```

### Key Inherited Properties from View

Since `ViewGroup` extends `View`, it inherits all View properties and methods:

```kotlin
class CustomLayout : ViewGroup {

    fun demonstrateInheritedFeatures(context: Context) {
        // Inherited from View
        this.visibility = View.VISIBLE
        this.isEnabled = true
        this.alpha = 0.5f
        this.rotation = 45f
        this.translationX = 100f
        this.translationY = 100f

        this.setBackgroundColor(Color.RED)
        this.setPadding(16, 16, 16, 16)

        this.setOnClickListener {
            // Handle click
        }

        // ViewGroup-specific features
        this.addView(TextView(context))
        this.clipChildren = false
        this.clipToPadding = false
    }
}
```

### Practical Example: Custom ViewGroup

```kotlin
class CustomContainerLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : ViewGroup(context, attrs, defStyleAttr) {

    // Must override onMeasure (inherited from View)
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        var maxWidth = 0
        var maxHeight = 0

        // Measure all children
        measureChildren(widthMeasureSpec, heightMeasureSpec)

        // Calculate dimensions based on children
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            maxWidth = maxOf(maxWidth, child.measuredWidth)
            maxHeight = maxOf(maxHeight, child.measuredHeight)
        }

        // Set measured dimensions (using View's method)
        setMeasuredDimension(
            resolveSize(maxWidth, widthMeasureSpec),
            resolveSize(maxHeight, heightMeasureSpec)
        )
    }

    // Must override onLayout (inherited from View)
    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        // Position all children
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            child.layout(0, 0, child.measuredWidth, child.measuredHeight)
        }
    }

    // Can override onDraw (inherited from View)
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // Custom drawing if needed
    }
}
```

### Common ViewGroup Subclasses

All these classes ultimately inherit from View through ViewGroup:

```kotlin
// Linear arrangement
class LinearLayout : ViewGroup()

// Relative positioning
class RelativeLayout : ViewGroup()

// Frame/stack layout
class FrameLayout : ViewGroup()

// Constraint-based layout
class ConstraintLayout : ViewGroup()

// Coordinate layout
class CoordinatorLayout : ViewGroup()

// Grid layout
class GridLayout : ViewGroup()
```

### Why This Inheritance Matters

1. **Unified Interface**: All UI elements share common methods and properties
2. **Polymorphism**: Can treat ViewGroup as View when needed
3. **Consistent API**: Same event handling, drawing, and lifecycle methods
4. **Flexibility**: ViewGroup can be used anywhere a View can be used

```kotlin
// ViewGroup can be used as View
fun setViewProperties(view: View) {
    view.visibility = View.VISIBLE
    view.alpha = 1.0f
}

val linearLayout = LinearLayout(context)
setViewProperties(linearLayout) // Works because LinearLayout extends ViewGroup extends View
```

### Summary

- **ViewGroup** inherits from **View**
- **View** is the base class for all UI elements
- **ViewGroup** adds child management capabilities
- All layouts (LinearLayout, RelativeLayout, etc.) extend ViewGroup
- This inheritance provides a consistent, unified API for all UI components

## Answer (RU)

ViewGroup является наследником класса View, который является базовым для всех элементов пользовательского интерфейса. ViewGroup выступает как контейнер для других View, предоставляя им общую структуру и управление дочерними элементами.
