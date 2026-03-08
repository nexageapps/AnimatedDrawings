#!/bin/bash
# Run the application in TESTING mode

echo "🎨 Starting Animated Drawings in TESTING MODE..."
echo "================================================"
echo ""

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export APP_MODE=testing
export PORT=5001

# Run the application
echo "Server will start at: http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
