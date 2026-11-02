def _free_code(value, taken):
    suffix = 2
    while f"{value}_{suffix}" in taken:
        suffix += 1
    return f"{value}_{suffix}"


def _free_name(value, taken):
    suffix = 2
    while f"{value} ({suffix})" in taken:
        suffix += 1
    return f"{value} ({suffix})"


def migrate(cr, version):
    if not version:
        return

    cr.execute("SELECT to_regclass('school_position_type')")
    if not cr.fetchone()[0]:
        return

    cr.execute("SELECT id, code, name FROM school_position_type ORDER BY id")
    rows = cr.fetchall()

    taken_codes = {code for _id, code, _name in rows if code is not None}
    taken_names = {name for _id, _code, name in rows if name is not None}
    seen_codes = set()
    seen_names = set()

    for record_id, code, name in rows:
        new_code = code
        if code is not None:
            if code in seen_codes:
                new_code = _free_code(code, taken_codes)
            seen_codes.add(new_code)
            taken_codes.add(new_code)

        new_name = name
        if name is not None:
            if name in seen_names:
                new_name = _free_name(name, taken_names)
            seen_names.add(new_name)
            taken_names.add(new_name)

        if new_code != code or new_name != name:
            cr.execute(
                "UPDATE school_position_type SET code = %s, name = %s WHERE id = %s",
                (new_code, new_name, record_id),
            )
