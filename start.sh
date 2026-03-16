#!/bin/bash

# AI Learning Tutor - Complete Startup Script
echo "🎓 Starting AI Learning Tutor..."
echo "=================================="

# Change to project directory
cd "$(dirname "$0")"

# Kill any existing servers
echo "📡 Cleaning up old processes..."
lsof -ti :8000 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti :3000 2>/dev/null | xargs kill -9 2>/dev/null
sleep 1

# Start Backend
echo ""
echo "🚀 Starting Backend API on port 8000..."
python -m uvicorn simple_api:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
sleep 2

# Check if backend started
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend started successfully (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start. Check /tmp/backend.log"
    exit 1
fi

# Start Frontend
echo ""
echo "🌐 Starting Frontend on port 3000..."
python serve_frontend.py > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 2

# Check if frontend started
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend started successfully (PID: $FRONTEND_PID)"
else
    echo "❌ Frontend failed to start. Check /tmp/frontend.log"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ All services are running!"
echo ""
echo "📊 Service Status:"
echo "   Backend:  http://localhost:8000 ✓"
echo "   Frontend: http://localhost:3000 ✓"
echo "   API Docs: http://localhost:8000/docs ✓"
echo ""
echo "🌐 Open your browser to: http://localhost:3000"
echo ""
echo "📝 Process IDs:"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop all services, run:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Or use: lsof -ti :8000,:3000 | xargs kill -9"
echo "=================================="
