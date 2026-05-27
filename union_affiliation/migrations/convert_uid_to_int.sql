-- Migration: convert affiliation_affiliate.uid from text to integer
-- 1) BACKUP your DB before running anything!
-- 2) Run these steps in a transaction for safety, inspect the results, then commit.

BEGIN;
-- Save original values for auditing
ALTER TABLE affiliation_affiliate ADD COLUMN uid_old text;
UPDATE affiliation_affiliate SET uid_old = uid::text;

-- Create a cleaned integer candidate column (remove non-digits)
ALTER TABLE affiliation_affiliate ADD COLUMN uid_temp integer;
UPDATE affiliation_affiliate SET uid_temp = NULLIF(regexp_replace(uid_old, '\\D', '', 'g'), '')::integer;

-- 3) Validation queries (run and inspect results):
-- Rows that had non-numeric content that could not be converted
SELECT id, uid_old FROM affiliation_affiliate WHERE uid_old IS NOT NULL AND uid_temp IS NULL LIMIT 100;

-- Duplicated cleaned values (will block final conversion)
SELECT uid_temp, COUNT(*) FROM affiliation_affiliate WHERE uid_temp IS NOT NULL GROUP BY uid_temp HAVING COUNT(*) > 1 LIMIT 100;

-- If both result sets are empty/acceptable, you can proceed to apply conversion.
-- Final conversion (only after manual verification):
-- Note: this will remove any non-digit characters and cast to integer. Keep backup!
ALTER TABLE affiliation_affiliate ALTER COLUMN uid TYPE integer USING (NULLIF(regexp_replace(uid::text, '\\D', '', 'g'), '')::integer);

-- Optionally create an index/constraint (example unique):
-- ALTER TABLE affiliation_affiliate ADD CONSTRAINT unique_affiliate_uid UNIQUE (uid);

COMMIT;

-- After running migration, remove temporary columns if desired:
-- ALTER TABLE affiliation_affiliate DROP COLUMN uid_old;
-- ALTER TABLE affiliation_affiliate DROP COLUMN uid_temp;
