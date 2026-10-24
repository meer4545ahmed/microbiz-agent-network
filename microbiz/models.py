"""Typed messages shared by the MicroBiz agents."""

from uagents import Model


class OperationsReviewRequest(Model):
    request_id: str


class StockFinding(Model):
    sku: str
    product_name: str
    on_hand: int
    open_demand: int
    projected_available: int
    reorder_point: int
    impacted_order_ids: list[str]
    supplier_name: str
    supplier_contact: str


class OperationsReviewResult(Model):
    request_id: str
    generated_at: str
    orders_reviewed: int
    findings: list[StockFinding]
    warnings: list[str]
