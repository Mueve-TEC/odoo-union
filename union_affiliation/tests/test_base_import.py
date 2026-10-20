import io
from datetime import date, datetime

import openpyxl
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBaseImport(TransactionCase):
    """Regression tests for the xlsx date-cell import fix (Odoo 19)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Import = cls.env["base_import.import"]

    def _make_import(self, value, number_format):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["date"])
        sheet.append([value])
        sheet.cell(row=2, column=1).number_format = number_format

        buffer = io.BytesIO()
        workbook.save(buffer)

        return self.Import.create(
            {
                "res_model": "affiliation.affiliate",
                "file": buffer.getvalue(),
                "file_name": "test.xlsx",
                "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        )

    def test_time_formatted_date_is_imported(self):
        """A date cell formatted as "D/M/YYYY" must not abort the import."""
        record = self._make_import(datetime(2023, 6, 21), "D/M/YYYY")

        length, rows = record._read_xlsx({})

        self.assertEqual(length, 2)
        self.assertEqual(rows[1][0], datetime(2023, 6, 21))

    def test_date_formatted_cell_returns_date(self):
        """A regular date cell still returns a date object."""
        record = self._make_import(date(2023, 6, 21), "yyyy-mm-dd")

        _length, rows = record._read_xlsx({})

        value = rows[1][0]
        self.assertEqual(value, date(2023, 6, 21))
        self.assertIsInstance(value, date)
        self.assertNotIsInstance(value, datetime)
