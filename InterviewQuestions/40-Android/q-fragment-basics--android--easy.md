---
id: 20251012-1227141
title: "Fragment Basics / Основы Fragment"
topic: android
status: draft
created: 2025-10-05
updated: 2025-10-05
difficulty: easy
topics:
  - android
subtopics:
  - fragment
  - lifecycle
  - ui-navigation
tags: [fragment, ui-component, lifecycle, difficulty/easy, android/lifecycle, android/ui-navigation]
language_tags: [fragment, ui-component, lifecycle, difficulty/easy, android/lifecycle, android/ui-navigation]
original_language: en
source: https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20is%20Fragment.md
author: null
related: [q-compose-modifier-order-performance--jetpack-compose--medium, q-what-each-android-component-represents--android--easy, q-android-build-optimization--android--medium]
  - "[[moc-android]]"
  - "[[q-fragment-lifecycle--android--medium]]"
  - "[[q-activity-lifecycle--android--easy]]"
moc: moc-android
  - "[[moc-android]]"
connections: []
---

# Fragment Basics / Основы Fragment

# Question (EN)
> 

# Вопрос (RU)
> 

---

## Answer (EN)
### Definition

A `Fragment` represents a reusable portion of your app's UI. A fragment defines and manages its own layout, has its own lifecycle, and can handle its own input events.

**Key characteristics:**
- Fragments can't live on their own - they must be **hosted** by an activity or another fragment
- The fragment's view hierarchy becomes part of, or **attaches** to, the host's view hierarchy

### Modularity

Fragments introduce modularity and reusability into your activity's UI by letting you divide the UI into discrete chunks.

**Separation of concerns:**
- **Activities**: Ideal place to put global elements around your app's user interface, such as a navigation drawer
- **Fragments**: Better suited to define and manage the UI of a single screen or portion of a screen

**Adaptive UI example:**
- On tablets: Two UI modules defined by fragments can be combined into one activity
- On handsets: The same fragments can be separated into different activities

### Dynamic UI Management

Dividing your UI into fragments makes it easier to modify your activity's appearance at runtime:

**While your activity is in the `STARTED` lifecycle state or higher:**
- Fragments can be **added**
- Fragments can be **replaced**
- Fragments can be **removed**

**Back stack management:**
- You can keep a record of these changes in a back stack managed by the activity
- Changes can be reversed

### Understanding Fragments

Important things to understand about fragments:

1. A `Fragment` is a combination of an XML layout file and a Kotlin/Java class (much like an `Activity`)
2. Using the support library, fragments are supported back to all relevant Android versions
3. Fragments encapsulate views and logic so that it is easier to reuse within activities
4. Fragments are standalone components that can contain views, events, and logic

**Fragment-oriented architecture:**
Within a fragment-oriented architecture, **activities become navigational containers** that are primarily responsible for:
- Navigation to other activities
- Presenting fragments
- Passing data

### Importance of Fragments

Common use cases for fragments:

1. **Reusing View and Logic Components**
   - Fragments enable re-use of parts of your screen including views and event logic
   - Example: Using the same list across different data sources within an app

2. **Tablet Support**
   - The tablet version of an activity often has a substantially different layout from the phone version
   - Fragments enable device-specific activities to reuse shared elements while also having differences

3. **Screen Orientation**
   - The portrait version of an activity often has a substantially different layout from the landscape version
   - Fragments enable both orientations to reuse shared elements while also having differences

### How to Use Fragments

There are three main ways to use fragments:

#### 1. Add Fragment Statically

Add a fragment tag inside the activity layout and set the name to the fragment:

```xml
<fragment
    android:id="@+id/music_fragment"
    android:name="com.example.app.SecondFragment"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    app:layout_constraintBottom_toBottomOf="parent"
    app:layout_constraintEnd_toEndOf="parent" />
```

#### 2. Add Fragment Dynamically

Adding a fragment dynamically means setting the `FragmentManager` to begin a transaction using methods like `add()` or `replace()`, and then calling the `commit()` method:

```kotlin
// Dynamic way of adding fragment
supportFragmentManager
    .beginTransaction()
    .replace(R.id.fragment_container, SenderFragment())
    .commit()
```

**Difference between `add()` and `replace()`:**

- **`add()`**: Keeps adding fragment on top of the previous fragment in the `FragmentContainer`
  - Previous fragments remain in memory
  - Multiple fragments can be visible simultaneously (if they're transparent)

- **`replace()`**: Clears all the previous fragments from container and then adds the new fragment
  - Previous fragments are removed
  - Only the new fragment is visible

**Visual representation:**
```
add():     [Fragment A] → [Fragment A][Fragment B] → [Fragment A][Fragment B][Fragment C]
replace(): [Fragment A] → [Fragment B] → [Fragment C]
```

#### 3. Using Navigation Component

Set up the fragment graph using the Navigation Component, which provides a framework for handling fragment transactions and navigation.

### Code Example: Creating a Simple Fragment

```kotlin
class MyFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // Set up view components here
        view.findViewById<Button>(R.id.myButton).setOnClickListener {
            // Handle button click
        }
    }
}
```

### Best Practices

1. **Use Fragment constructors carefully**: Always provide a no-argument constructor
2. **Communicate through interfaces**: Don't directly reference the activity; use interfaces or ViewModels
3. **Lifecycle awareness**: Be aware of the fragment lifecycle and when views are created/destroyed
4. **Avoid excessive nesting**: Deep fragment nesting can cause performance issues
5. **Use Navigation Component**: For complex navigation flows, prefer the Navigation Component

---



## Ответ (RU)

### Определение

`Fragment` представляет собой многократно используемую часть UI вашего приложения. Фрагмент определяет и управляет своим собственным макетом, имеет свой собственный жизненный цикл и может обрабатывать свои собственные события ввода.

**Ключевые характеристики:**
- Фрагменты не могут существовать самостоятельно - они должны быть **размещены** в Activity или другом Fragment
- Иерархия представлений Fragment становится частью иерархии представлений хоста или **присоединяется** к ней

### Модульность

Fragment вносят модульность и возможность повторного использования в UI вашей Activity, позволяя разделить UI на дискретные части.

**Разделение ответственности:**
- **Activity**: Идеальное место для размещения глобальных элементов пользовательского интерфейса вашего приложения, таких как навигационный ящик
- **Fragment**: Лучше подходят для определения и управления UI одного экрана или части экрана

**Пример адаптивного UI:**
- На планшетах: Два UI-модуля, определенных Fragment, могут быть объединены в одну Activity
- На телефонах: Те же Fragment могут быть разделены на разные Activity

### Динамическое управление UI

Разделение вашего UI на Fragment облегчает изменение внешнего вида вашей Activity во время выполнения:

**Пока ваша Activity находится в состоянии жизненного цикла `STARTED` или выше:**
- Fragment могут быть **добавлены**
- Fragment могут быть **заменены**
- Fragment могут быть **удалены**

**Управление обратным стеком:**
- Вы можете вести запись этих изменений в обратном стеке, управляемом Activity
- Изменения могут быть отменены

### Понимание Fragment

Важные вещи, которые нужно понимать о Fragment:

1. `Fragment` - это комбинация XML-файла макета и класса Kotlin/Java (так же, как и `Activity`)
2. Используя библиотеку поддержки, Fragment поддерживаются во всех соответствующих версиях Android
3. Fragment инкапсулируют представления и логику, что облегчает их повторное использование в Activity
4. Fragment - это самостоятельные компоненты, которые могут содержать представления, события и логику

**Архитектура, ориентированная на Fragment:**
В архитектуре, ориентированной на Fragment, **Activity становятся навигационными контейнерами**, которые в первую очередь отвечают за:
- Навигацию к другим Activity
- Представление Fragment
- Передачу данных

### Важность Fragment

Распространенные случаи использования Fragment:

1. **Повторное использование компонентов представления и логики**
   - Fragment позволяют повторно использовать части вашего экрана, включая представления и логику событий
   - Пример: Использование одного и того же списка для разных источников данных в приложении

2. **Поддержка планшетов**
   - Версия Activity для планшета часто имеет существенно отличающийся макет от версии для телефона
   - Fragment позволяют Activity для конкретных устройств повторно использовать общие элементы, имея при этом различия

3. **Ориентация экрана**
   - Портретная версия Activity часто имеет существенно отличающийся макет от альбомной версии
   - Fragment позволяют обеим ориентациям повторно использовать общие элементы, имея при этом различия

### Как использовать Fragment

Существует три основных способа использования Fragment:

#### 1. Добавить Fragment статически

Добавьте тег fragment в макет Activity и укажите имя Fragment:

```xml
<fragment
    android:id="@+id/music_fragment"
    android:name="com.example.app.SecondFragment"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    app:layout_constraintBottom_toBottomOf="parent"
    app:layout_constraintEnd_toEndOf="parent" />
```

#### 2. Добавить Fragment динамически

Динамическое добавление Fragment означает настройку `FragmentManager` для начала транзакции с использованием таких методов, как `add()` или `replace()`, а затем вызов метода `commit()`:

```kotlin
// Динамический способ добавления фрагмента
supportFragmentManager
    .beginTransaction()
    .replace(R.id.fragment_container, SenderFragment())
    .commit()
```

**Разница между `add()` и `replace()`:**

- **`add()`**: Продолжает добавлять Fragment поверх предыдущего Fragment в `FragmentContainer`
  - Предыдущие Fragment остаются в памяти
  - Несколько Fragment могут быть видны одновременно (если они прозрачные)

- **`replace()`**: Очищает все предыдущие Fragment из контейнера, а затем добавляет новый Fragment
  - Предыдущие Fragment удаляются
  - Виден только новый Fragment

**Визуальное представление:**
```
add():     [Fragment A] → [Fragment A][Fragment B] → [Fragment A][Fragment B][Fragment C]
replace(): [Fragment A] → [Fragment B] → [Fragment C]
```

#### 3. Использование Navigation Component

Настройте граф Fragment с помощью Navigation Component, который предоставляет фреймворк для обработки транзакций Fragment и навигации.

### Пример кода: Создание простого Fragment

```kotlin
class MyFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Инфлейт макета для этого фрагмента
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // Настройка компонентов представления здесь
        view.findViewById<Button>(R.id.myButton).setOnClickListener {
            // Обработка нажатия кнопки
        }
    }
}
```

### Лучшие практики

1. **Используйте конструкторы Fragment осторожно**: Всегда предоставляйте конструктор без аргументов
2. **Общайтесь через интерфейсы**: Не ссылайтесь напрямую на Activity; используйте интерфейсы или ViewModel
3. **Осведомленность о жизненном цикле**: Будьте в курсе жизненного цикла Fragment и того, когда представления создаются/уничтожаются
4. **Избегайте чрезмерной вложенности**: Глубокая вложенность Fragment может вызвать проблемы с производительностью
5. **Используйте Navigation Component**: Для сложных потоков навигации предпочтительнее использовать Navigation Component

---

## References

- [Android Developer Docs: Fragments](https://developer.android.com/guide/fragments)
- [CodePath: Creating and Using Fragments](https://guides.codepath.com/android/creating-and-using-fragments)
- [GeeksforGeeks: Introduction to Fragments | Android](https://www.geeksforgeeks.org/introduction-fragments-android/)
- [Medium: Fragments in Android](https://medium.com/@myofficework000/fragments-in-android-eab537b00071)
- [Vogella: Building dynamic user interfaces in Android with fragments](https://www.vogella.com/tutorials/AndroidFragments/article.html)
- [Square: Advocating Against Android Fragments](https://developer.squareup.com/blog/advocating-against-android-fragments/)
- [Medium: 7 Common Mistakes Easily Made with Android Fragment](https://medium.com/mobile-app-development-publication/7-common-mistakes-easily-made-with-android-fragment-6fc85c44e783)

---

## Related Questions

### Related (Easy)
- [[q-how-to-choose-layout-for-fragment--android--easy]] - Fragment

### Advanced (Harder)
- [[q-save-data-outside-fragment--android--medium]] - Fragment
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Fragment
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - Fragment
