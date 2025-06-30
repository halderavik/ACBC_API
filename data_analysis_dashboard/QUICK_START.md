# 🚀 Quick Start Guide - ACBC Data Analysis Dashboard

Get the ACBC Data Analysis Dashboard running in 5 minutes!

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL database with ACBC data
- Access to the main ACBC database

## ⚡ Quick Start (3 Steps)

### Step 1: Navigate to Dashboard Directory
```bash
cd data_analysis_dashboard
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Start the Dashboard

**Option A: Using the startup script (Recommended)**
```bash
python start_dashboard.py
```

**Option B: Direct start**
```bash
python app.py
```

**Option C: Windows users**
```bash
start_dashboard.bat
```

## 🌐 Access the Dashboard

Once started, open your browser and go to:
- **Dashboard**: http://localhost:5001
- **API Endpoints**: http://localhost:5001/api/

## 🔧 Configuration

### Environment Variables (Optional)

Set these environment variables to customize the dashboard:

```bash
# Database connection (REQUIRED - update with your actual database)
export DATABASE_URL="postgresql://username:password@localhost/acbc_db"

# API base URL (optional)
export API_BASE_URL="https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com"

# Dashboard port (default: 5001)
export PORT=5001
```

### Default Configuration

If you don't set environment variables, the dashboard uses these defaults:
- **Database**: `postgresql://postgres:password@localhost/acbc_db`
- **API URL**: `https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com`
- **Port**: `5001`

## 🧪 Test Your Setup

Run the connection test to verify everything is working:

```bash
python test_connection.py
```

This will:
- ✅ Test database connection
- ✅ Verify required tables exist
- ✅ Check data availability
- ✅ Test dashboard queries

## 📊 Dashboard Features

Once running, you'll have access to:

### 📈 Overview Tab
- Session statistics and completion rates
- Real-time activity charts
- Recent sessions table

### 🔍 Sessions Tab
- Individual session details
- Session progress tracking
- Response analysis

### 🎨 Designs Tab
- Screening concept analysis
- Tournament concept analysis
- Attribute level usage

### 📝 Responses Tab
- Response distribution charts
- Choice pattern analysis
- Concept preference analysis

### ✅ Completion Tab
- Session completion flow
- Daily activity trends
- Average response analysis

### 🏷️ Attributes Tab
- Attribute preferences
- BYO configuration analysis
- Level preference analysis

## 🚨 Troubleshooting

### Common Issues

**"Database connection failed"**
- Check if PostgreSQL is running
- Verify DATABASE_URL is correct
- Ensure database credentials are valid

**"No data displayed"**
- Verify database contains ACBC data
- Check if sessions, screening_tasks, and tournament_tasks tables exist
- Run `python test_connection.py` to diagnose

**"Port already in use"**
- Change PORT environment variable
- Or stop other services using port 5001

### Getting Help

1. **Run the test script**: `python test_connection.py`
2. **Check the logs**: Look for error messages in the console
3. **Verify database**: Ensure ACBC tables exist and contain data
4. **Check environment**: Verify all environment variables are set correctly

## 📱 Dashboard Usage

### Navigation
- Use the tab navigation at the top to switch between different analysis views
- Each tab provides different insights into your ACBC data

### Data Refresh
- Dashboard auto-refreshes every 30 seconds
- Use the "Refresh Data" button to manually update

### Export Data
- Use the export functionality to download all data as JSON
- Perfect for external analysis or backup

## 🎯 Next Steps

After getting the dashboard running:

1. **Explore the data**: Navigate through different tabs to understand your data
2. **Analyze patterns**: Look for trends in completion rates and preferences
3. **Optimize designs**: Use design analysis to improve concept generation
4. **Monitor performance**: Track session completion and response patterns

## 📞 Support

If you encounter issues:

1. Check this Quick Start Guide
2. Review the full README.md
3. Run the test script: `python test_connection.py`
4. Check console logs for error messages

---

**Dashboard Version**: 1.0.0  
**Last Updated**: December 2024 