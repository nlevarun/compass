#!/bin/bash
# Reset database - use this if schema changed

echo "🗑️  Removing old database..."
rm -f compass.db

echo "✅ Database will be recreated fresh on next startup"
echo ""
echo "Now run: python main.py"
