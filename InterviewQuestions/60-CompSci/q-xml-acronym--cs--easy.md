---
id: cs-007
title: "Xml Acronym / Расшифровка аббревиатуры XML"
aliases: ["XML Acronym", "Аббревиатура XML"]
topic: cs
subtopics: [data-format, fundamentals, markup-language]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-builder-pattern--design-patterns--medium, q-design-patterns-types--design-patterns--medium, q-factory-method-pattern--design-patterns--medium]
created: 2025-10-13
updated: 2025-01-25
tags: [data-format, difficulty/easy, fundamentals, markup-language, xml]
sources: [https://www.w3.org/XML/]
---

# Вопрос (RU)
> Как расшифровывается аббревиатура XML?

# Question (EN)
> How is XML acronym deciphered?

---

## Ответ (RU)

**Теория XML:**
XML - eXtensible Markup Language (Расширяемый язык разметки). Markup language - uses tags для structuring data, self-describing format, human и machine readable. Extensible - can define own tags, not limited к predefined set (unlike HTML).

**Определение:**

*Теория:* XML - text-based markup language для storing и transporting structured data. Key characteristics: tags-based syntax, attributes support, hierarchical structure, comments support `<!-- -->`. Widely used для: configuration files, data exchange, document storage, web services (SOAP).

```xml
// ✅ XML structure
<?xml version="1.0" encoding="UTF-8"?>
<library>
    <book id="1">
        <title>Clean Code</title>
        <author>Robert Martin</author>
        <year>2008</year>
    </book>
</library>
```

**Ключевые характеристики:**

**1. Extensible:**
*Теория:* You can define own tags, not limited к predefined set. Unlike HTML - HTML has fixed tags (div, p, span), XML allows custom tags для any domain.

```xml
// ✅ Custom tags
<user>
    <name>John Doe</name>
    <email>john@example.com</email>
</user>
```

**2. Markup Language:**
*Теория:* Uses tags для structuring data. Self-describing format - tags describe content meaning. Both human и machine readable - easy для humans, parsable для computers.

**3. Common Uses:**
*Теория:* XML used в: Configuration files (Android layouts, Maven pom.xml), Data exchange между systems, Document storage, Web services (SOAP), Android resources (strings.xml, AndroidManifest.xml).

```xml
// ✅ Android Layout (XML)
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

**XML vs JSON:**

*Теория:* Syntax differences, verbosity, attributes support, use cases. XML: verbose, supports attributes, comments, config files. JSON: compact, no attributes, no comments, web APIs.

| Feature | XML | JSON |
|---------|-----|------|
| Syntax | Tag-based | Key-value pairs |
| Verbosity | More verbose | More compact |
| Attributes | Supports attributes | No attributes |
| Comments | Supports `<!-- -->` | No comments |
| Use case | Config files, docs | Web APIs |

## Answer (EN)

**XML Theory:**
XML - eXtensible Markup Language. Markup language - uses tags for structuring data, self-describing format, human and machine readable. Extensible - can define own tags, not limited to predefined set (unlike HTML).

**Definition:**

*Theory:* XML - text-based markup language for storing and transporting structured data. Key characteristics: tags-based syntax, attributes support, hierarchical structure, comments support `<!-- -->`. Widely used for: configuration files, data exchange, document storage, web services (SOAP).

```xml
// ✅ XML structure
<?xml version="1.0" encoding="UTF-8"?>
<library>
    <book id="1">
        <title>Clean Code</title>
        <author>Robert Martin</author>
        <year>2008</year>
    </book>
</library>
```

**Key Characteristics:**

**1. Extensible:**
*Theory:* You can define own tags, not limited to predefined set. Unlike HTML - HTML has fixed tags (div, p, span), XML allows custom tags for any domain.

```xml
// ✅ Custom tags
<user>
    <name>John Doe</name>
    <email>john@example.com</email>
</user>
```

**2. Markup Language:**
*Theory:* Uses tags for structuring data. Self-describing format - tags describe content meaning. Both human and machine readable - easy for humans, parsable for computers.

**3. Common Uses:**
*Theory:* XML used in: Configuration files (Android layouts, Maven pom.xml), Data exchange between systems, Document storage, Web services (SOAP), Android resources (strings.xml, AndroidManifest.xml).

```xml
// ✅ Android Layout (XML)
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

**XML vs JSON:**

*Theory:* Syntax differences, verbosity, attributes support, use cases. XML: verbose, supports attributes, comments, config files. JSON: compact, no attributes, no comments, web APIs.

| Feature | XML | JSON |
|---------|-----|------|
| Syntax | Tag-based | Key-value pairs |
| Verbosity | More verbose | More compact |
| Attributes | Supports attributes | No attributes |
| Comments | Supports `<!-- -->` | No comments |
| Use case | Config files, docs | Web APIs |

---

## Follow-ups

- What is the difference between XML and JSON?
- How is XML used in Android development?
- What are XML parsers and how do they work?

## Related Questions

### Prerequisites (Easier)
- Basic data formats concepts
- Understanding of text-based data representation

### Related (Same Level)
- Data serialization formats
- Android resources and layouts
- Web API design
