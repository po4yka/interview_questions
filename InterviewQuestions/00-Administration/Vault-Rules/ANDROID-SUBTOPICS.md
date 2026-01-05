---
---

# Android Subtopics (Controlled List)

**Purpose**: Complete controlled list of Android subtopics for YAML frontmatter.
**Last Updated**: 2025-11-25

**Critical Rule**: For Android notes (`topic: android`), subtopics MUST come from this list and MUST be mirrored to tags as `android/<subtopic>`.

## Usage Example

```yaml
# CORRECT
topic: android
subtopics: [ui-compose, lifecycle, coroutines]
tags: [android/ui-compose, android/lifecycle, android/coroutines, difficulty/medium]

# WRONG - Missing android/* tags
topic: android
subtopics: [ui-compose, lifecycle]
tags: [compose, lifecycle, difficulty/medium]
```

## UI & Compose

```yaml
ui-compose              # Jetpack Compose UI framework
ui-views                # Traditional View system
ui-navigation           # Navigation component, deep links
ui-state                # State management, remember, State
ui-animation            # Animations, transitions
ui-theming              # Material Design, themes, styles
ui-accessibility        # Accessibility, TalkBack, content descriptions
ui-graphics             # Canvas, custom drawing, graphics
ui-widgets              # App widgets, Glance
```

## Architecture

```yaml
architecture-mvvm       # Model-View-ViewModel pattern
architecture-mvi        # Model-View-Intent pattern
architecture-clean      # Clean Architecture principles
architecture-modularization  # Multi-module projects
di-hilt                 # Hilt dependency injection
di-koin                 # Koin dependency injection
feature-flags-remote-config  # Feature flags, Firebase Remote Config
```

## Lifecycle & Components

```yaml
lifecycle               # Activity/Fragment lifecycle
activity                # Activity component
fragment                # Fragment component
service                 # Service component
broadcast-receiver      # BroadcastReceiver component
content-provider        # ContentProvider component
app-startup             # App Startup library
processes               # Process management, IPC
```

## Concurrency

```yaml
coroutines              # Kotlin coroutines
flow                    # Kotlin Flow
threads-sync            # Threads, synchronization, locks
background-execution    # Background work, JobScheduler
```

## Data & Storage

```yaml
room                    # Room database
sqldelight              # SQLDelight database
datastore               # DataStore preferences
files-media             # File system, MediaStore
serialization           # JSON, Protobuf, serialization
cache-offline           # Caching, offline-first patterns
```

## Networking

```yaml
networking-http         # HTTP, Retrofit, OkHttp
websockets              # WebSocket connections
grpc                    # gRPC protocol
graphql                 # GraphQL APIs
connectivity-caching    # Network state, caching strategies
```

## Performance

```yaml
performance-startup     # App startup optimization
performance-rendering   # Rendering, frame rate, jank
performance-memory      # Memory optimization, leaks
performance-battery     # Battery optimization
strictmode-anr          # StrictMode, ANR prevention
profiling               # Profiler, benchmarking
```

## Testing

```yaml
testing-unit            # Unit testing, JUnit
testing-instrumented    # Instrumented tests
testing-ui              # UI testing, Espresso, Compose testing
testing-screenshot      # Screenshot testing
testing-benchmark       # Benchmarking, Macrobenchmark
testing-mocks           # Mocking, test doubles
```

## Build & Tooling

```yaml
gradle                  # Gradle build system
build-variants          # Build variants, flavors
dependency-management   # Dependency management, version catalogs
static-analysis         # Lint, Detekt, static analysis
ci-cd                   # Continuous integration/deployment
versioning              # App versioning, release management
```

## Distribution

```yaml
app-bundle              # Android App Bundle
play-console            # Google Play Console
in-app-updates          # In-app updates
in-app-review           # In-app review
billing                 # Google Play Billing
instant-apps            # Instant Apps
```

## Security

```yaml
permissions             # Runtime permissions
keystore-crypto         # Keystore, cryptography
obfuscation             # ProGuard, R8, obfuscation
network-security-config # Network security configuration
privacy-sdks            # Privacy, GDPR, SDK compliance
```

## Device Features

```yaml
camera                  # CameraX, Camera2
media                   # Media playback, ExoPlayer
location                # Location services
bluetooth               # Bluetooth, BLE
nfc                     # NFC
sensors                 # Device sensors
notifications           # Notifications, channels
intents-deeplinks       # Intents, deep links
shortcuts-widgets       # App shortcuts, widgets
```

## Localization

```yaml
i18n-l10n               # Internationalization, localization
a11y                    # Accessibility
```

## Multiplatform

```yaml
kmp                     # Kotlin Multiplatform
compose-multiplatform   # Compose Multiplatform
```

## Form Factors

```yaml
wear                    # Wear OS
tv                      # Android TV
auto                    # Android Auto
foldables-chromeos      # Foldables, Chrome OS
```

## Monitoring

```yaml
analytics               # Analytics, Firebase Analytics
logging-tracing         # Logging, tracing
crash-reporting         # Crash reporting, Firebase Crashlytics
monitoring-slo          # Monitoring, SLOs
```

## Engagement

```yaml
ads                     # Advertising, AdMob
engagement-retention    # User engagement, retention
ab-testing              # A/B testing, experiments
```

## Quick Reference by Category

| Category | Subtopics |
|----------|-----------|
| **UI** | ui-compose, ui-views, ui-navigation, ui-state, ui-animation |
| **Architecture** | architecture-mvvm, architecture-mvi, di-hilt, di-koin |
| **Lifecycle** | lifecycle, activity, fragment, service |
| **Concurrency** | coroutines, flow, threads-sync |
| **Data** | room, datastore, serialization |
| **Network** | networking-http, websockets, graphql |
| **Performance** | performance-startup, performance-memory, profiling |
| **Testing** | testing-unit, testing-ui, testing-benchmark |

## See Also

- [[TAXONOMY]] - Main taxonomy reference
- [[YAML-EXAMPLES]] - Full YAML examples
- [[AGENT-CHECKLIST]] - Quick reference for AI agents
