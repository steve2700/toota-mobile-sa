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
## Environment Variables Setup

### Overview of `.env` File

The `.env` file is used to store sensitive environment variables. Below is an example structure for the `.env` file:

```plaintext
SECRET_KEY=django-insecure-hbmce+fcnw4$$^fcf$#7wb3l_#^+mcx7jzy51lc8h8q=*5)a)a
DEBUG=True
EMAIL_HOST_USER=@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_here
DATABASE_URL=postgresql://username:password@hostname:port/dbname
DIRECT_URL=postgresql://username:password@hostname:port/dbname
### How to Set Up Email Credentials

1. **Create a Gmail Account**  
   - If you don't already have a Gmail account, [create one here](https://accounts.google.com/signup).

2. **Enable "App Passwords" in Gmail**:  
   - Go to [Google Account Security Settings](https://myaccount.google.com/security).  
   - Enable "2-Step Verification" by following the steps provided.  
   - Once "2-Step Verification" is enabled, generate an "App Password":  
     - Under "Signing in to Google," select "App Passwords."  
     - Choose an app and device (e.g., "Mail" and "Windows Computer") and click "Generate."  
     - Copy the generated password.

3. **Update the `.env` File**:  
   - Add the following variables to your `.env` file:
     ```plaintext
     EMAIL_HOST_USER=your_email@gmail.com
     EMAIL_HOST_PASSWORD=your_generated_app_password
     ```
   - Replace `your_email@gmail.com` with your Gmail address and `your_generated_app_password` with the password generated in Step 2.
```
--- 

### How to Set Up the Database with Supabase

1. **Create a Supabase Account**  
   - Go to the [Supabase Website](https://supabase.com) and sign up for an account.

2. **Create a New Project**:  
   - After logging in, click on "New Project."
   - Choose a project name, database password, and a region for your project.

3. **Retrieve Database Credentials**:  
   - Navigate to the "Settings" tab in your Supabase project.
   - Go to the "Database" section.
   - Copy the database connection string under "Connection Pooling (PostgreSQL)."  
   - Example:
     ```plaintext
     DATABASE_URL=postgresql://username:password@aws-0-region.pooler.supabase.com:6543/dbname
     DIRECT_URL=postgresql://username:password@aws-0-region.pooler.supabase.com:5432/dbname
     ```

4. **Add to the `.env` File**:  
   - Paste the connection string as `DATABASE_URL` in your `.env` file.
   - Use the same credentials for `DIRECT_URL`.

5. **Test Your Database Connection**:  
   - Run the following command to ensure your database is properly connected:
     ```bash
     python manage.py migrate
     ```

6. **Supabase Documentation**:  
   - For more information on setting up and managing your Supabase project, visit the [Supabase Documentation](https://supabase.com/docs).




