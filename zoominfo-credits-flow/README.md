# ZoomInfo + Claude/Slack Credits Flow

Three related flowcharts so product, IT, ops and brokers can reason about the
same thing from different angles. Each is an SVG (vector, opens in any browser)
with a PNG export alongside for quick preview / pasting into decks.

| File | Audience | Answers |
|------|----------|---------|
| `1-end-to-end-stakeholder-flow.svg` | Product / IT / Ops | How a query moves through Slack/Claude → ZoomInfo → Salesforce, and where credits are (and aren't) spent |
| `2-broker-user-experience.svg` | Brokers / enablement | What the broker actually sees and does, with the spend-protecting confirmation step called out |
| `3-credits-governance.svg` | Ops / finance | The three independent cost meters, when each is charged, and the controls to keep spend predictable |

## The core mental model (from the call)

There are **three independent cost events** — they are easy to conflate:

1. **Claude usage credits** — charged per query (~$1). Always applies when the
   agent runs. Separate from ZoomInfo.
2. **ZoomInfo AI action credits** — *research* (company history, list building).
   ~100 are auto-granted each time a user connects an MCP.
   **Risk:** today this is effectively unlimited and *any* MCP connection
   (even a personal ChatGPT) draws from the shared pool.
3. **ZoomInfo bulk credits** — *contact enrichment* (phone/email),
   **1 credit per contact**. 5,000 allocated per pilot user, drawn from 25,000
   moved out of Simone's company-level pool. Ops-managed directly.

**Key behavior:** asking for a *list* of names + titles is **free**. You only
spend **bulk credits** when you pull **contact details** for specific people.
That gap is the single most important lever for controlling spend — hence the
explicit "pull contact info?" confirmation in diagram 2.

## Decisions captured

- Pilot is funded by moving credits from bucket A (Simone / data product +
  data lake) to bucket B (pilot) — a **trial**, with an FY decision point:
  chargeback model vs. drive adoption.
- Don't over-streamline out of the gate. Let the agent pick the best/freshest
  source (ZoomInfo, Rhetorik, LinkedIn/Sales Nav, 10-Ks), **monitor
  consumption**, then curtail if needed.
- Tie accounts to a **ZoomInfo ID field in Salesforce** for enrichment,
  dedup, and triage.
- Start with a **very small pilot** (e.g. Joe) before widening access.

## Open questions / to confirm (shown in red on the diagrams)

- Ask ZoomInfo to **cap AI action credits per user** (default 100 and stop,
  not unlimited).
- **Managed-account dedup:** repeat asks on already-enriched companies should
  not re-charge — confirm whether there's a *delta* charge, and whether this
  can be managed at the **MDM / enterprise level** so OneCap + Occupier asking
  the same question don't double-charge.
- Net-new enrichment via per-user MCP currently charges **that user**; pulling
  into the CRM via MCP still charges. Can one pull be made to **count for
  everyone** (enterprise visibility)?
- Does **Slack bot** actually reach ZoomInfo yet, and do we need both the Slack
  apps (Sales OS vs. Copilot)? Pending a technical conversation with ZoomInfo.
- Pilot scope: Industry CRM vs. Occupier CRM (or both); contacts open vs.
  closed; the enrichment business process.

## Regenerating the PNGs

```bash
pip install cairosvg
for f in *.svg; do python3 -c "import cairosvg; cairosvg.svg2png(url='$f', write_to='${f%.svg}.png', scale=2.0)"; done
```

> Note: speaker attributions in the source transcript were rough; this captures
> the substance of the discussion, not verbatim quotes. Treat the red items as
> open questions to validate with ZoomInfo and the pilot users.
