from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAffiliateDelete(TransactionCase):
    """Deleting an affiliate with school positions must be blocked."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.affiliate = (
            cls.env["affiliation.affiliate"]
            .sudo()
            .create(
                {
                    "uid": 72000001,
                    "name": "Delete Position Affiliate",
                    "state": "new",
                }
            )
        )
        cls.pos_type = cls.env["school_position.type"].create(
            {"code": "DELT", "name": "Delete Type", "in_hours": True, "dedication": "FT"}
        )
        cls.character = cls.env["school_position.character"].create({"code": "DELC", "name": "Delete Character"})
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

    def test_delete_affiliate_with_position_is_blocked(self):
        with self.assertRaises(UserError) as error:
            self.affiliate.with_context(lang="en_US").unlink()

        self.assertIn("1 position(s)", str(error.exception))
        # nothing was deleted, not even the partner
        self.assertTrue(self.affiliate.exists())
        self.assertTrue(self.position.exists())
        self.assertTrue(self.partner.exists())

    def test_delete_affiliate_after_removing_position(self):
        self.position.unlink()
        self.affiliate.unlink()
        self.assertFalse(self.affiliate.exists())
        self.assertFalse(self.partner.exists())
