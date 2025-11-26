# Docker Setup Guide - Credit Guardian AI

## 🐳 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- Ollama model will be downloaded automatically (first run takes longer)

### Start All Services

```bash
# Start all services (database, Ollama, API, frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Access Services

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
- **Ollama**: http://localhost:11434
- **PostgreSQL**: localhost:5432

## 📋 Services

### 1. PostgreSQL Database
- **Container**: `cg_postgres`
- **Port**: 5432
- **Database**: `credit_guardian`
- **User**: `cg_user`
- **Password**: `cg_pass`
- **Volume**: `pgdata` (persistent storage)

### 2. Ollama (AI Server)
- **Container**: `cg_ollama`
- **Port**: 11434
- **Model**: `llama3.2` (auto-downloaded)
- **Volume**: `ollama_data` (model storage)

### 3. API Server
- **Container**: `cg_api`
- **Port**: 8080 (mapped from 8000)
- **Features**:
  - Connection pooling (20 connections)
  - Auto-restart on failures
  - Health checks
  - Database retry logic

### 4. Frontend (Nginx)
- **Container**: `cg_frontend`
- **Port**: 3000
- **Serves**: Static HTML with API proxy

### 5. System Monitor (Optional)
- **Container**: `cg_monitor`
- **Function**: Monitors system health
- **Logs**: `system_monitor.log`

## 🔧 Configuration

### Environment Variables

Edit `docker-compose.yml` or create `.env` file:

```bash
# Database
DATABASE_URL=postgresql+psycopg2://cg_user:cg_pass@db:5432/credit_guardian
DB_POOL_SIZE=20
DB_POOL_RECYCLE=3600

# AI
AI_PROVIDER=ollama
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2

# Server
PORT=8000
LOG_LEVEL=INFO
```

### Production Configuration

For production, use the production override:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

This enables:
- Higher connection pool (50 connections)
- Resource limits
- Better restart policies
- Optimized database settings

## 🚀 Common Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Volumes
```bash
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f db
docker-compose logs -f ollama
```

### Restart Service
```bash
docker-compose restart api
```

### Rebuild After Code Changes
```bash
docker-compose build api
docker-compose up -d api
```

### Run Database Migrations
```bash
docker-compose run --rm migrate
```

### Access Database
```bash
docker-compose exec db psql -U cg_user -d credit_guardian
```

### Access API Container
```bash
docker-compose exec api bash
```

## 🔍 Health Checks

### Check API Health
```bash
curl http://localhost:8080/health
curl http://localhost:8080/readiness
curl http://localhost:8080/api/health/detailed
```

### Check Database
```bash
docker-compose exec db pg_isready -U cg_user
```

### Check Ollama
```bash
curl http://localhost:11434/api/tags
```

## 📊 Monitoring

### View Container Stats
```bash
docker stats
```

### View System Monitor Logs
```bash
docker-compose logs -f monitor
```

### Check Service Status
```bash
docker-compose ps
```

## 🛠️ Troubleshooting

### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Check connection from API container
docker-compose exec api python -c "from database.connection import check_connection; print(check_connection())"
```

### Ollama Not Responding
```bash
# Check Ollama logs
docker-compose logs ollama

# Restart Ollama
docker-compose restart ollama

# Pull model manually
docker-compose exec ollama ollama pull llama3.2
```

### API Not Starting
```bash
# Check API logs
docker-compose logs api

# Rebuild API
docker-compose build --no-cache api
docker-compose up -d api
```

### Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs frontend

# Verify nginx config
docker-compose exec frontend nginx -t
```

### Port Conflicts
If ports are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8081:8000"  # Change 8080 to 8081
```

## 🔄 Updates

### Update Code
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose build api
docker-compose up -d api
```

### Update Database Schema
```bash
# Run migrations
docker-compose run --rm migrate
```

### Update Ollama Model
```bash
docker-compose exec ollama ollama pull llama3.2
```

## 💾 Backup & Restore

### Backup Database
```bash
docker-compose exec db pg_dump -U cg_user credit_guardian > backup.sql
```

### Restore Database
```bash
docker-compose exec -T db psql -U cg_user credit_guardian < backup.sql
```

### Backup Volumes
```bash
docker run --rm -v credit-guardian_pgdata:/data -v $(pwd):/backup alpine tar czf /backup/pgdata-backup.tar.gz /data
```

## 🎯 Production Deployment

1. **Use Production Compose**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

2. **Set Strong Passwords**:
   - Change `POSTGRES_PASSWORD` in `docker-compose.yml`
   - Use secrets management (Docker secrets, Kubernetes secrets, etc.)

3. **Enable SSL/TLS**:
   - Add reverse proxy (Traefik, Nginx) with SSL
   - Use Let's Encrypt for certificates

4. **Monitor Resources**:
   - Set up monitoring (Prometheus, Grafana)
   - Configure alerts
   - Monitor logs (ELK stack, Loki)

5. **Backup Strategy**:
   - Automated daily backups
   - Off-site backup storage
   - Test restore procedures

## 📝 Notes

- **First Run**: Ollama will download the model (~2GB), this takes time
- **GPU Support**: Remove GPU section from `docker-compose.yml` if no GPU available
- **Memory**: Ensure at least 4GB RAM for all services
- **Storage**: Ollama models require ~5GB disk space per model
- **Network**: Services communicate via Docker network (no external exposure needed)

## 🔐 Security

- Change default passwords in production
- Use Docker secrets for sensitive data
- Enable firewall rules
- Use HTTPS in production
- Regular security updates: `docker-compose pull && docker-compose up -d`

---

**Status**: ✅ Ready for Docker deployment with all reliability features

