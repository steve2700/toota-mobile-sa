# Table of Contents

- [Toota Backend Server](#toota-backend-server)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Clone the Repository](#1-clone-the-repository)
  - [Create and Activate Virtual Environment](#2-create-and-activate-virtual-environment)
  - [Install Dependencies](#3-install-dependencies)
  - [Apply Migrations](#4-apply-migrations)
  - [Start the Server](#5-start-the-server)
- [API Documentation](#api-documentation)
- [Authentication and Endpoints](#authentication-and-endpoints)

# Toota Backend Server

Welcome to the Toota Backend Server! This server powers the backend for the Toota platform, handling user authentication, KYC updates, and more.

## Tech Stack

The backend of this application is built using the following technologies:

- Python: General-purpose programming language.
- Django: High-level Python web framework.
- Django REST Framework (DRF): Toolkit for building Web APIs.
- PostgreSQL: Relational database management system.
- JWT: JSON Web Tokens for authentication.
- Swagger: API documentation generator.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/steve2700/toota-mobile-sa.git
cd server/toota
```
---

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate
```
---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```
---

### 4. Apply Migrations
```bash
python manage.py migrate
```
### 5.Start the Server
```bash
python manage.py runserver
```

### API Documentation
Explore the API endpoints by accessing the Swagger documentation:
```bash
http://127.0.0.1:8000/swagger-docs/ or production level  https://toota-mobile-sa.onrender.com/swagger/
```


