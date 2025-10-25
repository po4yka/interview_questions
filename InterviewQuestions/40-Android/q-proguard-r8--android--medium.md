---
id: 20251005-215458
title: "ProGuard and R8 / ProGuard и R8"
aliases: []

# Classification
topic: android
subtopics: [gradle, performance-memory, obfuscation]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru, android/build-tools, android/optimization, android/obfuscation, difficulty/medium]
source: https://github.com/Kirchhoff-Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: [q-why-user-data-may-disappear-on-screen-rotation--android--hard, q-kakaya-raznitsa-mezhdu-dialogom-i-fragmentom--android--medium, q-stop-service--android--medium]

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [android/gradle, android/performance-memory, android/obfuscation, en, ru, difficulty/medium]
---

# Question (EN)
> What's ProGuard?
# Вопрос (RU)
> Что такое ProGuard?

---

## Answer (EN)

ProGuard is free Java class file shrinker, optimizer, obfuscator, and preverifier. It detects and removes unused classes, fields, methods, and attributes. It optimizes bytecode and removes unused instructions. It renames the remaining classes, fields, and methods using short meaningless names.

When you build you project using `Android Gradle plugin 3.4.0` or higher, the plugin no longer uses ProGuard to perform compile-time code optimization. Instead, the plugin works with the R8 compiler to handle the following compile-time tasks:

- **Code shrinking (or tree-shaking)**: detects and safely removes unused classes, fields, methods, and attributes from your app and its library dependencies (making it a valuable tool for working around the 64k reference limit). For example, if you use only a few APIs of a library dependency, shrinking can identify library code that your app is not using and remove only that code from your app
- **Resource shrinking**: Removes unused resources from your packaged app, including unused resources in your app's library dependencies. It works in conjunction with code shrinking such that once unused code has been removed, any resources no longer referenced can be safely removed as well
- **Obfuscation**: Shortens the name of classes and members, which results in reduced DEX file sizes
- **Optimization**: Inspects and rewrites your code to further reduce the size of your app's DEX files. For example, if R8 detects that the `else {}` branch for a given `if/else` statement is never taken, R8 removes the code for the `else {}` branch

When building the release version of your app, by default, R8 automatically performs the compile-time tasks described above for you. However, you can disable certain tasks or customize R8's behavior through ProGuard rules files. In fact, R8 works with all of your existing ProGuard rules files, so updating the Android Gradle plugin to use R8 should not require you to change your existing rules.

To enable shrinking, obfuscation, and optimization, include the following in your project-level build.gradle file:

```gradle
android {
    buildTypes {
        release {
            // Enables code shrinking, obfuscation, and optimization for only
            // your project's release build type.
            minifyEnabled true

            // Enables resource shrinking, which is performed by the
            // Android Gradle plugin.
            shrinkResources true

            // Includes the default ProGuard rules files that are packaged with
            // the Android Gradle plugin. To learn more, go to the section about
            // R8 configuration files.
            proguardFiles getDefaultProguardFile(
                    'proguard-android-optimize.txt'),
                    'proguard-rules.pro'
        }
    }
    ...
}
```

### Customize which code to keep

For most situations, the default ProGuard rules file (`proguard-android-optimize.txt`) is sufficient for R8 to remove only the unused code. However, some situations are difficult for R8 to analyze correctly and it might remove code your app actually needs. Some examples of when it might incorrectly remove code include:

- When your app calls a method from the Java Native Interface (JNI)
- When your app looks up code at runtime (such as with reflection)

To fix errors and force R8 to keep certain code, add a `-keep` line in the ProGuard rules file. For example:

```
-keep public class MyClass
```

Alternatively, you can add the `@Keep` annotation to the code you want to keep. Adding `@Keep` on a class keeps the entire class as-is. Adding it on a method or field will keep the method/field (and its name) as well as the class name intact. **Note** that this annotation is available only when using the `AndroidX Annotations Library` and when you include the ProGuard rules file that is packaged with the `Android Gradle plugin`.

### Conclusion

**Benefits:**

ProGuard (or R8 compiler) obfuscates your code by removing unused code and renaming classes, fields, and methods with semantically obscure names which make the code base, smaller and more efficient. The result is a smaller sized `.apk` file that is more difficult to reverse engineer.

**Drawbacks:**
- Potential misconfiguration causes the app to get crash
- Additional testing is required
- Stacktraces are difficult to read with obfuscated method names
- `ClassNotFoundExceptions`, which happens when ProGuard strips away an entire class that application calls

## Ответ (RU)

ProGuard - это бесплатный инструмент для сжатия, оптимизации, обфускации и предварительной проверки файлов классов Java. Он обнаруживает и удаляет неиспользуемые классы, поля, методы и атрибуты. Он оптимизирует байткод и удаляет неиспользуемые инструкции. Он переименовывает оставшиеся классы, поля и методы, используя короткие бессмысленные имена.

Когда вы собираете свой проект, используя `Android Gradle plugin 3.4.0` или выше, плагин больше не использует ProGuard для выполнения оптимизации кода во время компиляции. Вместо этого плагин работает с компилятором R8 для обработки следующих задач во время компиляции:

- **Сжатие кода (или tree-shaking)**: обнаруживает и безопасно удаляет неиспользуемые классы, поля, методы и атрибуты из вашего приложения и его библиотечных зависимостей (что делает его ценным инструментом для обхода ограничения в 64k ссылок). Например, если вы используете только несколько API библиотечной зависимости, сжатие может идентифицировать код библиотеки, который ваше приложение не использует, и удалить только этот код из вашего приложения
- **Сжатие ресурсов**: Удаляет неиспользуемые ресурсы из упакованного приложения, включая неиспользуемые ресурсы в библиотечных зависимостях вашего приложения. Он работает в сочетании со сжатием кода таким образом, что после удаления неиспользуемого кода любые ресурсы, на которые больше нет ссылок, также могут быть безопасно удалены
- **Обфускация**: Сокращает имена классов и членов, что приводит к уменьшению размеров файлов DEX
- **Оптимизация**: Проверяет и переписывает ваш код для дальнейшего уменьшения размера файлов DEX вашего приложения. Например, если R8 обнаруживает, что ветвь `else {}` для данного оператора `if/else` никогда не выполняется, R8 удаляет код для ветви `else {}`

При создании релизной версии вашего приложения по умолчанию R8 автоматически выполняет описанные выше задачи во время компиляции. Однако вы можете отключить определенные задачи или настроить поведение R8 через файлы правил ProGuard. Фактически, R8 работает со всеми вашими существующими файлами правил ProGuard, поэтому обновление плагина Android Gradle для использования R8 не должно требовать изменения существующих правил.

Чтобы включить сжатие, обфускацию и оптимизацию, включите следующее в файл build.gradle на уровне проекта:

```gradle
android {
    buildTypes {
        release {
            // Включает сжатие кода, обфускацию и оптимизацию только для
            // релизного типа сборки вашего проекта.
            minifyEnabled true

            // Включает сжатие ресурсов, которое выполняется
            // плагином Android Gradle.
            shrinkResources true

            // Включает файлы правил ProGuard по умолчанию, которые упакованы с
            // плагином Android Gradle. Чтобы узнать больше, перейдите в раздел о
            // файлах конфигурации R8.
            proguardFiles getDefaultProguardFile(
                    'proguard-android-optimize.txt'),
                    'proguard-rules.pro'
        }
    }
    ...
}
```

### Настройка того, какой код сохранить

Для большинства ситуаций файл правил ProGuard по умолчанию (`proguard-android-optimize.txt`) достаточен для того, чтобы R8 удалил только неиспользуемый код. Однако некоторые ситуации трудны для правильного анализа R8, и он может удалить код, который фактически нужен вашему приложению. Некоторые примеры, когда он может неправильно удалить код, включают:

- Когда ваше приложение вызывает метод из Java Native Interface (JNI)
- Когда ваше приложение ищет код во время выполнения (например, с помощью рефлексии)

Чтобы исправить ошибки и заставить R8 сохранить определенный код, добавьте строку `-keep` в файл правил ProGuard. Например:

```
-keep public class MyClass
```

В качестве альтернативы вы можете добавить аннотацию `@Keep` к коду, который вы хотите сохранить. Добавление `@Keep` к классу сохраняет весь класс как есть. Добавление его к методу или полю сохранит метод/поле (и его имя), а также имя класса неизменным. **Примечание**: эта аннотация доступна только при использовании `AndroidX Annotations Library` и когда вы включаете файл правил ProGuard, который упакован с `Android Gradle plugin`.

### Заключение

**Преимущества:**

ProGuard (или компилятор R8) обфусцирует ваш код, удаляя неиспользуемый код и переименовывая классы, поля и методы семантически неясными именами, что делает кодовую базу меньше и более эффективной. Результатом является файл `.apk` меньшего размера, который труднее подвергнуть обратной разработке.

**Недостатки:**
- Потенциальная неправильная конфигурация вызывает сбой приложения
- Требуется дополнительное тестирование
- Трассировки стека трудно читать с обфусцированными именами методов
- `ClassNotFoundExceptions`, которые происходят, когда ProGuard удаляет целый класс, который вызывает приложение

---

## References
- [ProGuard Android](https://www.perfomatix.com/proguard-android)
- [Shrink, obfuscate, and optimize your app](https://developer.android.com/studio/build/shrink-code)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview
### Related (Medium)
- [[q-macrobenchmark-startup--android--medium]] - Performance
- [[q-reduce-app-size--android--medium]] - Optimization
- [[q-build-optimization-gradle--android--medium]] - Gradle
- [[q-app-startup-optimization--android--medium]] - Performance
### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
