"""Quick checks for the rule layer. Run:  python test_rules.py"""
from finshield import PRESETS, run_rules, verdict


def check(name, expected):
    score, _, _ = run_rules(PRESETS[name])
    got = verdict(score)
    status = "PASS" if got.startswith(expected) else "FAIL"
    print(f"{status}  {name:5} score={score:3}  {got}")
    return status == "PASS"


ok = all([check("kyc", "HIGH"), check("upi", "HIGH"), check("real", "LOOKS SAFE")])
raise SystemExit(0 if ok else 1)
