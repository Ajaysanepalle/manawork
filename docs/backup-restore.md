# Backup and Restore

The local Compose PostgreSQL volume is disposable development data, not a backup. UAT and production use external databases, so configure backup policy on the selected managed PostgreSQL provider before deployment.

Minimum production target: encrypted daily full backups, point-in-time recovery where the provider supports it, a separately protected backup account/location, and documented retention approved for the data policy. Keep UAT backups separate from production backups. Never restore production personal data into UAT.

Suggested operator procedure (replace placeholders with the provider-approved endpoint and secret source):

1. Confirm the backup timestamp, database identity, encryption, and restore point.
2. Restore to an isolated temporary database using the provider's documented recovery workflow.
3. Verify schema revision, row counts, and application connectivity without exposing personal records.
4. Obtain approval before changing production traffic or replacing the current database.
5. Record the restore operator, timestamps, source backup, verification, and outcome.

Example logical export for a controlled local database only:

```powershell
pg_dump --format=custom --no-owner --file=manaworks.dump $env:DATABASE_URL
pg_restore --list manaworks.dump
```

No production backup provider or automated retention job is configured in this repository. Define RPO/RTO with the service owner and test recovery regularly before launch.