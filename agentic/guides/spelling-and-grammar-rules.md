# Spelling and grammar rules

The spelling and grammar rules described in here should be adhered to strictly across any text output,
including comments, code identifiers, documentation.

### Spelling
Please use the correct spelling in a particular context:

| Context                          | Use                                      |
|----------------------------------|------------------------------------------|
| Code and identifiers             | American (`color`, `initialize`)         |
| Comments, MD files, UI text      | British (`colour`, `initialise`)         |
| Existing code/library references | As defined (e.g. `Authorization` header) |
| Code snippets in MD              | American                                 |
| IT and UI terms                  | Standard form (see list below)           |

**IT and UI terms** that have a British English variant should use the standard IT/UI spelling,
not the British variant. These terms are established industry conventions and match the
component or API names used in code:

| Term      | Use (IT standard) | Not (British variant) | Reason                               |
|-----------|-------------------|-----------------------|--------------------------------------|
| dialog    | dialog            | dialogue              | MUI `Dialog` component, Windows term |
| program   | program           | programme             | Standard computing term              |
| check box | checkbox          | tick box              | MUI `Checkbox` component             |
| analog    | analog            | analogue              | Standard in electronics/computing    |

Grammar checkers may flag these — override them when the term refers to a UI component or
computing concept.

**Compound and British-variant terms** that recur in prose across projects. Use the form on
the left in comments / Markdown; the right column is the form to avoid.

| Use (canonical)   | Not (avoid)              | Reason                                                                                     |
|-------------------|--------------------------|--------------------------------------------------------------------------------------------|
| autoconfigured    | auto&#8209;configured    | Spring Boot's own term is "autoconfiguration" — no hyphen in the adjective                 |
| autoconfiguration | auto&#8209;configuration | Same as above                                                                              |
| customiser        | custom&#8203;izer        | British spelling rule applies to prose; preserve identifier names verbatim                 |
| customise         | custom&#8203;ize         | Same as above                                                                              |
| preloaded         | pre&#8209;loaded         | Closed compound — common usage drops the hyphen                                            |
| preempt           | pre&#8209;empt           | Closed compound                                                                            |
| clean-up          | clean&#8203;up           | Noun form is hyphenated; verb form is two words ("clean up"). Avoid the closed "cleanup".  |

Identifier names (Java class names, method names, Spring bean names — e.g.
`JsonMapperBuilderCustomizer`, `Jackson2ObjectMapperBuilderCustomizer`) are preserved verbatim
per the "Existing code/library references" row above.

### Grammar
1. *Avoid missing articles*: Include articles ("the", "a", "an") where grammatically required,
   as per the implied variety of English (British or American — see above).
   You can omit articles in code identifiers, but strictly adhere to this rule in all written text,
   including code comments, JSDoc, Javadoc and inline remarks.
   - Bad: `// Fetch books using Apollo Client` → missing "the" before "Apollo Client"
   - Good: `// Fetch books using the Apollo Client` → missing "the" before "Apollo Client"
   - Bad:  `// Wait for transition to complete` — missing "the"
   - Good: `// Wait for the transition to complete`
   - Bad:  `// Content should still be within viewport` — missing "the"
   - Good: `// Content should still be within the viewport`
   - Bad:  `// Returns list of accounts` — missing "the" / "a"
   - Good: `// Returns the list of accounts` or `// Returns a list of accounts`
   - Bad:  `// Wait for keystroke` — missing "the" / "a"
   - Good: `// Wait for a keystroke` or `// Wait for the keystroke` (depending on context)
2. *Avoid missing modal verbs*: Do not abbreviate sentences by skipping modal verbs ("should", "can", "must")
3. Avoid comma after abbreviations: `e.g. something` not `e.g., something`
4. Use the commas consistently in the lists, avoid comma before the final and / or: "apple, banana and orange", not "apple, banana, and orange"
5. *Trailing periods on fragments*: Single-line Javadoc, JSDoc, bullet points and other short comments that
   are fragments (i.e. not full sentences) should **not** end with a trailing period. Full sentences should
   end with a period as normal.
   - Bad:  `/** The user's email address. */` — fragment, should not end with a period
   - Good: `/** The user's email address */`
   - Bad:  `/** Input DTO for validating an activation link. */` — fragment
   - Good: `/** Input DTO for validating an activation link */`
   - OK:   `/** Sanitise a user-supplied text input by trimming whitespace and stripping control characters. */` — full sentence, period is correct
6. Make sure the noun-noun constructs are used in a grammatically correct way:
   - Bad: The users list (should be either of the above or "The user's list" or "The users' list", but that may not be what you wanted to say)
   - OK: The `users` list (`users` is an identifier)
   - Also OK: The list of users (if "users" is not an identifier)
7. *Comma after conjunctive / linking adverbs* at the start of a clause: include a comma after
   "Instead", "However", "Moreover", "Therefore", "Hence", "Thus", "Indeed", "Similarly",
   "Consequently", "Furthermore", "Meanwhile", "Otherwise" when they introduce a clause.
   - Bad:  `// Instead the tests open plain JDBC connections directly.`
   - Good: `// Instead, the tests open plain JDBC connections directly.`
   - Bad:  `// However the schema is pre-populated by the dev compose.`
   - Good: `// However, the schema is pre-populated by the dev compose.`
8. *Space between `§` and a quoted section name*: write `§ "Section name"`, not `§"Section name"`.
   The non-breaking-space convention for cross-reference markers improves scanability and
   matches how the same form is read in published prose.
