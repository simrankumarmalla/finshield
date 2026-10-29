"""FinShield FastAPI Backend Service.

Ready for deployment on Render (Web Service), Railway, Fly.io, or any Docker/Python host.
Provides REST API endpoints for bank SMS, email, and UPI scam detection.
"""

import os
import sys
from typing import List, Optional

# Ensure current directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from finshield import analyze, run_rules, verdict, PRESETS, MODEL_ID
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# Check if model should be enabled by default (default False on free tier to save RAM)
DEFAULT_USE_MODEL = os.getenv("ENABLE_MODEL", "false").lower() in ("true", "1", "yes")

app = FastAPI(
    title="FinShield Scam Detector API",
    description="Privacy-first AI & rule-based banking scam detection API.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for all origins so Vercel frontend or any client can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Message text (SMS, email, UPI prompt) to analyze")
    use_model: Optional[bool] = Field(
        default=DEFAULT_USE_MODEL,
        description="Whether to run the neural model (requires ~500MB RAM) or rules only."
    )


class AnalyzeResponse(BaseModel):
    verdict: str
    score: int
    ai_line: str
    reasons: List[str]
    flags: List[str]
    good: List[str]


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>FinShield API</title>
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #1e293b; }
        h1 { color: #0f172a; margin-bottom: 8px; }
        .badge { display: inline-block; background: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 14px; margin-bottom: 20px; }
        pre { background: #f1f5f9; padding: 16px; border-radius: 8px; overflow-x: auto; }
        a { color: #2563eb; text-decoration: none; font-weight: 500; }
        a:hover { text-decoration: underline; }
        .links { margin: 24px 0; display: flex; gap: 16px; }
      </style>
    </head>
    <body>
      <h1>FinShield Scam Detector API</h1>
      <span class="badge">API Active</span>
      <p>This service provides automated banking SMS and UPI scam detection combining heuristic rules and open-source models.</p>
      <div class="links">
        <a href="/docs">Interactive Swagger Docs</a> &bull;
        <a href="/health">Health Status</a> &bull;
        <a href="/presets">Sample Presets</a>
      </div>
      <h3>Quick Example</h3>
      <pre>POST /analyze
Content-Type: application/json

{
  "text": "Your account will be blocked in 24h. Click bit.ly/kyc and share OTP.",
  "use_model": false
}</pre>
    </body>
    </html>
    """


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "finshield-api",
        "default_model_enabled": DEFAULT_USE_MODEL,
        "model_id": MODEL_ID,
    }


@app.get("/presets")
def get_presets():
    return PRESETS


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_post(req: AnalyzeRequest):
    rule_score, flags, good = run_rules(req.text)
    score, reasons, ai_line = analyze(req.text, use_model=req.use_model)
    v = verdict(score)
    return AnalyzeResponse(
        verdict=v,
        score=score,
        ai_line=ai_line,
        reasons=reasons,
        flags=flags,
        good=good,
    )


@app.get("/analyze", response_model=AnalyzeResponse)
def analyze_get(
    text: str = Query(..., min_length=1, description="Message text to analyze"),
    use_model: bool = Query(DEFAULT_USE_MODEL, description="Run ML model layer"),
):
    rule_score, flags, good = run_rules(text)
    score, reasons, ai_line = analyze(text, use_model=use_model)
    v = verdict(score)
    return AnalyzeResponse(
        verdict=v,
        score=score,
        ai_line=ai_line,
        reasons=reasons,
        flags=flags,
        good=good,
    )
