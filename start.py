import os
import sys
import uvicorn

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    
    port = int(os.getenv("PORT", 8000))
    
    if os.path.exists("app/main.py"):
        app_module = "app.main:app"
    elif os.path.exists("backend/app/main.py"):
        app_module = "backend.app.main:app"
    else:
        app_module = "app.main:app"
        
    print(f"[RENDER] Launching FastAPI on 0.0.0.0:{port} (Module: {app_module})...", flush=True)
    uvicorn.run(app_module, host="0.0.0.0", port=port, log_level="info")
