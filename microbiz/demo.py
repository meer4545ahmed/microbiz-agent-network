"""Offline demo runner for MicroBiz; uses synthetic CSVs and no network."""

from microbiz.analysis import analyze_operations


def main() -> None:
    result = analyze_operations(request_id="offline-demo")
    print("MICROBIZ OPERATIONS REVIEW — SYNTHETIC DEMO DATA")
    print(f"Generated: {result.generated_at}")
    print(f"Open orders reviewed: {result.orders_reviewed}")
    print("\nPRIORITIZED FINDINGS")
    for finding in result.findings:
        orders = ", ".join(finding.impacted_order_ids) or "none identified"
        print(
            f"- {finding.product_name} ({finding.sku}): on hand {finding.on_hand}; "
            f"open demand {finding.open_demand}; projected {finding.projected_available}; "
            f"reorder point {finding.reorder_point}; affected orders: {orders}."
        )
        print(
            f"  SUPPLIER DRAFT — OWNER APPROVAL REQUIRED: Ask {finding.supplier_name} "
            f"({finding.supplier_contact}) to confirm availability and lead time for "
            f"{finding.product_name} / {finding.sku}. No message sent."
        )
        for order_id in finding.impacted_order_ids:
            print(
                f"  CUSTOMER DRAFT — OWNER APPROVAL REQUIRED ({order_id}): "
                f"We are checking availability for {finding.product_name} and will "
                "share an update after review. No message sent."
            )
    if result.warnings:
        print("\nDATA WARNINGS")
        for warning in result.warnings:
            print(f"- {warning}")
    print("\nRead-only demo: no orders/inventory changed; no messages or purchases made.")


if __name__ == "__main__":
    main()
