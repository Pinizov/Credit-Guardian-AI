# Docker Setup for WSL (Windows Subsystem for Linux)

## 🐛 Common WSL Docker Issues

### Issue: NVIDIA GPU Error in WSL

**Error Message:**
```
nvidia-container-cli: initialization error: WSL environment detected but no adapters were found
```

**Solution**: Use CPU-only mode (Ollama works fine on CPU, just slower)

## ✅ Quick Fix

### Option 1: Use CPU-Only Compose (Recommended for WSL)

```powershell
# Use CPU-only configuration
docker-compose -f docker-compose.yml -f docker-compose.cpu.yml up -d
```

### Option 2: Edit docker-compose.yml

The GPU section is already commented out in the latest version. If you still see the error:

1. Open `docker-compose.yml`
2. Find the `ollama` service
3. Make sure the `deploy` section is commented out or removed:

```yaml
ollama:
  image: ollama/ollama:latest
  # GPU section should be commented out:
  # deploy:
  #   resources:
  #     reservations:
  #       devices:
  #         - driver: nvidia
```

## 🚀 Start Services (WSL/CPU Mode)

```powershell
# Start all services without GPU
docker-compose up -d

# Or explicitly use CPU-only override
docker-compose -f docker-compose.yml -f docker-compose.cpu.yml up -d
```

## 📊 Verify Services

```powershell
# Check all services are running
docker-compose ps

# Check Ollama is working (CPU mode)
docker-compose logs ollama

# Test API
curl http://localhost:8080/health
```

## ⚡ Performance Notes

- **CPU Mode**: Ollama will use CPU (slower but works)
- **Recommended Model**: Use `llama3.2` (smaller, faster on CPU)
- **Response Time**: Expect 10-30 seconds per analysis (vs 2-5s with GPU)

## 🔧 If You Want GPU Support in WSL

1. **Install NVIDIA Drivers** on Windows
2. **Install WSL2 NVIDIA Driver**: https://developer.nvidia.com/cuda/wsl
3. **Install nvidia-container-toolkit** in WSL:
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```
4. **Uncomment GPU section** in `docker-compose.yml`

## ✅ Current Status

The `docker-compose.yml` file is now configured to work **without GPU by default**. The GPU section is commented out, so it will work on:
- ✅ WSL (Windows Subsystem for Linux)
- ✅ Mac (no GPU support)
- ✅ Linux without NVIDIA GPU
- ✅ Any system with Docker

---

**Ollama works great on CPU!** Just expect slightly slower response times. 🚀

