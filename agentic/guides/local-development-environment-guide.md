# Local development environment guide

This guide is **project-agnostic**. It documents a proven pattern for bootstrapping
a working local development environment for any Spring Boot + Vite/React project
in this organisation, with support for both IntelliJ IDEA and plain-CLI Gradle.

The pattern is designed around three forces:

1. **Secrets must not be committed**, but the IDE and Gradle both need to see them
   at runtime.
2. **IntelliJ "Run" and "Debug" workflows must be one click** — not "one click after
   you remember to `source` something in a terminal first".
3. **The same secret value** (one random string of hex digits) must reach three
   consumers: the running JVM, the test-runner JVM, and any `docker-compose up`
   invocation. Duplication is a source of bugs; derive all three from one file.

## The pattern

```
repo-root/
├── .secrets/                    # values gitignored; directory itself is committed
│   ├── README.md                # committed; documents each secret
│   ├── db-creator.txt.example   # committed; placeholder value
│   └── db-creator.txt           # gitignored; real secret (one file per secret)
├── .run/                        # committed IntelliJ run configurations
│   ├── README.md                # committed; documents every run config
│   ├── Local - Run API.run.xml
│   ├── Local - Test API.run.xml
│   ├── Util - Set build environment.run.xml
│   └── …
├── scripts/
│   ├── generate-secret.sh       # one file per secret, random value
│   └── set-build-env.sh         # reads .secrets/*.txt → options.txt + gradle.properties.local
├── options.txt                  # gitignored; generated; `-DFOO=bar` per secret
├── gradle.properties.local      # gitignored; generated; `systemProp.FOO=bar` per secret
├── build.gradle                 # converts `systemProp.*` in the local file into test env vars
└── .gitignore                   # excludes .secrets/*, options.txt, gradle.properties.local, etc.
```

The **directory is committed** (with `README.md` plus `*.example`
placeholders) but each individual `<name>.txt` value file is
gitignored at the root `.gitignore`. This is the pattern the
worktree-bootstrap script ([setup-worktree.sh](../../scripts/setup-worktree.sh))
relies on: it cannot link the parent `.secrets/` directory because
the worktree already owns its tracked contents, so it links each
gitignored value file individually via `link_file_if_missing`.

### How the three consumers receive the same secret

1. **Spring Boot running from IntelliJ** — the "Local - Run API" run config passes
   `@options.txt` as its VM parameters. IntelliJ expands the file on launch, so
   each line becomes a JVM `-D` argument. Spring picks up the value through its
   standard property resolution.
2. **Gradle tests / `./gradlew test`** — `build.gradle` reads every
   `systemProp.FOO=bar` line out of `gradle.properties.local` and declares
   `environment 'FOO', 'bar'` on every `Test` task. Test code sees it as
   `System.getenv("FOO")` or — if the test also registers a Spring
   `@DynamicPropertySource` — as a Spring property.
3. **`docker-compose up`** — the compose file (or the overlay) references the
   same secret via `secrets:` + `MYSQL_*_PASSWORD_FILE: /run/secrets/*`. The
   compose secret is backed by the same `./.secrets/*.txt` file on disk; no
   copy, no sync.

Only the fourth consumer — an operator invoking `mysql` or `mysqldump` by hand —
needs to read the secret directly: `$(cat .secrets/db-root.txt)`. Scripts that
do this live in `./scripts/`.

### The five-file contract

| File                        | Committed? | Generated? | Consumed by                                       |
|-----------------------------|------------|------------|---------------------------------------------------|
| `.secrets/<name>.txt`       | No         | Yes (by `generate-secret.sh`) | docker-compose `secrets:` blocks; shell `$(cat …)` |
| `.secrets/<name>.txt.example` | Yes      | No         | Documentation; developers copy to `.txt` if not using the script |
| `options.txt`               | No         | Yes (by `set-build-env.sh`)   | IntelliJ "Run" / "Debug" via `@options.txt` VM flag |
| `gradle.properties.local`   | No         | Yes (by `set-build-env.sh`)   | `build.gradle` pass-through → test env vars        |
| `.run/*.run.xml`            | Yes        | No         | IntelliJ; declares `set-build-env.sh` as pre-task  |

## The two scripts

### `scripts/generate-secret.sh`

Creates a single secret file with a cryptographically random value:

```bash
./scripts/generate-secret.sh <name> [--overwrite]
```

- `<name>` is one of the project's allowed secret names (validated against an
  allowlist in the script).
- The file is written with mode `0600` and contains 48 hex chars (192 bits).
- Without `--overwrite`, an existing file is **not** replaced — rotation is an
  explicit choice.

Why a script instead of a `Makefile` target: shell scripts are debuggable step
by step; make targets are not. And secret generation is a single operation, not
a dependency graph.

### `scripts/set-build-env.sh`

Reads the secret files and regenerates the two IDE-facing files:

```bash
source scripts/set-build-env.sh     # interactive: also exports into your shell
scripts/set-build-env.sh            # non-interactive: only writes the files
```

- Runs fast (<100 ms) — safe to invoke as an IntelliJ "Pre-task" on every
  single run configuration. IntelliJ silently re-runs it before every launch,
  so a secret rotation is picked up on the next click.
- Truncates both `options.txt` and `gradle.properties.local` on each run —
  stale entries don't accumulate.
- Refuses to run if the project's primary DB secret is missing (clear error
  message telling you to `generate-secret.sh db-creator` first).

## IntelliJ run configurations

The `.run/` directory is **committed**. It holds one XML file per run config,
shared across developers. The critical elements inside each XML:

### Declaring the pre-task

Every Java/Gradle run config declares `Util - Set build environment` as its
pre-task via `<option name="RunConfigurationTask">`:

```xml
<method v="2">
    <option name="Make" enabled="true" />
    <option name="RunConfigurationTask" enabled="true"
            run_configuration_name="Util - Set build environment"
            run_configuration_type="ShConfigurationType" />
</method>
```

This is the whole magic. Every "Run" click implicitly runs the env-script first,
so `options.txt` and `gradle.properties.local` are always fresh.

### Passing `@options.txt` as VM parameters

Spring Boot run configurations:

```xml
<option name="VM_PARAMETERS" value="@options.txt" />
```

The `@file` syntax is Java's own "read args from file" — not an IntelliJ feature.
Each line of `options.txt` becomes one JVM argument.

### The utility shell run config

`Util - Set build environment.run.xml` wraps `scripts/set-build-env.sh` as an
IntelliJ "Shell Script" run config:

```xml
<configuration name="Util - Set build environment" type="ShConfigurationType">
    <option name="SCRIPT_PATH" value="$PROJECT_DIR$/scripts/set-build-env.sh" />
    <option name="SCRIPT_WORKING_DIRECTORY" value="$PROJECT_DIR$" />
    <option name="INTERPRETER_PATH" value="/bin/bash" />
    <option name="EXECUTE_SCRIPT_FILE" value="true" />
</configuration>
```

On Windows hosts with WSL, replace `INTERPRETER_PATH` with `wsl.exe` and set
`SCRIPT_PATH` to the WSL-style `\\wsl$\<Distro>\...` path. The
`.run.xml` files on disk look different between a pure-Linux and a WSL
developer, which is awkward — acknowledged, but the config is usually edited
rarely.

### The typical 15–20 configs per project

A complete `.run/` directory has configs grouped by purpose:

| Group           | Example configs                                                    |
|-----------------|--------------------------------------------------------------------|
| **Local**       | Run API · Test API · Test API Integration · Clean build API       |
| **Deploy**      | Deploy - Dev · Deploy - Dev (no build) · Deploy - Stage · Deploy - Prod |
| **DB**          | DB - Deploy Dev · DB - Deploy Stage · DB - Deploy Prod · DB - Reset Dev DB (DANGER) |
| **Util**        | Set build environment · Connect to Dev DB · Docker Logs · Docker Stop |
| **UI**          | Dev Server · Build                                                 |

Ship a `.run/README.md` mapping "I want to X" → "Run this" so a new developer
can be productive within ten minutes of opening the project.

## First-time setup for a new developer

```bash
# 1. Clone the repo.
git clone <url> && cd <repo>

# 2. Generate the database secrets.
./scripts/generate-secret.sh db-root
./scripts/generate-secret.sh db-creator
./scripts/generate-secret.sh db-api

# 3. Wire them into IntelliJ + Gradle.
source scripts/set-build-env.sh

# 4. Open in IntelliJ. Run configs in the top toolbar are ready to use.
```

No manual `.env` editing, no hand-written `gradle.properties.local`, no
copy-pasting passwords into Run Configuration VM options.

## Adapting this to a new project

1. **Copy `scripts/generate-secret.sh`** and change the `ALLOWED_NAMES` array
   to your project's secret names.
2. **Copy `scripts/set-build-env.sh`** and change the `SECRETS` associative
   array mapping — one line per secret-name → env-var-name.
3. **Copy `.gitignore` lines** for `.secrets/`, `options.txt`,
   `gradle.properties.local`, and an allowlist exception for `.run/`.
4. **Add the `systemProp.*` pass-through block** to `build.gradle`:
   ```groovy
   def localPropertiesFile = file('gradle.properties.local')
   if (localPropertiesFile.exists()) {
       def localProperties = new Properties()
       localProperties.load(new FileInputStream(localPropertiesFile))
       localProperties.each { key, value ->
           if (key.startsWith('systemProp.')) {
               def envVarName = key.substring('systemProp.'.length())
               tasks.withType(Test) {
                   environment envVarName, value
               }
           }
       }
   }
   ```
5. **Author one IntelliJ run config per lane** in `.run/`, each declaring
   `Util - Set build environment` as its pre-task. Start with "Local - Run
   API" and "Local - Test API"; add deploys and DB shortcuts later.

## Anti-patterns

- **Committing `options.txt` or `gradle.properties.local`.** These files have
  secrets in them by construction. Both belong in `.gitignore`.
- **Hand-editing `options.txt`.** It's regenerated on every
  `set-build-env.sh` run; changes vanish. Edit the `.secrets/*.txt` file
  instead.
- **Baking secrets into `.run/*.run.xml` as `envs`.** That commits secrets to
  git. The `@options.txt` indirection exists specifically to keep secrets out
  of committed files.
- **Adding a pre-task for `Util - Set build environment` via a git hook.**
  Hooks run on commit, not on IDE launch. The IntelliJ pre-task mechanism is
  the correct layer — use it.
- **Skipping the example files.** `.secrets/<name>.txt.example` with a
  placeholder value is how a new developer discovers a secret exists without
  having to grep the source tree.

## See also

- [Database scripts guide](database-scripts-guide.md) — the `./.secrets/` →
  Docker `secrets:` → `/run/secrets/*` wiring inside compose
- [Backend code layout guide](backend-code-layout-guide.md#gradlepropertieslocal--personal-overrides)
  — the `build.gradle` pass-through block in detail
- [Testing guide](testing-guide.md) — how integration tests read
  `<APP>_DB_PASSWORD` at runtime
