# FinShield Deployment Guide: Vercel & Render

This guide provides exact step-by-step instructions to create a new repository on GitHub and deploy **FinShield** to **Vercel** (Frontend) and **Render** (Backend API).

---

## 🏗️ Project Architecture

```
├── index.html            # Web Frontend (Served on Vercel)
├── style.css             # UI Styling
├── dist/                 # Pre-compiled JS (Transformers.js ONNX scam model)
├── src/                  # TypeScript source
├── backend/              # Python Backend (Deployed on Render)
│   ├── app.py            # FastAPI REST API (/analyze, /presets, /health)
│   ├── requirements.txt  # FastAPI & Uvicorn dependencies
│   ├── finshield.py      # Banking rules & zero-shot detection
│   └── test_rules.py     # Verification tests
├── render.yaml           # 1-Click Render Blueprint
├── vercel.json           # Vercel static site settings
└── .vercelignore         # Tells Vercel to ignore backend/ and focus on frontend
```

---

## Step 1: Create New GitHub Repository & Push

1. Open your browser and go to **[github.com/new](https://github.com/new)**.
2. Name your repository (for example: `SCAM-FINDER-ASA` or `finshield`).
3. Leave **"Add a README"**, **".gitignore"**, and **"license"** **UNCHECKED** (we already have them).
4. Click **"Create repository"**.
5. Copy your new repository URL (e.g. `https://github.com/YOUR_USERNAME/SCAM-FINDER-ASA.git`).
6. Run the following commands in your project terminal:

```bash
# 1. Stage and commit all files
git add .
git commit -m "Initial commit: FinShield frontend & FastAPI backend"

# 2. Set main branch
git branch -M main

# 3. Link to your new repository (replace YOUR_USERNAME and REPO_NAME)
git remote set-url origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 4. Push code to GitHub
git push -u origin main
```

*(If you ever need to reset the remote completely: `git remote remove origin` then `git remote add origin <URL>`)*

---

## Step 2: Deploy Frontend on Vercel

FinShield's web app runs client-side AI directly in the browser via Transformers.js (WebAssembly / ONNX). Deploying on Vercel is instantaneous with zero configuration:

1. Go to **[vercel.com](https://vercel.com)** and log in.
2. Click **"Add New..."** > **"Project"**.
3. Select your new GitHub repository and click **"Import"**.
4. In the configuration settings:
   - **Framework Preset**: `Other` (or default)
   - **Root Directory**: `./` (default)
   - **Build Command**: *(leave blank)*
   - **Output Directory**: *(leave blank)*
5. Click **"Deploy"**.

Your web frontend will be live in ~20 seconds with HTTPS and a fast global CDN!

---

## Step 3: Deploy Backend on Render

The backend provides a REST API with interactive Swagger documentation (`/docs`) for programmatic scam detection.

### Option A: 1-Click Render Blueprint (Recommended)
1. Go to **[dashboard.render.com](https://dashboard.render.com)**.
2. Click **"New +"** in the top bar > **"Blueprint"**.
3. Connect your new GitHub repository.
4. Render will detect `render.yaml` and configure:
   - `finshield-api`: Python Web Service pointing to `backend/`.
5. Click **"Apply"**.

### Option B: Manual Setup on Render
1. In the Render Dashboard, click **"New +"** > **"Web Service"**.
2. Select your repository.
3. Configure the following fields:
   - **Name**: `finshield-api`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
4. Click **"Create Web Service"**.

Once deployed, access your live API:
- **Interactive API Docs**: `https://your-api.onrender.com/docs`
- **Health Check**: `https://your-api.onrender.com/health`
- **Analyze Endpoint**: `POST https://your-api.onrender.com/analyze`
