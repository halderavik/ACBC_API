# ACBC Data Analysis Dashboard

A comprehensive data viewing and analyzing dashboard for the ACBC (Adaptive Choice-Based Conjoint) system that shows all collected data based on session data storage, designs shown, all options presented at all stages of the process, and corresponding selections by respondents.

**🔄 Updated**: This dashboard now connects directly to the **Heroku production database** to provide real-time analysis of live data.

## 🎯 Features

### 📊 Overview Dashboard
- **Session Statistics**: Total sessions, screening started, tournament started, and completion rates
- **Completion Flow Visualization**: Interactive charts showing the flow from session creation to completion
- **Recent Activity**: Real-time tracking of recent sessions and their progress
- **Recent Sessions Table**: Detailed view of the latest 20 sessions with response counts

### 🔍 Session Analysis
- **Individual Session Details**: Click on any session to view detailed information
- **Session Progress Tracking**: Monitor screening and tournament task completion
- **Response Analysis**: View all responses and choices made by respondents
- **Session Timeline**: Track when sessions were created and completed

### 🎨 Design Analysis
- **Screening Concepts**: Analysis of all screening concepts shown to respondents
- **Tournament Concepts**: Analysis of all tournament concepts presented
- **Attribute Level Usage**: Frequency analysis of attribute levels shown across all sessions
- **Design Distribution**: Visual representation of concept frequency and distribution

### 📈 Response Analysis
- **Screening Response Distribution**: Analysis of Yes/No responses in screening phase
- **Tournament Choice Distribution**: Analysis of choice patterns in tournament phase
- **Concept Preference Analysis**: Detailed breakdown of concept preferences and selection rates
- **Response Patterns**: Identification of common response patterns and trends

### ✅ Completion Analysis
- **Session Completion Flow**: Track completion rates at each stage
- **Daily Activity Trends**: Time-based analysis of session creation and completion
- **Average Response Analysis**: Statistical analysis of responses per session
- **Completion Rate Optimization**: Identify bottlenecks in the completion process

### 🏷️ Attribute Analysis
- **Attribute Level Preferences**: Analysis of respondent preferences for each attribute level
- **BYO Configuration Usage**: Analysis of different Build-Your-Own configurations used
- **Utility Analysis**: Examination of utility values and their distribution
- **Preference Patterns**: Identification of attribute importance and preference patterns

### 🔎 Session Filtering (NEW)
- **Session ID Filter**: Multi-select dropdown to filter all analysis tabs (except Overview) by one or more session IDs
- **Submit Button**: Apply the filter to update all charts and tables in the current tab
- **Works on**: Sessions, Designs, Responses, Completion, and Attributes tabs
- **Endpoint**: Uses `/api/all-session-ids` to fetch all available session IDs

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Access to the Heroku production database
- No local PostgreSQL required (connects to production)

### Installation

1. **Clone or navigate to the dashboard directory**:
   ```bash
   cd data_analysis_dashboard
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**:
   The dashboard comes pre-configured with the Heroku database connection. The `.env` file contains:
   ```env
   # Heroku Production Database
   DATABASE_URL=postgresql://your-heroku-db-url-here
   API_BASE_URL=https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com
   PORT=5001
   ```

4. **Start the dashboard**:

   **Option A: Using startup script (Recommended)**
   ```bash
   python start_dashboard.py
   ```

   **Option B: Direct start**
   ```bash
   hypercorn app:app --bind 0.0.0.0:5001 --workers 1
   ```

   **Option C: Windows users**
   ```bash
   start_dashboard.bat
   ```

5. **Access the dashboard**:
   Open your browser and navigate to `http://localhost:5001`

## 📊 Dashboard Sections

### 1. Overview Tab
- **Key Metrics**: Total sessions, completion rates, and activity levels
- **Completion Flow Chart**: Visual representation of session progression
- **Recent Activity Chart**: Time-series analysis of recent sessions
- **Recent Sessions Table**: Quick overview of latest sessions

### 2. Sessions Tab
- **Session Cards**: Interactive cards showing session details
- **Session Statistics**: Individual session metrics and progress
- **Session Details**: Click to view detailed session information (coming soon)

### 3. Designs Tab
- **Screening Concepts Chart**: Most frequently shown screening concepts
- **Tournament Concepts Chart**: Most frequently shown tournament concepts
- **Attribute Usage Table**: Complete breakdown of attribute level usage

### 4. Responses Tab
- **Screening Response Distribution**: Pie chart of Yes/No responses
- **Tournament Choice Distribution**: Bar chart of choice patterns
- **Concept Preferences Table**: Detailed preference analysis

### 5. Completion Tab
- **Daily Activity Chart**: Time-series of session activity
- **Average Responses Chart**: Statistical analysis of responses per session
- **Completion Statistics Table**: Detailed completion flow statistics

### 6. Attributes Tab
- **Attribute Preferences Chart**: Visual representation of level preferences
- **BYO Configurations Chart**: Analysis of different configurations used
- **Level Preferences Table**: Detailed preference analysis by attribute

## 🔧 Configuration

### Database Connection
The dashboard connects directly to the **Heroku production PostgreSQL database** to access:
- `sessions` table: Session information and configurations
- `screening_tasks` table: Screening phase data and responses
- `tournament_tasks` table: Tournament phase data and choices

### Environment Variables
- `DATABASE_URL`: Heroku PostgreSQL connection string (pre-configured)
- `API_BASE_URL`: Main ACBC API URL (pre-configured)
- `PORT`: Dashboard port (default: 5001)

### Default Configuration
The dashboard is pre-configured to connect to the production database:
- **Database**: Heroku PostgreSQL production database
- **API URL**: `https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com`
- **Port**: `5001`

## 📈 Data Analysis Features

### Real-time Analytics
- **Auto-refresh**: Dashboard automatically refreshes every 30 seconds
- **Live Data**: Direct connection to production database for real-time insights
- **Interactive Charts**: Click on chart elements for detailed information

### Export Functionality
- **JSON Export**: Export all data for external analysis
- **Timestamped Exports**: All exports include timestamp for tracking
- **Complete Dataset**: Full session data including all responses and choices

### Statistical Analysis
- **Completion Rates**: Track session completion at each stage
- **Response Patterns**: Analyze common response patterns
- **Preference Analysis**: Identify attribute and level preferences
- **Trend Analysis**: Time-based analysis of user behavior

## 🛠️ Technical Details

### Architecture
- **Flask Backend**: Lightweight web framework for API endpoints
- **Async Database**: Async PostgreSQL connections to production database
- **Chart.js Frontend**: Interactive charts and visualizations
- **Responsive Design**: Works on desktop and mobile devices

### Database Queries
The dashboard uses optimized SQL queries to:
- Aggregate session data efficiently
- Calculate completion statistics
- Analyze response patterns
- Generate preference insights

### Performance
- **Connection Pooling**: Efficient database connection management
- **Async Operations**: Non-blocking database queries
- **Caching**: Chart data caching for improved performance
- **Optimized Queries**: Efficient SQL for large datasets

## 🔍 Usage Examples

### Analyzing Session Completion
1. Navigate to the "Completion" tab
2. View the completion flow chart to identify bottlenecks
3. Check the daily activity chart for trends
4. Review completion statistics table for detailed metrics

### Understanding Respondent Preferences
1. Go to the "Responses" tab
2. Analyze screening response distribution
3. Review tournament choice patterns
4. Examine concept preference analysis

### Design Optimization
1. Visit the "Designs" tab
2. Review most shown concepts
3. Analyze attribute level usage
4. Identify underutilized or overutilized designs

## 🚨 Troubleshooting

### Common Issues

**Database Connection Error**:
- Verify `DATABASE_URL` in `.env` file is correct
- Ensure Heroku database is accessible
- Check if the production database is running

**No Data Displayed**:
- Verify production database contains ACBC data
- Check database permissions
- Review console for error messages
- Run `python test_connection.py` to diagnose

**Charts Not Loading**:
- Check browser console for JavaScript errors
- Verify Chart.js is loading correctly
- Ensure API endpoints are responding

### Debug Mode
Run the dashboard in debug mode for detailed error messages:
```bash
export FLASK_ENV=development
hypercorn app:app --bind 0.0.0.0:5001 --workers 1
```

### Connection Test
Run the connection test to verify everything is working:
```bash
python test_connection.py
```

This will:
- ✅ Test database connection to production
- ✅ Verify required tables exist
- ✅ Check data availability
- ✅ Test dashboard queries

## 📝 API Endpoints

The dashboard provides the following API endpoints:

- `GET /api/sessions-overview`: Session overview and statistics (now supports filtering by session_ids)
- `GET /api/all-session-ids`: List of all session IDs for filtering
- `GET /api/session-details/<session_id>`: Detailed session information
- `GET /api/design-analysis`: Design and concept analysis (supports session_ids)
- `GET /api/response-analysis`: Response and choice analysis (supports session_ids)
- `GET /api/completion-analysis`: Completion rate analysis (supports session_ids)
- `GET /api/attribute-analysis`: Attribute preference analysis (supports session_ids)
- `GET /api/export-data`: Export all data for external analysis

## 🔮 Future Enhancements

- **Session Detail Modal**: Detailed view of individual sessions
- **Advanced Filtering**: Filter data by date, completion status, etc.
- **Comparative Analysis**: Compare different time periods or configurations
- **Predictive Analytics**: Predict completion rates and preferences
- **Real-time Alerts**: Notifications for unusual patterns or issues
- **Data Export Formats**: CSV, Excel, and other export formats

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review console logs for error messages
3. Verify database connectivity and permissions
4. Ensure all dependencies are installed correctly
5. Run `python test_connection.py` to diagnose issues

---

**Dashboard Version**: 1.0.0  
**Last Updated**: December 2024  
**Compatible with**: ACBC API v1.0.0+  
**Database**: Heroku Production PostgreSQL 