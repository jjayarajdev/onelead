# Streamlit Cloud Deployment Guide

## 🚀 Quick Start

Your Streamlit Cloud app is already set up at: **https://onelead.streamlit.app/**

## 📋 Prerequisites

This guide assumes you've already:
1. ✅ Created a Streamlit Cloud account
2. ✅ Connected your GitHub repository (https://github.com/jjayarajdev/onelead.git)
3. ✅ Deployed the app

## 🔄 Update Deployment

### Step 1: Configure Streamlit Cloud App Settings

1. Go to: https://share.streamlit.io/
2. Select your app: **onelead**
3. Click **Settings** (⚙️ icon)
4. Configure:

**Main file path**: `src/main_enhanced.py`
**Branch**: `29Sept`
**Python version**: 3.11

### Step 2: Upload Database to Streamlit Cloud

Since the database file (`data/onelead.db`) is not in GitHub (too large), you need to set it up:

**Option A: Use GitHub Secrets & Auto-generate on Startup**
1. In Streamlit Cloud app settings → **Secrets**
2. Add the following to rebuild database on startup:

```toml
# Streamlit Secrets (TOML format)

[database]
auto_setup = true
rebuild_on_startup = true
```

3. The app will automatically run database setup scripts on first launch

**Option B: Upload via Streamlit Secrets as Base64 (Small DBs)**
```bash
# On your local machine
base64 data/onelead.db > db_base64.txt
```

Then add to Streamlit Secrets:
```toml
[database]
base64_data = "paste base64 string here"
```

**Option C: Use External Database (Recommended for Production)**
- Use PostgreSQL on platforms like:
  - Supabase (free tier)
  - Railway.app
  - Heroku Postgres
  - AWS RDS

### Step 3: Environment Variables (if needed)

Add to Streamlit Cloud **Secrets**:

```toml
# Add any API keys or sensitive configuration
# Currently, the app doesn't require external secrets

[general]
debug = false
```

## 📦 Files Required for Deployment

Your repository already has these files in the `29Sept` branch:

| File | Purpose | Status |
|------|---------|--------|
| `requirements.txt` | Python dependencies | ✅ Created |
| `.streamlit/config.toml` | Streamlit theme & settings | ✅ Created |
| `packages.txt` | System packages (none needed) | ✅ Created |
| `src/main_enhanced.py` | Main application | ✅ Exists |
| `data/onelead.db` | Database (needs setup) | ⚠️ Not in repo |

## 🗄️ Database Setup on Streamlit Cloud

### Automatic Database Creation

The app will automatically create the database on first run if you follow these steps:

1. **Ensure database scripts are in repo**:
   - ✅ `src/database/create_sqlite_database.py`
   - ✅ `src/database/ls_sku_data_loader.py`
   - ✅ `data/DataExportAug29th.xlsx`
   - ✅ `data/LS_SKU_for_Onelead.xlsx`

2. **Modify `src/main_enhanced.py` to auto-setup** (already done):
   ```python
   import os
   import sys

   # Auto-setup database on Streamlit Cloud
   if not os.path.exists('data/onelead.db'):
       st.info("🔄 Setting up database for first time...")
       # Run database creation
       sys.path.insert(0, 'src/database')
       import create_sqlite_database
       create_sqlite_database.main()
       st.success("✅ Database setup complete!")
   ```

3. **The database will be created automatically** on first app load

## 🔧 Troubleshooting

### Issue: Database Not Found
**Error**: `no such table: fact_install_base`

**Solution**:
1. Check Streamlit Cloud logs
2. Verify Excel files are in `data/` folder in GitHub
3. Check that database setup scripts ran successfully
4. Restart the app from Streamlit Cloud dashboard

### Issue: Module Not Found
**Error**: `ModuleNotFoundError: No module named 'openpyxl'`

**Solution**:
- Verify `requirements.txt` includes all dependencies
- Reboot app from Streamlit Cloud dashboard

### Issue: Excel Files Not Found
**Error**: `FileNotFoundError: data/DataExportAug29th.xlsx`

**Solution**:
- Ensure Excel files are committed to GitHub (check branch `29Sept`)
- Excel files should be < 100MB for GitHub

### Issue: App Slow or Timeout
**Solution**:
- Streamlit Cloud has resource limits
- Consider caching with `@st.cache_data`
- Optimize queries in recommendation engine
- Use smaller data samples for demo

## 📊 Monitoring

### Check App Status
1. Go to: https://share.streamlit.io/
2. View **Logs** tab to see:
   - Database setup progress
   - Any errors during startup
   - Query execution times

### Performance Optimization
```python
# Already implemented in main_enhanced.py
@st.cache_data(ttl=3600)
def load_database_data():
    """Cache database loads for 1 hour"""
    pass

@st.cache_resource
def get_recommendation_engine():
    """Cache engine instance"""
    pass
```

## 🔄 Updating the App

When you push changes to the `29Sept` branch:

1. Streamlit Cloud automatically detects changes
2. App rebuilds within 2-3 minutes
3. New version goes live automatically

**Manual Reboot**:
1. Go to: https://share.streamlit.io/
2. Select your app
3. Click **☰** menu → **Reboot app**

## 🌐 Custom Domain (Optional)

To use a custom domain like `onelead.yourdomain.com`:

1. Go to Streamlit Cloud app settings
2. Click **Advanced settings** → **Custom domain**
3. Add your domain
4. Update DNS records as instructed

## 📝 Current Configuration

**App URL**: https://onelead.streamlit.app/
**Repository**: https://github.com/jjayarajdev/onelead.git
**Branch**: 29Sept
**Main File**: src/main_enhanced.py
**Python**: 3.11

## ✅ Deployment Checklist

- [x] Create `requirements.txt`
- [x] Create `.streamlit/config.toml`
- [x] Create `packages.txt`
- [x] Push all files to GitHub branch `29Sept`
- [ ] Verify Excel files are in repo
- [ ] Configure Streamlit Cloud app settings
- [ ] Test database auto-setup on first load
- [ ] Verify app loads successfully
- [ ] Test all 5 dashboard steps
- [ ] Test recommendations generation
- [ ] Test filters (customer, urgency, confidence)
- [ ] Test download functionality

## 🆘 Support

**Streamlit Cloud Docs**: https://docs.streamlit.io/streamlit-community-cloud
**Repository**: https://github.com/jjayarajdev/onelead
**Issues**: https://github.com/jjayarajdev/onelead/issues

---

**Last Updated**: September 30, 2025
**Version**: 1.0