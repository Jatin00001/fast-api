# FastAPI Project

A comprehensive FastAPI project with SQL, GCP, AWS, and HTTPS support.

## Features

- FastAPI framework with automatic OpenAPI documentation
- SQL database support with SQLAlchemy ORM
- AWS S3 integration for file storage
- Google Cloud Storage integration
- HTTPS support with SSL/TLS
- JWT authentication
- User management API
- File upload to AWS S3 and GCP Storage
- Environment-based configuration

## Requirements

- Python 3.8+
- PostgreSQL (or any other SQL database supported by SQLAlchemy)
- AWS account with S3 access (optional)
- GCP account with Storage access (optional)

## Quick Start with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fastapi-project.git
   cd fastapi-project
   ```

2. Start the application with Docker:
   ```bash
   # Simple one-command startup
   ./docker-start.sh
   
   # Or manually:
   docker-compose up --build -d
   ```

3. Access your application:
   - **FastAPI**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Database**: localhost:5434

4. Stop the application:
   ```bash
   ./docker-stop.sh
   # Or: docker-compose down
   ```

## Manual Installation (Alternative)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL database manually

4. Create and configure `.env` file:
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

## Generate SSL Certificate for HTTPS

To enable HTTPS, generate a self-signed SSL certificate:

```
./generate_ssl_cert.sh
```

This will create a `certs` directory with `key.pem` and `cert.pem` files.

## Docker Commands

### Basic Usage
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and start
docker-compose up --build -d

# Remove all data (including database)
docker-compose down -v
```

### Development Commands
```bash
# Access the running container
docker exec -it fastapi_app bash

# Run database migrations
docker exec fastapi_app alembic upgrade head

# View database logs
docker-compose logs postgres
```

## Manual Running (Without Docker)

```bash
# Start the FastAPI application
python main.py

# Or with uvicorn directly
uvicorn main:app --reload
```

## Access Points

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Project Structure

```
fastapi-project/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   └── storage.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── deps.py
│   │   ├── events.py
│   │   └── security.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── sql.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── aws_service.py
│   │   └── gcp_service.py
│   └── __init__.py
├── certs/
│   ├── cert.pem
│   └── key.pem
├── .env
├── env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── docker-start.sh
├── docker-stop.sh
├── init-db.sql
├── generate_ssl_cert.sh
├── main.py
├── README.md
└── requirements.txt
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Get JWT token

### Users
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{user_id}` - Get user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Storage
- `POST /api/v1/storage/upload/aws` - Upload file to AWS S3
- `POST /api/v1/storage/upload/gcp` - Upload file to GCP Storage
- `GET /api/v1/storage/presigned-url/aws` - Get AWS S3 presigned URL
- `GET /api/v1/storage/signed-url/gcp` - Get GCP Storage signed URL

## Docker Configuration

### Database Configuration
- **Database**: PostgreSQL 15
- **User**: `fastapi_user`
- **Password**: `SecureFastAPI2024!`
- **Database**: `fastapi_app_db`
- **External Port**: 5434 (Internal: 5432)

### Services
- **FastAPI App**: Port 8000
- **PostgreSQL**: Port 5434 (external)

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Check what's using the port
   lsof -i :8000
   # Or change port in docker-compose.yml
   ```

2. **Database connection issues**:
   ```bash
   # Check database logs
   docker-compose logs db
   # Restart database
   docker-compose restart db
   ```

3. **Permission issues**:
   ```bash
   # Make scripts executable
   chmod +x docker-start.sh docker-stop.sh
   ```

4. **Docker not found**:
   ```bash
   # Install Docker and Docker Compose
   # https://docs.docker.com/get-docker/
   ```

### Reset Everything
```bash
# Stop all services and remove data
docker-compose down -v
# Remove images
docker-compose down --rmi all
# Start fresh
./docker-start.sh
```
