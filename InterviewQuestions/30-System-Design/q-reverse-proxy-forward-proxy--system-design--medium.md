---
id: sysdes-017
title: Reverse Proxy vs Forward Proxy
aliases:
- Reverse Proxy
- Forward Proxy
- Proxy Server
topic: system-design
subtopics:
- infrastructure
- networking
- security
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-load-balancing-strategies--system-design--medium
- q-api-gateway-patterns--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- infrastructure
- difficulty/medium
- networking
- system-design
anki_cards:
- slug: sysdes-017-0-en
  language: en
  anki_id: 1769158890392
  synced_at: '2026-01-23T13:49:17.739256'
- slug: sysdes-017-0-ru
  language: ru
  anki_id: 1769158890416
  synced_at: '2026-01-23T13:49:17.740712'
---
# Question (EN)
> What is the difference between a reverse proxy and a forward proxy? When would you use each?

# Vopros (RU)
> В чем разница между reverse proxy и forward proxy? Когда использовать каждый из них?

---

## Answer (EN)

A **proxy** is an intermediary server that sits between clients and servers. The key difference is which side benefits.

### Forward Proxy

Sits in front of **clients**, acts on behalf of clients.

```
[Clients] → [Forward Proxy] → [Internet/Servers]

Client knows about proxy
Server sees proxy's IP, not client's IP
```

**Use cases:**
- Corporate network filtering
- Bypass geo-restrictions
- Privacy/anonymity (hide client IP)
- Caching for multiple clients
- Access control

**Examples:** Squid, VPN, corporate proxies

### Reverse Proxy

Sits in front of **servers**, acts on behalf of servers.

```
[Clients] → [Reverse Proxy] → [Backend Servers]

Client doesn't know about backend servers
Client sees proxy's IP/domain
```

**Use cases:**
- Load balancing
- SSL termination
- Caching
- Compression
- Security (hide server topology)
- Rate limiting

**Examples:** Nginx, HAProxy, Traefik

### Comparison Table

| Aspect | Forward Proxy | Reverse Proxy |
|--------|---------------|---------------|
| Protects | Clients | Servers |
| Hides | Client identity | Server identity |
| Client awareness | Client configured to use proxy | Transparent to client |
| Typical location | Client network | Server network |
| Primary purpose | Access control, privacy | Load balancing, security |

### Reverse Proxy Features in Detail

**1. Load Balancing**
```nginx
upstream backend {
    server backend1:8080;
    server backend2:8080;
    server backend3:8080;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

**2. SSL Termination**
```
Client ──HTTPS──→ Reverse Proxy ──HTTP──→ Backend
                  (decrypts here)
```

**3. Caching**
```nginx
proxy_cache_path /cache levels=1:2 keys_zone=my_cache:10m;

location / {
    proxy_cache my_cache;
    proxy_pass http://backend;
}
```

**4. Request Routing**
```nginx
location /api {
    proxy_pass http://api-servers;
}
location /static {
    proxy_pass http://cdn;
}
```

### Common Reverse Proxy Software

| Software | Strengths |
|----------|-----------|
| Nginx | High performance, widely used |
| HAProxy | Advanced load balancing |
| Traefik | Cloud-native, auto-discovery |
| Envoy | Service mesh, observability |
| Caddy | Automatic HTTPS |

---

## Otvet (RU)

**Прокси** - промежуточный сервер между клиентами и серверами. Ключевое отличие - какая сторона получает выгоду.

### Forward Proxy

Стоит перед **клиентами**, действует от имени клиентов.

```
[Клиенты] → [Forward Proxy] → [Интернет/Серверы]

Клиент знает о прокси
Сервер видит IP прокси, а не клиента
```

**Применение:**
- Фильтрация в корпоративных сетях
- Обход гео-ограничений
- Приватность/анонимность (скрытие IP клиента)
- Кеширование для множества клиентов
- Контроль доступа

**Примеры:** Squid, VPN, корпоративные прокси

### Reverse Proxy

Стоит перед **серверами**, действует от имени серверов.

```
[Клиенты] → [Reverse Proxy] → [Backend Серверы]

Клиент не знает о backend серверах
Клиент видит IP/домен прокси
```

**Применение:**
- Балансировка нагрузки
- SSL терминация
- Кеширование
- Сжатие
- Безопасность (скрытие топологии серверов)
- Rate limiting

**Примеры:** Nginx, HAProxy, Traefik

### Сравнительная таблица

| Аспект | Forward Proxy | Reverse Proxy |
|--------|---------------|---------------|
| Защищает | Клиентов | Серверы |
| Скрывает | Идентичность клиента | Идентичность сервера |
| Осведомленность клиента | Клиент настроен на прокси | Прозрачно для клиента |
| Типичное расположение | Сеть клиента | Сеть сервера |
| Основная цель | Контроль доступа, приватность | Балансировка, безопасность |

### Функции Reverse Proxy подробнее

**1. Балансировка нагрузки**
```nginx
upstream backend {
    server backend1:8080;
    server backend2:8080;
    server backend3:8080;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

**2. SSL терминация**
```
Клиент ──HTTPS──→ Reverse Proxy ──HTTP──→ Backend
                  (расшифровка здесь)
```

**3. Кеширование**
```nginx
proxy_cache_path /cache levels=1:2 keys_zone=my_cache:10m;

location / {
    proxy_cache my_cache;
    proxy_pass http://backend;
}
```

**4. Маршрутизация запросов**
```nginx
location /api {
    proxy_pass http://api-servers;
}
location /static {
    proxy_pass http://cdn;
}
```

### Популярное ПО для Reverse Proxy

| ПО | Преимущества |
|----|--------------|
| Nginx | Высокая производительность, широко используется |
| HAProxy | Продвинутая балансировка |
| Traefik | Cloud-native, авто-обнаружение |
| Envoy | Service mesh, observability |
| Caddy | Автоматический HTTPS |

---

## Follow-ups

- How does a reverse proxy differ from a load balancer?
- What is SSL passthrough vs SSL termination?
- How do you configure sticky sessions in a reverse proxy?

## Related Questions

### Prerequisites (Easier)
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing

### Related (Same Level)
- [[q-api-gateway-patterns--system-design--medium]] - API Gateway
- [[q-cdn-content-delivery-network--system-design--medium]] - CDN

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - Architecture
