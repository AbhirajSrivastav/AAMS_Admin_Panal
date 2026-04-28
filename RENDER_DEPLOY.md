# Deploying to Render

This guide walks you through deploying the AI Attendance Management System on [Render](https://render.com) using the **Blueprint** (Infrastructure-as-Code) workflow.

---

## Prerequisites

1. A [Render](https://dashboard.render.com) account (free tier works).
2. This project pushed to a **GitHub** or **GitLab** repository.
3. You are aware of the **cloud limitations** listed below.

---

## ⚠️ Important Cloud Limitations

| Feature | Local Dev | Render (Cloud) |
|---------|-----------|----------------|
| **Webcam / Camera** | Works via `cv2.VideoCapture(0)` | ❌ No physical camera. The `/video_feed` endpoint will not work. |
| **Face Recognition Build** | `dlib` compiles locally | ⚠️ May time out on the free plan (see workaround below). |
| **Uploaded Images** | Persist on disk | ❌ Filesystem is ephemeral. Only images committed to Git survive deploys. |

> **Recommendation:** Use Render to host the dashboard, API, and database. For live face capture, consider a companion desktop app or browser-based webcam upload.

---

## Step 1: Push to GitHub

Ensure the following files are committed to your repo:

```bash
git add requirements.txt wsgi.py render.yaml RENDER_DEPLOY.md
git commit -m "chore: add Render deployment files"
git push origin main
```

---

## Step 2: Create a Blueprint on Render

1. Go to the [Render Dashboard](https://dashboard.render.com).
2. Click **New** → **Blueprint**.
3. Connect your GitHub/GitLab account and select this repository.
4. Render will read `render.yaml` and show you the resources it will create:
   - **Web Service:** `attendance-management-system`
   - **PostgreSQL Database:** `attendance-db`
5. Click **Apply**.

Render will now:
- Provision a free PostgreSQL database.
- Build the Python environment (`pip install -r requirements.txt`).
- Start the app with **Gunicorn** using `wsgi.py`.
- Automatically inject database credentials as environment variables.

---

## Step 3: Monitor the First Deploy

Open the deploy logs for the web service and watch for:

- **Build stage:** `pip install` running. `face-recognition` / `dlib` compilation may take 5–15 minutes.
- **Startup stage:** You should see:
  ```
  [INFO] Using PostgreSQL database.
  [INFO] face_recognition loaded: X student(s)
  ```

If the build fails with a **timeout** during `dlib` compilation, you have two options:

### Option A: Upgrade to Render's Starter plan
Starter plans have longer build timeouts and more RAM, which usually allows `dlib` to compile successfully.

### Option B: Use a Docker deployment (advanced)
Create a `Dockerfile` that uses a pre-built base image with `dlib` already installed, or install system dependencies (`cmake`, `libopenblas-dev`, `liblapack-dev`) before `pip install`. If you need this, open an issue and we can provide the `Dockerfile`.

---

## Step 4: Verify the Deployment

Once the service shows **"Live"**, visit the provided `.onrender.com` URL.

| Route | Expected Result |
|-------|-----------------|
| `/` | Dashboard loads with charts & stats |
| `/student-directory` | Student list page |
| `/api/stats` | JSON API response |
| `/video_feed` | **Will fail** (no camera) — this is expected |

---

## Environment Variables

The following variables are automatically managed by Render:

| Variable | Source | Purpose |
|----------|--------|---------|
| `DB_HOST` | Postgres service | Database host |
| `DB_PORT` | Postgres service | Database port |
| `DB_NAME` | Postgres service | Database name |
| `DB_USER` | Postgres service | Database user |
| `DB_PASSWORD` | Postgres service | Database password |
| `SECRET_KEY` | Auto-generated | Flask session security |
| `FLASK_ENV` | `render.yaml` | Switches app to `ProductionConfig` |
| `PORT` | Render runtime | Gunicorn binds to this port |

You can view or override them in the dashboard:
**Dashboard → Select Web Service → Environment**.

---

## Troubleshooting

### "Module not found" errors
Make sure `wsgi.py` and `requirements.txt` are at the **repository root** (same level as `run.py`).

### Database connection errors
Check the Environment tab to confirm all `DB_*` variables are populated. If you created the database manually instead of via Blueprint, ensure you copy the **Internal Database URL** values into the matching environment variables.

### Camera / video feed not working
This is expected on Render. The cloud server has no webcam. To disable the camera thread and avoid errors, you can temporarily comment out the camera initialization in `app/__init__.py` or add an env-var gate:
```python
if os.getenv('DISABLE_CAMERA'):
    # skip camera init
```

### Static files not loading
Ensure `app/static/` is committed to Git. Render’s Python environment serves static files via Flask automatically.

---

## Local Development (still works!)

Nothing changes for local development:

```bash
python run.py
```

`run.py` continues to use the Flask development server and `DevelopmentConfig`, while Render uses `wsgi.py` + Gunicorn + `ProductionConfig`.

---

## Next Steps / SaaS Roadmap on Render

- **Custom Domain:** Add your own domain in the Render dashboard (free TLS included).
- **Persistent Image Storage:** Migrate `app/image_data/` to an S3-compatible object store (e.g., Render Disks or AWS S3) so user uploads survive redeploys.
- **Background Jobs:** Add Celery + Redis for async face-encoding tasks.
- **Monitoring:** Connect Render’s Log Streams or add an APM tool (e.g., Sentry).

Happy deploying! 🚀

