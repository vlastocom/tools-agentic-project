# Date and Time Guide

This guide defines the policies for handling date and time values across the project —
from the database through the REST / JSON API to the frontend.

## Core Policies

1. **The database stores all timestamps in UTC.** MySQL `datetime` columns hold UTC
   values. The JDBC connection is configured with `serverTimezone=UTC` and Hibernate
   with `hibernate.jdbc.time_zone=UTC`.
2. **The REST API carries timestamps and dates as ISO 8601 strings in JSON.** The
   OpenAPI schema declares them as `type: string, format: date-time` (timestamps) and
   `type: string, format: date` (business dates), so clients cannot send or receive
   malformed values. Timestamps include an explicit UTC indicator (the `Z` suffix,
   e.g. `2025-03-12T14:30:00Z`); business dates use the date-only format
   (e.g. `2025-03-12`).
3. **Business dates (date-only values with no time component) are timezone-agnostic.**
   A trade date of `2025-03-12` means the same calendar day everywhere in the world.
4. **All conversions between UTC and local time happen in the frontend.** The backend
   never converts to a local timezone.

## Two Value Types

| Aspect          | Timestamp                            | Business date         |
|-----------------|--------------------------------------|-----------------------|
| **Meaning**     | An instant in time                   | A calendar day        |
| **Examples**    | `createdAt`, `expiresAt`,            | `Task.startDate`,     |
|                 | `startedAt`, `occurredAt`            | `Sprint.endDate`      |
| **MySQL type**  | `datetime` (or `datetime(6)`)        | `date`                |
| **Java type**   | `OffsetDateTime`                     | `LocalDate`           |
| **Created via** | `OffsetDateTime.now(ZoneOffset.UTC)` | `LocalDate.now()`     |
| **OpenAPI**     | `string`, `format: date-time`        | `string`, `format: date` |
| **Wire format** | `2025-03-12T14:30:00Z`               | `2025-03-12`          |
| **TypeScript**  | `string` (parsed with `new Date()`)  | `string` (used as-is) |

## Database Layer

Use `datetime` for timestamps and `date` for business dates:

```sql
create table if not exists `Example`
(
    created_at datetime not null,                      -- UTC timestamp
    trade_date date     not null                       -- timezone-agnostic business date
);
```

Never use `timestamp` — MySQL silently converts `timestamp` columns based on the session
timezone, which undermines the UTC-everywhere policy.

Microsecond precision (`datetime(6)`) is appropriate where ordering matters
(audit trails, time-entry start/stop). Default precision (`datetime`, second-resolution)
is fine elsewhere.

## REST / JSON API

### Global Jackson configuration

Configure Jackson globally in `application.yml` so every timestamp field on every DTO
behaves identically:

```yaml
spring:
  jackson:
    serialization:
      write-dates-as-timestamps: false
    deserialization:
      adjust-dates-to-context-time-zone: false
    time-zone: UTC
```

With this config Spring Boot serialises `OffsetDateTime` as an ISO 8601 string
(`2025-03-12T14:30:00Z`) and `LocalDate` as `2025-03-12`.

### DTO fields

DTOs use `OffsetDateTime` for timestamps and `LocalDate` for business dates:

```java
public record TaskDto(
    Long id,
    String code,
    LocalDate startDate,
    LocalDate endDate,
    OffsetDateTime createdAt,
    OffsetDateTime updatedAt
) {}
```

### OpenAPI schema

SpringDoc auto-derives the format from the Java type. Where the default is insufficient
(e.g. for documentation), pin the schema explicitly:

```java
@Schema(type = "string", format = "date-time", example = "2025-03-12T14:30:00Z")
private OffsetDateTime createdAt;

@Schema(type = "string", format = "date", example = "2025-03-12")
private LocalDate startDate;
```

### Input validation

Jackson rejects malformed input at deserialisation with `400 Bad Request`. Strings
**without** an explicit offset (e.g. `2025-03-12T14:30:00`) must be rejected — ambiguous
timestamps must not be silently assumed to be UTC. The global configuration above,
combined with `OffsetDateTime` typing on the DTO field, achieves this without custom
coercion code.

Bean-validation annotations layer on top:

```java
public record CreateTaskInput(
    @NotNull LocalDate startDate,
    @NotNull OffsetDateTime dueAt
) {}
```

## Backend (Java / Spring Boot)

### Creating timestamps

Always pass `ZoneOffset.UTC` explicitly:

```java
final OffsetDateTime now = OffsetDateTime.now(ZoneOffset.UTC);
```

Never use `OffsetDateTime.now()` or `LocalDateTime.now()` without a zone — they use the
JVM's default timezone, which may differ between environments.

### Accepting timestamps from clients

The API accepts any valid ISO 8601 string **with an explicit offset** — both
`2025-03-12T14:30:00Z` and `2025-03-12T22:30:00+08:00` are valid and represent the same
instant. The service layer normalises to UTC before persisting:

```java
final OffsetDateTime utc = input.withOffsetSameInstant(ZoneOffset.UTC);
```

The API always **returns** timestamps in UTC (`Z` suffix), regardless of the offset the
client sent in the input.

### Business dates

Business dates use `LocalDate` and require no timezone handling:

```java
final LocalDate tradeDate = LocalDate.parse(input);  // "2025-03-12"
```

## Frontend (TypeScript / React)

### Displaying timestamps

The API returns UTC strings with a `Z` suffix. JavaScript's `Date` constructor correctly
interprets these as UTC and `toLocaleString()` converts to the user's local timezone:

```typescript
const formatTimestamp = (utcString: string): string => {
    return new Date(utcString).toLocaleString()
}

// "2025-03-12T14:30:00Z" → "12/03/2025, 22:30:00" in UTC+8
```

### Sending timestamps to the API

When the frontend needs to send a timestamp (rare — most timestamps are server-generated),
convert to UTC first:

```typescript
const utcString = new Date().toISOString()  // "2025-03-12T14:30:00.000Z"
```

### Displaying business dates

Business dates have no time component and must not be passed through `new Date()` (which
would add a midnight UTC time and potentially shift the displayed date in certain
timezones). Display them as-is or use a date-only formatter:

```typescript
const formatDate = (dateString: string): string => {
    const [year, month, day] = dateString.split('-')
    return `${day}/${month}/${year}`  // or use Intl.DateTimeFormat
}
```

## Summary of the Data Flow

```
Frontend (local time)
    ↓  new Date().toISOString() → "2025-03-12T14:30:00.000Z"
    ↓
REST / JSON API (Jackson deserialises → OffsetDateTime)
    ↓
Service layer (OffsetDateTime, always UTC)
    ↓
Hibernate (OffsetDateTime → datetime using hibernate.jdbc.time_zone=UTC)
    ↓
Database (datetime, UTC)
    ↓
Hibernate (datetime → OffsetDateTime at UTC)
    ↓
Service layer (OffsetDateTime, always UTC)
    ↓
REST / JSON API (Jackson serialises → "2025-03-12T14:30:00Z")
    ↓
Frontend — new Date(value).toLocaleString() → local time
```

## See Also

- [Database scripts guide](database-scripts-guide.md) — schema conventions
