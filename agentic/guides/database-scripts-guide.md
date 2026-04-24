# Database Scripts Guide

This is the guide to the database scripts in this project. It defines the directory
layout, deployment mechanism, formatting conventions, and the different kinds of scripts —
production initialisation, migrations, E2E fixtures, and integration-test cleanup.

## Directory structure

All database scripts live under `database/` in the project root:

```
<project-root>/
├── database/
│   ├── clean/                   # Production initialisation — runs on first DB boot
│   ├── migrations/              # Schema and data migrations, one folder per date
│   ├── stage/                   # Scripts used to populate the staging environment
│   └── dev/
│       ├── e2e/                 # Fixtures loaded before Playwright E2E test runs
│       └── integration-test/    # Per-class cleanup scripts for JUnit integration tests
└── database/db-config-file.cnf  # MySQL server config mounted into the container
```

## How `database/clean/` gets executed

The MySQL official Docker image runs every `*.sql`, `*.sql.gz`, and `*.sh` file inside
`/docker-entrypoint-initdb.d/` in **alphabetical order** on first container start (i.e. when
the data volume is empty).

The compose file mounts `database/clean/` into that directory read-only:

```yaml
volumes:
    - db-data:/var/lib/mysql:rw
    - ./database/clean:/docker-entrypoint-initdb.d:ro
    - ./database/db-config-file.cnf:/etc/mysql/conf.d/config-file.cnf:ro
```

This means:

* The folder you see in git **is** the deployment artefact — no Flyway, no custom bootstrap.
* Ordering is controlled by numeric filename prefixes (`01-`, `02-`, …). Pad with zeroes so
  alphabetical sort matches numeric sort (use `01-` / `02-` if more than 9 files, so `10-`
  does not collide with `1-`).
* `docker compose down -v && docker compose up` wipes the volume and re-runs every script
  from scratch. That is the "completely wipe and reinitialise" button.

## Purpose of each directory

### `database/clean/` — production initialisation

Initialises an empty database to its vanilla production state. Typical breakdown:

```
database/clean/
├── 01-schema.sql                # The entire schema — one file, all tables
├── 02-seed-reference-data.sql   # Production reference rows (optional)
├── 03-copy-api-secret.sh        # Copies the API user password secret into place
├── 04-create-api-user.sql       # Creates the restricted application DB user, grants perms
└── 05-remove-api-secret.sh      # Removes the password file once the user has been created
```

Principles:

* **One consolidated `01-schema.sql` for the whole schema.** Group tables by subsystem with
  banner comments (see formatting conventions below), not by separate files. Rationale: the
  whole schema is reviewed as one unit; cross-table FKs and naming consistency are easier to
  verify when everything is in one place; evolution happens in `migrations/`, so `clean/`
  churn is low.
* **Reference data the application needs to boot** goes in `02-seed-reference-data.sql` (or
  similar). Do **not** put dev/test fixtures here.
* **Secrets** are read from `/run/secrets/` (mounted by Docker Compose) via a short shell
  step that copies the secret to `/var/lib/mysql-files/` (the only location MySQL's
  `LOAD_FILE()` is allowed to read from) and a second step that removes it after the user
  has been created. See `copy-api-secret.sh` / `remove-api-secret.sh` in the nest project
  for the pattern.
* **Application DB user with least-privilege grants** — see "Database users" below.

#### Database users

This project uses three MySQL accounts, each with a different blast radius. The privilege
boundary is a policy guarantee, not a convention — it is enforced by the database, not
by code.

| Account   | Purpose                                | DDL | DML on business tables        | Audit tables                     |
|-----------|----------------------------------------|-----|-------------------------------|----------------------------------|
| `root`    | DBA — emergency / administrative       | ✔   | ✔                             | `SELECT, INSERT, UPDATE, DELETE` |
| `creator` | Schema owner — migrations, test resets | ✔   | ✔                             | `SELECT, INSERT, UPDATE, DELETE` |
| `api`     | Application runtime (Spring Boot)      | ✘   | `SELECT, INSERT, UPDATE, DELETE` on every business table | **`SELECT, INSERT` only** (no `UPDATE`, no `DELETE`) |

The Spring Boot application connects exclusively as `api`. This means:

* **History is tamper-proof at the DB level.** A SQL-injection escape reaching the audit
  table could at worst append a row — it could not modify or remove an existing one.
* **Application-level cascading deletes leave audit rows behind.** The cascade protocol
  runs as `api`; it can delete business rows but the audit rows it inserts along the way
  are permanent at the DB level.
* **Integration-test cleanup scripts run as `creator`**, because they must
  `DELETE FROM <audit-table>` between methods. The `api` user cannot.

The per-table grants are written out explicitly in the `create-api-user.sql` script —
one `GRANT` per table — so adding a new table forces a deliberate grant addition in the
same migration. A table that is silently `SELECT`-only because we forgot to grant write
is a visible, loud failure in integration tests, not a silent production bug.

The `api` user also needs `CREATE TEMPORARY TABLES` and `LOCK TABLES` on the schema to
support Spring Data's query mechanics.

### `database/migrations/` — schema and data evolution

Scripts that migrate an existing database from one version to the next.

* **One folder per migration set, named `YYYY-MM-DD/`.** If more than one distinct set is
  applied on the same day, use `YYYY-MM-DD-HH-MM-SS/`.
* Each folder contains one or more numbered scripts (`01-…`, `02-…`, …) executed in order.
* **State the desired outcome** in a comment at the top of each script.
* **Link to the backlog task** (`AUTH-0042`) in the same header comment.
* Migrations may **assume the production schema is in the pre-migration state** — unlike
  everything else in the `database/` tree, migrations are not idempotent in the
  "can-be-run-on-any-state" sense. They are idempotent in the "safe to re-run once applied"
  sense: use `alter table … add column if not exists`, etc., where MySQL supports it.

### `database/stage/` — staging environment

Scripts that populate the staging environment from real data (e.g. a sanitised production
dump). Contents are unspecified until we have a staging environment. This is also where
ad-hoc restore scripts live if we need to load a dump into stage for reproducing an
incident.

### `database/dev/e2e/` — Playwright E2E fixtures

Pre-populates the development database with the deterministic set of entities the
Playwright E2E suite asserts against. Use numbered prefixes (`01-initialise.sql`, …).

* **Preserve the `root` user.** The E2E script wipes test data but never touches the root
  user or the API user — those are created by `clean/` and must survive.
* **Fixture-isolation rules:** mutation-heavy specs claim dedicated fixture users/projects
  so that concurrent E2E specs never contend for the same state. Document the ownership in
  a comment next to each fixture ID. (See nest's `01-initialise.sql` for the shape of this.)

### `database/dev/integration-test/` — JUnit integration-test cleanup

One file per integration-test class, named `<ClassName>.cleanup.sql`. The test base class
runs it in `@BeforeEach` (or `@BeforeAll` where sensible) to restore a known baseline.

* **Uses the `creator` DB user**, not the `api` user. `api` cannot delete from the audit
  table (audit is append-only for the API); `creator` can.
* **Delete in reverse-FK order** — children first, parents last. Keep the order explicit and
  commented so a reader can see why the sequence is what it is.
* **Preserve the `root` user** (`delete from User where id != @rootId`).
* **Re-delete the audit table after the other deletes** to catch any `@Async` audit writes
  that landed after the first pass.
* **Retry on FK violations with short backoff** — concurrent `@Async` audit writes can land
  between deletes. The test helper should retry briefly on MySQL error `1451` before
  failing. (See `TestDataCleanupHelper` in the nest project.)

## Formatting and style guidelines

### File and directory names

1. Use `kebab-case` for file and directory names.
2. Avoid spaces or special characters.
3. **Numeric prefixes** for ordered scripts: `01-…`, `02-…`. Pad with zeroes so alphabetical
   sort matches numeric sort.
4. **Temporal prefixes** for date-bound scripts:
    * `YYYY-MM-DD-script-name.sql` — up to one per day
    * `YYYY-MM-DD-HH-MM-SS-script-name.sql` — otherwise (24-hour format, zero-padded)
5. Numeric and temporal prefixes can combine — the migration subdirectory gets the date, the
   scripts inside get numeric prefixes.

### Date and time columns

Use `datetime` for timestamps and `date` for business dates. Never use `timestamp` — MySQL
silently converts `timestamp` columns based on session timezone, which undermines the
UTC-everywhere policy. See the [date and time guide](date-time-guide.md) for the full
policy.

### SQL code conventions

1. `;` terminates every statement.
2. `--` for single-line comments, `/* … */` for multi-line.
3. **`lowercase` for SQL keywords** (`create table`, `select`, `insert into`).
4. **`PascalCase` for table names** — plural nouns (`Projects`, `Areas`, `Epics`, `Tasks`,
   `TimeEntries`, `AuditLogs`).
5. **`snake_case` for column names** (`created_at`, `assignee_name`, `next_epic_seq`).
6. **Constraint and index names** embed the table (PascalCase) and column(s) (snake_case):
    * `fk_<TableName>_<column>` — foreign keys
    * `uq_<TableName>_<purpose>` — unique constraints (use `purpose` when the column list
      alone is unclear, e.g. `uq_Epics_area_code` rather than listing three columns)
    * `chk_<TableName>_<purpose>` — check constraints
    * `idx_<TableName>_<purpose>` — regular indexes
    * `ft_<TableName>_<cols>` — `FULLTEXT` indexes
7. **Parentheses in long statements:**
    * Opening `(` on a new line, aligned with the `create table` keyword.
    * Content indented by 4 spaces.
    * Closing `)` on its own line, aligned with the opening.
    * Align column names and their types with spaces.

```sql
create table if not exists `Areas`
(
    id              bigint unsigned not null auto_increment,
    project_id      bigint unsigned not null,
    code            varchar(32)     not null,
    name            varchar(200)    not null,
    next_epic_seq   int unsigned    not null default 0,
    created_at      datetime        not null default current_timestamp,
    updated_at      datetime        not null default current_timestamp on update current_timestamp,
    version         bigint unsigned not null default 0,
    primary key (id),
    constraint fk_Areas_project_id foreign key (project_id) references `Projects` (id),
    constraint uq_Areas_project_code unique (project_id, code)
) engine = innodb
  row_format = dynamic
  default charset = utf8mb4
  collate = utf8mb4_0900_ai_ci;
```

8. **Group tables by subsystem** in `01-schema.sql` with banner comments:

```sql
/*****************************************************************************/
/* Projects, areas, epics                                                    */
/*****************************************************************************/
```

9. **Character set and collation.** Every table is `utf8mb4` / `utf8mb4_0900_ai_ci`,
   accent-insensitive and case-insensitive, matching the application layer's
   case-insensitive comparisons.
10. **Storage engine and row format.** `engine = innodb`, `row_format = dynamic` — required
    for the large `varchar` / `text` columns we use and for online DDL support.

## Functional guidelines

1. **Single purpose per script.** If a script does multiple disjointed things, split it.
2. **Purpose in the header.** File name captures the summary; a comment block at the top
   states the longer intent — and for migrations, links the backlog task.
3. **Idempotent by default.**
    * `create table if not exists`, `create index if not exists`, `create fulltext index if
      not exists`, `drop … if exists` where the script could run more than once.
    * For data population, `delete from … where true;` (or `truncate`) before inserting.
    * **Exception:** migration scripts assume the pre-migration state and need not be
      idempotent in the "safe to run on any state" sense.
4. **Wrap data-population scripts in a transaction** (`start transaction; … commit;`) so
   partial failures don't leave inconsistent state. DDL in MySQL autocommits, so the
   transaction wrapper only applies to DML scripts.
5. **End every script with a verification `select`.** A short status query (e.g.
   `select 'API user created successfully' as status;`, or counts of inserted rows) makes it
   easy to confirm the script succeeded by reading the init log.

## See also

* [Date and time guide](date-time-guide.md) — `datetime` / `date` usage, UTC policy
* [Testing guide](testing-guide.md) — how `dev/integration-test/` cleanup scripts fit into
  the JUnit base class, how `dev/e2e/` fixtures are loaded before Playwright runs
