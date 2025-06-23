# ACBC API Dashboard

A comprehensive monitoring dashboard for the ACBC (Adaptive Choice-Based Conjoint) API that provides real-time insights into API activity, performance, errors, and traffic sources.

## Features

### 📊 Real-time Monitoring
- **API Health Status**: Live monitoring of API availability and response times
- **Request Statistics**: Total requests, 24-hour activity, and response time metrics
- **Error Tracking**: Comprehensive error logging with stack traces and request details
- **Session Analytics**: Track user sessions, completion rates, and engagement

### 📈 Visual Analytics
- **Endpoint Usage Charts**: Doughnut chart showing API endpoint distribution
- **Status Code Distribution**: Bar chart of HTTP status codes
- **Real-time Updates**: Auto-refresh every 30 seconds
- **Responsive Design**: Works on desktop and mobile devices

### 🔍 Detailed Logging
- **Request Logs**: Complete request/response details with timestamps
- **Error Logs**: Detailed error information with stack traces
- **Traffic Sources**: Track where requests are coming from
- **Session Tracking**: Monitor user journey through the ACBC process

## Quick Start

### 1. Install Dependencies

```bash
cd dashboard
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
python app.py
```

The dashboard will be available at `http://localhost:5000`

### 3. Access the Dashboard

Open your browser and navigate to `http://localhost:5000` to view the monitoring dashboard.

## Dashboard Components

### Main Statistics
- **Total Requests**: All-time API request count
- **Requests (24h)**: Requests in the last 24 hours
- **Errors (24h)**: Error count in the last 24 hours
- **Avg Response Time**: Average API response time
- **Active Sessions**: Sessions created in the last 7 days

### Charts
- **Endpoint Usage**: Distribution of API endpoint usage
- **Status Codes**: HTTP status code distribution

### Tables
- **Recent Requests**: Latest 50 API requests with details
- **Recent Errors**: Latest 20 errors with full context

## Integration with Your API

### Option 1: Automatic Monitoring (Recommended)

Add the monitoring middleware to your existing FastAPI application:

```python
from fastapi import FastAPI
from dashboard.monitor_middleware import monitoring_middleware

app = FastAPI()

# Add the monitoring middleware
app.middleware("http")(monitoring_middleware)
```

### Option 2: Manual Logging

Use the utility functions to log specific events:

```python
from dashboard.monitor_middleware import (
    log_session_creation,
    log_screening_completion,
    log_tournament_completion,
    log_response_count
)

# In your route handlers:
@app.post("/byo")
async def create_byo_config(request: Request):
    # Your existing logic here
    
    # Log session creation
    log_session_creation(session_id, byo_config)
    
    return response

@app.post("/screening/response")
async def submit_screening_response(request: Request):
    # Your existing logic here
    
    # Log screening completion
    log_screening_completion(session_id)
    
    return response
```

## Configuration

### API Base URL
Update the `API_BASE_URL` in `app.py` to point to your deployed API:

```python
API_BASE_URL = "https://your-api-url.herokuapp.com"
```

### Database Location
The dashboard uses SQLite for data storage. You can change the database path in `app.py`:

```python
DB_PATH = "dashboard/api_monitor.db"
```

## API Endpoints

The dashboard provides several API endpoints for data access:

### GET `/api/stats`
Returns overall API statistics including request counts, error rates, and performance metrics.

### GET `/api/recent-requests`
Returns the 50 most recent API requests with full details.

### GET `/api/recent-errors`
Returns the 20 most recent errors with stack traces and context.

### GET `/api/traffic-sources`
Returns traffic source statistics and user agent information.

### GET `/api/sessions`
Returns session statistics and completion rates.

### GET `/api/health-check`
Performs a health check on the monitored API and returns status.

## Database Schema

### api_requests
Stores all API request details:
- `timestamp`: Request timestamp
- `endpoint`: API endpoint path
- `method`: HTTP method
- `status_code`: HTTP status code
- `response_time`: Response time in seconds
- `user_agent`: User agent string
- `ip_address`: Client IP address
- `session_id`: Session identifier
- `error_message`: Error message if any
- `request_body`: Request body content
- `response_body`: Response body content

### sessions
Tracks user sessions:
- `session_id`: Unique session identifier
- `created_at`: Session creation timestamp
- `byo_config`: BYO configuration data
- `screening_completed`: Whether screening was completed
- `tournament_completed`: Whether tournament was completed
- `total_responses`: Total number of responses

### errors
Stores error information:
- `timestamp`: Error timestamp
- `error_type`: Type of error
- `error_message`: Error message
- `endpoint`: Endpoint where error occurred
- `stack_trace`: Full stack trace
- `request_body`: Request body that caused error

### traffic_sources
Tracks traffic sources:
- `timestamp`: Request timestamp
- `source`: Traffic source identifier
- `user_agent`: User agent string
- `ip_address`: Client IP address
- `endpoint`: Requested endpoint

## Customization

### Adding New Metrics
To add new metrics, modify the `get_stats()` function in `app.py`:

```python
@app.route('/api/stats')
def get_stats():
    # Add your custom queries here
    cursor.execute('YOUR_CUSTOM_QUERY')
    custom_metric = cursor.fetchone()[0]
    
    return jsonify({
        # ... existing stats
        'custom_metric': custom_metric
    })
```

### Custom Charts
Add new charts by modifying the HTML template and JavaScript:

```javascript
// Add new chart initialization
const newChart = new Chart(ctx, {
    // Chart configuration
});

// Update chart with data
function updateNewChart(data) {
    newChart.data.labels = data.labels;
    newChart.data.datasets[0].data = data.values;
    newChart.update();
}
```

### Styling
The dashboard uses CSS Grid and Flexbox for responsive design. Modify the CSS in `dashboard.html` to customize the appearance.

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
For production deployment, consider using Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
```

## Troubleshooting

### Dashboard Not Loading
1. Check if the dashboard is running on the correct port
2. Verify all dependencies are installed
3. Check the browser console for JavaScript errors

### No Data Showing
1. Ensure the monitoring middleware is integrated with your API
2. Check if the database file exists and is writable
3. Verify the API base URL is correct

### Performance Issues
1. Consider using a production database like PostgreSQL for large datasets
2. Implement data retention policies to limit database size
3. Add database indexing for frequently queried columns

## Security Considerations

- The dashboard is designed for internal monitoring and should not be exposed publicly
- Consider adding authentication for production use
- Implement rate limiting for dashboard API endpoints
- Regularly backup the monitoring database

## Contributing

To contribute to the dashboard:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This dashboard is part of the ACBC API project and follows the same licensing terms. 