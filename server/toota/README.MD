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
- [Environment Variables Setup](#environment-variables-setup)
  - [Overview of `.env` File](#overview-of-env-file)
  - [How to Set Up Email Credentials](#how-to-set-up-email-credentials)
  - [How to Set Up the Database with Supabase](#how-to-set-up-the-database-with-supabase)
- [Trip Management](#trip-management)
  - [Find Available Drivers](#find-available-drivers)
  - [Real-Time Trip Requests](#real-time-trip-requests)
  - [Real-Time Location Updates](#real-time-location-updates)
  - [Trip Status Updates](#trip-status-updates)

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

### Overview of .env File

The env file is used to store sensitive environment variables. Below is an example structure for the .env file:

```
SECRET_KEY=django-insecure-hbmce+fcnw4$$^fcf$#7wb3l_#^+mcx7jzy51lc8h8q=*5)a)a
DEBUG=True
EMAIL_HOST_USER=@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_here
DATABASE_URL=postgresql://username:password@hostname:port/dbname
DIRECT_URL=postgresql://username:password@hostname:port/dbname
```

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
   - Add the following variables to your .env file:
     ```
     EMAIL_HOST_USER=your_email@gmail.com
     EMAIL_HOST_PASSWORD=your_generated_app_password
     ```
   - Replace your_email@gmail.com with your Gmail address and your_generated_app_password with the password generated in Step 2.

--- 

### How to Set Up the Database with Supabase

1. **Create a Supabase Account**  
   - Go to the [Supabase Website](https://supabase.com) and sign up for an account.

2. **Create a New Project**:  
   - After logging in, click on "New Project."
   - Choose a project name, database password, and a region for your project.

3. **Retrieve Database Credentials**:  
   - Navigate to the "connect" tab in your Supabase project at the top.
   - Go to the "ORMs" section.
   - Copy the database connection string under ".env.local" file  
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


## Trip Management
The Trip module handles finding available drivers, updating trip status, and real-time communication using WebSockets.

### Find Available Drivers
A passenger can search for available drivers near their location. The system will return a list of drivers who are currently available to accept a trip request

```bash
GET /trip/find-driver/
```

**Response Example**:
- If available drivers are found**:
```bash
{
    "message": "Available drivers found",
    "drivers": [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe"
            "latitude": 12.34,
            "longitude": 56.78,
            "is_available": True,
            ...
        },
        {
            "id": 2,
            "first_name": "Barry",
            "last_name": "Griffin"
            "latitude": 12.34,
            "longitude": 56.78,
            "is_available": True,
            ...
        },
        ...
    ]
}
```
- If no drivers are found:
```bash
{
   "message": "No available drivers nearby"
}
```

## Real-Time Trip Requests
To provide instant trip requests to drivers, a WebSocket connection is used. When a passenger requests a ride, the system sends a real-time trip request to nearby drivers.

- Websocket connection for the user to request the trip
```bash
ws://localhost:8000/ws/trips/user/request/<str:driver_id>/
```
* Example payload to be sent to the socket for the user:
```bash
{
   "user_id": 1,
   "trip_request_status": "this is optional (only included as 'cancelled' if user cancels the trip while request is made)",
   "trip_info": 
   {
      "pickup_lat": 12.56,
      "destination_lat": 45.67,
      "pickup": "string text of the location. eg 123 Main Street",
      "destination": "string text of the location. eg 456 Elm Street",
      "load_description": "2 large bags, 1 small bag"
   }
}
```
*if driver accepts, this will be the example response recieved*:
```bash
{
   "trip_id": 1,
   "status": "accepted"
}
```
*if driver rejects, this will be the example response recieved*:
```bash
{
   "status": "rejected"
}
```

- Websocket connection for the driver to request the trip
```bash
ws://localhost:8000/ws/trips/driver/response/<str:driver_id>/
```
* Example payload to be sent to the socket for the driver:
```bash
{
   "user_id": 1,
   "trip_response_status": "accepted or rejected"
}
```

### Trip Status Updates
Drivers and passengers can update the status of a trip (e.g., "on the way", "cancelled" ,"picked up," "in progress", "completed").
```bash
POST /trips/<str:trip_id>/status/
```
Expected response recieved:
```bash
{
   "message": "trip updated successfully"
}
```

