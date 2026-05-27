Migration checklist: convert `affiliation_affiliate.uid` from text to integer

Prerequisites

- Work on a copy of production DB. Backup first.
- Ensure code changes in this branch are deployed (models using Integer for `uid`).
- Stop incoming imports while migrating.

Steps (recommended order)

1) Backup DB

```bash
pg_dump -U <dbuser> -h <dbhost> -Fc <dbname> > backup_$(date +%F).dump
```

1) Run the normalization & validation queries (preview)

- Run the SQL in `convert_uid_to_int_final.sql` up to the SELECTs (DO NOT COMMIT yet) to inspect problematic rows.

Quick psql commands to run the SELECTs only:

```sql
-- Rows not convertible (no digits)
SELECT id, uid AS uid_old FROM affiliation_affiliate WHERE uid IS NOT NULL AND regexp_replace(uid::text, '\\D', '', 'g') = '' LIMIT 200;

-- Duplicated normalized values
SELECT (NULLIF(regexp_replace(uid::text, '\\D', '', 'g'), ''))::integer AS normalized_uid, COUNT(*) FROM affiliation_affiliate WHERE regexp_replace(uid::text, '\\D', '', 'g') <> '' GROUP BY normalized_uid HAVING COUNT(*) > 1 LIMIT 200;

-- Examples with leading zeros
SELECT id, uid AS uid_old, regexp_replace(uid::text, '^0+', '') AS stripped FROM affiliation_affiliate WHERE uid::text ~ '^0+' LIMIT 200;
```

If the result sets are empty (or acceptable after manual fixes), proceed.

1) (Optional) Fix problematic rows manually

- Update rows with letters, dashes or empty strings, or decide mapping.

1) Run the full migration SQL on test DB

```bash
psql -U <dbuser> -h <dbhost> -d <dbname> -f union_affiliation/migrations/convert_uid_to_int_final.sql
```

1) Restart Odoo and update modules

```bash
# Example systemd service
systemctl restart odoo
# Or if running via script, restart the process

# Update module in Odoo shell or via CLI
# Using Odoo CLI:
/path/to/odoo-bin -c /etc/odoo/odoo.conf -d <dbname> -u union_affiliation,union_benefit_request,union_contribution,union_school_position
```

1) Verification queries

```sql
-- Ensure uid is integer
SELECT column_name, data_type FROM information_schema.columns WHERE table_name='affiliation_affiliate' AND column_name='uid';

-- Sample checks
SELECT id, uid FROM affiliation_affiliate ORDER BY id LIMIT 20;

-- Ensure no duplicates if UNIQUE constraint added
SELECT uid, COUNT(*) FROM affiliation_affiliate GROUP BY uid HAVING COUNT(*) > 1;
```

1) Run app-level tests / manual flows

- Search affiliates by UID in UI
- Run imports (small sample files)
- Create new affiliate with numeric UID
- Create benefit request and contributions referencing UID

Rollback plan

- If things go wrong, restore DB from dump:

```bash
pg_restore -U <dbuser> -h <dbhost> -d <dbname> backup_YYYY-MM-DD.dump
```

Notes and hints

- The migration script strips non-digits and leading zeros. If you want to preserve leading zeros, do NOT apply automatic normalization — instead fix rows manually and alter type.
- After migration, update external fixtures (XML/CSV) and integrations to send numeric UIDs without leading zeros.
- Consider adding a UNIQUE constraint after verifying duplicates are resolved.
