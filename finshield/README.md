# FinShield: Privacy-First Banking SMS & UPI Scam Detector

FinShield checks a pasted bank SMS, email or payment message and says whether it looks like a scam.
It combines an **open-source AI model** that runs inside your browser with **banking-specific rule checks**,
then explains exactly why a message was flagged.

## Problem
Customers lose money to "smishing": fake KYC-suspension texts, fake UPI prize links and fake OTP requests.
People also hesitate to paste financial messages into cloud tools. FinShield runs on the user's device.

## How it works
1. **Open-source model layer.** `Xenova/mobilebert-uncased-mnli` (ONNX conversion of MobileBERT fine-tuned on MNLI)
   runs in the browser through Transformers.js. It does zero-shot classification: how well does the message fit
   "a banking scam or phishing attempt" versus "a genuine bank notification".
2. **Rule layer.** Checks for shortened links, UPI PIN / CVV / OTP requests, panic wording, KYC / PAN excuses,
   prize bait and remote-access apps. It also recognises genuine "do not share your OTP" warnings.
3. **Combined score.** 40% model, 60% rules, shown as a 0 to 100 risk meter with a list of reasons.

## Privacy and responsible AI
- No server, no database, no analytics. Pasted text never leaves the browser.
- Decisions are explainable: every flag is listed in plain language.
- Results are advisory only. The model is a general-purpose zero-shot model, not a fine-tuned fraud detector,
  so it can be wrong. Never share your OTP, UPI PIN or CVV.

## Project layout
```
finshield/
  index.html          page
  style.css           styling
  src/                TypeScript source (rules.ts, model.ts, main.ts)
  dist/               compiled JavaScript the page loads (rebuild with npm run build)
  python/             command-line version using the same rules and model
  serve.py            tiny local web server
```

## Run the web app
Browsers block ES modules and model downloads on `file://` pages, so use a local server:
```
python serve.py
```
It opens http://localhost:8000. The first load downloads the model (a few tens of MB) and caches it.
An internet connection is needed for that first download only.

## Edit the TypeScript
```
npm install
npm run build        # compiles src/*.ts to dist/*.js
```
`dist/` is committed so the app runs without Node.js. To try another open model, change `MODEL_ID` and
`MODEL_TASK` at the top of `src/model.ts`, then rebuild.

## Run the Python version
```
cd python
pip install -r requirements.txt
python finshield.py --preset kyc
python finshield.py --text "Your account is blocked, share OTP now"
python finshield.py --preset upi --no-model     # rules only
python test_rules.py                            # rule checks
```

## Deployment (Vercel & Render)
See [DEPLOYMENT.md](../DEPLOYMENT.md) for full step-by-step instructions.
- **Vercel**: Deploy the privacy-first frontend directly (configured via `vercel.json`).
- **Render**: Deploy the Python REST API (`app.py`) as a Web Service or deploy the frontend as a Static Site (configured via `render.yaml`).

## Deploy on GitHub Pages
Push the repo, then Settings > Pages > Deploy from branch `main`, folder `/ (root)`.

## Attribution and pre-existing work
- Model: [Xenova/mobilebert-uncased-mnli](https://huggingface.co/Xenova/mobilebert-uncased-mnli),
  derived from [typeform/mobilebert-uncased-mnli](https://huggingface.co/typeform/mobilebert-uncased-mnli).
  Check the model card for its license before submitting.
- Library: [Transformers.js](https://github.com/huggingface/transformers.js) and
  [Hugging Face Transformers](https://github.com/huggingface/transformers), both Apache-2.0.
- Rule checks, interface and code written for this project with help from an AI coding assistant (Claude by Anthropic).
- License: MIT (see LICENSE).
