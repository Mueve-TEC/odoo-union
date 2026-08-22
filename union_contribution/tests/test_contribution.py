from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestContribution(TransactionCase):
    """Tests for contribution.affiliate_contribution: _compute_display_name
    (handles date=False), import logic, and contribution_code display_name."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Contribution = cls.env["contribution.affiliate_contribution"]
        cls.CodeModel = cls.env["contribution.affiliate_contribution_code"]
        cls.affiliate = (
            cls.env["affiliation.affiliate"]
            .sudo()
            .create(
                {
                    "uid": "70000001",
                    "name": "Contribution Test Affiliate",
                    "state": "new",
                }
            )
        )
        cls.contrib_code = cls.CodeModel.create(
            {"code": "C001", "description": "Test Contribution Code", "enabled": True}
        )

    def _create_contribution(self, **kw):
        from datetime import date

        vals = {
            "affiliate_id": self.affiliate.id,
            "date": date(2024, 1, 15),
            "contrib_amount": 100.0,
            "contribution_code_id": self.contrib_code.id,
        }
        vals.update(kw)
        return self.Contribution.sudo().create(vals)

    # ─── _compute_display_name with date=False handling ───────────────────────

    def test_display_name_with_date(self):
        """display_name includes the date when set."""
        from datetime import date

        contrib = self._create_contribution(date=date(2024, 6, 30))
        contrib._compute_display_name()
        self.assertIn("2024-06-30", contrib.display_name)

    def test_display_name_without_date(self):
        """display_name does not crash when date is False (regression test)."""
        contrib = (
            self.env["contribution.affiliate_contribution"]
            .sudo()
            .new(
                {
                    "affiliate_id": self.affiliate.id,
                    "date": False,
                    "contrib_amount": 50.0,
                    "contribution_code_id": self.contrib_code.id,
                }
            )
        )
        contrib._compute_display_name()
        self.assertIn(self.affiliate.name, contrib.display_name)

    # ─── contribution_code _compute_display_name ───────────────────────────────

    def test_code_display_name_uses_description(self):
        """contribution_code display_name uses the description field."""
        code = self.CodeModel.create({"code": "C002", "description": "Special Code", "enabled": True})
        code._compute_display_name()
        self.assertEqual(code.display_name, "Special Code")

    # ─── create with import context ────────────────────────────────────────────

    def test_create_from_import_valid_uid(self):
        """create with import_uid resolves to existing affiliate."""
        from datetime import date

        contrib = (
            self.Contribution.sudo()
            .with_context(import_file=True)
            .create(
                {
                    "import_uid": "70000001",
                    "import_name": "Contribution Test Affiliate",
                    "date": date(2024, 2, 1),
                    "contrib_amount": 200.0,
                    "contribution_code_id": self.contrib_code.id,
                }
            )
        )
        self.assertEqual(contrib.affiliate_id, self.affiliate)

    def test_create_from_import_invalid_uid_non_digit(self):
        """create with non-digit import_uid raises ValidationError."""
        from datetime import date

        with self.assertRaises(ValidationError):
            self.Contribution.sudo().with_context(import_file=True).create(
                {
                    "import_uid": "ABC123",
                    "import_name": "Bad UID",
                    "date": date(2024, 2, 1),
                    "contrib_amount": 200.0,
                    "contribution_code_id": self.contrib_code.id,
                }
            )

    def test_create_from_import_leading_zero_uid(self):
        """create with import_uid starting with '0' raises ValidationError."""
        from datetime import date

        with self.assertRaises(ValidationError):
            self.Contribution.sudo().with_context(import_file=True).create(
                {
                    "import_uid": "01234567",
                    "import_name": "Leading Zero",
                    "date": date(2024, 2, 1),
                    "contrib_amount": 200.0,
                    "contribution_code_id": self.contrib_code.id,
                }
            )


@tagged("post_install", "-at_install")
class TestInconsistenciesResult(TransactionCase):
    """Tests for inconsistencies.result: action_set_quote, action_unset_quote,
    and _compute_display_name."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Result = cls.env["inconsistencies.result"]
        cls.affiliate_type = cls.env["affiliation.affiliate_type"].create(
            {"name": "Test Type for Inconsistency", "enabled": True}
        )
        cls.affiliate = (
            cls.env["affiliation.affiliate"]
            .sudo()
            .create(
                {
                    "uid": "80000001",
                    "name": "Inconsistency Test Affiliate",
                    "state": "affiliated",
                    "quote": False,
                    "affiliate_type_id": cls.affiliate_type.id,
                }
            )
        )

    def _create_result(self, **kw):
        vals = {
            "affiliate_id": self.affiliate.id,
            "description": "Test inconsistency",
            "status": "active",
        }
        vals.update(kw)
        return self.Result.sudo().create(vals)

    # ─── action_set_quote ──────────────────────────────────────────────────────

    def test_action_set_quote(self):
        """action_set_quote sets quote=True on affiliated affiliate."""
        result = self._create_result()
        result.action_set_quote()
        self.assertTrue(self.affiliate.quote)

    def test_action_set_quote_only_for_affiliated(self):
        """action_set_quote raises when affiliate is not 'affiliated'."""
        self.affiliate.write({"state": "disaffiliated"})
        result = self._create_result()
        with self.assertRaises(ValidationError):
            result.action_set_quote()

    # ─── action_unset_quote ────────────────────────────────────────────────────

    def test_action_unset_quote(self):
        """action_unset_quote sets quote=False on affiliated affiliate."""
        self.affiliate.write({"quote": True})
        result = self._create_result()
        result.action_unset_quote()
        self.assertFalse(self.affiliate.quote)

    def test_action_unset_quote_only_for_affiliated(self):
        """action_unset_quote raises when affiliate is not 'affiliated'."""
        self.affiliate.write({"state": "disaffiliated", "quote": True})
        result = self._create_result()
        with self.assertRaises(ValidationError):
            result.action_unset_quote()

    # ─── _compute_display_name ─────────────────────────────────────────────────

    def test_display_name(self):
        """display_name includes the affiliate name."""
        result = self._create_result()
        result._compute_display_name()
        self.assertIn(self.affiliate.name, result.display_name)

    # ─── related fields ───────────────────────────────────────────────────────

    def test_affiliate_state_related(self):
        """affiliate_state reflects the affiliate's state."""
        result = self._create_result()
        self.assertEqual(result.affiliate_state, "affiliated")

    def test_quote_related(self):
        """quote reflects the affiliate's quote field."""
        self.affiliate.write({"quote": True})
        result = self._create_result()
        self.assertTrue(result.quote)
