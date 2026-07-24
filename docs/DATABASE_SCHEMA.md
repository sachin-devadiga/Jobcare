# JobCare Voice Database Schema

## Entity Relationship Diagram

```
┌─────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│      User       │       │  EmployeeProfile  │       │  EmployerProfile  │
├─────────────────┤       ├──────────────────┤       ├──────────────────┤
│ id (UUID, PK)   │──1:1──│ user_id (FK)      │       │ user_id (FK)      │
│ email           │       │ full_name         │       │ designation       │
│ phone           │       │ avatar            │       │ department        │
│ password        │       │ date_of_birth     │       │ company_id (FK)   │──1:1──┐
│ role (enum)     │       │ gender            │       │ is_verified       │       │
│ is_verified     │       │ address           │       │ verification_doc  │       │
│ is_active       │       │ city              │       └──────────────────┘       │
│ otp             │       │ state             │                                  │
│ otp_created_at  │       │ pincode           │       ┌──────────────────┐       │
│ fcm_token       │       │ latitude          │       │     Company      │◄──────┘
│ created_at      │       │ longitude         │       ├──────────────────┤
│ updated_at      │       │ skills (JSON)     │──1:N──│ id (UUID, PK)    │
└─────────────────┘       │ experience_years  │       │ name              │
        │                 │ education (JSON)  │       │ slug              │
        │ 1:N             │ languages (JSON)  │       │ logo              │
        ▼                 │ certificates(JSON)│       │ cover_image       │
┌─────────────────┐       │ resume_url        │       │ description       │
│  Notification   │       │ voice_resume_url  │       │ website           │
├─────────────────┤       │ expected_salary   │       │ industry (enum)   │
│ id (UUID, PK)   │       │ pref_categories   │       │ size (enum)       │
│ user_id (FK)    │       │ pref_locations    │       │ founded_year      │
│ type (enum)     │       │ availability(enum)│       │ headquarters      │
│ title           │       │ aadhaar_number    │       │ locations (JSON)  │
│ message         │       │ aadhaar_verified  │       │ is_verified       │
│ data (JSON)     │       │ profile_completion│       │ social_links(JSON)│
│ is_read         │       │ is_profile_complete│      │ contact_email     │
│ created_at      │       │ created_at        │       │ contact_phone     │
└─────────────────┘       │ updated_at        │       │ created_at        │
                          └──────────────────┘       │ updated_at        │
                                                      └──────────────────┘
        ┌──────────────────┐                                  │
        │     Category     │                                  │ 1:N
        ├──────────────────┤                                  │
        │ id (UUID, PK)    │◄────┐                            ▼
        │ name             │     │      ┌──────────────────────────────┐
        │ icon             │     │      │            Job              │
        │ slug             │     ├──────├──────────────────────────────┤
        │ created_at       │     │      │ id (UUID, PK)                │
        └──────────────────┘     │      │ company_id (FK)              │
                                 │      │ employer_id (FK)             │
        ┌──────────────────┐     │      │ category_id (FK)             │
        │      Skill       │     │      │ title                        │
        ├──────────────────┤     │      │ slug                         │
        │ id (UUID, PK)    │     │      │ description                  │
        │ category_id (FK) │─────┘      │ responsibilities (JSON)      │
        │ name             │            │ requirements (JSON)          │
        │ created_at       │            │ skills_required (JSON)       │
        └──────────────────┘            │ experience_min               │
                                        │ experience_max               │
        ┌──────────────────┐            │ salary_min                   │
        │      City        │            │ salary_max                   │
        ├──────────────────┤            │ salary_type (enum)           │
        │ id (UUID, PK)    │            │ location                     │
        │ name             │            │ city                         │
        │ state            │            │ state                        │
        │ latitude         │            │ latitude                     │
        │ longitude        │            │ longitude                    │
        │ created_at       │            │ job_type (enum)              │
        └──────────────────┘            │ shift_timing (enum)          │
                                        │ education_required (JSON)    │
                                        │ benefits (JSON)              │
                                        │ openings                     │
                                        │ urgency (enum)               │
                                        │ status (enum)                │
                                        │ is_featured                  │
                                        │ is_urgent                    │
                                        │ views_count                  │
                                        │ application_count            │
                                        │ save_count                   │
                                        │ created_at                   │
                                        │ updated_at                   │
                                        │ expires_at                   │
                                        └──────────────────────────────┘
                                                     │ 1:N
                                                     ▼
                                        ┌──────────────────────────────┐
                                        │        Application           │
                                        ├──────────────────────────────┤
                                        │ id (UUID, PK)                │
                                        │ job_id (FK)                  │
                                        │ employee_id (FK)             │
                                        │ status (enum)                │
                                        │ cover_letter                 │
                                        │ resume_url                   │
                                        │ voice_resume_url             │
                                        │ ai_match_score               │
                                        │ employer_notes               │
                                        │ rejection_reason             │
                                        │ interview_date               │
                                        │ interview_time               │
                                        │ interview_location           │
                                        │ interview_type (enum)        │
                                        │ offer_letter_url             │
                                        │ joined_date                  │
                                        │ created_at                   │
                                        │ updated_at                   │
                                        └──────────────────────────────┘

┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
│  SubscriptionPlan    │    │    Subscription       │    │      Payment         │
├──────────────────────┤    ├──────────────────────┤    ├──────────────────────┤
│ id (UUID, PK)        │──1:N│ id (UUID, PK)        │    │ id (UUID, PK)        │
│ name                 │    │ user_id (FK)          │    │ user_id (FK)          │
│ description          │    │ plan_id (FK)          │    │ subscription_id (FK)  │
│ price                │    │ status (enum)         │    │ razorpay_order_id    │
│ billing_cycle (enum) │    │ start_date            │    │ razorpay_payment_id  │
│ features (JSON)      │    │ end_date              │    │ razorpay_signature   │
│ plan_type (enum)     │    │ auto_renew            │    │ amount               │
│ is_active            │    │ created_at            │    │ currency             │
│ created_at           │    │ updated_at            │    │ status (enum)        │
└──────────────────────┘    └──────────────────────┘    │ payment_method       │
                                                         │ created_at           │
┌──────────────────────┐    ┌──────────────────────┐    └──────────────────────┘
│    VoiceSession      │    │    InterviewSchedule  │
├──────────────────────┤    ├──────────────────────┤
│ id (UUID, PK)        │    │ id (UUID, PK)        │
│ user_id (FK)         │    │ application_id (FK)  │
│ session_type (enum)  │    │ employer_id (FK)     │
│ input_text           │    │ employee_id (FK)     │
│ output_text          │    │ schedule_date        │
│ input_audio_url      │    │ schedule_time        │
│ output_audio_url     │    │ interview_type (enum)│
│ language             │    │ location             │
│ confidence           │    │ meeting_link         │
│ processing_time_ms   │    │ notes                │
│ status (enum)        │    │ status (enum)        │
│ created_at           │    │ reminders_sent       │
└──────────────────────┘    │ created_at           │
                             │ updated_at           │
                             └──────────────────────┘

┌──────────────────────┐    ┌──────────────────────┐
│       Device         │    │     AuditLog         │
├──────────────────────┤    ├──────────────────────┤
│ id (UUID, PK)        │    │ id (UUID, PK)        │
│ user_id (FK)         │    │ user_id (FK, null)   │
│ fcm_token            │    │ action               │
│ device_type (enum)   │    │ entity_type          │
│ device_id            │    │ entity_id            │
│ is_active            │    │ changes (JSON)       │
│ created_at           │    │ ip_address           │
│ updated_at           │    │ user_agent           │
└──────────────────────┘    │ created_at           │
                             └──────────────────────┘
```

## Enums

### User Role
```
employee, employer, admin
```

### Job Type
```
full_time, part_time, contract, internship, remote
```

### Shift Timing
```
day, night, flexible
```

### Salary Type
```
monthly, yearly, hourly
```

### Job Urgency
```
high, medium, low
```

### Job Status
```
active, paused, closed, filled
```

### Application Status
```
applied, under_review, shortlisted, interview_scheduled, selected, rejected, withdrawn
```

### Interview Type
```
in_person, video, call
```

### Availability
```
immediate, notice_period, not_available
```

### Notification Type
```
job_alert, application_update, interview_schedule, offer_letter, system_announcement, message, voice_assistant
```

### Session Type
```
voice_search, voice_apply, voice_navigate, voice_question, interview_practice
```

### Billing Cycle
```
monthly, quarterly, yearly
```

### Plan Type
```
free, basic, professional, enterprise
```

### Subscription Status
```
active, expiring, expired, cancelled, paused
```

### Payment Status
```
created, authorized, captured, failed, refunded
```

### Company Industry
```
construction, manufacturing, logistics, hospitality, healthcare, retail, technology, staffing, education, other
```

### Company Size
```
1_10, 11_50, 51_200, 201_500, 501_1000, 1001_5000, 5000_plus
```

## Indexes

### Users
- `idx_user_email` ON email (UNIQUE)
- `idx_user_phone` ON phone (UNIQUE)
- `idx_user_role` ON role

### Jobs
- `idx_job_status` ON status
- `idx_job_category` ON category_id
- `idx_job_city` ON city
- `idx_job_job_type` ON job_type
- `idx_job_salary` ON salary_min, salary_max
- `idx_job_created` ON created_at DESC
- `idx_job_location` ON latitude, longitude (for nearby search)
- `idx_job_company` ON company_id
- `idx_job_featured_urgent` ON is_featured, is_urgent

### Applications
- `idx_app_job` ON job_id
- `idx_app_employee` ON employee_id
- `idx_app_status` ON status
- `idx_app_created` ON created_at DESC
- `idx_app_employee_job` ON employee_id, job_id (UNIQUE)

### Notifications
- `idx_notif_user` ON user_id
- `idx_notif_read` ON is_read
- `idx_notif_created` ON created_at DESC

### Payments
- `idx_pay_user` ON user_id
- `idx_pay_order` ON razorpay_order_id
- `idx_pay_status` ON status

### Voice Sessions
- `idx_voice_user` ON user_id
- `idx_voice_type` ON session_type
- `idx_voice_created` ON created_at DESC

## Foreign Key Constraints

| Constraint | From | To | On Delete |
|------------|------|----|-----------|
| fk_employee_profile_user | employee_profiles.user_id | users.id | CASCADE |
| fk_employer_profile_user | employer_profiles.user_id | users.id | CASCADE |
| fk_employer_profile_company | employer_profiles.company_id | companies.id | SET NULL |
| fk_job_company | jobs.company_id | companies.id | CASCADE |
| fk_job_employer | jobs.employer_id | users.id | CASCADE |
| fk_job_category | jobs.category_id | categories.id | RESTRICT |
| fk_application_job | applications.job_id | jobs.id | CASCADE |
| fk_application_employee | applications.employee_id | users.id | CASCADE |
| fk_notification_user | notifications.user_id | users.id | CASCADE |
| fk_subscription_user | subscriptions.user_id | users.id | CASCADE |
| fk_subscription_plan | subscriptions.plan_id | subscription_plans.id | RESTRICT |
| fk_payment_user | payments.user_id | users.id | CASCADE |
| fk_payment_subscription | payments.subscription_id | subscriptions.id | SET NULL |
| fk_voice_session_user | voice_sessions.user_id | users.id | CASCADE |
| fk_device_user | devices.user_id | users.id | CASCADE |
| fk_skill_category | skills.category_id | categories.id | CASCADE |

## Database Configuration

PostgreSQL 15 with the following extensions:
- `uuid-ossp` - UUID generation
- `pg_trgm` - Trigram search for text search
- `unaccent` - Accent-insensitive search
- `pg_stat_statements` - Query performance monitoring
