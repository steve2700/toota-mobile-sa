# Payment API Documentation

### Base URL
```
https://yourdomain.coms/api/payment/
```

---

## 1. **Initiate Payment for a Trip**

### **Endpoint**
```
POST /api/payment/initiate/
```

### **Purpose**
Initiate a payment for a trip. Depending on the `payment_method` selected:
- **Cash**: Driver will confirm receipt manually.
- **Card**, **Mobile Money**, **Bank Transfer**: A payment link is generated through Flutterwave for the user to complete payment.

### **Authentication**
✅ Required (Bearer Token)

### **Request Body**
`application/json`

| Field            | Type   | Required | Description                                                                  |
|------------------|--------|----------|------------------------------------------------------------------------------|
| `trip_id`        | string | ✅       | UUID of the trip to be paid for                                              |
| `payment_method` | string | ✅       | Payment method (`cash`, `card`, `mobile_money`, `bank_transfer`)             |
| `currency`       | string | ✅       | Currency of the payment (`NGN`, `ZAR`, etc.)                                 |
| `location`       | string | ✅       | location from where the user is making payment from (`ZA`, `NG`, `GH`, `KE`)|

#### **Example Request**
```json
{
    "trip_id": "1",
    "payment_method": "card",
    "currency": "NGN"
}
```

---

### **Success Responses**

#### **For Cash Payment:**
`200 OK`
```json
{
    "message": "Cash payment selected. Driver will confirm receipt."
}
```

#### **For Card, Mobile Money, Bank Transfer:**
`200 OK`
```json
{
    "message": "Payment initialized successfully",
    "payment_link": "https://flutterwave.com/pay/xyz",
    "transaction_id": "8c33a5e8-4275-4d4f-94ae-f3b5b093a0c4"
}
```

---

### **Error Responses**

#### **400 Bad Request**
Invalid data provided.
```json
{
    "error": "Invalid input data",
    "details": {
        "trip_id": ["This field is required."]
    }
}
```

#### **503 Service Unavailable**
Flutterwave/payment service failure.
```json
{
    "error": "Payment service unavailable",
    "details": "Request timeout"
}
```

---

## 2. **Verify Payment**

### **Endpoint**
```
GET /api/payment/verify/
```

### **Purpose**
Verify the status of a payment transaction after redirection from Flutterwave. This can also be used to manually check the status of a payment.

### **Authentication**
❌ No Authentication Required (Public Access)

### **Query Parameters**

| Parameter        | Type   | Required | Description                                                     |
|------------------|--------|----------|-----------------------------------------------------------------|
| `tx_ref`         | string | ✅       | Transaction reference used during payment initialization        |
| `transaction_id` | string | ✅       | Transaction ID from Flutterwave                                |
| `status`         | string | ✅       | Status returned from Flutterwave (`successful`, `cancelled`, etc.) |

---

### **Example Request**
```
GET /api/payment/verify/?tx_ref=8c33a5e8-4275-4d4f-94ae-f3b5b093a0c4&transaction_id=54321&status=successful
```

---

### **Success Response**
`200 OK`
```json
{
    "status": "success",
    "message": "Payment successful.",
    "transaction_reference": "8c33a5e8-4275-4d4f-94ae-f3b5b093a0c4",
    "payment_reference": "54321",
    "payment_method": "card",
    "amount": 100.0,
    "currency": "NGN",
    "trip_id": "1"
}
```

---

### **Failure Responses**

#### **400 Bad Request**
Transaction not successful or invalid.
```json
{
    "status": "failed",
    "message": "Payment not successful"
}
```

#### **404 Not Found**
Trip or payment not found.
```json
{
    "error": "Trip not found"
}
```

---

# 📝 Payment Flow Overview for Mobile Developers

1. **Start Payment (POST `/initiate/`)**
   - Send trip details and payment method.
   - If **cash**, you are done!
   - If **card/mobile_money/bank_transfer**, you receive a `payment_link`. Open it in a WebView or redirect the user to it.

2. **User Completes Payment on Flutterwave**
   - After payment, the user is redirected back to your app with query parameters: `tx_ref`, `transaction_id`, and `status`.

3. **Verify Payment (GET `/verify/`)**
   - Send the query parameters received from Flutterwave to `/verify/`.
   - If verified, you’ll get a **success** response and can mark the trip as paid in your UI.

---

# 🔐 Security Notes
- Only authenticated users can initiate payments.
- The verification endpoint does **not** require authentication because it's called after Flutterwave redirects.

---

# 💳 Supported Payment Methods
- `cash`
- `card`
- `mobile_money`
- `bank_transfer`

---

## 🗒️ Notes
- You can check the test folder for more references.
  