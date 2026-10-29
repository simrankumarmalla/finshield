# FinShield Deployment Guide: Vercel & Render

This guide provides exact step-by-step instructions to deploy **FinShield (SCAM-FINDER-ASA)** to **Vercel** and **Render**.

---

## 🏗️ Architecture Overview

| Component | Platform | Service Type | What it runs |
| :--- | :--- | :--- | :--- |
| **Web Frontend** | **Vercel** *(or Render)* | Static Site | Privacy-first browser app with client-side AI (Transformers.js ONNX) |
| **Backend API** | **Render** | Python Web Service | FastAPI REST API (`/analyze`, `/presets`, `/docs`) |

---

## Part 1: Deploy Frontend on Vercel

FinShield runs 100% in the user's browser, making Vercel the ideal hosting platform (fast global CDN, HTTPS, automatic preview branches).

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Add Vercel and Render deployment configurations"
   git push origin main
   ```

2. Go to **[vercel.com](https://vercel.com)** and log in with your GitHub account.

3. Click **"Add New..."** > **"Project"**.

4. Find your repository **`SCAM-FINDER-ASA`** and click **"Import"**.

5. **Configure Project Settings**:
   - **Framework Preset**: Select `Other` (or leave default).
   - **Root Directory**: Leave as `./` (the included `vercel.json` automatically serves the `finshield` folder) — *or* click "Edit" and choose `finshield`.
   - **Build & Output Settings**:
     - Build Command: Leave blank (static files in `dist/` are pre-compiled).
     - Output Directory: Leave blank (controlled by `vercel.json`).

6. Click **"Deploy"**.

7. In about 30 seconds, your site will be live at `https://scam-finder-asa.vercel.app` (or your chosen project name)!

> [!NOTE]
> **Why `.vercelignore` is included**:
> Because the project contains a Python backend for Render (`app.py` & `requirements.txt`), `.vercelignore` tells Vercel to bypass Python serverless function compilation and deploy FinShield purely as a fast, client-side static web application.

---

## Part 2: Deploy on Render

Render gives you two deployment options:
1. **Python Web Service (FastAPI Backend API)** for programmatic scam detection.
2. **Static Site (Frontend)** if you prefer to host the web app on Render as well.

---

### Option A: 1-Click Render Blueprint (Deploys Both Backend & Frontend)

This repository includes a `render.yaml` blueprint file.

1. Go to **[dashboard.render.com](https://dashboard.render.com)** and log in.
2. Click **"New +"** in the top navigation bar and select **"Blueprint"**.
3. Connect your GitHub repository **`SCAM-FINDER-ASA`**.
4. Render will read `render.yaml` and configure:
   - `finshield-api` (Python Web Service)
   - `finshield-web` (Frontend Static Site)
5. Click **"Apply"** to deploy!

---

### Option B: Deploy Python Backend API Manually (Render Web Service)

Use this if you want to deploy only the backend REST API:

1. In the Render Dashboard, click **"New +"** > **"Web Service"**.
2. Select your repository `SCAM-FINDER-ASA`.
3. Set the following options:
   - **Name**: `finshield-api`
   - **Region**: Choose the closest to you (e.g., Oregon, Frankfurt, Singapore).
   - **Branch**: `main`
   - **Root Directory**: Leave blank (root).
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn app:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: Select **Free**.
4. (Optional) Under **Environment Variables**, you can add:
   - `ENABLE_MODEL` = `false` *(Recommended for Free tier: instant responses within 512MB RAM using 10+ banking scam heuristics)*
5. Click **"Create Web Service"**.

Once deployed, visit your Render URL:
- `https://finshield-api.onrender.com/` (Welcome page)
- `https://finshield-api.onrender.com/docs` (Interactive Swagger API documentation)
- `https://finshield-api.onrender.com/health` (Health check)

#### Example API Request:
```bash
curl -X POST "https://your-api.onrender.com/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "URGENT: SBI account blocked. Visit bit.ly/sbi-kyc and share OTP."}'
```

---

### Option C: Deploy Frontend Manually on Render (Static Site)

1. In the Render Dashboard, click **"New +"** > **"Static Site"**.
2. Select your repository `SCAM-FINDER-ASA`.
3. Set the following fields:
   - **Name**: `finshield-web`
   - **Branch**: `main`
   - **Root Directory**: `finshield`
   - **Build Command**: *(leave empty)*
   - **Publish Directory**: `.`
4. Click **"Create Static Site"**.

---

## 🛠️ Verification Checklist

- [x] **Vercel Config**: `vercel.json` created at project root and inside `finshield/`.
- [x] **Render Blueprint**: `render.yaml` configured with both Web Service and Static Site definitions.
- [x] **Python REST API**: `app.py` created with FastAPI, CORS enabled, Swagger `/docs`, and fallback error handling.
- [x] **Lightweight Dependencies**: `requirements.txt` configured to ensure clean, crash-free builds on Render's 512MB free tier.
- [x] **Local Server Script**: `finshield/serve.py` updated to run seamlessly regardless of working directory.
