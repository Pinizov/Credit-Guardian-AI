import time
import uvicorn


def run_server():
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False, log_level="info")


if __name__ == "__main__":
    while True:
        try:
            run_server()
            break  # normal shutdown
        except Exception as e:
            print(f"Server crashed: {e}. Restarting in 3s...")
            time.sleep(3)
