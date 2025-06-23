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
APP_NAME="acbc-api-$(date +%Y%m%d-%H%M%S)"
echo "📦 Creating Heroku app: $APP_NAME"
heroku create $APP_NAME

# Add PostgreSQL addon (Essential 0 plan - ~$5/month)
echo "🗄️ Adding PostgreSQL addon (Essential 0 plan)..."
heroku addons:create heroku-postgresql:essential-0

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

# Test the API
echo "🧪 Testing the API..."
echo "📊 Health check: https://$APP_NAME.herokuapp.com/"
echo "📚 API Documentation: https://$APP_NAME.herokuapp.com/docs"

# Open the application
echo "🌐 Opening the application..."
heroku open

echo "✅ Deployment complete!"
echo ""
echo "🎉 Your ACBC API is now live!"
echo "📊 API URL: https://$APP_NAME.herokuapp.com"
echo "📚 Interactive Docs: https://$APP_NAME.herokuapp.com/docs"
echo "💚 Health Check: https://$APP_NAME.herokuapp.com/health"
echo ""
echo "🧪 Quick Test:"
echo "curl https://$APP_NAME.herokuapp.com/"
echo ""
echo "📖 For complete API documentation, see: API.md"
echo "💰 PostgreSQL plan: Essential 0 (~$5/month)" 