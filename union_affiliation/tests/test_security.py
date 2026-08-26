from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged

grp = lambda env, x: env.ref(x).id


@tagged("post_install", "security", "union")
class TestAffiliationSecurity(TransactionCase):
    """Verify workplace internal read ACL (2.2) and write-group no-delete (2.5)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Workplace = cls.env["union.workplace"]
        cls.Affiliate = cls.env["affiliation.affiliate"]
        cls.affiliate_type = cls.env["affiliation.affiliate_type"].create({"name": "Sec AffType", "enabled": True})
        cls.user_internal = cls.env["res.users"].create(
            {
                "name": "Sec Internal",
                "login": "sec_internal",
                "group_ids": [(6, 0, [grp(cls.env, "base.group_user")])],
            }
        )
        cls.user_aff_read = cls.env["res.users"].create(
            {
                "name": "Sec Aff Read",
                "login": "sec_aff_read",
                "group_ids": [(6, 0, [grp(cls.env, "union_affiliation.group_affiliation_read")])],
            }
        )
        cls.user_aff_write = cls.env["res.users"].create(
            {
                "name": "Sec Aff Write",
                "login": "sec_aff_write",
                "group_ids": [(6, 0, [grp(cls.env, "union_affiliation.group_affiliation_write")])],
            }
        )

    def test_internal_user_can_read_workplace(self):
        wp = self.Workplace.sudo().create({"name": "Sec WP", "code": "SECWP"})
        wp.with_user(self.user_internal).read(["name"])
        results = self.Workplace.with_user(self.user_internal).name_search("Sec WP")
        self.assertTrue(results)

    def test_internal_user_cannot_write_workplace(self):
        wp = self.Workplace.sudo().create({"name": "Sec WP2", "code": "SECWP2"})
        with self.assertRaises(AccessError):
            wp.with_user(self.user_internal).write({"name": "X"})

    def test_affiliation_read_user_can_read(self):
        aff = self.Affiliate.sudo().create({"uid": 12121212, "name": "Sec Aff R", "state": "new"})
        aff.with_user(self.user_aff_read).read(["name"])

    def test_affiliation_write_user_cannot_delete(self):
        aff = self.Affiliate.sudo().create({"uid": 34343434, "name": "Sec Aff Del", "state": "new"})
        with self.assertRaises(AccessError):
            aff.with_user(self.user_aff_write).unlink()
