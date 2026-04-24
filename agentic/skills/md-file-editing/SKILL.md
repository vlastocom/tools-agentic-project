---
name: md-file-editing
description: Use this skill whenever creating or editing Markdown (.md) files in the project.
---

# Markdown File Editing Guidelines

Follow these rules whenever creating or editing any `.md` file in the project.

## Spelling and Grammar

Strictly follow the [spelling and grammar rules](../../guides/spelling-and-grammar-rules.md):

- **Spelling:** Use British English in Markdown text (e.g. "colour", "initialise"), American English in code snippets and identifiers
- **Articles:** Always include articles ("the", "a", "an") where grammatically required — this is the most common mistake
- **Modal verbs:** Do not skip "should", "can", "must" when abbreviating sentences
- **Commas:** No comma after abbreviations (e.g. `e.g. something`), no Oxford comma (`apple, banana and orange`)

## Table Formatting

All Markdown tables must be correctly formatted for IntelliJ compatibility:

1. **Consistent column widths:** Every table row must have the same column widths, padded with spaces
2. **Cell padding:** At least one space before and after each cell's content (`| value |`, not `|value|`)
3. **Separator row:** Dashes must fill the full column width (matching the padded width of the widest cell)
4. **Alignment:**
    - Left-align text or generic content by default; the separator row uses plain dashes (`---`, not `:--`)
    - Use right-aligned columns for numeric values (separator row uses `|-------:|`)
       - You must still pad right-aligned columns with spaces
    - Centre-align columns with short, uniform values (e.g. "Yes"/"No", status codes, single numbers)

Example of a correctly formatted table:

```markdown
| Task No | Field           | Value                          | Estimate (days) |
|:-------:|-----------------|--------------------------------|----------------:|
|    1    | **Code**        | AUTH                           |              14 |
|    2    | **Short name**  | Authentication                 |             172 |
|    3    | **Description** | System authentication process. |              21 |
```

Common mistakes to avoid:
- Mismatched column widths between header, separator and data rows
- Missing space padding (e.g. `|**Field**|` instead of `| **Field** |`)
- Separator row shorter or longer than the data columns

**Scripts:**
- Use `python agentic/scripts/check_md_tables.py <file>` to validate table formatting
- Use `python agentic/scripts/format_md_tables.py <file>` to auto-fix table formatting issues

## Links

- Use **relative paths** for all internal links — never use absolute filesystem paths (e.g. `/home/...`)
- Verify that the link target exists before adding it
- Use `python agentic/scripts/check_all_md_links.py` to validate all links across the project
    - Use the output to identify issues (broken links, absolute paths)
    - Attempt to fix these issues automatically by locating the target file
    - If you cannot identify the target for the broken link, ask for clarification 

## General Structure

- Use blank lines before and after headings, tables, code blocks and horizontal rules (`---`)
- Use ATX-style headings (`# H1`, `## H2`) — not underline style
- Use fenced code blocks with a language identifier (e.g. ` ```java `, ` ```markdown `)
- Keep lines at a reasonable length (~80-120 characters, apply any exceptions reasonably); 
  long content in table cells should use `<br>` for line breaks rather than wrapping
- Separate paragraphs with a single blank line

