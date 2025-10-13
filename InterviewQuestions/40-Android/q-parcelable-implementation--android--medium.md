---
topic: android
tags:
  - android
  - parcelable
  - serialization
  - intent
  - bundle
  - difficulty/medium
difficulty: medium
status: draft
---

# Parcelable in Android / Parcelable в Android

**English**: What do you know about Parcelable?

## Answer (EN)
**Parcelable** is an Android interface used for **passing data between components** (activities, fragments, services). It's the Android-optimized analog of Java's `Serializable` interface, specifically designed for mobile devices. It assumes a certain structure and way of processing data for efficient inter-process communication.

**Key Characteristics:**

-  **Faster than Serializable** — optimized for Android's IPC (Inter-Process Communication)
-  **Used with Intents and Bundles** — standard way to pass objects between components
-  **Requires implementation** — needs specific methods to be implemented
-  **Type-safe** — compile-time checking of data types

**Basic Implementation:**

Classes implementing the `Parcelable` interface must also have a non-null static field called `CREATOR` of a type that implements the `Parcelable.Creator` interface.

A typical implementation of `Parcelable` is:

```kotlin
// Manual implementation (Java-style)
public class MyParcelable implements Parcelable {
    private int mData;

    public int describeContents() {
        return 0;
    }

    public void writeToParcel(Parcel out, int flags) {
        out.writeInt(mData);
    }

    public static final Parcelable.Creator<MyParcelable> CREATOR
            = new Parcelable.Creator<MyParcelable>() {
        public MyParcelable createFromParcel(Parcel in) {
            return new MyParcelable(in);
        }

        public MyParcelable[] newArray(int size) {
            return new MyParcelable[size];
        }
    };

    private MyParcelable(Parcel in) {
        mData = in.readInt();
    }
}
```

**Kotlin @Parcelize (Recommended):**

The modern and recommended way to implement Parcelable in Kotlin is using the `@Parcelize` annotation:

```kotlin
import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val age: Int,
    val isActive: Boolean
) : Parcelable
```

That's it! The Kotlin compiler plugin automatically generates all the boilerplate code.

**Enabling @Parcelize:**

Add to your `build.gradle`:

```gradle
plugins {
    id 'kotlin-parcelize'
}
```

**Passing Parcelable data between Activities:**

```kotlin
// Sending Activity
val user = User(
    id = 1,
    name = "John Doe",
    email = "john@example.com",
    age = 25,
    isActive = true
)

val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("user_key", user)
startActivity(intent)
```

**Receiving Parcelable data:**

```kotlin
// Receiving Activity
class DetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // API 33+ (Android 13+)
        val user = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra("user_key", User::class.java)
        } else {
            @Suppress("DEPRECATION")
            intent.getParcelableExtra("user_key")
        }

        user?.let {
            // Use the user object
            textView.text = "Name: ${it.name}, Age: ${it.age}"
        }
    }
}
```

**Passing Parcelable ArrayList:**

```kotlin
// Sending
val users = arrayListOf(
    User(1, "John", "john@example.com", 25, true),
    User(2, "Jane", "jane@example.com", 30, true)
)

intent.putParcelableArrayListExtra("users_list", users)
```

**Receiving ArrayList:**

```kotlin
// Receiving
val users = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    intent.getParcelableArrayListExtra("users_list", User::class.java)
} else {
    @Suppress("DEPRECATION")
    intent.getParcelableArrayListExtra("users_list")
}
```

**Complex Parcelable Example:**

```kotlin
@Parcelize
data class Address(
    val street: String,
    val city: String,
    val zipCode: String
) : Parcelable

@Parcelize
data class UserProfile(
    val id: Int,
    val name: String,
    val address: Address,  // Nested Parcelable
    val hobbies: List<String>,
    val metadata: Map<String, String>,
    val registrationDate: Long
) : Parcelable

// Usage
val profile = UserProfile(
    id = 1,
    name = "John Doe",
    address = Address("123 Main St", "New York", "10001"),
    hobbies = listOf("Reading", "Coding", "Gaming"),
    metadata = mapOf("premium" to "true", "verified" to "yes"),
    registrationDate = System.currentTimeMillis()
)

intent.putExtra("profile", profile)
```

**Custom Parceling with @TypeParceler:**

For types that don't implement Parcelable naturally (like Date):

```kotlin
@Parcelize
@TypeParceler<Date, DateParceler>()
data class Event(
    val title: String,
    val date: Date
) : Parcelable

object DateParceler : Parceler<Date> {
    override fun create(parcel: Parcel): Date {
        return Date(parcel.readLong())
    }

    override fun Date.write(parcel: Parcel, flags: Int) {
        parcel.writeLong(time)
    }
}
```

**Parcelable vs Serializable:**

| Feature | Parcelable | Serializable |
|---------|-----------|--------------|
| **Performance** |  Fast |  Slow |
| **Implementation** | More code (without @Parcelize) | Simple |
| **Android optimization** | - Yes | - No |
| **Reflection** | - No | - Yes (slower) |
| **Boilerplate** | With @Parcelize: minimal | Minimal |
| **Use case** | Android IPC | Java serialization |

**When to use Parcelable:**

- - Passing data between Activities
- - Passing data between Fragments
- - Passing data to Services
- - Saving/restoring state in Bundles
- - Any Android IPC scenario

**Best Practices:**

1. **Use @Parcelize** — simplest and most maintainable approach
2. **Keep objects small** — don't pass huge objects through Intents
3. **Use type-safe retrieval** — use the new API on Android 13+
4. **Consider alternatives** — for very large data, use ViewModel, database, or singleton
5. **Avoid circular references** — can cause infinite loops during parceling

**Resources for Parcelable generation:**

- [Kotlin @Parcelize](https://kotlinlang.org/docs/compiler-plugins.html#parcelable-implementations-generator) — **Recommended**
- [parcelabler.com](http://www.parcelabler.com/) — web tool
- [Android Parcelable Plugin](https://github.com/mcharmas/android-parcelable-intellij-plugin) — IntelliJ IDEA plugin

**Summary:**

- **Parcelable**: Android interface for efficient object serialization
- **Purpose**: Pass objects between Android components (Activities, Fragments, Services)
- **Implementation**: Use `@Parcelize` annotation in Kotlin (automatic code generation)
- **Performance**: Much faster than Serializable
- **Use cases**: Intent extras, Bundle arguments, IPC communication

**Sources:**
- [Android Parcelable documentation](https://developer.android.com/reference/android/os/Parcelable)
- [Using Parcelable guide](https://guides.codepath.com/android/using-parcelable)

## Ответ (RU)
**Parcelable** — это Android интерфейс, используемый для **передачи данных между компонентами** (активности, фрагменты, сервисы). Это оптимизированный для Android аналог Java интерфейса `Serializable`, специально разработанный для мобильных устройств.

**Основные характеристики:**

- Быстрее чем Serializable — оптимизирован для IPC (межпроцессного взаимодействия) Android
- Используется с Intent и Bundle — стандартный способ передачи объектов между компонентами
- Требует реализации — необходимо реализовать специфические методы
- Типобезопасный — проверка типов данных во время компиляции

**Современная реализация в Kotlin (@Parcelize):**

Рекомендуемый способ — использование аннотации `@Parcelize`:

```kotlin
import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val age: Int,
    val isActive: Boolean
) : Parcelable
```

Плагин компилятора Kotlin автоматически генерирует весь необходимый код.

**Передача данных между Activity:**

```kotlin
// Отправка
val user = User(1, "John Doe", "john@example.com", 25, true)
val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("user_key", user)
startActivity(intent)

// Получение
class DetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val user = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            intent.getParcelableExtra("user_key", User::class.java)
        } else {
            intent.getParcelableExtra("user_key")
        }
    }
}
```

**Parcelable vs Serializable:**

| Характеристика | Parcelable | Serializable |
|----------------|-----------|--------------|
| Производительность | Быстрый | Медленный |
| Реализация | Больше кода (без @Parcelize) | Простая |
| Оптимизация для Android | Да | Нет |
| Использование рефлексии | Нет | Да (медленнее) |

**Когда использовать Parcelable:**

- Передача данных между Activity
- Передача данных между Fragment
- Передача данных в Service
- Сохранение/восстановление состояния в Bundle
- Любые сценарии IPC в Android

**Лучшие практики:**

1. Используйте @Parcelize — самый простой и поддерживаемый подход
2. Держите объекты небольшими — не передавайте огромные объекты через Intent
3. Используйте типобезопасное получение — новый API на Android 13+
4. Рассмотрите альтернативы — для больших данных используйте ViewModel, базу данных или singleton
5. Избегайте циклических ссылок — могут вызвать бесконечные циклы

**Резюме:**

Parcelable — это интерфейс Android для эффективной сериализации объектов с целью передачи между компонентами. Используйте аннотацию @Parcelize в Kotlin для автоматической генерации кода. Значительно быстрее чем Serializable благодаря отсутствию рефлексии и оптимизации для Android.
