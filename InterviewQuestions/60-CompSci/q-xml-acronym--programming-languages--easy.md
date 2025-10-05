---
id: 20251003141211
title: XML acronym / Расшифровка XML
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, xml]
question_kind: practical
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/1400
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-xml
  - c-data-formats

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [xml, markup-language, acronym, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> How is XML deciphered

# Вопрос (RU)
> Как расшифровывается xml

---

## Answer (EN)

**XML** stands for **eXtensible Markup Language** (Расширяемый язык разметки).

### Key Characteristics

**1. Extensible:**
- You can define your own tags
- Not limited to predefined set (unlike HTML)

```xml
<!-- Custom tags -->
<user>
    <name>John Doe</name>
    <email>john@example.com</email>
</user>
```

**2. Markup Language:**
- Uses tags to structure data
- Self-describing format
- Both human and machine readable

**3. Common Uses:**
- Configuration files (Android layouts, Maven pom.xml)
- Data exchange between systems
- Document storage
- Web services (SOAP)

### XML Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<library>
    <book id="1">
        <title>Clean Code</title>
        <author>Robert Martin</author>
        <year>2008</year>
    </book>
    <book id="2">
        <title>Effective Java</title>
        <author>Joshua Bloch</author>
        <year>2018</year>
    </book>
</library>
```

### Android Context

In Android development, XML is heavily used:

**Layout files:**
```xml
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:text="Hello World"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content" />
</LinearLayout>
```

**Resources:**
```xml
<!-- strings.xml -->
<resources>
    <string name="app_name">MyApp</string>
    <string name="welcome">Welcome!</string>
</resources>
```

**Manifest:**
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:label="@string/app_name">
        <activity android:name=".MainActivity" />
    </application>
</manifest>
```

### XML vs JSON

| Feature | XML | JSON |
|---------|-----|------|
| **Syntax** | Tag-based | Key-value pairs |
| **Verbosity** | More verbose | More compact |
| **Attributes** | Supports attributes | No attributes |
| **Arrays** | More complex | Native support |
| **Comments** | Supports `<!-- -->` | No comments |
| **Use case** | Config files, docs | Web APIs, data transfer |

**Same data in both formats:**

```xml
<!-- XML -->
<person>
    <name>John</name>
    <age>30</age>
</person>
```

```json
// JSON
{
  "name": "John",
  "age": 30
}
```

## Ответ (RU)

XML — это eXtensible Markup Language (Расширяемый язык разметки).

---

## Follow-ups
- What is the difference between XML and HTML?
- How to parse XML in Kotlin?
- What are XML namespaces?

## References
- [[c-xml]]
- [[c-data-formats]]
- [[moc-kotlin]]

## Related Questions
- [[q-json-vs-xml--programming-languages--easy]]
- [[q-android-xml-layouts--android--easy]]
