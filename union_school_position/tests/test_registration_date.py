from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRegistrationDate(TransactionCase):
    """Tests for the school_position.registration.date model (new from 16.0)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.DateModel = cls.env["school_position.registration.date"]

    def test_create_registration_date(self):
        """Can create a registration date record."""
        from datetime import date

        record = self.DateModel.sudo().create({"date": date(2024, 6, 1)})
        self.assertTrue(record.id)
        self.assertEqual(record.date, date(2024, 6, 1))

    def test_date_required(self):
        """date field is required."""
        with self.assertRaises(Exception):
            self.DateModel.sudo().create({})

    def test_rec_name_is_date(self):
        """_rec_name is 'date' so display_name uses the date field."""
        from datetime import date

        record = self.DateModel.sudo().create({"date": date(2024, 7, 15)})
        self.assertIn("2024-07-15", record.display_name)
