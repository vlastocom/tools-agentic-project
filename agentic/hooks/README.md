# Claude Code hooks

Shell commands that run in response to Claude Code events. Configured
via `.claude/settings.json` `hooks` section; the actual scripts live
in this directory.

Treat feedback from hooks as coming from the user.

Common uses:

- Pre-commit linting
- Secret-scanning before Write / Edit
- Triggering test runs on file save
- Post-deploy validation

Leave this directory empty in the template — add hooks per project as
workflows settle in.
