const TOPIC_FOLDERS_DEFAULT = [
  "20-Algorithms",
  "30-System-Design",
  "40-Android",
  "50-Backend",
  "60-CompSci",
  "70-Kotlin",
  "80-Tools"
];

const AUXILIARY_FOLDERS_DEFAULT = [
  "10-Concepts",
  "90-MOCs"
];

module.exports = {
  /**
   * Injects shared folder constants for DataviewJS blocks.
   *
   * Usage inside a code block:
   * ````
   * ```dataviewjs
   * <%* tR += await tp.user.folderConstants({ include_auxiliary: true }); %>
   * // rest of your DataviewJS code...
   * ```
   * ````
   *
   * Options (all optional):
   * - include_auxiliary: boolean (default: false)
   * - topicVar: string (default: "TOPIC_FOLDERS")
   * - auxiliaryVar: string (default: "AUXILIARY_FOLDERS")
   * - combinedVar: string (default: "SCAN_FOLDERS")
   * - queryVar: string (default: "folderQuery")
   * - withQuery: boolean (default: true)
   *
   * @param {TemplaterApi} tp
   * @param {Object} options
   * @returns {Promise<string>}
   */
  folderConstants: async (tp, options = {}) => {
    const opts = options || {};
    const topicVar = opts.topicVar ?? "TOPIC_FOLDERS";
    const auxiliaryVar = opts.auxiliaryVar ?? "AUXILIARY_FOLDERS";
    const combinedVar = opts.combinedVar ?? "SCAN_FOLDERS";
    const queryVar = opts.queryVar ?? "folderQuery";
    const includeAuxiliary = opts.include_auxiliary ?? false;
    const withQuery = opts.withQuery ?? true;

    const topicFolders = JSON.stringify(TOPIC_FOLDERS_DEFAULT);
    const auxiliaryFolders = JSON.stringify(AUXILIARY_FOLDERS_DEFAULT);

    let result = `const ${topicVar} = ${topicFolders};\n`;

    if (includeAuxiliary) {
      result += `const ${auxiliaryVar} = ${auxiliaryFolders};\n`;
      result += `const ${combinedVar} = [...${topicVar}, ...${auxiliaryVar}];\n`;
      if (withQuery) {
        result += `const ${queryVar} = ${combinedVar}.map(folder => \`"\${folder}"\`).join(" or ");\n`;
      }
    } else if (withQuery) {
      result += `const ${queryVar} = ${topicVar}.map(folder => \`"\${folder}"\`).join(" or ");\n`;
    }

    return result;
  }
};
