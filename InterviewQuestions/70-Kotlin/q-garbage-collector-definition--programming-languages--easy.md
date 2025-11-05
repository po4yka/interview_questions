---
id: lang-021
title: "Garbage Collector Definition / Определение Garbage Collector"
aliases: [Garbage Collector Definition, Определение Garbage Collector]
topic: programming-languages
subtopics: [garbage-collection, jvm, memory-management]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-garbage-collection, q-garbage-collector-basics--programming-languages--medium, q-garbage-collector-roots--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy, garbage-collection, java, jvm, kotlin, memory-management, programming-languages]
date created: Friday, October 31st 2025, 6:31:04 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---
# Что Такое Сборщик Мусора?

# Вопрос (RU)
> Что такое сборщик мусора?

---

# Question (EN)
> What is a garbage collector?

## Ответ (RU)

**Garbage Collector (GC, Сборщик мусора)** — это **механизм управления памятью**, который **автоматически освобождает память**, выделенную для объектов, которые больше не используются в программе.

Эта функция присутствует во многих современных языках программирования (Java, Kotlin, C#, Python, JavaScript, Go), где не требуется ручное управление памятью (как в C или C++).

## Answer (EN)

**Garbage Collector (GC)** is a **memory management mechanism** that **automatically frees memory** allocated for objects that are no longer used in the program.

This feature is present in many modern programming languages (Java, Kotlin, C#, Python, JavaScript, Go) where manual memory management (like in C or C++) is not required.

## Как Он Работает

Сборщик мусора работает в **фоновом режиме**, периодически сканируя память программы на предмет объектов, которые больше не доступны для использования.

**Доступность объекта** обычно определяется по наличию **живых ссылок** на него. Если на объект нет активных ссылок, то считается, что он больше не нужен и память, которую он занимает, может быть освобождена.

### Базовые Принципы

Многие алгоритмы сборки мусора используют следующие базовые принципы:

**1. Пометка (Mark Phase)**

Сканирует объекты, доступные из **корневого набора** (например, переменные стека, статические переменные) и помечает все объекты, которые можно достичь напрямую или косвенно, как **живые**.

```kotlin
// Корневые объекты (достижимые)
val user = User("John")         // Переменная стека - ROOT
companion object {
    val config = Config()       // Статическая переменная - ROOT
}

// Достижимые объекты
val profile = user.profile      // Достижим из user ROOT
val settings = config.settings  // Достижим из config ROOT

// Недостижимые объекты (могут быть собраны)
var temp = Data()
temp = null  // Оригинальный Data() теперь недостижим → GC eligible
```

**2. Очистка (Sweep Phase)**

Затем сборщик проходит по всей heap памяти и освобождает память, занимаемую объектами, которые не были помечены как живые.

```
Heap Memory:

До GC:
[User] ← живой (помечен)
[Profile] ← живой (помечен, ссылается User)
[TempData] ← мёртвый (не помечен, нет ссылок)
[Config] ← живой (помечен)

После GC:
[User] ← оставлен
[Profile] ← оставлен
[        ] ← освобождён (был TempData)
[Config] ← оставлен
```

**3. Уплотнение (Compacting, опционально)**

Некоторые алгоритмы GC также уплотняют память, перемещая живые объекты вместе для уменьшения фрагментации.

```
До уплотнения:
[Object1] [      ] [Object2] [      ] [Object3]
  (живой) (освобождён) (живой) (освобождён) (живой)

После уплотнения:
[Object1] [Object2] [Object3] [                ]
  compact    compact   compact     свободное место
```

---

## Алгоритмы GC

### Generational GC (Наиболее распространённый)

Объекты разделяются на поколения в зависимости от их времени жизни:

- **Young Generation** - только что созданные объекты
- **Old Generation** - долгоживущие объекты
- **Minor GC** - собирает молодое поколение (быстро, часто)
- **Major/Full GC** - собирает весь heap (медленно, редко)

```kotlin
// Молодое поколение (короткоживущие)
fun processRequest() {
    val request = Request()  // Создан
    val response = handle(request)
    return response
    // request становится eligible для GC сразу после выхода из функции
}

// Старое поколение (долгоживущие)
object Cache {
    val data = mutableMapOf<String, Any>()  // Живёт всё время работы приложения
}
```

### Mark and Sweep

Классический алгоритм, который помечает живые объекты, затем очищает мёртвые.

### Copying GC

Разделяет heap на два пространства, копирует живые объекты в одно пространство, затем меняет их местами.

### Reference Counting (не В JVM)

Считает ссылки на каждый объект, освобождает когда счётчик достигает нуля (используется в Python, Swift).

---

## Преимущества

### 1. Уменьшение Ошибок Управления Памятью

Автоматическое управление памятью значительно снижает риски ошибок, таких как:

**Утечки памяти** - память выделяется, но не освобождается:

```kotlin
// ХОРОШО - Не нужно ручное управление памятью
class UserCache {
    private val cache = mutableListOf<User>()

    fun addUser(user: User) {
        cache.add(user)
        // Не нужно вручную освобождать память
    }
}

// GC автоматически освобождает когда cache или users больше не используются
```

**Double free** - память освобождается более одного раза:

```c
// Проблема C/C++ (не существует в GC языках)
free(ptr);
free(ptr);  // Double free - crash!
```

**Use after free** - доступ к освобождённой памяти:

```c
// Проблема C/C++ (не существует в GC языках)
free(ptr);
*ptr = 10;  // Use after free - undefined behavior!
```

### 2. Простота Разработки

Нет необходимости тратить время на явное управление памятью, что упрощает процесс разработки.

```kotlin
// Kotlin - Просто, безопасно
fun createUsers(): List<User> {
    return listOf(
        User("Alice"),
        User("Bob")
    )
}  // Объекты живут столько, сколько нужно, затем GC собирает их

// C - Ручное управление памятью
// User* create_users(int* count) {
//     User* users = (User*)malloc(2 * sizeof(User));
//     // ... инициализация users
//     *count = 2;
//     return users;
// }
// // Вызывающий должен помнить о free(users)!
```

---

## Недостатки

### 1. Непредсказуемость

Сборка мусора может произойти **в любой момент**, что может привести к **кратковременным задержкам** в выполнении программы, особенно если GC занимает много времени.

```kotlin
// GC может приостановить приложение в непредсказуемые моменты
fun processFrame() {
    // Рендеринг кадра
    drawUI()  // Занимает 5ms

    // GC может сделать паузу здесь на 10-50ms!
    // Это вызывает пропуск кадров и дрожание UI

    updateAnimations()
}

// Результат: Непостоянное время кадров
// Кадр 1: 16ms ХОРОШО
// Кадр 2: 45ms - (пауза GC)
// Кадр 3: 16ms ХОРОШО
```

**Stop-the-World (STW) Паузы:**

Во время некоторых фаз GC все потоки приложения приостанавливаются:

```
Приложение работает → Пауза GC (STW) → Приложение возобновляется
     ||||||||||||       [pause]          ||||||||||||
     Нормальное          Все потоки       Нормальное
     выполнение          остановлены!     выполнение
```

### 2. Накладные Расходы

Сборка мусора потребляет **системные ресурсы**, такие как время CPU и память, что может снизить общую производительность приложения.

```kotlin
// Накладные расходы GC
// 1. Время CPU для сканирования и пометки объектов
// 2. Накладные расходы памяти для отслеживания метаданных объектов
// 3. Паузы во время циклов сборки

// Пример: Сервер обрабатывающий запросы
fun handleRequest(request: Request): Response {
    // Создание временных объектов
    val data = parseRequest(request)      // Выделяет память
    val result = processData(data)        // Больше выделений
    return createResponse(result)         // Больше выделений
}

// После многих запросов:
// - Создаётся много мусора
// - GC должен запускаться часто
// - Время CPU тратится на GC вместо обслуживания запросов
```

**Накладные расходы памяти:**

GC нужна дополнительная память для отслеживания объектов:

```
Приложению нужно: 100 MB
Накладные расходы GC: +20 MB (для метаданных, отслеживания)
Всего:            120 MB
```

---

## Резюме

**Garbage Collector:**
- Механизм автоматического управления памятью
- Освобождает память неиспользуемых объектов
- Работает в фоновом режиме, сканируя недостижимые объекты
- Использует алгоритмы mark-and-sweep (и вариации)

**Преимущества:**
- Устраняет утечки памяти
- Предотвращает ошибки double-free
- Упрощает разработку

**Недостатки:**
- Непредсказуемые паузы (Stop-the-World)
- Накладные расходы CPU и памяти
- Может влиять на производительность

**Лучшие практики:**
- Минимизировать выделение объектов
- Переиспользовать объекты когда возможно
- Использовать пулы объектов для частых выделений
- Мониторить поведение GC в продакшене

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-iterator-order-guarantee--programming-languages--medium]]
-
-
