import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/providers.dart';
import '../providers/auth_provider.dart';
import '../screens/splash_screen.dart';
import '../screens/onboarding_screen.dart';
import '../screens/language_selection_screen.dart';
import '../screens/login_screen.dart';
import '../screens/signup_screen.dart';
import '../screens/otp_verification_screen.dart';
import '../screens/forgot_password_screen.dart';
import '../screens/home_screen.dart';
import '../screens/jobs_screen.dart';
import '../screens/job_detail_screen.dart';
import '../screens/search_results_screen.dart';
import '../screens/applications_screen.dart';
import '../screens/chat_list_screen.dart';
import '../screens/chat_screen.dart';
import '../screens/profile_screen.dart';
import '../screens/edit_profile_screen.dart';
import '../screens/settings_screen.dart';
import '../screens/voice_assistant_screen.dart';
import '../screens/voice_help_screen.dart';
import '../screens/notifications_screen.dart';
import '../screens/saved_jobs_screen.dart';
import '../screens/interview_schedule_screen.dart';
import '../screens/help_support_screen.dart';
import '../screens/voice_resume_screen.dart';
import '../theme/app_colors.dart';
import 'route_names.dart';

final _routerKey = GlobalKey<NavigatorState>();
final _shellKey = GlobalKey<NavigatorState>();

final routerProvider = Provider<GoRouter>((ref) {
  // Do not watch authProvider here. Watching it recreates GoRouter on every
  // auth state change, which removes the navigator's inherited routing tree
  // while route descendants can still depend on it.
  final router = GoRouter(
    navigatorKey: _routerKey,
    initialLocation: RouteNames.splash,
    debugLogDiagnostics: false,
    refreshListenable: ref.read(authProvider.notifier).listenable,
    redirect: (context, state) {
      final authState = ref.read(authProvider);
      final isLoggedIn = authState.status == AuthStatus.authenticated;
      final isSplash = state.matchedLocation == RouteNames.splash;
      final isPublicAuthRoute = state.matchedLocation == RouteNames.login ||
          state.matchedLocation == RouteNames.signup ||
          state.matchedLocation == RouteNames.otpVerification ||
          state.matchedLocation == RouteNames.forgotPassword ||
          state.matchedLocation == RouteNames.onboarding;
      // Language selection is shared by onboarding and Settings. It must stay
      // available to signed-in users so they can change the app language.
      final isLanguageSelection =
          state.matchedLocation == RouteNames.languageSelection;

      if (isSplash) return null;
      if (!isLoggedIn && !isPublicAuthRoute && !isLanguageSelection) {
        return RouteNames.login;
      }
      if (isLoggedIn && isPublicAuthRoute && !authState.isNewUser) {
        return RouteNames.home;
      }

      return null;
    },
    routes: [
      GoRoute(path: RouteNames.splash, name: 'splash', builder: (context, state) => const SplashScreen()),
      GoRoute(path: RouteNames.onboarding, name: 'onboarding', builder: (context, state) => const OnboardingScreen()),
      GoRoute(
        path: RouteNames.languageSelection,
        name: 'languageSelection',
        builder: (context, state) => LanguageSelectionScreen(
          returnToSettings: state.uri.queryParameters['from'] == 'settings',
        ),
      ),
      GoRoute(path: RouteNames.login, name: 'login', builder: (context, state) => const LoginScreen()),
      GoRoute(path: RouteNames.signup, name: 'signup', builder: (context, state) => const SignupScreen()),
      GoRoute(path: RouteNames.otpVerification, name: 'otpVerification', builder: (context, state) => const OtpVerificationScreen()),
      GoRoute(path: RouteNames.forgotPassword, name: 'forgotPassword', builder: (context, state) => const ForgotPasswordScreen()),

      ShellRoute(
        navigatorKey: _shellKey,
        builder: (context, state, child) {
          final location = state.matchedLocation;
          int currentIndex = 0;
          if (location.startsWith(RouteNames.jobs)) currentIndex = 1;
          if (location.startsWith(RouteNames.applications)) currentIndex = 2;
          if (location.startsWith(RouteNames.messages)) currentIndex = 3;
          if (location.startsWith(RouteNames.profile)) currentIndex = 4;

          return HomeShell(child: child, currentIndex: currentIndex);
        },
        routes: [
          GoRoute(
            path: RouteNames.home,
            name: 'home',
            builder: (context, state) => const HomeScreen(),
            routes: [
              GoRoute(
                path: '${RouteNames.jobDetail.substring(1)}/:id',
                name: 'jobDetail',
                builder: (context, state) => JobDetailScreen(jobId: state.pathParameters['id']!),
              ),
            ],
          ),
          GoRoute(path: RouteNames.jobs, name: 'jobs', builder: (context, state) => const JobsScreen()),
          GoRoute(path: RouteNames.applications, name: 'applications', builder: (context, state) => const ApplicationsScreen()),
          GoRoute(path: RouteNames.messages, name: 'messages', builder: (context, state) => const ChatListScreen()),
          GoRoute(path: RouteNames.profile, name: 'profile', builder: (context, state) => const ProfileScreen()),
        ],
      ),

      GoRoute(path: RouteNames.searchResults, name: 'searchResults', builder: (context, state) => SearchResultsScreen(query: state.uri.queryParameters['query'] ?? '')),
      GoRoute(path: RouteNames.voiceAssistant, name: 'voiceAssistant', builder: (context, state) => const VoiceAssistantScreen()),
      GoRoute(path: RouteNames.voiceHelp, name: 'voiceHelp', builder: (context, state) => const VoiceHelpScreen()),
      GoRoute(path: RouteNames.voiceResume, name: 'voiceResume', builder: (context, state) => const VoiceResumeScreen()),
      GoRoute(path: RouteNames.editProfile, name: 'editProfile', builder: (context, state) => const EditProfileScreen()),
      GoRoute(path: RouteNames.settings, name: 'settings', builder: (context, state) => const SettingsScreen()),
      GoRoute(path: RouteNames.notifications, name: 'notifications', builder: (context, state) => const NotificationsScreen()),
      GoRoute(path: RouteNames.savedJobs, name: 'savedJobs', builder: (context, state) => const SavedJobsScreen()),
      GoRoute(path: RouteNames.interviewSchedule, name: 'interviewSchedule', builder: (context, state) => const InterviewScheduleScreen()),
      GoRoute(path: RouteNames.helpSupport, name: 'helpSupport', builder: (context, state) => const HelpSupportScreen()),
    ],
  );

  // GoRouter registers listeners with its refreshListenable. Dispose it before
  // this provider releases the AuthNotifier's ChangeNotifier.
  ref.onDispose(router.dispose);
  return router;
});

class HomeShell extends StatelessWidget {
  final Widget child;
  final int currentIndex;
  const HomeShell({super.key, required this.child, required this.currentIndex});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, -4))],
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _NavItem(icon: Icons.home_filled, label: 'Home', isActive: currentIndex == 0, onTap: () => context.go(RouteNames.home)),
                _NavItem(icon: Icons.work_rounded, label: 'Jobs', isActive: currentIndex == 1, onTap: () => context.go(RouteNames.jobs)),
                _NavItem(icon: Icons.assignment_rounded, label: 'Applied', isActive: currentIndex == 2, onTap: () => context.go(RouteNames.applications)),
                _NavItem(icon: Icons.chat_bubble_rounded, label: 'Chats', isActive: currentIndex == 3, onTap: () => context.go(RouteNames.messages)),
                _NavItem(icon: Icons.person_rounded, label: 'Profile', isActive: currentIndex == 4, onTap: () => context.go(RouteNames.profile)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isActive;
  final VoidCallback onTap;

  const _NavItem({required this.icon, required this.label, required this.isActive, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final color = isActive ? AppColors.primary : AppColors.textSecondary;
    return GestureDetector(
      onTap: onTap,
      behavior: HitTestBehavior.opaque,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: 26),
          const SizedBox(height: 4),
          Text(label, style: TextStyle(color: color, fontSize: 11, fontWeight: isActive ? FontWeight.bold : FontWeight.w500)),
        ],
      ),
    );
  }
}
