---
id: 'ivm-<% tp.date.now("YYYYMMDD-HHmmss") %>'
title: <%- tp.file.title %> — MOC
kind: moc
created: '<% tp.date.now("YYYY-MM-DD") %>'
updated: '<% tp.date.now("YYYY-MM-DD") %>'
tags: [moc]
date created: Friday, October 3rd 2025, 3:15:06 pm
date modified: Saturday, November 1st 2025, 5:43:22 pm
---

# Start Here
- ...

## Auto: by Difficulty (example)
```dataview
TABLE difficulty, file.link, subtopics
FROM "20-Algorithms"
WHERE difficulty = "easy"
SORT file.name ASC
```
