#!/usr/bin/env python3
"""
Signal-Based Prospecting Engine
--------------------------------
Detects hiring activity, funding events, and technology changes across a
list of accounts, scores each account's buying intent, and routes
qualified accounts into an output list ready for personalized outbound
sequencing (e.g. into Clay / Smartlead / HubSpot).

This standalone version reads accounts from a local JSON file so it is
fully runnable without any external API keys. In production, `load_accounts`
is the seam you'd swap out for a Clay webhook, Apollo export, or a CRM pull.

Usage:
    python signal_engine.py --input sample_accounts.json --threshold 5
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List


# --------------------------------------------------------------------------
# Scoring weights -- tune these against your own ICP definition.
# --------------------------------------------------------------------------

WEIGHTS = {
    "relevant_hire_posted_recently": 2.0,   # each relevant open role posted <14 days ago
    "recent_funding": 3.0,                  # funding announced <90 days ago
    "tech_stack_signal": 1.5,               # each relevant tech stack change
    "high_website_activity": 2.0,           # website_activity_score > 0.5
    "employee_band_fit": 1.0,               # employee_count within target band
}

RELEVANT_HIRE_KEYWORDS = ("growth", "gtm", "revops", "revenue operations", "sdr", "account executive")
RELEVANT_TECH_KEYWORDS = ("clay", "hubspot", "smartlead", "apollo")
TARGET_EMPLOYEE_BAND = (10, 250)


@dataclass
class ScoredAccount:
    account_id: str
    company: str
    score: float
    reasons: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------

def load_accounts(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------

def score_account(account: Dict[str, Any]) -> ScoredAccount:
    score = 0.0
    reasons: List[str] = []

    # Hiring signals
    for hire in account.get("hiring_signals", []):
        role = hire.get("role", "").lower()
        posted_days_ago = hire.get("posted_days_ago", 9999)
        if posted_days_ago <= 14 and any(kw in role for kw in RELEVANT_HIRE_KEYWORDS):
            score += WEIGHTS["relevant_hire_posted_recently"]
            reasons.append(f"Hiring '{hire.get('role')}' ({posted_days_ago}d ago)")

    # Funding signals
    funding = account.get("funding") or {}
    announced_days_ago = funding.get("announced_days_ago")
    if announced_days_ago is not None and announced_days_ago <= 90:
        score += WEIGHTS["recent_funding"]
        reasons.append(f"Raised {funding.get('stage')} {announced_days_ago}d ago")

    # Tech stack signals
    for change in account.get("tech_stack_changes", []):
        if any(kw in change.lower() for kw in RELEVANT_TECH_KEYWORDS):
            score += WEIGHTS["tech_stack_signal"]
            reasons.append(f"Tech change: {change}")

    # Website activity
    activity = account.get("website_activity_score", 0.0)
    if activity > 0.5:
        score += WEIGHTS["high_website_activity"]
        reasons.append(f"High website activity ({activity:.2f})")

    # Employee band fit
    employees = account.get("employee_count", 0)
    lo, hi = TARGET_EMPLOYEE_BAND
    if lo <= employees <= hi:
        score += WEIGHTS["employee_band_fit"]
        reasons.append(f"Employee count {employees} within target band {lo}-{hi}")

    return ScoredAccount(
        account_id=account["account_id"],
        company=account["company"],
        score=round(score, 2),
        reasons=reasons,
        raw=account,
    )


def rank_accounts(accounts: List[Dict[str, Any]]) -> List[ScoredAccount]:
    scored = [score_account(a) for a in accounts]
    scored.sort(key=lambda a: a.score, reverse=True)
    return scored


def qualify(scored: List[ScoredAccount], threshold: float) -> List[ScoredAccount]:
    return [a for a in scored if a.score >= threshold]


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Signal-Based Prospecting Engine")
    parser.add_argument("--input", default="sample_accounts.json", help="Path to accounts JSON file")
    parser.add_argument("--threshold", type=float, default=5.0, help="Minimum score to qualify an account")
    args = parser.parse_args()

    accounts = load_accounts(args.input)
    ranked = rank_accounts(accounts)
    qualified = qualify(ranked, args.threshold)

    print(f"Scored {len(ranked)} accounts, {len(qualified)} qualified at threshold {args.threshold}\n")
    for a in ranked:
        flag = "QUALIFIED" if a in qualified else "skip"
        print(f"[{flag:9}] {a.company:20} score={a.score:5.2f}")
        for reason in a.reasons:
            print(f"             - {reason}")
    print()

    print("Routing qualified accounts to outbound sequencing:")
    for a in qualified:
        print(f"  -> {a.company} (account_id={a.account_id}, score={a.score})")


if __name__ == "__main__":
    main()
