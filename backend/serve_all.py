#!/usr/bin/env python3
"""
Single-command server for Compass.
Serves both backend API and frontend from one process.
"""
import subprocess
import sys
import os
from pathlib import Path

def check_frontend_built():
    """Check if frontend is built."""
    dist_path = Path(__file__).parent.parent / "frontend" / "dist"
    return dist_path.exists() and (dist_path / "index.html").exists()

def build_frontend():
    """Build frontend for production."""
    frontend_path = Path(__file__).parent.parent / "frontend"

    print("📦 Building frontend...")
    print(f"   Location: {frontend_path}")

    # Check if node_modules exists
    if not (frontend_path / "node_modules").exists():
        print("📥 Installing frontend dependencies...")
        result = subprocess.run(
            ["npm", "install"],
            cwd=frontend_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ npm install failed:\n{result.stderr}")
            return False

    # Build frontend
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=frontend_path,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ Frontend built successfully")
        return True
    else:
        print(f"❌ Frontend build failed:\n{result.stderr}")
        return False

def main():
    print("🚀 Compass All-in-One Server")
    print("=" * 50)

    # Check if frontend is built
    if not check_frontend_built():
        print("\n📦 Frontend not built. Building now...")
        if not build_frontend():
            print("\n⚠️  Frontend build failed, but backend will still start.")
            print("   You can build manually: cd frontend && npm run build")
    else:
        print("✅ Frontend already built")

    print("\n🔧 Starting backend server...")
    print("   Backend API: http://localhost:8000/api")
    print("   Frontend UI:  http://localhost:8000")
    print("   API Docs:     http://localhost:8000/docs")
    print("\n   Press Ctrl+C to stop\n")

    # Import and run main app
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent))

        # Import main app
        import main_with_static

        # This will start the server
        main_with_static.run_server()
    except ImportError:
        print("❌ Could not import main_with_static.py")
        print("   Falling back to regular main.py (API only)")
        import main
        main.run_server()

if __name__ == "__main__":
    main()
