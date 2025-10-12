# Interview Questions Knowledge Base

> **Comprehensive bilingual collection** of interview questions for Android, Kotlin, Computer Science, and more. Perfect for interview preparation from Junior to Staff+ levels.

---

## Vault Statistics

### Overall Metrics

```dataview
TABLE WITHOUT ID
    length(rows) as "Total Questions"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE topic
GROUP BY true
```

### By Topic

```dataview
TABLE WITHOUT ID
    topic as "Topic",
    length(rows) as "Count",
    round((length(filter(rows, (r) => r.difficulty = "easy")) / length(rows)) * 100) + "%" as "Easy",
    round((length(filter(rows, (r) => r.difficulty = "medium")) / length(rows)) * 100) + "%" as "Medium",
    round((length(filter(rows, (r) => r.difficulty = "hard")) / length(rows)) * 100) + "%" as "Hard"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE topic
GROUP BY topic
SORT length(rows) DESC
```

### By Difficulty

```dataview
TABLE WITHOUT ID
    difficulty as "Difficulty",
    length(rows) as "Count",
    round((length(rows) / 580) * 100) + "%" as "Percentage"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE difficulty
GROUP BY difficulty
SORT difficulty ASC
```

### By Status

```dataview
TABLE WITHOUT ID
    status as "Status",
    length(rows) as "Count",
    round((length(rows) / 580) * 100) + "%" as "Percentage"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE status
GROUP BY status
SORT length(rows) DESC
```
## Quick Links

### Documentation
- [Vault Documentation](00-Administration/README.md)
- [File Naming Rules](00-Administration/FILE-NAMING-RULES.md)
- [Import Progress Report](00-Administration/SOURCE-IMPORT-PROGRESS.md)

### Templates
- [Q&A Template](_templates/_tpl-qna.md)
- [Concept Template](_templates/_tpl-concept.md)
- [MOC Template](_templates/_tpl-moc.md)

### Reports
- [Complete Import Summary](00-Administration/COMPLETE-SOURCE-IMPORT-SUMMARY.md)
- [Quality Review Report](00-Administration/QUALITY-REVIEW-REPORT.md)

---

## Language Coverage

**All questions support**:
- English (EN)
- Russian (RU)

```dataview
TABLE WITHOUT ID
    "Bilingual Coverage" as "Metric",
    length(filter(rows, (r) => contains(r.language_tags, "en") AND contains(r.language_tags, "ru"))) as "Questions with EN+RU",
    round((length(filter(rows, (r) => contains(r.language_tags, "en") AND contains(r.language_tags, "ru"))) / length(rows)) * 100) + "%" as "Coverage"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE language_tags
GROUP BY true
```

---

## 🔗 Link Health Monitor

### Broken Links Detection

```dataviewjs
// Find all files with broken wikilinks
const files = dv.pages('"40-Android" or "70-Kotlin" or "60-CompSci" or "20-Algorithms" or "50-Backend" or "80-Tools" or "90-MOCs"')
    .where(p => p.file.path.endsWith('.md'));

let brokenLinks = [];
let totalLinks = 0;
let brokenCount = 0;

for (let file of files) {
    const content = await dv.io.load(file.file.path);
    if (!content) continue;

    // Find all wikilinks [[...]]
    const wikilinkRegex = /\[\[([^\]|]+)(\|[^\]]+)?\]\]/g;
    let match;

    while ((match = wikilinkRegex.exec(content)) !== null) {
        totalLinks++;
        const linkTarget = match[1].trim();

        // Check if target exists (try with and without .md extension)
        const targetExists = dv.page(linkTarget) ||
                           dv.page(linkTarget + '.md') ||
                           dv.pages().find(p => p.file.name === linkTarget);

        if (!targetExists) {
            brokenCount++;
            brokenLinks.push({
                source: file.file.name,
                target: linkTarget,
                path: file.file.path
            });
        }
    }
}

// Display results
dv.header(3, `📊 Summary`);
dv.paragraph(`**Total Links**: ${totalLinks} | **Broken**: ${brokenCount} | **Health**: ${Math.round((totalLinks - brokenCount) / totalLinks * 100)}%`);

if (brokenCount > 0) {
    dv.header(3, `❌ Broken Links (${brokenCount})`);

    // Group by source file
    const grouped = {};
    for (let link of brokenLinks) {
        if (!grouped[link.source]) {
            grouped[link.source] = [];
        }
        grouped[link.source].push(link.target);
    }

    // Display top 10 files with most broken links
    const sorted = Object.entries(grouped)
        .sort((a, b) => b[1].length - a[1].length)
        .slice(0, 10);

    dv.table(
        ["Source File", "Broken Links", "Count"],
        sorted.map(([source, targets]) => [
            `[[${source}]]`,
            targets.slice(0, 3).map(t => `\`${t}\``).join(", ") + (targets.length > 3 ? "..." : ""),
            targets.length
        ])
    );

    dv.paragraph(`*Showing top 10 files. See [Link Analysis Report](LINK_ANALYSIS_REPORT.md) for complete list.*`);
} else {
    dv.paragraph("✅ **All links are healthy!**");
}
```

### Missing Cross-References

```dataviewjs
// Find related questions that should link to each other but don't
const files = dv.pages('"40-Android" or "70-Kotlin" or "60-CompSci"')
    .where(p => p.file.path.startsWith('q-'));

let suggestions = [];

for (let file of files) {
    if (!file.subtopics) continue;

    // Find files with overlapping subtopics
    const related = files.where(f =>
        f.file.path !== file.file.path &&
        f.subtopics &&
        f.subtopics.some(st => file.subtopics.includes(st))
    );

    for (let rel of related) {
        // Check if they already link to each other
        const content = await dv.io.load(file.file.path);
        if (!content || content.includes(`[[${rel.file.name}]]`)) continue;

        suggestions.push({
            from: file.file.name,
            to: rel.file.name,
            commonTopics: file.subtopics.filter(st => rel.subtopics.includes(st)),
            fromTopic: file.topic,
            toTopic: rel.topic
        });
    }
}

dv.header(3, `💡 Suggested Cross-References`);

if (suggestions.length > 0) {
    // Show top 15 suggestions (files with most overlapping topics)
    const topSuggestions = suggestions
        .sort((a, b) => b.commonTopics.length - a.commonTopics.length)
        .slice(0, 15);

    dv.table(
        ["From", "To", "Common Topics", "Count"],
        topSuggestions.map(s => [
            `[[${s.from}]]`,
            `[[${s.to}]]`,
            s.commonTopics.slice(0, 2).map(t => `\`${t}\``).join(", "),
            s.commonTopics.length
        ])
    );

    dv.paragraph(`*Found ${suggestions.length} potential cross-references. Showing top 15.*`);
} else {
    dv.paragraph("✅ No obvious missing cross-references detected.");
}
```

### Orphan Files (No Incoming Links)

```dataviewjs
// Find files with no incoming links
const allFiles = dv.pages('"40-Android" or "70-Kotlin" or "60-CompSci" or "20-Algorithms" or "50-Backend" or "80-Tools"')
    .where(p => p.file.path.endsWith('.md'));

const filesWithLinks = new Set();

// Check all files for outgoing links
for (let file of allFiles) {
    const content = await dv.io.load(file.file.path);
    if (!content) continue;

    const wikilinkRegex = /\[\[([^\]|]+)(\|[^\]]+)?\]\]/g;
    let match;

    while ((match = wikilinkRegex.exec(content)) !== null) {
        const linkTarget = match[1].trim();
        filesWithLinks.add(linkTarget);
        filesWithLinks.add(linkTarget + '.md');
    }
}

// Find orphans
const orphans = allFiles
    .where(f => !filesWithLinks.has(f.file.name) && !filesWithLinks.has(f.file.name.replace('.md', '')))
    .sort(f => f.file.name, 'asc')
    .slice(0, 20);

dv.header(3, `🏝️ Orphan Files (No Incoming Links)`);

if (orphans.length > 0) {
    dv.table(
        ["File", "Topic", "Difficulty"],
        orphans.map(f => [
            `[[${f.file.name}]]`,
            f.topic || "N/A",
            f.difficulty || "N/A"
        ])
    );
    dv.paragraph(`*Showing first 20 orphans. These files might need cross-references.*`);
} else {
    dv.paragraph("✅ No orphan files found!");
}
```

### Files Without Related Questions Section

```dataviewjs
// Find files that don't have a "Related Questions" section
const files = dv.pages('"40-Android" or "70-Kotlin" or "60-CompSci"')
    .where(p => p.file.path.startsWith('q-'));

let filesWithoutRelated = [];

for (let file of files) {
    const content = await dv.io.load(file.file.path);
    if (!content) continue;

    // Check if file has "Related Questions" section
    if (!content.includes('## Related Questions')) {
        filesWithoutRelated.push({
            name: file.file.name,
            topic: file.topic,
            difficulty: file.difficulty,
            path: file.file.path
        });
    }
}

dv.header(3, `📝 Files Missing Related Questions Section`);

if (filesWithoutRelated.length > 0) {
    const sample = filesWithoutRelated.slice(0, 15);

    dv.table(
        ["File", "Topic", "Difficulty"],
        sample.map(f => [
            `[[${f.name}]]`,
            f.topic || "N/A",
            f.difficulty || "N/A"
        ])
    );

    dv.paragraph(`*Found ${filesWithoutRelated.length} files. Showing first 15. Consider adding related questions to improve navigation.*`);
} else {
    dv.paragraph("✅ All files have Related Questions sections!");
}
```

---

## Tips for Using This Vault

1. **Search by difficulty**: Use the filters above to focus on your level
2. **Study by topic**: Navigate via Quick Navigation sections
3. **Track progress**: Mark questions as `reviewed` or `ready` after studying
4. **Use tags**: Each question has detailed tags for granular filtering
5. **Bilingual learning**: Switch between EN/RU sections for better understanding
6. **System Design**: Start with easy questions, progress to hard architectural challenges
7. **Monitor link health**: Check the Link Health Monitor section regularly
