---
id: ivm-20251012-140500
title: Tools — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-12
tags: [moc, topic/tools]
---

# Tools — Map of Content

## Overview
This MOC covers development tools including version control (Git), build systems, CI/CD, IDEs, command-line tools, debugging tools, profiling tools, and other essential developer productivity tools.

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "80-Tools"
WHERE difficulty = "easy"
SORT file.name ASC
LIMIT 50
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "80-Tools"
WHERE difficulty = "medium"
SORT file.name ASC
LIMIT 50
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "80-Tools"
WHERE difficulty = "hard"
SORT file.name ASC
LIMIT 50
```

## By Subtopic

### Git & Version Control
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "git") OR contains(tags, "version-control") OR contains(subtopics, "git") OR contains(file.name, "git")
SORT difficulty ASC, file.name ASC
```

### Build Systems
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "gradle") OR contains(tags, "maven") OR contains(tags, "build-systems") OR contains(tags, "build-tools")
SORT difficulty ASC, file.name ASC
```

### CI/CD
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "ci-cd") OR contains(tags, "continuous-integration") OR contains(tags, "deployment")
SORT difficulty ASC, file.name ASC
```

### IDEs & Editors
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "ide") OR contains(tags, "android-studio") OR contains(tags, "intellij")
SORT difficulty ASC, file.name ASC
```

### Command-Line Tools
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "cli") OR contains(tags, "command-line") OR contains(tags, "terminal")
SORT difficulty ASC, file.name ASC
```

### Debugging & Profiling
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "debugging") OR contains(tags, "profiling") OR contains(tags, "performance-tools")
SORT difficulty ASC, file.name ASC
```

### Testing Tools
```dataview
TABLE difficulty, status
FROM "80-Tools"
WHERE contains(tags, "testing-tools") OR contains(tags, "test-frameworks")
SORT difficulty ASC, file.name ASC
```

## All Questions
```dataview
TABLE difficulty, subtopics, status, tags
FROM "80-Tools"
SORT difficulty ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM "80-Tools"
GROUP BY difficulty
SORT difficulty ASC
```

## Related MOCs
- [[moc-android]]
- [[moc-backend]]
- [[moc-kotlin]]
