#  Link Health Dashboard

**Purpose**: Comprehensive automated monitoring of link health, cross-references, and vault connectivity.

**Last Generated**: Auto-updates on every view

---

##  Overall Link Health

```dataviewjs
// Comprehensive link health analysis
<%* tR += await tp.user.folderConstants({ include_auxiliary: true }); %>
const files = dv.pages(folderQuery)
    .where(p => p.file.ext === "md");

let stats = {
    totalFiles: 0,
    totalLinks: 0,
    brokenLinks: 0,
    validLinks: 0,
    orphanFiles: 0,
    filesWithoutRelated: 0
};

let brokenLinkDetails = [];
const filesWithLinks = new Set();

for (let file of files) {
    const isQuestion = file.file.name.startsWith('q-');
    if (isQuestion) {
        stats.totalFiles++;
    }
    const content = await dv.io.load(file.file.path);
    if (!content) continue;

    // Find all wikilinks
    const wikilinkRegex = /\[\[([^\]|]+)(\|[^\]]+)?\]\]/g;
    let match;
    let fileHasLinks = false;

    while ((match = wikilinkRegex.exec(content)) !== null) {
        stats.totalLinks++;
        fileHasLinks = true;
        const linkTarget = match[1].trim();

        // Track for orphan detection
        filesWithLinks.add(linkTarget);
        filesWithLinks.add(linkTarget + '.md');

        // Check if target exists
        const targetExists = dv.page(linkTarget) ||
                           dv.page(linkTarget + '.md') ||
                           dv.pages().find(p => p.file.name === linkTarget);

        if (!targetExists) {
            stats.brokenLinks++;
            brokenLinkDetails.push({
                source: file.file.name,
                target: linkTarget,
                sourcePath: file.file.path
            });
        } else {
            stats.validLinks++;
        }
    }

    // Check for Related Questions section
    if (isQuestion && !content.includes('## Related Questions')) {
        stats.filesWithoutRelated++;
    }
}

// Calculate orphans
for (let file of files) {
    if (!file.file.name.startsWith('q-')) continue;
    if (!filesWithLinks.has(file.file.name) && !filesWithLinks.has(file.file.name.replace('.md', ''))) {
        stats.orphanFiles++;
    }
}

// Calculate health score (weighted)
const linkHealth = stats.totalLinks > 0 ? Math.round((stats.validLinks / stats.totalLinks) * 100) : 100;
const structureHealth = stats.totalFiles > 0 ? Math.round(((stats.totalFiles - stats.filesWithoutRelated) / stats.totalFiles) * 100) : 100;
const connectivityHealth = stats.totalFiles > 0 ? Math.round(((stats.totalFiles - stats.orphanFiles) / stats.totalFiles) * 100) : 100;
const overallHealth = Math.round((linkHealth * 0.5) + (structureHealth * 0.25) + (connectivityHealth * 0.25));

// Display summary
dv.header(3, " Vault Health Score");
dv.paragraph(`
**Overall Health**: ${overallHealth}% ${overallHealth >= 90 ? '🟢' : overallHealth >= 70 ? '🟡' : ''}

| Metric | Score | Status |
|--------|-------|--------|
| **Link Integrity** | ${linkHealth}% | ${linkHealth >= 90 ? '🟢 Excellent' : linkHealth >= 70 ? '🟡 Good' : ' Needs Work'} |
| **Structure Quality** | ${structureHealth}% | ${structureHealth >= 90 ? '🟢 Excellent' : structureHealth >= 70 ? '🟡 Good' : ' Needs Work'} |
| **Connectivity** | ${connectivityHealth}% | ${connectivityHealth >= 90 ? '🟢 Excellent' : connectivityHealth >= 70 ? '🟡 Good' : ' Needs Work'} |
`);

dv.header(3, " Key Metrics");
dv.table(
    ["Metric", "Count", "Details"],
    [
        ["Total Files", stats.totalFiles, "Q&A files across all topics"],
        ["Total Links", stats.totalLinks, "Wikilinks found in all files"],
        ["Valid Links", stats.validLinks, `${linkHealth}% of all links`],
        ["Broken Links", stats.brokenLinks, `${stats.brokenLinks > 0 ? ' Needs attention' : ' All good'}`],
        ["Orphan Files", stats.orphanFiles, "Files with no incoming links"],
        ["Missing Structure", stats.filesWithoutRelated, "Files without Related Questions"]
    ]
);
```

---

##  Broken Links Detail

```dataviewjs
<%* tR += await tp.user.folderConstants({ include_auxiliary: true }); %>
const files = dv.pages(folderQuery)
    .where(p => p.file.ext === "md");

let brokenLinks = [];

for (let file of files) {
    const content = await dv.io.load(file.file.path);
    if (!content) continue;

    const wikilinkRegex = /\[\[([^\]|]+)(\|[^\]]+)?\]\]/g;
    let match;

    while ((match = wikilinkRegex.exec(content)) !== null) {
        const linkTarget = match[1].trim();
        const targetExists = dv.page(linkTarget) ||
                           dv.page(linkTarget + '.md') ||
                           dv.pages().find(p => p.file.name === linkTarget);

        if (!targetExists) {
            brokenLinks.push({
                source: file.file.name,
                target: linkTarget,
                topic: file.topic || 'N/A',
                difficulty: file.difficulty || 'N/A'
            });
        }
    }
}

if (brokenLinks.length > 0) {
    // Group by target (most common missing files)
    const targetCounts = {};
    for (let link of brokenLinks) {
        targetCounts[link.target] = (targetCounts[link.target] || 0) + 1;
    }

    const topMissing = Object.entries(targetCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 20);

    dv.header(3, " Most Referenced Missing Files");
    dv.table(
        ["Missing File", "References", "Priority"],
        topMissing.map(([file, count]) => [
            `\`${file}\``,
            count,
            count >= 3 ? " High" : count >= 2 ? "🟡 Medium" : "Low"
        ])
    );

    // Group by source
    const grouped = {};
    for (let link of brokenLinks) {
        if (!grouped[link.source]) {
            grouped[link.source] = [];
        }
        grouped[link.source].push(link.target);
    }

    const topSources = Object.entries(grouped)
        .sort((a, b) => b[1].length - a[1].length)
        .slice(0, 15);

    dv.header(3, " Files with Most Broken Links");
    dv.table(
        ["Source File", "Topic", "Broken Links", "Count"],
        topSources.map(([source, targets]) => {
            const file = files.find(f => f.file.name === source);
            return [
                `[[${source}]]`,
                file?.topic || 'N/A',
                targets.slice(0, 2).map(t => `\`${t}\``).join(", ") + (targets.length > 2 ? "..." : ""),
                targets.length
            ];
        })
    );
} else {
    dv.paragraph(" **No broken links found! Your vault is in perfect health.**");
}
```

---

##  Orphan Files Analysis

```dataviewjs
// Find files with no incoming links
<%* tR += await tp.user.folderConstants({ include_auxiliary: true }); %>
const scopedFiles = dv.pages(folderQuery)
    .where(p => p.file.ext === "md");
const questionFiles = scopedFiles.where(p => p.file.name.startsWith('q-'));

const filesWithLinks = new Set();

// Scan all files for outgoing links
for (let file of scopedFiles) {
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
const orphans = questionFiles
    .where(f => !filesWithLinks.has(f.file.name) && !filesWithLinks.has(f.file.name.replace('.md', '')))
    .sort(f => f.file.name, 'asc');

if (orphans.length > 0) {
    dv.header(3, `Found ${orphans.length} Orphan Files`);

    // Group by topic
    const byTopic = {};
    for (let orphan of orphans) {
        const topic = orphan.topic || 'uncategorized';
        if (!byTopic[topic]) byTopic[topic] = [];
        byTopic[topic].push(orphan);
    }

    for (let [topic, files] of Object.entries(byTopic).sort((a, b) => b[1].length - a[1].length)) {
        dv.header(4, `${topic} (${files.length} files)`);

        const sample = files.slice(0, 10);
        dv.table(
            ["File", "Difficulty", "Status"],
            sample.map(f => [
                `[[${f.file.name}]]`,
                f.difficulty || 'N/A',
                f.status || 'N/A'
            ])
        );

        if (files.length > 10) {
            dv.paragraph(`*${files.length - 10} more files...*`);
        }
    }

    dv.paragraph(`
**Recommendation**: Orphan files should be linked from:
- Related questions with similar topics
- MOC (Map of Content) files
- Index pages

These files exist but aren't discoverable through navigation.
    `);
} else {
    dv.paragraph(" **No orphan files! Excellent connectivity.**");
}
```

---

##  Missing Cross-References

```dataviewjs
// Find questions that should link to each other based on shared subtopics
<%* tR += await tp.user.folderConstants(); %>
const qFiles = dv.pages(folderQuery)
    .where(p => p.file.name.startsWith('q-') && p.subtopics);

let suggestions = [];

for (let file of qFiles) {
    const related = qFiles.where(f =>
        f.file.path !== file.file.path &&
        f.subtopics &&
        f.subtopics.some(st => file.subtopics.includes(st))
    );

    for (let rel of related) {
        const content = await dv.io.load(file.file.path);
        if (!content || content.includes(`[[${rel.file.name}]]`)) continue;

        const commonTopics = file.subtopics.filter(st => rel.subtopics.includes(st));

        suggestions.push({
            from: file.file.name,
            to: rel.file.name,
            commonTopics: commonTopics,
            fromTopic: file.topic,
            toTopic: rel.topic,
            relevance: commonTopics.length
        });
    }
}

if (suggestions.length > 0) {
    dv.header(3, `Found ${suggestions.length} Suggested Cross-References`);

    // Show highest relevance suggestions
    const topSuggestions = suggestions
        .sort((a, b) => b.relevance - a.relevance)
        .slice(0, 25);

    dv.table(
        ["From", "To", "Common Subtopics", "Relevance"],
        topSuggestions.map(s => [
            `[[${s.from}]]`,
            `[[${s.to}]]`,
            s.commonTopics.slice(0, 3).map(t => `\`${t}\``).join(", "),
            s.relevance >= 3 ? " High" : s.relevance >= 2 ? "🟡 Medium" : "Low"
        ])
    );

    dv.paragraph(`*Showing top 25 of ${suggestions.length} suggestions.*`);
    dv.paragraph(`
**How to use**:
1. Click on the "From" file
2. Scroll to the "Related Questions" section
3. Add a link to the "To" file if relevant
    `);
} else {
    dv.paragraph(" **All obvious cross-references are in place!**");
}
```

---

##  Structure Quality Check

```dataviewjs
// Check for common structural issues
<%* tR += await tp.user.folderConstants(); %>
const files = dv.pages(folderQuery)
    .where(p => p.file.name.startsWith('q-'));

let issues = {
    missingRelated: [],
    missingReferences: [],
    missingTags: [],
    missingSubtopics: []
};

for (let file of files) {
    const content = await dv.io.load(file.file.path);
    if (!content) continue;

    // Check for Related Questions section
    if (!content.includes('## Related Questions')) {
        issues.missingRelated.push(file);
    }

    // Check for References section
    if (!content.includes('## References')) {
        issues.missingReferences.push(file);
    }

    // Check for tags
    if (!file.tags || file.tags.length === 0) {
        issues.missingTags.push(file);
    }

    // Check for subtopics
    if (!file.subtopics || file.subtopics.length === 0) {
        issues.missingSubtopics.push(file);
    }
}

dv.header(3, "Structure Issues Summary");
dv.table(
    ["Issue Type", "Count", "Severity"],
    [
        ["Missing Related Questions", issues.missingRelated.length, issues.missingRelated.length > 50 ? " High" : "🟡 Medium"],
        ["Missing References", issues.missingReferences.length, issues.missingReferences.length > 100 ? "🟡 Medium" : "🟢 Low"],
        ["Missing Tags", issues.missingTags.length, issues.missingTags.length > 20 ? " High" : "🟢 Low"],
        ["Missing Subtopics", issues.missingSubtopics.length, issues.missingSubtopics.length > 20 ? " High" : "🟢 Low"]
    ]
);

// Show sample of files missing Related Questions (highest priority)
if (issues.missingRelated.length > 0) {
    dv.header(4, " Files Missing Related Questions (Sample)");
    const sample = issues.missingRelated.slice(0, 15);
    dv.table(
        ["File", "Topic", "Difficulty"],
        sample.map(f => [
            `[[${f.file.name}]]`,
            f.topic || 'N/A',
            f.difficulty || 'N/A'
        ])
    );
}
```

---

##  Action Items

```dataviewjs
// Generate prioritized action items based on the analysis
dv.header(3, "Recommended Actions");

dv.paragraph(`
### Priority 1: Fix Broken Links 
1. Review the "Most Referenced Missing Files" section above
2. Create the top 5 most-referenced missing files
3. Fix naming inconsistencies in remaining broken links

### Priority 2: Add Cross-References 🟡
1. Review the "Missing Cross-References" section
2. Add relevant links between related questions
3. Focus on high-relevance suggestions first

### Priority 3: Connect Orphan Files 🟢
1. Review orphan files by topic
2. Add links from related questions or MOC files
3. Improve discoverability of these files

### Priority 4: Structure Improvements 🟢
1. Add "Related Questions" sections to files that lack them
2. Add relevant tags and subtopics
3. Include references to documentation

### Maintenance
- Run this dashboard weekly to track improvements
- Use the Homepage Link Health Monitor for quick checks
- Keep the LINK_ANALYSIS_REPORT.md updated
`);
```

---

##  Historical Tracking

**Tip**: Take a screenshot of the health metrics above each time you make improvements to track your progress over time.

**Target Goals**:
- Overall Health: 95%+
- Link Integrity: 95%+
- Orphan Files: <5%
- Structure Quality: 90%+

---

**Auto-refreshes**: This dashboard automatically updates when you open it in Obsidian.
**Manual refresh**: Close and reopen the file to force refresh.
