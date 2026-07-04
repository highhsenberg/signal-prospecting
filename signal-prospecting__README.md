# Signal-Based Prospecting Engine

Detects hiring activity, funding events, and technology changes across a
list of accounts. Scores each account against ICP criteria and routes
high-intent accounts into an output list ready for personalized outbound
sequencing (Clay / Smartlead / HubSpot, or any sequencing tool).

See [`example_output.md`](./example_output.md) for a full run against the
included sample data, with reasoning for why each account did or didn't
qualify.

## How scoring works

Each account earns points for signals that correlate with active buying
intent, not just ICP fit on paper:

| Signal | Points | Why it matters |
|---|---|---|
| Relevant role posted in the last 14 days (Growth, GTM, RevOps, SDR, AE) | +2.0 each | Actively building out the function you'd sell into |
| Funding announced in the last 90 days | +3.0 | Budget just unlocked |
| Relevant tech stack change (Clay, HubSpot, Smartlead, Apollo) | +1.5 each | Actively investing in GTM infrastructure right now |
| Website activity score > 0.5 | +2.0 | Elevated engagement, not just a cold record |
| Employee count within target band | +1.0 | Basic ICP fit |

Weights and keyword lists are defined as constants at the top of
`signal_engine.py` so they're easy to tune against your own ICP without
touching the scoring logic.

## Install

No external dependencies beyond the Python standard library.

## Usage

```bash
python signal_engine.py --input sample_accounts.json --threshold 5
```

`load_accounts()` is the integration seam -- swap it for a Clay webhook
payload, an Apollo export, or a CRM query and everything downstream (scoring,
qualification, routing) runs unchanged.

## Project structure

```
signal_engine.py          -- scoring + qualification + routing logic
sample_accounts.json       -- 4 example accounts covering qualified / unqualified cases
example_output.md          -- full example run with reasoning
```

## Limitations / next steps

- Signal weights here are a reasonable starting point, not a trained model --
  the natural next step is fitting weights against historical won/lost deals.
- Currently single-run / batch; a production version would run on a schedule
  or via webhook as new signals arrive, and de-duplicate against accounts
  already in an active sequence.
