from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

grp = lambda env, x: env.ref(x).id


@tagged("post_install", "security", "union")
class TestContributionSecurity(TransactionCase):
    """Verify set/unset quote server actions are gated by group_inconsistencies_write (2.3)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Affiliate = cls.env["affiliation.affiliate"]
        cls.Result = cls.env["inconsistencies.result"]
        cls.affiliate_type = cls.env["affiliation.affiliate_type"].create({"name": "Sec CType", "enabled": True})
        cls.aff = cls.Affiliate.sudo().create(
            {
                "uid": "22222222",
                "name": "Sec Aff Q",
                "state": "affiliated",
                "affiliate_type_id": cls.affiliate_type.id,
            }
        )
        cls.user_none = cls.env["res.users"].create(
            {
                "name": "Sec None Q",
                "login": "sec_none_q",
                "group_ids": [(6, 0, [grp(cls.env, "base.group_user")])],
            }
        )
        cls.user_inc_read = cls.env["res.users"].create(
            {
                "name": "Sec Inc Read",
                "login": "sec_inc_read",
                "group_ids": [(6, 0, [grp(cls.env, "union_contribution.group_inconsistencies_read")])],
            }
        )
        cls.user_inc_write = cls.env["res.users"].create(
            {
                "name": "Sec Inc Write",
                "login": "sec_inc_write",
                "group_ids": [(6, 0, [grp(cls.env, "union_contribution.group_inconsistencies_write")])],
            }
        )

    def _make_result(self):
        return self.Result.sudo().create(
            {
                "affiliate_id": self.aff.id,
                "from_date": "2024-01-01",
                "to_date": "2024-12-31",
                "query_date": "2024-06-01",
                "description": "Sec Q",
            }
        )

    def test_set_quote_allowed_for_write_group(self):
        rec = self._make_result()
        rec.with_user(self.user_inc_write).action_set_quote()
        self.assertTrue(self.aff.sudo().quote)

    def test_set_quote_denied_for_read_group(self):
        rec = self._make_result()
        with self.assertRaises(UserError):
            rec.with_user(self.user_inc_read).action_set_quote()

    def test_set_quote_denied_for_no_group(self):
        rec = self._make_result()
        with self.assertRaises(UserError):
            rec.with_user(self.user_none).action_set_quote()

    def test_unset_quote_allowed_for_write_group(self):
        self.aff.sudo().write({"quote": True})
        rec = self._make_result()
        rec.with_user(self.user_inc_write).action_unset_quote()
        self.assertFalse(self.aff.sudo().quote)
