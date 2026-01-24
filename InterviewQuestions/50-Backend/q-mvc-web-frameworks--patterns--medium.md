---
id: be-pat-002
title: MVC Pattern in Web Frameworks / Паттерн MVC в веб-фреймворках
aliases: []
topic: patterns
subtopics:
- mvc
- architecture
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Backend interview preparation
status: draft
moc: moc-backend
related:
- c-patterns
- c-architecture
created: 2025-01-23
updated: 2025-01-23
tags:
- patterns
- mvc
- architecture
- difficulty/medium
- topic/patterns
anki_cards:
- slug: be-pat-002-0-en
  language: en
  anki_id: 1769167241505
  synced_at: '2026-01-23T15:20:43.023818'
- slug: be-pat-002-0-ru
  language: ru
  anki_id: 1769167241531
  synced_at: '2026-01-23T15:20:43.025119'
---
# Question (EN)
> What is MVC pattern and how is it implemented in web frameworks?

# Vopros (RU)
> Что такое паттерн MVC и как он реализуется в веб-фреймворках?

---

## Answer (EN)

**MVC (Model-View-Controller)** - Architectural pattern that separates application into three interconnected components.

**Components:**

**Model** - Business logic and data
- Domain entities
- Database access
- Business rules
- Data validation

**View** - Presentation layer
- HTML templates
- JSON serialization
- Response formatting

**Controller** - Request handling
- Receives HTTP requests
- Validates input
- Calls model/services
- Returns response

---

**Web Framework Implementation:**

```
HTTP Request
    |
    v
[Router] -> [Controller] -> [Service/Model] -> [Repository] -> [Database]
                |
                v
            [View/Serializer]
                |
                v
HTTP Response
```

**Django Example:**
```python
# models.py (Model)
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

# views.py (Controller - Django calls it "View")
class ArticleListView(View):
    def get(self, request):
        articles = Article.objects.all()
        return render(request, 'articles/list.html', {'articles': articles})

# templates/articles/list.html (View)
{% for article in articles %}
  <h2>{{ article.title }}</h2>
{% endfor %}
```

**FastAPI Example:**
```python
# models.py (Model)
class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String)

# schemas.py (View - serialization)
class ArticleResponse(BaseModel):
    id: int
    title: str

# routes.py (Controller)
@router.get("/articles", response_model=List[ArticleResponse])
def list_articles(db: Session = Depends(get_db)):
    return db.query(Article).all()
```

---

**MVC Variants in Web:**

| Pattern | Description | Framework |
|---------|-------------|-----------|
| MVC | Classic separation | Rails, Django |
| MVP | Presenter mediates | Android, WinForms |
| MVVM | Two-way data binding | Vue, Angular |
| MVT | Template-based views | Django |

**Layered Architecture (Modern):**
```
Controller -> Service -> Repository -> Database
    |            |
    v            v
  DTO      Domain Model
```

**Controller Responsibilities:**
- Input validation
- Authentication check
- Call service layer
- Error handling
- Response formatting

**Anti-patterns:**
- Fat controllers (too much logic)
- Anemic models (no behavior)
- Business logic in views

## Otvet (RU)

**MVC (Model-View-Controller)** - Архитектурный паттерн, разделяющий приложение на три взаимосвязанных компонента.

**Компоненты:**

**Model** - Бизнес-логика и данные
- Доменные сущности
- Доступ к базе данных
- Бизнес-правила
- Валидация данных

**View** - Слой представления
- HTML-шаблоны
- JSON-сериализация
- Форматирование ответа

**Controller** - Обработка запросов
- Получает HTTP-запросы
- Валидирует ввод
- Вызывает model/services
- Возвращает ответ

---

**Реализация в веб-фреймворках:**

```
HTTP Request
    |
    v
[Router] -> [Controller] -> [Service/Model] -> [Repository] -> [Database]
                |
                v
            [View/Serializer]
                |
                v
HTTP Response
```

**Пример Django:**
```python
# models.py (Model)
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

# views.py (Controller - Django называет это "View")
class ArticleListView(View):
    def get(self, request):
        articles = Article.objects.all()
        return render(request, 'articles/list.html', {'articles': articles})

# templates/articles/list.html (View)
{% for article in articles %}
  <h2>{{ article.title }}</h2>
{% endfor %}
```

**Пример FastAPI:**
```python
# models.py (Model)
class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String)

# schemas.py (View - сериализация)
class ArticleResponse(BaseModel):
    id: int
    title: str

# routes.py (Controller)
@router.get("/articles", response_model=List[ArticleResponse])
def list_articles(db: Session = Depends(get_db)):
    return db.query(Article).all()
```

---

**Варианты MVC в вебе:**

| Паттерн | Описание | Фреймворк |
|---------|----------|-----------|
| MVC | Классическое разделение | Rails, Django |
| MVP | Presenter посредник | Android, WinForms |
| MVVM | Двустороннее связывание | Vue, Angular |
| MVT | Шаблонные views | Django |

**Слоистая архитектура (современная):**
```
Controller -> Service -> Repository -> Database
    |            |
    v            v
  DTO      Domain Model
```

**Обязанности контроллера:**
- Валидация ввода
- Проверка аутентификации
- Вызов сервисного слоя
- Обработка ошибок
- Форматирование ответа

**Антипаттерны:**
- Толстые контроллеры (слишком много логики)
- Анемичные модели (нет поведения)
- Бизнес-логика во views

---

## Follow-ups
- What is the difference between MVC and Clean Architecture?
- How to avoid fat controllers?
- What is the service layer pattern?

## Dopolnitelnye voprosy (RU)
- В чём разница между MVC и Clean Architecture?
- Как избежать толстых контроллеров?
- Что такое паттерн сервисного слоя?

## References
- [[c-patterns]]
- [[c-architecture]]
- [[moc-backend]]
