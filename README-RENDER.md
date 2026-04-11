# Django POS System - Render Deployment Guide

## 🚀 Deploy to Render

### Prerequisites
- GitHub repository with your code
- Render account (free tier available)
- PostgreSQL database (Render provides free tier)

### Step 1: Update Requirements
Replace your current `requirements.txt` with `requirements-render.txt`:
```bash
cp requirements-render.txt requirements.txt
```

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 3: Deploy on Render
1. Go to [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: pos-system
   - **Region**: Choose nearest
   - **Branch**: main
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn pos_system.wsgi:application --bind 0.0.0.0:$PORT`

### Step 4: Add PostgreSQL Database
1. In Render dashboard, click "New" → "PostgreSQL"
2. **Name**: pos-db
3. **Plan**: Free
4. Once created, go to your web service settings
5. Add environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: Copy from database connection string

### Step 5: Environment Variables
Add these environment variables in your web service:
- `SECRET_KEY`: Generate a random string
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `.onrender.com`
- `DATABASE_URL`: From your PostgreSQL database

### Step 6: Deploy
Click "Create Web Service" and Render will deploy your app!

## 📋 Files Created for Render

### Core Files
- `Procfile` - Tells Render how to run your app
- `runtime.txt` - Specifies Python version
- `render.yaml` - Render configuration file
- `pos_system/settings_production.py` - Production settings
- `requirements-render.txt` - Clean production dependencies

### Scripts
- `scripts/build.sh` - Build script
- `scripts/start.sh` - Start script with migrations

### Configuration Files
- `env-example.txt` - Environment variables template
- `README-RENDER.md` - This deployment guide

## 🔧 Important Changes Made

### Settings
- Updated WSGI to use production settings
- Added PostgreSQL database configuration
- Enhanced security settings
- Configured static and media files
- Added email backend configuration

### Security
- SSL redirect enabled
- Secure cookies
- HSTS security headers
- Environment-based secret key

### Database
- PostgreSQL ready
- Automatic migrations on deploy
- Database connection pooling

## 🌐 Post-Deployment Setup

1. **Create Admin User**:
   - Access your deployed app
   - Go to `/admin/`
   - Create admin account

2. **Configure Email**:
   - Set up Gmail app password
   - Add email environment variables

3. **Test Features**:
   - User registration
   - POS functionality
   - Reports generation

## 🐛 Troubleshooting

### Common Issues
1. **Database Connection Error**
   - Check `DATABASE_URL` environment variable
   - Ensure PostgreSQL is running

2. **Static Files Not Loading**
   - Run `collectstatic` command
   - Check `STATIC_ROOT` setting

3. **Permission Denied**
   - Check file permissions
   - Ensure proper user roles

### Debug Mode
For debugging, temporarily set:
- `DEBUG = True` in production settings
- Check Render logs for errors

## 📞 Support

If you encounter issues:
1. Check Render logs
2. Verify environment variables
3. Ensure all dependencies are installed
4. Test locally with production settings

---

**Your POS System is now ready for production deployment on Render!** 🎉
