# Deployment Guide

Guide for deploying the BBG Rebate Processing Tool to production.

## Deployment Overview

**Recommended Stack:**
- **Backend:** Render.com (free tier or paid)
- **Frontend:** Vercel (free tier)
- **Database:** PostgreSQL on Render or keep SQLite with persistent disk
- **Documentation:** GitHub Pages (free)

---

## Prerequisites

- GitHub account with repository access
- Render.com account
- Vercel account
- Domain name (optional)

---

## Backend Deployment (Render.com)

### Step 1: Prepare Backend for Production

**1.1 Update requirements.txt**

Add production dependencies:
```bash
cd backend
echo "psycopg2-binary==2.9.9" >> requirements.txt  # If using PostgreSQL
echo "gunicorn==21.2.0" >> requirements.txt
```

**1.2 Create Render configuration**

Create `render.yaml` in project root:
```yaml
services:
  - type: web
    name: bbg-rebate-api
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      - key: DATABASE_URL
        fromDatabase:
          name: bbg-rebates-db
          property: connectionString
```

**1.3 Update CORS settings**

Edit `backend/app/main.py`:
```python
# Add your Vercel URL to allowed origins
allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174",
    "https://your-app.vercel.app",  # Add this
    "https://your-custom-domain.com",  # Add if using custom domain
]
```

### Step 2: Deploy to Render

**2.1 Create New Web Service**
1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** bbg-rebate-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - **Plan:** Free or Starter ($7/mo)

**2.2 Add Environment Variables**
- `DATABASE_URL` - PostgreSQL connection string (if using PostgreSQL)
- `ALLOWED_ORIGINS` - Your frontend URL

**2.3 Optional: Add PostgreSQL Database**
1. Click "New +" → "PostgreSQL"
2. Name: bbg-rebates-db
3. Link to web service
4. Note connection string

**2.4 Optional: Add Persistent Disk (for SQLite)**
If keeping SQLite:
1. Go to web service settings
2. Add "Disk" → Mount path: `/opt/render/project/backend`
3. Size: 1GB ($1/mo)

### Step 3: Seed Production Database

**Option A: Via script**
```bash
# SSH into Render shell (if available on paid plan)
cd backend
python3 seed_real_data.py
python3 seed_rules.py
```

**Option B: Via API**
Use the bulk upload endpoints to upload CSV files via the deployed API.

### Step 4: Verify Backend

Visit: `https://bbg-rebate-api.onrender.com/docs`

You should see the FastAPI documentation.

---

## Frontend Deployment (Vercel)

### Step 1: Prepare Frontend for Production

**1.1 Update API URL**

Edit `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
```

**1.2 Create Environment Variable File**

Create `frontend/.env.production`:
```env
VITE_API_URL=https://bbg-rebate-api.onrender.com
```

**1.3 Test Production Build Locally**
```bash
cd frontend
npm run build
npm run preview
```

### Step 2: Deploy to Vercel

**2.1 Install Vercel CLI** (optional)
```bash
npm install -g vercel
```

**2.2 Deploy via GitHub**
1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

**2.3 Add Environment Variables**
In Vercel project settings:
- `VITE_API_URL` = `https://bbg-rebate-api.onrender.com`

**2.4 Deploy**
Click "Deploy" - takes 1-2 minutes

### Step 3: Verify Frontend

Visit: `https://your-app.vercel.app`

Test file upload and processing.

---

## Documentation Deployment (GitHub Pages)

### Step 1: Build Documentation

```bash
python3 -m mkdocs build
```

This creates a `site/` folder with static HTML.

### Step 2: Deploy to GitHub Pages

```bash
python3 -m mkdocs gh-deploy
```

This automatically:
1. Builds the documentation
2. Pushes to `gh-pages` branch
3. Enables GitHub Pages

### Step 3: Enable GitHub Pages

1. Go to GitHub repository settings
2. Pages section
3. Source: `gh-pages` branch
4. Save

**Documentation URL:** `https://[username].github.io/bbg/`

---

## Custom Domain (Optional)

### Backend Custom Domain (Render)

1. Go to Render dashboard → Your service → Settings
2. Add custom domain (e.g., `api.your-domain.com`)
3. Add DNS records:
   ```
   Type: CNAME
   Name: api
   Value: bbg-rebate-api.onrender.com
   ```

### Frontend Custom Domain (Vercel)

1. Go to Vercel project → Settings → Domains
2. Add domain (e.g., `rebates.your-domain.com`)
3. Add DNS records as instructed by Vercel

---

## Environment Variables Reference

### Backend

| Variable | Development | Production |
|----------|-------------|------------|
| `API_HOST` | `0.0.0.0` | `0.0.0.0` |
| `API_PORT` | `8001` | Set by Render |
| `DATABASE_URL` | `sqlite:///./bbg_rebates.db` | PostgreSQL connection string |
| `ALLOWED_ORIGINS` | `http://localhost:5174` | Your Vercel URL |
| `DEBUG` | `True` | `False` |

### Frontend

| Variable | Development | Production |
|----------|-------------|------------|
| `VITE_API_URL` | `http://localhost:8001` | `https://your-api.onrender.com` |

---

## Security Checklist

Before production:

- [ ] Add authentication (OAuth, JWT, or basic auth)
- [ ] Enable HTTPS only (done automatically by Render/Vercel)
- [ ] Restrict CORS to specific domains (not wildcard)
- [ ] Add rate limiting to API endpoints
- [ ] Sanitize file uploads (scan for malware)
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy for database
- [ ] Add error tracking (Sentry, etc.)
- [ ] Review and limit API access
- [ ] Set strong database passwords
- [ ] Rotate secrets regularly
- [ ] Add logging for audit trail

---

## Monitoring and Maintenance

### Health Checks

Set up monitoring for:
- `GET /health` endpoint
- Database connectivity
- File processing performance
- Error rates

**Tools:**
- Render built-in metrics
- Vercel Analytics
- UptimeRobot (free uptime monitoring)
- Sentry (error tracking)

### Backups

**Database:**
- Render PostgreSQL: Automatic daily backups
- Manual backup: Export via API or database tools

**Code:**
- Git repository (GitHub)
- Tag releases: `git tag v1.0.0`

### Updates

**Dependencies:**
```bash
# Backend
cd backend
pip list --outdated
pip install --upgrade [package]

# Frontend
cd frontend
npm outdated
npm update
```

**Deploy Updates:**
- Push to GitHub
- Render and Vercel auto-deploy from main branch

---

## Rollback Procedure

### Render (Backend)

1. Go to Render dashboard → Your service → Events
2. Find previous successful deployment
3. Click "Redeploy" on that event

### Vercel (Frontend)

1. Go to Vercel project → Deployments
2. Find previous deployment
3. Click "..." → "Promote to Production"

### Database Rollback

1. Stop backend service
2. Restore database from backup
3. Restart backend service

---

## Cost Estimation

### Free Tier (Development/Testing)

| Service | Plan | Cost |
|---------|------|------|
| Render (Backend) | Free | $0 |
| Vercel (Frontend) | Hobby | $0 |
| GitHub Pages (Docs) | Free | $0 |
| **Total** | | **$0/month** |

**Limitations:**
- Backend sleeps after 15 min inactivity (30s cold start)
- 750 hours/month render time
- Limited bandwidth

### Production Tier (Recommended)

| Service | Plan | Cost |
|---------|------|------|
| Render (Backend) | Starter | $7/mo |
| Render PostgreSQL | Starter | $7/mo |
| Render Disk (if SQLite) | 1GB | $1/mo |
| Vercel (Frontend) | Pro (optional) | $20/mo |
| **Total** | | **$14-35/month** |

**Benefits:**
- No sleep/cold starts
- Better performance
- More resources
- Support

---

## Troubleshooting Deployment

### Backend Issues

**Build Fails:**
- Check `requirements.txt` is correct
- Verify Python version matches (3.12)
- Check build logs in Render

**Database Connection Fails:**
- Verify DATABASE_URL environment variable
- Check PostgreSQL is running
- Test connection string

**CORS Errors:**
- Add frontend URL to ALLOWED_ORIGINS
- Restart backend service

### Frontend Issues

**Build Fails:**
- Check `package.json` dependencies
- Verify Node version (20+)
- Check build logs in Vercel

**API Calls Fail:**
- Verify VITE_API_URL is correct
- Check backend is running
- Test API endpoint directly

**Environment Variables Not Working:**
- Redeploy after adding env vars
- Check variable names (must start with VITE_)

---

## Next Steps After Deployment

1. **Test thoroughly:**
   - Upload test files
   - Test all features
   - Check on different devices

2. **Set up monitoring:**
   - Health check endpoints
   - Error tracking
   - Usage analytics

3. **Train users:**
   - Share documentation URL
   - Conduct training session
   - Gather feedback

4. **Plan for scale:**
   - Monitor usage patterns
   - Optimize performance bottlenecks
   - Consider upgrading plans if needed

---

## Support

For deployment issues:
- **Render:** https://render.com/docs
- **Vercel:** https://vercel.com/docs
- **GitHub Pages:** https://docs.github.com/pages

---

**Production deployment complete!** Monitor your application and gather user feedback for improvements.
