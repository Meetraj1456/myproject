# ✅ Render Deployment Checklist

## Before Deployment

- [ ] Requirements are updated: `pip freeze > requirements.txt`
- [ ] `.env.example` file exists with all needed variables
- [ ] `.gitignore` includes `staticfiles/`, `db.sqlite3`, `.env`
- [ ] `build.sh` exists and has correct commands
- [ ] `Procfile` points to `gunicorn myproject.wsgi`
- [ ] `runtime.txt` specifies Python version

## Code Changes Made ✅

- [x] **settings.py**
  - [x] WhiteNoise middleware enabled
  - [x] `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
  - [x] Environment variables support (SECRET_KEY, DEBUG)
  - [x] CSRF settings configured
  - [x] Media files served from urls.py

- [x] **urls.py**
  - [x] Media files always served (even when DEBUG=False)
  - [x] Static files served in DEBUG mode

- [x] **build.sh**
  - [x] Runs `collectstatic --noinput`
  - [x] Runs `migrate`

## Deployment Steps

1. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Fix static files and prepare for Render"
   git push origin main
   ```

2. **On Render Dashboard:**
   - Create Web Service or redeply existing service
   - Build Command: `bash build.sh`
   - Start Command: `gunicorn myproject.wsgi`

3. **Environment Variables on Render:**
   ```
   SECRET_KEY=<generate-random-string>
   DEBUG=False
   CSRF_TRUSTED_ORIGINS=https://yourapp.onrender.com,https://www.yourapp.onrender.com
   ```

4. **After Deployment:**
   - Check logs for errors
   - Visit your app URL
   - Test CSS/JS loading: `https://yourapp.onrender.com/static/css/style.css`
   - Go to admin: `https://yourapp.onrender.com/admin/`

## Static Files Debugging

If static files still don't load on Render:

1. **Check logs:**
   - Go to Render dashboard → Logs tab
   - Search for "static" or "ERROR"

2. **Test your URLs structure:**
   - Your app should have images at: `myapp/static/images/`
   - Your CSS should be at: `myapp/static/css/`

3. **Check file paths in templates:**
   - Use: `<img src="{{ i.img.url }}">`  (for media files)
   - Use: `<link href="{% static 'css/style.css' %}">`  (for static files)

4. **Collect static files locally:**
   ```bash
   python manage.py collectstatic --noinput --clear -v 2
   ```
   This shows what files are being collected.

## Production Database Note

For persistent data on Render:
- Free tier: Data persists but use PostgreSQL, not SQLite
- Add: `DATABASE_URL` environment variable
- Update `requirements.txt`: Add `psycopg2-binary==2.9.9` and `dj-database-url==2.1.0`

## Files Status

✅ **Ready for deployment:**
- [x] requirements.txt - Complete with all packages
- [x] runtime.txt - Python 3.11.0
- [x] Procfile - Configured for gunicorn
- [x] build.sh - Runs collectstatic + migrate
- [x] settings.py - Production settings with WhiteNoise
- [x] urls.py - Media file serving configured
- [x] .env.example - Template provided
- [x] DEPLOYMENT.md - Full guide
- [x] STATIC_FILES_GUIDE.md - Static file troubleshooting
