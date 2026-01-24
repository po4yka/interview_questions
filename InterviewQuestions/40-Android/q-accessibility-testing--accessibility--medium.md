---
id: android-acc-005
title: Accessibility Testing Tools / Instrumenty testirovaniya dostupnosti
aliases: [Accessibility Testing, Accessibility Scanner, Testirovanie dostupnosti]
topic: android
subtopics: [accessibility, testing]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, q-content-descriptions--accessibility--medium, q-talkback-support--accessibility--medium, q-testing-compose-ui--android--medium]
created: 2026-01-23
updated: 2026-01-23
tags: [android/accessibility, android/testing, difficulty/medium, accessibility, testing]

---
# Vopros (RU)
> Kakie instrumenty suschestvuyut dlya testirovaniya dostupnosti Android-prilozhenij?

# Question (EN)
> What tools exist for testing accessibility in Android applications?

---

## Otvet (RU)

Testirovanie dostupnosti vklyuchaet ruchnuyu proverku s TalkBack, avtomaticheskie skanery i programmnye testy. Kompleksnyj podkhod obespechibaet maksimal'nuyu dostupnost'.

### 1. Accessibility Scanner (Google)

Besplatnoe prilozhenie ot Google dlya avtomaticheskogo analiza UI.

**Ustanovka i ispol'zovanie:**
1. Skazhat' iz Google Play: "Accessibility Scanner"
2. Vklyuchit' v Nastrojkakh > Spetsdostup
3. Otkryt' prilozhenie dlya testirovaniya
4. Nazhat' knopku skanirovaniya (plavayuschaya knopka)

**Chto proveryaet:**
| Proverka | Opisanie |
|----------|----------|
| Touch target size | Minimum 48x48dp dlya interaktivnykh elementov |
| Color contrast | Koeffitsient kontrasta teksta k fonu (minimum 4.5:1) |
| Content labels | Nalichie contentDescription |
| Duplicate clickable | Vlozhennye klikabel'nye elementy |
| Text scaling | Podderzhka uvelicheniya teksta |

**Ogranicheniya:**
- Ne proveryaet logiku navigatsii TalkBack
- Ne testiruet dinamicheskie izmeneniya
- Trebuet ruchnaya proverka dlya custom controls

### 2. Ruchnoe testirovanie s TalkBack

**Vklyuchenie TalkBack:**
```
Nastrojki > Spetsdostup > TalkBack > Vklyuchit'
```

**Osnovnye zhesty:**
| Zhest | Dejstvie |
|-------|----------|
| Provesti vpravo | Sleduyuschij element |
| Provesti vlevo | Predyduschij element |
| Dvojnoj tap | Aktivirovat' |
| Dvojnoj tap i uderzhat' | Kontekst (dolgoye nazhatie) |
| Provesti vverkh/vniz | Izmenenie navigatsii |
| Tri pal'tsa tap | Menyu TalkBack |

**Chek-list ruchnogo testirovaniya:**
- [ ] Vse interaktivnye elementy imeyut opisaniya
- [ ] Poryadok fokusa logichnyj
- [ ] Dinamicheskie obnovleniya ob"yavlyayutsya
- [ ] Modal'nye okna uderzhivayut fokus
- [ ] Net lovushek fokusa (focus traps)
- [ ] Custom controls polnost'yu dostupny

### 3. Espresso Accessibility Checks

```kotlin
// Vklyuchenie proverki dostupnosti v Espresso
@RunWith(AndroidJUnit4::class)
class AccessibilityTest {

    @Before
    fun setUp() {
        // Vklyuchit' accessibility proverki
        AccessibilityChecks.enable()
            .setRunChecksFromRootView(true)
            .setThrowExceptionFor(AccessibilityCheckResult.AccessibilityCheckResultType.ERROR)
    }

    @Test
    fun mainScreen_meetsAccessibilityGuidelines() {
        // Lyuboe vzaimodejstvie s UI avtomaticheski
        // proveryaet dostupnost'
        onView(withId(R.id.loginButton))
            .perform(click())

        // Accessibility proverki vypolnyatsya avtomaticheski
    }

    @Test
    fun profileScreen_hasValidTouchTargets() {
        ActivityScenario.launch(ProfileActivity::class.java)

        onView(withId(R.id.settingsIcon))
            .check(matches(isDisplayed()))

        // Avtomaticheskaya proverka touch target >= 48dp
    }
}
```

### 4. Compose Accessibility Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class ComposeAccessibilityTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun button_hasContentDescription() {
        composeTestRule.setContent {
            SendButton(onClick = {})
        }

        composeTestRule
            .onNodeWithContentDescription("Otpravit' soobschenie")
            .assertExists()
            .assertHasClickAction()
    }

    @Test
    fun listItem_hasMergedSemantics() {
        composeTestRule.setContent {
            UserListItem(
                name = "Ivan Petrov",
                status = "Online"
            )
        }

        // Proverit' chto elementy ob"edineny
        composeTestRule
            .onNodeWithText("Ivan Petrov")
            .onParent()
            .assertExists()
    }

    @Test
    fun touchTarget_meetsMinimumSize() {
        composeTestRule.setContent {
            IconButton(onClick = {}) {
                Icon(
                    Icons.Default.Favorite,
                    contentDescription = "Dobavit' v izbrannoe"
                )
            }
        }

        composeTestRule
            .onNodeWithContentDescription("Dobavit' v izbrannoe")
            .assertTouchHeightIsAtLeast(48.dp)
            .assertTouchWidthIsAtLeast(48.dp)
    }

    @Test
    fun heading_isMarkedCorrectly() {
        composeTestRule.setContent {
            Text(
                "Zagolovok sektsii",
                modifier = Modifier.semantics { heading() }
            )
        }

        composeTestRule
            .onNode(isHeading())
            .assertExists()
    }

    @Test
    fun customAction_isAvailable() {
        composeTestRule.setContent {
            ItemCard(
                onDelete = {},
                onShare = {}
            )
        }

        // Proverit' nalichie kastomnyh dejstvij
        composeTestRule
            .onNode(hasAnyDescendant(hasText("Item")))
            .assert(hasCustomAction("Udalit'"))
    }
}

// Vspomogatel'nye matchers
fun hasCustomAction(label: String): SemanticsMatcher =
    SemanticsMatcher("has custom action [$label]") { node ->
        node.config.getOrNull(SemanticsActions.CustomActions)
            ?.any { it.label == label } == true
    }
```

### 5. Layout Inspector dlya semantik

Android Studio Layout Inspector pokazyvaet semanticheskoe derevo:

1. **Zapustit' prilozhenie** na emulyatore ili ustrojstve
2. **Otkryt' Layout Inspector**: View > Tool Windows > Layout Inspector
3. **Vybrat' process** prilozheniia
4. **Pereyti na vkladku "Semantics"** (Compose)

**Chto mozhno uvidet':**
- Semanticheskoe derevo
- contentDescription kazhdogo elementa
- Merged nodes
- Roli i sostoyaniya

### 6. Lint proverki

```kotlin
// build.gradle.kts
android {
    lintOptions {
        // Vklyuchit' proverki dostupnosti
        enable("ContentDescription")
        enable("LabelFor")
        enable("ClickableViewAccessibility")

        // Sdelat' oshibkami (ne preduprezhdeniami)
        error("ContentDescription")
    }
}
```

**Osnovnye lint proverki:**
| Proverka | Opisanie |
|----------|----------|
| ContentDescription | ImageView bez opisaniya |
| LabelFor | EditText bez svyazannogo label |
| ClickableViewAccessibility | Clickable bez accessibility |
| DuplicateIds | Dublirovannye ID (problemy s navigation) |

### 7. Pre-launch otchet v Google Play Console

Google Play avtomaticheski testiruet dostupnost' pered publikatsiej:
- Otsutstvuyuschie content descriptions
- Malye touch targets
- Nizkij kontrast

**Gde najti:**
```
Google Play Console > Prilozhenie > Testing > Pre-launch report > Accessibility
```

### Kompleksnyj chek-list testirovaniya

| Etap | Instrument | Chto proveryaem |
|------|------------|-----------------|
| Razrabotka | Lint | Bazovye problemy v kode |
| Local testing | Layout Inspector | Semanticheskoe derevo |
| Manual testing | TalkBack | Pol'zovatel'skij opyt |
| Automated | Espresso/Compose tests | Regressii |
| Pre-release | Accessibility Scanner | Kompleksnaya proverka |
| Production | Play Console | Otchety pre-launch |

### Primer polnogo testa

```kotlin
@RunWith(AndroidJUnit4::class)
class FullAccessibilityTest {

    @get:Rule
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Before
    fun setup() {
        // Vklyuchit' accessibility checks dlya vsego testa
        AccessibilityChecks.enable()
    }

    @Test
    fun fullUserJourney_isAccessible() {
        // 1. Login screen
        composeTestRule
            .onNodeWithText("Email")
            .assertExists()
            .performTextInput("test@example.com")

        composeTestRule
            .onNodeWithText("Password")
            .performTextInput("password123")

        composeTestRule
            .onNodeWithContentDescription("Vojti")
            .assertIsEnabled()
            .performClick()

        // 2. Main screen
        composeTestRule.waitUntil(5000) {
            composeTestRule
                .onAllNodesWithTag("main_content")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // 3. Proverka navigatsii
        composeTestRule
            .onNodeWithContentDescription("Nastrojki")
            .assertExists()
            .assertHasClickAction()

        // 4. Proverka spiska
        composeTestRule
            .onAllNodesWithTag("list_item")
            .onFirst()
            .assert(hasContentDescription())
    }
}
```

---

## Answer (EN)

Accessibility testing includes manual verification with TalkBack, automated scanners, and programmatic tests. A comprehensive approach ensures maximum accessibility.

### 1. Accessibility Scanner (Google)

Free Google app for automated UI analysis.

**Installation and usage:**
1. Download from Google Play: "Accessibility Scanner"
2. Enable in Settings > Accessibility
3. Open the app to test
4. Tap the scan button (floating button)

**What it checks:**
| Check | Description |
|-------|-------------|
| Touch target size | Minimum 48x48dp for interactive elements |
| Color contrast | Text to background contrast ratio (minimum 4.5:1) |
| Content labels | Presence of contentDescription |
| Duplicate clickable | Nested clickable elements |
| Text scaling | Support for text enlargement |

**Limitations:**
- Doesn't verify TalkBack navigation logic
- Doesn't test dynamic changes
- Requires manual verification for custom controls

### 2. Manual Testing with TalkBack

**Enabling TalkBack:**
```
Settings > Accessibility > TalkBack > Enable
```

**Basic gestures:**
| Gesture | Action |
|---------|--------|
| Swipe right | Next element |
| Swipe left | Previous element |
| Double tap | Activate |
| Double tap and hold | Context (long press) |
| Swipe up/down | Change navigation mode |
| Three-finger tap | TalkBack menu |

**Manual testing checklist:**
- [ ] All interactive elements have descriptions
- [ ] Focus order is logical
- [ ] Dynamic updates are announced
- [ ] Modal dialogs trap focus correctly
- [ ] No focus traps
- [ ] Custom controls are fully accessible

### 3. Espresso Accessibility Checks

```kotlin
// Enabling accessibility checks in Espresso
@RunWith(AndroidJUnit4::class)
class AccessibilityTest {

    @Before
    fun setUp() {
        // Enable accessibility checks
        AccessibilityChecks.enable()
            .setRunChecksFromRootView(true)
            .setThrowExceptionFor(AccessibilityCheckResult.AccessibilityCheckResultType.ERROR)
    }

    @Test
    fun mainScreen_meetsAccessibilityGuidelines() {
        // Any UI interaction automatically
        // verifies accessibility
        onView(withId(R.id.loginButton))
            .perform(click())

        // Accessibility checks run automatically
    }

    @Test
    fun profileScreen_hasValidTouchTargets() {
        ActivityScenario.launch(ProfileActivity::class.java)

        onView(withId(R.id.settingsIcon))
            .check(matches(isDisplayed()))

        // Automatic check for touch target >= 48dp
    }
}
```

### 4. Compose Accessibility Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class ComposeAccessibilityTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun button_hasContentDescription() {
        composeTestRule.setContent {
            SendButton(onClick = {})
        }

        composeTestRule
            .onNodeWithContentDescription("Send message")
            .assertExists()
            .assertHasClickAction()
    }

    @Test
    fun listItem_hasMergedSemantics() {
        composeTestRule.setContent {
            UserListItem(
                name = "John Smith",
                status = "Online"
            )
        }

        // Verify elements are merged
        composeTestRule
            .onNodeWithText("John Smith")
            .onParent()
            .assertExists()
    }

    @Test
    fun touchTarget_meetsMinimumSize() {
        composeTestRule.setContent {
            IconButton(onClick = {}) {
                Icon(
                    Icons.Default.Favorite,
                    contentDescription = "Add to favorites"
                )
            }
        }

        composeTestRule
            .onNodeWithContentDescription("Add to favorites")
            .assertTouchHeightIsAtLeast(48.dp)
            .assertTouchWidthIsAtLeast(48.dp)
    }

    @Test
    fun heading_isMarkedCorrectly() {
        composeTestRule.setContent {
            Text(
                "Section heading",
                modifier = Modifier.semantics { heading() }
            )
        }

        composeTestRule
            .onNode(isHeading())
            .assertExists()
    }

    @Test
    fun customAction_isAvailable() {
        composeTestRule.setContent {
            ItemCard(
                onDelete = {},
                onShare = {}
            )
        }

        // Verify custom actions exist
        composeTestRule
            .onNode(hasAnyDescendant(hasText("Item")))
            .assert(hasCustomAction("Delete"))
    }
}

// Helper matchers
fun hasCustomAction(label: String): SemanticsMatcher =
    SemanticsMatcher("has custom action [$label]") { node ->
        node.config.getOrNull(SemanticsActions.CustomActions)
            ?.any { it.label == label } == true
    }
```

### 5. Layout Inspector for Semantics

Android Studio Layout Inspector shows the semantics tree:

1. **Run the app** on emulator or device
2. **Open Layout Inspector**: View > Tool Windows > Layout Inspector
3. **Select the process**
4. **Go to "Semantics" tab** (Compose)

**What you can see:**
- Semantics tree
- contentDescription of each element
- Merged nodes
- Roles and states

### 6. Lint Checks

```kotlin
// build.gradle.kts
android {
    lintOptions {
        // Enable accessibility checks
        enable("ContentDescription")
        enable("LabelFor")
        enable("ClickableViewAccessibility")

        // Make errors (not warnings)
        error("ContentDescription")
    }
}
```

**Main lint checks:**
| Check | Description |
|-------|-------------|
| ContentDescription | ImageView without description |
| LabelFor | EditText without associated label |
| ClickableViewAccessibility | Clickable without accessibility |
| DuplicateIds | Duplicate IDs (navigation issues) |

### 7. Pre-launch Report in Google Play Console

Google Play automatically tests accessibility before publishing:
- Missing content descriptions
- Small touch targets
- Low contrast

**Where to find:**
```
Google Play Console > App > Testing > Pre-launch report > Accessibility
```

### Comprehensive Testing Checklist

| Stage | Tool | What to verify |
|-------|------|----------------|
| Development | Lint | Basic code issues |
| Local testing | Layout Inspector | Semantics tree |
| Manual testing | TalkBack | User experience |
| Automated | Espresso/Compose tests | Regressions |
| Pre-release | Accessibility Scanner | Comprehensive check |
| Production | Play Console | Pre-launch reports |

### Full Test Example

```kotlin
@RunWith(AndroidJUnit4::class)
class FullAccessibilityTest {

    @get:Rule
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Before
    fun setup() {
        // Enable accessibility checks for entire test
        AccessibilityChecks.enable()
    }

    @Test
    fun fullUserJourney_isAccessible() {
        // 1. Login screen
        composeTestRule
            .onNodeWithText("Email")
            .assertExists()
            .performTextInput("test@example.com")

        composeTestRule
            .onNodeWithText("Password")
            .performTextInput("password123")

        composeTestRule
            .onNodeWithContentDescription("Sign in")
            .assertIsEnabled()
            .performClick()

        // 2. Main screen
        composeTestRule.waitUntil(5000) {
            composeTestRule
                .onAllNodesWithTag("main_content")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // 3. Navigation check
        composeTestRule
            .onNodeWithContentDescription("Settings")
            .assertExists()
            .assertHasClickAction()

        // 4. List check
        composeTestRule
            .onAllNodesWithTag("list_item")
            .onFirst()
            .assert(hasContentDescription())
    }
}
```

---

## Follow-ups

- How to integrate accessibility testing into CI/CD pipeline?
- What are common accessibility issues found by automated tools?
- How to create custom accessibility checks?
- How to handle accessibility testing for dynamic content?

## References

- Accessibility Testing: https://developer.android.com/guide/topics/ui/accessibility/testing
- Accessibility Scanner: https://support.google.com/accessibility/android/answer/6376570
- Espresso Accessibility: https://developer.android.com/training/testing/espresso/accessibility-checking
- Compose Testing: https://developer.android.com/develop/ui/compose/testing

## Related Questions

### Prerequisites
- [[q-testing-compose-ui--android--medium]] - Compose UI testing
- [[q-content-descriptions--accessibility--medium]] - Content descriptions

### Related
- [[q-talkback-support--accessibility--medium]] - TalkBack support
- [[q-compose-semantics--accessibility--medium]] - Semantics in Compose
- [[q-touch-target-size--accessibility--easy]] - Touch target size
