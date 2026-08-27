from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


def grp(env, x):
    return env.ref(x).id


@tagged("post_install", "security", "union")
class TestSchoolPositionSecurity(TransactionCase):
    """Verify featured server actions are gated (2.3) and write-group cannot delete positions (2.5)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Position = cls.env["school_position.position"]
        cls.Affiliate = cls.env["affiliation.affiliate"]
        cls.affiliate_type = cls.env["affiliation.affiliate_type"].create({"name": "Sec PType", "enabled": True})
        cls.aff = cls.Affiliate.sudo().create({"uid": 33333333, "name": "Sec Aff P", "state": "new"})
        cls.pos_type = cls.env["school_position.type"].create(
            {"code": "SECT", "name": "Sec PosType", "in_hours": True, "dedication": "FT"}
        )
        cls.character = cls.env["school_position.character"].create({"code": "SECC", "name": "Sec Character"})
        cls.user_pos_read = cls.env["res.users"].create(
            {
                "name": "Sec Pos Read",
                "login": "sec_pos_read",
                "group_ids": [(6, 0, [grp(cls.env, "union_school_position.group_school_position_read")])],
            }
        )
        cls.user_pos_write = cls.env["res.users"].create(
            {
                "name": "Sec Pos Write",
                "login": "sec_pos_write",
                "group_ids": [(6, 0, [grp(cls.env, "union_school_position.group_school_position_write")])],
            }
        )

    def _create_position(self, **kw):
        vals = {
            "affiliate_id": self.aff.id,
            "type_id": self.pos_type.id,
            "character_id": self.character.id,
        }
        vals.update(kw)
        return self.Position.sudo().create(vals)

    def test_set_featured_allowed_for_write_group(self):
        pos = self._create_position()
        pos.with_user(self.user_pos_write).action_set_featured()
        self.assertTrue(pos.sudo().featured)

    def test_set_featured_denied_for_read_group(self):
        pos = self._create_position()
        with self.assertRaises(UserError):
            pos.with_user(self.user_pos_read).action_set_featured()

    def test_write_user_cannot_delete_position(self):
        pos = self._create_position()
        with self.assertRaises(AccessError):
            pos.with_user(self.user_pos_write).unlink()
