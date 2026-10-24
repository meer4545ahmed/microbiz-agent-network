"""Tests for the deterministic, read-only inventory analysis."""

import tempfile
import unittest
from pathlib import Path

from microbiz.analysis import analyze_operations


class AnalyzeOperationsTests(unittest.TestCase):
    def test_sample_data_flags_stockout_and_reorder_warning(self) -> None:
        result = analyze_operations(request_id="test-1")

        self.assertEqual(result.orders_reviewed, 3)
        self.assertEqual([item.sku for item in result.findings], ["TSHIRT-BLK-M", "CAP-NVY"])
        tee = result.findings[0]
        self.assertEqual(tee.open_demand, 3)
        self.assertEqual(tee.projected_available, -1)
        self.assertEqual(tee.impacted_order_ids, ["ORD-1001", "ORD-1002"])
        self.assertFalse(result.warnings)

    def test_malformed_quantity_is_reported_and_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            folder = Path(temporary_directory)
            (folder / "orders.csv").write_text(
                "order_id,sku,quantity,status\nORD-X,SKU-X,not-a-number,processing\n",
                encoding="utf-8",
            )
            (folder / "inventory.csv").write_text(
                "sku,product_name,on_hand,reorder_point,supplier_id\nSKU-X,Demo,4,2,SUP-X\n",
                encoding="utf-8",
            )
            (folder / "suppliers.csv").write_text(
                "supplier_id,supplier_name,contact\nSUP-X,Demo Supplier,supplier@example.invalid\n",
                encoding="utf-8",
            )

            result = analyze_operations(data_dir=folder)

        self.assertEqual(result.orders_reviewed, 0)
        self.assertTrue(any("invalid quantity" in warning for warning in result.warnings))
        self.assertEqual(result.findings, [])

    def test_missing_csv_returns_warning_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = analyze_operations(data_dir=Path(temporary_directory))

        self.assertEqual(result.findings, [])
        self.assertEqual(len(result.warnings), 3)


if __name__ == "__main__":
    unittest.main()
