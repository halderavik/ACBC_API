# ACBC (Adaptive Choice-Based Conjoint) API

A FastAPI-based backend service for implementing Adaptive Choice-Based Conjoint analysis. This API provides endpoints for BYO (Bring Your Own) configuration, screening tasks, and tournament-based choice experiments.

## 🏗️ Architecture Overview

The ACBC API follows a modular architecture with clear separation of concerns:

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration and async session management
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic schemas for request/response validation
│   ├── services.py          # Business logic and service layer
│   ├── utils.py             # Utility functions for design generation
│   └── routers/
│       ├── byo.py           # BYO configuration endpoints
│       ├── screening.py     # Screening task endpoints
│       └── tournament.py    # Tournament choice endpoints
├── alembic/                 # Database migrations
├── requirements.txt         # Python dependencies
└── .env                     # Environment configuration
```

## 🚀 Features

- **BYO Configuration**: Set up custom attributes and levels for conjoint analysis
- **Screening Tasks**: Generate and manage initial screening tasks
- **Tournament Choices**: Adaptive choice-based conjoint with utility updates
- **Async Database**: PostgreSQL with asyncpg for high performance
- **Automatic Migrations**: Alembic for database schema management
- **Robust Error Handling**: Comprehensive error handling for malformed requests
- **Heroku Ready**: Production-ready deployment configuration

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 12+
- pip (Python package manager)

## 🛠️ Installation & Setup

### Local Development

#### 1. Clone and Navigate to Backend

```bash
cd backend
```

#### 2. Create Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Environment Configuration

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:Password123!@localhost:5432/conjoint

# Application Settings
APP_NAME=ACBC Backend
APP_VERSION=1.0.0
DEBUG=True

# Security Settings
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Settings
HOST=0.0.0.0
PORT=8000
```

#### 5. Database Setup

##### Create PostgreSQL Database

```bash
# Using psql (replace with your PostgreSQL path)
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -c "CREATE DATABASE conjoint;"
```

##### Run Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

#### 6. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## ☁️ Heroku Deployment

### Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

### Quick Deployment

#### Option 1: Using Deployment Script (Recommended)

```bash
# Make script executable (macOS/Linux)
chmod +x deploy.sh

# Run deployment script
./deploy.sh
```

#### Option 2: Manual Deployment

1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

3. **Add PostgreSQL Addon**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key-here
   heroku config:set DEBUG=False
   ```

5. **Deploy Application**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Run Database Migrations**
   ```bash
   heroku run alembic upgrade head
   ```

7. **Open Application**
   ```bash
   heroku open
   ```

### Heroku Configuration Files

The project includes the following Heroku-specific files:

- **`Procfile`**: Tells Heroku how to run the application
- **`runtime.txt`**: Specifies Python version
- **`app.json`**: Heroku app configuration
- **`deploy.sh`**: Automated deployment script

### Environment Variables on Heroku

Heroku automatically provides:
- `DATABASE_URL`: PostgreSQL connection string
- `PORT`: Port number for the application

You can set additional variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
```

## 📚 API Documentation

Once the server is running, you can access:
- **Interactive API Docs**: `http://localhost:8000/docs` (local) or `https://your-app.herokuapp.com/docs` (Heroku)
- **ReDoc Documentation**: `http://localhost:8000/redoc` (local) or `https://your-app.herokuapp.com/redoc` (Heroku)

## 🔌 API Endpoints

### 1. BYO Configuration

#### Create Session and Configure Attributes

**Endpoint:** `POST /api/byo-config`

**Request Body:**
```json
{
  "session_id": null,
  "selected_attributes": {
    "Color": ["Red", "Blue", "Green"],
    "Size": ["S", "M", "L"],
    "Price": ["$10", "$20", "$30"]
  }
}
```

**Response:**
```json
{
  "session_id": "019aa9fe-4c76-4b4b-bb8d-cc5cdcc0019d"
}
```

**Alternative GET Request (handles malformed URLs):**
```
GET /api/byo-config?session_id=null&selected_attributes={"Color":["Red","Blue"],"Size":["S","M"]}
```

### 2. Screening Tasks

#### Get Screening Design

**Endpoint:** `GET /api/screening/design`

**Query Parameters:**
- `session_id` (required): Session identifier
- `task_number` (optional): Defaults to 1

**Example:**
```
GET /api/screening/design?session_id=019aa9fe-4c76-4b4b-bb8d-cc5cdcc0019d
```

**Response:**
```json
[
  {
    "id": 1,
    "concept": {
      "Color": "Red",
      "Size": "S"
    },
    "position": 1,
    "response": null
  },
  {
    "id": 2,
    "concept": {
      "Color": "Blue",
      "Size": "M"
    },
    "position": 2,
    "response": null
  }
]
```

#### Submit Screening Responses

**Endpoint:** `POST /api/screening/responses`

**Request Body:**
```json
{
  "session_id": "019aa9fe-4c76-4b4b-bb8d-cc5cdcc0019d",
  "responses": [true, false, true, false, true]
}
```

**Response:**
```json
{
  "status": "ok"
}
```

### 3. Tournament Choices

#### Get Tournament Choice

**Endpoint:** `GET /api/tournament/choice`

**Query Parameters:**
- `session_id` (required): Session identifier
- `task_number` (optional): Defaults to 1

**Example:**
```
GET /api/tournament/choice?session_id=019aa9fe-4c76-4b4b-bb8d-cc5cdcc0019d&task_number=1
```

**Response:**
```json
{
  "task_number": 1,
  "concepts": [
    {
      "Color": "Red",
      "Size": "S"
    },
    {
      "Color": "Blue",
      "Size": "M"
    },
    {
      "Color": "Red",
      "Size": "M"
    }
  ]
}
```

#### Submit Choice Response

**Endpoint:** `POST /api/tournament/choice-response`

**Request Body:**
```json
{
  "session_id": "019aa9fe-4c76-4b4b-bb8d-cc5cdcc0019d",
  "task_number": 1,
  "selected_concept_id": 2
}
```

**Response:**
```json
{
  "next_task": 2
}
```

## 🧪 Testing with Postman

### Complete Testing Flow

1. **Create Session**
   ```
   POST http://localhost:8000/api/byo-config
   Content-Type: application/json
   
   {
     "session_id": null,
     "selected_attributes": {
       "Color": ["Red", "Blue"],
       "Size": ["S", "M"]
     }
   }
   ```

2. **Get Screening Design**
   ```
   GET http://localhost:8000/api/screening/design?session_id=YOUR_SESSION_ID
   ```

3. **Submit Screening Responses**
   ```
   POST http://localhost:8000/api/screening/responses
   Content-Type: application/json
   
   {
     "session_id": "YOUR_SESSION_ID",
     "responses": [true, false, true, false, true]
   }
   ```

4. **Get Tournament Choice**
   ```
   GET http://localhost:8000/api/tournament/choice?session_id=YOUR_SESSION_ID&task_number=1
   ```

5. **Submit Choice Response**
   ```
   POST http://localhost:8000/api/tournament/choice-response
   Content-Type: application/json
   
   {
     "session_id": "YOUR_SESSION_ID",
     "task_number": 1,
     "selected_concept_id": 2
   }
   ```

### Testing on Heroku

Replace `localhost:8000` with your Heroku app URL:
```
https://your-app-name.herokuapp.com
```

## 🗄️ Database Schema

### Tables

1. **sessions**
   - `id` (String, Primary Key): Session identifier
   - `byo_config` (JSON): BYO configuration attributes
   - `utilities` (JSON): Estimated utilities

2. **screening_tasks**
   - `id` (Integer, Primary Key): Task identifier
   - `session_id` (String, Foreign Key): Reference to session
   - `concept` (JSON): Concept attributes
   - `position` (Integer): Task position
   - `response` (Boolean): User response

3. **tournament_tasks**
   - `id` (Integer, Primary Key): Task identifier
   - `session_id` (String, Foreign Key): Reference to session
   - `task_number` (Integer): Tournament task number
   - `concepts` (JSON): Available concepts
   - `choice` (Integer): Selected concept ID

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `sqlite+aiosqlite:///./acbc.db` |
| `DEBUG` | Enable debug mode | `True` |
| `SECRET_KEY` | Application secret key | `your-secret-key-here` |

### Database Configuration

The API supports both PostgreSQL (recommended) and SQLite:

- **PostgreSQL**: `postgresql+asyncpg://user:password@host:port/database`
- **SQLite**: `sqlite+aiosqlite:///./acbc.db`
- **Heroku**: Automatically configured via `DATABASE_URL`

## 🚨 Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid parameters or malformed requests
- **404 Not Found**: Session or resource not found
- **500 Internal Server Error**: Server-side errors

### Common Error Scenarios

1. **Session not found**: Ensure the session_id exists
2. **Invalid JSON**: Check request body format
3. **Database connection**: Verify PostgreSQL is running
4. **Missing parameters**: Provide all required parameters

## 🔄 Development

### Adding New Features

1. **Models**: Add to `app/models.py`
2. **Schemas**: Add to `app/schemas.py`
3. **Services**: Add business logic to `app/services.py`
4. **Routes**: Add endpoints to appropriate router in `app/routers/`

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Style

The project follows PEP 8 standards and uses:
- **Black** for code formatting
- **Type hints** for better code quality
- **Docstrings** for documentation

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions or issues, please create an issue in the repository or contact the development team.

---

**ACBC API** - Adaptive Choice-Based Conjoint Analysis Backend Service 