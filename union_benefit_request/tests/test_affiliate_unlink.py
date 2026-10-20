from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAffiliateUnlink(TransactionCase):
    """Deleting an affiliate removes its partner's benefit requests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.affiliate = (
            cls.env["affiliation.affiliate"]
            .sudo()
            .create(
                {
                    "uid": 73000001,
                    "name": "Unlink Benefit Affiliate",
                    "state": "new",
                }
            )
        )
        cls.request_type = cls.env["benefit_request.request_type"].create(
            {"name": "Unlink Request Type", "who_apply": "everybody"}
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
        cls.partner = cls.affiliate.partner_id

    def test_unlink_affiliate_deletes_benefit_request_and_partner(self):
        self.affiliate.unlink()
        self.assertFalse(self.request.exists())
        self.assertFalse(self.partner.exists())
