---
id: be-sec-006
title: OWASP Top 10 Vulnerabilities / Топ-10 уязвимостей OWASP
aliases: []
topic: security
subtopics:
- owasp
- vulnerabilities
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
source_note: Backend interview preparation
status: draft
moc: moc-backend
related:
- c-security
- c-owasp
created: 2025-01-23
updated: 2025-01-23
tags:
- security
- owasp
- vulnerabilities
- difficulty/hard
- topic/security
anki_cards:
- slug: be-sec-006-0-en
  language: en
  anki_id: 1769167241457
  synced_at: '2026-01-23T15:20:43.018986'
- slug: be-sec-006-0-ru
  language: ru
  anki_id: 1769167241482
  synced_at: '2026-01-23T15:20:43.022194'
---
# Question (EN)
> What are the OWASP Top 10 vulnerabilities and how to prevent them?

# Vopros (RU)
> Что такое OWASP Top 10 и как предотвратить эти уязвимости?

---

## Answer (EN)

**OWASP Top 10 (2021)** - Most critical web application security risks:

**A01: Broken Access Control**
- Users access unauthorized resources
- **Prevention:** Deny by default, validate permissions server-side, use RBAC

**A02: Cryptographic Failures**
- Sensitive data exposed (passwords, PII)
- **Prevention:** Use strong encryption (AES-256), HTTPS everywhere, hash passwords with bcrypt/argon2

**A03: Injection**
- SQL, NoSQL, OS command injection
- **Prevention:** Parameterized queries, input validation, ORM

**A04: Insecure Design**
- Missing security requirements in design phase
- **Prevention:** Threat modeling, secure design patterns, security reviews

**A05: Security Misconfiguration**
- Default credentials, verbose errors, unnecessary features
- **Prevention:** Hardening guides, automated configuration audits, minimal installs

**A06: Vulnerable Components**
- Using libraries with known vulnerabilities
- **Prevention:** Dependency scanning, regular updates, SBOM

**A07: Authentication Failures**
- Weak passwords, missing MFA, session issues
- **Prevention:** Strong password policies, MFA, secure session management

**A08: Software and Data Integrity Failures**
- Untrusted sources, unsigned updates
- **Prevention:** Verify signatures, use trusted CDNs, integrity checks

**A09: Security Logging and Monitoring Failures**
- Insufficient logging, no alerting
- **Prevention:** Log security events, monitor anomalies, incident response plan

**A10: Server-Side Request Forgery (SSRF)**
- Server makes requests to unintended destinations
- **Prevention:** Allowlist URLs, disable unnecessary protocols, network segmentation

## Otvet (RU)

**OWASP Top 10 (2021)** - Наиболее критичные риски безопасности веб-приложений:

**A01: Нарушение контроля доступа**
- Пользователи получают доступ к неавторизованным ресурсам
- **Предотвращение:** Запрет по умолчанию, валидация прав на сервере, использование RBAC

**A02: Криптографические ошибки**
- Раскрытие конфиденциальных данных (пароли, PII)
- **Предотвращение:** Сильное шифрование (AES-256), HTTPS везде, хэширование паролей bcrypt/argon2

**A03: Инъекции**
- SQL, NoSQL, инъекции команд ОС
- **Предотвращение:** Параметризованные запросы, валидация ввода, ORM

**A04: Небезопасный дизайн**
- Отсутствие требований безопасности на этапе проектирования
- **Предотвращение:** Моделирование угроз, безопасные паттерны, ревью безопасности

**A05: Неправильная конфигурация**
- Учётные данные по умолчанию, подробные ошибки, лишние функции
- **Предотвращение:** Руководства по hardening, автоматический аудит, минимальные установки

**A06: Уязвимые компоненты**
- Использование библиотек с известными уязвимостями
- **Предотвращение:** Сканирование зависимостей, регулярные обновления, SBOM

**A07: Ошибки аутентификации**
- Слабые пароли, отсутствие MFA, проблемы с сессиями
- **Предотвращение:** Строгие политики паролей, MFA, безопасное управление сессиями

**A08: Нарушения целостности ПО и данных**
- Ненадёжные источники, неподписанные обновления
- **Предотвращение:** Проверка подписей, надёжные CDN, проверка целостности

**A09: Недостатки логирования и мониторинга**
- Недостаточное логирование, отсутствие оповещений
- **Предотвращение:** Логирование событий безопасности, мониторинг аномалий, план реагирования

**A10: Server-Side Request Forgery (SSRF)**
- Сервер делает запросы к непредусмотренным адресам
- **Предотвращение:** Allowlist URL, отключение лишних протоколов, сегментация сети

---

## Follow-ups
- How to implement security testing in CI/CD pipeline?
- What is threat modeling?
- What tools can detect OWASP vulnerabilities?

## Dopolnitelnye voprosy (RU)
- Как внедрить тестирование безопасности в CI/CD pipeline?
- Что такое моделирование угроз?
- Какие инструменты могут обнаружить уязвимости OWASP?

## References
- [[c-security]]
- [[c-owasp]]
- [[moc-backend]]
