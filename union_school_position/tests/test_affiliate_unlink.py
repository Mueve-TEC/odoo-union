from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAffiliateUnlink(TransactionCase):
    """Deleting an affiliate cascades to its school positions and partner."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.affiliate = (
            cls.env["affiliation.affiliate"]
            .sudo()
            .create(
                {
                    "uid": 72000001,
                    "name": "Unlink Position Affiliate",
                    "state": "new",
                }
            )
        )
        cls.pos_type = cls.env["school_position.type"].create(
            {"code": "UNLT", "name": "Unlink Type", "in_hours": True, "dedication": "FT"}
        )
        cls.character = cls.env["school_position.character"].create({"code": "UNLC", "name": "Unlink Character"})
        cls.position = (
            cls.env["school_position.position"]
            .sudo()
            .create(
                {
                    "affiliate_id": cls.affiliate.id,
                    "type_id": cls.pos_type.id,
                    "character_id": cls.character.id,
                }
            )
        )
        cls.partner = cls.affiliate.partner_id

    def test_unlink_affiliate_deletes_position_and_partner(self):
        self.affiliate.unlink()
        self.assertFalse(self.position.exists())
        self.assertFalse(self.partner.exists())
