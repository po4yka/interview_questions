#  Quick Link Monitor

**Quick Status Check** - Auto-updates when opened

---

##  Quick Health Check

```dataviewjs
<%* tR += await tp.user.folderConstants({ include_auxiliary: true }); %>
const files = dv.pages(folderQuery)
    .where(p => p.file.ext === "md");

let totalLinks = 0, brokenLinks = 0;

for (let file of files) {
    const content = await dv.io.load(file.file.path);
    if (!content) continue;

    const wikilinkRegex = /\[\[([^\]|]+)(\|[^\]]+)?\]\]/g;
    let match;

    while ((match = wikilinkRegex.exec(content)) !== null) {
        totalLinks++;
        const linkTarget = match[1].trim();
        const targetExists = dv.page(linkTarget) || dv.page(linkTarget + '.md') ||
                           dv.pages().find(p => p.file.name === linkTarget);
        if (!targetExists) brokenLinks++;
    }
}

const health = totalLinks > 0 ? Math.round(((totalLinks - brokenLinks) / totalLinks) * 100) : 100;
const emoji = health >= 90 ? '🟢' : health >= 70 ? '🟡' : '';

dv.paragraph(`# ${emoji} ${health}%`);
dv.paragraph(`**${totalLinks}** total links | **${brokenLinks}** broken | **${totalLinks - brokenLinks}** valid`);

if (brokenLinks > 0) {
    dv.paragraph(` **${brokenLinks} broken links need attention**`);
} else {
    dv.paragraph(` **All links are healthy!**`);
}
```

---

##  Today's Top Issues

```dataviewjs
<%* tR += await tp.user.folderConstants(); %>
const files = dv.pages(folderQuery)
    .where(p => p.file.ext === "md");

let brokenByTarget = {};

for (let file of files) {
    const content = await dv.io.load(file.file.path);
    if (!content) continue;

    const wikilinkRegex = /\[\[([^\]|]+)(\|[^\]]+)?\]\]/g;
    let match;

    while ((match = wikilinkRegex.exec(content)) !== null) {
        const linkTarget = match[1].trim();
        const targetExists = dv.page(linkTarget) || dv.page(linkTarget + '.md') ||
                           dv.pages().find(p => p.file.name === linkTarget);

        if (!targetExists) {
            brokenByTarget[linkTarget] = (brokenByTarget[linkTarget] || 0) + 1;
        }
    }
}

const topIssues = Object.entries(brokenByTarget)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

if (topIssues.length > 0) {
    dv.header(3, " Top 5 Missing Files");
    dv.table(
        ["Missing File", "References"],
        topIssues.map(([file, count]) => [
            `\`${file}\``,
            count
        ])
    );
} else {
    dv.paragraph(" No issues!");
}
```

---

##  Full Reports

- **[Link Health Dashboard](00-Administration/LINK-HEALTH-DASHBOARD.md)** - Comprehensive analysis
- **[Homepage](Homepage.md)** - Link Health Monitor section
- **[Link Analysis Report](LINK_ANALYSIS_REPORT.md)** - Detailed breakdown
- **[Broken Links Quick Reference](BROKEN_LINKS_QUICK_REFERENCE.md)** - Action items

---

*Last checked: Auto-updates on open*
