from datetime import date

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAffiliateUnlink(TransactionCase):
    """Deleting an affiliate cascades to its contributions and partner."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.affiliate = (
            cls.env["affiliation.affiliate"]
            .sudo()
            .create(
                {
                    "uid": 71000001,
                    "name": "Unlink Contribution Affiliate",
                    "state": "new",
                }
            )
        )
        cls.contrib_code = cls.env["contribution.affiliate_contribution_code"].create(
            {"code": "UNL", "description": "Unlink Test Code", "enabled": True}
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
        cls.partner = cls.affiliate.partner_id

    def test_unlink_affiliate_deletes_contribution_and_partner(self):
        self.affiliate.unlink()
        self.assertFalse(self.contribution.exists())
        self.assertFalse(self.partner.exists())
