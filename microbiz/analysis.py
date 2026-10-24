"""Read-only analysis of the bundled synthetic retail CSV files."""

import csv
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from microbiz.models import OperationsReviewResult, StockFinding

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
OPEN_STATUSES = {"awaiting_fulfillment", "processing", "paid", "unfulfilled"}
REQUIRED_COLUMNS = {
    "orders.csv": {"order_id", "sku", "quantity", "status"},
    "inventory.csv": {"sku", "product_name", "on_hand", "reorder_point", "supplier_id"},
    "suppliers.csv": {"supplier_id", "supplier_name", "contact"},
}


def _read_csv(data_dir: Path, filename: str, warnings: list[str]) -> list[dict[str, str]]:
    path = data_dir / filename
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            actual_columns = set(reader.fieldnames or [])
            missing = REQUIRED_COLUMNS[filename] - actual_columns
            if missing:
                warnings.append(f"{filename}: missing required columns: {', '.join(sorted(missing))}.")
                return []
            return list(reader)
    except (OSError, csv.Error) as exc:
        warnings.append(f"{filename}: could not read file ({exc.__class__.__name__}).")
        return []


def analyze_operations(
    request_id: str = "local-demo",
    data_dir: Path | str = DEFAULT_DATA_DIR,
) -> OperationsReviewResult:
    """Analyze sample records without changing files or performing external actions."""
    folder = Path(data_dir)
    warnings: list[str] = []
    supplier_rows = _read_csv(folder, "suppliers.csv", warnings)
    inventory_rows = _read_csv(folder, "inventory.csv", warnings)
    order_rows = _read_csv(folder, "orders.csv", warnings)

    suppliers: dict[str, tuple[str, str]] = {}
    for line_number, row in enumerate(supplier_rows, start=2):
        supplier_id = (row.get("supplier_id") or "").strip()
        supplier_name = (row.get("supplier_name") or "").strip()
        contact = (row.get("contact") or "").strip()
        if not supplier_id or not supplier_name:
            warnings.append(f"suppliers.csv row {line_number}: supplier ID or name is blank; skipped.")
            continue
        if supplier_id in suppliers:
            warnings.append(f"suppliers.csv row {line_number}: duplicate supplier {supplier_id}; first row kept.")
            continue
        suppliers[supplier_id] = (supplier_name, contact or "Contact not provided")

    inventory: dict[str, dict[str, object]] = {}
    for line_number, row in enumerate(inventory_rows, start=2):
        sku = (row.get("sku") or "").strip()
        try:
            on_hand = int(row.get("on_hand", ""))
            reorder_point = int(row.get("reorder_point", ""))
            if on_hand < 0 or reorder_point < 0:
                raise ValueError
        except (TypeError, ValueError):
            warnings.append(f"inventory.csv row {line_number}: invalid stock quantity; skipped.")
            continue
        if not sku:
            warnings.append(f"inventory.csv row {line_number}: SKU is blank; skipped.")
            continue
        if sku in inventory:
            warnings.append(f"inventory.csv row {line_number}: duplicate SKU {sku}; first row kept.")
            continue
        inventory[sku] = {
            "product_name": (row.get("product_name") or "Unnamed product").strip(),
            "on_hand": on_hand,
            "reorder_point": reorder_point,
            "supplier_id": (row.get("supplier_id") or "").strip(),
        }

    demand: dict[str, int] = defaultdict(int)
    affected_orders: dict[str, list[str]] = defaultdict(list)
    reviewed_order_ids: set[str] = set()
    for line_number, row in enumerate(order_rows, start=2):
        order_id = (row.get("order_id") or "").strip()
        sku = (row.get("sku") or "").strip()
        status = (row.get("status") or "").strip().lower()
        if status not in OPEN_STATUSES:
            continue
        try:
            quantity = int(row.get("quantity", ""))
            if quantity <= 0:
                raise ValueError
        except (TypeError, ValueError):
            warnings.append(f"orders.csv row {line_number}: invalid quantity; skipped.")
            continue
        if not order_id or not sku:
            warnings.append(f"orders.csv row {line_number}: order ID or SKU is blank; skipped.")
            continue
        if sku not in inventory:
            warnings.append(f"orders.csv row {line_number}: SKU {sku} has no valid inventory record.")
            continue
        demand[sku] += quantity
        reviewed_order_ids.add(order_id)
        affected_orders[sku].append(order_id)

    findings: list[StockFinding] = []
    for sku, item in inventory.items():
        on_hand = int(item["on_hand"])
        reorder_point = int(item["reorder_point"])
        open_demand = demand[sku]
        projected = on_hand - open_demand
        if projected >= 0 and on_hand > reorder_point:
            continue
        supplier_id = str(item["supplier_id"])
        supplier_name, supplier_contact = suppliers.get(
            supplier_id, ("Supplier not found", "Contact not provided")
        )
        if supplier_id not in suppliers:
            warnings.append(f"inventory SKU {sku}: no matching supplier record; draft will use a placeholder.")
        findings.append(
            StockFinding(
                sku=sku,
                product_name=str(item["product_name"]),
                on_hand=on_hand,
                open_demand=open_demand,
                projected_available=projected,
                reorder_point=reorder_point,
                impacted_order_ids=sorted(set(affected_orders[sku])),
                supplier_name=supplier_name,
                supplier_contact=supplier_contact,
            )
        )

    findings.sort(key=lambda finding: (finding.projected_available, finding.sku))
    return OperationsReviewResult(
        request_id=request_id,
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        orders_reviewed=len(reviewed_order_ids),
        findings=findings,
        warnings=warnings,
    )


if __name__ == "__main__":
    print(analyze_operations().json(indent=2))
