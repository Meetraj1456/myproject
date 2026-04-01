# Deployment Guide - Render

This guide will help you deploy your Django application to Render.

## Prerequisites

- A Render account (sign up at https://render.com)
- Your GitHub repository with this code
- Environment variables configured

## ⚠️ IMPORTANT: Media Files on Render

**SQLite database and local media files won't persist on Render** because it has an ephemeral filesystem. 

**Solution Options:**

### Option 1: Use Render's PostgreSQL (Recommended)
- Database data persists automatically
- Much better for production

### Option 2: Use AWS S3 or Cloudinary for Media
- Store images in the cloud instead of locally
- Free tier available for both services

## Quick Setup (SQLite - for testing only)

If you just want to test the deployment:
1. Skip the database setup
2. Media will still be lost on restart
3. Suitable only for development/testing

## Full Production Setup (Recommended)

### Step 1: Set Up PostgreSQL on Render

1. Go to https://dashboard.render.com
2. Create a new PostgreSQL database
3. Copy the database URL
4. Add two new packages to requirements.txt:
   ```
   psycopg2-binary==2.9.9
   dj-database-url==2.1.0
   ```

### Step 2: Update settings.py for Database

Add this to the end of your `settings.py`:

```python
import dj_database_url

# Use PostgreSQL in production
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(conn_max_age=600)
else:
    # Development: use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

### Step 3: Set Up Cloud Storage for Media Files

Choose one:

#### Option A: AWS S3
1. Install packages:
   ```
   boto3==1.28.85
   django-storages==1.14.2
   ```
2. Add to settings.py end:
   ```python
   if not DEBUG:
       AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
       AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
       AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
       DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
       MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'
   ```

#### Option B: Cloudinary (Easier - Recommended)
1. Create free account at https://cloudinary.com
2. Install package:
   ```
   cloudinary==1.35.0
   ```
3. Add to requirements.txt
4. Set environment variable: `CLOUDINARY_URL=cloudinary://key:secret@cloud_name`

## Deployment Steps

### 1. Prepare Your Repository

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create a Web Service on Render

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Choose your repository and branch

### 3. Configure Service

**Basic Settings:**
- **Name:** myproject
- **Environment:** Python 3
- **Build Command:** `bash build.sh`
- **Start Command:** `gunicorn myproject.wsgi`
- **Plan:** Free tier (or Starter+)

### 4. Set Environment Variables

**Minimum (for testing):**
```
SECRET_KEY=generate-a-random-string-here
DEBUG=False
CSRF_TRUSTED_ORIGINS=https://yourapp.onrender.com,https://www.yourapp.onrender.com
```

**With PostgreSQL:**
```
DATABASE_URL=<from your Render PostgreSQL service>
SECRET_KEY=generate-a-random-string-here
DEBUG=False
CSRF_TRUSTED_ORIGINS=https://yourapp.onrender.com,https://www.yourapp.onrender.com
```

**With AWS S3:**
```
DATABASE_URL=<from PostgreSQL>
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
SECRET_KEY=generate-a-random-string-here
DEBUG=False
CSRF_TRUSTED_ORIGINS=https://yourapp.onrender.com
```

### 5. Deploy

Click "Create Web Service" and Render will automatically:
- Install dependencies
- Run build.sh (collectstatic + migrate)
- Start your application

### 6. Run Migrations

After first deployment, run migrations via Render Shell:

1. Go to service dashboard
2. Click "Shell" tab  
3. Run:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Static files not loading** | Ensure `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')` and `whitenoise` is installed |
| **Images not loading** | Use Option 2/3 (S3/Cloudinary) for production. Local media files don't persist on Render |
| **Database errors** | Check `DATABASE_URL` is set and PostgreSQL is created |
| **Import errors** | Run `pip freeze > requirements.txt` to ensure all packages are listed |
| **Port issues** | Render automatically handles port 3000 - no need to configure |

## Recommended Production Stack

```
✅ Framework: Django 6.0.3
✅ Database: PostgreSQL (Render)
✅ Media Storage: S3 or Cloudinary
✅ Static Files: WhiteNoise (included)
✅ Web Server: Gunicorn (included)
```

## Files You've Set Up

- ✅ `requirements.txt` - All dependencies
- ✅ `runtime.txt` - Python 3.11.0
- ✅ `Procfile` - Gunicorn start command
- ✅ `build.sh` - Build script (migrations + static)
- ✅ `settings.py` - Production-ready config
- ✅ `urls.py` - Media file serving
- ✅ `.env.example` - Environment template
- ✅ `render.yaml` - Auto-deployment config

## Need Help?

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/6.0/howto/deployment/
- Cloudinary Guide: https://cloudinary.com/documentation/django_integration

