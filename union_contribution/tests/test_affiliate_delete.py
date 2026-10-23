from datetime import date

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAffiliateDelete(TransactionCase):
    """Deleting an affiliate with contributions must be blocked."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.affiliate = (
            cls.env["affiliation.affiliate"]
            .sudo()
            .create(
                {
                    "uid": 71000001,
                    "name": "Delete Contribution Affiliate",
                    "state": "new",
                }
            )
        )
        cls.contrib_code = cls.env["contribution.affiliate_contribution_code"].create(
            {"code": "DEL", "description": "Delete Test Code", "enabled": True}
        )
        cls.contribution = (
            cls.env["contribution.affiliate_contribution"]
            .sudo()
            .create(
                {
                    "affiliate_id": cls.affiliate.id,
                    "date": date(2024, 1, 15),
                    "contrib_amount": 100.0,
                    "contribution_code_id": cls.contrib_code.id,
                }
            )
        )

    def test_delete_affiliate_with_contribution_is_blocked(self):
        with self.assertRaises(UserError) as error:
            self.affiliate.with_context(lang="en_US").unlink()

        self.assertIn("1 contribution(s)", str(error.exception))
        self.assertTrue(self.affiliate.exists())
        self.assertTrue(self.contribution.exists())

    def test_delete_affiliate_after_removing_contribution(self):
        self.contribution.unlink()
        self.affiliate.unlink()
        self.assertFalse(self.affiliate.exists())
