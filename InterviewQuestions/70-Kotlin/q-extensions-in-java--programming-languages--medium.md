---
tags:
  - programming-languages
difficulty: medium
status: reviewed
---

# How are Extensions applied in Java?

**English**: How are Extensions applied in Java? Does Java support extension functions like Kotlin?

## Answer

Java does not have direct support for extensions like Kotlin. However, you can implement similar functionality through utility methods (Utility Methods). This allows adding functional capabilities to existing classes without modifying their source code.

**Key differences:**
- **Kotlin extensions**: Look like methods on the class, called with dot notation
- **Java utility methods**: Static methods that take the object as a parameter

**Kotlin extension under the hood:**
When Kotlin compiles extension functions, they become static methods in Java bytecode. The receiver object becomes the first parameter.

### Code Examples

**Kotlin extension function:**

```kotlin
// Kotlin extension function
fun String.addExclamation(): String {
    return "$this!"
}

fun main() {
    val text = "Hello"
    println(text.addExclamation())  // Hello!
}
```

**How Kotlin extension is compiled (Java equivalent):**

```java
// What the compiler generates (approximately)
public final class StringExtensionsKt {
    public static final String addExclamation(String receiver) {
        return receiver + "!";
    }
}

// Usage from Java
public class Main {
    public static void main(String[] args) {
        String text = "Hello";
        String result = StringExtensionsKt.addExclamation(text);
        System.out.println(result);  // Hello!
    }
}
```

**Java utility methods pattern:**

```java
// Java utility class
public class StringUtils {
    // Private constructor to prevent instantiation
    private StringUtils() {
        throw new UnsupportedOperationException("Utility class");
    }

    public static String addExclamation(String str) {
        return str + "!";
    }

    public static String capitalize(String str) {
        if (str == null || str.isEmpty()) {
            return str;
        }
        return str.substring(0, 1).toUpperCase() + str.substring(1);
    }

    public static boolean isNullOrEmpty(String str) {
        return str == null || str.isEmpty();
    }

    public static String repeat(String str, int times) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < times; i++) {
            sb.append(str);
        }
        return sb.toString();
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        String text = "hello";

        System.out.println(StringUtils.addExclamation(text));  // hello!
        System.out.println(StringUtils.capitalize(text));      // Hello
        System.out.println(StringUtils.repeat("*", 5));        // *****

        if (StringUtils.isNullOrEmpty(text)) {
            System.out.println("Empty string");
        } else {
            System.out.println("Not empty");
        }
    }
}
```

**Kotlin extension calling from Java:**

```kotlin
// Kotlin file: StringExtensions.kt
package com.example.utils

fun String.reverse(): String {
    return this.reversed()
}

fun String.truncate(maxLength: Int): String {
    return if (this.length > maxLength) {
        this.substring(0, maxLength) + "..."
    } else {
        this
    }
}

fun Int.isEven(): Boolean {
    return this % 2 == 0
}
```

```java
// Java usage
package com.example;

import com.example.utils.StringExtensionsKt;

public class JavaMain {
    public static void main(String[] args) {
        // Calling Kotlin extensions from Java
        String text = "Hello World";

        String reversed = StringExtensionsKt.reverse(text);
        System.out.println(reversed);  // dlroW olleH

        String truncated = StringExtensionsKt.truncate(text, 5);
        System.out.println(truncated);  // Hello...

        boolean even = StringExtensionsKt.isEven(4);
        System.out.println(even);  // true
    }
}
```

**Java utility class with generics:**

```java
// Java utility class for collections
import java.util.*;
import java.util.function.Predicate;

public class CollectionUtils {
    private CollectionUtils() {}

    public static <T> List<T> filter(List<T> list, Predicate<T> predicate) {
        List<T> result = new ArrayList<>();
        for (T item : list) {
            if (predicate.test(item)) {
                result.add(item);
            }
        }
        return result;
    }

    public static <T> T firstOrNull(List<T> list) {
        return list.isEmpty() ? null : list.get(0);
    }

    public static <T> T lastOrNull(List<T> list) {
        return list.isEmpty() ? null : list.get(list.size() - 1);
    }

    public static <T> boolean contains(List<T> list, T element) {
        return list.contains(element);
    }
}

// Usage
public class Main {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

        // Filter even numbers
        List<Integer> evenNumbers = CollectionUtils.filter(numbers, n -> n % 2 == 0);
        System.out.println(evenNumbers);  // [2, 4, 6, 8, 10]

        // Get first element
        Integer first = CollectionUtils.firstOrNull(numbers);
        System.out.println(first);  // 1

        // Get last element
        Integer last = CollectionUtils.lastOrNull(numbers);
        System.out.println(last);  // 10
    }
}
```

**Comparison: Kotlin vs Java approaches:**

```kotlin
// Kotlin - extension functions (clean syntax)
fun List<Int>.sumEven(): Int {
    return this.filter { it % 2 == 0 }.sum()
}

fun String.isPalindrome(): Boolean {
    return this == this.reversed()
}

fun main() {
    val numbers = listOf(1, 2, 3, 4, 5, 6)
    println(numbers.sumEven())  // 12

    println("racecar".isPalindrome())  // true
    println("hello".isPalindrome())    // false
}
```

```java
// Java - utility methods (verbose syntax)
public class MathUtils {
    public static int sumEven(List<Integer> list) {
        return list.stream()
                   .filter(n -> n % 2 == 0)
                   .mapToInt(Integer::intValue)
                   .sum();
    }
}

public class StringUtils {
    public static boolean isPalindrome(String str) {
        String reversed = new StringBuilder(str).reverse().toString();
        return str.equals(reversed);
    }
}

public class Main {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6);
        System.out.println(MathUtils.sumEven(numbers));  // 12

        System.out.println(StringUtils.isPalindrome("racecar"));  // true
        System.out.println(StringUtils.isPalindrome("hello"));    // false
    }
}
```

**Using @JvmName to customize Java method names:**

```kotlin
// Kotlin file: Extensions.kt
@file:JvmName("TextUtils")  // Custom class name for Java

package com.example

fun String.toTitleCase(): String {
    return this.split(" ")
        .joinToString(" ") { word ->
            word.replaceFirstChar { it.uppercase() }
        }
}
```

```java
// Java usage with custom name
import com.example.TextUtils;  // Note: TextUtils, not ExtensionsKt

public class Main {
    public static void main(String[] args) {
        String text = "hello world from kotlin";
        String result = TextUtils.toTitleCase(text);
        System.out.println(result);  // Hello World From Kotlin
    }
}
```

**Modern Java alternatives:**

```java
// Java 8+ with static imports and method references
import static java.util.stream.Collectors.*;

public class StreamUtils {
    public static String joinStrings(List<String> list, String delimiter) {
        return list.stream().collect(joining(delimiter));
    }

    public static <T> List<T> distinct(List<T> list) {
        return list.stream().distinct().collect(toList());
    }
}

// Usage with static import
import static com.example.StreamUtils.*;

public class Main {
    public static void main(String[] args) {
        List<String> names = Arrays.asList("Alice", "Bob", "Alice", "Charlie");

        String joined = joinStrings(names, ", ");
        System.out.println(joined);  // Alice, Bob, Alice, Charlie

        List<String> uniqueNames = distinct(names);
        System.out.println(uniqueNames);  // [Alice, Bob, Charlie]
    }
}
```

---

## Ответ

### Вопрос
Как Extension применяются в Java

### Ответ
В Java нет прямой поддержки расширений как в Kotlin. Однако можно реализовать аналогичную функциональность через утилитные методы (Utility Methods). Это позволяет добавлять функциональные возможности к существующим классам без изменения их исходного кода.
