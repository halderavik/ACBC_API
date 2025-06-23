# ACBC Dashboard Deployment Guide

This guide covers deploying the ACBC API Dashboard to various hosting platforms.

## 🚀 Quick Deploy Options

### 1. Render (Recommended - Free)

**Steps:**
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the `dashboard` directory
5. Configure:
   - **Name**: `acbc-dashboard`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
6. Click "Create Web Service"

**Environment Variables:**
- `API_BASE_URL`: Your ACBC API URL
- `PORT`: 5000 (auto-set by Render)

**Cost**: Free tier (750 hours/month)

---

### 2. Railway (Free with $5 credit)

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository and `dashboard` directory
5. Railway will auto-detect Python and deploy

**Environment Variables:**
- `API_BASE_URL`: Your ACBC API URL

**Cost**: Free with $5 monthly credit

---

### 3. Fly.io (Free Tier)

**Steps:**
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Deploy: `fly launch` (in dashboard directory)
4. Follow prompts

**Cost**: Free tier (3 shared-cpu VMs)

---

### 4. Heroku (Same as your API)

**Steps:**
1. Create new Heroku app: `heroku create acbc-dashboard`
2. Deploy: `git push heroku main`
3. Set environment variables:
   ```bash
   heroku config:set API_BASE_URL=https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com
   ```

**Cost**: $5/month (Basic dyno)

---

### 5. DigitalOcean App Platform ($5/month)

**Steps:**
1. Go to [digitalocean.com](https://digitalocean.com)
2. Create App Platform project
3. Connect GitHub repository
4. Select `dashboard` directory
5. Configure build settings

**Cost**: $5/month

---

## 🐳 Docker Deployment

### Using Dockerfile

```bash
# Build image
docker build -t acbc-dashboard .

# Run container
docker run -p 5000:5000 -e API_BASE_URL=https://your-api-url.com acbc-dashboard
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  dashboard:
    build: .
    ports:
      - "5000:5000"
    environment:
      - API_BASE_URL=https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com
    volumes:
      - ./data:/app/data
```

Run: `docker-compose up -d`

---

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | Your ACBC API URL | `https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com` |
| `DB_PATH` | Database file path | `api_monitor.db` |
| `PORT` | Server port | `5000` |

---

## 📊 Database Considerations

### SQLite (Default)
- **Pros**: Simple, no setup required
- **Cons**: Not suitable for high traffic, data lost on restart
- **Best for**: Development, testing, low traffic

### PostgreSQL (Production)
For production use, consider switching to PostgreSQL:

1. **Add PostgreSQL dependency:**
   ```bash
   pip install psycopg2-binary
   ```

2. **Update database connection:**
   ```python
   # In app.py
   DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///api_monitor.db")
   ```

3. **Use with hosting platforms that provide PostgreSQL:**
   - Render (PostgreSQL addon)
   - Railway (built-in PostgreSQL)
   - Heroku (PostgreSQL addon)

---

## 🔒 Security Considerations

### For Production Deployment

1. **Add Authentication:**
   ```python
   # Add basic auth
   from flask_httpauth import HTTPBasicAuth
   auth = HTTPBasicAuth()
   ```

2. **Environment Variables:**
   - Never commit sensitive data
   - Use platform-specific secret management

3. **HTTPS:**
   - Most platforms provide SSL automatically
   - Ensure API calls use HTTPS

4. **Rate Limiting:**
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app)
   ```

---

## 📈 Monitoring & Scaling

### Performance Monitoring
- Use platform-specific monitoring tools
- Monitor database size and performance
- Set up alerts for errors

### Scaling Considerations
- **Horizontal Scaling**: Use load balancers
- **Database Scaling**: Consider managed databases
- **Caching**: Add Redis for session storage

---

## 🆘 Troubleshooting

### Common Issues

1. **Port Issues:**
   - Ensure `PORT` environment variable is set
   - Use `0.0.0.0` as host for containerized deployments

2. **Database Issues:**
   - Check file permissions
   - Ensure database directory is writable

3. **API Connection Issues:**
   - Verify `API_BASE_URL` is correct
   - Check CORS settings on your API

4. **Memory Issues:**
   - Monitor database size
   - Implement data retention policies

### Logs
- Check platform-specific logs
- Use `heroku logs --tail` for Heroku
- Use `fly logs` for Fly.io

---

## 💰 Cost Comparison

| Platform | Cost | Best For |
|----------|------|----------|
| **Render** | Free | Small projects, testing |
| **Railway** | Free ($5 credit) | Quick deployment |
| **Fly.io** | Free | Global performance |
| **Heroku** | $5/month | Production, familiar |
| **DigitalOcean** | $5/month | Production, managed |

---

## 🎯 Recommendation

**For your use case, I recommend:**

1. **Start with Render** (Free) - Easy setup, good for testing
2. **Move to Railway** if you need more features
3. **Consider Heroku** if you want to keep everything on one platform

All options will work well with your existing ACBC API! 