from odoo import fields


class BigInteger(fields.Integer):
    """Integer stored in a bigint column (int8) instead of int4.

    Odoo 19 only ships ``fields.Integer``, pinned to an int4 column, so a CUIT
    (11 digits, about 2.7e10) does not fit in the affiliate UID. This keeps the
    ORM type as ``integer`` (related fields, search, the web client and the
    import converter keep working) and only widens the SQL column.
    """

    _column_type = ("int8", "int8")
