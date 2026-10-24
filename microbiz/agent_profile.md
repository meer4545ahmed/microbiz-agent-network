# MicroBiz Operations Agent Network

MicroBiz helps small retailers review orders and inventory in one operations workflow. The Coordinator accepts a review request, delegates a structured request to the Operations Analyst, and returns prioritized findings with supplier/customer message drafts for the shop owner's review.

## What it can do

- Read the bundled fictional orders, inventory, and supplier CSV files.
- Identify open-order demand, projected stock, reorder warnings, and affected order IDs.
- Prepare supplier inquiry and customer update drafts grounded in the supplied records.
- Report missing or malformed data rather than inventing values.

## How to use

Ask: "Review today's orders and inventory, identify problems, and prepare the actions I need to take."

The Coordinator uses the Agent Chat Protocol. The Analyst accepts a typed `OperationsReviewRequest` through the `MicroBizOperations` protocol and returns an `OperationsReviewResult`.

## Safety and demo boundaries

This hackathon MVP uses synthetic local CSVs only; it is not connected to a real shop. It never sends messages, edits orders or inventory, or places purchases. All communications are drafts labeled for owner approval. Do not provide real customer data or secrets in chat.
