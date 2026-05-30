# Backup Strategy

## PostgreSQL

- Use Supabase automated daily backups.
- Run an additional scheduled `pg_dump` using `scripts/backup_postgres.sh` before releases.
- Store backups in encrypted object storage with at least 14 days of retention.

## Storage

- Keep original sign clips and generated sequence outputs in separate buckets.
- Replicate reviewed sign clips to durable object storage when traffic grows.
- Generated videos can be regenerated from gloss tokens and dictionary clips, so they can use shorter retention.

## Restore Drill

- Restore latest backup to a staging Supabase project.
- Run migrations.
- Verify login, article read, feedback, dictionary lookup, and sequence playback.
- Document restore time and any manual remediation steps.
