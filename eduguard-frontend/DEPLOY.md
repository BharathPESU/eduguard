# Frontend CI/CD (branch `frontend`)

Pushing to the **`frontend`** branch automatically builds the Docker image and deploys it to **Cloud Run** via GitHub Actions and Cloud Build.

## Flow

```text
git push origin frontend
  → GitHub Actions (.github/workflows/deploy-frontend.yml)
  → gcloud builds submit (eduguard-frontend/cloudbuild.yaml)
  → Docker build + push to Artifact Registry
  → gcloud run deploy
```

Only changes under `eduguard-frontend/` (or the workflow file) trigger a deploy.

## One-time GCP setup

### 1. Service account

Create a service account (e.g. `github-actions-deploy`) in project `career-492408` with:

| Role | Why |
|------|-----|
| `roles/cloudbuild.builds.editor` | Submit Cloud Build jobs |
| `roles/run.admin` | Deploy Cloud Run |
| `roles/artifactregistry.writer` | Push images |
| `roles/iam.serviceAccountUser` | Act as the Cloud Run runtime SA |
| `roles/storage.objectAdmin` | Upload source to the Cloud Build staging bucket |
| `roles/serviceusage.serviceUsageConsumer` | Use enabled GCP APIs |

Cloud Build’s default service account also needs permission to deploy to Cloud Run. In **IAM**, grant the Cloud Build service account (`PROJECT_NUMBER@cloudbuild.gserviceaccount.com`):

- `roles/run.admin`
- `roles/iam.serviceAccountUser`

### 2. Artifact Registry

Ensure repository `eduguard` exists in region `us-central1` (Docker format). The workflow pushes to:

`us-central1-docker.pkg.dev/career-492408/eduguard/frontend:<git-sha>`

### 3. Cloud Run service

Create the frontend service once (if it does not exist), or confirm its name matches `eduguard-frontend`:

```bash
gcloud run deploy eduguard-frontend \
  --image=us-central1-docker.pkg.dev/career-492408/eduguard/frontend:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080
```

If your service uses a different name, set GitHub repository variable **`CLOUD_RUN_SERVICE`**.

## Step-by-step: GitHub secrets (start here)

GitHub Actions needs two passwords so it can talk to Google Cloud and bake your API URL into the React app.

| Secret | Plain English |
|--------|----------------|
| `VITE_API_URL` | The **public URL of your FastAPI backend** in production (where tutor/exam/auth APIs live). |
| `GCP_SA_KEY` | A **Google Cloud login file** (JSON) that lets GitHub trigger builds and deploys. |

---

### Part 1 — Set `VITE_API_URL` (your backend URL)

**What it is:** When you run locally, the frontend calls `http://localhost:8000`. In production, the built React app must know the real backend URL. That URL is stored in `VITE_API_URL` at **build time** (it is not read from `.env` on the server later).

**Step 1 — Find your backend URL**

Pick the option that matches you:

**Option A — Backend already on Google Cloud Run**

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Select project **`career-492408`** (top bar).
3. Go to **Cloud Run** (search “Cloud Run” in the top search box).
4. Click your **backend** service (often named like `eduguard-backend`, not the frontend).
5. Copy the URL at the top, e.g. `https://eduguard-backend-xxxxx-uc.a.run.app`
6. **Rules:** use `https://`, **no** trailing `/`, **no** path like `/docs`.

**Option B — Find it with terminal (if `gcloud` is logged in as you)**

```bash
gcloud run services list --project=career-492408 --region=us-central1
```

Copy the **URL** column for your backend service.

**Option C — Backend not deployed yet**

Deploy the FastAPI backend to Cloud Run first, then come back with that URL. Until then, auto-deploy will build the frontend but API calls will fail in production.

**Step 2 — Quick test**

Open in a browser:

`YOUR_URL/health`

You should see JSON like `{"status":"ok"}` or similar from EduGuard.

**Step 3 — Add secret in GitHub**

1. Open your repo: `https://github.com/BharathPESU/eduguard`
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. **Name:** `VITE_API_URL`
5. **Secret:** paste only the URL, e.g. `https://eduguard-backend-xxxxx-uc.a.run.app`
6. Click **Add secret**

---

### Part 2 — Set `GCP_SA_KEY` (Google deploy key)

**What it is:** A JSON file that proves to Google “GitHub Actions is allowed to run Cloud Build and deploy Cloud Run.” You create it once and paste the whole file into GitHub.

**Step 1 — Open IAM service accounts**

1. [Google Cloud Console](https://console.cloud.google.com/) → project **`career-492408`**
2. Menu ☰ → **IAM & Admin** → **Service Accounts**
3. Click **+ Create service account**

**Step 2 — Create the account**

| Field | Value |
|-------|--------|
| Service account name | `github-actions-deploy` |
| Service account ID | (auto-filled, keep it) |
| Description | `Deploy frontend from GitHub Actions` |

Click **Create and continue**.

**Step 3 — Grant roles** (click **Add another role** for each)

| Role | Why |
|------|-----|
| Cloud Build Editor | Start builds |
| Cloud Run Admin | Deploy the frontend service |
| Artifact Registry Writer | Push Docker images |
| Service Account User | Use Cloud Run’s runtime account |

Click **Continue** → **Done** (skip granting users access).

**Step 4 — Create and download the JSON key**

1. Click the new service account **`github-actions-deploy@...`**
2. Tab **Keys** → **Add key** → **Create new key**
3. Type: **JSON** → **Create**
4. A `.json` file downloads — **keep it private** (like a password). Do not commit it to git.

**Step 5 — Allow Cloud Build to deploy** (one-time, easy to miss)

Cloud Build runs the deploy step using Google’s build robot account:

1. **IAM & Admin** → **IAM**
2. Find principal: `PROJECT_NUMBER@cloudbuild.gserviceaccount.com`  
   (replace `PROJECT_NUMBER` — on IAM page you see numbers like `123456789012@cloudbuild...`)
3. Click **Edit** (pencil) → **Add another role**:
   - **Cloud Run Admin**
   - **Service Account User**
4. **Save**

To find `PROJECT_NUMBER`: **IAM & Admin** → **Settings**, or run:

```bash
gcloud projects describe career-492408 --format='value(projectNumber)'
```

**Step 6 — Add secret in GitHub**

1. Open the downloaded `.json` in a text editor (Notepad, VS Code, etc.)
2. Select **all** text — it starts with `{` and ends with `}`
3. GitHub repo → **Settings** → **Secrets and variables** → **Actions**
4. **New repository secret**
5. **Name:** `GCP_SA_KEY`
6. **Secret:** paste the **entire** JSON file (one block)
7. **Add secret**

You will never see this value again in GitHub after saving — that is normal.

---

### Part 3 — Verify

1. Push any small change under `eduguard-frontend/` to branch **`frontend`**
2. On GitHub: **Actions** tab → workflow **Deploy Frontend**
3. Green check = deployed; red X = open the failed step log

**Checklist**

- [ ] `VITE_API_URL` opens `/health` in browser
- [ ] `GCP_SA_KEY` is the full JSON (not just the filename)
- [ ] Cloud Build service account has Run Admin + Service Account User
- [ ] Workflow file exists on `frontend` branch (merge/push the CI/CD commit)

---

## GitHub repository configuration (reference)

In **Settings → Secrets and variables → Actions**:

### Secrets (required)

| Name | Example / notes |
|------|-----------------|
| `GCP_SA_KEY` | Full JSON key for the deploy service account |
| `VITE_API_URL` | `https://your-backend-xxxxx.run.app` (no trailing slash) |

### Secrets (optional)

| Name | Default |
|------|---------|
| `GCP_PROJECT_ID` | `career-492408` |

### Variables (optional)

| Name | Default |
|------|---------|
| `CLOUD_RUN_SERVICE` | `eduguard-frontend` |
| `GCP_REGION` | `us-central1` |

## Manual deploy (without GitHub)

```bash
cd eduguard-frontend
gcloud builds submit . \
  --project=career-492408 \
  --region=us-central1 \
  --config=cloudbuild.yaml \
  --substitutions=_VITE_API_URL=https://YOUR-BACKEND.run.app,_TAG=manual
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Workflow skipped | Push must be on branch `frontend` and touch `eduguard-frontend/**` |
| `Missing GCP_SA_KEY` | Add secrets in GitHub (see above) |
| Cloud Build `PERMISSION_DENIED` on deploy | Grant Cloud Build SA `run.admin` + `iam.serviceAccountUser` |
| `Unable to read file [cloudbuild.yaml]` | Fixed in workflow: use `--config=eduguard-frontend/cloudbuild.yaml` |
| `forbidden from accessing the bucket ..._cloudbuild` | Add `Storage Object Admin` to `github-actions-deploy` SA |
| Wrong API URL in browser | Update `VITE_API_URL` secret and push again (value is baked in at build time) |
| Wrong Cloud Run service | Set `CLOUD_RUN_SERVICE` variable to your actual service name |
