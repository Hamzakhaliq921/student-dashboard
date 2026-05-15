# 🚀 Deploy to Render (Free, Always Online)

## What you need
- GitHub account (free) → github.com
- Render account (free) → render.com

---

## Step 1 — Push to GitHub

### First time only:
```bash
# Install git if you don't have it
# Download from: https://git-scm.com

# Inside your project folder
git init
git add .
git commit -m "first commit"

# Create a repo on github.com → click New Repository → name it "student-dashboard"
# Then run:
git remote add origin https://github.com/YOUR_USERNAME/student-dashboard.git
git push -u origin main
```

---

## Step 2 — Deploy on Render

1. Go to **render.com** → Sign up free
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub account
4. Select your **student-dashboard** repo
5. Render auto-detects the Dockerfile ✅
6. Settings:
   - **Name:** student-dashboard
   - **Plan:** Free
   - **Branch:** main
7. Click **"Create Web Service"**

Wait ~3 minutes for it to build and deploy.

You get a URL like: `https://student-dashboard.onrender.com` 🎉

---

## Step 3 — Add Persistent Disk (so DB doesn't reset)

1. In Render dashboard → your service → **Disks**
2. Click **"Add Disk"**
3. Settings:
   - **Name:** db-storage
   - **Mount Path:** /app/data
   - **Size:** 1 GB (free)
4. Click Save → service restarts automatically

---

## Step 4 — Done!

Open your URL on any device, anywhere, anytime:
```
https://student-dashboard.onrender.com
```

Login: admin / admin

---

## ⚠️ Important Notes

- **Free Render spins down after 15 min of inactivity** — first load takes ~30 seconds to wake up
- **Selenium scrapers work** because Dockerfile installs Chrome
- **DB is persistent** — data stays even after restarts (because of the disk)

---

## Updating your app later

```bash
# Make your changes, then:
git add .
git commit -m "updated something"
git push
```
Render auto-redeploys on every push. ✅
