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
