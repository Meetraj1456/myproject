# Deployment Guide - Render

This guide will help you deploy your Django application to Render.

## Prerequisites

- A Render account (sign up at https://render.com)
- Your GitHub repository with this code
- Environment variables configured

## Deployment Steps

### 1. Prepare Your Repository

Ensure you have pushed your code to GitHub:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create a New Web Service on Render

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Choose your repository and branch

### 3. Configure Your Service

**Basic Settings:**
- **Name:** myproject (or your preferred name)
- **Environment:** Python 3
- **Build Command:** `bash build.sh`
- **Start Command:** `gunicorn myproject.wsgi`
- **Plan:** Free (or Starter for better performance)

### 4. Set Environment Variables

In the Render dashboard, add the following environment variables:

```
SECRET_KEY=<your-generated-secret-key>
DEBUG=False
CSRF_TRUSTED_ORIGINS=https://yourapp.onrender.com,https://www.yourapp.onrender.com
```

Replace `yourapp` with your actual Render service name.

### 5. Optional: Database Configuration

**For Production Use:**
If you want persistent data, use PostgreSQL instead of SQLite:

```
DATABASE_URL=postgres://user:password@hostname:5432/database
```

In your `settings.py`, add database URL parsing:
```python
import dj_database_url

if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config()
```

Don't forget to install `dj-database-url` in requirements.txt.

### 6. Deploy

Click "Create Web Service" and Render will automatically:
- Install dependencies from `requirements.txt`
- Run your `build.sh` script
- Start your application with gunicorn

### 7. Run Migrations (After First Deployment)

Once deployed, run migrations via the Render Shell:

1. Go to your service dashboard
2. Click "Shell" tab
3. Run: `python manage.py migrate`

## Troubleshooting

**Static Files Not Loading:**
- Ensure `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')`
- Run `python manage.py collectstatic --noinput`

**Debug Mode Issues:**
- Set `DEBUG=False` in production
- Check `ALLOWED_HOSTS` includes your Render URL

**Database Issues:**
- Use PostgreSQL for production (SQLite has limitations on Render)
- Check `DATABASE_URL` is set correctly

**Import Errors:**
- Verify all packages are in `requirements.txt`
- Check Python version in `runtime.txt` matches your venv

## Files You've Set Up

- ✅ `requirements.txt` - All dependencies
- ✅ `runtime.txt` - Python 3.11.0
- ✅ `Procfile` - Gunicorn configuration
- ✅ `build.sh` - Build script for migrations & static files
- ✅ `settings.py` - Production-ready configuration
- ✅ `.env.example` - Environment variables template
- ✅ `render.yaml` - Optional auto-deployment config

## Need Help?

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/6.0/howto/deployment/
