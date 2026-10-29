import { runRules } from "./rules.js";
import { loadModel, scoreWithModel, MODEL_ID } from "./model.js";

const PRESETS: Record<string, string> = {
  kyc:
    "URGENT: Your SBI account will be blocked in 24 hours as your PAN is unlinked. " +
    "Complete KYC now: http://bit.ly/sbi-kyc-update and share the OTP you receive to avoid suspension.",
  upi:
    "Congratulations! You have won Rs 25,00,000 in the UPI Lucky Draw. " +
    "Claim your prize now by clicking http://tinyurl.com/upi-win99 and enter your UPI PIN to receive the money.",
  real:
    "482913 is your OTP for transaction of Rs 1,250.00 at AMAZON on HDFC Bank Card ending 4417. " +
    "Do not share this OTP with anyone. If not done by you, call the number on the back of your card.",
};

// How much each layer counts in the final score.
const MODEL_WEIGHT = 0.4;
const RULE_WEIGHT = 0.6;

function el<T extends HTMLElement>(id: string): T {
  const node = document.getElementById(id);
  if (!node) throw new Error("Missing element: " + id);
  return node as T;
}

const msg = el<HTMLTextAreaElement>("msg");
const analyzeBtn = el<HTMLButtonElement>("analyze");
const statusEl = el<HTMLParagraphElement>("modelStatus");
const resultCard = el<HTMLElement>("result");

let modelReady = false;

function setStatus(text: string, state: "loading" | "ready" | "failed"): void {
  statusEl.textContent = text;
  statusEl.className = "model-status " + state;
}

// Start loading the open-source model as soon as the page opens.
setStatus("Starting open-source model…", "loading");
loadModel((m) => setStatus(m, "loading"))
  .then(() => {
    modelReady = true;
    setStatus("Open-source model ready: " + MODEL_ID, "ready");
  })
  .catch(() => {
    setStatus("Model could not load (check your internet). Rule checks still work.", "failed");
  });

function verdictFor(score: number): { cls: string; text: string } {
  if (score >= 60) return { cls: "danger", text: "High-risk scam" };
  if (score >= 30) return { cls: "warn", text: "Suspicious. Verify first" };
  return { cls: "safe", text: "Looks safe" };
}

async function analyze(): Promise<void> {
  const text = msg.value.trim();
  if (!text) {
    msg.focus();
    return;
  }

  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing…";

  const rules = runRules(text);
  let finalScore = rules.score;
  let aiLine = "Open-source model unavailable. Showing rule-based result only.";

  try {
    const ai = await scoreWithModel(text, (m) => setStatus(m, "loading"));
    if (!modelReady) {
      modelReady = true;
      setStatus("Open-source model ready: " + MODEL_ID, "ready");
    }
    finalScore = Math.round(MODEL_WEIGHT * ai + RULE_WEIGHT * rules.score);
    aiLine = `Model (${MODEL_ID}) says ${ai}% scam. Rule checks say ${rules.score}/100. Combined result shown.`;
  } catch {
    setStatus("Model could not load (check your internet). Rule checks still work.", "failed");
  }

  render(finalScore, rules.flags, rules.good, aiLine);
  analyzeBtn.disabled = false;
  analyzeBtn.textContent = "Analyze message";
}

function render(score: number, flags: string[], good: string[], aiLine: string): void {
  const v = verdictFor(score);

  resultCard.className = "card result " + v.cls;
  el("verdict").textContent = v.text;
  el("scoreNum").textContent = String(score);
  el("meterFill").style.width = score + "%";
  el("aiLine").textContent = aiLine;

  const list = el("flags");
  list.innerHTML = "";

  const items = [...flags, ...good];
  if (items.length === 0) {
    items.push("No known scam patterns found. Stay careful with unexpected messages.");
  }
  for (const t of items) {
    const li = document.createElement("li");
    li.textContent = t; // textContent avoids injecting HTML
    list.appendChild(li);
  }

  resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

document.querySelectorAll<HTMLButtonElement>("[data-preset]").forEach((b) => {
  b.addEventListener("click", () => {
    msg.value = PRESETS[b.dataset.preset ?? ""] ?? "";
    void analyze();
  });
});

analyzeBtn.addEventListener("click", () => void analyze());
