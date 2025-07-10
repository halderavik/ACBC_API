# ACBC API Documentation

## Overview

The ACBC (Adaptive Choice-Based Conjoint) API is a FastAPI-based backend service that implements a complete conjoint analysis workflow. The API supports three main phases: BYO (Build-Your-Own) configuration, screening tasks, and tournament choices.

**Base URL:** `https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com`

**API Documentation:** `https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/docs`

## 📊 Monitoring Dashboard

The ACBC API includes a comprehensive monitoring dashboard for tracking API activity, performance, and user behavior.

**Dashboard URL:** `http://localhost:5000` (when running locally)

**Features:**
- **Real-time API Monitoring**: Live tracking of API health and performance
- **Request Analytics**: Detailed statistics on API usage and response times
- **Error Tracking**: Comprehensive error logging with stack traces
- **Session Analytics**: User session tracking and completion rates
- **Traffic Analysis**: Traffic sources and user agent tracking
- **Visual Charts**: Interactive charts for endpoint usage and status codes

**Dashboard Setup:**
```bash
cd dashboard
pip install -r requirements.txt
python generate_sample_data.py  # Optional: Generate demo data
hypercorn app:app --bind 0.0.0.0:5000  # Use Hypercorn for async support
```

**Integration with API:**
The dashboard can be integrated with your FastAPI application using the provided monitoring middleware:

```python
from fastapi import FastAPI
from dashboard.monitor_middleware import monitoring_middleware

app = FastAPI()
app.middleware("http")(monitoring_middleware)
```

For detailed dashboard documentation, see [dashboard/README.md](./dashboard/README.md).

## 📊 Data Analysis Dashboard

The ACBC API also includes a comprehensive data analysis dashboard for viewing and analyzing all collected data.

**Data Analysis Dashboard URL:** `http://localhost:5001` (when running locally)

**Features:**
- **Session Overview**: Total sessions, completion rates, recent activity
- **Session Details**: Individual session analysis and progress tracking
- **Design Analysis**: Screening and tournament concept analysis
- **Response Analysis**: Respondent choices and preference analysis
- **Completion Analysis**: Session completion flow and time analysis
- **Attribute Analysis**: Attribute preferences and utility analysis
- **Interactive Charts**: Chart.js visualizations for all data types
- **Real-time Data**: Direct connection to production database
- **Export Functionality**: JSON export of all collected data
- **Responsive Design**: Works on desktop and mobile devices

**Data Analysis Dashboard Setup:**
```bash
cd data_analysis_dashboard
pip install -r requirements.txt
hypercorn app:app --bind 0.0.0.0:5001  # Use Hypercorn for async support
```

**Quick Start (Windows):**
```bash
cd data_analysis_dashboard
start_dashboard.bat
```

**Quick Start (Python):**
```bash
cd data_analysis_dashboard
python start_dashboard.py
```

For detailed data analysis dashboard documentation, see [data_analysis_dashboard/README.md](./data_analysis_dashboard/README.md).

---

## Table of Contents

1. [Authentication](#authentication)
2. [Workflow Overview](#workflow-overview)
3. [BYO Configuration](#byo-configuration)
4. [Screening Tasks](#screening-tasks)
5. [Tournament Choices](#tournament-choices)
6. [Error Handling](#error-handling)
7. [Data Models](#data-models)
8. [Examples](#examples)
9. [Monitoring Dashboard](#monitoring-dashboard)
10. [Data Analysis Dashboard](#data-analysis-dashboard)
11. [Troubleshooting](#troubleshooting)

---

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

---

## Workflow Overview

The ACBC workflow consists of three sequential phases:

1. **BYO Configuration** - Define attributes and their possible values
2. **Screening Tasks** - Rate concept combinations to establish initial preferences
3. **Tournament Choices** - Make pairwise choices to refine preference estimates

Each phase builds upon the previous one, creating an adaptive learning system.

---

## BYO Configuration

### POST /api/byo-config

Creates a new session with BYO (Build-Your-Own) configuration and initializes screening tasks.

**Endpoint:** `POST /api/byo-config`

**Request Body:**
```json
{
  "session_id": "string (optional)",
  "selected_attributes": {
    "attribute_name": ["value1", "value2", "value3"],
    "another_attribute": ["option1", "option2", "option3"]
  }
}
```

**Parameters:**
- `session_id` (optional): Custom session identifier. If not provided, a UUID will be generated
- `selected_attributes` (required): Dictionary where keys are attribute names and values are arrays of possible values

**Example Request:**
```json
{
  "session_id": "test123",
  "selected_attributes": {
    "brand": ["Nike", "Adidas", "Puma"],
    "material": ["leather", "canvas", "synthetic"],
    "style": ["casual", "athletic", "formal"]
  }
}
```

**Response:**
```json
{
  "session_id": "test123"
}
```

**What Happens:**
- Creates a new session record in the database
- Stores the BYO configuration
- Generates screening tasks based on the attribute combinations
- Returns the session ID for future API calls

**Error Responses:**
- `422 Unprocessable Entity`: Missing or invalid `selected_attributes`
- `500 Internal Server Error`: Database or processing errors

---

## Screening Tasks

### GET /api/screening/design

Retrieves the screening design for a specific session.

**Endpoint:** `GET /api/screening/design?session_id={session_id}`

**Parameters:**
- `session_id` (required): The session ID from the BYO configuration

**Example Request:**
```
GET /api/screening/design?session_id=test123
```

**Response:**
```json
[
  {
    "id": 1,
    "concept": {
      "brand": "Nike",
      "material": "leather",
      "style": "casual"
    },
    "position": 1,
    "response": null
  },
  {
    "id": 2,
    "concept": {
      "brand": "Adidas",
      "material": "canvas",
      "style": "athletic"
    },
    "position": 2,
    "response": null
  }
]
```

**Response Fields:**
- `id`: Unique identifier for the screening task
- `concept`: Object containing attribute-value combinations
- `position`: Order of presentation
- `response`: User's response (null until submitted)

**Error Responses:**
- `400 Bad Request`: Missing session_id parameter
- `404 Not Found`: Session not found

### POST /api/screening/responses

Submits screening responses and calculates initial utility estimates.

**Endpoint:** `POST /api/screening/responses`

**Request Body:**
```json
{
  "session_id": "string",
  "responses": [boolean, boolean, boolean, ...]
}
```

**Parameters:**
- `session_id` (required): The session ID
- `responses` (required): Array of boolean values corresponding to each screening task (true = like, false = dislike)

**Example Request:**
```json
{
  "session_id": "test123",
  "responses": [true, false, true, false, true]
}
```

**Response:**
```json
{
  "status": "ok"
}
```

**What Happens:**
- Records user responses for each screening task
- Calculates initial utility estimates based on preferences
- Updates the session with utility data for tournament phase

**Error Responses:**
- `404 Not Found`: Session not found
- `422 Unprocessable Entity`: Invalid response format

---

## Tournament Choices

### GET /api/tournament/choice

Retrieves tournament choice tasks for a specific session and task number.

**Endpoint:** `GET /api/tournament/choice?session_id={session_id}&task_number={task_number}`

**Parameters:**
- `session_id` (required): The session ID
- `task_number` (optional): Task number (defaults to 1)

**Example Request:**
```
GET /api/tournament/choice?session_id=test123&task_number=1
```

**Response:**
```json
{
  "task_number": 1,
  "concepts": [
    {
      "id": 1,
      "attributes": {
        "brand": "Nike",
        "material": "leather",
        "style": "casual"
      }
    },
    {
      "id": 2,
      "attributes": {
        "brand": "Adidas",
        "material": "canvas",
        "style": "athletic"
      }
    }
  ]
}
```

**Response Fields:**
- `task_number`: Current tournament task number
- `concepts`: Array of concept pairs for choice tasks

**Error Responses:**
- `400 Bad Request`: Missing session_id or invalid task_number
- `404 Not Found`: Session not found

### POST /api/tournament/choice-response

Submits a choice response and updates utility estimates.

**Endpoint:** `POST /api/tournament/choice-response`

**Request Body:**
```json
{
  "session_id": "string",
  "task_number": "integer",
  "selected_concept_id": "integer"
}
```

**Parameters:**
- `session_id` (required): The session ID
- `task_number` (required): Current task number
- `selected_concept_id` (required): ID of the chosen concept (0, 1, 2, etc.)

**Example Request:**
```json
{
  "session_id": "test123",
  "task_number": 1,
  "selected_concept_id": 0
}
```

**Response:**
```json
{
  "next_task": 2
}
```

**What Happens:**
- Records the user's choice
- Updates utility estimates using adaptive algorithms
- Returns the next task number

**Important Notes:**
- `selected_concept_id` must be a valid index into the concepts array (0, 1, 2, etc.)
- The concept IDs correspond to the order in the concepts array returned by the tournament choice endpoint
- For sessions with legacy data structure, only concept ID 0 may be available initially

**Error Responses:**
- `400 Bad Request`: Invalid concept ID (e.g., "Invalid choice_id 1. Must be between 0 and 0")
- `404 Not Found`: Session or task not found
- `422 Unprocessable Entity`: Invalid request format

---

## Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

For validation errors:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "field_name"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

---

## Data Models

### BYOConfig
```json
{
  "session_id": "string (optional)",
  "selected_attributes": {
    "attribute_name": ["value1", "value2", "value3"]
  }
}
```

### ScreeningDesignOut
```json
{
  "id": "integer",
  "concept": {
    "attribute_name": "value"
  },
  "position": "integer",
  "response": "boolean (nullable)"
}
```

### ScreeningResponseIn
```json
{
  "session_id": "string",
  "responses": ["boolean"]
}
```

### TournamentDesignOut
```json
{
  "task_number": "integer",
  "concepts": [
    {
      "id": "integer",
      "attributes": {
        "attribute_name": "value"
      }
    }
  ]
}
```

### ChoiceResponseIn
```json
{
  "session_id": "string",
  "task_number": "integer",
  "selected_concept_id": "integer"
}
```

---

## Examples

### Complete Workflow Example

#### 1. Create BYO Configuration
```bash
curl -X POST "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/byo-config" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "example123",
    "selected_attributes": {
      "color": ["red", "blue", "green"],
      "size": ["small", "medium", "large"],
      "price": [10, 20, 30]
    }
  }'
```

#### 2. Get Screening Design
```bash
curl "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/screening/design?session_id=example123"
```

#### 3. Submit Screening Responses
```bash
curl -X POST "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/screening/responses" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "example123",
    "responses": [true, false, true, false, true]
  }'
```

#### 4. Get Tournament Choice
```bash
curl "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/tournament/choice?session_id=example123&task_number=1"
```

#### 5. Submit Choice Response
```bash
curl -X POST "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/tournament/choice-response" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "example123",
    "task_number": 1,
    "selected_concept_id": 0
  }'
```

### Postman Collection

You can import these requests into Postman:

1. **BYO Configuration**
   - Method: POST
   - URL: `{{base_url}}/api/byo-config`
   - Body: Raw JSON with BYOConfig

2. **Screening Design**
   - Method: GET
   - URL: `{{base_url}}/api/screening/design?session_id={{session_id}}`

3. **Screening Responses**
   - Method: POST
   - URL: `{{base_url}}/api/screening/responses`
   - Body: Raw JSON with ScreeningResponseIn

4. **Tournament Choice**
   - Method: GET
   - URL: `{{base_url}}/api/tournament/choice?session_id={{session_id}}&task_number={{task_number}}`

5. **Choice Response**
   - Method: POST
   - URL: `{{base_url}}/api/tournament/choice-response`
   - Body: Raw JSON with ChoiceResponseIn

---

## Frequently Asked Questions

### Q: How many attributes can I define in BYO configuration?
A: There's no hard limit, but typically 3-5 attributes work best for user experience.

### Q: How many values can each attribute have?
A: Recommended 2-5 values per attribute for optimal analysis.

### Q: How many screening tasks are generated?
A: The system generates a subset of all possible combinations, typically 5-10 tasks.

### Q: Can I reuse a session ID?
A: No, each session ID should be unique. If you provide an existing ID, it will create a new session.

### Q: How many tournament tasks are there?
A: The number varies based on the adaptive algorithm, typically 10-20 tasks.

### Q: What happens if I skip a screening response?
A: All screening responses must be provided before proceeding to tournament tasks.

### Q: Can I get the final utility estimates?
A: Currently, the API focuses on the choice process. Utility estimates are used internally for adaptive learning.

### Q: Is the API stateless?
A: No, the API maintains session state in the database throughout the workflow.

### Q: What if I get "Invalid choice_id" errors?
A: The `selected_concept_id` must be a valid index (0, 1, 2, etc.) into the concepts array. Check the tournament choice response to see available concept IDs.

### Q: What if I get "Multiple rows were found" errors?
A: This indicates duplicate tournament tasks in the database. The API now handles this automatically, but you may need to use concept ID 0 for legacy sessions.

---

## Troubleshooting

### Common Error Messages

**"Invalid choice_id X. Must be between 0 and Y"**
- **Cause**: Trying to select a concept ID that doesn't exist
- **Solution**: Use a valid concept ID (0, 1, 2, etc.) based on the concepts returned by the tournament choice endpoint

**"Multiple rows were found when one or none was required"**
- **Cause**: Duplicate tournament tasks in the database (legacy data issue)
- **Solution**: The API now handles this automatically. Use concept ID 0 for existing sessions

**"Concepts should be a list, but got <class 'dict'>"**
- **Cause**: Legacy data structure where concepts were stored as single objects
- **Solution**: The API now automatically converts old data structure to new format

**"Tournament task not found for session X, task Y"**
- **Cause**: No tournament task exists for the specified session and task number
- **Solution**: Ensure you've completed the screening phase and the tournament task exists

### Dashboard Issues

**"RuntimeError: Install Flask with the 'async' extra in order to use async views"**
- **Cause**: Running Flask app with async views using the default development server
- **Solution**: Use Hypercorn ASGI server instead of `python app.py`
  ```bash
  # Instead of: python app.py
  # Use: hypercorn app:app --bind 0.0.0.0:5000
  ```

**"ModuleNotFoundError: No module named 'hypercorn'"**
- **Cause**: Hypercorn not installed in virtual environment
- **Solution**: Install requirements with async Flask support
  ```bash
  pip install -r requirements.txt
  ```

**"Database connection failed"**
- **Cause**: Database URL not configured or database not accessible
- **Solution**: 
  1. Check DATABASE_URL environment variable
  2. Ensure PostgreSQL is running
  3. Verify database credentials
  4. Test connection with `python test_connection.py`

**"Port already in use"**
- **Cause**: Another application is using the same port
- **Solution**: 
  1. Stop other applications using the port
  2. Use a different port: `hypercorn app:app --bind 0.0.0.0:5002`

### Data Analysis Dashboard Issues

**"500 Internal Server Error on /api/sessions-overview"**
- **Cause**: Async Flask views not properly configured
- **Solution**: 
  1. Ensure using Hypercorn: `hypercorn app:app --bind 0.0.0.0:5001`
  2. Check Flask version: `pip show flask` (should be 3.1.1+)
  3. Verify async support: `pip show flask[async]`

**"NumPy/Pandas version mismatch"**
- **Cause**: Incompatible versions of NumPy and Pandas
- **Solution**: Update to compatible versions
  ```bash
  pip install "pandas>=2.2.0" "numpy>=2.0.0" --upgrade
  ```

**"No data displayed in charts"**
- **Cause**: No data in database or connection issues
- **Solution**:
  1. Check database connection
  2. Verify data exists in production database
  3. Test with sample data generation

### Data Structure Compatibility

The API is backward-compatible with legacy data structures:
- **Old Structure**: Single concept stored as dictionary
- **New Structure**: List of concepts with IDs and attributes
- **Automatic Conversion**: Old data is automatically converted to new format

### Performance Issues

**"Slow dashboard loading"**
- **Cause**: Large datasets or inefficient queries
- **Solution**:
  1. Check database query performance
  2. Consider adding database indexes
  3. Implement caching for frequently accessed data

**"High memory usage"**
- **Cause**: Large datasets loaded into memory
- **Solution**:
  1. Implement pagination for large datasets
  2. Use streaming responses for data export
  3. Optimize database queries

### Development Environment Issues

**"Virtual environment not found"**
- **Cause**: Virtual environment not created or activated
- **Solution**:
  ```bash
  python -m venv venv
  venv\Scripts\activate  # Windows
  source venv/bin/activate  # macOS/Linux
  pip install -r requirements.txt
  ```

**"Permission denied" (Windows)**
- **Cause**: PowerShell execution policy restrictions
- **Solution**:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

**"Module not found" errors**
- **Cause**: Dependencies not installed in virtual environment
- **Solution**:
  ```bash
  pip install -r requirements.txt
  ```

### Production Deployment Issues

**"Heroku deployment failed"**
- **Cause**: Build errors or missing dependencies
- **Solution**:
  1. Check Heroku logs: `heroku logs --tail`
  2. Verify requirements.txt includes all dependencies
  3. Ensure Procfile is correctly configured

**"Database migration errors"**
- **Cause**: Schema changes not applied to production database
- **Solution**:
  ```bash
  heroku run alembic upgrade head
  ```

---

## Support

For technical support or questions about the API:

1. Check the interactive documentation at `/docs`
2. Review the error messages for specific issues
3. Ensure all required parameters are provided
4. Verify the request format matches the expected schema
5. Test with the provided examples
6. Check the troubleshooting section above

### Getting Help

1. **API Issues**: Check the interactive docs and error messages
2. **Dashboard Issues**: Verify async Flask setup and database connection
3. **Deployment Issues**: Check Heroku logs and configuration
4. **Data Issues**: Use the data analysis dashboard to inspect data

---

## Version Information

- **API Version**: 1.2.0
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Deployment**: Heroku
- **Last Updated**: December 2024

### Recent Updates (v1.2.0)
- ✅ Added comprehensive data analysis dashboard
- ✅ Updated both dashboards to Flask 3.x with async support
- ✅ Added Hypercorn ASGI server for proper async Flask support
- ✅ Updated all dependencies to latest compatible versions
- ✅ Enhanced .gitignore with comprehensive patterns
- ✅ Added startup scripts for easy dashboard deployment
- ✅ Improved error handling and troubleshooting documentation
- ✅ Added backward compatibility for legacy data structures
- ✅ Enhanced duplicate tournament task handling
- ✅ Updated concept ID validation and processing 