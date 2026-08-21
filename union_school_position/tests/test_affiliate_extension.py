from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAffiliateExtension(TransactionCase):
    """Tests for union_school_position affiliate extensions:
    has_featured_position, position_registration_date_ids, position_type_ids."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.affiliate = (
            cls.env["affiliation.affiliate"]
            .sudo()
            .create(
                {"uid": "40000001", "name": "Extension Test Affiliate", "state": "new"}
            )
        )
        cls.pos_type = cls.env["school_position.type"].create(
            {
                "code": "EXT",
                "name": "Extension Type",
                "in_hours": True,
                "dedication": "FT",
            }
        )
        cls.character = cls.env["school_position.character"].create(
            {"code": "ECH", "name": "Extension Character"}
        )
        cls.other_type = cls.env["school_position.type"].create(
            {"code": "OTH", "name": "Other Type", "in_hours": False, "dedication": "PT"}
        )

    def _create_position(self, **kw):
        vals = {
            "affiliate_id": self.affiliate.id,
            "type_id": self.pos_type.id,
            "character_id": self.character.id,
        }
        vals.update(kw)
        return self.env["school_position.position"].sudo().create(vals)

    # ─── has_featured_position compute (new from 16.0) ────────────────────────

    def test_has_featured_position_default_false(self):
        """has_featured_position is False when no featured positions exist."""
        self._create_position(featured=False)
        self.affiliate.invalidate_recordset(["has_featured_position"])
        self.assertFalse(self.affiliate.has_featured_position)

    def test_has_featured_position_true(self):
        """has_featured_position is True when at least one position is featured."""
        self._create_position(featured=True)
        self.affiliate.invalidate_recordset(["has_featured_position"])
        self.assertTrue(self.affiliate.has_featured_position)

    def test_has_featured_position_mixed(self):
        """has_featured_position is True if any position is featured."""
        self._create_position(featured=False)
        self._create_position(featured=True)
        self.affiliate.invalidate_recordset(["has_featured_position"])
        self.assertTrue(self.affiliate.has_featured_position)

    # ─── position_type_ids compute ─────────────────────────────────────────────

    def test_position_type_ids_empty(self):
        """position_type_ids is empty when no positions exist."""
        self.affiliate.invalidate_recordset(["position_type_ids"])
        self.assertFalse(self.affiliate.position_type_ids)

    def test_position_type_ids_populated(self):
        """position_type_ids contains the types of the affiliate's positions."""
        self._create_position(type_id=self.pos_type.id)
        self._create_position(type_id=self.other_type.id)
        self.affiliate.invalidate_recordset(["position_type_ids"])
        self.assertIn(self.pos_type, self.affiliate.position_type_ids)
        self.assertIn(self.other_type, self.affiliate.position_type_ids)

    # ─── position_registration_date_ids compute (new from 16.0) ───────────────

    def test_registration_date_empty(self):
        """position_registration_date_ids is empty when no registration dates."""
        self._create_position()
        self.affiliate.invalidate_recordset(["position_registration_date_ids"])
        self.assertFalse(self.affiliate.position_registration_date_ids)

    def test_registration_date_populated(self):
        """position_registration_date_ids creates/links date records."""
        from datetime import date

        self._create_position(registration_date=date(2024, 3, 15))
        self.affiliate.invalidate_recordset(["position_registration_date_ids"])
        self.assertTrue(self.affiliate.position_registration_date_ids)
        self.assertEqual(
            self.affiliate.position_registration_date_ids[0].date,
            date(2024, 3, 15),
        )

    def test_registration_date_deduplication(self):
        """Multiple positions with same registration_date share one date record."""
        from datetime import date

        d = date(2024, 5, 20)
        self._create_position(registration_date=d)
        self._create_position(registration_date=d)
        self.affiliate.invalidate_recordset(["position_registration_date_ids"])
        self.assertEqual(len(self.affiliate.position_registration_date_ids), 1)
