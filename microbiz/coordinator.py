"""ASI:One-facing MicroBiz Coordinator agent."""

import os
import time
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)

from microbiz.models import OperationsReviewRequest, OperationsReviewResult, StockFinding

load_dotenv()

seed = os.getenv("COORDINATOR_SEED", "").strip()
analyst_address = os.getenv("ANALYST_ADDRESS", "").strip()
if not seed or seed.startswith("replace-"):
    raise RuntimeError("Set a unique COORDINATOR_SEED in your local .env file first.")
if not analyst_address or analyst_address.startswith("replace-"):
    raise RuntimeError("Set ANALYST_ADDRESS in .env to the address printed by the running analyst.")

coordinator = Agent(
    name="microbiz-operations-coordinator",
    seed=seed,
    port=8000,
    mailbox=True,
    description="Coordinates a small-retailer operations review over ACP and prepares stock findings plus approval-only supplier/customer drafts.",
    readme_path=str(Path(__file__).with_name("agent_profile.md")),
)

chat_protocol = Protocol(spec=chat_protocol_spec)
operations_protocol = Protocol(name="MicroBizOperations", version="0.1.0")
pending_requests: dict[str, tuple[str, float]] = {}


def create_text_chat(text: str) -> ChatMessage:
    """Create a Chat Protocol response containing plain text."""
    from datetime import datetime, timezone

    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )


def format_finding(finding: StockFinding) -> str:
    orders = ", ".join(finding.impacted_order_ids) or "none currently identified"
    return (
        f"- **{finding.product_name} ({finding.sku})**: {finding.on_hand} on hand; "
        f"{finding.open_demand} units in open orders; projected stock after demand: "
        f"{finding.projected_available}; reorder point: {finding.reorder_point}. "
        f"Affected orders: {orders}."
    )


def create_owner_review(result: OperationsReviewResult) -> str:
    """Format evidence and drafts; this function never contacts anyone."""
    lines = [
        "**MicroBiz operations review (synthetic demo data)**",
        f"Generated: {result.generated_at}",
        f"Open orders reviewed: {result.orders_reviewed}",
    ]
    if result.findings:
        lines.append("\n**Prioritized stock findings**")
        lines.extend(format_finding(finding) for finding in result.findings)
        lines.append("\n**Supplier inquiry draft — OWNER APPROVAL REQUIRED**")
        for finding in result.findings:
            lines.append(
                f"\nTo: {finding.supplier_contact} ({finding.supplier_name})\n"
                f"Subject: Availability inquiry for {finding.sku}\n"
                f"Hello, could you please confirm current availability and lead time for "
                f"{finding.product_name} (SKU {finding.sku})? Our sample data shows "
                f"{finding.on_hand} units on hand and a reorder point of "
                f"{finding.reorder_point}. This is a draft only; no message was sent."
            )
        affected = [
            (finding, order_id)
            for finding in result.findings
            for order_id in finding.impacted_order_ids
        ]
        if affected:
            lines.append("\n**Customer update drafts — OWNER APPROVAL REQUIRED**")
            for finding, order_id in affected:
                lines.append(
                    f"\nOrder {order_id}: Hello, we’re reviewing availability for your "
                    f"{finding.product_name}. We’ll share an update once the shop confirms "
                    "the next step. This is a draft only; no message was sent."
                )
    else:
        lines.append("\nNo low-stock or fulfilment risk was found in the demo records.")
    if result.warnings:
        lines.append("\n**Data warnings**")
        lines.extend(f"- {warning}" for warning in result.warnings)
    lines.append("\nNo orders, inventory, or messages were changed or sent. Please review all drafts before use.")
    return "\n".join(lines)


@chat_protocol.on_message(ChatMessage)
async def handle_user_chat(ctx: Context, sender: str, msg: ChatMessage) -> None:
    """Acknowledge a chat request and delegate it to the analyst over ACP."""
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=msg.timestamp, acknowledged_msg_id=msg.msg_id),
    )
    has_text = any(isinstance(item, TextContent) and item.text.strip() for item in msg.content)
    if not has_text:
        return

    request_id = str(uuid4())
    pending_requests[request_id] = (sender, time.monotonic())
    await ctx.send(sender, create_text_chat("I’m reviewing the sample orders and inventory now. I’ll return findings and approval-only drafts."))
    await ctx.send(analyst_address, OperationsReviewRequest(request_id=request_id))
    ctx.logger.info("Delegated review %s to Operations Analyst", request_id)


@chat_protocol.on_message(ChatAcknowledgement)
async def handle_user_ack(ctx: Context, sender: str, msg: ChatAcknowledgement) -> None:
    ctx.logger.info("Chat acknowledgement from %s for %s", sender, msg.acknowledged_msg_id)


@operations_protocol.on_message(OperationsReviewResult)
async def handle_analysis_result(
    ctx: Context, sender: str, msg: OperationsReviewResult
) -> None:
    """Return the analyst result to the original ASI:One conversation sender."""
    pending = pending_requests.pop(msg.request_id, None)
    if pending is None:
        ctx.logger.warning("Received uncorrelated review result %s", msg.request_id)
        return
    user_address, _started_at = pending
    await ctx.send(user_address, create_text_chat(create_owner_review(msg)))
    ctx.logger.info("Returned review %s to the user", msg.request_id)


@coordinator.on_interval(period=5.0)
async def expire_slow_reviews(ctx: Context) -> None:
    """Tell the user when the analyst has not replied within 45 seconds."""
    now = time.monotonic()
    expired = [
        request_id
        for request_id, (_user_address, started_at) in pending_requests.items()
        if now - started_at > 45
    ]
    for request_id in expired:
        user_address, _started_at = pending_requests.pop(request_id)
        await ctx.send(
            user_address,
            create_text_chat(
                "I couldn’t reach the Operations Analyst in time. Please confirm both agents are running and try again. No data was changed."
            ),
        )
        ctx.logger.warning("Review %s timed out waiting for the Analyst", request_id)


coordinator.include(chat_protocol, publish_manifest=True)
coordinator.include(operations_protocol, publish_manifest=True)


if __name__ == "__main__":
    print(f"Coordinator agent address: {coordinator.address}")
    coordinator.run()
