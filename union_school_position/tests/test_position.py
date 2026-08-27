from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPosition(TransactionCase):
    """Tests for school_position.position: sector, featured, workplace levels,
    constraints, _compute_display_name, and create-from-import logic."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Position = cls.env["school_position.position"]
        cls.affiliate = (
            cls.env["affiliation.affiliate"]
            .sudo()
            .create({"uid": 20000001, "name": "Position Test Affiliate", "state": "new"})
        )
        cls.pos_type = cls.env["school_position.type"].create(
            {"code": "TST", "name": "Test Type", "in_hours": True, "dedication": "FT"}
        )
        cls.character = cls.env["school_position.character"].create({"code": "CHR", "name": "Test Character"})
        cls.workplace = cls.env["union.workplace"].create({"name": "Test Workplace", "code": "WP001"})

    def _create_position(self, **kw):
        vals = {
            "affiliate_id": self.affiliate.id,
            "type_id": self.pos_type.id,
            "character_id": self.character.id,
        }
        vals.update(kw)
        return self.Position.sudo().create(vals)

    # ─── sector field (new from 16.0) ─────────────────────────────────────────

    def test_sector_field_create(self):
        """sector field can be set on create."""
        pos = self._create_position(sector="Education")
        self.assertEqual(pos.sector, "Education")

    def test_sector_field_write(self):
        """sector field can be updated via write."""
        pos = self._create_position()
        pos.write({"sector": "Administration"})
        self.assertEqual(pos.sector, "Administration")

    def test_sector_field_optional(self):
        """sector is not required."""
        pos = self._create_position()
        self.assertFalse(pos.sector)

    # ─── featured field + actions ─────────────────────────────────────────────

    def test_featured_default_false(self):
        """featured defaults to False."""
        pos = self._create_position()
        self.assertFalse(pos.featured)

    def test_action_set_featured(self):
        """action_set_featured sets featured=True."""
        pos = self._create_position()
        pos.action_set_featured()
        self.assertTrue(pos.featured)

    def test_action_unset_featured(self):
        """action_unset_featured sets featured=False."""
        pos = self._create_position(featured=True)
        pos.action_unset_featured()
        self.assertFalse(pos.featured)

    # ─── workplace_level1/2/3 compute ─────────────────────────────────────────

    def test_workplace_levels_without_workplace(self):
        """workplace_level1/2/3 show 'Sin lugar de trabajo' when no workplace."""
        pos = self._create_position()
        self.assertEqual(pos.workplace_level1, "Sin lugar de trabajo")

    def test_workplace_levels_with_workplace(self):
        """workplace_level3 matches workplace name."""
        pos = self._create_position(workplace_id=self.workplace.id)
        self.assertEqual(pos.workplace_level3, "Test Workplace")

    def test_workplace_levels_hierarchy(self):
        """workplace_level1/2/3 resolve correctly in a 3-level hierarchy."""
        wp1 = self.env["union.workplace"].create({"name": "Level 1", "code": "L1"})
        wp2 = self.env["union.workplace"].create({"name": "Level 2", "code": "L2", "parent_id": wp1.id})
        wp3 = self.env["union.workplace"].create({"name": "Level 3", "code": "L3", "parent_id": wp2.id})
        pos = self._create_position(workplace_id=wp3.id)
        self.assertEqual(pos.workplace_level1, "Level 1")
        self.assertEqual(pos.workplace_level2, "Level 2")
        self.assertEqual(pos.workplace_level3, "Level 3")

    def test_workplace_level2_label_is_correct(self):
        """workplace_level2 string is 'Workplace Level 2' (regression: was 'Workplace Level 1')."""
        field = self.Position._fields["workplace_level2"]
        self.assertEqual(field.string, "Workplace Level 2")

    # ─── _compute_display_name ────────────────────────────────────────────────

    def test_display_name(self):
        """display_name combines type name and affiliate name."""
        pos = self._create_position()
        pos._compute_display_name()
        self.assertIn(self.pos_type.name, pos.display_name)
        self.assertIn(self.affiliate.name, pos.display_name)

    # ─── Constraints ──────────────────────────────────────────────────────────

    def test_check_dates_valid(self):
        """Valid date_from < date_to passes constraint."""
        from datetime import date

        pos = self._create_position(date_from=date(2024, 1, 1), date_to=date(2024, 12, 31))
        self.assertEqual(pos.date_to, date(2024, 12, 31))

    def test_check_dates_invalid(self):
        """date_to <= date_from raises ValidationError."""
        from datetime import date

        with self.assertRaises(ValidationError):
            self._create_position(date_from=date(2024, 12, 31), date_to=date(2024, 1, 1))

    def test_check_registration_date_future(self):
        """registration_date in the future raises ValidationError."""
        from datetime import date

        future = date(date.today().year + 1, 1, 1)
        with self.assertRaises(ValidationError):
            self._create_position(registration_date=future)

    def test_check_hs_amount_required_for_hours(self):
        """hs_amount must be > 0 when type is in_hours."""
        with self.assertRaises(ValidationError):
            self._create_position(hs_amount=0)

    def test_check_hs_amount_must_be_empty_for_non_hours(self):
        """hs_amount must be empty when type is not in_hours."""
        non_hours_type = self.env["school_position.type"].create(
            {
                "code": "NH",
                "name": "Non Hours Type",
                "in_hours": False,
                "dedication": "PT",
            }
        )
        with self.assertRaises(ValidationError):
            self._create_position(type_id=non_hours_type.id, hs_amount=10)

    # ─── create-from-import logic ─────────────────────────────────────────────

    def test_create_from_import_existing_affiliate(self):
        """create with import_uid resolves to existing affiliate."""
        pos = (
            self.Position.sudo()
            .with_context(import_file=True)
            .create(
                {
                    "import_uid": "20000001",
                    "type_id": self.pos_type.id,
                    "character_id": self.character.id,
                    "import_name": "Position Test Affiliate",
                }
            )
        )
        self.assertEqual(pos.affiliate_id, self.affiliate)

    def test_create_from_import_auto_create_disabled(self):
        """create with unknown import_uid raises when auto-create is disabled."""
        with self.assertRaises(ValidationError):
            self.Position.sudo().with_context(import_file=True).create(
                {
                    "import_uid": "99999999",
                    "type_id": self.pos_type.id,
                    "character_id": self.character.id,
                    "import_name": "Unknown Person",
                }
            )

    def test_create_from_import_auto_create_enabled(self):
        """create with unknown import_uid auto-creates affiliate when config enabled."""
        config = self.env["affiliation.affiliation_configuration"].browse(1)
        config.write({"create_user_from_position": True})

        pos = (
            self.Position.sudo()
            .with_context(import_file=True)
            .create(
                {
                    "import_uid": "30000003",
                    "type_id": self.pos_type.id,
                    "character_id": self.character.id,
                    "import_name": "Auto Created Affiliate",
                }
            )
        )
        self.assertTrue(pos.affiliate_id)
        self.assertEqual(pos.affiliate_id.uid, 30000003)

        # Cleanup
        config.write({"create_user_from_position": False})

    def test_create_from_import_invalid_uid_non_digit(self):
        """create with non-digit import_uid raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.Position.sudo().with_context(import_file=True).create(
                {
                    "import_uid": "ABC123",
                    "type_id": self.pos_type.id,
                    "character_id": self.character.id,
                    "import_name": "Bad UID",
                }
            )

    def test_create_from_import_leading_zero_uid(self):
        """create with import_uid starting with '0' raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.Position.sudo().with_context(import_file=True).create(
                {
                    "import_uid": "01234567",
                    "type_id": self.pos_type.id,
                    "character_id": self.character.id,
                    "import_name": "Leading Zero",
                }
            )

    # ─── on_import_error must not crash (P0 regression) ──────────────────────

    def test_on_import_error_does_not_crash(self):
        """Import row errors are logged, never raise.

        Regression: the old body called res.users.notify_danger(), an API
        that does not exist in Odoo 19 -> AttributeError aborted the whole
        import wizard on any failing row.
        """
        pos = self._create_position()
        result = pos.on_import_error("bad,row", {"record": "0", "message": "simulated"})
        self.assertIsNone(result)
