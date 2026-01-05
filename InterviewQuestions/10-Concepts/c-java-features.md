---
id: concept-005
title: Java Language Features / Особенности языка Java
aliases: [Java Features, Java язык, JVM, Особенности Java]
kind: concept
summary: Overview of key Java language features including object-oriented programming, platform independence, garbage collection, strong typing, and the extensive standard library.
links: []
created: 2025-11-05
updated: 2025-11-05
tags: [concept, java, jvm, language-features, programming-languages]
---

# Summary (EN)

**Java** is a class-based, object-oriented programming language designed to have minimal implementation dependencies. It follows the "write once, run anywhere" (WORA) principle through compilation to bytecode that runs on the Java Virtual Machine (JVM).

**Key Language Features**:

**1. Platform Independence**:
- Compiles to bytecode (.class files) that runs on any JVM
- JVM implementations exist for all major platforms
- Consistent behavior across operating systems

**2. Object-Oriented**:
- Everything is an object (except primitives)
- Classes, inheritance, polymorphism, encapsulation
- Single inheritance (class extends), multiple interface implementation

**3. Strongly Typed**:
- Static type checking at compile time
- Type safety prevents type mismatches
- Generics for type-safe collections (since Java 5)

**4. Automatic Memory Management**:
- Garbage collection handles memory allocation/deallocation
- No manual `free()` or `delete` needed
- Prevents memory leaks and dangling pointers

**5. Rich Standard Library**:
- Collections Framework (List, Set, Map)
- java.util.concurrent for multithreading
- java.io, java.nio for file/network I/O
- java.time for date/time handling (Java 8+)

**6. Multithreading**:
- Built-in support via `Thread` class and `Runnable` interface
- `synchronized` keyword for thread safety
- Higher-level concurrency utilities (Executors, Locks, atomic types)

**7. Exception Handling**:
- Checked exceptions (must handle or declare)
- Unchecked exceptions (RuntimeException)
- try-catch-finally blocks

**8. Modern Features (Java 8+)**:
- **Lambda expressions**: Anonymous functions for functional programming
- **Stream API**: Declarative data processing pipelines
- **Optional**: Container for possibly-null values
- **Method references**: Shorthand for lambdas (`System.out::println`)
- **Default methods**: Interface methods with default implementation
- **Records** (Java 14+): Immutable data carriers
- **Pattern matching** (Java 16+): Type patterns in `instanceof`
- **Sealed classes** (Java 17+): Restricted inheritance hierarchies

**9. Backwards Compatibility**:
- Extremely strong commitment to backwards compatibility
- Code from Java 1.0 (1996) still compiles on modern JVMs
- Deprecation over removal

# Сводка (RU)

**Java** — это объектно-ориентированный язык программирования, основанный на классах, спроектированный с минимальными зависимостями от реализации. Он следует принципу "написано однажды — работает везде" (WORA) через компиляцию в байткод, который выполняется на виртуальной машине Java (JVM).

**Ключевые возможности языка**:

**1. Платформенная независимость**:
- Компилируется в байткод (.class файлы), который работает на любой JVM
- Реализации JVM существуют для всех основных платформ
- Согласованное поведение на разных операционных системах

**2. Объектно-ориентированность**:
- Всё является объектом (кроме примитивов)
- Классы, наследование, полиморфизм, инкапсуляция
- Одиночное наследование (class extends), множественная реализация интерфейсов

**3. Строгая типизация**:
- Статическая проверка типов на этапе компиляции
- Типобезопасность предотвращает несоответствия типов
- Generics для типобезопасных коллекций (с Java 5)

**4. Автоматическое управление памятью**:
- Сборка мусора обрабатывает выделение/освобождение памяти
- Не нужны ручные `free()` или `delete`
- Предотвращает утечки памяти и висячие указатели

**5. Богатая стандартная библиотека**:
- Collections Framework (List, Set, Map)
- java.util.concurrent для многопоточности
- java.io, java.nio для файлового/сетевого ввода-вывода
- java.time для работы с датой/временем (Java 8+)

**6. Многопоточность**:
- Встроенная поддержка через класс `Thread` и интерфейс `Runnable`
- Ключевое слово `synchronized` для потокобезопасности
- Высокоуровневые утилиты конкурентности (Executors, Locks, atomic типы)

**7. Обработка исключений**:
- Проверяемые исключения (checked exceptions) — нужно обработать или объявить
- Непроверяемые исключения (RuntimeException)
- Блоки try-catch-finally

**8. Современные возможности (Java 8+)**:
- **Лямбда-выражения**: Анонимные функции для функционального программирования
- **Stream API**: Декларативные конвейеры обработки данных
- **Optional**: Контейнер для потенциально null значений
- **Ссылки на методы**: Сокращённая запись лямбд (`System.out::println`)
- **Методы по умолчанию**: Методы интерфейса с реализацией по умолчанию
- **Records** (Java 14+): Неизменяемые носители данных
- **Pattern matching** (Java 16+): Шаблоны типов в `instanceof`
- **Sealed классы** (Java 17+): Ограниченные иерархии наследования

**9. Обратная совместимость**:
- Чрезвычайно сильная приверженность обратной совместимости
- Код из Java 1.0 (1996) всё ещё компилируется на современных JVM
- Устаревание (deprecation) вместо удаления

## Use Cases / Trade-offs

**When to use Java**:
- **Enterprise applications**: Banking, e-commerce, large-scale systems
- **Android development**: Primary language before Kotlin (still widely used)
- **Backend services**: Microservices, REST APIs (Spring Boot)
- **Big data**: Hadoop, Spark, Kafka (JVM-based ecosystems)
- **Legacy codebases**: Massive existing Java codebases in production

**Advantages**:
- **Mature ecosystem**: 25+ years of libraries, frameworks, tools
- **Performance**: JIT compilation makes Java very fast
- **Tooling**: Excellent IDE support (IntelliJ, Eclipse, NetBeans)
- **Community**: Huge developer community, extensive documentation
- **Job market**: High demand for Java developers

**Trade-offs**:
- **Verbosity**: More boilerplate than modern languages (Kotlin, Scala)
- **Null safety**: No null safety guarantees (NullPointerException common)
- **Slow evolution**: Conservative language evolution to maintain compatibility
- **Checked exceptions**: Controversial feature, often misused
- **No operator overloading**: Can't define custom operators

**Modern alternatives on JVM**:
- **Kotlin**: Modern, concise, null-safe, 100% Java interop
- **Scala**: Functional + OOP, advanced type system
- **Groovy**: Dynamic typing, scripting-friendly

## References

- [Java SE Documentation](https://docs.oracle.com/en/java/javase/)
- [Effective Java by Joshua Bloch](https://www.oreilly.com/library/view/effective-java/9780134686097/)
- [Java Language Specification](https://docs.oracle.com/javase/specs/)
- [Java Tutorials by Oracle](https://docs.oracle.com/javase/tutorial/)
- [OpenJDK](https://openjdk.org/)
