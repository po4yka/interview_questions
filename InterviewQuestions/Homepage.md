---
---

# Interview Questions Knowledge Base

> **Comprehensive bilingual collection** of interview questions for Android, Kotlin, Computer Science, and more. Perfect for interview preparation from Junior to Staff+ levels.

---

## Vault Statistics

### Overall Metrics

```dataview
TABLE WITHOUT ID
    length(rows) as "Total Questions"
FROM "20-Algorithms" OR "30-System-Design" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
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
FROM "20-Algorithms" OR "30-System-Design" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE topic
GROUP BY topic
SORT length(rows) DESC
```

### By Difficulty

```dataviewjs
const sources = '"20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"';
const difficultyPages = dv.pages(sources)
    .where(p => p.difficulty);

const totalDifficulty = difficultyPages.length;
const preferredOrder = ["easy", "medium", "hard"];
const difficultyCounts = {};

for (const page of difficultyPages) {
    const key = String(page.difficulty).toLowerCase();
    difficultyCounts[key] = (difficultyCounts[key] ?? 0) + 1;
}

const formatLabel = value => value ? value.charAt(0).toUpperCase() + value.slice(1) : "Unknown";

const orderedRows = preferredOrder
    .map(diff => ({ diff, count: difficultyCounts[diff] ?? 0 }))
    .filter(entry => entry.count > 0);

const otherRows = Object.keys(difficultyCounts)
    .filter(diff => !preferredOrder.includes(diff))
    .sort()
    .map(diff => ({ diff, count: difficultyCounts[diff] }));

const tableRows = orderedRows.concat(otherRows).map(({ diff, count }) => [
    formatLabel(diff),
    count,
    totalDifficulty ? `${Math.round((count / totalDifficulty) * 100)}%` : "0%"
]);

if (tableRows.length) {
    dv.table(["Difficulty", "Count", "Percentage"], tableRows);
} else {
    dv.paragraph("No questions with difficulty metadata.");
}
```

### By Status

```dataviewjs
const statusSources = '"20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"';
const statusPages = dv.pages(statusSources)
    .where(p => p.status);

const totalStatuses = statusPages.length;
const statusOrder = ["draft", "reviewed", "ready"];
const statusCounts = {};

for (const page of statusPages) {
    const key = String(page.status).toLowerCase();
    statusCounts[key] = (statusCounts[key] ?? 0) + 1;
}

const formatLabel = value => value ? value.charAt(0).toUpperCase() + value.slice(1) : "Unknown";

const preferredStatuses = statusOrder
    .map(status => ({ status, count: statusCounts[status] ?? 0 }))
    .filter(entry => entry.count > 0);

const additionalStatuses = Object.keys(statusCounts)
    .filter(status => !statusOrder.includes(status))
    .sort()
    .map(status => ({ status, count: statusCounts[status] }));

const statusRows = preferredStatuses.concat(additionalStatuses).map(({ status, count }) => [
    formatLabel(status),
    count,
    totalStatuses ? `${Math.round((count / totalStatuses) * 100)}%` : "0%"
]);

if (statusRows.length) {
    dv.table(["Status", "Count", "Percentage"], statusRows);
} else {
    dv.paragraph("No questions with status metadata.");
}
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
FROM "20-Algorithms" OR "30-System-Design" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE language_tags
GROUP BY true
```

---

## Link Health Monitor

### Broken Links Detection

```dataviewjs
// Find all files with broken wikilinks
const folderQuery = '"20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"';
const files = dv.pages(folderQuery)
    .where(p => p.file.ext === "md");

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
dv.header(3, ` Summary`);
const linkHealth = totalLinks > 0 ? Math.round(((totalLinks - brokenCount) / totalLinks) * 100) : 100;
dv.paragraph(`**Total Links**: ${totalLinks} | **Broken**: ${brokenCount} | **Health**: ${linkHealth}%`);

if (brokenCount > 0) {
    dv.header(3, ` Broken Links (${brokenCount})`);

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
    dv.paragraph(" **All links are healthy!**");
}
```

### Missing Cross-References

```dataviewjs
// Find related questions that should link to each other but don't
const questionFiles = dv.pages('"20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"')
    .where(p => p.file.name.startsWith('q-'));

let suggestions = [];

for (let file of questionFiles) {
    if (!file.subtopics) continue;

    // Find files with overlapping subtopics
    const related = questionFiles.where(f =>
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

dv.header(3, ` Suggested Cross-References`);

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
    dv.paragraph(" No obvious missing cross-references detected.");
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

dv.header(3, ` Orphan Files (No Incoming Links)`);

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
    dv.paragraph(" No orphan files found!");
}
```

### Files Without Related Questions Section

```dataviewjs
// Find files that don't have a "Related Questions" section
const files = dv.pages('"20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"')
    .where(p => p.file.name.startsWith('q-'));

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

dv.header(3, ` Files Missing Related Questions Section`);

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
    dv.paragraph(" All files have Related Questions sections!");
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
