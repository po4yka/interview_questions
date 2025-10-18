---
id: 20251012-12271109
title: "Internal App Distribution / Внутреннее распространение приложения"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-memory-leaks-definition--android--easy, q-recyclerview-viewtypes-delegation--recyclerview--medium, q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]
created: 2025-10-15
tags: [Kotlin, Distribution, Testing, Firebase, difficulty/medium]
---

# Question (EN)

> Explain internal app distribution strategies for beta testing and QA. How do you use Firebase App Distribution, Google Play Internal Testing, and enterprise distribution tools? What are best practices for managing test groups, collecting feedback, and automating distribution?

# Вопрос (RU)

> Объясните стратегии внутреннего распространения приложения для beta-тестирования и QA. Как использовать Firebase App Distribution, Google Play Internal Testing и корпоративные инструменты? Лучшие практики для управления группами тестирования, сбора обратной связи и автоматизации распространения?

## Answer (EN)

Internal app distribution enables rapid iteration with beta testers and QA teams before public release, using various platforms and automation strategies to streamline the testing process.

#### Firebase App Distribution

**1. Setup and Configuration**

```kotlin
// build.gradle.kts (project level)
buildscript {
    dependencies {
        classpath("com.google.firebase:firebase-appdistribution-gradle:4.0.1")
    }
}

// build.gradle.kts (app level)
plugins {
    id("com.google.firebase.appdistribution")
}

android {
    buildTypes {
        debug {
            firebaseAppDistribution {
                artifactType = "APK"
                releaseNotesFile = "release-notes/debug.txt"
                groups = "qa-team, internal-testers"
                serviceCredentialsFile = "firebase-service-account.json"
            }
        }

        create("qa") {
            initWith(getByName("debug"))
            applicationIdSuffix = ".qa"
            versionNameSuffix = "-qa"

            firebaseAppDistribution {
                artifactType = "APK"
                releaseNotes = generateReleaseNotes()
                groups = "qa-team"
                testers = "qa@example.com, lead@example.com"
            }
        }

        create("staging") {
            initWith(getByName("release"))
            matchingFallbacks += listOf("release")
            applicationIdSuffix = ".staging"
            versionNameSuffix = "-staging"

            firebaseAppDistribution {
                artifactType = "AAB"
                releaseNotesFile = "release-notes/staging.txt"
                groups = "beta-testers, stakeholders"
            }
        }
    }
}

fun generateReleaseNotes(): String {
    return buildString {
        appendLine("Build: ${getBuildNumber()}")
        appendLine("Commit: ${getGitCommitHash()}")
        appendLine("Branch: ${getGitBranch()}")
        appendLine()
        appendLine("Changes:")
        appendLine(getRecentCommits())
    }
}

fun getBuildNumber(): String {
    return System.getenv("BUILD_NUMBER") ?: "local"
}

fun getGitCommitHash(): String {
    return Runtime.getRuntime()
        .exec("git rev-parse --short HEAD")
        .inputStream
        .bufferedReader()
        .readText()
        .trim()
}

fun getGitBranch(): String {
    return Runtime.getRuntime()
        .exec("git rev-parse --abbrev-ref HEAD")
        .inputStream
        .bufferedReader()
        .readText()
        .trim()
}

fun getRecentCommits(): String {
    return Runtime.getRuntime()
        .exec("git log --oneline -5")
        .inputStream
        .bufferedReader()
        .readText()
        .trim()
}
```

**2. Gradle Tasks for Distribution**

```kotlin
// Custom Gradle tasks
tasks.register("distributeToQa") {
    group = "distribution"
    description = "Build and distribute QA build to Firebase"

    dependsOn("assembleQa")
    finalizedBy("appDistributionUploadQa")

    doLast {
        println(" QA build distributed successfully")
        println("Testers will receive notification via email")
    }
}

tasks.register("distributeToStaging") {
    group = "distribution"
    description = "Build and distribute Staging build to Firebase"

    dependsOn("bundleStaging")
    finalizedBy("appDistributionUploadStaging")

    doLast {
        println(" Staging build distributed successfully")
    }
}

// Automated distribution on successful build
tasks.named("assembleQa").configure {
    doLast {
        if (project.hasProperty("autoDistribute")) {
            tasks.named("appDistributionUploadQa").get().exec()
        }
    }
}
```

**3. CI/CD Integration**

```yaml
# .github/workflows/firebase-distribution.yml
name: Firebase App Distribution

on:
    push:
        branches:
            - develop
            - staging

jobs:
    distribute:
        runs-on: ubuntu-latest

        steps:
            - uses: actions/checkout@v4
              with:
                  fetch-depth: 0 # Full history for git commands

            - name: Set up JDK 17
              uses: actions/setup-java@v4
              with:
                  java-version: "17"
                  distribution: "temurin"

            - name: Decode keystore
              run: |
                  echo "${{ secrets.DEBUG_KEYSTORE_BASE64 }}" | base64 -d > debug.keystore

            - name: Generate release notes
              id: release_notes
              run: |
                  echo "RELEASE_NOTES<<EOF" >> $GITHUB_OUTPUT
                  echo "Build: ${{ github.run_number }}" >> $GITHUB_OUTPUT
                  echo "Commit: ${GITHUB_SHA::7}" >> $GITHUB_OUTPUT
                  echo "Branch: ${GITHUB_REF#refs/heads/}" >> $GITHUB_OUTPUT
                  echo "" >> $GITHUB_OUTPUT
                  echo "Recent changes:" >> $GITHUB_OUTPUT
                  git log --oneline -5 >> $GITHUB_OUTPUT
                  echo "EOF" >> $GITHUB_OUTPUT

            - name: Build Debug APK
              if: github.ref == 'refs/heads/develop'
              run: ./gradlew assembleDebug

            - name: Build Staging APK
              if: github.ref == 'refs/heads/staging'
              run: ./gradlew assembleStaging

            - name: Upload to Firebase App Distribution
              uses: wzieba/Firebase-Distribution-Github-Action@v1
              with:
                  appId: ${{ secrets.FIREBASE_APP_ID }}
                  serviceCredentialsFileContent: ${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
                  groups: qa-team, internal-testers
                  file: app/build/outputs/apk/debug/app-debug.apk
                  releaseNotes: ${{ steps.release_notes.outputs.RELEASE_NOTES }}

            - name: Post to Slack
              uses: slackapi/slack-github-action@v1
              with:
                  payload: |
                      {
                        "text": "New build available!",
                        "blocks": [
                          {
                            "type": "section",
                            "text": {
                              "type": "mrkdwn",
                              "text": " *New Build Distributed*\n*Branch:* ${{ github.ref }}\n*Build:* #${{ github.run_number }}\n*Commit:* ${GITHUB_SHA::7}"
                            }
                          }
                        ]
                      }
              env:
                  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**4. In-App Feedback Collection**

```kotlin
@Singleton
class FeedbackManager @Inject constructor(
    private val context: Context,
    private val firestore: FirebaseFirestore,
    private val crashlytics: FirebaseCrashlytics
) {
    fun submitFeedback(
        feedback: Feedback,
        screenshot: Bitmap? = null,
        onSuccess: () -> Unit,
        onError: (Exception) -> Unit
    ) {
        viewModelScope.launch {
            try {
                val feedbackData = hashMapOf(
                    "message" to feedback.message,
                    "type" to feedback.type.name,
                    "rating" to feedback.rating,
                    "email" to feedback.userEmail,
                    "timestamp" to FieldValue.serverTimestamp(),
                    "deviceInfo" to getDeviceInfo(),
                    "appVersion" to BuildConfig.VERSION_NAME,
                    "buildNumber" to BuildConfig.VERSION_CODE,
                    "userId" to getUserId()
                )

                // Upload screenshot if provided
                screenshot?.let { bitmap ->
                    val screenshotUrl = uploadScreenshot(bitmap)
                    feedbackData["screenshot"] = screenshotUrl
                }

                // Add to Firestore
                firestore.collection("feedback")
                    .add(feedbackData)
                    .addOnSuccessListener { documentRef ->
                        Log.d(TAG, "Feedback submitted: ${documentRef.id}")

                        // Log to Crashlytics for visibility
                        crashlytics.log("Feedback submitted: ${feedback.type}")
                        crashlytics.setCustomKey("feedback_id", documentRef.id)

                        onSuccess()
                    }
                    .addOnFailureListener { exception ->
                        Log.e(TAG, "Failed to submit feedback", exception)
                        onError(exception)
                    }
            } catch (e: Exception) {
                onError(e)
            }
        }
    }

    private suspend fun uploadScreenshot(bitmap: Bitmap): String = withContext(Dispatchers.IO) {
        val storage = FirebaseStorage.getInstance()
        val ref = storage.reference
            .child("feedback-screenshots/${UUID.randomUUID()}.jpg")

        val baos = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 80, baos)
        val data = baos.toByteArray()

        val uploadTask = ref.putBytes(data).await()
        ref.downloadUrl.await().toString()
    }

    private fun getDeviceInfo(): Map<String, Any> {
        return mapOf(
            "manufacturer" to Build.MANUFACTURER,
            "model" to Build.MODEL,
            "androidVersion" to Build.VERSION.RELEASE,
            "sdkInt" to Build.VERSION.SDK_INT,
            "brand" to Build.BRAND,
            "device" to Build.DEVICE,
            "screenDensity" to context.resources.displayMetrics.densityDpi,
            "screenWidth" to context.resources.displayMetrics.widthPixels,
            "screenHeight" to context.resources.displayMetrics.heightPixels
        )
    }

    companion object {
        private const val TAG = "FeedbackManager"
    }
}

data class Feedback(
    val message: String,
    val type: FeedbackType,
    val rating: Int? = null,
    val userEmail: String? = null
)

enum class FeedbackType {
    BUG_REPORT,
    FEATURE_REQUEST,
    GENERAL_FEEDBACK,
    UI_UX_ISSUE,
    PERFORMANCE_ISSUE
}
```

**5. In-App Feedback UI**

```kotlin
@Composable
fun FeedbackDialog(
    onDismiss: () -> Unit,
    onSubmit: (Feedback, Bitmap?) -> Unit
) {
    var message by remember { mutableStateOf("") }
    var feedbackType by remember { mutableStateOf(FeedbackType.GENERAL_FEEDBACK) }
    var rating by remember { mutableStateOf(3) }
    var email by remember { mutableStateOf("") }
    var includeScreenshot by remember { mutableStateOf(false) }
    var screenshot by remember { mutableStateOf<Bitmap?>(null) }

    val context = LocalContext.current

    // Capture screenshot when dialog opens
    LaunchedEffect(includeScreenshot) {
        if (includeScreenshot && screenshot == null) {
            screenshot = captureScreenshot(context)
        }
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text("Send Feedback")
        },
        text = {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
            ) {
                // Feedback type selector
                Text("Feedback Type", style = MaterialTheme.typography.labelLarge)
                Spacer(modifier = Modifier.height(8.dp))

                FeedbackType.values().forEach { type ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { feedbackType = type }
                            .padding(vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = feedbackType == type,
                            onClick = { feedbackType = type }
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(type.name.replace('_', ' '))
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Message input
                OutlinedTextField(
                    value = message,
                    onValueChange = { message = it },
                    label = { Text("Your feedback") },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 4,
                    maxLines = 8
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Rating (optional)
                if (feedbackType == FeedbackType.GENERAL_FEEDBACK) {
                    Text("Rating", style = MaterialTheme.typography.labelLarge)
                    Slider(
                        value = rating.toFloat(),
                        onValueChange = { rating = it.toInt() },
                        valueRange = 1f..5f,
                        steps = 3
                    )
                    Text("$rating / 5")

                    Spacer(modifier = Modifier.height(16.dp))
                }

                // Email (optional)
                OutlinedTextField(
                    value = email,
                    onValueChange = { email = it },
                    label = { Text("Email (optional)") },
                    modifier = Modifier.fillMaxWidth(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email)
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Screenshot option
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(
                        checked = includeScreenshot,
                        onCheckedChange = { includeScreenshot = it }
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Include screenshot")
                }

                if (includeScreenshot && screenshot != null) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Image(
                        bitmap = screenshot!!.asImageBitmap(),
                        contentDescription = "Screenshot preview",
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(150.dp),
                        contentScale = ContentScale.Fit
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Build info
                Text(
                    text = "Build: ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = {
                    val feedback = Feedback(
                        message = message,
                        type = feedbackType,
                        rating = if (feedbackType == FeedbackType.GENERAL_FEEDBACK) rating else null,
                        userEmail = email.takeIf { it.isNotBlank() }
                    )
                    onSubmit(feedback, if (includeScreenshot) screenshot else null)
                    onDismiss()
                },
                enabled = message.isNotBlank()
            ) {
                Text("Submit")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}

private fun captureScreenshot(context: Context): Bitmap? {
    val activity = context.findActivity() ?: return null
    val view = activity.window.decorView.rootView

    view.isDrawingCacheEnabled = true
    val bitmap = Bitmap.createBitmap(view.drawingCache)
    view.isDrawingCacheEnabled = false

    return bitmap
}

private fun Context.findActivity(): Activity? {
    var context = this
    while (context is ContextWrapper) {
        if (context is Activity) return context
        context = context.baseContext
    }
    return null
}
```

#### Google Play Internal Testing

**1. Play Console API Integration**

```kotlin
// Upload APK/AAB to Internal Testing track
class PlayConsoleUploader @Inject constructor(
    private val serviceAccountKey: String
) {
    private val transport = NetHttpTransport()
    private val jsonFactory = GsonFactory.getDefaultInstance()

    fun uploadToInternalTesting(
        packageName: String,
        apkFile: File,
        releaseNotes: String
    ) {
        val credential = GoogleCredential.fromStream(
            serviceAccountKey.byteInputStream(),
            transport,
            jsonFactory
        ).createScoped(AndroidPublisherScopes.all())

        val publisher = AndroidPublisher.Builder(transport, jsonFactory, credential)
            .setApplicationName("AppDistributionTool")
            .build()

        // Create edit
        val edit = publisher.edits().insert(packageName, null).execute()
        val editId = edit.id

        try {
            // Upload APK
            val apkUpload = publisher.edits().apks()
                .upload(packageName, editId, FileContent("application/vnd.android.package-archive", apkFile))
                .execute()

            val versionCode = apkUpload.versionCode

            // Assign to internal testing track
            val track = Track().apply {
                this.track = "internal"
                releases = listOf(
                    TrackRelease().apply {
                        this.versionCodes = listOf(versionCode.toLong())
                        this.status = "completed"
                        this.releaseNotes = listOf(
                            LocalizedText().apply {
                                language = "en-US"
                                text = releaseNotes
                            }
                        )
                    }
                )
            }

            publisher.edits().tracks()
                .update(packageName, editId, "internal", track)
                .execute()

            // Commit the edit
            publisher.edits().commit(packageName, editId).execute()

            println(" Successfully uploaded to Internal Testing track")
        } catch (e: Exception) {
            // Abort edit on failure
            publisher.edits().delete(packageName, editId).execute()
            throw e
        }
    }
}
```

#### Enterprise Distribution (MDM)

**1. Managed Google Play**

```kotlin
// Enterprise app configuration
class EnterpriseManagedConfig {
    companion object {
        // res/xml/managed_configurations.xml
        const val MANAGED_CONFIG_TEMPLATE = """
            <managed-configurations xmlns:android="http://schemas.android.com/apk/res/android">
                <bundle-array android:key="vpn_configurations">
                    <bundle>
                        <string android:key="server_url" />
                        <integer android:key="port" android:defaultValue="443" />
                        <boolean android:key="use_ssl" android:defaultValue="true" />
                    </bundle>
                </bundle-array>

                <string android:key="api_endpoint" />
                <boolean android:key="enable_debug_mode" android:defaultValue="false" />
                <choice android:key="log_level" android:defaultValue="INFO">
                    <item android:value="DEBUG">Debug</item>
                    <item android:value="INFO">Info</item>
                    <item android:value="WARN">Warning</item>
                    <item android:value="ERROR">Error</item>
                </choice>
            </managed-configurations>
        """
    }

    fun readManagedConfigurations(context: Context): Bundle? {
        val restrictionsManager = context.getSystemService(Context.RESTRICTIONS_SERVICE) as? RestrictionsManager
        return restrictionsManager?.applicationRestrictions
    }

    fun applyManagedConfigurations(context: Context) {
        val config = readManagedConfigurations(context) ?: return

        // Apply enterprise configurations
        val apiEndpoint = config.getString("api_endpoint")
        val debugMode = config.getBoolean("enable_debug_mode", false)
        val logLevel = config.getString("log_level", "INFO")

        // Save to app preferences
        context.getSharedPreferences("enterprise_config", Context.MODE_PRIVATE)
            .edit()
            .putString("api_endpoint", apiEndpoint)
            .putBoolean("debug_mode", debugMode)
            .putString("log_level", logLevel)
            .apply()

        Log.d("EnterpriseManagedConfig", "Applied managed configurations")
    }
}
```

**2. AppConfig for MDM**

```xml
<!-- res/xml/app_restrictions.xml -->
<restrictions xmlns:android="http://schemas.android.com/apk/res/android">
    <restriction
        android:key="server_url"
        android:title="Server URL"
        android:restrictionType="string"
        android:description="Backend API server URL"
        android:defaultValue="https://api.example.com" />

    <restriction
        android:key="require_authentication"
        android:title="Require Authentication"
        android:restrictionType="bool"
        android:defaultValue="true" />

    <restriction
        android:key="allowed_domains"
        android:title="Allowed Domains"
        android:restrictionType="multi-select"
        android:description="List of allowed email domains for sign-in">
        <choice
            android:key="example.com"
            android:title="example.com" />
        <choice
            android:key="company.com"
            android:title="company.com" />
    </restriction>

    <restriction
        android:key="session_timeout"
        android:title="Session Timeout (minutes)"
        android:restrictionType="integer"
        android:defaultValue="30" />
</restrictions>
```

**3. MDM Detection and Compliance**

```kotlin
@Singleton
class MdmComplianceChecker @Inject constructor(
    private val context: Context
) {
    fun isDeviceManaged(): Boolean {
        val devicePolicyManager = context.getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        return devicePolicyManager.isDeviceOwnerApp(context.packageName) ||
                devicePolicyManager.isProfileOwnerApp(context.packageName)
    }

    fun getDeviceOwnerPackage(): String? {
        val devicePolicyManager = context.getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            devicePolicyManager.deviceOwnerComponentOnAnyUser?.packageName
        } else {
            null
        }
    }

    fun enforceCompliance(): ComplianceResult {
        val devicePolicyManager = context.getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager

        val issues = mutableListOf<String>()

        // Check encryption
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (devicePolicyManager.storageEncryptionStatus != DevicePolicyManager.ENCRYPTION_STATUS_ACTIVE) {
                issues.add("Device storage is not encrypted")
            }
        }

        // Check screen lock
        if (!devicePolicyManager.isActivePasswordSufficient) {
            issues.add("Screen lock does not meet requirements")
        }

        // Check if debug mode is enabled
        if (Settings.Global.getInt(context.contentResolver, Settings.Global.DEVELOPMENT_SETTINGS_ENABLED, 0) == 1) {
            issues.add("Developer options enabled")
        }

        return ComplianceResult(
            isCompliant = issues.isEmpty(),
            issues = issues
        )
    }
}

data class ComplianceResult(
    val isCompliant: Boolean,
    val issues: List<String>
)
```

#### Best Practices

1. **Firebase App Distribution**:

    - Automate distribution from CI/CD
    - Use groups for different tester segments
    - Generate meaningful release notes
    - Set up Slack/Teams notifications
    - Monitor download and feedback metrics

2. **Test Group Management**:

    - Segment testers (QA, beta, internal, stakeholders)
    - Rotate testers to avoid feedback bias
    - Limit group sizes for focused feedback
    - Provide clear testing guidelines
    - Set expectations for response time

3. **Feedback Collection**:

    - Make feedback easy (in-app, shake to report)
    - Include screenshots automatically
    - Capture device and build information
    - Categorize feedback (bug, feature, UX)
    - Follow up with testers

4. **Release Notes**:

    - Auto-generate from git commits
    - Include build number and commit hash
    - Highlight breaking changes
    - Mention known issues
    - Link to detailed changelog

5. **Security**:
    - Protect service account credentials
    - Use short-lived access tokens
    - Restrict distribution to trusted testers
    - Monitor unauthorized redistributions
    - Remove debug features in production

#### Common Pitfalls

1. **No Automation**: Manual distribution is slow and error-prone
2. **Poor Release Notes**: Testers don't know what to test
3. **No Feedback Mechanism**: Can't collect structured feedback
4. **Mixing Test Groups**: Confusing feedback from different audiences
5. **No Version Control**: Can't track which build has which fixes
6. **Ignored Feedback**: Testers lose motivation

### Summary

Internal app distribution enables rapid iteration and quality assurance:

-   **Firebase App Distribution**: Automated distribution to testers
-   **Google Play Internal Testing**: Pre-release testing track
-   **Enterprise MDM**: Managed app configuration
-   **In-App Feedback**: Structured feedback collection
-   **CI/CD Integration**: Automated build and distribution

Key considerations: automation, segmented test groups, meaningful release notes, easy feedback mechanisms, and comprehensive monitoring.

---

# Вопрос (RU)

> Объясните стратегии внутреннего распространения приложений для бета-тестирования и QA. Как использовать Firebase App Distribution, Google Play Internal Testing и enterprise инструменты распространения? Каковы best practices для управления группами тестировщиков, сбора feedback и автоматизации распространения?

## Ответ (RU)

Внутреннее распространение приложений позволяет быструю итерацию с бета-тестировщиками и QA командами до публичного релиза, используя различные платформы и стратегии автоматизации.

#### Firebase App Distribution

**Преимущества**:

-   Быстрое распространение APK/AAB
-   Email/ссылка для тестировщиков
-   Интеграция с CI/CD
-   Автоматические уведомления
-   Сбор crash reports

**Функции**:

-   Группы тестировщиков
-   Release notes
-   Gradle plugin для автоматизации
-   Интеграция с Crashlytics

#### Google Play Internal Testing

**Преимущества**:

-   Официальный Play Store трек
-   До 100 тестировщиков
-   Мгновенный доступ
-   Нет review процесса
-   Pre-launch reports

**Use Cases**:

-   Ежедневные builds
-   QA тестирование
-   Быстрая итерация
-   Stakeholder previews

#### Enterprise Distribution (MDM)

**Managed Google Play**:

-   Managed configurations
-   AppConfig стандарт
-   Device policy enforcement
-   Enterprise catalog

**Compliance**:

-   Проверка шифрования
-   Screen lock требования
-   Developer options detection
-   Managed app restrictions

#### In-App Feedback

**Функции**:

-   Shake to report
-   Screenshot capture
-   Device info автоматически
-   Categorized feedback
-   Email follow-up

**Интеграция**:

-   Firestore для хранения
-   Crashlytics logging
-   Slack notifications
-   Jira ticket creation

#### Автоматизация

**CI/CD Integration**:

-   GitHub Actions
-   GitLab CI
-   Jenkins
-   Bitrise

**Процесс**:

1. Commit → Build
2. Auto-generate release notes
3. Upload to Firebase/Play Console
4. Notify testers (Slack/Email)
5. Collect feedback

#### Best Practices

1. **Test Groups**:

    - Сегментация (QA, beta, internal, stakeholders)
    - Четкие guidelines
    - Rotation для избежания bias
    - Ограниченный размер групп

2. **Release Notes**:

    - Auto-generate из git
    - Build number + commit hash
    - Highlight breaking changes
    - Known issues
    - Ссылка на детальный changelog

3. **Feedback**:

    - Легкий доступ (in-app)
    - Auto-capture screenshots
    - Категоризация
    - Follow-up

4. **Security**:
    - Защита credentials
    - Short-lived tokens
    - Restricted distribution
    - Мониторинг unauthorized redistribution

### Резюме

Внутреннее распространение обеспечивает быструю итерацию:

-   **Firebase App Distribution**: Автоматизированное распространение
-   **Google Play Internal Testing**: Pre-release трек
-   **Enterprise MDM**: Managed конфигурация
-   **In-App Feedback**: Структурированный сбор отзывов
-   **CI/CD Integration**: Автоматизированный build и distribution

Ключевые моменты: автоматизация, сегментированные группы, meaningful release notes, легкий feedback, comprehensive monitoring.

---

## Related Questions

### Related (Medium)

-   [[q-app-store-optimization--distribution--medium]] - Distribution
-   [[q-alternative-distribution--distribution--medium]] - Distribution
-   [[q-play-store-publishing--distribution--medium]] - Distribution
-   [[q-android-app-bundles--android--easy]] - Distribution
