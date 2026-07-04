# Example run

```
$ python signal_engine.py --input sample_accounts.json --threshold 5

Scored 4 accounts, 2 qualified at threshold 5.0

[QUALIFIED] Fieldworks AI         score=15.00
             - Hiring 'Account Executive' (10d ago)
             - Hiring 'SDR Manager' (9d ago)
             - Hiring 'RevOps Lead' (2d ago)
             - Raised Seed 45d ago
             - Tech change: Added Smartlead
             - Tech change: Added Clay
             - High website activity (0.81)
             - Employee count 40 within target band 10-250
[QUALIFIED] Northwind Data        score=13.00
             - Hiring 'Head of Growth' (6d ago)
             - Hiring 'GTM Engineer' (3d ago)
             - Raised Series A 21d ago
             - Tech change: Added HubSpot
             - Tech change: Added Clay
             - High website activity (0.62)
             - Employee count 85 within target band 10-250
[skip     ] Barrow & Finch        score= 1.00
             - Employee count 22 within target band 10-250
[skip     ] Ledgerline            score= 0.00

Routing qualified accounts to outbound sequencing:
  -> Fieldworks AI (account_id=acc_003, score=15.0)
  -> Northwind Data (account_id=acc_001, score=13.0)
```

## Why this ranking makes sense

- **Fieldworks AI** and **Northwind Data** both show the classic "about to
  buy" combination: recent relevant hiring, recent funding, and a tech stack
  change that signals they're actively building out GTM infrastructure right
  now.
- **Ledgerline** is a large, well-funded company with none of those signals
  active this quarter -- still a fine account long-term, just not a good use
  of outbound attention this week.
- **Barrow & Finch** fits the employee-count band but shows no active buying
  signals, so it's correctly filtered out despite being a plausible ICP fit
  on paper.

Swap `load_accounts()` for a Clay webhook, Apollo export, or CRM pull and the
same scoring + routing logic runs unchanged in production.
