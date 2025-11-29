---
date created: Friday, November 29th 2025
date modified: Friday, November 29th 2025
---

# Link Health Report

> **Note:** This page contains intensive queries that read file contents. It may take a moment to load on large vaults.

[[Homepage|Back to Homepage]]

---

## Broken Links Detection

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
dv.header(3, "Summary");
const linkHealth = totalLinks > 0 ? Math.round(((totalLinks - brokenCount) / totalLinks) * 100) : 100;
dv.paragraph(`**Total Links**: ${totalLinks} | **Broken**: ${brokenCount} | **Health**: ${linkHealth}%`);

if (brokenCount > 0) {
    dv.header(3, `Broken Links (${brokenCount})`);

    // Group by source file
    const grouped = {};
    for (let link of brokenLinks) {
        if (!grouped[link.source]) {
            grouped[link.source] = [];
        }
        grouped[link.source].push(link.target);
    }

    // Display top 20 files with most broken links
    const sorted = Object.entries(grouped)
        .sort((a, b) => b[1].length - a[1].length)
        .slice(0, 20);

    dv.table(
        ["Source File", "Broken Links", "Count"],
        sorted.map(([source, targets]) => [
            `[[${source}]]`,
            targets.slice(0, 3).map(t => `\`${t}\``).join(", ") + (targets.length > 3 ? "..." : ""),
            targets.length
        ])
    );
} else {
    dv.paragraph("**All links are healthy!**");
}
```

---

## Missing Cross-References

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

dv.header(3, "Suggested Cross-References");

if (suggestions.length > 0) {
    // Show top 25 suggestions (files with most overlapping topics)
    const topSuggestions = suggestions
        .sort((a, b) => b.commonTopics.length - a.commonTopics.length)
        .slice(0, 25);

    dv.table(
        ["From", "To", "Common Topics", "Count"],
        topSuggestions.map(s => [
            `[[${s.from}]]`,
            `[[${s.to}]]`,
            s.commonTopics.slice(0, 2).map(t => `\`${t}\``).join(", "),
            s.commonTopics.length
        ])
    );

    dv.paragraph(`*Found ${suggestions.length} potential cross-references. Showing top 25.*`);
} else {
    dv.paragraph("No obvious missing cross-references detected.");
}
```

---

## Orphan Files (No Incoming Links)

```dataviewjs
// Find files with no incoming links
const allFiles = dv.pages('"10-Concepts" or "20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"')
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
    .slice(0, 30);

dv.header(3, `Orphan Files (No Incoming Links)`);

if (orphans.length > 0) {
    dv.table(
        ["File", "Topic", "Difficulty"],
        orphans.map(f => [
            `[[${f.file.name}]]`,
            f.topic || "N/A",
            f.difficulty || "N/A"
        ])
    );
    dv.paragraph(`*Showing first 30 orphans. These files might need cross-references.*`);
} else {
    dv.paragraph("No orphan files found!");
}
```

---

## Files Without Related Questions Section

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

dv.header(3, `Files Missing Related Questions Section`);

if (filesWithoutRelated.length > 0) {
    const sample = filesWithoutRelated.slice(0, 25);

    dv.table(
        ["File", "Topic", "Difficulty"],
        sample.map(f => [
            `[[${f.name}]]`,
            f.topic || "N/A",
            f.difficulty || "N/A"
        ])
    );

    dv.paragraph(`*Found ${filesWithoutRelated.length} files. Showing first 25. Consider adding related questions to improve navigation.*`);
} else {
    dv.paragraph("All files have Related Questions sections!");
}
```

---

## Files Without 'related' Frontmatter Field

```dataviewjs
const QA_SOURCES = '"20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"';
const pages = dv.pages(QA_SOURCES).where(p => p.file.name.startsWith('q-'));

const noRelated = pages.where(p => !p.related || p.related.length === 0)
    .sort(p => p.file.name, 'asc')
    .slice(0, 30);

dv.header(3, `Files Without 'related' Field (${noRelated.length} shown)`);

if (noRelated.length > 0) {
    dv.table(
        ["File", "Topic", "Difficulty"],
        noRelated.map(p => [
            p.file.link,
            p.topic || "N/A",
            p.difficulty || "N/A"
        ])
    );
} else {
    dv.paragraph("All Q&A files have the 'related' field populated!");
}
```
