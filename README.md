# MicroBiz Agent Network

A beginner-friendly, two-agent demo for a small retailer. The owner asks for an operations review; a Coordinator delegates to an Operations Analyst, which reads fictional CSV files and calculates stock risks. The Coordinator returns evidence plus supplier/customer message drafts for owner approval.

> **Demo-only data:** Orders, stock, and suppliers in `data/` are fictional. This MVP does not connect to a real store.
>
> **No side effects:** It does not send messages, change orders or inventory, or place purchases. All generated messages are drafts requiring owner review.

## What it demonstrates

- Two uAgents with a typed agent-to-agent request and response.
- Agent Chat Protocol (ACP) for the user-facing Coordinator.
- Deterministic Python/CSV analysis rather than model-generated stock arithmetic.
- Findings that include stock on hand, open demand, projected stock, reorder point, and affected synthetic orders.
- Clear data warnings and approval-only drafts.

## Current status

- [x] Project structure, sample data, deterministic analyzer, and tests scaffolded.
- [x] Coordinator and Analyst agent code added.
- [x] Install Python 3.12 and project dependencies.
- [x] Run the CSV analysis tests and verify both agent modules import.
- [x] Generate local agent seeds and start the Analyst; its typed protocol manifest published successfully.
- [x] Connect both local agents to Agentverse Mailbox using the Inspector UI.
- [ ] Complete Agentverse profile setup checklist for both agents. Coordinator now has handle `microbiz-ops`, Agent Chat Protocol, Agent Guide, and description; checklist was 58% at last screenshot. The Agentverse Testing page generated 5 questions, but its Run Test button is disabled while the agent is marked Inactive. Use successful direct ASI:One chats to build real interactions; do not claim the checklist or activation is complete until the portal confirms it.
- [x] Verify ASI:One direct chat and real ACP delegation end-to-end: sent the review request to the Coordinator, Analyst logged receiving the typed request and returning two findings, Coordinator logged delegation and return, and ASI:One displayed the final report/drafts.
- [ ] Publish a safe public GitHub repository and record final demo links.

## Requirements

Use **Python 3.12** for this project. Although uAgents compatibility information lists Python 3.10–3.13, dependency installation on Python 3.13 failed here because pip could not find a compatible `grpcio` distribution. Python 3.12 installed the full dependency set successfully. Python 3.14 and 3.15 are not listed as supported. Keep existing Python installations; install 3.12 side-by-side.

### Windows PowerShell setup

1. Install Python 3.12 from the official Python downloads page: <https://www.python.org/downloads/>. During setup, enable the Python launcher if offered.
2. Close and reopen the VS Code terminal, then check that the launcher sees Python 3.12:

   ```powershell
   py -0p
   ```

   You should see an entry for `3.12`.

3. From the repository root, create a virtual environment and install project dependencies:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   Calling the virtual environment's Python directly avoids PowerShell activation-policy issues.

4. Run the deterministic analyzer tests:

   ```powershell
   .\.venv\Scripts\python.exe -m unittest discover -s tests -v
   ```

   Expected: 3 tests pass.

5. Run the analyzer once against the bundled synthetic data:

   ```powershell
   .\.venv\Scripts\python.exe -m microbiz.analysis
   ```

   The output is JSON. You should see findings for `TSHIRT-BLK-M` and `CAP-NVY`.

## Configure agent identities

1. Copy the example environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Generate two different random agent seed phrases locally. Run this command twice and keep each result private:

   ```powershell
   .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
   ```

3. Open `.env` in VS Code and replace the two seed placeholders with the two generated values. Do not paste seeds into chat, commit `.env`, or reuse a password. `.env` is ignored by Git.

The Analyst must be started first. Its startup prints its agent address. Copy that address into `ANALYST_ADDRESS` in `.env` before starting the Coordinator. Never use real order/customer data in the demo.

## Run the agents

Open two terminals in the repository root. Start the Analyst first:

```powershell
.\.venv\Scripts\python.exe -m microbiz.analyst
```

Copy the printed Analyst address into `.env`. Then start the Coordinator in the second terminal:

```powershell
.\.venv\Scripts\python.exe -m microbiz.coordinator
```

The Coordinator is the user-facing agent. Both local agents have been connected to Agentverse Mailbox through the Inspector UI. Keep both running during a demo. A direct ASI:One profile chat was verified end-to-end with a real Coordinator-to-Analyst ACP exchange and report. The Agentverse profiles may still require their setup checklist before showing as active/discoverable in search. Do not send funds or apply wallet credit to address the Almanac on-chain low-funds warning. The hackathon image's offer advertises one month of ASI:One Pro and Agentverse Premium, not $100 of wallet funds; it is unrelated to this local CSV demo.

## Demo prompt

> Review today's orders and inventory, identify problems, and prepare the actions I need to take.

Direct ASI:One Coordinator profile: <https://asi1.ai/ai/agent1qwr3zl3gsy6rjl0c7uzvq7a6nkwkejg6dz7je2xgfd6hgzdznph8u8ggx2x>
Coordinator Agentverse profile: <https://agentverse.ai/agents/details/agent1qwr3zl3gsy6rjl0c7uzvq7a6nkwkejg6dz7je2xgfd6hgzdznph8u8ggx2x/profile>
Analyst Agentverse profile: <https://agentverse.ai/agents/details/agent1qv3y2qm3nly22jkryp0x7c8mqnnjuhpwmj0yv29grday5533nnqgztlpy3a/profile>

Expected sample result:

   - `TSHIRT-BLK-M`: 2 units on hand; 3 units in open orders; projected stock after demand is -1; affected orders are `ORD-1001` and `ORD-1002`.
   - `CAP-NVY`: at/below the reorder point.
   - A supplier inquiry draft and customer update drafts, clearly marked for owner approval.
   - No email or other message is sent, and no data file is changed.

- `TSHIRT-BLK-M`: 2 units on hand; 3 units in open orders; projected stock after demand is -1; affected orders are `ORD-1001` and `ORD-1002`.
- `CAP-NVY`: at/below the reorder point.
- A supplier inquiry draft and customer update drafts, clearly marked for owner approval.
- No email or other message is sent, and no data file is changed.

### Fast offline presentation fallback

If Agentverse/ASI:One is unavailable, run the local deterministic demo. This does not require mailbox access or an API key:

```powershell
.\.venv\Scripts\python.exe -m microbiz.demo
```

It prints the same synthetic-data findings and approval-only draft examples in the terminal. Be transparent during the presentation: this local fallback demonstrates the data-analysis workflow, but it does not prove ASI:One or remote ACP delivery.

## Data files

- `data/orders.csv`: `order_id`, `sku`, `quantity`, `status`.
- `data/inventory.csv`: `sku`, `product_name`, `on_hand`, `reorder_point`, `supplier_id`.
- `data/suppliers.csv`: `supplier_id`, `supplier_name`, `contact`.

Supplier contacts use the reserved `.invalid` domain and are not real addresses.

## Architecture

```text
Owner in ASI:One
       |
MicroBiz Coordinator (Chat Protocol / ACP)
       | typed OperationsReviewRequest over uAgents
Operations Analyst
       | read-only CSV tool + deterministic checks
       v
Structured findings and warnings
       |
Coordinator creates approval-only drafts and returns the report
```

The MVP uses local CSV fixtures, not a live shop connector. A future integration must target one named platform (such as Shopify or WooCommerce) and use narrowly scoped read-only access. API credentials must never be sent to an LLM or exposed in chat, logs, README, or source control.

## Troubleshooting

- **`No suitable Python runtime found` for `py -3.12`:** install Python 3.12 from python.org, reopen VS Code, and check `py -0p` again.
- **`ModuleNotFoundError: uagents` or `dotenv`:** install requirements using the `.venv` Python command above.
- **Missing seed/address error:** edit local `.env`; make sure the Analyst seed and Coordinator seed differ and use the address printed by the running Analyst.
- **Agent communication fails:** keep both agents running, verify the copied address exactly, and complete any Agentverse mailbox setup requested by the current service.
- **Do not paste secrets or real customer/order data into issue reports or chat.** Share error messages only after removing keys, seed values, addresses if private, and personal data.

## Decision and build log

- **2026-10-24:** Selected MicroBiz Agent Network instead of trip planning. Limited the first build to two agents, fictional CSVs, deterministic stock analysis, and owner-approved drafts.
- **2026-10-24:** Confirmed there is no test shop/API access available today. Live platform connectors are deferred; no generic API-key integration is claimed.
- **2026-10-24:** Detected Python 3.14.7 and 3.15 on the machine. Installed Python 3.13, but its dependency install failed because pip could not find a compatible `grpcio` distribution. Installed Python 3.12 side-by-side instead.
- **2026-10-24:** Added initial source/data/tests and installed dependencies in `.venv` using Python 3.12. All 3 CSV tests pass. Two unique seeds were generated directly into ignored `.env` without displaying them. Agentverse Inspector confirmed mailbox connections for both agents. Agentverse public profiles still show Inactive and require completion of their profile checklist. Added local profile descriptions/readmes. User set the Coordinator handle to `microbiz-ops`, and completed the Coordinator's Agent Guide and description. Verified direct ASI:One chat end-to-end: Coordinator delegated the typed request over ACP, Analyst read synthetic CSVs and returned two findings, and Coordinator returned the report plus approval-only drafts. Agentverse checklist was at 58% at the latest screenshot; next use the checklist's Send Test Prompts action to reach 10 interactions, then recheck inactive status. General personal-AI chat may still hang, but direct Coordinator chat works. Account rate limits show OK. Added `python -m microbiz.demo` as an offline fallback. Do not purchase anything. No wallet funds or promo redemption used.

This log records decisions and build milestones, not a verbatim copy of private conversations.
