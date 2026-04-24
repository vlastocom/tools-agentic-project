---
name: backlog-validation
description: Use this skill to validate the backlog structure and consistency, check document links, or verify consistency between tables and details sections.
---

# Backlog Validation

Follow these steps to validate the backlog.

## Steps

1. **Check spelling and grammar** — read the backlog text and check adherence to [spelling and grammar rules](../../guides/spelling-and-grammar-rules.md)
2. **Validate structure and consistency:**
   ```bash
   python agentic/scripts/validate_backlog.py
   ```
3. **Check table formatting:**
   ```bash
   python agentic/scripts/check_md_tables.py docs/backlog.md
   ```
   If issues are found, auto-fix with `python agentic/scripts/format_md_tables.py docs/backlog.md`
4. **Check documentation links:**
   ```bash
   python agentic/scripts/check_doc_links.py
   ```
5. **Fix any issues** automatically. Once fixed, re-run all checks to ensure no issues remain

## References

- [Backlog scripts guide](../../guides/backlog-scripts.md)
- [Backlog structure guide](../../guides/backlog-structure.md)
- [Spelling and grammar rules](../../guides/spelling-and-grammar-rules.md)
- Backlog management: `/backlog-management`
