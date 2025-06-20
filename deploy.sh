#!/bin/bash

# Heroku Deployment Script for ACBC API

echo "🚀 Starting Heroku deployment for ACBC API..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Not logged in to Heroku. Please run: heroku login"
    exit 1
fi

# Create Heroku app (if it doesn't exist)
APP_NAME="acbc-api-$(date +%s)"
echo "📦 Creating Heroku app: $APP_NAME"
heroku create $APP_NAME

# Add PostgreSQL addon
echo "🗄️ Adding PostgreSQL addon..."
heroku addons:create heroku-postgresql:mini

# Set environment variables
echo "⚙️ Setting environment variables..."
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
heroku config:set DEBUG=False

# Deploy the application
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Run database migrations
echo "🗄️ Running database migrations..."
heroku run alembic upgrade head

# Open the application
echo "🌐 Opening the application..."
heroku open

echo "✅ Deployment complete!"
echo "📊 Your API is now live at: https://$APP_NAME.herokuapp.com"
echo "📚 API Documentation: https://$APP_NAME.herokuapp.com/docs"
echo "💚 Health Check: https://$APP_NAME.herokuapp.com/health" 