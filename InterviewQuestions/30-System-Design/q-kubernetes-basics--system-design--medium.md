---
id: sysdes-055
title: Kubernetes Basics
aliases:
- Kubernetes
- K8s
- Container Orchestration
topic: system-design
subtopics:
- infrastructure
- containers
- orchestration
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-service-mesh--system-design--medium
- q-horizontal-vs-vertical-scaling--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- infrastructure
- difficulty/medium
- containers
- system-design
anki_cards:
- slug: sysdes-055-0-en
  language: en
  anki_id: 1769160581427
  synced_at: '2026-01-23T13:29:45.902928'
- slug: sysdes-055-0-ru
  language: ru
  anki_id: 1769160581449
  synced_at: '2026-01-23T13:29:45.905223'
---
# Question (EN)
> What is Kubernetes? Explain its key components and how it helps with system scalability.

# Vopros (RU)
> Что такое Kubernetes? Объясните его ключевые компоненты и как он помогает с масштабируемостью системы.

---

## Answer (EN)

**Kubernetes (K8s)** is a container orchestration platform that automates deployment, scaling, and management of containerized applications.

### Architecture

```
┌─────────────────────────────────────────────────┐
│                 Control Plane                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │API Server│ │Scheduler │ │Controller Manager│ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────────────────────────────────────┐   │
│  │                  etcd                     │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼─────┐ ┌───────▼─────┐ ┌───────▼─────┐
│   Node 1    │ │   Node 2    │ │   Node 3    │
│ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │
│ │ kubelet │ │ │ │ kubelet │ │ │ │ kubelet │ │
│ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │
│ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │
│ │kube-proxy│ │ │ kube-proxy│ │ │ kube-proxy│ │
│ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │
│   [Pods]    │ │   [Pods]    │ │   [Pods]    │
└─────────────┘ └─────────────┘ └─────────────┘
```

### Key Components

| Component | Function |
|-----------|----------|
| **API Server** | Frontend for K8s, handles REST operations |
| **etcd** | Distributed key-value store for cluster state |
| **Scheduler** | Assigns pods to nodes based on resources |
| **Controller Manager** | Runs controllers (ReplicaSet, Deployment) |
| **kubelet** | Agent on each node, manages containers |
| **kube-proxy** | Network proxy, handles service routing |

### Core Concepts

```
Pod:        Smallest deployable unit (1+ containers)
            ┌─────────────────┐
            │ Pod             │
            │ ┌─────┐ ┌─────┐ │
            │ │App  │ │Sidecar│ │
            │ └─────┘ └─────┘ │
            └─────────────────┘

Deployment: Manages ReplicaSets, rolling updates
            Deployment → ReplicaSet → Pods

Service:    Stable endpoint for pods
            ClusterIP, NodePort, LoadBalancer

Ingress:    HTTP/HTTPS routing to services
```

### Scaling

```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Why Kubernetes?

| Feature | Benefit |
|---------|---------|
| Auto-scaling | Scale based on load |
| Self-healing | Restart failed containers |
| Rolling updates | Zero-downtime deployments |
| Service discovery | Built-in DNS |
| Load balancing | Distribute traffic across pods |
| Secret management | Secure credential storage |

---

## Otvet (RU)

**Kubernetes (K8s)** - платформа оркестрации контейнеров, автоматизирующая развёртывание, масштабирование и управление контейнеризированными приложениями.

### Ключевые компоненты

| Компонент | Функция |
|-----------|---------|
| **API Server** | Frontend для K8s, обрабатывает REST операции |
| **etcd** | Распределённое key-value хранилище состояния |
| **Scheduler** | Назначает поды на ноды по ресурсам |
| **Controller Manager** | Запускает контроллеры (ReplicaSet, Deployment) |
| **kubelet** | Агент на каждой ноде, управляет контейнерами |
| **kube-proxy** | Сетевой прокси, обрабатывает роутинг сервисов |

### Основные концепции

```
Pod:        Минимальная развёртываемая единица (1+ контейнеров)

Deployment: Управляет ReplicaSet, rolling updates
            Deployment → ReplicaSet → Pods

Service:    Стабильный endpoint для подов
            ClusterIP, NodePort, LoadBalancer

Ingress:    HTTP/HTTPS роутинг к сервисам
```

### Масштабирование

```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 70
```

### Почему Kubernetes?

| Возможность | Польза |
|-------------|--------|
| Auto-scaling | Масштабирование по нагрузке |
| Self-healing | Перезапуск упавших контейнеров |
| Rolling updates | Деплой без простоя |
| Service discovery | Встроенный DNS |
| Load balancing | Распределение трафика между подами |
| Secret management | Безопасное хранение credentials |

---

## Follow-ups

- What is the difference between a Deployment and a StatefulSet?
- How does Kubernetes handle persistent storage?
- What are init containers and when would you use them?
