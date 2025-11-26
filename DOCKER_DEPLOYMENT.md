# 🐳 Credit Guardian - Docker Deployment Guide

## Quick Start

### Option 1: CPU-only (Recommended for most users)

```powershell
# Windows
.\deploy.ps1

# Linux/Mac
chmod +x deploy.sh
./deploy.sh
```

### Option 2: With GPU Acceleration

```powershell
# Windows (requires NVIDIA GPU + Docker with GPU support)
.\deploy.ps1 -GPU

# Linux/Mac
./deploy.sh --gpu
```

## Prerequisites

1. **Docker Desktop** installed and running
2. **8GB+ RAM** recommended (Ollama needs memory for LLM)
3. **(Optional) NVIDIA GPU** with Docker GPU support for faster inference

## Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React web app |
| API | 8080 | FastAPI backend |
| Ollama | 11434 | Local LLM server |
| PostgreSQL | 5432 | Database |

## Access Points

After deployment:

- 🌐 **Frontend**: http://localhost:3000
- 📡 **API**: http://localhost:8080
- 📚 **API Docs**: http://localhost:8080/docs
- 🤖 **Ollama**: http://localhost:11434

## Commands

### PowerShell (Windows)

```powershell
# Start (CPU mode)
.\deploy.ps1

# Start (GPU mode)
.\deploy.ps1 -GPU

# Rebuild and start
.\deploy.ps1 -Build

# View all logs
.\deploy.ps1 -Logs

# View specific service logs
.\deploy.ps1 -Logs -Service api

# Check status
.\deploy.ps1 -Status

# Stop everything
.\deploy.ps1 -Down
```

### Bash (Linux/Mac)

```bash
# Start (CPU mode)
./deploy.sh

# Start (GPU mode)
./deploy.sh --gpu

# Rebuild and start
./deploy.sh --build

# View logs
./deploy.sh --logs

# View specific service
./deploy.sh --logs --service api

# Status
./deploy.sh --status

# Stop
./deploy.sh --down
```

### Direct Docker Commands

```bash
# CPU mode
docker-compose -f docker-compose.cpu.yml up -d

# GPU mode
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose -f docker-compose.cpu.yml logs -f

# Stop
docker-compose -f docker-compose.cpu.yml down

# Rebuild
docker-compose -f docker-compose.cpu.yml build --no-cache
```

## Testing Ollama

```bash
# List available models
docker exec cg_ollama ollama list

# Test the model
docker exec cg_ollama ollama run llama3.2 "Какъв е максималният ГПР по закон?"

# Pull a different model
docker exec cg_ollama ollama pull mistral
```

## Environment Variables

The Docker setup uses these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_PROVIDER` | ollama | "ollama" or "perplexity" |
| `OLLAMA_URL` | http://ollama:11434 | Ollama server URL |
| `OLLAMA_MODEL` | llama3.2 | Model to use |
| `PERPLEXITY_API_KEY` | - | Perplexity API key |
| `DATABASE_URL` | (set in compose) | PostgreSQL connection |

### Using Perplexity Instead of Ollama

Edit `docker-compose.yml` or `docker-compose.cpu.yml`:

```yaml
api:
  environment:
    AI_PROVIDER: perplexity
    PERPLEXITY_API_KEY: ${PERPLEXITY_API_KEY}
```

Then set the env var:

```powershell
$env:PERPLEXITY_API_KEY = "pplx-your-key"
.\deploy.ps1
```

## Troubleshooting

### Ollama model not loading

```bash
# Check Ollama logs
docker logs cg_ollama_pull

# Manually pull the model
docker exec cg_ollama ollama pull llama3.2
```

### API not connecting to Ollama

```bash
# Test Ollama from API container
docker exec cg_api curl http://ollama:11434/api/tags
```

### Out of memory

Ollama needs ~4-8GB RAM depending on the model. Try:

1. Use a smaller model: `llama3.2:1b`
2. Increase Docker memory limit
3. Close other applications

### Database connection issues

```bash
# Check PostgreSQL
docker logs cg_postgres

# Reset database
docker-compose -f docker-compose.cpu.yml down -v
docker-compose -f docker-compose.cpu.yml up -d
```

## Production Deployment

For production, consider:

1. **Use a managed PostgreSQL** (e.g., Render, AWS RDS)
2. **Use Perplexity API** instead of local Ollama (faster, more reliable)
3. **Add HTTPS** with a reverse proxy (nginx, Traefik)
4. **Set proper secrets** (don't use default passwords)

### Production docker-compose override

Create `docker-compose.prod.yml`:

```yaml
version: "3.9"
services:
  api:
    environment:
      AI_PROVIDER: perplexity
      PERPLEXITY_API_KEY: ${PERPLEXITY_API_KEY}
      DATABASE_URL: ${DATABASE_URL}
    restart: always
  
  frontend:
    restart: always
```

Run with:

```bash
docker-compose -f docker-compose.cpu.yml -f docker-compose.prod.yml up -d
```

## Resource Requirements

| Service | Min RAM | Recommended RAM | CPU |
|---------|---------|-----------------|-----|
| Ollama (llama3.2) | 4GB | 8GB | 4 cores |
| API | 256MB | 512MB | 1 core |
| Frontend | 64MB | 128MB | 0.5 cores |
| PostgreSQL | 256MB | 512MB | 1 core |
| **Total** | **~5GB** | **~10GB** | 6 cores |

## GPU Support (Optional)

For NVIDIA GPU acceleration:

1. Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
2. Use `docker-compose.yml` (not `.cpu.yml`)
3. Run with `-GPU` flag

GPU provides 5-10x faster inference for Ollama.

---

**Happy deploying! 🚀**

