---
id: "20251110-134645"
title: "Manifest / Manifest"
aliases: ["Manifest"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: []
created: "2025-11-10"
updated: "2025-11-10"
tags: ["programming-languages", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

A manifest is a structured metadata file that describes the components, configuration, and dependencies of an application, module, or package. It is used by build tools, runtimes, and package managers to understand how to load, verify, version, and execute software artifacts. Common examples include AndroidManifest.xml (Android apps), MANIFEST.MF (Java archives), and package manifests in ecosystems like npm, Maven, Gradle, and Docker.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Манифест — это структурированный файл метаданных, описывающий компоненты, конфигурацию и зависимости приложения, модуля или пакета. Он используется сборочными инструментами, рантаймами и менеджерами пакетов, чтобы определить, как загружать, проверять, версионировать и выполнять программные артефакты. Типичные примеры: AndroidManifest.xml (Android-приложения), MANIFEST.MF (Java-архивы), а также манифесты пакетов в экосистемах npm, Maven, Gradle и Docker.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Describes identity and entry points: defines application/package name, version, main class or entry activity, permissions, and exported components.
- Drives tooling behavior: build systems, IDEs, and runtimes read manifests to assemble classpaths, sign artifacts, perform dependency resolution, and configure deployment.
- Enables dependency and capability declaration: lists required libraries, minimum platform/runtime versions, features, and permissions (e.g., Android permissions).
- Supports integrity and distribution: often used with signatures and hashes to ensure artifact integrity and to meet store or repository requirements.
- Ecosystem-specific but conceptually similar: different platforms have their own manifest formats, but all serve to make software self-describing and machine-readable.

## Ключевые Моменты (RU)

- Описывает идентичность и точки входа: задаёт имя приложения/пакета, версию, основной класс или стартовую активность, права и экспортируемые компоненты.
- Управляет поведением инструментов: системы сборки, IDE и рантаймы читают манифест для формирования classpath, подписи артефактов, разрешения зависимостей и настройки деплоя.
- Позволяет объявлять зависимости и возможности: перечисляет необходимые библиотеки, минимальные версии платформы/рантайма, функции и разрешения (например, разрешения Android).
- Поддерживает целостность и распространение: часто используется вместе с подписями и хешами для проверки целостности артефакта и выполнения требований магазинов/репозиториев.
- Специфичен для экосистемы, но концептуально одинаков: у разных платформ свои форматы манифестов, но цель одна — сделать ПО самоописанным и машинно-читаемым.

## References

- Android Manifest overview: https://developer.android.com/guide/topics/manifest/manifest-intro
- Java JAR File Specification (MANIFEST.MF): https://docs.oracle.com/javase/8/docs/technotes/guides/jar/jar.html
- npm package.json documentation: https://docs.npmjs.com/cli/v10/configuring-npm/package-json
