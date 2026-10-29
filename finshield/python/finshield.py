"""
FinShield (Python version): Banking SMS & UPI scam detector.

Uses the same open-source model family as the web app, run locally with
Hugging Face Transformers, plus the same banking rule checks.

Usage:
    python finshield.py                          # paste a message when asked
    python finshield.py --preset kyc             # sample: kyc | upi | real
    python finshield.py --text "your message"
    python finshield.py --preset kyc --no-model  # rules only, no download

First run with the model downloads it once (about 100 MB), then it works offline.
"""

import argparse
import re

# Open-source model (PyTorch weights). The web app uses the ONNX conversion
# of the same model: Xenova/mobilebert-uncased-mnli
MODEL_ID = "typeform/mobilebert-uncased-mnli"
SCAM_LABEL = "a banking scam or phishing attempt"
SAFE_LABEL = "a genuine bank notification"

MODEL_WEIGHT = 0.4
RULE_WEIGHT = 0.6

PRESETS = {
    "kyc": "URGENT: Your SBI account will be blocked in 24 hours as your PAN is unlinked. "
           "Complete KYC now: http://bit.ly/sbi-kyc-update and share the OTP you receive to avoid suspension.",
    "upi": "Congratulations! You have won Rs 25,00,000 in the UPI Lucky Draw. "
           "Claim your prize now by clicking http://tinyurl.com/upi-win99 and enter your UPI PIN to receive the money.",
    "real": "482913 is your OTP for transaction of Rs 1,250.00 at AMAZON on HDFC Bank Card ending 4417. "
            "Do not share this OTP with anyone. If not done by you, call the number on the back of your card.",
}

# (regex, points, reason)
RULES = [
    (r"\b(upi\s*pin|cvv|card\s*pin|atm\s*pin|net\s*banking\s*password|mpin)\b", 35,
     "Asks for or mentions a UPI PIN, CVV or banking password. Real banks never ask for these."),
    (r"\b(bit\.ly|tinyurl\.com|t\.co|goo\.gl|cutt\.ly|rb\.gy|is\.gd|shorturl\.at)\b", 25,
     "Contains a shortened link that hides the real website."),
    (r"https?://\S+", 8,
     "Contains a link. Open banking apps directly instead of tapping links."),
    (r"\b(blocked|suspended|deactivated|frozen|closed)\b", 15,
     "Threatens to block or suspend your account."),
    (r"\b(kyc|pan)\b[\s\S]*\b(update|unlinked|expire|pending|verify|complete)\b|"
     r"\b(update|verify|complete)\b[\s\S]*\b(kyc|pan)\b", 20,
     "Uses a KYC / PAN update excuse, a very common scam script."),
    (r"\b(urgent|immediately|within\s*\d+\s*(hours?|hrs?|minutes?|mins?)|last chance|today only)\b|in\s*24\s*hours", 15,
     "Creates artificial time pressure."),
    (r"\b(won|winner|lottery|lucky draw|prize|reward|cashback|refund)\b", 20,
     "Promises a prize, refund or reward you did not ask for."),
    (r"\b(click|tap)\s+(here|now|below|the link)\b|\bclaim\b", 10,
     "Pushes you to click or claim immediately."),
    (r"\b(anydesk|teamviewer|quicksupport|apk)\b", 30,
     "Asks you to install a remote-access or unknown app."),
]

SAFE_SIGNALS = [
    (r"do not share|don't share|never share", -25,
     "Warns you not to share the OTP, typical of genuine bank alerts."),
    (r"\b(debited|credited|transaction of|txn)\b", -10,
     "Reads like a normal transaction notification."),
]

OTP_REQUEST = (r"\b(otp|one[- ]time password)\b[\s\S]*\b(share|send|tell|forward|enter)\b|"
               r"\b(share|send|tell|forward)\b[\s\S]*\botp\b")
OTP_WARNING = r"do not share|don't share|never share"


def run_rules(text):
    """Returns (score 0-100, risky reasons, genuine reasons)."""
    score, flags, good = 0, [], []

    if re.search(OTP_REQUEST, text, re.I) and not re.search(OTP_WARNING, text, re.I):
        score += 35
        flags.append("Asks you to share or enter an OTP. Banks never request your OTP.")

    for pattern, pts, why in RULES:
        if re.search(pattern, text, re.I):
            score += pts
            flags.append(why)

    for pattern, pts, why in SAFE_SIGNALS:
        if re.search(pattern, text, re.I):
            score += pts
            good.append(why)

    return max(0, min(100, score)), flags, good


_classifier = None


def load_model():
    global _classifier
    if _classifier is None:
        try:
            from transformers import pipeline
        except ImportError as err:
            raise RuntimeError("Install the model libraries first: pip install -r requirements.txt") from err
        print(f"Loading open-source model {MODEL_ID} (first run downloads it)...")
        _classifier = pipeline("zero-shot-classification", model=MODEL_ID)
    return _classifier


def run_model(text):
    """Returns the model's confidence (0-100) that the text is a scam."""
    out = load_model()(text, candidate_labels=[SCAM_LABEL, SAFE_LABEL])
    return round(out["scores"][out["labels"].index(SCAM_LABEL)] * 100)


def verdict(score):
    if score >= 60:
        return "HIGH-RISK SCAM"
    if score >= 30:
        return "SUSPICIOUS - verify first"
    return "LOOKS SAFE"


def analyze(text, use_model=True):
    rule_score, flags, good = run_rules(text)
    final = rule_score
    ai_line = "Model skipped. Using built-in banking rules only."

    if use_model:
        try:
            ai = run_model(text)
            final = round(MODEL_WEIGHT * ai + RULE_WEIGHT * rule_score)
            ai_line = f"Model ({MODEL_ID}) says {ai}% scam. Rule checks say {rule_score}/100."
        except Exception as err:  # keep the tool usable if the model fails
            ai_line = f"Model unavailable ({err}). Showing rule-based result."

    return final, flags + good, ai_line


def show(text, use_model=True):
    score, reasons, ai_line = analyze(text, use_model)
    bar = "#" * (score // 5) + "-" * (20 - score // 5)
    print("\n" + "=" * 54)
    print(f"Verdict : {verdict(score)}")
    print(f"Risk    : {score}/100  [{bar}]")
    print(ai_line)
    print("\nWhy:")
    for r in reasons or ["No known scam patterns found. Stay careful with unexpected messages."]:
        print(" -", r)
    print("=" * 54)
    print("Advisory only. Never share your OTP, UPI PIN or CVV with anyone.\n")


def main():
    parser = argparse.ArgumentParser(description="FinShield banking scam detector")
    parser.add_argument("--preset", choices=PRESETS.keys(), help="run a sample message")
    parser.add_argument("--text", help="message to analyze")
    parser.add_argument("--no-model", action="store_true", help="skip the model, use rules only")
    args = parser.parse_args()

    if args.preset:
        text = PRESETS[args.preset]
        print("Message:", text)
    elif args.text:
        text = args.text
    else:
        text = input("Paste the message to check:\n> ").strip()

    if not text:
        print("No message provided.")
        return
    show(text, use_model=not args.no_model)


if __name__ == "__main__":
    main()
