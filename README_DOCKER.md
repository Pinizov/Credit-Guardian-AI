# 🐳 Docker Deployment - Credit Guardian AI

## Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access services
# Frontend: http://localhost:3000
# API: http://localhost:8080
# API Docs: http://localhost:8080/docs
```

## What's Included

✅ **PostgreSQL Database** - With connection pooling and health checks  
✅ **Ollama AI Server** - Local LLM (llama3.2 model)  
✅ **FastAPI Backend** - With auto-restart and reliability features  
✅ **Nginx Frontend** - Static HTML with API proxy  
✅ **System Monitor** - Health monitoring (optional)  

## Features

- 🔄 **Auto-restart** on failures
- 💾 **Connection pooling** (20 connections)
- 🔍 **Health checks** for all services
- 📊 **Monitoring** and logging
- 🚀 **Production-ready** configuration

## Documentation

- **Quick Start**: [QUICK_START_DOCKER.md](QUICK_START_DOCKER.md)
- **Full Guide**: [DOCKER_SETUP.md](DOCKER_SETUP.md)
- **System Improvements**: [SYSTEM_IMPROVEMENTS.md](SYSTEM_IMPROVEMENTS.md)

## Requirements

- Docker & Docker Compose
- 4GB+ RAM
- 10GB+ disk space (for Ollama models)

---

**Ready to deploy!** 🚀

