# ACBC (Adaptive Choice-Based Conjoint) API

A FastAPI-based backend service for implementing Adaptive Choice-Based Conjoint analysis. This API provides endpoints for BYO (Build-Your-Own) configuration, screening tasks, and tournament-based choice experiments.

## 🌐 Live API

**Production URL:** `https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com`

**Interactive Documentation:** `https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/docs`

**API Documentation:** [API.md](./API.md)

## 📊 Monitoring Dashboard

**Dashboard Features:**
- **Real-time API Monitoring**: Live tracking of API health, requests, and performance
- **Visual Analytics**: Charts for endpoint usage and status code distribution
- **Error Tracking**: Comprehensive error logging with stack traces
- **Session Analytics**: User session tracking and completion rates
- **Traffic Analysis**: Traffic sources and user agent tracking
- **Auto-refresh**: 30-second automatic data updates

**Dashboard Setup:**
```bash
cd dashboard
pip install -r requirements.txt
python generate_sample_data.py  # Optional: Generate demo data
python app.py
```
Then open `http://localhost:5000` in your browser.

**Dashboard Documentation:** [dashboard/README.md](./dashboard/README.md)

## 🏗️ Architecture Overview

The ACBC API follows a modular architecture with clear separation of concerns:

```
ACBC/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── database.py          # Database configuration and async session management
│   │   ├── models.py            # SQLAlchemy database models
│   │   ├── schemas.py           # Pydantic schemas for request/response validation
│   │   ├── services.py          # Business logic and service layer
│   │   ├── utils.py             # Utility functions for design generation
│   │   └── routers/
│   │       ├── byo.py           # BYO configuration endpoints
│   │       ├── screening.py     # Screening task endpoints
│   │       └── tournament.py    # Tournament choice endpoints
│   ├── alembic/                 # Database migrations
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment configuration
├── dashboard/                   # Monitoring dashboard
│   ├── app.py                   # Flask dashboard application
│   ├── templates/               # HTML templates
│   ├── monitor_middleware.py    # FastAPI monitoring middleware
│   ├── generate_sample_data.py  # Sample data generator
│   └── requirements.txt         # Dashboard dependencies
├── requirements.txt             # Root requirements for Heroku
├── Procfile                     # Heroku process configuration
├── runtime.txt                  # Python version specification
├── app.json                     # Heroku app configuration
├── deploy.sh                    # Automated deployment script
├── API.md                       # Comprehensive API documentation
└── README.md                    # This file
```

## 🚀 Features

- **BYO Configuration**: Set up custom attributes and levels for conjoint analysis
- **Screening Tasks**: Generate and manage initial screening tasks
- **Tournament Choices**: Adaptive choice-based conjoint with utility updates
- **Async Database**: PostgreSQL with asyncpg for high performance
- **Automatic Migrations**: Alembic for database schema management
- **Robust Error Handling**: Comprehensive error handling for malformed requests
- **Heroku Ready**: Production-ready deployment configuration
- **Complete API Documentation**: Interactive docs and comprehensive guides
- **Real-time Monitoring**: Comprehensive dashboard for API activity tracking
- **Visual Analytics**: Charts and graphs for performance insights

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

### Current Deployment Status

✅ **Successfully Deployed** to Heroku  
✅ **PostgreSQL Database** configured and running  
✅ **Database Migrations** applied  
✅ **All API Endpoints** tested and working  

**Live Application:** `https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com`

### Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)
3. **Payment Verification**: Required for PostgreSQL addon (Essential 0 plan: ~$5/month)

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
   heroku addons:create heroku-postgresql:essential-0
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

## 🧪 Testing the API

### Quick Test with curl

#### 1. Health Check
```bash
curl https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/
```

#### 2. Create BYO Configuration
```bash
curl -X POST "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/byo-config" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "selected_attributes": {
      "brand": ["Nike", "Adidas", "Puma"],
      "material": ["leather", "canvas", "synthetic"],
      "style": ["casual", "athletic", "formal"]
    }
  }'
```

#### 3. Get Screening Design
```bash
curl "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/screening/design?session_id=test123"
```

### Using Postman

1. Import the API collection from the examples in [API.md](./API.md)
2. Set the base URL to: `https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com`
3. Test each endpoint sequentially

## 📚 API Documentation

### Complete Documentation

- **[API.md](./API.md)**: Comprehensive API documentation with examples
- **[Interactive Docs](https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/docs)**: Swagger UI for real-time testing

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check and API info |
| GET | `/health` | Health check for Heroku |
| POST | `/api/byo-config` | Create BYO configuration |
| GET | `/api/screening/design` | Get screening design |
| POST | `/api/screening/responses` | Submit screening responses |
| GET | `/api/tournament/choice` | Get tournament choice tasks |
| POST | `/api/tournament/choice-response` | Submit choice response |

## 🔧 Development

### Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app configuration
│   ├── database.py          # Database setup and session management
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic validation schemas
│   ├── services.py          # Business logic layer
│   ├── utils.py             # Utility functions
│   └── routers/             # API route handlers
│       ├── byo.py           # BYO configuration routes
│       ├── screening.py     # Screening task routes
│       └── tournament.py    # Tournament choice routes
├── alembic/                 # Database migration files
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

### Database Schema

The application uses the following main tables:

- **`sessions`**: Stores BYO configurations and session data
- **`screening_tasks`**: Stores screening task concepts and responses
- **`tournament_tasks`**: Stores tournament choice tasks and responses

### Key Features

- **Async Database Operations**: All database operations are asynchronous
- **Automatic Migration Management**: Alembic handles schema changes
- **Robust Error Handling**: Comprehensive error responses
- **Input Validation**: Pydantic schemas ensure data integrity
- **Adaptive Learning**: Utility estimates update based on user choices

## 🚀 Performance & Scalability

- **Async Architecture**: Non-blocking I/O operations
- **Database Connection Pooling**: Efficient database connections
- **Stateless Design**: Each request is independent
- **Heroku Optimization**: Configured for Heroku's ephemeral filesystem

## 🔒 Security Considerations

- **Input Validation**: All inputs validated with Pydantic
- **SQL Injection Protection**: SQLAlchemy ORM prevents injection
- **Environment Variables**: Sensitive data stored in environment variables
- **CORS Configuration**: Configurable CORS settings for production

## 📊 Monitoring & Logging

- **Health Check Endpoints**: `/` and `/health` for monitoring
- **Error Logging**: Comprehensive error handling and logging
- **Database Monitoring**: Alembic migration tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

1. Check the [API Documentation](./API.md)
2. Visit the [Interactive Docs](https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/docs)
3. Review the error messages in the API responses
4. Check the deployment logs: `heroku logs --tail`

## 📈 Future Enhancements

- [ ] Authentication and authorization
- [ ] Rate limiting
- [ ] Advanced analytics endpoints
- [ ] Export functionality for results
- [ ] Real-time collaboration features
- [ ] Mobile app support 