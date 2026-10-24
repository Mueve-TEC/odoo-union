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
        cls.partner = cls.affiliate.partner_id

    def test_delete_affiliate_with_contribution_is_blocked(self):
        with self.assertRaises(UserError) as error:
            self.affiliate.with_context(lang="en_US").unlink()

        message = str(error.exception)
        self.assertIn("1 contribution(s)", message)
        self.assertIn("Delete those records first", message)
        self.assertIn("archive it instead", message)
        # nothing was deleted, not even the partner
        self.assertTrue(self.affiliate.exists())
        self.assertTrue(self.contribution.exists())
        self.assertTrue(self.partner.exists())

    def test_delete_affiliate_after_removing_contribution(self):
        self.contribution.unlink()
        self.affiliate.unlink()
        self.assertFalse(self.affiliate.exists())
        self.assertFalse(self.partner.exists())

    def test_blocked_batch_delete_removes_nothing(self):
        """A batch blocked by one affiliate deletes neither of them."""
        clean = (
            self.env["affiliation.affiliate"]
            .sudo()
            .create({"uid": 71000002, "name": "Batch Clean Affiliate", "state": "new"})
        )

        with self.assertRaises(UserError):
            (clean | self.affiliate).with_context(lang="en_US").unlink()

        self.assertTrue(clean.exists())
        self.assertTrue(self.affiliate.exists())
        self.assertTrue(clean.partner_id.exists())
        self.assertTrue(self.partner.exists())

    def test_blocked_message_lists_every_dependency(self):
        """One message names all three dependents, not only the first one."""
        registry = self.env.registry
        if "school_position.position" not in registry or "benefit_request.benefit_request" not in registry:
            self.skipTest("school_position / benefit_request are not installed")

        pos_type = self.env["school_position.type"].create(
            {"code": "AGG", "name": "Aggregate Type", "in_hours": True, "dedication": "FT"}
        )
        character = self.env["school_position.character"].create({"code": "AGGCH", "name": "Aggregate Character"})
        self.env["school_position.position"].sudo().create(
            {
                "affiliate_id": self.affiliate.id,
                "type_id": pos_type.id,
                "character_id": character.id,
                "hs_amount": 10,
            }
        )
        request_type = self.env["benefit_request.request_type"].create(
            {"name": "Aggregate Request Type", "who_apply": "everybody"}
        )
        self.env["benefit_request.benefit_request"].sudo().create(
            {"partner_id": self.partner.id, "request_type_id": request_type.id}
        )

        with self.assertRaises(UserError) as error:
            self.affiliate.with_context(lang="en_US").unlink()

        message = str(error.exception)
        self.assertIn("1 contribution(s)", message)
        self.assertIn("1 position(s)", message)
        self.assertIn("1 benefit request(s)", message)
        self.assertTrue(self.affiliate.exists())
        self.assertTrue(self.partner.exists())
