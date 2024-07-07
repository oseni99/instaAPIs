# Social Media API

This is a fully functional social media API built with FastAPI. The API allows users to register, log in, create posts, comment on posts, like posts, and follow other users.

## Features

- **User Authentication**: Register and log in users with JWT-based authentication.
- **User Profiles**: Manage user profiles including updating profile information.
- **Posts**: Create, read, update, and delete posts with support for image uploads.
- **Comments**: Comment on posts, read comments, and delete comments.
- **Likes**: Like and unlike posts.
- **Followers**: Follow and unfollow other users.
- **Secure**: Secure endpoints with JWT-based authentication.
- **Documentation**: Auto-generated API documentation with Swagger UI.

## Technologies Used

- **FastAPI**: Web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library for Python.
- **PostgreSQL**: Relational database system.
- **Docker**: Containerization for development and deployment.
- **JWT**: JSON Web Tokens for secure authentication.

## Setup Instructions

### Prerequisites

- Python 3.7+
- Pipenv
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/oseni99/instaAPIs.git
   cd src

## API Documentation
After starting the server, you can access the auto-generated API documentation at:

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc