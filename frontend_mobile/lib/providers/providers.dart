import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

import '../services/api_service.dart';
import '../services/storage_service.dart';
import '../services/auth_service.dart';
import '../services/job_service.dart';
import '../services/application_service.dart';
import '../services/profile_service.dart';
import '../services/notification_service.dart';
import '../services/voice_service.dart';
import '../services/chat_service.dart';
import '../services/payment_service.dart';
import '../repositories/auth_repository.dart';
import '../repositories/job_repository.dart';
import '../repositories/application_repository.dart';
import '../repositories/profile_repository.dart';
import '../repositories/notification_repository.dart';
import '../repositories/chat_repository.dart';
import '../repositories/voice_repository.dart';
import '../core/network.dart';
import 'auth_provider.dart';
import 'job_provider.dart';
import 'application_provider.dart';
import 'profile_provider.dart';
import 'notification_provider.dart';
import 'voice_provider.dart';
import 'chat_provider.dart';
import 'theme_provider.dart';
import 'location_provider.dart';
import 'language_provider.dart';

final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});

final storageServiceProvider = Provider<StorageService>((ref) {
  return StorageService(ref.read(secureStorageProvider));
});

final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService(ref.read(storageServiceProvider));
});

final networkInfoProvider = Provider<NetworkInfo>((ref) {
  return NetworkInfo(Connectivity());
});

final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService(
    ref.read(apiServiceProvider),
    ref.read(storageServiceProvider),
  );
});

final jobServiceProvider = Provider<JobService>((ref) {
  return JobService(ref.read(apiServiceProvider));
});

final applicationServiceProvider = Provider<ApplicationService>((ref) {
  return ApplicationService(ref.read(apiServiceProvider));
});

final profileServiceProvider = Provider<ProfileService>((ref) {
  return ProfileService(ref.read(apiServiceProvider));
});

final notificationServiceProvider = Provider<NotificationService>((ref) {
  return NotificationService(ref.read(apiServiceProvider), ref.read(storageServiceProvider));
});

final voiceServiceProvider = Provider<VoiceService>((ref) {
  return VoiceService(ref.read(apiServiceProvider));
});

final paymentServiceProvider = Provider<PaymentService>((ref) {
  return PaymentService(ref.read(apiServiceProvider));
});

final chatServiceProvider = Provider<ChatService>((ref) {
  return ChatService(
    ref.read(apiServiceProvider),
    ref.read(storageServiceProvider),
  );
});

final chatRepositoryProvider = Provider<ChatRepository>((ref) {
  return ChatRepository(ref.read(chatServiceProvider));
});

final chatProvider = StateNotifierProvider<ChatNotifier, ChatState>((ref) {
  final authState = ref.watch(authProvider);
  final notifier = ChatNotifier(
    ref.read(chatRepositoryProvider),
    currentUserId: authState.user?.id,
  );
  ref.listen(authProvider, (prev, next) {
    if (next.user?.id != prev?.user?.id) {
      notifier.setCurrentUserId(next.user?.id ?? '');
    }
  });
  return notifier;
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(
    ref.read(authServiceProvider),
    ref.read(storageServiceProvider),
  );
});

final jobRepositoryProvider = Provider<JobRepository>((ref) {
  return JobRepository(
    ref.read(jobServiceProvider),
    ref.read(storageServiceProvider),
  );
});

final applicationRepositoryProvider = Provider<ApplicationRepository>((ref) {
  return ApplicationRepository(ref.read(applicationServiceProvider));
});

final profileRepositoryProvider = Provider<ProfileRepository>((ref) {
  return ProfileRepository(ref.read(profileServiceProvider));
});

final notificationRepositoryProvider = Provider<NotificationRepository>((ref) {
  return NotificationRepository(ref.read(notificationServiceProvider));
});

final voiceRepositoryProvider = Provider<VoiceRepository>((ref) {
  return VoiceRepository(
    ref.read(voiceServiceProvider),
    ref.read(apiServiceProvider),
  );
});

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final notifier = AuthNotifier(ref.read(authRepositoryProvider));
  notifier.checkAuth();
  return notifier;
});

final jobProvider = StateNotifierProvider<JobNotifier, JobState>((ref) {
  return JobNotifier(ref.read(jobRepositoryProvider));
});

final applicationProvider =
    StateNotifierProvider<ApplicationNotifier, ApplicationState>((ref) {
  return ApplicationNotifier(ref.read(applicationRepositoryProvider));
});

final profileProvider =
    StateNotifierProvider<ProfileNotifier, ProfileState>((ref) {
  return ProfileNotifier(ref.read(profileRepositoryProvider));
});

final notificationProvider =
    StateNotifierProvider<NotificationNotifier, NotificationState>((ref) {
  return NotificationNotifier(ref.read(notificationRepositoryProvider));
});

final voiceProvider = StateNotifierProvider<VoiceNotifier, VoiceState>((ref) {
  return VoiceNotifier(ref.read(voiceRepositoryProvider));
});

final themeModeProvider =
    StateNotifierProvider<ThemeNotifier, ThemeMode>((ref) {
  return ThemeNotifier(ref.read(storageServiceProvider));
});

final languageProvider = StateNotifierProvider<LanguageNotifier, String>((ref) {
  return LanguageNotifier(ref.read(storageServiceProvider));
});

final locationProvider =
    StateNotifierProvider<LocationNotifier, LocationState>((ref) {
  return LocationNotifier();
});
