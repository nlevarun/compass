#!/usr/bin/env python3
"""Test if OAuth module imports correctly."""

try:
    from slack_oauth import router
    print("✅ OAuth router imports successfully")
    print(f"Routes: {len(router.routes)}")
    for route in router.routes:
        method = list(route.methods)[0] if route.methods else "GET"
        print(f"  - {method} {route.path}")
except Exception as e:
    print(f"❌ Error importing OAuth router: {e}")
    import traceback
    traceback.print_exc()
