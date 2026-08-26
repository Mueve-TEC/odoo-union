def migrate(cr, _version):
    """uid field type changed from Char to Integer.

    Odoo's _auto_init handles the column type change
    (ALTER TABLE ... ALTER COLUMN uid TYPE int4 USING uid::int4).
    All existing values are guaranteed numeric by the previous
    isdigit() constraint, so the cast is safe.

    This script validates the precondition and aborts early if
    non-numeric data is found, giving a clear error instead of
    a cryptic PostgreSQL cast failure.
    """
    cr.execute("SELECT count(*) FROM affiliation_affiliate WHERE uid !~ '^[0-9]+$'")
    non_numeric = cr.fetchone()[0]
    if non_numeric:
        raise ValueError(
            f"Found {non_numeric} affiliate(s) with non-numeric uid. "
            "Fix them before upgrading (the uid column is changing from "
            "varchar to integer)."
        )
