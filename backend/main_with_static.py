"""
Compass backend with static file serving.
This allows running frontend + backend from one command.
"""
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import the main app
from main import app

# Path to frontend build
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"

# Mount static files if they exist
if frontend_dist.exists():
    # Serve static assets
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    # Serve index.html for all other routes (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend for all non-API routes."""
        # API routes are already handled, this catches everything else
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            # Let FastAPI handle API routes
            return

        # Serve index.html for frontend routes
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(index_path)

        # If no index.html, return 404
        return {"error": "Frontend not built. Run: cd frontend && npm run build"}

def run_server():
    """Run the server."""
    import uvicorn

    if frontend_dist.exists():
        print("✅ Serving frontend from /")
        print("✅ API endpoints at /api/*")
    else:
        print("⚠️  Frontend not built. API only mode.")
        print("   To build: cd frontend && npm run build")

    print("\nStarting Compass server...")
    uvicorn.run("main_with_static:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run_server()
