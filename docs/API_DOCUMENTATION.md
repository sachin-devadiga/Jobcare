# JobCare Voice API Documentation

## Base URL

```
Development: http://localhost:8000/api/v1/
Production: https://your-domain.com/api/v1/
```

## Authentication

All authenticated endpoints require a JWT access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Types

| Token | Lifetime | Purpose |
|-------|----------|---------|
| Access Token | 15 minutes | API authentication |
| Refresh Token | 7 days | Get new access token |

---

## Authentication Endpoints

### Register

```
POST /auth/register/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "phone": "+919876543210",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "role": "employee",
  "full_name": "Rahul Sharma"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "phone": "+919876543210",
  "role": "employee",
  "is_verified": false,
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### Login

```
POST /auth/login/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "employee",
    "full_name": "Rahul Sharma",
    "is_verified": true
  }
}
```

### Verify OTP

```
POST /auth/verify-otp/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response (200):**
```json
{
  "message": "Email verified successfully",
  "is_verified": true
}
```

### Refresh Token

```
POST /auth/refresh/
```

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### Forgot Password

```
POST /auth/forgot-password/
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "OTP sent to your email"
}
```

### Reset Password

```
POST /auth/reset-password/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "NewSecurePass123!",
  "confirm_password": "NewSecurePass123!"
}
```

**Response (200):**
```json
{
  "message": "Password reset successfully"
}
```

---

## Jobs Endpoints

### List Jobs

```
GET /jobs/?page=1&page_size=20
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| search | string | Search by title, description, company |
| category | uuid | Filter by category |
| city | string | Filter by city |
| state | string | Filter by state |
| job_type | string | full_time, part_time, contract, internship, remote |
| salary_min | integer | Minimum salary |
| salary_max | integer | Maximum salary |
| experience_min | integer | Minimum experience (years) |
| experience_max | integer | Maximum experience (years) |
| skills | string | Comma-separated skill names |
| is_featured | boolean | Featured jobs only |
| is_urgent | boolean | Urgent jobs only |
| ordering | string | created_at, -created_at, salary_min, -salary_min |
| page | integer | Page number |
| page_size | integer | Items per page (max 50) |

**Response (200):**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "title": "Electrician Needed",
      "company": {
        "id": "uuid",
        "name": "ABC Construction",
        "logo": "https://storage.example.com/logos/abc.png",
        "is_verified": true
      },
      "category": {
        "id": "uuid",
        "name": "Electrician",
        "icon": "⚡"
      },
      "salary_min": 25000,
      "salary_max": 35000,
      "salary_type": "monthly",
      "location": "Whitefield, Bangalore",
      "city": "Bangalore",
      "state": "Karnataka",
      "job_type": "full_time",
      "experience_min": 1,
      "experience_max": 5,
      "skills_required": ["Electrical Wiring", "Circuit Breakers", "Safety Compliance"],
      "openings": 5,
      "is_urgent": true,
      "is_featured": false,
      "application_count": 12,
      "created_at": "2026-07-20T10:30:00Z"
    }
  ]
}
```

### Job Detail

```
GET /jobs/{id}/
```

**Response (200):**
```json
{
  "id": "uuid",
  "title": "Electrician Needed",
  "slug": "electrician-needed-abc-construction",
  "company": {
    "id": "uuid",
    "name": "ABC Construction",
    "logo": "https://storage.example.com/logos/abc.png",
    "cover_image": "https://storage.example.com/covers/abc.jpg",
    "description": "Leading construction company in Bangalore",
    "industry": "Construction",
    "size": "500-1000",
    "founded_year": 2010,
    "website": "https://abcconstruction.com",
    "location": "Bangalore, Karnataka",
    "is_verified": true,
    "rating": 4.2,
    "review_count": 45
  },
  "category": {
    "id": "uuid",
    "name": "Electrician",
    "icon": "⚡"
  },
  "title": "Electrician Needed",
  "description": "We are looking for experienced electricians for our new residential project in Whitefield...",
  "responsibilities": [
    "Install electrical wiring and fixtures",
    "Troubleshoot electrical issues",
    "Ensure safety compliance",
    "Read blueprints and diagrams"
  ],
  "requirements": [
    "Minimum 1 year experience",
    "ITI certification preferred",
    "Knowledge of safety protocols",
    "Physically fit for the job"
  ],
  "skills_required": ["Electrical Wiring", "Circuit Breakers", "Safety Compliance", "Blueprint Reading"],
  "experience_min": 1,
  "experience_max": 5,
  "salary_min": 25000,
  "salary_max": 35000,
  "salary_type": "monthly",
  "location": "Whitefield, Bangalore",
  "city": "Bangalore",
  "state": "Karnataka",
  "latitude": 12.9698,
  "longitude": 77.7500,
  "job_type": "full_time",
  "shift_timing": "day",
  "education_required": ["ITI", "10th Pass"],
  "benefits": ["Health Insurance", "PF", "Bonus", "Transport Allowance"],
  "openings": 5,
  "urgency": "high",
  "status": "active",
  "is_featured": false,
  "is_urgent": true,
  "views_count": 234,
  "application_count": 12,
  "created_at": "2026-07-20T10:30:00Z",
  "expires_at": "2026-08-20T10:30:00Z"
}
```

### Create Job (Employer)

```
POST /jobs/
```

**Request Body:**
```json
{
  "title": "Electrician Needed",
  "description": "We are looking for experienced electricians...",
  "category": "category-uuid",
  "responsibilities": ["Install wiring", "Troubleshoot issues"],
  "requirements": ["1 year experience", "ITI preferred"],
  "skills_required": ["Electrical Wiring", "Safety"],
  "experience_min": 1,
  "experience_max": 5,
  "salary_min": 25000,
  "salary_max": 35000,
  "salary_type": "monthly",
  "location": "Whitefield, Bangalore",
  "city": "Bangalore",
  "state": "Karnataka",
  "latitude": 12.9698,
  "longitude": 77.7500,
  "job_type": "full_time",
  "shift_timing": "day",
  "education_required": ["ITI", "10th Pass"],
  "benefits": ["Health Insurance", "PF"],
  "openings": 5,
  "urgency": "high"
}
```

**Response (201):** Full job object

### Nearby Jobs

```
GET /jobs/nearby/?latitude=12.9698&longitude=77.7500&radius=10
```

| Parameter | Type | Description |
|-----------|------|-------------|
| latitude | float | User's latitude |
| longitude | float | User's longitude |
| radius | integer | Search radius in km (default: 10) |

### Categories

```
GET /jobs/categories/
```

**Response (200):**
```json
[
  {
    "id": "uuid",
    "name": "Electrician",
    "icon": "⚡",
    "slug": "electrician",
    "job_count": 45
  }
]
```

### Skills

```
GET /jobs/skills/?search=electric
```

**Response (200):**
```json
[
  {
    "id": "uuid",
    "name": "Electrical Wiring",
    "category": "uuid"
  }
]
```

---

## Applications Endpoints

### Apply to Job

```
POST /applications/
```

**Request Body:**
```json
{
  "job": "job-uuid",
  "cover_letter": "I have 3 years of experience as an electrician...",
  "resume_url": "https://storage.example.com/resumes/my-resume.pdf"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "job": "job-uuid",
  "status": "applied",
  "ai_match_score": 85.5,
  "created_at": "2026-07-21T10:30:00Z"
}
```

### My Applications

```
GET /applications/my-applications/?status=applied
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | applied, under_review, shortlisted, interview_scheduled, selected, rejected, withdrawn |

### Update Application Status (Employer)

```
PATCH /applications/{id}/status/
```

**Request Body:**
```json
{
  "status": "shortlisted",
  "employer_notes": "Good candidate, schedule interview"
}
```

### Schedule Interview

```
PATCH /applications/{id}/schedule-interview/
```

**Request Body:**
```json
{
  "interview_date": "2026-07-28",
  "interview_time": "10:00:00",
  "interview_type": "in_person",
  "interview_location": "Office #42, Whitefield Main Road, Bangalore",
  "employer_notes": "Please bring your tools"
}
```

### Withdraw Application

```
POST /applications/{id}/withdraw/
```

---

## Voice AI Endpoints

### Speech-to-Text

```
POST /voice/stt/
```

**Request Body (multipart/form-data):**
| Field | Type | Description |
|-------|------|-------------|
| audio | file | Audio file (wav, mp3, m4a) |
| language | string | Language code (hi, en, ta, te, kn, ml, mr, gu, bn) |

**Response (200):**
```json
{
  "transcript": "I need electrician jobs near Whitefield paying more than 25000 rupees",
  "language": "hi",
  "confidence": 0.95,
  "duration": 3.5
}
```

### Text-to-Speech

```
POST /voice/tts/
```

**Request Body:**
```json
{
  "text": "Here are three electrician jobs near Whitefield",
  "language": "hi",
  "gender": "female"
}
```

**Response (200):**
Binary audio file (wav/mp3)

### Voice Search

```
POST /voice/search/
```

**Request Body (multipart/form-data):**
| Field | Type | Description |
|-------|------|-------------|
| audio | file | Voice query audio |
| latitude | float | User's latitude (optional) |
| longitude | float | User's longitude (optional) |

**Response (200):**
```json
{
  "transcript": "I need electrician jobs near Whitefield paying more than 25000 rupees",
  "parsed_query": {
    "skills": ["Electrician"],
    "location": "Whitefield",
    "salary_min": 25000,
    "job_type": null
  },
  "results": [
    {
      "id": "uuid",
      "title": "Electrician Needed",
      "company_name": "ABC Construction",
      "salary_min": 25000,
      "salary_max": 35000,
      "location": "Whitefield, Bangalore",
      "match_score": 95.0
    }
  ],
  "result_count": 3
}
```

### Voice Navigation

```
POST /voice/navigate/
```

**Request Body (multipart/form-data):**
| Field | Type | Description |
|-------|------|-------------|
| audio | file | Voice command audio |

**Response (200):**
```json
{
  "transcript": "Open my profile",
  "intent": "navigate",
  "action": "open_profile",
  "route": "/profile",
  "response_text": "Opening your profile now"
}
```

---

## Notifications Endpoints

### List Notifications

```
GET /notifications/?page=1&page_size=20
```

### Unread Count

```
GET /notifications/unread-count/
```

**Response (200):**
```json
{
  "count": 5
}
```

### Mark as Read

```
PATCH /notifications/{id}/read/
```

### Mark All Read

```
POST /notifications/mark-all-read/
```

### Register Device (FCM)

```
POST /notifications/register-device/
```

**Request Body:**
```json
{
  "fcm_token": "fcm-token-string",
  "device_type": "android",
  "device_id": "device-unique-id"
}
```

---

## Payments Endpoints

### Create Payment Order

```
POST /payments/create-order/
```

**Request Body:**
```json
{
  "plan_id": "plan-uuid"
}
```

**Response (200):**
```json
{
  "order_id": "order_xxxxx",
  "amount": 49900,
  "currency": "INR",
  "key_id": "rzp_live_xxxxx",
  "plan_name": "Professional Monthly",
  "user_name": "Rahul Sharma",
  "user_email": "rahul@example.com",
  "user_phone": "+919876543210"
}
```

### Verify Payment

```
POST /payments/verify-payment/
```

**Request Body:**
```json
{
  "razorpay_order_id": "order_xxxxx",
  "razorpay_payment_id": "pay_xxxxx",
  "razorpay_signature": "signature_hash"
}
```

**Response (200):**
```json
{
  "message": "Payment verified successfully",
  "subscription": {
    "id": "uuid",
    "plan_name": "Professional Monthly",
    "status": "active",
    "start_date": "2026-07-21",
    "end_date": "2026-08-21"
  }
}
```

### Subscription Plans

```
GET /payments/plans/
```

---

## Analytics Endpoints

### Dashboard Stats

```
GET /analytics/dashboard/
```

**Response (200) - Employer:**
```json
{
  "active_jobs": 12,
  "total_applications": 156,
  "new_applications_today": 5,
  "interviews_scheduled": 3,
  "applications_by_status": {
    "applied": 80,
    "under_review": 30,
    "shortlisted": 20,
    "interview_scheduled": 15,
    "selected": 8,
    "rejected": 3
  },
  "applications_over_time": [
    {"date": "2026-07-15", "count": 12},
    {"date": "2026-07-16", "count": 18}
  ],
  "recent_applications": []
}
```

### Job Analytics

```
GET /analytics/jobs/{id}/
```

### Application Analytics

```
GET /analytics/applications/
```

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message 1", "Error message 2"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 429 Rate Limit Exceeded
```json
{
  "detail": "Request was throttled. Expected available in 60 seconds."
}
```

### 500 Internal Server Error
```json
{
  "detail": "An unexpected error occurred. Please try again later."
}
```

---

## Rate Limits

| Endpoint Group | Rate Limit |
|----------------|------------|
| Authentication | 10 requests/minute |
| Voice AI | 20 requests/minute |
| Job Search | 60 requests/minute |
| Applications | 30 requests/minute |
| General API | 100 requests/minute |

---

## WebSocket Events

### Notification Channel
```
ws://your-domain.com/ws/notifications/{user_id}/
```

**Events:**
```json
{
  "type": "new_application",
  "data": {
    "job_title": "Electrician Needed",
    "applicant_name": "Rahul Sharma",
    "ai_match_score": 85.5
  }
}
```

```json
{
  "type": "application_status_update",
  "data": {
    "job_title": "Electrician Needed",
    "company_name": "ABC Construction",
    "new_status": "interview_scheduled",
    "interview_date": "2026-07-28"
  }
}
```

```json
{
  "type": "new_job_alert",
  "data": {
    "job_id": "uuid",
    "title": "Electrician Needed",
    "salary_min": 25000,
    "location": "Whitefield, Bangalore"
  }
}
```
