---
id: "20251111-224424"
title: "Load Balancing / Load Balancing"
aliases: ["Load Balancing"]
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
created: "2025-11-11"
updated: "2025-11-11"
tags: ["programming-languages", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Load balancing is the process of distributing incoming traffic or workloads across multiple computing resources (servers, instances, services) to optimize performance, availability, and resource utilization. It helps prevent single points of failure, mitigates overload on individual nodes, and enables horizontal scaling as demand grows. Commonly used in web backends, microservices, distributed systems, and cloud environments.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Балансировка нагрузки — это процесс распределения входящего трафика или вычислительных задач между несколькими ресурсами (серверами, инстансами, сервисами) для оптимизации производительности, отказоустойчивости и использования ресурсов. Она предотвращает перегрузку отдельных узлов, уменьшает риск единой точки отказа и позволяет горизонтально масштабировать систему по мере роста нагрузки. Широко используется в веб-бэкендах, микросервисах, распределённых системах и облачной инфраструктуре.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Types of load balancers: can operate at different OSI layers (L4 TCP/UDP, L7 HTTP/HTTPS), influencing how traffic is inspected and routed.
- Algorithms: common strategies include Round Robin, Least Connections, IP Hash, and Weighted variants to control how requests are distributed.
- Health checks: periodically probe backend instances; unhealthy nodes are automatically removed from rotation to maintain availability.
- Scalability and high availability: supports horizontal scaling (adding/removing instances) and reduces impact of failures or traffic spikes.
- State and sessions: often requires strategies like sticky sessions or external session storage (cache/DB) to handle user sessions across multiple nodes.

## Ключевые Моменты (RU)

- Типы балансировщиков: работают на разных уровнях модели OSI (L4 TCP/UDP, L7 HTTP/HTTPS), что определяет глубину анализа и маршрутизации трафика.
- Алгоритмы: типичные стратегии — Round Robin, Least Connections, IP Hash и их взвешенные варианты для управления распределением запросов.
- Проверка работоспособности: регулярные health-check'и бекендов; неуспешные узлы автоматически исключаются из ротации для сохранения доступности.
- Масштабируемость и отказоустойчивость: поддерживает горизонтальное масштабирование (добавление/удаление инстансов) и снижает влияние отказов и пиков нагрузки.
- Состояние и сессии: требует подходов вроде sticky sessions или вынесенного хранилища сессий (кэш/БД) для корректной работы пользователей через несколько узлов.

## References

- NGINX Load Balancing Documentation: https://docs.nginx.com/nginx/admin-guide/load-balancer/
- HAProxy Documentation: https://www.haproxy.org/#docs
- AWS Elastic Load Balancing (ELB) Documentation: https://docs.aws.amazon.com/elasticloadbalancing/
