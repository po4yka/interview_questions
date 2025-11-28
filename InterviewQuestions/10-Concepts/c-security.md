---
id: "20251111-082256"
title: "Security / Security"
aliases: ["Security"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-encryption, c-encryption-android, c-https-tls, c-biometric-authentication, c-keystore]
created: "2025-11-11"
updated: "2025-11-11"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Tuesday, November 11th 2025, 8:22:56 am
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Security in programming is the practice of designing, writing, and operating software so that it resists unauthorized access, data disclosure, manipulation, and disruption. It matters because vulnerabilities in code and configuration are a primary entry point for attacks that can compromise users, systems, and businesses. In interviews, candidates are expected to understand core secure coding principles, common classes of vulnerabilities, and how language and framework features affect security.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Безопасность в программировании — это практика проектирования, написания и эксплуатации ПО так, чтобы предотвратить несанкционированный доступ, утечку, подмену данных и нарушения работы системы. Это важно, потому что уязвимости в коде и конфигурации являются одним из основных векторов атак, приводящих к компрометации пользователей, систем и бизнеса. На собеседованиях ожидается понимание принципов безопасного кодирования, типичных уязвимостей и того, как особенности языка и фреймворков влияют на безопасность.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Input validation and output encoding: Always validate and sanitize external input, and encode output correctly to prevent injections (e.g., SQL injection, XSS).
- Authentication and authorization: Use proven mechanisms (framework security modules, OAuth/OpenID Connect, role-based access control) instead of ad-hoc solutions.
- Secure storage and transmission: Protect sensitive data using encryption in transit (TLS/HTTPS) and at rest, avoid hardcoding secrets, and use secret managers.
- Dependency and configuration hygiene: Keep dependencies updated, use minimal privileges, secure defaults, and avoid exposing debug/config information in production.
- Defense-in-depth and least privilege: Layer security controls and ensure code and services have only the access they strictly need.

## Ключевые Моменты (RU)

- Валидация ввода и экранирование вывода: Всегда проверяйте и очищайте внешний ввод и корректно кодируйте вывод, чтобы предотвращать инъекции (SQL injection, XSS и др.).
- Аутентификация и авторизация: Используйте проверенные механизмы (security-модули фреймворков, OAuth/OpenID Connect, ролевую модель доступа), а не самодельные решения.
- Безопасное хранение и передача данных: Защищайте чувствительные данные шифрованием при передаче (TLS/HTTPS) и в хранилище, не хардкодьте секреты, применяйте менеджеры секретов.
- Гигиена зависимостей и конфигурации: Обновляйте библиотеки, используйте минимально необходимые права, безопасные значения по умолчанию и не раскрывайте отладочную/служебную конфигурацию в продакшене.
- Многоуровневая защита и минимальные привилегии: Стройте несколько уровней защит и предоставляйте коду и сервисам только строго необходимый доступ.

## References

- OWASP Top Ten (owasp.org/www-project-top-ten/)
- OWASP Cheat Sheet Series (owasp.org/www-project-cheat-sheet-series/)
