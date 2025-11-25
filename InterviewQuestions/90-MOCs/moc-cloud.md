---
id: ivm-20251018-140200
title: Cloud Platforms — MOC
kind: moc
created: 2025-10-18
updated: 2025-10-18
tags: [moc, topic/cloud]
date created: Saturday, October 18th 2025, 2:46:11 pm
date modified: Tuesday, November 25th 2025, 8:53:47 pm
---

# Cloud Platforms — Map of Content

## Overview

This MOC covers cloud computing platforms (AWS, GCP, Azure), cloud-native architectures, serverless computing, containerization, infrastructure as code, and best practices for building scalable cloud-based systems.

**Note**: This MOC is currently a placeholder. Cloud-related interview questions are being developed and will be added to this map as they become available.

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM ""
WHERE topic = "cloud" AND difficulty = "easy"
SORT file.name ASC
LIMIT 50
```

**Status**: No easy cloud questions yet. Coming soon.

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM ""
WHERE topic = "cloud" AND difficulty = "medium"
SORT file.name ASC
LIMIT 50
```

**Status**: No medium cloud questions yet. Coming soon.

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM ""
WHERE topic = "cloud" AND difficulty = "hard"
SORT file.name ASC
LIMIT 50
```

**Status**: No hard cloud questions yet. Coming soon.

## By Subtopic

### AWS (Amazon Web Services)

**Planned Coverage**:
- EC2 (Elastic Compute Cloud)
- S3 (Simple Storage Service)
- Lambda (Serverless Functions)
- RDS (Relational Database Service)
- DynamoDB (NoSQL Database)
- API Gateway
- CloudFront (CDN)
- VPC (Virtual Private Cloud)
- IAM (Identity and Access Management)
- CloudWatch (Monitoring)
- ECS/EKS (Container Services)

**All AWS Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE topic = "cloud" AND (contains(tags, "aws") OR contains(subtopics, "aws"))
SORT difficulty ASC, file.name ASC
```

**Status**: No AWS questions yet. Coming soon.

### GCP (Google Cloud Platform)

**Planned Coverage**:
- Compute Engine
- Cloud Storage
- Cloud Functions
- Cloud Run
- BigQuery
- Firestore
- Pub/Sub
- Cloud CDN
- IAM
- Cloud Monitoring

**All GCP Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE topic = "cloud" AND (contains(tags, "gcp") OR contains(subtopics, "gcp"))
SORT difficulty ASC, file.name ASC
```

**Status**: No GCP questions yet. Coming soon.

### Azure (Microsoft Azure)

**Planned Coverage**:
- Virtual Machines
- Blob Storage
- Azure Functions
- Cosmos DB
- Azure SQL Database
- Application Gateway
- Azure CDN
- Active Directory
- Azure Monitor

**All Azure Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE topic = "cloud" AND (contains(tags, "azure") OR contains(subtopics, "azure"))
SORT difficulty ASC, file.name ASC
```

**Status**: No Azure questions yet. Coming soon.

### Cloud-Native Architecture

**Planned Coverage**:
- Microservices patterns
- Service mesh
- API gateways
- Cloud-native security
- Observability and monitoring
- Disaster recovery
- Multi-region deployment
- Cost optimization

**All Cloud-Native Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE topic = "cloud" AND (contains(tags, "cloud-native") OR contains(subtopics, "cloud-native"))
SORT difficulty ASC, file.name ASC
```

**Status**: No cloud-native questions yet. Coming soon.

### Serverless Computing

**Planned Coverage**:
- Function as a Service (FaaS)
- Event-driven architecture
- Lambda/Cloud Functions patterns
- Cold starts and optimization
- Serverless databases
- API Gateway patterns
- Step Functions/Cloud Workflows
- Serverless security

**All Serverless Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE topic = "cloud" AND (contains(tags, "serverless") OR contains(subtopics, "serverless"))
SORT difficulty ASC, file.name ASC
```

**Status**: No serverless questions yet. Coming soon.

### Containers & Orchestration

**Planned Coverage**:
- Docker fundamentals
- Kubernetes basics
- ECS/EKS/GKE/AKS
- Container networking
- Service discovery
- Container security
- CI/CD with containers
- Container registries

**All Container Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE topic = "cloud" AND (contains(tags, "containers") OR contains(tags, "kubernetes") OR contains(tags, "docker"))
SORT difficulty ASC, file.name ASC
```

**Status**: No container questions yet. Coming soon.

### Cloud Storage

**Planned Coverage**:
- Object storage (S3, Cloud Storage, Blob)
- Block storage
- File storage
- Storage classes and lifecycle
- CDN integration
- Data transfer optimization
- Storage security
- Backup and archival

**All Storage Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE topic = "cloud" AND (contains(tags, "cloud-storage") OR contains(subtopics, "storage"))
SORT difficulty ASC, file.name ASC
```

**Status**: No storage questions yet. Coming soon.

### Infrastructure as Code

**Planned Coverage**:
- Terraform
- CloudFormation
- ARM Templates
- Pulumi
- Configuration management
- State management
- Module design
- Best practices

**All IaC Questions:**
```dataview
TABLE difficulty, status
FROM ""
WHERE topic = "cloud" AND (contains(tags, "iac") OR contains(tags, "terraform") OR contains(tags, "cloudformation"))
SORT difficulty ASC, file.name ASC
```

**Status**: No IaC questions yet. Coming soon.

## All Questions

```dataview
TABLE difficulty, subtopics, status, tags
FROM ""
WHERE topic = "cloud"
SORT difficulty ASC, file.name ASC
```

**Current Count**: 0 questions

## Statistics

```dataview
TABLE length(rows) as "Count"
FROM ""
WHERE topic = "cloud"
GROUP BY difficulty
SORT difficulty ASC
```

**Current Status**: No cloud questions in vault. This MOC is ready to organize content as it's created.

## Related MOCs

- [[moc-system-design]] - System design and scalability patterns
- [[moc-backend]] - Backend infrastructure and databases
- [[moc-cs]] - Computer science fundamentals (networking, OS concepts)

## Recommended Question Topics

When creating cloud questions, consider covering:

**AWS Essentials**:
- EC2 instance types and use cases
- S3 storage classes and lifecycle policies
- Lambda function design and cold starts
- RDS vs DynamoDB trade-offs
- VPC networking basics
- IAM policies and best practices

**GCP Essentials**:
- Compute Engine vs Cloud Run vs Cloud Functions
- Cloud Storage classes
- BigQuery optimization
- Firestore vs Cloud SQL
- VPC networking
- IAM roles and service accounts

**Azure Essentials**:
- VM types and pricing
- Blob Storage tiers
- Azure Functions triggers
- Cosmos DB consistency levels
- Virtual Networks
- Azure AD authentication

**Cross-Platform Concepts**:
- Multi-cloud strategies
- Cloud cost optimization
- Security best practices
- Monitoring and observability
- Disaster recovery and backup
- Compliance and governance

**Serverless Patterns**:
- Event-driven architectures
- API Gateway design
- Function composition
- State management
- Error handling and retries
- Performance optimization

**Container & Kubernetes**:
- Container basics and Docker
- Kubernetes architecture
- Pod scheduling and scaling
- Service mesh patterns
- Helm charts
- GitOps workflows

## Notes

This MOC uses flexible Dataview queries that search across all folders for `topic: cloud` notes, since cloud questions may be placed in various folders (30-System-Design/, 50-Backend/, 60-CompSci/) depending on their specific focus.

When creating cloud questions:
- Set `topic: cloud` in YAML frontmatter
- Choose appropriate subtopics (aws, gcp, azure, serverless, containers, etc.)
- Add platform-specific tags (aws, gcp, azure, kubernetes, docker, terraform)
- Link to this MOC with `moc: moc-cloud`
- Cross-reference with moc-system-design and moc-backend where relevant

---

**Last Updated**: 2025-10-18
**Status**: Placeholder MOC ready for content
**Questions**: 0/0 (0%)
