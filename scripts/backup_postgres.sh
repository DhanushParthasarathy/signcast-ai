#!/usr/bin/env sh
set -eu

BACKUP_DIR="${BACKUP_DIR:-/backups}"
POSTGRES_DB="${POSTGRES_DB:-signcast}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
FILE="${BACKUP_DIR}/signcast-${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"
pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" | gzip > "${FILE}"
find "${BACKUP_DIR}" -name "signcast-*.sql.gz" -mtime +14 -delete

echo "Created ${FILE}"
