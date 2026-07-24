# Release Checklist - JobCare Voice

## Pre-release Tasks

### Code Freeze
- [ ] All feature branches merged to `main`
- [ ] No unmerged PRs targeted for this release
- [ ] Release branch created (`release/v<version>`)
- [ ] All team members notified of code freeze

### Version Bump
- [ ] Update version in `frontend_mobile/pubspec.yaml`
- [ ] Update version in `backend/config/settings.py` (API version)
- [ ] Update version in `frontend_web/package.json`
- [ ] Update `CHANGELOG.md` with release notes

### Dependency Audit
- [ ] Run `flutter pub outdated` - review and update dependencies
- [ ] Run `pip list --outdated` - review Python dependencies
- [ ] Run `npm outdated` - review web dependencies
- [ ] Check for security vulnerabilities:
  - Flutter: `flutter pub audit`
  - Python: `safety check` or `pip-audit`
  - Web: `npm audit`

---

## Build Verification Steps

### Flutter Mobile App
- [ ] `flutter clean`
- [ ] `flutter pub get`
- [ ] `flutter analyze` - 0 errors, 0 warnings
- [ ] `flutter test` - all tests passing
- [ ] `flutter build apk --release` - successful build
- [ ] `flutter build appbundle --release` - successful build
- [ ] `flutter build ios --release` - successful build (macOS only)
- [ ] Verify APK size is within limits
- [ ] Verify app bundle size is within Play Store limits

### Django Backend
- [ ] `python manage.py check --deploy` - no warnings
- [ ] `python manage.py makemigrations --check` - no pending migrations
- [ ] `python manage.py collectstatic --noinput` - successful
- [ ] `pytest` - all tests passing
- [ ] Coverage report: `pytest --cov --cov-report=html`
- [ ] API documentation generates correctly: `python manage.py spectacular --file schema.yml`

### Web Dashboard (Next.js)
- [ ] `npm run build` - successful build
- [ ] `npm run lint` - no errors
- [ ] `npm run test` - all tests passing
- [ ] Verify build output size

### Docker
- [ ] `docker-compose build` - all images build successfully
- [ ] `docker-compose up` - all services start correctly
- [ ] Container health checks pass

---

## Testing Signoff

### Manual Testing Checklist

#### Authentication & Onboarding
- [ ] User registration with phone number works
- [ ] OTP verification works correctly
- [ ] Google Sign-In works
- [ ] User profile creation flow works
- [ ] Language selection persists correctly
- [ ] Voice introduction/setup works

#### Job Search & Discovery
- [ ] Browse jobs by category works
- [ ] Voice search returns accurate results
- [ ] Text search with filters works
- [ ] Nearby jobs (location-based) works
- [ ] Job details page loads correctly
- [ ] Infinite scroll works on job listings

#### Application Process
- [ ] Apply to job works (with voice/text)
- [ ] Voice resume upload works
- [ ] Document upload works
- [ ] Application status tracking works
- [ ] Withdraw application works

#### Voice AI Features
- [ ] Speech-to-text works in supported languages
- [ ] Text-to-speech works clearly
- [ ] Voice commands (navigate, search, apply) work
- [ ] Voice search handles multiple languages
- [ ] Offline voice commands work (cached)

#### Notifications
- [ ] Push notifications arrive correctly
- [ ] Local notifications work (job alerts)
- [ ] Notification deep linking works
- [ ] Notification preferences save correctly

#### Employer Features
- [ ] Company profile creation works
- [ ] Job posting flow works
- [ ] Applicant list loads correctly
- [ ] Voice resume playback works
- [ ] Applicant status update works

#### Payments
- [ ] Razorpay checkout opens correctly
- [ ] Payment success/failure handled correctly
- [ ] Subscription management works
- [ ] Payment history displays correctly

#### Cross-cutting
- [ ] Dark mode toggle works
- [ ] Language switching works throughout app
- [ ] Offline mode shows cached content
- [ ] Data sync when back online
- [ ] App reload/resume works correctly
- [ ] Deep links open correct screens
- [ ] Push notification taps open correct screens

### Regression Test Results
- [ ] Critical flow tests: PASS
- [ ] Edge case tests: PASS
- [ ] Error handling tests: PASS
- [ ] Performance benchmarks met

### Accessibility
- [ ] Screen reader compatibility tested
- [ ] Minimum touch target sizes met
- [ ] Color contrast ratios meet WCAG AA
- [ ] Font scaling works correctly

---

## Security Review

### Authentication
- [ ] JWT access tokens expire correctly
- [ ] JWT refresh token rotation works
- [ ] Token blacklisting after logout
- [ ] OTP rate limiting is enforced
- [ ] Failed login attempts are limited

### Data Protection
- [ ] All API endpoints require auth (except public)
- [ ] Passwords hashed with Argon2
- [ ] Sensitive data encrypted at rest
- [ ] HTTPS enforced (HSTS configured)
- [ ] `SECURE_SSL_REDIRECT` is enabled
- [ ] `SESSION_COOKIE_SECURE` is True
- [ ] `CSRF_COOKIE_SECURE` is True
- [ ] `X_FRAME_OPTIONS` is 'DENY'

### API Security
- [ ] Rate limiting is active on all endpoints
- [ ] Input validation on all endpoints
- [ ] File upload validation and size limits
- [ ] No sensitive data in error responses
- [ ] CORS is properly restricted
- [ ] SQL injection prevention (ORM only)

### Infrastructure
- [ ] Debug mode is False
- [ ] Secret key is not default
- [ ] All secrets are environment variables
- [ ] `.env` files are not in version control
- [ ] `key.properties` is not in version control
- [ ] Firebase config files are not in version control
- [ ] Google Services plist/json not in version control

---

## Performance Benchmarks

### Mobile App
- [ ] App cold start < 3 seconds
- [ ] App warm start < 1.5 seconds
- [ ] Screen transitions < 300ms
- [ ] Job list load (20 items) < 2 seconds
- [ ] Voice search response < 3 seconds
- [ ] Image load (cached) < 500ms
- [ ] APK size < 80MB
- [ ] Memory usage < 200MB
- [ ] Battery drain (30 min usage) < 5%

### Backend API
- [ ] API response time (p50) < 200ms
- [ ] API response time (p99) < 1s
- [ ] Concurrent users supported: 1000+
- [ ] Database query time (p50) < 50ms
- [ ] Voice AI processing < 5 seconds

### Load Test Results
- [ ] 100 concurrent users: PASS
- [ ] 500 concurrent users: PASS
- [ ] 1000 concurrent users: PASS (target)
- [ ] Sustained load for 1 hour: PASS

---

## Deployment Steps

### Pre-deployment
- [ ] Database migration backed up
- [ ] Media files backed up
- [ ] Current configuration backed up
- [ ] Maintenance page ready (if needed)
- [ ] DNS records verified
- [ ] SSL certificates valid (not expiring soon)
- [ ] CDN purged (if using)

### Backend Deployment
```bash
# 1. SSH into production server
ssh deploy@jobcarevoice.com

# 2. Pull latest code
cd /opt/jobcare-voice
git pull origin main

# 3. Build and restart containers
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 4. Run database migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 5. Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# 6. Verify services are healthy
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml exec backend python manage.py check --deploy
```

### Mobile App Deployment

#### Google Play Store
```bash
# Build release AAB
cd frontend_mobile
flutter build appbundle --release

# Upload via Play Console or Fastlane
fastlane android deploy_play_store_production
```

#### Apple App Store
```bash
# Build release IPA
cd frontend_mobile
flutter build ios --release

# Upload via Xcode or Fastlane
fastlane ios deploy_app_store
```

### Web Dashboard
```bash
cd frontend_web
npm run build
# Upload dist/ folder to CDN or web server
```

---

## Post-deployment Monitoring

### Immediate Checks (First 30 minutes)
- [ ] Health check endpoint returns 200: `GET /api/v1/health/`
- [ ] Prometheus metrics endpoint accessible
- [ ] Sentry error rate normal (< 0.1%)
- [ ] API response times within baseline
- [ ] Database connection pool stable
- [ ] Redis memory usage normal
- [ ] No 5xx errors in logs
- [ ] New users can register
- [ ] Login flow works
- [ ] Payment flow works

### Short-term Monitoring (First 24 hours)
- [ ] Crash-free rate > 99.5%
- [ ] ANR rate < 0.1%
- [ ] Average session length normal
- [ ] Push notification delivery rate > 95%
- [ ] Voice AI response time within limits
- [ ] Server CPU/memory usage stable
- [ ] Database query performance stable
- [ ] No unusual error patterns

### Long-term Monitoring (First Week)
- [ ] User retention metrics normal
- [ ] App rating/reviews monitored
- [ ] Support tickets volume normal
- [ ] API usage within expected range
- [ ] Cost monitoring (server, API calls)
- [ ] Gradual rollout expanding (if staged)

---

## Rollback Procedure

### Backend Rollback
```bash
# Option 1: Revert to previous Docker image
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d <previous-image-tag>

# Option 2: Git revert
git revert HEAD --no-edit
git push origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Option 3: Database rollback (if migration caused issues)
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate <app_name> <previous_migration>
```

### Mobile App Rollback
- **Android**: Use Play Console to revert to previous version (keep current as draft)
- **iOS**: Use App Store Connect to remove the build (or push update)
- **Force update**: If critical, use remote config to force update from previous version

### Web Dashboard Rollback
- Redeploy previous `dist/` folder
- If using CDN, point to previous version

### Database Restore
```bash
# Restore from latest backup
./scripts/restore.sh --latest

# Restore specific backup
./scripts/restore.sh --file /backups/jobcare_db_2024-01-01.sql
```

### Communication During Rollback
- [ ] Notify team via Slack/email
- [ ] Update status page
- [ ] Log incident in tracking system
- [ ] Post-mortem scheduled

---

## Release Notes Template

```markdown
# Release v<version> - <date>

## Highlights
- Brief summary of major features and improvements

## New Features
- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## Improvements
- Improvement 1: Description
- Improvement 2: Description

## Bug Fixes
- Fix 1: Description (Issue #)
- Fix 2: Description (Issue #)

## Performance
- Performance improvement 1
- Performance improvement 2

## Security
- Security fix 1
- Security fix 2

## Breaking Changes
- Breaking change 1 (if any)
- Breaking change 2 (if any)

## Known Issues
- Known issue 1
- Known issue 2

## Build Information
- Flutter version: 3.x.x
- Dart version: 3.x.x
- Python version: 3.13.x
- Django version: 5.x.x
- Node.js version: 20.x.x

## Assets
- Android APK: jobcare-voice-v<version>-release.apk
- Android AAB: jobcare-voice-v<version>-release.aab
- iOS IPA: JobCare_Voice_v<version>.ipa
```

---

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Manager | | | |
| Lead Developer | | | |
| QA Lead | | | |
| Security Lead | | | |
| DevOps Lead | | | |

---

*Last updated: $(date +%Y-%m-%d)*
