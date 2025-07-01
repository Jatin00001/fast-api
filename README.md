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

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fastapi-project.git
   cd fastapi-project
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file with your configuration.

## Generate SSL Certificate for HTTPS

To enable HTTPS, generate a self-signed SSL certificate:

```
./generate_ssl_cert.sh
```

This will create a `certs` directory with `key.pem` and `cert.pem` files.

## Running the Application

Start the FastAPI application:

```
python main.py
```

Or with uvicorn directly:

```
uvicorn main:app --reload
```

The API will be available at:
- HTTP: http://localhost:8000
- HTTPS: https://localhost:8000 (if SSL certificates are configured)

API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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
├── .env.example
├── .gitignore
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

## system Issue
export DOCKER_HOST=unix:///var/run/docker.sock
