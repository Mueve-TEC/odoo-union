import csv
import io

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestImportGender(TransactionCase):
    """End-to-end regression for the affiliate ``gender`` import.

    The gender selection was originally only matched against its English
    labels.  The options displayed in the Spanish UI (``Femenino``,
    ``Masculino``, ``Otro``, ``No responde``) must be accepted by the regular
    ``base_import`` flow as well.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Import = cls.env["base_import.import"]
        cls.Affiliate = cls.env["affiliation.affiliate"]

        # The golden test database ships es_AR active; make sure of it so the
        # selection translations are available to the converter.
        cls.lang_es = (
            cls.env["res.lang"]
            .with_context(active_test=False)
            .search([("code", "=", "es_AR")], limit=1)
        )
        if cls.lang_es and not cls.lang_es.active:
            cls.lang_es.active = True

    def _make_import(self, rows):
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["uid", "gender", "name"])
        writer.writerows(rows)

        return self.Import.create(
            {
                "res_model": "affiliation.affiliate",
                "file": buffer.getvalue().encode("utf-8"),
                "file_name": "gender.csv",
                "file_type": "text/csv",
            }
        )

    def _options(self):
        return {
            "quoting": '"',
            "separator": ",",
            "has_headers": True,
            "advanced": True,
            "keep_matches": False,
            "encoding": "utf-8",
            "datetime_format": "%Y-%m-%d",
            "date_format": "%Y-%m-%d",
            "float_thousand_separator": ",",
            "float_decimal_separator": ".",
        }

    def test_spanish_gender_labels_are_imported(self):
        """Spanish labels, English labels and technical keys all import."""
        rows = [
            (99000001, "Femenino", "Spanish female"),
            (99000002, "Masculino", "Spanish male"),
            (99000003, "Otro", "Spanish other"),
            (99000004, "No responde", "Spanish not report"),
            (99000005, "Female", "English female"),
            (99000006, "female", "Technical female"),
        ]
        expected = {
            99000001: "female",
            99000002: "male",
            99000003: "other",
            99000004: "not_report",
            99000005: "female",
            99000006: "female",
        }

        record = self._make_import(rows)
        result = record.execute_import(
            ["uid", "gender", "name"],
            ["uid", "gender", "name"],
            self._options(),
            dryrun=False,
        )

        self.assertEqual(result["messages"], [])
        self.assertEqual(len(result["ids"]), len(rows))

        for uid, gender in expected.items():
            affiliate = self.Affiliate.search([("uid", "=", uid)])
            self.assertEqual(len(affiliate), 1, f"affiliate {uid} was not imported")
            self.assertEqual(
                affiliate.gender,
                gender,
                f"uid {uid}: expected gender {gender!r}, got {affiliate.gender!r}",
            )
