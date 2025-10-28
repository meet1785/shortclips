# Deployment Guide

## Deployment Options

### 1. Local Development

**Use Case:** Development and testing

**Setup:**
```bash
git clone https://github.com/meet1785/shortclips.git
cd shortclips
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python main.py
```

**Access:** http://localhost:8000

### 2. GitHub Codespaces (Recommended)

**Use Case:** Cloud development without local setup

**Steps:**
1. Open repository in GitHub
2. Click "Code" → "Codespaces" → "Create codespace"
3. Wait for environment setup
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with API keys
   ```
6. Run:
   ```bash
   python main.py
   ```

**Advantages:**
- No local installation needed
- Pre-configured environment
- Free tier available
- FFmpeg pre-installed

### 3. Docker Deployment

**Use Case:** Containerized deployment

**Build and Run:**
```bash
# Build image
docker build -t shortclips-ai .

# Run container
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e FREESOUND_API_KEY=your_key \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/outputs:/app/outputs \
  --name shortclips \
  shortclips-ai
```

**Docker Compose:**
```bash
# Create .env file first
docker-compose up -d
```

**Access:** http://localhost:8000

### 4. Cloud Platform Deployment

#### Heroku

**Prerequisites:**
- Heroku account
- Heroku CLI installed

**Setup:**
```bash
# Login
heroku login

# Create app
heroku create shortclips-ai

# Add buildpacks
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
heroku buildpacks:add --index 2 heroku/python

# Set environment variables
heroku config:set GEMINI_API_KEY=your_key
heroku config:set FREESOUND_API_KEY=your_key

# Deploy
git push heroku main

# Open app
heroku open
```

**Note:** Free tier has limitations on processing time and storage.

#### Railway.app

**Prerequisites:**
- Railway account

**Setup:**
1. Connect GitHub repository
2. Select `shortclips` repo
3. Add environment variables:
   - `GEMINI_API_KEY`
   - `FREESOUND_API_KEY`
4. Deploy automatically

**Access:** Provided by Railway

#### DigitalOcean App Platform

**Setup:**
1. Create account on DigitalOcean
2. Go to App Platform
3. Create new app from GitHub
4. Select repository
5. Configure:
   - Dockerfile detected automatically
   - Set environment variables
   - Choose instance size (Basic $5/mo recommended)
6. Deploy

**Access:** app-url.ondigitalocean.app

#### AWS EC2

**Setup:**
```bash
# Launch EC2 instance (Ubuntu 22.04)
# SSH into instance

# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and FFmpeg
sudo apt install python3 python3-pip ffmpeg git -y

# Clone repository
git clone https://github.com/meet1785/shortclips.git
cd shortclips

# Install dependencies
pip3 install -r requirements.txt

# Set up environment
cp .env.example .env
nano .env  # Edit with API keys

# Run with nohup
nohup python3 main.py > app.log 2>&1 &

# Or use systemd service (see below)
```

**Access:** http://ec2-public-ip:8000

### 5. Production Server (VPS)

**Use Case:** Self-hosted production deployment

**Requirements:**
- Ubuntu 20.04+ / CentOS 8+
- 4GB RAM minimum (8GB recommended)
- 50GB disk space
- Python 3.8+

**Setup Script:**
```bash
#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv ffmpeg git nginx

# Create user
sudo useradd -m -s /bin/bash shortclips
sudo su - shortclips

# Clone repository
git clone https://github.com/meet1785/shortclips.git
cd shortclips

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add API keys

# Exit to root
exit

# Create systemd service
sudo nano /etc/systemd/system/shortclips.service
```

**Systemd Service:**
```ini
[Unit]
Description=Short Clips AI
After=network.target

[Service]
User=shortclips
Group=shortclips
WorkingDirectory=/home/shortclips/shortclips
Environment="PATH=/home/shortclips/shortclips/venv/bin"
ExecStart=/home/shortclips/shortclips/venv/bin/python main.py

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable shortclips
sudo systemctl start shortclips
sudo systemctl status shortclips
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for video processing
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }

    # Increase max upload size
    client_max_body_size 500M;
}
```

**Enable Nginx:**
```bash
sudo ln -s /etc/nginx/sites-available/shortclips /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**SSL with Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Environment Variables

### Required
```env
GEMINI_API_KEY=your_gemini_api_key
```

### Optional
```env
FREESOUND_API_KEY=your_freesound_api_key
HOST=0.0.0.0
PORT=8000
MIN_CLIP_DURATION=15
MAX_CLIP_DURATION=60
TARGET_ASPECT_RATIO=9:16
OUTPUT_RESOLUTION=1080x1920
```

## Security Best Practices

### 1. API Key Management
```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use secrets management
# AWS: AWS Secrets Manager
# Azure: Azure Key Vault
# GCP: Secret Manager
```

### 2. Rate Limiting
```python
# Add to main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/process")
@limiter.limit("5/hour")
async def process_video(...):
    ...
```

### 3. Authentication
```python
# Add API key authentication
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = "your-secret-api-key"
api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.post("/process")
async def process_video(request: VideoProcessRequest, 
                        api_key: str = Depends(get_api_key)):
    ...
```

### 4. File Upload Security
```python
# Validate file types
ALLOWED_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

def validate_file(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Invalid file type")
```

### 5. Resource Limits
```python
# Limit processing queue
MAX_CONCURRENT_JOBS = 3
processing_queue = Queue(maxsize=MAX_CONCURRENT_JOBS)

# Limit file size
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
```

## Monitoring

### 1. Logging
```python
# Configure logging in main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 2. Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": __version__,
    }
```

### 3. Metrics
```python
# Add Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## Scaling

### Horizontal Scaling
```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shortclips
spec:
  replicas: 3
  selector:
    matchLabels:
      app: shortclips
  template:
    metadata:
      labels:
        app: shortclips
    spec:
      containers:
      - name: shortclips
        image: shortclips-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: gemini
```

### Load Balancing
```nginx
upstream shortclips {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://shortclips;
    }
}
```

## Backup and Recovery

### Backup Strategy
```bash
# Backup outputs directory
tar -czf outputs-$(date +%Y%m%d).tar.gz outputs/

# Upload to S3
aws s3 cp outputs-*.tar.gz s3://your-bucket/backups/
```

### Database (if added)
```bash
# Backup PostgreSQL
pg_dump shortclips > backup.sql

# Restore
psql shortclips < backup.sql
```

## Troubleshooting

### Check Logs
```bash
# Systemd
sudo journalctl -u shortclips -f

# Docker
docker logs -f shortclips

# File
tail -f app.log
```

### Restart Service
```bash
# Systemd
sudo systemctl restart shortclips

# Docker
docker restart shortclips

# PM2
pm2 restart shortclips
```

### Check Resource Usage
```bash
# CPU and Memory
top
htop

# Disk
df -h
du -sh outputs/

# Network
netstat -tulpn | grep 8000
```

## Production Checklist

- [ ] Environment variables configured
- [ ] FFmpeg installed
- [ ] Dependencies installed
- [ ] Service configured (systemd/docker)
- [ ] Reverse proxy setup (nginx)
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Rate limiting enabled
- [ ] Authentication added
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] Backups scheduled
- [ ] Documentation updated
- [ ] Testing completed

## Cost Estimation

### Self-Hosted (VPS)
- **Server**: $10-40/month (4-8GB RAM)
- **Domain**: $10-15/year
- **SSL**: Free (Let's Encrypt)
- **API (Gemini)**: Free tier
- **Total**: ~$10-40/month

### Cloud Platform
- **Railway/Render**: $5-20/month
- **AWS EC2**: $10-50/month
- **DigitalOcean**: $5-40/month
- **API costs**: Free tier (Gemini)
- **Total**: $5-50/month

### Serverless (Future)
- Pay per processing time
- $0.01-0.10 per video processed
- Cost-effective for low volume

## Support

- Documentation: See README.md
- Issues: GitHub Issues
- Community: GitHub Discussions

---

For production deployment, always test thoroughly before going live!
