# Code-quality checklist

Consolidated punch list of code-quality patterns that have surfaced
repeatedly in review across projects using this template. Every
implementer and every reviewer must run through this checklist before
declaring work done. The
[code-reviewer agent](../agents/code-reviewer.md) treats every miss as
at-least a `should-fix` finding; correctness-impacting misses
(NPE-prone chains, SQL injection vectors, deprecated APIs that will be
removed) are `must-fix`.

This file is a **complement** to (not a replacement for) the deeper
guides:

- [spelling-and-grammar-rules.md](spelling-and-grammar-rules.md) — the
  authoritative spelling/grammar rules; this checklist captures the
  prose-level patterns implementers most often miss
- [testing-guide.md](testing-guide.md) — the authoritative testing
  conventions; § "Test-code quality" mirrors the test-specific items
  in this checklist
- [backend-code-layout-guide.md](backend-code-layout-guide.md),
  [frontend-code-layout-guide.md](frontend-code-layout-guide.md) — the
  authoritative layout / naming / build conventions

When this file disagrees with one of those, the deeper guide wins. When
a recurring pattern emerges that none of those cover, add it here and
update the relevant deeper guide in the same commit.

### Structure of this guide

The **main checklist** (sections 1-3, 7-10) is stack-agnostic and
applies to every project that adopts this template. The **stack
appendices** at the end carry idioms specific to one technology stack —
keep the appendix that matches your project, delete the rest.

---

## 1. Comments and doc-comments

1. **Sentences ≤ 40 words.** Long em-dash chains and parenthetical
   pile-ups are the usual culprits. Split into two sentences, or
   convert a comma-separated tail into a bullet list.
2. **No dangling doc-comment blocks.** A doc-comment (javadoc,
   JSDoc, TSDoc, Python docstring) must immediately precede the
   declaration it documents. Refactors that insert a new declaration
   between a docblock and its original target orphan the docblock —
   move it back.
3. **No cross-tier symbol refs.** Doc-comment cross-reference syntax
   (javadoc `{@link}`, TSDoc `{@link}`) cannot reliably resolve symbols
   across source sets or visibility boundaries. Reference the type as
   inline code with a short explanatory note instead.
4. **No stale class refs.** When a class is renamed or its
   implementation changes, scan its doc-comments for any reference
   that has rotted (old name, "auto-config" when it became "autoconfig",
   descriptions of the previous approach).
5. **No rotted TODOs.** Before adding a `TODO(<TASK-ID>)`, verify the
   task exists. When reviewing, verify the referenced task is not
   already `DONE`. A rotted TODO either gets removed or its reference
   updated.
6. **British spelling** in prose (comments, doc-comments, Markdown
   docs). See [spelling-and-grammar-rules.md](spelling-and-grammar-rules.md)
   for the IT-term exception list and the compound-term rules
   (clean-up, autoconfigured, customiser, preloaded, preempt).
7. **Comma after conjunctive adverbs** at the start of a clause:
   "Instead, …", "However, …", "Therefore, …", "Hence, …", "Thus, …",
   "Indeed, …", "Similarly, …", "Consequently, …", "Furthermore, …",
   "Meanwhile, …", "Otherwise, …".
8. **Space between `§` and a quoted section name**: `§ "Wiring rationale"`,
   not `§"Wiring rationale"`.

## 2. Imports and symbol references

1. **No unused imports.** Every imported symbol must reference the file
   body. IDE / linter check; do not rely on it during a sweep.
2. **No wildcard imports** in languages that support them — list the
   types explicitly. Wildcards hide rename failures and bloat the
   compile-time symbol table.
3. **Prefer imports over inline fully-qualified names** at use sites.
   An inline `org.example.foo.Bar` (or equivalent) is a code smell —
   import the symbol once at the top of the file.
4. **Import ordering matches the project's formatter default.** Whether
   that's IntelliJ's Optimize Imports, `goimports`, Prettier's import
   sorter, or `ruff`, re-running the formatter on a file you just
   edited must produce zero diff.

## 3. General idiomatic code (language-agnostic)

1. **Prefer immutable data holders** (records, dataclasses, frozen
   objects) for value carriers with no behaviour beyond accessors.
2. **Prefer the standard library's collection-literal helpers** over
   constructor + add chains for compile-time-constant constants.
3. **Prefer switch expressions / pattern matching** over `if`/`else if`
   chains on a finite set, in languages that support them.
4. **Mark unused parameters explicitly** where the language has a
   convention (`_` in Python / Rust / Java unnamed pattern, leading
   underscore in JS/TS lint conventions).

(Stack-specific idioms — Java 21+ `.getFirst()`, TypeScript narrowing
patterns, etc. — live in the stack appendices below.)

## 7. Code smells

1. **No dead vars / write-only fields.** A field that is `.set(...)`
   but never read should be removed.
2. **No magic strings** repeated across switches / handlers / test
   assertions. Extract to constants or enums. Pick a single source of
   truth — a shared catalogue type — when the same set of values is
   referenced from several places.
3. **No hand-rolled JSON serialisation** when a JSON library is already
   on the classpath / in `node_modules`. Use the library.
4. **No `console.log` / `println` debug stragglers** in committed code,
   in production paths or in tests (with the deliberate exception of
   suppression-test fixtures that assert on error output).

## 8. Asynchronous waiting

1. **Use a polling library** (Awaitility for JVM, `vi.waitFor` /
   `@testing-library/dom`'s `waitFor` for JS/TS, `tenacity` for
   Python) for tests that wait on external state to change. Hand-rolled
   sleep-and-retry loops are a code smell.
2. **A bare `sleep` is acceptable only for wall-clock progress** — e.g.
   sleeping past MySQL's per-second `datetime` resolution before an
   `updated_at`-strictly-greater assertion. These cases are not
   pollable; document the wall-clock dependency.

## 9. SQL safety

1. **Parameterised queries** for any value that could come from user
   input. Never concatenate `" + userValue + "` into a query string.
2. **Suppress static-analysis flow warnings narrowly** when a test
   feeds `@ValueSource`-style hardcoded SQL into an executor. The
   suppression annotation belongs on the specific test method, not on
   the class.

## 10. Test-code quality

1. **Helpers, not copy-paste.** A 7+ line block that appears in two
   places becomes a private method. A block that appears in three
   places becomes a shared helper under the project's test-support
   directory.
2. **NPE-prone chains** like `response.getBody().get("foo")` (where
   `getBody()` is nullable) get an asserting helper that asserts
   non-null first and returns the typed view.
3. **Shared test fixtures** (containers, MSW handlers, sample data
   factories) live in one place and are reused. Verbatim object
   literals copy-pasted across tests are a refactor target.
4. **No `@only` / `.only` / `fdescribe` / `fit`** committed. These
   trim the suite silently. The reviewer rejects them as `must-fix`.

---

## Stack appendix: Java / Spring Boot

Keep this appendix if your project uses Java + Spring Boot. Delete it
if not.

### J1. Idiomatic Java

1. **`.getFirst()` over `.get(0)`** on `List` (Java 21+).
2. **`Set.of(...)` / `List.of(...)` / `Map.of(...)`** over
   `new HashSet<>()` etc. for compile-time-constant constants.
3. **Switch expressions** over `if`/`else if` chains on a finite set.
4. **Unnamed pattern `_`** for lambda / try-with-resources / catch
   parameters that are required by the signature but never used
   (Java 22+). `(req, res) -> { /* no-op */ }` → `(_, _) -> { /* no-op */ }`.
   `try (var scope = ...)` where `scope` is never read →
   `try (var _ = ...)`.
5. **`record` over a class** for immutable data holders. Records with
   one or two fields and no behaviour beyond the canonical accessors
   are the canonical form.
6. **`@SuppressWarnings("SameParameterValue")` is a last resort.**
   When the warning fires, it's a signal the parameter is
   over-generalised — the method pretends to be configurable but
   isn't. Prefer fixing the contract over suppressing the warning:
   - If the constant has its own dedicated meaning, **hardcode it
     inside the helper** (which often becomes more specific in
     return — `truncate(s, 200)` becomes `boundedMalformedJsonDetail(s)`).
   - Suppress only when the helper is genuinely a one-call-site-today,
     plausibly-more-tomorrow utility. Add the annotation plus a
     javadoc line saying which call site uses what value and why the
     param stays parametric.
7. **String-emptiness checks.** Pick the right idiom based on whether
   the value can be null:
   - When the value is guaranteed non-null, prefer `value.isBlank()`
     over `value.isEmpty()` so a whitespace-only string is treated as
     empty.
   - When the value can be null AND blank-equals-empty in the domain,
     prefer `!StringUtils.hasText(value)` (Spring's
     `org.springframework.util.StringUtils`) over
     `value == null || value.isBlank()`. `hasText` returns `false` for
     `null`, `""` and `"   "` alike.
   - Apache Commons Lang's `StringUtils.isBlank(...)` is functionally
     equivalent but its dependency is **not** on a typical Spring
     Boot classpath; do not introduce it.
8. **Collection/Map emptiness with null tolerance.** In production
   code use `CollectionUtils.isEmpty(coll)` /
   `CollectionUtils.isEmpty(map)` (Spring) instead of
   `coll == null || coll.isEmpty()`. In AssertJ test code use the
   built-in `assertThat(coll).isNullOrEmpty()`.
9. **`final` on all locals and method parameters** that are never
   reassigned — production and test code alike. Makes the "is this a
   one-time assignment or a re-binding?" question answerable at a
   glance.
10. **No `var` in Java** — always declare with the explicit type. The
    inferred type is easy to misread in diff reviews. Applies to
    production and test code.
11. **Import ordering matches IntelliJ's default *Optimize Imports*
    output**: (1) `java.*` / `javax.*` / `jakarta.*`, (2) all other
    non-static imports, (3) static imports — separated by blank lines.
    Within each group, sort alphabetically by FQN. Explicit imports
    over wildcard. Re-running *Optimize Imports* on a file you just
    edited must produce zero diff.

### J2. Lombok

1. **`@Setter` on the class + `@Setter(AccessLevel.NONE)`** on the
   immutable-after-construction fields. Never hand-write per-field
   setters that just do `this.x = x;` — they are byte-for-byte
   identical to what Lombok generates.
2. **JPA entities extend `BaseEntity<T>`** (or the project's
   equivalent base). Never use `@EqualsAndHashCode(of = "id")` on a
   JPA entity — it breaks for Hibernate proxies and for the
   transient-then-persistent identity transition. Use the Vlad
   Mihalcea recipe encoded in `BaseEntity`.
3. **`@RequiredArgsConstructor` for Spring services**, with `final`
   fields. No `@Autowired` on constructors.

### J3. Type safety / nullability (JSpecify)

1. **`@NullMarked` `package-info.java`** in any package whose classes
   override Spring/Jakarta methods declared in a `@NullMarked` parent
   package. The package-info goes on
   `src/main/java/.../package-info.java` with
   `@org.jspecify.annotations.NullMarked`. Without it, IntelliJ flags
   every override as "non-annotated parameter overrides @NullMarked
   parameter."
2. **`@Nullable` on genuinely nullable fields/params** — never just
   pass `null` to a parameter that's declared `@NonNull`. If the
   contract is wrong, fix the contract; if the call site has a
   non-null value handy, use that.
3. **Don't "fix" `@NullMarked`-induced "always-null" warnings by
   deleting the null check.** When the static analyser flags
   `if (x == null)` as always-false after a package becomes
   `@NullMarked`, the warning is *technically* correct against the
   current types. It's often *factually* wrong about the runtime, and
   sometimes *factually* correct (the check really is dead). Decide
   case-by-case:
   - **If the runtime really does flow null** — for a `ThreadLocal<T>`
     where `.get()` returns null after `.remove()`, or a parameter
     whose only caller passes a genuinely-nullable expression:
     declare the type honestly (`ThreadLocal<@Nullable T>`,
     `@Nullable T method(...)`). Now the check is meaningful and the
     compiler forces callers to handle the nullable case.
   - **If the runtime really doesn't flow null** — for a constructor
     parameter whose only callers pass a built collection, or a
     method that the `@NullMarked` package contract already guarantees
     non-null on: delete the check. The defensive guard was
     unreachable. The `@NullMarked` boundary is exactly the "trust the
     contract" line; don't double-guard inside it.

   Suppressing with `//noinspection ConstantValue` is the wrong answer
   in both cases — it leaves the misleading contract or the dead
   check in place.
4. **`@NullMarked` scope.** Inside a `@NullMarked` package the
   annotation applies to every reference-type usage in API signatures:
   method parameters, return types, field types, constructor
   parameters, type arguments (`List<Foo>` — `Foo` is also marked),
   wildcard bounds, type-variable bounds. It does NOT apply to local
   variables or method-implementation internals.

### J4. Spring Boot conventions

1. **`server.error.*` → `spring.web.error.*`** in YAML (Spring Boot 4).
   The old keys log a deprecation warning at level `error` and will
   be removed.
2. **Jackson 3** is `tools.jackson.databind.*`. Jackson 2 stays
   `com.fasterxml.jackson.databind.*` in test code that still uses
   Jackson 2 mixins. `JsonNode.asString()` is Jackson 3 only;
   `JsonNode.asText()` is Jackson 2.
3. **`HttpStatusCode.valueOf(int)`** when converting from a plain
   `int` status to Spring's typed status. Avoid `HttpStatus.valueOf`
   for the int form (`HttpStatus.valueOf(String)` takes a name).
4. **`@SuppressWarnings("SpringJavaInjectionPointsAutowiringInspection")`**
   on `@SpringBootTest` / `@WebMvcTest` / `@DataJpaTest` classes that
   use field injection (`@Autowired private Foo foo;`). The
   inspection misfires for test-only contexts.
5. **`@SuppressWarnings("resource")` is NOT needed on Testcontainers
   `*Container` fields.** Ryuk owns the lifecycle; newer Testcontainers
   versions no longer emit the warning.

---

## Stack appendix: TypeScript / React

Keep this appendix if your project uses TypeScript + React. Delete it
if not.

### T1. Type safety

1. **No `as any`** without an inline
   `// eslint-disable-next-line @typescript-eslint/no-explicit-any`
   comment and a brief reason. `as unknown as TargetType` is usually
   the right escape hatch for runtime-shape-only assertions in tests.
2. **No `@ts-ignore`** — use `@ts-expect-error` instead. It errors
   when the next-line error disappears, catching stale suppressions.

### T2. Test plumbing

1. **MSW URL builders** (`projectsListUrl()`, etc.) instead of inline
   `${env.VITE_API_URL}/v1/projects`. Fixture factories
   (`projectsPage()`, `emptyProjectsPage()`,
   `buildIntegrationTestStore()`) replace verbatim object literals.
2. **No `screen.debug()`** committed. Use it locally; remove before
   commit.

---

## How to use this checklist

**As an implementer**, run through it before marking a task ready for
review. The reviewer's bar is "would the linter / IDE flag this?" —
for every item on the list, look at the same diff the linter would.

**As the [code-reviewer agent](../agents/code-reviewer.md)**, this
checklist is your conformance bar. Every miss is at-least a
`should-fix` finding; correctness issues (NPE-prone chains, SQL safety,
deprecated APIs that will be removed) are `must-fix`.

**As the operator**, when you find a recurring pattern not on this
list, add it here — and update the deeper guide (testing-guide,
backend-code-layout-guide, …) in the same commit so the linkage stays
intact.
