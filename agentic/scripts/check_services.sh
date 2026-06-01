#!/usr/bin/env bash
#
# Reports the up/down status of the local services this project depends
# on for tests and development. Designed to run as a **single bash
# invocation** so it can be allowlisted as one permission entry rather
# than triggering a prompt for each nested check — useful inside the
# orchestrator's integration / E2E pipeline phases.
#
# Exit code:
#   0 — all checks ran (regardless of up/down). Use --require to enforce.
#   1 — one or more services required via --require (or via the profile)
#       are down.
#
# Usage:
#   agentic/scripts/check_services.sh                    # report all known services
#   agentic/scripts/check_services.sh integration        # integration profile only
#   agentic/scripts/check_services.sh e2e                # e2e profile (typically wider)
#   agentic/scripts/check_services.sh --require <csv>    # require specific services
#
# Each check runs in well under a second; the script is safe to call
# repeatedly.
#
# -----------------------------------------------------------------------
# This is the project-agnostic template. Tailor the CONFIGURATION block
# below to your project's services. Everything outside that block is
# generic and should not need editing.
# -----------------------------------------------------------------------

set -u

CHECK_TIMEOUT=2

# =======================================================================
# CONFIGURATION — edit per project
# =======================================================================
#
# Add one entry per local service the project depends on. The associative
# arrays are keyed by short name (`mysql`, `redis`, `backend`, …); the
# script does a single TCP connect to HOSTS[name]:PORTS[name] for each.
# LABELS[name] is the human-readable string for the status row.
#
# Then list which short names belong to each profile under "Profiles".
# A profile is just a named subset; `--require` overrides whatever the
# profile implies.

declare -A HOSTS=(
  [mysql]="localhost"
  [mailpit]="localhost"
  [backend]="localhost"
  [frontend]="localhost"
)
declare -A PORTS=(
  [mysql]=3306
  [mailpit]=8025
  [backend]=8080
  [frontend]=3000
)
declare -A LABELS=(
  [mysql]="MySQL"
  [mailpit]="Mailpit (SMTP trap)"
  [backend]="Backend HTTP"
  [frontend]="Frontend dev server"
)

# Profiles — name → space-separated short names. The script accepts the
# profile name as a positional argument; pick the set that matches your
# project's integration / E2E stack.
declare -A PROFILES=(
  [integration]="mysql mailpit"
  [e2e]="mysql mailpit backend frontend"
  [all]="mysql mailpit backend frontend"
)

# =======================================================================
# Generic body — no per-project knobs below this line.
# =======================================================================

check_tcp() {
  local host=$1 port=$2
  # Prefer bash's built-in /dev/tcp so we depend on no external binary.
  (timeout "$CHECK_TIMEOUT" bash -c "exec 3<>/dev/tcp/${host}/${port}" 2>/dev/null) && return 0
  return 1
}

print_row() {
  local name=$1 status=$2 label=$3 host=$4 port=$5
  printf "%-10s %-6s %s (%s:%s)\n" "$name" "$status" "$label" "$host" "$port"
}

usage() {
  sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
}

# -- Argument parsing -----------------------------------------------------

profile=""
require_csv=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --require) shift; require_csv=$1 ;;
    --require=*) require_csv=${1#*=} ;;
    -h|--help) usage ;;
    -*) echo "Unknown option: $1" >&2; usage ;;
    *)
      if [[ -n "${PROFILES[$1]+set}" ]]; then
        profile=$1
      else
        echo "Unknown profile: $1 (valid: ${!PROFILES[*]})" >&2
        usage
      fi
      ;;
  esac
  shift
done

# Resolve service list from profile (or default to "all" if defined,
# else every key in HOSTS).
if [[ -n "$profile" ]]; then
  read -ra services <<< "${PROFILES[$profile]}"
elif [[ -n "${PROFILES[all]+set}" ]]; then
  read -ra services <<< "${PROFILES[all]}"
else
  services=("${!HOSTS[@]}")
fi

required=()
if [[ -n "$require_csv" ]]; then
  IFS=',' read -ra required <<< "$require_csv"
elif [[ -n "$profile" && "$profile" != "all" ]]; then
  required=("${services[@]}")
fi

# -- Run checks -----------------------------------------------------------

declare -A STATUS=()
for s in "${services[@]}"; do
  if check_tcp "${HOSTS[$s]}" "${PORTS[$s]}"; then
    STATUS[$s]="up"
  else
    STATUS[$s]="down"
  fi
  print_row "$s" "${STATUS[$s]}" "${LABELS[$s]}" "${HOSTS[$s]}" "${PORTS[$s]}"
done

# -- Enforce required services -------------------------------------------

missing=()
for r in "${required[@]}"; do
  if [[ "${STATUS[$r]:-down}" != "up" ]]; then
    missing+=("$r")
  fi
done

if [[ ${#missing[@]} -gt 0 ]]; then
  echo
  echo "Missing required service(s): ${missing[*]}" >&2
  exit 1
fi
