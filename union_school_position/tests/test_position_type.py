from odoo.tests import TransactionCase, tagged
from psycopg2.errors import UniqueViolation


@tagged("post_install", "-at_install")
class TestPositionType(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PositionType = cls.env["school_position.type"]
        cls.position_type = cls.PositionType.sudo().create(
            {
                "code": "TST",
                "name": "Test Type",
                "in_hours": True,
                "dedication": "FT",
            }
        )

    def test_display_name(self):
        self.assertEqual(self.position_type.display_name, "[TST] Test Type")

    def test_name_search_by_exact_code(self):
        result = self.PositionType.name_search("TST", operator="=")
        self.assertEqual(result, [(self.position_type.id, "[TST] Test Type")])

    def test_name_search_import_file_by_code(self):
        result = self.PositionType.with_context(import_file=True).name_search("TST", operator="=")
        self.assertEqual(result, [(self.position_type.id, "[TST] Test Type")])

    def test_name_search_import_file_by_description(self):
        result = self.PositionType.with_context(import_file=True).name_search("Test Type", operator="=")
        self.assertEqual(result, [(self.position_type.id, "[TST] Test Type")])

    def test_name_search_by_partial_description(self):
        result = self.PositionType.name_search("Test Typ", operator="ilike")
        self.assertIn(self.position_type.id, [record[0] for record in result])

    def test_code_unique_constraint(self):
        with self.assertRaises(UniqueViolation):
            with self.env.cr.savepoint():
                self.PositionType.sudo().create(
                    {
                        "code": "TST",
                        "name": "Other Type",
                        "in_hours": True,
                        "dedication": "FT",
                    }
                )

    def test_name_unique_constraint(self):
        with self.assertRaises(UniqueViolation):
            with self.env.cr.savepoint():
                self.PositionType.sudo().create(
                    {
                        "code": "OTH",
                        "name": "Test Type",
                        "in_hours": True,
                        "dedication": "FT",
                    }
                )

    def test_different_code_and_name_allowed(self):
        position_type = self.PositionType.sudo().create(
            {
                "code": "TST2",
                "name": "Test Type 2",
                "in_hours": True,
                "dedication": "FT",
            }
        )
        self.assertTrue(position_type.id)
