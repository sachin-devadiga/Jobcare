# JobCare Voice Developer Guide

## Architecture Overview

JobCare Voice follows a modern microservices-inspired architecture with three main components:

```
┌─────────────────────────────────────────────────────────┐
│                    Mobile App (Flutter)                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  UI Layer (Screens + Widgets)                    │   │
│  │  State Management (Riverpod)                     │   │
│  │  Services (API, Storage, Voice)                  │   │
│  │  Repositories (Data Access)                      │   │
│  └──────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP/REST + WebSocket
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  Django Backend (REST API)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Auth     │  │ Jobs     │  │ Apps     │  │ Voice  │ │
│  │ Service  │  │ Service  │  │ Service  │  │ AI     │ │
│  ├──────────┤  ├──────────┤  ├──────────┤  ├────────┤ │
│  │ Payments │  │ Notif.   │  │ Analytics│  │ Users  │ │
│  │ Service  │  │ Service  │  │ Service  │  │ Service│ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Repository Layer (Data Access Pattern)          │   │
│  │  Service Layer (Business Logic)                  │   │
│  │  Serializer Layer (Validation)                   │   │
│  └──────────────────────────────────────────────────┘   │
└───────┬────────────────────────────┬────────────────────┘
        │                            │
        ▼                            ▼
┌──────────────┐           ┌──────────────────┐
│  PostgreSQL   │           │      Redis       │
│  (Primary DB) │           │  (Cache + Queue) │
└──────────────┘           └──────────────────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │  Celery Workers   │
                          │  (Async Tasks)    │
                          └──────────────────┘
```

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Maximum line length: 88 characters (Black formatter)
- Use docstrings for all public functions and classes
- Follow Django best practices (fat models, thin views)
- Repository pattern for data access
- Service layer for business logic

### Python Code Style

```python
from typing import Optional

from django.db import models


class Job(models.Model):
    """Represents a job listing posted by an employer."""

    title: str = models.CharField(max_length=255)
    description: str = models.TextField()
    salary_min: int = models.PositiveIntegerField()
    salary_max: int = models.PositiveIntegerField()
    created_at: datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["salary_min", "salary_max"]),
        ]

    def __str__(self) -> str:
        return self.title
```

### Dart (Flutter)

- Follow Dart effective style guide
- Use `const` constructors where possible
- Extract widgets for reusable components
- Use Riverpod for state management
- Follow repository pattern for data access
- Use proper error handling with Either/Result types

### Dart Code Style

```dart
class JobModel {
  final String id;
  final String title;
  final int salaryMin;
  final int salaryMax;
  final DateTime createdAt;

  const JobModel({
    required this.id,
    required this.title,
    required this.salaryMin,
    required this.salaryMax,
    required this.createdAt,
  });

  factory JobModel.fromJson(Map<String, dynamic> json) {
    return JobModel(
      id: json['id'] as String,
      title: json['title'] as String,
      salaryMin: json['salary_min'] as int,
      salaryMax: json['salary_max'] as int,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'salary_min': salaryMin,
      'salary_max': salaryMax,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
```

## Git Workflow

### Branch Strategy

```
main ────── tags: v1.0.0, v1.1.0
  ├── develop
  │     ├── feature/voice-search
  │     ├── feature/payment-integration
  │     ├── bugfix/login-error
  │     └── ...
  └── release/v1.0.0
        └── hotfix/critical-bug
```

### Commit Convention

```
<type>(<scope>): <description>

Types:
  feat:     New feature
  fix:      Bug fix
  refactor: Code refactoring
  style:    Formatting, styling
  docs:     Documentation
  test:     Testing
  chore:    Maintenance, dependencies

Examples:
  feat(jobs): add nearby job search endpoint
  fix(auth): resolve JWT refresh token expiration
  refactor(voice): extract Sarvam AI service
  docs(api): update application endpoints
```

## Development Workflow

### 1. Local Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/jobcare-voice.git
cd jobcare-voice

# Set up environment
cp .env.example .env

# Start Docker services
docker-compose up -d postgres redis

# Create virtual environment and install dependencies
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Load seed data
python manage.py seed_data

# Start development server
python manage.py runserver
```

### 2. Testing

```bash
# Backend tests
cd backend
pytest
pytest --cov=. --cov-report=html

# Flutter tests
cd frontend_mobile
flutter test
flutter test --coverage

# Web dashboard tests
cd frontend_web
npm test
npm run test:coverage
```

### 3. Code Quality

```bash
# Backend
flake8 backend/
black --check backend/
isort --check backend/
mypy backend/

# Flutter
flutter analyze
dart format --set-exit-if-changed lib/

# Web
npm run lint
npm run format:check
```

### 4. Building

```bash
# Docker build
docker-compose build

# Flutter APK
cd frontend_mobile
flutter build apk --release
flutter build appbundle --release

# Flutter iOS
flutter build ios --release

# Web dashboard
cd frontend_web
npm run build
```

## API Development Guidelines

### Adding a New Endpoint

1. Create serializer in `serializers.py`
2. Create/add view in `views.py`
3. Add URL pattern in `urls.py`
4. Add service method in `services.py` (if needed)
5. Add repository method in `repositories/` (if needed)
6. Write tests
7. Add Swagger documentation decorators
8. Run migrations (if model changes)

### Example

```python
# serializers.py
class NewFeatureSerializer(serializers.Serializer):
    field1 = serializers.CharField()
    field2 = serializers.IntegerField(min_value=0)

# views.py
class NewFeatureView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=NewFeatureSerializer,
        responses={200: SuccessSerializer}
    )
    def post(self, request):
        serializer = NewFeatureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Business logic
        return Response({"message": "Success"}, status=200)

# urls.py
urlpatterns = [
    path('new-feature/', NewFeatureView.as_view(), name='new-feature'),
]
```

## Mobile App Development Guidelines

### Adding a New Screen

1. Create screen in `lib/screens/`
2. Add route in `lib/routes/app_router.dart`
3. Add provider in `lib/providers/`
4. Create/update service in `lib/services/`
5. Create/update repository in `lib/repositories/`

### State Management Pattern

```dart
// 1. Create a Provider
final jobProvider = StateNotifierProvider<JobNotifier, AsyncValue<List<JobModel>>>((ref) {
  return JobNotifier(ref.read(jobRepositoryProvider));
});

// 2. Create a StateNotifier
class JobNotifier extends StateNotifier<AsyncValue<List<JobModel>>> {
  final JobRepository _repository;

  JobNotifier(this._repository) : super(const AsyncValue.loading());

  Future<void> fetchJobs() async {
    try {
      state = const AsyncValue.loading();
      final jobs = await _repository.getJobs();
      state = AsyncValue.data(jobs);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

// 3. Use in UI
final jobsAsync = ref.watch(jobProvider);
jobsAsync.when(
  data: (jobs) => ListView.builder(itemBuilder: ...),
  loading: () => const ShimmerLoading(),
  error: (e, _) => ErrorWidget(message: e.toString(), onRetry: () => ref.refresh(jobProvider)),
);
```

## Web Dashboard Development Guidelines

### Adding a New Page

1. Create page in `src/pages/employer/`
2. Add route in `src/components/layout/Sidebar.jsx`
3. Create service methods in `src/services/`
4. Add API endpoint in Django backend

### Component Pattern

```jsx
import React, { useState, useEffect } from 'react';
import { Box, Typography, Card } from '@mui/material';
import { useAuth } from '../../hooks/useAuth';
import jobService from '../../services/jobService';

export default function MyComponent() {
  const { user } = useAuth();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await jobService.getData();
      setData(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;
  if (!data.length) return <EmptyState message="No data found" />;

  return (
    <Box>
      {data.map(item => (
        <Card key={item.id}>{/* content */}</Card>
      ))}
    </Box>
  );
}
```

## Voice AI Integration

### Sarvam AI API

JobCare Voice uses Sarvam AI for all voice-related features:

- **Speech-to-Text (STT)**: Convert user voice to text in multiple Indian languages
- **Text-to-Speech (TTS)**: Convert AI responses to natural-sounding speech
- **Voice Search**: Process voice queries and translate to structured job searches

### Voice Service Architecture

```python
# backend/voice_ai/services.py
class SarvamAIService:
    def speech_to_text(self, audio_file: File, language: str) -> dict:
        """Convert speech to text using Sarvam AI."""

    def text_to_speech(self, text: str, language: str, gender: str) -> bytes:
        """Convert text to speech using Sarvam AI."""

    def voice_search(self, audio_file: File) -> dict:
        """Process voice query and return job search results."""

    def process_voice_command(self, transcript: str) -> dict:
        """Parse voice command and determine intent (search, navigate, apply)."""
```

## Error Handling

### Backend

```python
# Custom exception handler
from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data['status_code'] = response.status_code
    return response
```

### Mobile App

```dart
// API error handling
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final Map<String, dynamic>? errors;

  ApiException({required this.message, this.statusCode, this.errors});

  @override
  String toString() => message;
}
```

### Web Dashboard

```jsx
// Error boundary component
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorState message="Something went wrong" onRetry={() => this.setState({ hasError: false })} />;
    }
    return this.props.children;
  }
}
```

## Environment Configuration

Each component requires specific environment variables:

### Backend (.env)
```
DJANGO_SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
REDIS_URL=
CELERY_BROKER_URL=
JWT_SECRET_KEY=
JWT_ACCESS_TOKEN_LIFETIME=
JWT_REFRESH_TOKEN_LIFETIME=
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
SARVAM_API_KEY=
SARVAM_API_URL=
FCM_CREDENTIALS=
GOOGLE_MAPS_API_KEY=
CORS_ALLOWED_ORIGINS=
SENTRY_DSN=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=
```

### Flutter (.env)
```
API_BASE_URL=
GOOGLE_MAPS_API_KEY=
RAZORPAY_KEY_ID=
FCM_SENDER_ID=
```

### Web (.env.local)
```
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_RAZORPAY_KEY_ID=
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=
```

## Performance Optimization

### Backend
- Use `select_related` and `prefetch_related` for related fields
- Add database indexes for frequently queried fields
- Use Redis caching for expensive queries
- Paginate all list endpoints
- Use asynchronous task processing (Celery) for heavy operations

### Mobile App
- Use `CachedNetworkImage` for image caching
- Implement pagination with `ScrollController`
- Use `const` constructors to reduce rebuilds
- Lazy load screens with `Navigator`
- Optimize assets (compress images, use vector graphics)

### Web Dashboard
- Implement code splitting with dynamic imports
- Use Next.js Image component for optimization
- Debounce search inputs
- Use memo and useMemo for expensive computations
- Virtualize long lists

## Security Checklist

- [ ] All API endpoints require authentication (except auth endpoints)
- [ ] JWT tokens stored securely (FlutterSecureStorage, httpOnly cookies)
- [ ] Input validation on all endpoints
- [ ] Rate limiting configured
- [ ] CORS configured properly
- [ ] SQL injection protection (use ORM, not raw queries)
- [ ] XSS protection (template escaping, Content-Security-Policy)
- [ ] CSRF protection enabled
- [ ] Passwords hashed with strong algorithm
- [ ] File upload validation (type, size)
- [ ] Environment variables never committed
- [ ] Regular dependency updates
- [ ] HTTPS enforced in production
