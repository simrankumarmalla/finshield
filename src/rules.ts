// Banking-specific rule checks. Runs instantly in the browser, no network needed.

export interface RuleResult {
  score: number;      // 0 to 100
  flags: string[];    // reasons the message looks risky
  good: string[];     // reasons the message looks genuine
}

interface Rule {
  pattern: RegExp;
  points: number;
  why: string;
}

const RULES: Rule[] = [
  {
    pattern: /\b(upi\s*pin|cvv|card\s*pin|atm\s*pin|net\s*banking\s*password|mpin)\b/i,
    points: 35,
    why: "Asks for or mentions a UPI PIN, CVV or banking password. Real banks never ask for these.",
  },
  {
    pattern: /\b(bit\.ly|tinyurl\.com|t\.co|goo\.gl|cutt\.ly|rb\.gy|is\.gd|shorturl\.at)\b/i,
    points: 25,
    why: "Contains a shortened link that hides the real website.",
  },
  {
    pattern: /https?:\/\/\S+/i,
    points: 8,
    why: "Contains a link. Open banking apps directly instead of tapping links.",
  },
  {
    pattern: /\b(blocked|suspended|deactivated|frozen|closed)\b/i,
    points: 15,
    why: "Threatens to block or suspend your account.",
  },
  {
    pattern: /\b(kyc|pan)\b[\s\S]*\b(update|unlinked|expire|pending|verify|complete)\b|\b(update|verify|complete)\b[\s\S]*\b(kyc|pan)\b/i,
    points: 20,
    why: "Uses a KYC / PAN update excuse, a very common scam script.",
  },
  {
    pattern: /\b(urgent|immediately|within\s*\d+\s*(hours?|hrs?|minutes?|mins?)|last chance|today only)\b|in\s*24\s*hours/i,
    points: 15,
    why: "Creates artificial time pressure.",
  },
  {
    pattern: /\b(won|winner|lottery|lucky draw|prize|reward|cashback|refund)\b/i,
    points: 20,
    why: "Promises a prize, refund or reward you did not ask for.",
  },
  {
    pattern: /\b(click|tap)\s+(here|now|below|the link)\b|\bclaim\b/i,
    points: 10,
    why: "Pushes you to click or claim immediately.",
  },
  {
    pattern: /\b(anydesk|teamviewer|quicksupport|apk)\b/i,
    points: 30,
    why: "Asks you to install a remote-access or unknown app.",
  },
];

const SAFE_SIGNALS: Rule[] = [
  {
    pattern: /do not share|don't share|never share/i,
    points: -25,
    why: "Warns you not to share the OTP, typical of genuine bank alerts.",
  },
  {
    pattern: /\b(debited|credited|transaction of|txn)\b/i,
    points: -10,
    why: "Reads like a normal transaction notification.",
  },
];

const OTP_REQUEST =
  /\b(otp|one[- ]time password)\b[\s\S]*\b(share|send|tell|forward|enter)\b|\b(share|send|tell|forward)\b[\s\S]*\botp\b/i;
const OTP_WARNING = /do not share|don't share|never share/i;

export function runRules(text: string): RuleResult {
  let score = 0;
  const flags: string[] = [];
  const good: string[] = [];

  // Asking for an OTP is a scam sign, but "do not share your OTP" is a genuine warning.
  if (OTP_REQUEST.test(text) && !OTP_WARNING.test(text)) {
    score += 35;
    flags.push("Asks you to share or enter an OTP. Banks never request your OTP.");
  }

  for (const rule of RULES) {
    if (rule.pattern.test(text)) {
      score += rule.points;
      flags.push(rule.why);
    }
  }

  for (const signal of SAFE_SIGNALS) {
    if (signal.pattern.test(text)) {
      score += signal.points;
      good.push(signal.why);
    }
  }

  return { score: Math.max(0, Math.min(100, score)), flags, good };
}
