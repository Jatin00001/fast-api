#!/bin/bash

# FastAPI Docker Stop Script
echo "🛑 Stopping FastAPI Application..."

# Stop and remove containers
docker-compose down

echo "✅ Application stopped successfully!"
echo ""
echo "💡 To remove all data (including database), run:"
echo "   docker-compose down -v" 