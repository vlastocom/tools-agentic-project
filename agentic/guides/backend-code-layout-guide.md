---
stack: spring-boot-gradle-java
applies-to: Spring Boot + Gradle + Java projects
---

# Backend code layout guide

**Applicability:** Spring Boot + Gradle + Java backend. If your project's
backend is on a different stack (Node + Express, Python + FastAPI, Go +
chi, etc.), **delete this file at adoption time** and replace with the
stack-specific equivalent.

This guide defines how the project's Spring Boot backend is organised: the Gradle
source-set layout, how `main`, `test`, `integrationTest` and `testFixtures` relate,
the package-by-layer structure inside each source set, and the supporting build
configuration (JaCoCo coverage, Mockito agent, JVM options).

It applies to any Spring Boot / Java project in this organisation; the specifics
below (package names, Gradle version, Spring Boot version) are the current project's
values and kept current in [infrastructure-design.md §20.1](../../docs/infrastructure-design.md).

## Why four source sets

`src/main` alone forces a choice between two bad options: either fast unit tests live
next to the production code (and grow entangled with it), or they share a single
`src/test` folder with slow integration tests and you can't run the fast set
independently. The four-source-set split gives each kind of test its own lane:

| Source set        | Path                       | Speed          | What lives here                                                    |
|-------------------|----------------------------|----------------|--------------------------------------------------------------------|
| `main`            | `src/main/java`            | n/a            | Production code                                                    |
| `test`            | `src/test/java`            | milliseconds   | Unit tests — pure in-JVM, no database, no Spring context where avoidable |
| `integrationTest` | `src/integration-test/java`| seconds        | Full-stack tests against a real MySQL and a real Spring context    |
| `testFixtures`    | `src/testFixtures/java`    | n/a            | Shared test builders, test DTO factories, test-only helper classes consumed by both `test` and `integrationTest` |

A developer running `./gradlew test` should finish in under a minute and can
iterate; `./gradlew integrationTest` is reserved for pre-PR verification and CI.

## Gradle configuration

### Plugins

```groovy
plugins {
    id 'java'
    id 'java-test-fixtures'                         // enables the testFixtures source set
    id 'org.springframework.boot' version '4.0.5'
    id 'io.spring.dependency-management' version '1.1.7'
    id 'jacoco'
}
```

The `java-test-fixtures` plugin is the key. It:

- Creates the `src/testFixtures/java` source set automatically.
- Publishes fixtures as a separate JAR if needed (we don't publish, but the feature is
  there).
- Makes `test` and any custom test source set able to declare
  `testImplementation testFixtures(project)` to pull fixtures in.

### The `integrationTest` source set

```groovy
sourceSets {
    integrationTest {
        java {
            srcDir 'src/integration-test/java'
        }
        resources {
            srcDir 'src/integration-test/resources'
        }
        // main.output is pulled in transitively through `testFixtures(project)` below.
        // Do NOT add it explicitly — duplicate classpath entries confuse Spring and cause
        // double-schema-registration errors when a resource (e.g. an OpenAPI file) gets
        // enumerated twice.
        compileClasspath += configurations.testCompileClasspath
        runtimeClasspath += output + compileClasspath + configurations.testRuntimeClasspath
    }
}

configurations {
    integrationTestImplementation.extendsFrom testImplementation
    integrationTestRuntimeOnly.extendsFrom testRuntimeOnly
}
```

`integrationTestImplementation` inherits from `testImplementation` so every
`testImplementation` dependency is automatically available to integration tests —
typically `spring-boot-starter-test`, mocking libraries, assertion libraries. Only
the things that differ (real JDBC driver, extra awaitility helpers) need to be
declared separately.

### The task registration

```groovy
tasks.register('integrationTest', Test) {
    description = 'Runs integration tests against a real MySQL database'
    group = 'verification'

    testClassesDirs = sourceSets.integrationTest.output.classesDirs
    classpath = sourceSets.integrationTest.runtimeClasspath

    shouldRunAfter test    // ordering only; integrationTest is not a `dependsOn` of check

    useJUnitPlatform()

    // Mockito 5.x needs a Java agent rather than self-attachment on JDK 25.
    jvmArgs "-javaagent:${configurations.integrationTestRuntimeClasspath.find { it.name.contains('byte-buddy-agent') }}",
            "-Xshare:off"
}
```

Key decisions:

- **`shouldRunAfter test`, not `dependsOn`.** Unit tests failing does not stop you
  from running integration tests — sometimes the quickest debugging loop is
  "run the integration test alone and look at the MySQL state". If you want the
  strict chain, `./gradlew test integrationTest` does it explicitly.
- **`integrationTest` is not wired into `check`.** `check` runs `test` + JaCoCo +
  lint. Integration tests require a running MySQL; forcing them into the default
  build would break `./gradlew build` for anyone without a DB on hand. CI runs them
  as a separate pipeline step.
- **Mockito agent flag.** JDK 25 rejects Mockito's default self-attachment with a
  runtime warning that escalates in future JDKs. Applying `byte-buddy-agent` as a
  `-javaagent` is the forward-compatible fix.

### The `testFixtures` dependency wiring

```groovy
dependencies {
    // test source set: gets fixtures automatically via the java-test-fixtures plugin
    testImplementation 'org.springframework.boot:spring-boot-starter-test'

    // integrationTest source set: declare explicitly
    integrationTestImplementation testFixtures(project)
    integrationTestImplementation 'org.springframework.boot:spring-boot-starter-test'
    integrationTestCompileOnly   'org.projectlombok:lombok'
    integrationTestAnnotationProcessor 'org.projectlombok:lombok'
    integrationTestRuntimeOnly   'com.mysql:mysql-connector-j'
    integrationTestRuntimeOnly   'org.junit.platform:junit-platform-launcher'
}
```

Note the Lombok duplication — each source set needs its own
`compileOnly` / `annotationProcessor` declaration because Gradle does not inherit
annotation-processor configurations across source sets.

## Package-by-layer inside `main`

```
src/main/java/com/<org>/<project>/
├── <Project>Application.java            # Spring Boot entry point
├── audit/                            # AuditLog service, aspects, DTO
├── config/                            # @Configuration classes, property bindings
├── controller/                       # @RestController classes (inbound HTTP)
├── dto/                              # request / response DTOs
├── entity/                           # JPA @Entity classes (one per table)
├── exception/                        # custom exceptions and @ControllerAdvice
├── mapper/                           # entity ↔ DTO mappers (MapStruct or hand-rolled)
├── repository/                       # Spring Data repositories
├── service/                          # transactional business logic
├── security/                         # ingress filter, actor-header parsing
└── util/                             # cross-cutting helpers; keep thin
```

Conventions:

- **One public class per file.** Internals live as package-private sibling classes.
- **`entity.Task`**, **`dto.TaskDto`**, **`dto.CreateTaskInput`**, **`mapper.TaskMapper`**,
  **`repository.TaskRepository`**, **`service.TaskService`**, **`controller.TaskController`**.
  The consistent suffix makes IDE "open file by name" navigation trivial.
- **No circular dependencies across packages.** `controller` → `service` → `repository` →
  `entity`. `dto` and `mapper` are leaves. `util` depends on nothing inside the app.
- **No `common` or `shared` package.** These become dumping grounds. Put a class
  where its *primary* consumer lives; extract only when a third consumer arrives.

Package names are lowercase, singular. `service`, not `services`.

## Mirror layout in `test` and `integrationTest`

Both test source sets mirror `main`'s package structure, one test package per
production package. Test classes end in `Test` (unit) or `IntegrationTest`
(integration).

```
src/test/java/com/<org>/<project>/
├── controller/
│   └── TaskControllerTest.java        # @WebMvcTest or pure unit
├── service/
│   └── TaskServiceTest.java           # pure JUnit + Mockito
└── repository/
    └── TaskRepositoryTest.java        # @DataJpaTest with H2, if we keep H2 tests at all

src/integration-test/java/com/<org>/<project>/
├── controller/
│   └── TaskControllerIntegrationTest.java     # @SpringBootTest, real MySQL
├── service/
│   └── TaskServiceIntegrationTest.java
├── http/
│   └── HealthCheckIntegrationTest.java        # hits the actual HTTP port
└── testutil/
    └── TestDataCleanupHelper.java             # shared cleanup harness
```

See the [testing guide](testing-guide.md) and the
[database scripts guide §database/dev/integration-test](database-scripts-guide.md#databasedevintegration-test--junit-integration-test-cleanup)
for the per-class `.cleanup.sql` convention that `TestDataCleanupHelper` drives.

## `testFixtures` — what goes there

Only code that is **useful to more than one test source set** belongs in
`testFixtures`. In practice that is:

- **Entity / DTO builders** — fluent, default-populated factories like
  `TaskFixtures.defaultTask().withCode("AUTH-01-0001").build()`.
- **Reusable JSON test payloads** for API tests, loaded from
  `src/testFixtures/resources/fixtures/*.json`.
- **Domain-specific assertions** — e.g.
  `TaskAssertions.assertTaskClosed(task)` that wraps several AssertJ assertions.
- **Fake implementations** that neither `test` nor `integrationTest` owns
  exclusively (rare).

If only unit tests need it, keep it in `src/test/java`. If only integration tests
need it, keep it in `src/integration-test/java`. Moving to fixtures is a deliberate
promotion — not the default location.

```
src/testFixtures/java/com/<org>/<project>/
├── fixtures/                 # entity and DTO builders
│   ├── TaskFixtures.java
│   └── ProjectFixtures.java
└── assertions/               # AssertJ extensions
    └── TaskAssertions.java
```

## Resources per source set

Each source set has its own `resources/` folder. The classpath precedence is
intuitive: the running source set's resources come first, so an
`application-integration-test.yml` under `src/integration-test/resources/` wins over
`application.yml` from `src/main/resources/` when the integration-test profile is
active.

| Path                                           | Contents                                                |
|------------------------------------------------|---------------------------------------------------------|
| `src/main/resources/application.yml`           | Default Spring config                                   |
| `src/main/resources/application-{dev,stage,prod}.yml` | Profile-specific overrides                       |
| `src/main/resources/logback-spring.xml`        | Log config (JSON encoder in prod, pretty in dev)        |
| `src/main/resources/db/migration/`             | Flyway migrations if we adopt Flyway (see §migrations)  |
| `src/test/resources/application-test.yml`      | Unit-test profile (H2 if used; disable SQL logging)     |
| `src/integration-test/resources/application-integration-test.yml` | Integration-test profile (real MySQL URL) |

## JaCoCo coverage

```groovy
jacoco {
    toolVersion = '0.8.14'
}

jacocoTestReport {
    dependsOn test
    reports {
        xml.required = true
        html.required = true
        csv.required = false
    }
    afterEvaluate {
        classDirectories.setFrom(files(classDirectories.files.collect {
            fileTree(dir: it, exclude: [
                '**/entity/**',
                '**/config/**',
                '**/dto/**',
                '**/<Project>Application.class',
            ])
        }))
    }
}

jacocoTestCoverageVerification {
    dependsOn jacocoTestReport
    violationRules {
        rule {
            limit {
                minimum = 0.70
            }
        }
    }
}

test {
    finalizedBy jacocoTestReport
}
```

Exclusions:

- **`entity`** — JPA entities are mostly getters/setters; Lombok generates the real
  code. Testing them adds noise without catching bugs.
- **`config`** — Spring configuration classes; exercised implicitly by any
  `@SpringBootTest`.
- **`dto`** — similar rationale to entities; data holders.
- **`<Project>Application`** — `main()` wrapper, trivially exercised on startup.

The 70% threshold applies to remaining code — `service`, `controller`, `mapper`,
`util`, `security`, `audit`, `exception`. In practice these tend to be higher
(85–95 %).

**Integration-test coverage is not counted.** The report is `test`-only. Integration
tests exist to catch integration bugs, not to pad coverage; if a line is only ever
exercised by an integration test, that's a hint the unit-test gap is real.

## `gradle.properties`

```properties
org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m --enable-native-access=ALL-UNNAMED
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.daemon=false

org.gradle.java.installations.auto-detect=true
org.gradle.java.installations.auto-download=true

version=0.1.0.0
```

- **`org.gradle.daemon=false`** — in CI and on the Synology NAS the daemon is more
  trouble than it's worth (stale state, memory pressure). Locally a developer can
  opt back in via `gradle.properties.local`.
- **`--enable-native-access=ALL-UNNAMED`** — silences JDK 25's warnings about
  reflective native access from dependencies (Netty, BouncyCastle if used).

### `gradle.properties.local` — personal overrides

Gitignored. A developer can override any property locally (e.g. re-enable the daemon,
bump heap for their machine), and — cleverly — set `systemProp.*` values that the
`build.gradle` pass-through block converts into test `environment` variables:

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

Meaning: putting
`systemProp.<APP>_DB_PASSWORD=secret` in `gradle.properties.local` gets the test
runner to see `<APP>_DB_PASSWORD=secret` in the environment, without that secret
ever touching the committed config.

## `bootRun` tuning

Spring Boot's default `bootRun` sets `-XX:TieredStopAtLevel=1` for faster startup.
That's fine for a quick `Ctrl-C` experiment but crippling when you're running `bootRun`
as a backend for an E2E test suite — cryptographic operations (password hashing, JWT
signing) slow by an order of magnitude with tier-1-only JIT. Always:

```groovy
bootRun {
    optimizedLaunch = false
}
```

Trade 5–10 s of startup for a correct JIT.

## Command cheat sheet

| Goal                                | Command                                                      |
|-------------------------------------|--------------------------------------------------------------|
| Unit tests (fast)                   | `./gradlew test`                                             |
| Integration tests                   | `./gradlew integrationTest`                                  |
| Both (sequenced)                    | `./gradlew test integrationTest`                             |
| All verification, default build     | `./gradlew check`                                            |
| Coverage report (HTML)              | `./gradlew jacocoTestReport` (opens `build/reports/jacoco/test/html/index.html`) |
| Enforce 70 % floor                  | `./gradlew jacocoTestCoverageVerification`                   |
| Build deployable JAR                | `./gradlew bootJar`                                          |
| Run the app locally                 | `./gradlew bootRun`                                          |
| Clean                               | `./gradlew clean`                                            |

## Anti-patterns

- **Dumping everything into `src/test`.** Slow Spring-context tests gate the fast
  unit-test loop; engineers stop running tests. Move them to `integrationTest`.
- **Duplicating fixtures across source sets.** The `testFixtures` source set
  exists precisely for this. If a builder appears in both `src/test` and
  `src/integration-test`, promote it.
- **Making `check` depend on `integrationTest`.** Breaks the quick build for
  anyone without a database. Run integration tests as a separate CI step.
- **Silent test dependencies on `main` code's static state.** Tests should set up
  their own state via fixtures. If a test fails depending on execution order,
  investigate before "fixing" with a sleep.
- **Cross-layer imports (`repository` → `service`, `dto` → `entity`).** Strictly one
  direction: `controller → service → repository → entity`. DTOs and mappers form a
  leaf. Violations show up as circular dependencies in the IDE.

## See also

- [Testing guide](testing-guide.md) — unit / integration / E2E boundaries, when to
  use which
- [Database scripts guide](database-scripts-guide.md) — the `cleanup.sql` per-class
  convention integration tests rely on
- [Frontend code layout guide](frontend-code-layout-guide.md) — the UI counterpart
