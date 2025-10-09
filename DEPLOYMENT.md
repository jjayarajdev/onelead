# OneLead - Streamlit Cloud Deployment Guide

## 🚀 Deployment URL
**https://oneleads.streamlit.app/**

---

## 📋 Pre-Deployment Checklist

### ✅ Files Configured for Deployment

1. **app.py** - Main entry point for Streamlit Cloud
2. **requirements.txt** - Python dependencies with specific versions
3. **.streamlit/config.toml** - Streamlit configuration
4. **.gitignore** - Updated to allow database and Excel files
5. **database/onelead.db** - SQLite database (912KB)
6. **data/*.xlsx** - Excel source files

### ✅ Repository Setup

- **Repository**: https://github.com/jjayarajdev/onelead.git
- **Branch**: 09Oct
- **Main File**: app.py (points to Premium Dashboard)

---

## 🔧 Streamlit Cloud Setup

### Step 1: Access Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with GitHub account
3. Click "New app"

### Step 2: Configure Deployment

**Repository Settings:**
```
GitHub Repository: jjayarajdev/onelead
Branch: 09Oct
Main file path: app.py
```

**Advanced Settings:**
```
Python version: 3.11
```

### Step 3: Deploy

1. Click "Deploy!"
2. Wait for deployment (usually 2-5 minutes)
3. App will be available at: https://oneleads.streamlit.app/

---

## 📦 What Gets Deployed

### Application Code
- `app.py` - Entry point
- `src/app/dashboard_premium.py` - Premium Dashboard (39KB)
- `src/models/*.py` - Database models
- `src/engines/*.py` - Lead generation engines
- `src/etl/*.py` - Data loading pipeline
- `src/utils/*.py` - Utility functions

### Data Files
- `database/onelead.db` - SQLite database (912KB, 77 leads)
- `data/DataExportAug29th.xlsx` - Install base data (628KB)
- `data/LS_SKU_for_Onelead.xlsx` - Service catalog (13KB)

### Configuration
- `.streamlit/config.toml` - UI theme and server settings
- `config/config.yaml` - Application configuration
- `requirements.txt` - Dependencies

---

## 🎨 Streamlit Cloud Configuration

### Theme Settings (from config.toml)
```toml
[theme]
primaryColor = "#3b82f6"      # Blue
backgroundColor = "#f8fafc"    # Light gray-blue
secondaryBackgroundColor = "#ffffff"  # White
textColor = "#0f172a"         # Dark slate
font = "sans serif"
```

### Server Settings
```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true
```

---

## 🔐 Environment Variables (if needed)

If you need to add secrets or environment variables:

1. Go to Streamlit Cloud app settings
2. Click "Advanced settings"
3. Add secrets in TOML format:

```toml
# Example secrets (not currently used)
[database]
connection_string = "sqlite:///database/onelead.db"

[api]
hpe_api_key = "your-key-here"
```

---

## 📊 Deployment Statistics

### App Size
- **Total Repository**: ~15 MB
- **Application Code**: ~200 KB
- **Database**: 912 KB
- **Excel Files**: 641 KB
- **Documentation**: ~500 KB

### Resource Usage
- **Memory**: ~200 MB (estimated)
- **Build Time**: 2-3 minutes
- **Startup Time**: 5-10 seconds

### Data Loaded
- 77 leads scored and prioritized
- $6.4M pipeline identified
- 63 install base records
- 98 opportunities
- 2,394 historical projects

---

## 🔄 Update Deployment

### Method 1: Git Push (Automatic)
```bash
# Make changes locally
git add .
git commit -m "Update dashboard"
git push origin 09Oct

# Streamlit Cloud auto-deploys in ~2 minutes
```

### Method 2: Streamlit Cloud UI
1. Go to app settings
2. Click "Reboot app" to use latest code
3. Click "Clear cache" if data isn't updating

---

## 🐛 Troubleshooting Deployment

### Issue: "ModuleNotFoundError"

**Problem**: Missing dependencies

**Solution**:
1. Check requirements.txt has all packages
2. Verify exact versions match local environment
3. Rebuild app from Streamlit Cloud UI

### Issue: "File Not Found" Errors

**Problem**: Database or Excel files not loading

**Solution**:
1. Verify files exist in repository
2. Check .gitignore allows these files:
   ```
   !database/onelead.db
   !data/*.xlsx
   ```
3. Verify file paths are relative, not absolute

### Issue: "App Loading Forever"

**Problem**: App crashes during startup

**Solutions**:
1. Check logs in Streamlit Cloud UI
2. Look for Python errors in stack trace
3. Test locally first: `streamlit run app.py`
4. Verify database file isn't corrupted

### Issue: "Slow Performance"

**Problem**: App is slow to load

**Solutions**:
1. Check `@st.cache_data` decorators are in place
2. Reduce data loaded at startup
3. Optimize database queries
4. Consider pagination for large datasets

---

## 📈 Monitoring

### Streamlit Cloud Dashboard

**Metrics Available:**
- App views
- Active users
- Error rate
- Uptime percentage

**Access**: https://share.streamlit.io/ → Your Apps → oneleads

### Logs

**View logs:**
1. Go to app page
2. Click "Manage app"
3. Click "Logs" tab
4. Monitor real-time logs

---

## 🔄 Rollback Procedure

If deployment breaks:

### Quick Rollback
```bash
# Revert to previous commit
git revert HEAD
git push origin 09Oct

# Streamlit Cloud auto-deploys previous version
```

### Full Rollback
```bash
# Reset to specific working commit
git reset --hard <commit-hash>
git push origin 09Oct --force

# Rebuild app in Streamlit Cloud
```

---

## 🎯 Production Checklist

Before going live to users:

- [ ] Test all dashboard features work
- [ ] Verify data loads correctly (77 leads)
- [ ] Check scoring breakdown displays
- [ ] Test filters (priority, type, score)
- [ ] Verify charts render properly
- [ ] Test on mobile/tablet view
- [ ] Check load time (<10 seconds)
- [ ] Review error logs (should be empty)
- [ ] Test with different users
- [ ] Document any known issues

---

## 📞 Support

### Streamlit Cloud Issues
- **Documentation**: https://docs.streamlit.io/streamlit-cloud
- **Community Forum**: https://discuss.streamlit.io/
- **Support**: support@streamlit.io

### Application Issues
- **GitHub Issues**: https://github.com/jjayarajdev/onelead/issues
- **Local Testing**: `streamlit run app.py`
- **Logs**: Check Streamlit Cloud logs tab

---

## 🚀 Post-Deployment Tasks

### Immediately After Deployment

1. **Verify App is Live**
   - Visit: https://oneleads.streamlit.app/
   - Check Premium Dashboard loads
   - Verify 77 leads display

2. **Test Core Features**
   - Filters work (priority, type, score)
   - Details expander shows scoring breakdown
   - Charts render correctly
   - Buttons are clickable

3. **Monitor Performance**
   - Initial load time: <10 seconds
   - Page transitions: <2 seconds
   - No errors in logs

### First Week

1. **Gather User Feedback**
   - Share URL with team
   - Document feature requests
   - Note any bugs or issues

2. **Monitor Usage**
   - Track app views
   - Monitor error rates
   - Check uptime percentage

3. **Optimize if Needed**
   - Add caching if slow
   - Fix any bugs found
   - Improve based on feedback

---

## 📝 Deployment History

| Date | Version | Changes | Status |
|------|---------|---------|--------|
| 2025-10-09 | 2.0 | Initial Premium Dashboard deployment | ✅ Ready |

---

## 🎉 Success Indicators

**Deployment is successful if:**

✅ App loads at https://oneleads.streamlit.app/
✅ Premium Dashboard displays with modern design
✅ 77 leads show with complete data
✅ Filters work (priority, type, score range)
✅ Details expander shows scoring breakdown
✅ Charts render (priority pipeline, type distribution)
✅ No errors in Streamlit Cloud logs
✅ Load time under 10 seconds

**Ready for users when:**

✅ All success indicators above are met
✅ Tested on Chrome, Firefox, Safari
✅ Mobile/tablet view works
✅ No critical bugs found
✅ Performance is acceptable
✅ Documentation is complete

---

## 🔗 Quick Links

- **Live App**: https://oneleads.streamlit.app/
- **GitHub**: https://github.com/jjayarajdev/onelead
- **Branch**: 09Oct
- **Streamlit Cloud**: https://share.streamlit.io/
- **Documentation**: /LAUNCH_PREMIUM.md
- **Quick Reference**: /QUICK_REFERENCE.md

---

**Last Updated**: October 9, 2025
**Deployment Status**: ✅ Ready for deployment
**Deployment Type**: Streamlit Cloud
**Expected URL**: https://oneleads.streamlit.app/
