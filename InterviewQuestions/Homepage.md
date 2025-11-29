---
date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Saturday, November 29th 2025, 12:07:29 pm
---

# Interview Questions Knowledge Base

**Comprehensive bilingual collection** of interview questions for Android, Kotlin, Computer Science, and more. Perfect for interview preparation from Junior to Staff+ levels.

---

## Quick Navigation

### Maps of Content

```dataviewjs
const topicMapping = {
    'moc-android': { folder: '40-Android', label: 'Android' },
    'moc-kotlin': { folder: '70-Kotlin', label: 'Kotlin' },
    'moc-algorithms': { folder: '20-Algorithms', label: 'Algorithms' },
    'moc-system-design': { folder: '30-System-Design', label: 'System Design' },
    'moc-backend': { folder: '50-Backend', label: 'Backend' },
    'moc-cs': { folder: '60-CompSci', label: 'Computer Science' },
    'moc-tools': { folder: '80-Tools', label: 'Tools' }
};

const mocs = dv.pages('"90-MOCs"').where(p => p.kind === "moc");
const rows = [];

for (const moc of mocs) {
    const mapping = topicMapping[moc.file.name];
    if (mapping) {
        const qCount = dv.pages(`"${mapping.folder}"`).where(p => p.file.name.startsWith('q-')).length;
        rows.push([mapping.label, moc.file.link, qCount]);
    }
}

rows.sort((a, b) => b[2] - a[2]);
dv.table(["Topic", "MOC", "Questions"], rows);
```

### Documentation & Templates

- [[00-Administration/README|Vault Documentation]] | [[00-Administration/Vault-Rules/TAXONOMY|Taxonomy]] | [[00-Administration/Vault-Rules/FILE-NAMING-RULES|Naming Rules]]
- [[_templates/_tpl-qna|Q&A Template]] | [[_templates/_tpl-concept|Concept Template]] | [[_templates/_tpl-moc|MOC Template]]

---

## Vault Statistics

### Overall Metrics

```dataviewjs
const QA_SOURCES = '"20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"';
const questions = dv.pages(QA_SOURCES).where(p => p.topic);
const concepts = dv.pages('"10-Concepts"').where(p => p.file.name.startsWith('c-'));
const mocs = dv.pages('"90-MOCs"').where(p => p.kind === "moc");

dv.table(
    ["Content Type", "Count", "Draft", "Reviewed", "Ready"],
    [
        [
            "Q&A Notes",
            questions.length,
            questions.where(p => String(p.status).toLowerCase() === "draft").length,
            questions.where(p => String(p.status).toLowerCase() === "reviewed").length,
            questions.where(p => String(p.status).toLowerCase() === "ready").length
        ],
        [
            "Concept Notes",
            concepts.length,
            "-",
            "-",
            "-"
        ],
        [
            "MOCs",
            mocs.length,
            "-",
            "-",
            "-"
        ]
    ]
);

dv.paragraph(`**Total Knowledge Items:** ${questions.length + concepts.length + mocs.length}`);
```

### By Topic

```dataviewjs
const QA_SOURCES = '"20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"';
const allPages = dv.pages(QA_SOURCES).where(p => p.topic);

const topicData = {};
for (const page of allPages) {
    const topic = String(page.topic).toLowerCase();
    if (!topicData[topic]) {
        topicData[topic] = { total: 0, easy: 0, medium: 0, hard: 0, ready: 0 };
    }
    topicData[topic].total++;
    const diff = String(page.difficulty).toLowerCase();
    if (diff === 'easy') topicData[topic].easy++;
    else if (diff === 'medium') topicData[topic].medium++;
    else if (diff === 'hard') topicData[topic].hard++;
    if (String(page.status).toLowerCase() === 'ready') topicData[topic].ready++;
}

const progressBar = (current, total, width = 10) => {
    if (total === 0) return '[' + '-'.repeat(width) + ']';
    const filled = Math.round((current / total) * width);
    return '[' + '='.repeat(filled) + '-'.repeat(width - filled) + ']';
};

const formatTopic = (t) => t.charAt(0).toUpperCase() + t.slice(1).replace(/-/g, ' ');

const rows = Object.entries(topicData)
    .sort((a, b) => b[1].total - a[1].total)
    .map(([topic, data]) => [
        formatTopic(topic),
        data.total,
        `${data.easy}/${data.medium}/${data.hard}`,
        data.total > 0 ? `${Math.round((data.ready / data.total) * 100)}%` : "0%",
        progressBar(data.ready, data.total)
    ]);

dv.table(["Topic", "Count", "E/M/H", "Ready %", "Progress"], rows);
```

### Distribution Summary

```dataviewjs
const QA_SOURCES = '"20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"';
const pages = dv.pages(QA_SOURCES).where(p => p.topic);
const total = pages.length;

// Difficulty counts
const easy = pages.where(p => String(p.difficulty).toLowerCase() === 'easy').length;
const medium = pages.where(p => String(p.difficulty).toLowerCase() === 'medium').length;
const hard = pages.where(p => String(p.difficulty).toLowerCase() === 'hard').length;

// Status counts
const draft = pages.where(p => String(p.status).toLowerCase() === 'draft').length;
const reviewed = pages.where(p => String(p.status).toLowerCase() === 'reviewed').length;
const ready = pages.where(p => String(p.status).toLowerCase() === 'ready').length;

const pct = (n) => total > 0 ? Math.round((n / total) * 100) : 0;

dv.paragraph(`**By Difficulty:** Easy: ${easy} (${pct(easy)}%) | Medium: ${medium} (${pct(medium)}%) | Hard: ${hard} (${pct(hard)}%)`);
dv.paragraph(`**By Status:** Draft: ${draft} (${pct(draft)}%) | Reviewed: ${reviewed} (${pct(reviewed)}%) | Ready: ${ready} (${pct(ready)}%)`);
```

---

## Concept Notes

```dataviewjs
const concepts = dv.pages('"10-Concepts"').where(p => p.file.name.startsWith('c-'));

// Group by main tags
const tagCounts = {};
for (const c of concepts) {
    if (c.tags) {
        const tags = Array.isArray(c.tags) ? c.tags : [c.tags];
        for (const tag of tags) {
            const mainTag = String(tag).split('/')[0].toLowerCase();
            // Filter to meaningful categories
            if (['android', 'kotlin', 'java', 'concurrency', 'lifecycle', 'compose', 'coroutines', 'testing', 'performance', 'security', 'architecture', 'ui', 'networking', 'database'].includes(mainTag)) {
                tagCounts[mainTag] = (tagCounts[mainTag] || 0) + 1;
            }
        }
    }
}

dv.paragraph(`**Total Concepts:** ${concepts.length}`);

const rows = Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([tag, count]) => [tag.charAt(0).toUpperCase() + tag.slice(1), count]);

if (rows.length > 0) {
    dv.table(["Category", "Count"], rows);
}

// Show concepts without tags
const noTags = concepts.where(c => !c.tags || c.tags.length === 0).length;
if (noTags > 0) {
    dv.paragraph(`*${noTags} concepts have no tags defined.*`);
}
```

---

## Recent Activity

### Recently Created

```dataviewjs
const ALL_CONTENT = '"10-Concepts" or "20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"';
const allPages = dv.pages(ALL_CONTENT);

const getType = (name) => {
    if (name.startsWith('q-')) return 'Q&A';
    if (name.startsWith('c-')) return 'Concept';
    return 'Other';
};

const recentlyCreated = allPages
    .sort(p => p.file.ctime, 'desc')
    .slice(0, 10);

dv.table(
    ["Note", "Type", "Topic", "Created"],
    recentlyCreated.map(p => [
        p.file.link,
        getType(p.file.name),
        p.topic || "-",
        dv.date(p.file.ctime).toFormat("yyyy-MM-dd")
    ])
);
```

### Recently Modified

```dataviewjs
const ALL_CONTENT = '"10-Concepts" or "20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"';
const allPages = dv.pages(ALL_CONTENT);

const getType = (name) => {
    if (name.startsWith('q-')) return 'Q&A';
    if (name.startsWith('c-')) return 'Concept';
    return 'Other';
};

const recentlyModified = allPages
    .sort(p => p.file.mtime, 'desc')
    .slice(0, 10);

dv.table(
    ["Note", "Type", "Topic", "Modified"],
    recentlyModified.map(p => [
        p.file.link,
        getType(p.file.name),
        p.topic || "-",
        dv.date(p.file.mtime).toFormat("yyyy-MM-dd")
    ])
);
```

---

## Language Coverage

```dataviewjs
const QA_SOURCES = '"20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"';
const pages = dv.pages(QA_SOURCES).where(p => p.language_tags);
const total = pages.length;

const hasTag = (p, tag) => {
    if (!p.language_tags) return false;
    const tags = Array.isArray(p.language_tags) ? p.language_tags : [p.language_tags];
    return tags.includes(tag);
};

const bilingual = pages.where(p => hasTag(p, 'en') && hasTag(p, 'ru')).length;
const enOnly = pages.where(p => hasTag(p, 'en') && !hasTag(p, 'ru')).length;
const ruOnly = pages.where(p => hasTag(p, 'ru') && !hasTag(p, 'en')).length;

const pct = (n) => total > 0 ? Math.round((n / total) * 100) : 0;

dv.paragraph(`**Language Coverage:** ${total} questions tracked`);
dv.paragraph(`- Bilingual (EN+RU): ${bilingual} (${pct(bilingual)}%)`);
dv.paragraph(`- English only: ${enOnly} (${pct(enOnly)}%)`);
dv.paragraph(`- Russian only: ${ruOnly} (${pct(ruOnly)}%)`);
```

---

## Quick Health Check

```dataviewjs
const QA_SOURCES = '"20-Algorithms" or "30-System-Design" or "40-Android" or "50-Backend" or "60-CompSci" or "70-Kotlin" or "80-Tools"';
const allPages = dv.pages(QA_SOURCES).where(p => p.file.name.startsWith('q-'));

const noRelated = allPages.where(p => !p.related || (Array.isArray(p.related) && p.related.length === 0)).length;
const orphans = allPages.where(p => p.file.inlinks.length === 0).length;

dv.paragraph(`**Files without 'related' field:** ${noRelated}`);
dv.paragraph(`**Potential orphans (no inlinks):** ${orphans}`);
dv.paragraph(`[[00-Administration/Link-Health-Report|View Full Link Health Report]]`);
```

---

## Quick Tips

1. **Navigate by MOC** - Start with topic MOCs above for structured learning paths
2. **Filter by difficulty** - Use Dataview queries or search `difficulty: easy/medium/hard`
3. **Track progress** - Update `status` field: draft -> reviewed -> ready
4. **Bilingual study** - Toggle between EN/RU sections for deeper understanding
5. **Link concepts** - Use `related` field to connect Q&As with concept notes
