---
tags:
  - elvis
  - kotlin
  - null-safety
  - nullable
  - operators
  - programming-languages
  - safe-call
difficulty: medium
status: reviewed
---

# Что такое null safety и как это пишется?

**English**: What is null safety and how is it written?

## Answer

Null safety is a concept aimed at preventing runtime errors that occur due to unexpected use of null values (like NullPointerException in Java).

**Kotlin null safety features:**

1. **Nullable types**: Variable types by default don't allow null. Use `?` to make type nullable:
```kotlin
var name: String = "John"     // Cannot be null
var nullable: String? = null  // Can be null
```

2. **Safe call operator** `?.`: Access methods/properties safely:
```kotlin
val length = nullable?.length // Returns null if nullable is null
```

3. **Elvis operator** `?:`: Provide default value:
```kotlin
val length = nullable?.length ?: 0 // Returns 0 if null
```

4. **Not-null assertion** `!!`: Force NPE (not recommended):
```kotlin
val length = nullable!!.length // Throws NPE if null
```

5. **Safe casts** `as?`: Cast safely without exception:
```kotlin
val result = value as? String // Returns null if cast fails
```

Kotlin's null safety prevents most null-related crashes at compile time.

## Ответ

Null safety, или безопасность относительно null, — это концепция направленная на предотвращение ошибок времени выполнения...

