import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'providers/providers.dart';
import 'routes/app_router.dart';
import 'theme/app_theme.dart';

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
    FlutterLocalNotificationsPlugin();

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  try {
    await Firebase.initializeApp();
    final firebaseApp = Firebase.app();
    debugPrint(
      'Firebase initialized: name=${firebaseApp.name} '
      'projectId=${firebaseApp.options.projectId} '
      'appId=${firebaseApp.options.appId}',
    );
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings();
    await flutterLocalNotificationsPlugin.initialize(
      const InitializationSettings(android: androidSettings, iOS: iosSettings),
    );
  } on FirebaseException catch (error, stackTrace) {
    // Do not silently continue with an unconfigured Firebase app. Phone
    // authentication depends on this initialization having succeeded.
    debugPrint(
      'Firebase initialization failed: code=${error.code} '
      'message=${error.message}\n$stackTrace',
    );
  } catch (error, stackTrace) {
    debugPrint('Firebase initialization failed: $error\n$stackTrace');
  }

  runApp(
    const ProviderScope(
      child: JobCareVoiceApp(),
    ),
  );
}

class JobCareVoiceApp extends StatelessWidget {
  const JobCareVoiceApp({super.key});

  @override
  Widget build(BuildContext context) {
    // CRITICAL: ScreenUtilInit MUST be a constant root that NEVER rebuilds.
    // Rebuilding this widget during transitions causes the '_dependents.isEmpty' crash.
    return ScreenUtilInit(
      designSize: const Size(390, 844),
      minTextAdapt: true,
      splitScreenMode: true,
      ensureScreenSize: true,
      child: const _AppLauncher(),
    );
  }
}

class _AppLauncher extends ConsumerWidget {
  const _AppLauncher();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Only the content inside rebuilds when state changes
    final router = ref.watch(routerProvider);
    final themeMode = ref.watch(themeModeProvider);
    final lang = ref.watch(languageProvider);

    return MaterialApp.router(
      title: 'JobCare Voice',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(lang),
      darkTheme: AppTheme.dark(lang),
      themeMode: themeMode,
      routerConfig: router,
    );
  }
}
