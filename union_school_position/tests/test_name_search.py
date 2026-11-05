from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNameSearchDomain(TransactionCase):
    """Regression: Odoo 19 name_search uses ``domain`` instead of ``args``."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Character = cls.env["school_position.character"]
        cls.character_a = cls.Character.sudo().create({"code": "DCHA", "name": "Domain Character Alpha"})
        cls.character_b = cls.Character.sudo().create({"code": "DCHB", "name": "Domain Character Beta"})

    def test_character_name_search_accepts_domain(self):
        result = self.Character.name_search("Domain Character", domain=[("id", "=", self.character_a.id)])
        self.assertEqual([record[0] for record in result], [self.character_a.id])

    def test_character_name_search_by_code_with_domain(self):
        result = self.Character.name_search("DCHB", operator="=", domain=[("id", "!=", self.character_a.id)])
        self.assertEqual([record[0] for record in result], [self.character_b.id])

    def test_character_import_name_search_accepts_domain(self):
        result = self.Character.with_context(import_file=True).name_search(
            "DCHA", operator="=", domain=[("id", "=", self.character_a.id)]
        )
        self.assertEqual([record[0] for record in result], [self.character_a.id])
