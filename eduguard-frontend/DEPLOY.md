# EduGuard CI/CD (branch `main`)

Pushing to the **`main`** branch automatically **builds and deploys both backend and frontend** to Cloud Run.

Workflow file: **`.github/workflows/deploy.yml`**

## Flow

```text
git push origin main
  → GitHub Actions "Deploy EduGuard"
  → Job 1: Backend  — docker build (repo root) → Artifact Registry → Cloud Run (eduguard-backend)
  → Job 2: Frontend — docker build (eduguard-frontend/) using live backend URL → Cloud Run (eduguard-frontend)
```

Any file change on `main` triggers **both** deploys (backend always runs first; frontend uses the backend URL from that deploy).

(`eduguard-frontend/cloudbuild.yaml` is only for optional manual frontend deploys from your laptop.)

## One-time GCP setup

### 1. Service account

Create a service account (e.g. `github-actions-deploy`) in project `career-492408` with **only these roles**:

| Role | Why |
|------|-----|
| **Cloud Run Admin** (`roles/run.admin`) | Deploy the frontend service |
| **Artifact Registry Writer** (`roles/artifactregistry.writer`) | Push Docker images |
| **Service Account User** (`roles/iam.serviceAccountUser`) | Run as Cloud Run’s runtime service account |

You do **not** need Cloud Build Editor or Storage access for GitHub Actions (the workflow builds Docker on GitHub, not in Cloud Build).

**Console:** IAM → select `github-actions-deploy@...` → **Edit** → remove extra roles if you added Cloud Build / Storage earlier → keep only the three above.

**Terminal:**

```bash
PROJECT=career-492408
SA="github-actions-deploy@${PROJECT}.iam.gserviceaccount.com"

for ROLE in roles/run.admin roles/artifactregistry.writer roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding "${PROJECT}" \
    --member="serviceAccount:${SA}" \
    --role="${ROLE}" \
    --condition=None
done
```

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
| `GCP_SA_KEY` | **Required.** Google Cloud JSON key so GitHub can push images and deploy Cloud Run. |
| `VITE_API_URL` | **Optional.** Backend URL for the React build; auto-detected from backend deploy if omitted. |

---

### Part 1 — `VITE_API_URL` (optional)

**What it is:** The frontend build needs your backend URL. The workflow **sets this automatically** after deploying the backend. You only need a GitHub secret if you want to override that URL.

**To set manually (optional) — find your backend URL**

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

**What it is:** A JSON file that proves to Google “GitHub Actions is allowed to push images and deploy Cloud Run.” You create it once and paste the whole file into GitHub.

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

**Step 3 — Grant roles** (click **Add another role** for each — only these three)

| Role | Why |
|------|-----|
| Cloud Run Admin | Deploy the frontend service |
| Artifact Registry Writer | Push Docker images |
| Service Account User | Use Cloud Run’s runtime account |

Do **not** add Cloud Build Editor or Storage roles (not needed).

Click **Continue** → **Done** (skip granting users access).

**Step 4 — Create and download the JSON key**

1. Click the new service account **`github-actions-deploy@...`**
2. Tab **Keys** → **Add key** → **Create new key**
3. Type: **JSON** → **Create**
4. A `.json` file downloads — **keep it private** (like a password). Do not commit it to git.

**Step 5 — Add secret in GitHub**

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

1. Push any commit to branch **`main`**
2. On GitHub: **Actions** tab → workflow **Deploy EduGuard**
3. Green check = deployed; red X = open the failed step log

**Checklist**

- [ ] Backend `/health` works on Cloud Run URL (after deploy)
- [ ] `GCP_SA_KEY` is the full JSON (not just the filename)
- [ ] `github-actions-deploy` has only Run Admin + Artifact Registry Writer + SA User
- [ ] Workflow file exists on `main` branch (merge/push the CI/CD commit)

---

## GitHub repository configuration (reference)

In **Settings → Secrets and variables → Actions**:

### Secrets (required)

| Name | Example / notes |
|------|-----------------|
| `GCP_SA_KEY` | Full JSON key for the deploy service account |
| `VITE_API_URL` | Optional. Auto-set from deployed backend URL. Override only if needed. |

### Secrets (optional)

| Name | Default |
|------|---------|
| `GCP_PROJECT_ID` | `career-492408` |

### Variables (optional)

| Name | Default |
|------|---------|
| `FRONTEND_SERVICE` | `eduguard-frontend` |
| `BACKEND_SERVICE` | `eduguard-backend` |
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
| Workflow skipped | Push must be on branch `main` |
| `Missing GCP_SA_KEY` | Add secrets in GitHub (see above) |
| Cloud Build `PERMISSION_DENIED` on deploy | Grant Cloud Build SA `run.admin` + `iam.serviceAccountUser` |
| `Unable to read file [cloudbuild.yaml]` | Fixed in workflow: use `--config=eduguard-frontend/cloudbuild.yaml` |
| `forbidden from accessing the bucket ..._cloudbuild` | Workflow no longer uses Cloud Build; pull latest workflow. Ensure SA has only Run Admin + Artifact Registry Writer + SA User |
| Wrong API URL in browser | Update `VITE_API_URL` secret and push again (value is baked in at build time) |
| Wrong Cloud Run service | Set `CLOUD_RUN_SERVICE` variable to your actual service name |
