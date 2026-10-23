from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAffiliateDelete(TransactionCase):
    """Deleting an affiliate with benefit requests must be blocked."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.affiliate = (
            cls.env["affiliation.affiliate"]
            .sudo()
            .create(
                {
                    "uid": 73000001,
                    "name": "Delete Benefit Affiliate",
                    "state": "new",
                }
            )
        )
        cls.request_type = cls.env["benefit_request.request_type"].create(
            {"name": "Delete Request Type", "who_apply": "everybody"}
        )
        cls.request = (
            cls.env["benefit_request.benefit_request"]
            .sudo()
            .create(
                {
                    "partner_id": cls.affiliate.partner_id.id,
                    "request_type_id": cls.request_type.id,
                }
            )
        )

    def test_delete_affiliate_with_benefit_request_is_blocked(self):
        with self.assertRaises(UserError) as error:
            self.affiliate.with_context(lang="en_US").unlink()

        self.assertIn("1 benefit request(s)", str(error.exception))
        self.assertTrue(self.affiliate.exists())
        self.assertTrue(self.request.exists())

    def test_delete_affiliate_after_removing_benefit_request(self):
        self.request.unlink()
        self.affiliate.unlink()
        self.assertFalse(self.affiliate.exists())
