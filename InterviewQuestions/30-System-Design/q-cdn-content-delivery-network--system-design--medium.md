---
id: sysdes-016
title: CDN - Content Delivery Network
aliases:
- CDN
- Content Delivery Network
- Edge Caching
topic: system-design
subtopics:
- infrastructure
- caching
- performance
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-caching-strategies--system-design--medium
- q-dns-resolution--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- infrastructure
- difficulty/medium
- caching
- system-design
anki_cards:
- slug: sysdes-016-0-en
  language: en
  anki_id: 1769158891691
  synced_at: '2026-01-23T13:49:17.861235'
- slug: sysdes-016-0-ru
  language: ru
  anki_id: 1769158891716
  synced_at: '2026-01-23T13:49:17.862375'
---
# Question (EN)
> What is a CDN and how does it work? When should you use a CDN in your system design?

# Vopros (RU)
> Что такое CDN и как он работает? Когда следует использовать CDN при проектировании систем?

---

## Answer (EN)

**CDN (Content Delivery Network)** is a geographically distributed network of servers that delivers content from locations closer to users.

### How CDN Works

```
Without CDN:
User (Tokyo) ──────────────────→ Origin (New York)
                 High latency

With CDN:
User (Tokyo) ────→ Edge Server (Tokyo) ─→ Origin (New York)
                    Low latency          Only on cache miss
```

### CDN Request Flow

```
1. User requests example.com/image.jpg
2. DNS resolves to nearest edge server
3. Edge server checks cache:
   - Cache HIT → Return cached content
   - Cache MISS → Fetch from origin, cache, return
4. Response served from edge location
```

### Types of Content

| Content Type | Cacheability | TTL |
|--------------|--------------|-----|
| Static assets (JS, CSS, images) | Highly cacheable | Hours to days |
| HTML pages | Depends on dynamism | Minutes to hours |
| API responses | Selective | Seconds to minutes |
| Real-time data | Not cacheable | N/A |

### CDN Features

**1. Caching**
```
Cache-Control: public, max-age=86400
```

**2. Compression**
- Gzip, Brotli for text content
- Reduces bandwidth by 60-80%

**3. SSL/TLS Termination**
- HTTPS handled at edge
- Reduces origin server load

**4. DDoS Protection**
- Absorbs attack traffic
- Rate limiting at edge

**5. Edge Computing**
- Run code at edge locations
- Cloudflare Workers, Lambda@Edge

### Push vs Pull CDN

| Pull CDN | Push CDN |
|----------|----------|
| Fetches content on first request | Content uploaded proactively |
| Automatic cache population | Manual cache management |
| Better for dynamic content | Better for known static assets |
| May have initial cache miss latency | Consistent performance |

### When to Use CDN

**Use CDN for:**
- Static assets (images, videos, JS, CSS)
- Global user base
- High-traffic websites
- Streaming media
- Software downloads

**Skip CDN for:**
- Internal applications
- Single-region users
- Highly personalized content
- Real-time data

### Popular CDN Providers

| Provider | Strength |
|----------|----------|
| CloudFlare | Security, Workers, free tier |
| AWS CloudFront | AWS integration |
| Akamai | Enterprise, largest network |
| Fastly | Real-time purging, edge compute |

---

## Otvet (RU)

**CDN (Content Delivery Network)** - географически распределенная сеть серверов, которая доставляет контент из локаций ближе к пользователям.

### Как работает CDN

```
Без CDN:
Пользователь (Токио) ──────────────────→ Origin (Нью-Йорк)
                        Высокая задержка

С CDN:
Пользователь (Токио) ────→ Edge Server (Токио) ─→ Origin (Нью-Йорк)
                           Низкая задержка       Только при cache miss
```

### Поток запроса CDN

```
1. Пользователь запрашивает example.com/image.jpg
2. DNS разрешается в ближайший edge сервер
3. Edge сервер проверяет кеш:
   - Cache HIT → Вернуть закешированный контент
   - Cache MISS → Получить с origin, закешировать, вернуть
4. Ответ отдается с edge-локации
```

### Типы контента

| Тип контента | Кешируемость | TTL |
|--------------|--------------|-----|
| Статика (JS, CSS, изображения) | Высокая | Часы-дни |
| HTML страницы | Зависит от динамичности | Минуты-часы |
| API ответы | Выборочно | Секунды-минуты |
| Реалтайм данные | Не кешируются | Н/Д |

### Функции CDN

**1. Кеширование**
```
Cache-Control: public, max-age=86400
```

**2. Сжатие**
- Gzip, Brotli для текстового контента
- Снижает трафик на 60-80%

**3. SSL/TLS терминация**
- HTTPS обрабатывается на edge
- Снижает нагрузку на origin

**4. DDoS защита**
- Поглощает атакующий трафик
- Rate limiting на edge

**5. Edge Computing**
- Запуск кода на edge-локациях
- Cloudflare Workers, Lambda@Edge

### Push vs Pull CDN

| Pull CDN | Push CDN |
|----------|----------|
| Получает контент по первому запросу | Контент загружается проактивно |
| Автоматическое заполнение кеша | Ручное управление кешем |
| Лучше для динамического контента | Лучше для известной статики |
| Может быть задержка при первом запросе | Стабильная производительность |

### Когда использовать CDN

**Используйте CDN для:**
- Статические ассеты (изображения, видео, JS, CSS)
- Глобальная база пользователей
- Высоконагруженные сайты
- Стриминг медиа
- Загрузка ПО

**Не нужен CDN для:**
- Внутренние приложения
- Пользователи в одном регионе
- Сильно персонализированный контент
- Реалтайм данные

### Популярные CDN провайдеры

| Провайдер | Преимущество |
|-----------|--------------|
| CloudFlare | Безопасность, Workers, бесплатный тариф |
| AWS CloudFront | Интеграция с AWS |
| Akamai | Enterprise, крупнейшая сеть |
| Fastly | Мгновенная инвалидация, edge compute |

---

## Follow-ups

- How do you invalidate CDN cache?
- What is cache warming and when do you need it?
- How does CDN handle dynamic content?

## Related Questions

### Prerequisites (Easier)
- [[q-caching-strategies--system-design--medium]] - Caching basics
- [[q-dns-resolution--system-design--medium]] - DNS

### Related (Same Level)
- [[q-reverse-proxy-forward-proxy--system-design--medium]] - Proxies
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing

### Advanced (Harder)
- [[q-design-youtube--system-design--hard]] - Video streaming design
