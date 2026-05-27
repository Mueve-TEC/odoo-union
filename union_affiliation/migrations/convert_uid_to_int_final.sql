-- Final migration: convert affiliation_affiliate.uid from text to integer
-- IMPORTANT: Run on a test copy first. Backup DB before running.
-- This script:
-- 1) Saves original uid values
-- 2) Computes a normalized integer candidate (remove non-digits, strip leading zeros)
-- 3) Shows rows that cannot be normalized and duplicated normalized values
-- 4) Converts the column type if checks pass

BEGIN;

-- 1) Save original values
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='affiliation_affiliate' AND column_name='uid_old'
    ) THEN
        ALTER TABLE affiliation_affiliate ADD COLUMN uid_old text;
    END IF;
END $$;

UPDATE affiliation_affiliate SET uid_old = uid::text;

-- 2) Prepare a normalized integer candidate in a temp column
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='affiliation_affiliate' AND column_name='uid_temp'
    ) THEN
        ALTER TABLE affiliation_affiliate ADD COLUMN uid_temp integer;
    END IF;
END $$;

-- Build normalized value: remove non-digits, strip leading zeros. Empty -> NULL
UPDATE affiliation_affiliate
SET uid_temp = NULLIF(regexp_replace(regexp_replace(uid_old, '\\D', '', 'g'), '^0+', ''), '')::integer
WHERE uid_old IS NOT NULL;

-- 3) Validation queries (inspect results BEFORE proceeding):
-- Rows that had no digits (cannot be converted)
SELECT id, uid_old FROM affiliation_affiliate WHERE uid_old IS NOT NULL AND uid_temp IS NULL LIMIT 100;

-- Rows where normalization produced duplicates (will block UNIQUE constraints or logical expectations)
SELECT uid_temp AS normalized_uid, COUNT(*) FROM affiliation_affiliate WHERE uid_temp IS NOT NULL GROUP BY uid_temp HAVING COUNT(*) > 1 LIMIT 100;

-- Rows that would change because of stripped leading zeros (show example)
SELECT id, uid_old, uid_temp FROM affiliation_affiliate WHERE uid_old ~ '^0+' LIMIT 100;

-- If the above result sets are empty/acceptable, you can proceed to apply conversion.
-- Final conversion (only after manual verification):

-- Option A: Alter column type using the prepared uid_temp column
-- This keeps the column name and converts in-place (safer for dependent code objects)
ALTER TABLE affiliation_affiliate ALTER COLUMN uid TYPE integer USING (uid_temp);

-- Option B (alternative): Drop original and rename temp (uncomment if you prefer this flow)
-- ALTER TABLE affiliation_affiliate DROP COLUMN uid;
-- ALTER TABLE affiliation_affiliate RENAME COLUMN uid_temp TO uid;

-- OPTIONAL: add a NOT NULL constraint if you want to enforce presence
-- ALTER TABLE affiliation_affiliate ALTER COLUMN uid SET NOT NULL;

-- OPTIONAL: add a UNIQUE constraint on uid
-- ALTER TABLE affiliation_affiliate ADD CONSTRAINT unique_affiliate_uid UNIQUE (uid);

COMMIT;

-- Cleanup: remove helper columns if desired (run after confirming everything is OK)
-- ALTER TABLE affiliation_affiliate DROP COLUMN uid_old;
-- ALTER TABLE affiliation_affiliate DROP COLUMN uid_temp;

-- NOTES:
-- - This script removes all non-digit characters and leading zeros. If you prefer to abort instead of normalizing, inspect the first SELECT and fix those rows manually.
-- - Test carefully: run the SELECT queries and review edge cases (empty strings, '0000', dashes, letters).
-- - After migration, update any external CSV/XML import fixtures that provided string UIDs to use numeric values (no leading zeros).
