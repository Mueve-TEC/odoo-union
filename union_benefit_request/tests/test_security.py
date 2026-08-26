from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged

grp = lambda env, x: env.ref(x).id


@tagged("post_install", "security", "union")
class TestBenefitRequestSecurity(TransactionCase):
    """Verify benefit_request.benefit_request ACLs are group-scoped (audit 2.1).

    ``check_access_rights`` returns None when allowed and raises AccessError
    when denied, so we call it directly for allowed ops and wrap denials in
    assertRaises. A real read proves end-to-end access without triggering
    mail.thread side effects.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Model = cls.env["benefit_request.benefit_request"]
        cls.RequestType = cls.env["benefit_request.request_type"]
        cls.partner = cls.env["res.partner"].create({"name": "Sec Test Partner"})
        cls.rt = cls.RequestType.create({"name": "Sec RT", "who_apply": "everybody"})
        cls.user_none = cls.env["res.users"].create(
            {
                "name": "Sec No Union",
                "login": "sec_no_union",
                "group_ids": [(6, 0, [grp(cls.env, "base.group_user")])],
            }
        )
        cls.user_read = cls.env["res.users"].create(
            {
                "name": "Sec BR Read",
                "login": "sec_br_read",
                "group_ids": [(6, 0, [grp(cls.env, "union_benefit_request.group_benefit_request_read")])],
            }
        )
        cls.user_write = cls.env["res.users"].create(
            {
                "name": "Sec BR Write",
                "login": "sec_br_write",
                "group_ids": [(6, 0, [grp(cls.env, "union_benefit_request.group_benefit_request_write")])],
            }
        )

    def test_no_group_has_no_access(self):
        Model = self.Model.with_user(self.user_none)
        with self.assertRaises(AccessError):
            Model.check_access_rights("read")
        with self.assertRaises(AccessError):
            Model.check_access_rights("write")
        with self.assertRaises(AccessError):
            Model.check_access_rights("create")

    def test_read_user_can_read_not_write(self):
        rec = self.Model.sudo().create({"partner_id": self.partner.id, "request_type_id": self.rt.id})
        rec.with_user(self.user_read).read(["state"])
        Model = self.Model.with_user(self.user_read)
        Model.check_access_rights("read")
        with self.assertRaises(AccessError):
            Model.check_access_rights("write")

    def test_write_user_has_write_create_not_unlink(self):
        Model = self.Model.with_user(self.user_write)
        Model.check_access_rights("read")
        Model.check_access_rights("write")
        Model.check_access_rights("create")
        with self.assertRaises(AccessError):
            Model.check_access_rights("unlink")
