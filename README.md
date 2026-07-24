# JobCare Voice - Employee App

## India's First AI Voice Job Platform for Workers

JobCare Voice is a revolutionary AI-powered job platform designed specifically for blue-collar and grey-collar workers in India. This repository contains the **Employee Mobile Application**, which allows workers to search and apply for jobs using natural voice commands in their preferred Indian languages.

---

## Key Features (Mobile App)

### 🎙️ AI Voice Assistant
- **Voice-First Navigation**: Move between screens using voice (e.g., "Go to my profile").
- **Smart Job Search**: "Find delivery jobs in Bangalore with salary above 20,000".
- **Multilingual Support**: Powered by Sarvam AI for regional languages (Hindi, Tamil, Telugu, etc.).

### 📄 Smart Voice Resume
- **No Typing Required**: Record a 30-second introduction instead of building a text CV.
- **AI Matching**: Matches your profile to jobs based on your spoken skills.

### 📍 Location & Nearby Jobs
- **Map Discovery**: Find jobs within walking or easy commuting distance.
- **Commute Filtering**: Filter jobs by distance (5km, 10km).

### ⚡ Professional Tracking
- **Application Status**: Real-time updates on your job applications.
- **Interview Scheduling**: Voice-enabled scheduling for upcoming interviews.

---

## Tech Stack

- **Framework**: Flutter (Latest Stable)
- **State Management**: Riverpod (Clean Architecture)
- **Navigation**: Go Router
- **Backend API**: Django 5 + PostgreSQL
- **AI**: Sarvam AI (STT/TTS)

---

## UI/UX Design Principles
- **Accessibility**: High contrast and large font sizes for better readability.
- **Touch Targets**: Large buttons for easy navigation in various work environments.
- **Visual Cues**: Strong use of icons and color-coding for job categories.

---

## Project Structure (Focus: Mobile)

```
jobcare_voice/
├── frontend_mobile/            # Flutter Employee App
│   ├── lib/
│   │   ├── core/               # Theme, constants, di
│   │   ├── screens/            # UI Screens
│   │   ├── providers/          # Riverpod logic
│   │   ├── services/           # Remote & Local services
│   │   └── widgets/            # Reusable UI components
│   └── ...
├── backend/                    # Django API Support
└── ...
```

## Quick Start (Mobile)

1. **Clone & Install**
```bash
cd frontend_mobile
flutter pub get
```

2. **Run the app**
```bash
flutter run
```
