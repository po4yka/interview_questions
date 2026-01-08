---\
---\

# Android System Design — Interviewer One-Pager

Open with the upgraded prompt and numeric targets. Listen for Android-specific constraints and measurable tradeoffs. Push on state machines, data models, background plans, observability, and rollout.

Link: [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]

## Flow

1. State constraints and targets
2. OS realities (Android 11–15) and background rules
3. Architecture + state machines
4. Data model & sync contracts
5. Background execution plan
6. Performance budgets + measurement
7. Reliability + safety
8. Security/privacy posture
9. Release + experiments
10. Sequencing & risks

## Green Flags

-   Explicit numeric budgets (cold start, input→render, jank, battery)
-   Android limits: Doze, FG service, notification permission, scoped storage
-   Concrete state machines and on-device schemas with migrations
-   Client/server contracts (ids, sequencing, idempotency, retries)
-   Observability, health gates, kill-switches, staged rollout with rollback

## Red Flags

-   Vague “MVVM + `Retrofit` + `Room`” with no budgets
-   Ignores background limits and permission flows
-   No schema evolution or conflict resolution
-   No telemetry or rollback strategy

## Failure Injections

-   Network flaps, packet loss, latency spikes
-   Process death, permission revocation, manufacturer throttling
-   CDN hiccups; encoder/decoder failure; socket disconnects

## Prompts (Upgraded)

### Instagram Stories — Capture + Playback

Design Stories capture & playback on Android. Capture: 15s video @ 720p/30fps, optional AR effects, and export <3s (p95) on a mid‑tier device (e.g., Snapdragon 7‑series). Playback: startup <150ms (p95), smooth 60fps on modern devices with graceful degradation on low‑end. Support intermittent connectivity and background‑resumable upload. Show: camera stack choice (CameraX vs. Camera2), render pipeline (zero-copy to encoder), encoder config (codec/profile/bitrate/GOP), chunked/resumable upload, CDN caching & prefetch, on‑device cache policy, ExoPlayer playback strategy, audio focus, thermal/battery mitigation, observability, release/rollback, and accessibility.

### Uber-like Rider App — Request to Dropoff

Design the rider Android app for requesting rides in a tier‑1 city. Targets: map interaction <200ms input→render, cold start <2.5s (p95) on a Pixel‑class device, battery <3%/hr foreground during tracking and <1%/hr background while waiting. Assume intermittent connectivity. Deliver: app architecture, location sampling & trip state machine, background execution plan (Android 14+ rules), realtime channel for driver ETA/updates, anti‑abuse & integrity, no Google Play services fallback, observability, and staged rollout strategy.

### WhatsApp-style E2E Chat — 1:1 & Small Groups

Design an E2E‑encrypted Android chat client supporting 1:1 and small groups. Requirements: online send latency <200ms (p95), durable offline messaging, and sync across 2 devices for the same user. Deliver: local data model & indexing, message ID/ordering, delivery/ack states (sent/received/read), attachment pipeline (encrypt → chunk → resumable upload), notification strategy under Android 13–15, key management & backup posture, spam/abuse mitigations, observability, and rollout plan.
