#!/usr/bin/env python3
"""
🚀 Compass - One Command Startup
Run everything (backend + frontend) from ONE terminal!
"""
import subprocess
import sys
import os
from pathlib import Path
import time

def main():
    print("🚀 Starting Compass - All-in-One Server")
    print("=" * 60)

    # Get project root
    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend"
    backend_dir = project_root / "backend"

    # Step 1: Activate the new UI
    print("\n📱 Step 1: Activating new UI...")
    frontend_src = frontend_dir / "src"
    app_jsx = frontend_src / "App.jsx"
    app_redesigned = frontend_src / "App.redesigned.jsx"
    app_old = frontend_src / "App.old.jsx"

    if app_redesigned.exists() and not app_old.exists():
        # Backup old App.jsx
        print("   ✓ Backing up old App.jsx...")
        app_jsx.rename(app_old)
        # Activate new UI
        print("   ✓ Activating redesigned UI...")
        import shutil
        shutil.copy(app_redesigned, app_jsx)
        print("   ✅ New UI activated!")
    else:
        print("   ✓ New UI already activated")

    # Step 2: Build frontend
    print("\n🏗️  Step 2: Building frontend...")
    os.chdir(frontend_dir)

    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("   📦 Installing dependencies (first time only)...")
        subprocess.run(["npm", "install"], check=True)

    print("   🔨 Building production frontend...")
    result = subprocess.run(["npm", "run", "build"], capture_output=True, text=True)
    if result.returncode != 0:
        print("   ❌ Build failed!")
        print(result.stderr)
        sys.exit(1)
    print("   ✅ Frontend built successfully!")

    # Step 3: Check backend dependencies
    print("\n🔧 Step 3: Checking backend...")
    os.chdir(backend_dir)

    # Initialize database if needed
    print("   🗄️  Initializing database...")
    init_db_code = """
from database import init_db
try:
    init_db()
    print('   ✅ Database ready!')
except Exception as e:
    print(f'   ⚠️  Database already initialized: {e}')
"""
    subprocess.run([sys.executable, "-c", init_db_code])

    # Step 4: Start the all-in-one server
    print("\n🚀 Step 4: Starting Compass server...")
    print("=" * 60)
    print("\n✨ Compass is starting up...")
    print("\n📍 Open in your browser:")
    print("   👉 http://localhost:8000")
    print("\n🛑 Press Ctrl+C to stop\n")

    # Check if main_with_static.py exists, otherwise use main_simple.py with static serving
    server_file = backend_dir / "main_with_static.py"
    if not server_file.exists():
        # Create it on the fly
        create_static_server()
        server_file = backend_dir / "serve_compass.py"

    # Run the server
    try:
        subprocess.run([sys.executable, str(server_file)])
    except KeyboardInterrupt:
        print("\n\n👋 Compass stopped. See you next time!")

def create_static_server():
    """Create a server that serves both API and frontend"""
    server_code = '''
"""
Compass - All-in-One Server
Serves backend API + frontend from one port
"""
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# Import the main FastAPI app
from main_simple import app

# Path to frontend build
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_dist.exists():
    # Mount static files (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    # Serve index.html for all non-API routes (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend for all non-API routes"""
        # Skip API routes
        if full_path.startswith("api/") or full_path == "docs" or full_path == "openapi.json":
            return

        # Serve index.html for frontend routes
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(index_path)

        return {"error": "Frontend not built"}

if __name__ == "__main__":
    print("✅ Serving frontend from /")
    print("✅ API endpoints at /api/*")
    print("\\n🌐 Open: http://localhost:8000\\n")

    uvicorn.run(
        "serve_compass:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
'''

    backend_dir = Path(__file__).parent / "backend"
    server_file = backend_dir / "serve_compass.py"
    server_file.write_text(server_code)
    print(f"   ✓ Created {server_file}")

if __name__ == "__main__":
    main()
