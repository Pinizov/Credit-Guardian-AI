# 🐳 Quick Start - Docker Deployment

## One-Command Start

### Windows (PowerShell)
```powershell
.\docker-start.ps1
```

### Linux/Mac
```bash
chmod +x docker-start.sh
./docker-start.sh
```

### Manual Start
```bash
docker-compose up -d
```

## ✅ Verify Installation

1. **Check Services**:
   ```bash
   docker-compose ps
   ```

2. **Check Logs**:
   ```bash
   docker-compose logs -f
   ```

3. **Test API**:
   ```bash
   curl http://localhost:8080/health
   ```

4. **Open Frontend**:
   - Browser: http://localhost:3000

## 📋 Services

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| API | 8080 | http://localhost:8080 |
| API Docs | 8080 | http://localhost:8080/docs |
| Ollama | 11434 | http://localhost:11434 |
| PostgreSQL | 5432 | localhost:5432 |

## 🔧 Common Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f api

# Restart a service
docker-compose restart api

# Rebuild after code changes
docker-compose build api
docker-compose up -d api
```

## 🚨 Troubleshooting

### Port Already in Use
Change ports in `docker-compose.yml`:
```yaml
ports:
  - "8081:8000"  # Change 8080 to 8081
```

### Database Connection Error
```bash
docker-compose restart db
docker-compose logs db
```

### Ollama Model Not Loading
```bash
docker-compose exec ollama ollama pull llama3.2
```

### View All Logs
```bash
docker-compose logs -f
```

## 📚 Full Documentation

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for complete documentation.

---

**Ready to use!** 🎉

