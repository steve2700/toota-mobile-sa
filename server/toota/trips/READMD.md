# TripDocumentation

## Overview
The application uses WebSockets for real-time communication between users, drivers, and the system. This enables features like live location tracking, trip requests, and status updates. There are also views(apis) that f

## WebSocket Endpoints

### 1. Driver Location WebSocket
**WebSocket URL:** `ws/driver/location/`

**Purpose:** Updates the location of a driver in real-time.

**Authentication:** Driver only

**Send data format:**
```json
{
    "latitude": float,
    "longitude": float
}
```

**Receive data format:**
```json
{
    "latitude": float,
    "longitude": float,
    "driver_details": {
        "id": string,
        "name": string,
        "email": string,
        "phone": string,
        "vehicle_type": string,
        "rating": float,
        "is_available": boolean,
        "profile_pic": string | null,
        "car_image": string | null
    }
}
```

### 2. User Get Driver Location WebSocket
**WebSocket URL:** `ws/user/driver/{driver_id}/location/`

**Purpose:** Allows a user to subscribe to a driver's real-time location updates.

**Authentication:** User only

**Send data format:** None required

**Receive data format:**
```json
{
    "latitude": float,
    "longitude": float,
    "driver_details": {
        "id": string,
        "name": string,
        "email": string,
        "phone": string,
        "vehicle_type": string,
        "rating": float,
        "is_available": boolean,
        "profile_pic": string | null,
        "car_image": string | null
    }
}
```

### 3. Trip Request WebSocket (User)
**WebSocket URL:** `ws/trips/user/request/`

**Purpose:** Allows users to create trip requests and select drivers.

**Authentication:** User only

**Send data format (create trip):**
```json
{
    "action": "create_trip",
    "vehicle_type": string,
    "pickup": string,
    "destination": string,
    "pickup_lat": float,
    "pickup_lon": float,
    "dest_lat": float,
    "dest_lon": float,
    "load_description": string
}
```

**Receive data format (after trip creation):**
```json
{
    "message": "Trip created successfully - select a driver",
    "trip_id": string,
    "estimated_fare": float,
    "distance_km": float,
    "estimated_time": string,
    "pickup": string,
    "destination": string,
    "vehicle_type": string,
    "load_description": string,
    "user_info": {
        "id": string,
        "name": string,
        "phone": string
    },
    "available_drivers": array,
    "status": "pending"
}
```

**Send data format (confirm driver):**
```json
{
    "action": "confirm_driver",
    "trip_id": string,
    "driver_id": string
}
```

**Receive data format (after driver confirmation):**
```json
{
    "message": "Awaiting driver response",
    "trip_id": string,
    "status": "pending",
    "driver_info": {
        "id": string,
        "name": string,
        "phone": string,
        "vehicle_type": string,
        "rating": float
    },
    "payment_info": {
        "payment_method": string,
        "payment_status": string,
        "amount": float,
        "currency": string
    }
}
```

**Receive data format (if driver accepts):**
```json
{
    "type": "trip_status_update",
    "trip_id": string,
    "status": "accepted",
    "driver_info": {
        "id": string,
        "name": string,
        "first_name": string,
        "last_name": string,
        "phone": string,
        "vehicle_type": string,
        "rating": float
    },
    "trip_details": {
        "id": string,
        "pickup": string,
        "destination": string,
        "pickup_lat": float,
        "pickup_long": float,
        "dest_lat": float,
        "dest_long": float,
        "vehicle_type": string,
        "load_description": string,
        "fare": float,
        "status": string,
        "distance_km": float,
        "estimated_time": string,
        "created_at": string
    },
    "payment_info": {
        "payment_method": string,
        "payment_status": string,
        "amount": float,
        "currency": string
    }
}
```

**Receive data format (if driver doesn't respond within 30 seconds):**
```json
{
    "message": "Driver did not respond - select another driver",
    "trip_id": string,
    "status": "pending",
    "available_drivers": array
}
```

### 4. Driver Trip Response WebSocket
**WebSocket URL:** `ws/trips/driver/response/`

**Purpose:** Allows drivers to receive trip requests and respond to them.

**Authentication:** Driver only

**Receive data format (new trip request):**
```json
{
    "type": "new_trip_request",
    "trip_details": {
        "trip_id": string,
        "estimated_fare": float,
        "distance_km": float,
        "estimated_time": string,
        "pickup": string,
        "destination": string,
        "vehicle_type": string,
        "load_description": string,
        "user_info": {
            "id": string,
            "name": string,
            "phone": string
        },
        "payment_info": {
            "payment_method": string,
            "payment_status": string,
            "amount": float,
            "currency": string
        }
    }
}
```

**Send data format (respond to trip request):**
```json
{
    "trip_id": string,
    "driver_response_status": "accepted" | "rejected"
}
```

**Receive data format (if accepted):**
```json
{
    "user_id": string,
    "first_name": string,
    "last_name": string,
    "email": string,
    "phone": string
}
```

### 5. Driver Update Trip Status WebSocket
**WebSocket URL:** `ws/trips/driver/status/update/<str:trip_id>/`

**Purpose:** Allows drivers to update the status of ongoing trips.

**Authentication:** Driver only

**Send data format:**
```json
{
    "trip_status": "in_progress" | "arrived at pickup" | "completed" | "cancelled" | "arrived at destination"
}

**Receive data format (if payment is cash and not yet paid):**
{
    "payment_status": "arrived at pickup",
    "trip_id": string,
    "message": "You must collect payment from user before pickup"
}

### 6. User Get Trip Status WebSocket
**WebSocket URL:** `ws/trips/user/status/{trip_id}/`

**Purpose:** Allows users to receive real-time updates on trip status.

**Authentication:** User only

**Send data format:** None required

**Receive data format (if driver arrived at pickup and payment is cash):**
{
    "payment_status": "arrived at pickup",
    "trip_id": string,
    "message": "You must make payment before trip starts"
}

**Recieve data format (status update):**
```json
{
    "trip_id": string,
    "trip_status": "in_progress" | "arrived at destination" | "completed" | "cancelled"
}
```


## API FOR USE
### Check Trip Status
**URL:** `trips/<uuid:trip_id>/status/`
**Purpose:** Returns the current status of the trip
**json response if success**
```json
{"trip_status": trip.status}
```
**if failed:**
```json
{"error": "Trip not found."}
```

## Notes
1. Always make your connection attempts to the socket to be a retry (max of 10)
2. The server always send a ping update to keep the connection alive
3. All WebSocket connections require authentication
4. Payment must be verified before a trip can be accepted
5. Driver has 30 seconds to respond to a trip request
6. For card payments, payment must be successful before a driver can accept the trip
7. You can check the test directory for more references on how to make connections to the endpoints