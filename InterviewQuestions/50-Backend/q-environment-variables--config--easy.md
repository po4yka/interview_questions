---
id: be-cfg-001
title: Environment Variables Best Practices / Лучшие практики переменных окружения
aliases: []
topic: config
subtopics:
- environment
- configuration
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
source_note: Backend interview preparation
status: draft
moc: moc-backend
related:
- c-configuration
- c-devops
created: 2025-01-23
updated: 2025-01-23
tags:
- config
- environment
- devops
- difficulty/easy
- topic/config
anki_cards:
- slug: be-cfg-001-0-en
  language: en
  anki_id: 1769167239631
  synced_at: '2026-01-23T15:20:42.938752'
- slug: be-cfg-001-0-ru
  language: ru
  anki_id: 1769167239656
  synced_at: '2026-01-23T15:20:42.940566'
---
# Question (EN)
> What are the best practices for using environment variables in applications?

# Vopros (RU)
> Какие лучшие практики использования переменных окружения в приложениях?

---

## Answer (EN)

**Environment Variables** - Key-value pairs set in the operating system environment, used to configure applications without code changes.

---

**Best Practices:**

**1. Fail Fast on Missing Required Variables:**
```python
# Good - explicit requirement
DATABASE_URL = os.environ["DATABASE_URL"]  # Raises KeyError

# Bad - silent default
DATABASE_URL = os.getenv("DATABASE_URL", "localhost")  # May use wrong DB
```

**2. Use Typed Configuration:**
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    port: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()  # Validates types automatically
```

**3. Document All Variables:**
```bash
# .env.example (commit to repo)
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379
SECRET_KEY=  # Generate with: openssl rand -hex 32
DEBUG=false
```

**4. Use Prefixes for Namespacing:**
```bash
APP_DATABASE_URL=...
APP_REDIS_URL=...
APP_SECRET_KEY=...
```

---

**What to Store in Environment Variables:**

| Store | Don't Store |
|-------|-------------|
| Database URLs | Business logic |
| API keys | Code paths |
| Secret keys | Feature implementations |
| Service endpoints | Build artifacts |
| Feature flags | Large data |
| Log levels | |

---

**Loading Order (Priority):**
```
1. Process environment (highest)
2. .env.local (gitignored)
3. .env.{environment} (.env.production)
4. .env (lowest)
5. Default values in code
```

**Example with python-dotenv:**
```python
from dotenv import load_dotenv

# Load in order of priority
load_dotenv(".env.local", override=True)
load_dotenv(".env")

# Access variables
import os
db_url = os.environ["DATABASE_URL"]
```

---

**Security Rules:**

| Rule | Reason |
|------|--------|
| Never commit `.env` | Contains secrets |
| Commit `.env.example` | Documents structure |
| Don't log env vars | May expose secrets |
| Use secrets manager in prod | Better security |
| Rotate secrets regularly | Limit exposure |

## Otvet (RU)

**Переменные окружения** - Пары ключ-значение, установленные в окружении операционной системы, используемые для конфигурации приложений без изменения кода.

---

**Лучшие практики:**

**1. Падать сразу при отсутствии обязательных переменных:**
```python
# Хорошо - явное требование
DATABASE_URL = os.environ["DATABASE_URL"]  # Вызывает KeyError

# Плохо - тихое значение по умолчанию
DATABASE_URL = os.getenv("DATABASE_URL", "localhost")  # Может использовать неправильную БД
```

**2. Использовать типизированную конфигурацию:**
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    port: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()  # Автоматически валидирует типы
```

**3. Документировать все переменные:**
```bash
# .env.example (коммитится в репо)
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379
SECRET_KEY=  # Сгенерировать: openssl rand -hex 32
DEBUG=false
```

**4. Использовать префиксы для пространства имён:**
```bash
APP_DATABASE_URL=...
APP_REDIS_URL=...
APP_SECRET_KEY=...
```

---

**Что хранить в переменных окружения:**

| Хранить | Не хранить |
|---------|------------|
| URL базы данных | Бизнес-логику |
| API-ключи | Пути кода |
| Секретные ключи | Реализации фич |
| Эндпоинты сервисов | Артефакты сборки |
| Feature flags | Большие данные |
| Уровни логирования | |

---

**Порядок загрузки (приоритет):**
```
1. Окружение процесса (высший)
2. .env.local (в gitignore)
3. .env.{environment} (.env.production)
4. .env (низший)
5. Значения по умолчанию в коде
```

**Пример с python-dotenv:**
```python
from dotenv import load_dotenv

# Загрузка в порядке приоритета
load_dotenv(".env.local", override=True)
load_dotenv(".env")

# Доступ к переменным
import os
db_url = os.environ["DATABASE_URL"]
```

---

**Правила безопасности:**

| Правило | Причина |
|---------|---------|
| Никогда не коммитить `.env` | Содержит секреты |
| Коммитить `.env.example` | Документирует структуру |
| Не логировать env vars | Может раскрыть секреты |
| Использовать secrets manager в проде | Лучшая безопасность |
| Регулярно ротировать секреты | Ограничение экспозиции |

---

## Follow-ups
- How to handle different environments (dev, staging, prod)?
- What is the 12-factor app methodology?
- How to validate configuration at startup?

## Dopolnitelnye voprosy (RU)
- Как обрабатывать разные окружения (dev, staging, prod)?
- Что такое методология 12-факторного приложения?
- Как валидировать конфигурацию при запуске?

## References
- [[c-configuration]]
- [[c-devops]]
- [[moc-backend]]
