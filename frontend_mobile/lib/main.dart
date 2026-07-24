import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'providers/providers.dart';
import 'routes/app_router.dart';
import 'routes/route_names.dart';
import 'theme/app_theme.dart';
import 'widgets/voice_floating_button.dart';

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
    FlutterLocalNotificationsPlugin();

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  try {
    await Firebase.initializeApp();
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings();
    await flutterLocalNotificationsPlugin.initialize(
      const InitializationSettings(android: androidSettings, iOS: iosSettings),
    );
  } catch (_) {}

  runApp(const ProviderScope(child: JobCareVoiceApp()));
}

class JobCareVoiceApp extends ConsumerWidget {
  const JobCareVoiceApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    final themeMode = ref.watch(themeModeProvider);
    final lang = ref.watch(languageProvider);

    return ScreenUtilInit(
      designSize: const Size(390, 844),
      minTextAdapt: true,
      splitScreenMode: true,
      builder: (context, child) {
        return MaterialApp.router(
          title: 'JobCare Voice',
          debugShowCheckedModeBanner: false,
          theme: AppTheme.light(lang),
          darkTheme: AppTheme.dark(lang),
          themeMode: themeMode,
          routerConfig: router,
          builder: (context, child) {
            return Stack(
              children: [
                if (child != null) child,
                // Safely handle global Voice FAB visibility
                Consumer(
                  builder: (context, ref, _) {
                    final config = router.routerDelegate.currentConfiguration;
                    final String path = config?.uri.path ?? '';
                    
                    final List<String> hiddenPaths = [
                      RouteNames.splash,
                      RouteNames.onboarding,
                      RouteNames.languageSelection,
                      RouteNames.login,
                      RouteNames.signup,
                      RouteNames.voiceAssistant,
                    ];
                    
                    final bool shouldHide = hiddenPaths.contains(path) || 
                                          path.contains(RouteNames.jobDetail);

                    if (shouldHide) return const SizedBox.shrink();

                    return Positioned(
                      right: 20,
                      bottom: 100,
                      child: VoiceFloatingButton(
                        onPressed: () => router.push(RouteNames.voiceAssistant),
                      ),
                    );
                  },
                ),
              ],
            );
          },
        );
      },
    );
  }
}
