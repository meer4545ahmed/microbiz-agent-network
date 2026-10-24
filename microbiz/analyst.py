"""Operations Analyst agent: runs deterministic, read-only CSV analysis."""

import os
from pathlib import Path

from dotenv import load_dotenv
from uagents import Agent, Context, Protocol

from microbiz.analysis import analyze_operations
from microbiz.models import OperationsReviewRequest, OperationsReviewResult

load_dotenv()

seed = os.getenv("ANALYST_SEED", "").strip()
if not seed or seed.startswith("replace-"):
    raise RuntimeError("Set a unique ANALYST_SEED in your local .env file first.")

analyst = Agent(
    name="microbiz-operations-analyst",
    seed=seed,
    port=8001,
    mailbox=True,
    description="Analyzes fictional retail orders, inventory, and supplier records; returns evidence-based stock risks and owner-review drafts.",
    readme_path=str(Path(__file__).with_name("agent_profile.md")),
)

operations_protocol = Protocol(name="MicroBizOperations", version="0.1.0")


@operations_protocol.on_message(OperationsReviewRequest, replies=OperationsReviewResult)
async def review_operations(
    ctx: Context, sender: str, msg: OperationsReviewRequest
) -> None:
    """Run the local analysis and return structured findings to the coordinator."""
    ctx.logger.info("Received read-only operations review request %s", msg.request_id)
    result = analyze_operations(request_id=msg.request_id)
    await ctx.send(sender, result)
    ctx.logger.info("Sent review result %s with %d finding(s)", msg.request_id, len(result.findings))


analyst.include(operations_protocol, publish_manifest=True)


if __name__ == "__main__":
    print(f"Analyst agent address: {analyst.address}")
    analyst.run()
