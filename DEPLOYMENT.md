# FinShield Deployment Guide: Vercel & Render

This guide provides exact step-by-step instructions to deploy **FinShield (SCAM-FINDER-ASA)** to **Vercel** and **Render**.

---

## 🏗️ Architecture Overview

| Component | Platform | Service Type | What it runs |
| :--- | :--- | :--- | :--- |
| **Web Frontend** | **Vercel** | Static Site | Privacy-first browser app with client-side AI (Transformers.js ONNX) |
| **Backend API** | **Render** | Python Web Service | FastAPI REST API (`/analyze`, `/presets`, `/docs`) |

---

## Part 1: Deploy Frontend on Vercel

FinShield runs 100% in the user's browser, making Vercel the ideal hosting platform (fast global CDN, HTTPS, automatic preview branches).

### Deploy via Vercel Dashboard

1. Push the project to GitHub if it is not already there:
   ```bash
   git add .
   git commit -m "Prepare Vercel and Render deployment"
   git push origin main
   ```

2. Go to **[vercel.com](https://vercel.com)** and log in with your GitHub account.

3. Click **"Add New..."** > **"Project"**.

4. Find your repository **`SCAM-FINDER-ASA`** and click **"Import"**.

5. **Configure Project Settings**:
   - **Framework Preset**: Select `Other` (or leave default).
   - **Root Directory**: Leave as `./`. The root `vercel.json` serves the `finshield` folder. Alternatively, select `finshield` as the root directory and use its local Vercel config.
   - **Build & Output Settings**:
     - Build Command: Leave blank (static files in `dist/` are pre-compiled).
     - Output Directory: Leave blank (controlled by `vercel.json`).

6. Click **"Deploy"**.

7. In about 30 seconds, your site will be live at `https://scam-finder-asa.vercel.app` (or your chosen project name)!

> [!NOTE]
> **Why `.vercelignore` is included**:
> Because the project contains a Python backend for Render (`app.py` & `requirements.txt`), `.vercelignore` tells Vercel to bypass Python serverless function compilation and deploy FinShield purely as a fast, client-side static web application.

---

## Part 2: Deploy the Backend on Render

The Render Blueprint in this repository deploys the Python REST API only. The frontend is hosted on Vercel.

1. Go to **[dashboard.render.com](https://dashboard.render.com)** and log in.
2. Click **"New +"** in the top navigation bar and select **"Blueprint"**.
3. Connect your GitHub repository **`SCAM-FINDER-ASA`**.
4. Render reads `render.yaml` and configures `finshield-api` as a Python Web Service.
5. Click **"Apply"** to deploy.

To configure the API manually instead:
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

---

## 🛠️ Verification Checklist

- [x] **Vercel Config**: `vercel.json` created at project root and inside `finshield/`.
- [x] **Render Blueprint**: `render.yaml` configures the backend Web Service only.
- [x] **Python REST API**: `app.py` created with FastAPI, CORS enabled, Swagger `/docs`, and fallback error handling.
- [x] **Lightweight Dependencies**: `requirements.txt` configured to ensure clean, crash-free builds on Render's 512MB free tier.
- [x] **Local Server Script**: `finshield/serve.py` updated to run seamlessly regardless of working directory.
