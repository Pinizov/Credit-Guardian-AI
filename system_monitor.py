"""
System Health Monitor and Auto-Restart

Monitors system health and automatically restarts services if needed.
Ensures the system runs independently and reliably (Самостоятелно и ВЯРНО).
"""
import os
import time
import logging
import subprocess
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
import os
log_dir = os.getenv("LOG_DIR", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "system_monitor.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))  # seconds
MAX_FAILURES = int(os.getenv("MAX_FAILURES", "3"))
RESTART_DELAY = int(os.getenv("RESTART_DELAY", "5"))  # seconds


class SystemMonitor:
    """Monitor system health and auto-restart services."""
    
    def __init__(self):
        self.failure_count = 0
        self.last_health_check = None
        self.running = True
    
    def check_api_health(self) -> bool:
        """Check if API is healthy."""
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "healthy"
        except Exception as e:
            logger.warning(f"API health check failed: {e}")
        return False
    
    def check_api_readiness(self) -> bool:
        """Check if API is ready (database connected)."""
        try:
            response = requests.get(f"{API_URL}/readiness", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "ready"
        except Exception as e:
            logger.warning(f"API readiness check failed: {e}")
        return False
    
    def check_ollama_health(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
        return False
    
    def check_database_health(self) -> bool:
        """Check database connection."""
        try:
            import requests
            api_url = os.getenv("API_URL", "http://localhost:8000")
            response = requests.get(f"{api_url}/readiness", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("database") == "connected"
            return False
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "api": {
                "health": self.check_api_health(),
                "readiness": self.check_api_readiness(),
            },
            "ollama": {
                "health": self.check_ollama_health(),
            },
            "database": {
                "health": self.check_database_health(),
            },
            "overall": "healthy"
        }
        
        # Determine overall status
        if not all([
            status["api"]["health"],
            status["api"]["readiness"],
            status["database"]["health"]
        ]):
            status["overall"] = "degraded"
        
        if not status["ollama"]["health"]:
            status["overall"] = "degraded"  # Ollama is optional but recommended
        
        return status
    
    def restart_api(self):
        """Restart the API server."""
        logger.info("Restarting API server...")
        try:
            # This would depend on how you're running the server
            # For uvicorn, you might use systemd, supervisor, or a process manager
            # For now, we'll just log the action
            logger.info("API restart requested (implement based on your deployment)")
            # Example: subprocess.run(["systemctl", "restart", "credit-guardian-api"])
        except Exception as e:
            logger.error(f"Failed to restart API: {e}")
    
    def monitor_loop(self):
        """Main monitoring loop."""
        logger.info("Starting system monitor...")
        
        while self.running:
            try:
                status = self.get_system_status()
                self.last_health_check = datetime.utcnow()
                
                if status["overall"] == "healthy":
                    self.failure_count = 0
                    logger.debug("System health: ✓ All systems operational")
                else:
                    self.failure_count += 1
                    logger.warning(f"System health: ✗ Degraded (failures: {self.failure_count})")
                    
                    # Check if we need to restart
                    if self.failure_count >= MAX_FAILURES:
                        logger.error("Maximum failures reached. Restarting services...")
                        self.restart_api()
                        self.failure_count = 0
                        time.sleep(RESTART_DELAY)
                
                # Log status periodically
                if self.failure_count == 0 or self.failure_count % 10 == 0:
                    logger.info(f"System status: {status['overall']}")
                    logger.info(f"  API: {'✓' if status['api']['health'] else '✗'}")
                    logger.info(f"  Database: {'✓' if status['database']['health'] else '✗'}")
                    logger.info(f"  Ollama: {'✓' if status['ollama']['health'] else '✗'}")
                
            except KeyboardInterrupt:
                logger.info("Monitor stopped by user")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(HEALTH_CHECK_INTERVAL)
            
            time.sleep(HEALTH_CHECK_INTERVAL)
    
    def stop(self):
        """Stop the monitor."""
        self.running = False


def main():
    """Run the system monitor."""
    monitor = SystemMonitor()
    try:
        monitor.monitor_loop()
    except KeyboardInterrupt:
        logger.info("Stopping monitor...")
        monitor.stop()


if __name__ == "__main__":
    main()

