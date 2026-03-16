#!/bin/bash

# AI Learning Tutor - Stop Script
echo "🛑 Stopping AI Learning Tutor..."

# Kill all servers
lsof -ti :8000 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti :3000 2>/dev/null | xargs kill -9 2>/dev/null

sleep 1

echo "✅ All services stopped!"
