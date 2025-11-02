---
date created: Wednesday, October 29th 2025, 4:40:17 pm
date modified: Saturday, November 1st 2025, 5:43:39 pm
---

# Android System Design Checklist

Use this end-to-end checklist to drive staff-level, Android-aware system design answers. Set measurable targets and enforce Android platform realities.

## 1) Constraints

-   Product scope and non-negotiables (e.g., CDN fixed, auth provider fixed)
-   Transport set: HTTP/gRPC/WebSocket/MQTT allowed?
-   Device classes: low-end, mid, flagship; RAM/CPU/GPU ceilings
-   Network envelope: 3G/Edge → LTE/5G → Wi‑Fi; flap/packet-loss ranges

## 2) OS Realities (Android 11–15)

-   Background limits: Doze/App Standby buckets; FG service rules (Android 14+)
-   Notifications: runtime permission (Android 13+), channels, importance
-   Storage: scoped storage, MediaStore, SAF; large-file handling
-   Play services: present/absent fallbacks (Maps, FusedLocation, Integrity)
-   Manufacturer throttling: alarms, jobs, sockets; mitigations and UX fallbacks

## 3) Non-Functionals (make Tradeoffs testable)

-   Cold start p95: e.g., ≤2.5s
-   Interaction latency (input→render): e.g., ≤150–200ms p95
-   Jank: frame time p95 ≤16.7ms budget; <1% long frames
-   Memory ceiling: steady-state ≤ X MB; spikes ≤ Y MB
-   Battery: foreground ≤3%/hr; background ≤1%/hr
-   Reliability: delivery/commit success ≥99.9% p99; data loss budget = 0
-   Failure budgets: retries N, backoff policy, timeouts per API

## 4) Architecture + State Machines

-   Modules, layering (MVVM/MVI + repositories + workers/services)
-   Client state machines: trip, message, upload/capture, playback
-   Contracts: idempotency keys, sequencing, ack states

## 5) Data & Sync

-   On-device schema: Room/protobuf entities; migrations; indices
-   IDs: local (ULID) vs global; ordering and reconciliation
-   Sync strategy: WS/MQTT vs push-nudge + short-lived fetch; delta formats
-   Conflict resolution: vector clocks/versioning; merge vs server-wins

## 6) Background Plan

-   WorkManager constraints windows; periodic and opportunistic sync
-   Foreground service criteria and lifetimes; notifications
-   Doze-aware scheduling; backoff; maintenance windows

## 7) Performance + Measurement

-   Budgets: CPU/GPU, memory, I/O, network; thermal thresholds and throttles
-   Media configs: codecs, bitrates, GOP, segment sizes (if media)
-   Telemetry: startup p95, jank, cache hit rate, rebuffer ratio, retry histograms
-   Device matrix: test tiers and gating thresholds

## 8) Reliability + Safety

-   Idempotency, dedupe, sequencing; outbox queues
-   Health gates, circuit breakers, fallbacks; kill-switches and feature flags
-   Chaos/latency injection; packet loss and flap tests

## 9) Security & Privacy

-   E2EE posture and key handling (if applicable)
-   At-rest encryption (DB, blobs); secure storage; backups/restore policy
-   Least-privilege permissions; link safety; spam/abuse controls

## 10) Release, Experiments, Ops

-   Staged rollout: 1% → 5% → 20% → 100% with auto-rollback criteria
-   A/B and flags: guard risky codecs/protocols/sampling ladders
-   Oncall & incident plan: dashboards, alerts, SLOs, runbooks

## 11) Sequencing & Risks

-   MVP cut: thinnest slice to ship value
-   Hardening milestones: reliability, battery, background, offline
-   Scale/optimization: ABR, prefetching, resumable uploads, integrity
-   Cross-team dependencies: maps/push/auth/media/infra

---

Use together with: [[ANDROID-INTERVIEWER-GUIDE]]
