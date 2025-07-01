#!/bin/bash

# Docker Database Setup Script
echo "🔧 Setting up database and migrations..."

# Start only the database first
echo "📦 Starting PostgreSQL database..."
docker-compose up db -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Check if we can connect to the database
until docker exec fastapi_postgres pg_isready -U fastapi_user -d fastapi_app_db; do
    echo "⏳ Database not ready yet, waiting..."
    sleep 2
done

echo "✅ Database is ready!"

# Initialize alembic if needed
echo "🔄 Initializing database schema..."
docker-compose run --rm web alembic stamp head || echo "Alembic already initialized"

# Create tables without migrations (for fresh setup)
echo "📊 Creating database tables..."
docker-compose run --rm web python -c "
from app.db.sql import Base, engine
import asyncio

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print('✅ Database tables created successfully!')

asyncio.run(create_tables())
" || echo "Tables might already exist"

echo "🎉 Database setup complete! Now starting the full application..." 