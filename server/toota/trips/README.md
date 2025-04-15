Here’s your documentation beautifully formatted in **README HTML-friendly Markdown style** (with `<details>` tags, code blocks, bold headers, and formatting polish) — clean and professional:

---

# 🚗 TripDocumentation

## 📌 Overview
The application uses **WebSockets** for real-time communication between users, drivers, and the system. This enables features like:

- Live location tracking  
- Trip requests  
- Status updates  

### ⚠️ Important Notes:

- **Base URL:**  
  ```
  /toota-mobile-sa.onrender.com/
  ```
- Always reconnect with retries (max: **10 times**)  
- Sockets will send a `ping` payload to keep the connection alive:
  ```json
  {
    "type": "ping"
  }
  ```
- When driver changes availability status, update via:  
  ```
  https://{base_url}/trips/driver/online-status/
  ```  
  Then:
  - Disconnect from all sockets if set to offline  
  - Reconnect if set to online  

- Errors from socket always follow this structure:
  ```json
  {
    "type": "error",
    "message": "..."
  }
  ```

- Disconnect from `wss://{base_url}/ws/trips/user/` once done to reduce server load.

---

## 🧭 Driver WebSocket Endpoints

<details>
<summary><strong>1. Driver Location WebSocket</strong></summary>

- **URL:**  
  `wss://{base_url}/ws/trips/driver/location/`

- **Purpose:**  
  Updates the driver's location in real-time

- **Authentication:**  
  Driver only

- **Instruction:**  
  - Use Google Maps API to extract coordinates  
  - Send coordinates every **30 seconds**  
  - **Driver must be online**, else connection fails

- **Send Format:**
  ```json
  {
    "latitude": float,
    "longitude": float
  }
  ```

- **Response Format:**
  ```json
  {
    "type": "driver_location_update",
    "message": "location updated successfully"
  }
  ```

</details>

---

<details>
<summary><strong>2. Driver Trip Response WebSocket</strong></summary>

- **URL:**  
  `wss://{base_url}/ws/trips/driver/`

- **Purpose:**  
  Driver receives and responds to trip requests in real time

- **Authentication:**  
  Driver only

- **Instructions:**
  - Driver must be online  
  - Wait for a trip request with type `new_trip_request`:

  ```json
  {
    "type": "new_trip_request",
    "data": {
      "trip_id": "...",
      "pickup": "...",
      "destination": "...",
      "vehicle_type": "...",
      "load_description": "...",
      "user_info": {
        "id": "...",
        "name": "...",
        "phone": "..."
      },
      "payment_info": {
        "payment_method": "...",
        "payment_status": "success/pending",
        "amount": float,
        "currency": "..."
      }
    }
  }
  ```

  - Respond within **30 seconds**, or lose the trip

- **Send Format:**
  ```json
  {
    "trip_id": "...",
    "driver_response": "accept" | "reject"
  }
  ```

- **Receive Format:**
  - If **rejected**:
    ```json
    {
      "type": "trip_rejected",
      "message": "Trip {trip_id} rejected"
    }
    ```
  - If **accepted**:
    ```json
    {
      "type": "trip_status_update",
      "message": "..."
    }
    ```

</details>

---

<details>
<summary><strong>3. Driver Update Trip Status WebSocket</strong></summary>

- **URL:**  
  `wss://{base_url}/ws/trips/driver/status/<str:trip_id>/`

- **Purpose:**  
  Driver updates the trip status in real time

- **Authentication:**  
  Driver only

- **Instruction:**  
  Driver must be online

- **Send Format:**
  ```json
  {
    "trip_id": "...",
    "status": "in progress" | "arrived at pickup" | "completed" | "cancelled" | "arrived at destination" | "picked up"
  }
  ```

- **Receive Format:**
  - If **payment method is cash and not yet paid**:
    ```json
    {
      "type": "trip_payment_update",
      "message": "..."
    }
    ```
  - Else:
    ```json
    {
      "type": "trip_status_update",
      "message": "..."
    }
    ```

</details>

---

## 👥 User WebSocket Endpoints

<details>
<summary><strong>1. User Get Available Drivers</strong></summary>

- **URL:**  
  `wss://{base_url}/ws/trips/drivers/all/`

- **Purpose:**  
  User fetches nearby drivers based on their current location

- **Authentication:**  
  User only

- **Instruction:**  
  - Use Google Maps API to extract user's current location  
  - Send coordinates to socket

- **Send Format:**
  ```json
  {
    "user_latitude": float,
    "user_longitude": float
  }
  ```

- **Receive Format:**
  - If no drivers:
    ```json
    {
      "type": "nearest_drivers",
      "nearest_drivers": []
    }
    ```

  - Else:
    ```json
    {
      "type": "nearest_drivers",
      "nearest_drivers": [
        {
          "driver": {
            "id": "...",
            "name": "...",
            "email": "...",
            "phone": "...",
            "vehicle_type": "...",
            "rating": float,
            "latitude": float,
            "longitude": float,
            "is_available": true,
            "profile_pic": "...",
            "car_images": ["...", "..."],
            "number_plate": "..."
          },
          "route_data": {
            "distance": "e.g. 850m or 2.1km",
            "duration": "e.g. 5 mins"
          }
        }
      ]
    }
    ```

</details>

---

<details>
<summary><strong>2. User Get Driver Location</strong></summary>

- **URL:**  
  `wss://{base_url}/ws/trips/user/location/<str:driver_id>/`

- **Purpose:**  
  User subscribes to a driver’s real-time location

- **Authentication:**  
  User only

- **Instruction:**  
  Use Google Maps API to get the user’s current coordinates

- **Send Format:**
  ```json
  {
    "user_latitude": float,
    "user_longitude": float
  }
  ```

- **Receive Format:**
  ```json
  {
    "type": "driver_location_update",
    "id": "...",
    "name": "...",
    "email": "...",
    "phone": "...",
    "vehicle_type": "...",
    "rating": float,
    "latitude": float,
    "longitude": float,
    "is_available": true,
    "profile_pic": "...",
    "car_images": ["...", "..."],
    "number_plate": "...",
    "duration": "...",
    "distance": "..."
  }
  ```

</details>

---

<details>
<summary><strong>3. User Trip Request WebSocket</strong></summary>

- **URL:**  
  `wss://{base_url}/ws/trips/user/`

- **Purpose:**  
  Allows authenticated users to request a trip, confirm a driver, and receive trip updates in real time.

- **Authentication:**  
  User only

- **Instruction:**  
  User must be authenticated

- **Send Format:**  
  - **Create Trip**
    ```json
    {
      "action": "create_trip",
      "vehicle_type": "truck",
      "pickup": "Ikeja, Lagos",
      "destination": "Victoria Island, Lagos",
      "pickup_latitude": 6.6018,
      "pickup_longitude": 3.3515,
      "dest_latitude": 6.4281,
      "dest_longitude": 3.4216,
      "load_description": "Building materials"
    }
    ```

  - **Confirm Driver**
    ```json
    {
      "action": "confirm_driver",
      "trip_id": "trip-uuid",
      "driver_id": "driver-id"
    }
    ```

- **Receive Format:**
  - **On successful trip creation:**
    ```json
    {
      "type": "trip_created",
      "trip_id": "trip-uuid",
      "estimated_fare": 1500.0,
      "distance": 12.5,
      "estimated_time": "25 mins",
      "status": "pending"
    }
    ```

  - **If driver is unavailable:**
    ```json
    {
      "type": "select_new_driver",
      "message": "Driver is not available. Please select another driver.",
      "available_drivers": [ ... ]
    }
    ```

  - **If driver is confirmed and awaiting response:**
    ```json
    {
      "type": "awaiting_driver_response",
      "trip_id": "trip-uuid",
      "status": "pending",
      "driver_info": { ... },
      "payment_info": {
        "payment_method": "card",
        "payment_status": "success",
        "amount": 1500.0,
        "currency": "NGN"
      }
    }
    ```

  - **If driver doesn't respond within timeout:**
    ```json
    {
      "type": "select_new_driver",
      "message": "Driver is not available. Please select another driver.",
      "available_drivers": [ ... ]
    }
    ```

  - **Real-time trip updates if driver accepts:**
    ```json
    {
      "type": "trip_status_update",
      "trip_id": "trip-uuid",
      "status": "accepted"
    }
    ```

</details>

---

<details>
<summary><strong>4. User Get Trip Status WebSocket</strong></summary>

- **URL:**  
  `wss://{base_url}/ws/trips/status/<str:trip_id>/`

- **Purpose:**  
 User gets the trip status in real time

- **Authentication:**  
  User only

- **Instruction:**  
  User must be connected to their ongoing opened trips

- **Send Format:** *None*

- **Receive Format:**
  - If **payment method is cash and not yet paid**:
    ```json
    {
      "type": "trip_payment_update",
      "message": "..."
    }
    ```
  - Else:
    ```json
    {
      "type": "trip_status_update",
      "message": "..."
    }
    ```

</details>


## 📂 Test References

> 🔍 You can check the `test/` folder for test scripts that simulate frontend connections and validate the socket communication process.

