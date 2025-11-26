# 🚀 Running Frontend with Live Server (Go Live)

## Quick Start - Frontend with Live Server + Docker Backend

### Step 1: Start Docker Backend

```powershell
# Start only backend services (database, API, Ollama)
docker-compose up -d db ollama api

# Verify API is running
curl http://localhost:8080/health
```

### Step 2: Open Frontend with Live Server

1. **Open VS Code**
2. **Open the file**: `frontend/index.html`
3. **Right-click** on the file
4. **Select**: "Open with Live Server" (or click "Go Live" in status bar)

The frontend will automatically:
- ✅ Detect you're using Live Server (port 5500)
- ✅ Connect to Docker API on port 8080
- ✅ Work with all features

### Alternative: Manual Server

If you don't have Live Server extension:

```powershell
# Navigate to frontend directory
cd frontend

# Start Python HTTP server
python -m http.server 5500

# Or use Node.js http-server
npx http-server -p 5500
```

Then open: http://localhost:5500

## 🔧 Configuration

The frontend automatically detects the environment:

| Frontend Port | API URL | Environment |
|--------------|---------|-------------|
| 5500-5502 | http://localhost:8080 | Live Server + Docker |
| 3000 | http://localhost:8080 | Docker Frontend |
| 8000 | http://localhost:8000 | Local Development |
| Other | http://localhost:8080 | Default (Docker) |

## ✅ Verify Connection

Open browser console (F12) and check:
```
API Base URL: http://localhost:8080 (detected from port: 5500)
```

## 🐛 Troubleshooting

### CORS Errors

If you see CORS errors, make sure:
1. Docker API is running: `docker-compose ps`
2. API is accessible: `curl http://localhost:8080/health`
3. Check browser console for errors

### API Not Responding

```powershell
# Check Docker services
docker-compose ps

# Check API logs
docker-compose logs api

# Restart API
docker-compose restart api
```

### Wrong API URL

If frontend connects to wrong API:
1. Check browser console for detected API URL
2. Manually edit `frontend/index.html` line ~348:
   ```javascript
   const API_BASE = 'http://localhost:8080';  // Force Docker API
   ```

## 📋 Complete Setup

### Option 1: Live Server (Recommended for Development)

```powershell
# 1. Start Docker backend
docker-compose up -d db ollama api

# 2. Open frontend/index.html in VS Code
# 3. Click "Go Live" or right-click -> "Open with Live Server"
# 4. Frontend opens on http://localhost:5500
# 5. Automatically connects to http://localhost:8080 (Docker API)
```

### Option 2: Docker Frontend

```powershell
# Start everything in Docker
docker-compose up -d

# Frontend: http://localhost:3000
# API: http://localhost:8080
```

### Option 3: Everything Local

```powershell
# Start local API
python start_server.py

# Open frontend/index.html with Live Server
# Frontend detects port 5500 -> connects to localhost:8000
```

## 🎯 Benefits of Live Server

- ✅ **Hot Reload**: Changes refresh automatically
- ✅ **Fast Development**: No Docker rebuild needed
- ✅ **Easy Debugging**: Direct file access
- ✅ **Flexible**: Works with any editor

## 📝 Notes

- Live Server typically uses port 5500, 5501, or 5502
- Frontend automatically detects Live Server ports
- Backend must be running in Docker (port 8080) or locally (port 8000)
- All API calls go through the detected API URL

---

**Ready to develop!** 🎉

