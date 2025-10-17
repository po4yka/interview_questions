---
id: 20251012-122748
title: Android Lint Tool / Инструмент Android Lint
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [lint, static-analysis, code-quality, gradle, difficulty/medium, android/analysis, android/gradle, android/build-variants]
language_tags: [lint, static-analysis, code-quality, gradle, difficulty/medium, android/analysis, android/gradle, android/build-variants]
moc: moc-android
original_language: en
source: https://github.com/Kirchhoff-/Android-Interview-Questions
subtopics:   - static-analysis
  - gradle
  - build-variants
---
# Android Lint Tool / Инструмент Android Lint

# Question (EN)
> What do you know about Android Lint?

# Вопрос (RU)
> Что вы знаете о Lint в Android?

---

## Answer (EN)

Android Studio provides a code scanning tool called **lint** that can help you to identify and correct problems with the structural quality of your code without your having to execute the app or write test cases. Each problem detected by the tool is reported with a description message and a severity level, so that you can quickly prioritize the critical improvements that need to be made. Also, you can lower the severity level of a problem to ignore issues that are not relevant to your project, or raise the severity level to highlight specific problems.

The lint tool helps find poorly structured code that can impact the reliability and efficiency of your Android apps and make your code harder to maintain. The lint tool checks your Android project source files for potential bugs and optimization improvements for correctness, security, performance, usability, accessibility, and internationalization. When using Android Studio, configured lint and IDE inspections run whenever you build your app.

### How Lint Works

The lint tool processes the application source files:

1. **Application source files** - The source files consist of files that make up your Android project, including Java, Kotlin, and XML files, icons, and ProGuard configuration files.

2. **The `lint.xml` file** - A configuration file that you can use to specify any lint checks that you want to exclude and to customize problem severity levels.

3. **The lint tool** - A static code scanning tool that you can run on your Android project either from the command line or in Android Studio. The lint tool checks for structural code problems that could affect the quality and performance of your Android application.

4. **Results of lint checking** - You can view the results from lint either in the console or in the Inspection Results window in Android Studio.

### Configure Lint to Suppress Warnings

By default when you run a lint scan, the tool checks for all issues that lint supports. You can also restrict the issues for lint to check and assign the severity level for those issues.

You can configure lint checking for different levels:
- Globally (entire project)
- Project module
- Production module
- Test module
- Open files
- Class hierarchy
- Version Control System (VCS) scopes

### Configure the lint.xml File

You can specify your lint checking preferences in the `lint.xml` file. If you are creating this file manually, place it in the root directory of your Android project.

Example `lint.xml` file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<lint>
    <!-- Disable the given check in this project -->
    <issue id="IconMissingDensityFolder" severity="ignore" />

    <!-- Ignore the ObsoleteLayoutParam issue in the specified files -->
    <issue id="ObsoleteLayoutParam">
        <ignore path="res/layout/activation.xml" />
        <ignore path="res/layout-xlarge/activation.xml" />
    </issue>

    <!-- Change the severity of hardcoded strings to "error" -->
    <issue id="HardcodedText" severity="error" />
</lint>
```

### Configure Lint Options with Gradle

The Android plugin for Gradle allows you to configure certain lint options using the `lintOptions {}` block in your module-level `build.gradle` file:

```gradle
android {
  ...
  lintOptions {
    // Turns off checks for the issue IDs you specify.
    disable 'TypographyFractions','TypographyQuotes'
    // Turns on checks for the issue IDs you specify.
    enable 'RtlHardcoded','RtlCompat', 'RtlEnabled'
    // If set to true, turns off analysis progress reporting by lint.
    quiet true
    // if set to true (default), stops the build if errors are found.
    abortOnError false
    // if true, only report errors.
    ignoreWarnings true
  }
}
```

---

## Ответ (RU)

Android Studio предоставляет инструмент сканирования кода под названием **lint**, который может помочь вам выявить и исправить проблемы со структурным качеством кода без необходимости запуска приложения или написания тестов. Каждая проблема, обнаруженная инструментом, сообщается с описанием и уровнем серьезности, чтобы вы могли быстро определить приоритетность критических улучшений. Вы также можете понизить уровень серьезности проблемы, чтобы игнорировать вопросы, не относящиеся к вашему проекту, или повысить уровень серьезности, чтобы выделить конкретные проблемы.

Инструмент lint помогает находить плохо структурированный код, который может повлиять на надежность и эффективность ваших Android-приложений и усложнить поддержку кода. Инструмент lint проверяет исходные файлы вашего Android-проекта на потенциальные ошибки и возможности оптимизации для правильности, безопасности, производительности, удобства использования, доступности и интернационализации. При использовании Android Studio настроенные проверки lint и IDE запускаются всякий раз, когда вы собираете приложение.

### Как работает Lint

Инструмент lint обрабатывает исходные файлы приложения:

1. **Исходные файлы приложения** - Исходные файлы состоят из файлов, составляющих ваш Android-проект, включая файлы Java, Kotlin и XML, значки и файлы конфигурации ProGuard.

2. **Файл `lint.xml`** - Файл конфигурации, который вы можете использовать для указания любых проверок lint, которые вы хотите исключить, и для настройки уровней серьезности проблем.

3. **Инструмент lint** - Инструмент статического сканирования кода, который вы можете запустить в своем Android-проекте либо из командной строки, либо в Android Studio. Инструмент lint проверяет структурные проблемы кода, которые могут повлиять на качество и производительность вашего Android-приложения.

4. **Результаты проверки lint** - Вы можете просмотреть результаты lint либо в консоли, либо в окне Inspection Results в Android Studio.

### Настройка Lint для подавления предупреждений

По умолчанию при запуске сканирования lint инструмент проверяет все проблемы, которые поддерживает lint. Вы также можете ограничить проблемы для проверки lint и назначить уровень серьезности для этих проблем.

Вы можете настроить проверку lint для разных уровней:
- Глобально (весь проект)
- Модуль проекта
- Production модуль
- Test модуль
- Открытые файлы
- Иерархия классов
- Области системы контроля версий (VCS)

### Настройка файла lint.xml

Вы можете указать свои предпочтения проверки lint в файле `lint.xml`. Если вы создаете этот файл вручную, поместите его в корневой каталог вашего Android-проекта.

Пример файла `lint.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<lint>
    <!-- Отключить данную проверку в этом проекте -->
    <issue id="IconMissingDensityFolder" severity="ignore" />

    <!-- Игнорировать проблему ObsoleteLayoutParam в указанных файлах -->
    <issue id="ObsoleteLayoutParam">
        <ignore path="res/layout/activation.xml" />
        <ignore path="res/layout-xlarge/activation.xml" />
    </issue>

    <!-- Изменить серьезность жестко закодированных строк на "error" -->
    <issue id="HardcodedText" severity="error" />
</lint>
```

### Настройка опций Lint с помощью Gradle

Плагин Android для Gradle позволяет настроить определенные параметры lint, используя блок `lintOptions {}` в файле `build.gradle` уровня модуля:

```gradle
android {
  ...
  lintOptions {
    // Отключает проверки для указанных ID проблем
    disable 'TypographyFractions','TypographyQuotes'
    // Включает проверки для указанных ID проблем
    enable 'RtlHardcoded','RtlCompat', 'RtlEnabled'
    // Если установлено в true, отключает отчеты о прогрессе анализа lint
    quiet true
    // если установлено в true (по умолчанию), останавливает сборку при обнаружении ошибок
    abortOnError false
    // если true, сообщать только об ошибках
    ignoreWarnings true
  }
}
```

## References

- [Improve your code with lint checks](https://developer.android.com/studio/write/lint)
- [Configure lint options with Gradle](https://developer.android.com/studio/write/lint#gradle)
