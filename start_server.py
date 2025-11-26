"""
Reliable Server Startup with Auto-Restart

Ensures the system runs independently and reliably (Самостоятелно и ВЯРНО).
"""
import os
import time
import logging
import uvicorn
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all dependencies are available."""
    issues = []
    
    # Check database
    try:
        from database.connection import check_connection
        if not check_connection():
            issues.append("Database connection failed")
    except Exception as e:
        issues.append(f"Database error: {e}")
    
    # Check Ollama (optional but recommended)
    try:
        import requests
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if response.status_code != 200:
            issues.append("Ollama not responding (optional)")
    except:
        logger.warning("Ollama not available (optional, but recommended)")
    
    if issues:
        logger.warning(f"Dependency issues: {', '.join(issues)}")
    
    return len(issues) == 0


def run_server():
    """Run the FastAPI server."""
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting Credit Guardian API on {host}:{port}")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production for stability
        log_level="info",
        access_log=True,
        loop="asyncio",
        timeout_keep_alive=300,  # 5 minutes for long-running AI requests
        limit_concurrency=100,
        limit_max_requests=1000
    )


if __name__ == "__main__":
    # Check dependencies before starting
    if not check_dependencies():
        logger.warning("Some dependencies are unavailable, but continuing...")
    
    # Auto-restart loop for reliability
    max_restarts = int(os.getenv("MAX_RESTARTS", "10"))
    restart_count = 0
    restart_delay = int(os.getenv("RESTART_DELAY", "5"))
    
    while restart_count < max_restarts:
        try:
            run_server()
            break  # Normal shutdown
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
            break
        except Exception as e:
            restart_count += 1
            logger.error(f"Server crashed (restart {restart_count}/{max_restarts}): {e}")
            
            if restart_count >= max_restarts:
                logger.error("Maximum restart attempts reached. Exiting.")
                break
            
            logger.info(f"Restarting in {restart_delay} seconds...")
            time.sleep(restart_delay)
