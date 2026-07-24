import 'package:flutter_test/flutter_test.dart';
import '../lib/core/error.dart';
import '../lib/core/utils.dart';
import '../lib/providers/auth_provider.dart';
import '../lib/providers/job_provider.dart';
import '../lib/providers/application_provider.dart';
import '../lib/providers/voice_provider.dart';
import '../lib/providers/profile_provider.dart';
import '../lib/providers/location_provider.dart';
import '../lib/providers/notification_provider.dart';
import '../lib/models/user_model.dart';
import '../lib/models/job_model.dart';
import '../lib/models/application_model.dart';
import '../lib/models/voice_session_model.dart';
import '../lib/models/employee_profile_model.dart';
import '../lib/models/notification_model.dart';
import '../lib/repositories/auth_repository.dart';
import '../lib/repositories/job_repository.dart';
import '../lib/repositories/application_repository.dart';
import '../lib/repositories/voice_repository.dart';
import '../lib/repositories/profile_repository.dart';
import '../lib/repositories/notification_repository.dart';
import '../lib/services/storage_service.dart';
import '../lib/services/api_service.dart';
import '../lib/services/auth_service.dart';
import '../lib/services/job_service.dart';
import '../lib/services/application_service.dart';
import '../lib/services/profile_service.dart';
import '../lib/services/notification_service.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:intl/date_symbol_data_local.dart';

class FakeStorageService extends StorageService {
  FakeStorageService() : super(const FlutterSecureStorage());
}

class FakeApiService extends ApiService {
  FakeApiService() : super(FakeStorageService());
}

class FakeAuthService extends AuthService {
  FakeAuthService() : super(FakeApiService(), FakeStorageService());
}

class FakeJobService extends JobService {
  FakeJobService() : super(FakeApiService());
}

class FakeApplicationService extends ApplicationService {
  FakeApplicationService() : super(FakeApiService());
}

class FakeProfileService extends ProfileService {
  FakeProfileService() : super(FakeApiService());
}

class FakeNotificationService extends NotificationService {
  FakeNotificationService() : super(FakeApiService(), FakeStorageService());
}

class FakeAuthRepository extends AuthRepository {
  final Map<String, dynamic> _stub;
  FakeAuthRepository(this._stub) : super(FakeAuthService(), FakeStorageService());
  @override Future<bool> isLoggedIn() async {
    final fn = _stub['isLoggedIn'] as Future<bool> Function()?;
    return fn != null ? await fn() : false;
  }
  @override Future<UserModel?> getSavedUser() async => (_stub['getSavedUser'] as Future<UserModel?> Function()?)?.call();
  @override Future<UserModel> loginWithEmail(String e, String p) async => (_stub['loginWithEmail'] as Future<UserModel> Function(String, String)?)?.call(e, p) ?? (throw const Failure(message: 'unexpected'));
  @override Future<UserModel> loginWithPhone(String p, String pass) async => (_stub['loginWithPhone'] as Future<UserModel> Function(String, String)?)?.call(p, pass) ?? (throw const Failure(message: 'unexpected'));
  @override Future<void> logout() async => (_stub['logout'] as Future<void> Function()?)?.call();
  @override Future<UserModel> register({String? name, String? email, String? phone, String? password, String? role}) async => (_stub['register'] as Future<UserModel> Function(String?, String?, String?, String?, String?)?)?.call(name, email, phone, password, role) ?? (throw const Failure(message: 'unexpected'));
  @override Future<UserModel> getCurrentUser() async => (_stub['getCurrentUser'] as Future<UserModel> Function()?)?.call() ?? (throw const Failure(message: 'unexpected'));
}

class FakeJobRepository extends JobRepository {
  final Map<String, dynamic> _stub;
  FakeJobRepository(this._stub) : super(FakeJobService(), FakeStorageService());
  @override Future<List<JobModel>> getJobs({int page = 1, int limit = 20, String? category, String? search, String? location, String? jobType, String? experienceLevel, double? salaryMin, double? salaryMax, String? sortBy, double? latitude, double? longitude, double? radiusKm}) async {
    final fn = _stub['getJobs'] as Future<List<JobModel>> Function({int page})?;
    return fn != null ? await fn(page: page) : [];
  }
  @override Future<List<JobModel>> searchJobs({required String query, int page = 1, int limit = 20, String? category, String? location, String? jobType}) async {
    final fn = _stub['searchJobs'] as Future<List<JobModel>> Function({String? query, String? category, String? location, String? jobType})?;
    return fn != null ? await fn(query: query, category: category, location: location, jobType: jobType) : [];
  }
  @override Future<List<JobModel>> getRecommendedJobs({int limit = 10}) async {
    final fn = _stub['getRecommendedJobs'] as Future<List<JobModel>> Function({int limit})?;
    return fn != null ? await fn(limit: limit) : [];
  }
}

class FakeApplicationRepository extends ApplicationRepository {
  final Map<String, dynamic> _stub;
  FakeApplicationRepository(this._stub) : super(FakeApplicationService());
  @override Future<ApplicationModel> apply({required String jobId, String? coverLetter, String? resumeUrl, String? voiceResumeUrl}) async => (_stub['apply'] as Future<ApplicationModel> Function({String? jobId})?)?.call(jobId: jobId) ?? (throw const Failure(message: 'unexpected'));
  @override Future<List<ApplicationModel>> getApplications({int page = 1, int limit = 20, String? status}) async {
    final fn = _stub['getApplications'] as Future<List<ApplicationModel>> Function({int page})?;
    return fn != null ? await fn(page: page) : [];
  }
  @override Future<void> withdrawApplication(String id) async => (_stub['withdrawApplication'] as Future<void> Function(String)?)?.call(id);
}

class FakeVoiceRepository implements VoiceRepository {
  final Map<String, dynamic> _stub;
  FakeVoiceRepository(this._stub);
  @override Future<bool> requestMicrophonePermission() async {
    final fn = _stub['requestMicrophonePermission'] as Future<bool> Function()?;
    return fn != null ? await fn() : false;
  }
  @override Future<String> startRecording({String? fileName}) async {
    final fn = _stub['startRecording'] as Future<String> Function()?;
    return fn != null ? await fn() : '/tmp/voice.m4a';
  }
  @override Future<String?> stopRecording() async => (_stub['stopRecording'] as Future<String?> Function()?)?.call();
  @override Future<void> cancelRecording() async => (_stub['cancelRecording'] as Future<void> Function()?)?.call();
  @override Future<VoiceCommandResult> processVoiceCommand({required String transcript}) async => (_stub['processVoiceCommand'] as Future<VoiceCommandResult> Function({required String transcript})?)?.call(transcript: transcript) ?? (throw const Failure(message: 'unexpected'));
  @override Future<String> textToSpeech({required String text, String language = 'hi'}) async {
    final fn = _stub['textToSpeech'] as Future<String> Function({required String text})?;
    return fn != null ? await fn(text: text) : 'https://audio.url';
  }
  @override Future<String> speechToText({required String audioFilePath, String language = 'hi'}) async {
    final fn = _stub['speechToText'] as Future<String> Function({required String audioFilePath})?;
    return fn != null ? await fn(audioFilePath: audioFilePath) : '';
  }
  @override Future<String> voiceSearch({required String query, String language = 'hi'}) async {
    final fn = _stub['voiceSearch'] as Future<String> Function({required String query})?;
    return fn != null ? await fn(query: query) : '';
  }
  @override Future<String> translateText({required String text, required String sourceLanguage, required String targetLanguage}) async => '';
  @override Future<String> generateVoiceResume({required String text, String language = 'hi'}) async => '';
  @override Future<bool> checkHealth() async => true;
  @override Future<double> getAmplitude() async => 0;
  @override Future<Map<String, dynamic>> extractProfileFromTranscript({required String transcript, String language = 'hi'}) async => {};
}

class FakeProfileRepository extends ProfileRepository {
  final Map<String, dynamic> _stub;
  FakeProfileRepository(this._stub) : super(FakeProfileService());
  @override Future<EmployeeProfileModel> getEmployeeProfile() async => (_stub['getEmployeeProfile'] as Future<EmployeeProfileModel> Function()?)?.call() ?? (throw const Failure(message: 'unexpected'));
  @override Future<EmployeeProfileModel> updateEmployeeProfile({String? fullName, String? phone, String? bio, String? dateOfBirth, String? gender, String? address, String? city, String? state, String? pincode, double? latitude, double? longitude, List<String>? skills, String? expectedSalary, String? preferredJobType, List<String>? preferredLocations, bool? isAvailable, String? noticePeriod}) async => (_stub['updateEmployeeProfile'] as Future<EmployeeProfileModel> Function({String? fullName})?)?.call(fullName: fullName) ?? (throw const Failure(message: 'unexpected'));
}

class FakeNotificationRepository extends NotificationRepository {
  final Map<String, dynamic> _stub;
  FakeNotificationRepository(this._stub) : super(FakeNotificationService());
  @override Future<List<NotificationModel>> getNotifications({int page = 1, int limit = 20}) async {
    final fn = _stub['getNotifications'] as Future<List<NotificationModel>> Function({int page})?;
    return fn != null ? await fn(page: page) : [];
  }
  @override Future<int> getUnreadCount() async {
    final fn = _stub['getUnreadCount'] as Future<int> Function()?;
    return fn != null ? await fn() : 0;
  }
  @override Future<void> markAsRead(String id) async => (_stub['markAsRead'] as Future<void> Function(String)?)?.call(id);
  @override Future<void> markAllAsRead() async => (_stub['markAllAsRead'] as Future<void> Function()?)?.call();
  @override Future<void> clearAll() async => (_stub['clearAll'] as Future<void> Function()?)?.call();
}

final _now = DateTime.now();

UserModel _user({String id = '1', String email = 'test@test.com', String name = 'Test'}) =>
  UserModel(id: id, email: email, name: name, role: UserRole.employee, createdAt: _now, updatedAt: _now);

JobModel _job({String id = '1', String title = 'Job'}) =>
  JobModel(id: id, title: title, companyId: 'c1', employerId: 'e1', jobType: JobType.fullTime, createdAt: _now, updatedAt: _now);

void main() {
  group('AuthProvider', () {
    late Map<String, dynamic> stub;
    late AuthNotifier authNotifier;

    setUp(() {
      stub = {};
      authNotifier = AuthNotifier(FakeAuthRepository(stub));
    });

    test('initial state is initial', () {
      expect(authNotifier.state.status, AuthStatus.initial);
      expect(authNotifier.state.user, isNull);
      expect(authNotifier.state.failure, isNull);
    });

    test('loginWithEmail sets authenticated on success', () async {
      final user = _user(email: 'test@example.com', name: 'Test User');
      stub['loginWithEmail'] = (String e, String p) async => user;

      await authNotifier.loginWithEmail('test@example.com', 'password');

      expect(authNotifier.state.status, AuthStatus.authenticated);
      expect(authNotifier.state.user?.email, 'test@example.com');
      expect(authNotifier.state.isLoginLoading, false);
    });

    test('loginWithEmail sets failure on error', () async {
      stub['loginWithEmail'] = (String e, String p) async => throw const Failure(message: 'Invalid credentials');

      await authNotifier.loginWithEmail('test@example.com', 'wrong');

      expect(authNotifier.state.failure?.message, 'Invalid credentials');
      expect(authNotifier.state.isLoginLoading, false);
    });

    test('loginWithPhone calls repository', () async {
      stub['loginWithPhone'] = (String p, String pass) async => _user(id: '2', email: 'phone@test.com', name: 'Phone User');

      await authNotifier.loginWithPhone('9999999999', 'pass');

      expect(authNotifier.state.status, AuthStatus.authenticated);
    });

    test('logout clears user state', () async {
      stub['logout'] = () async {};

      await authNotifier.logout();

      expect(authNotifier.state.status, AuthStatus.unauthenticated);
      expect(authNotifier.state.user, isNull);
    });

    test('register sets authenticated on success', () async {
      stub['register'] = (String? n, String? e, String? p, String? pass, String? r) async =>
        _user(id: '3', email: e ?? '', name: n ?? '');

      await authNotifier.register(name: 'New User', email: 'new@test.com', phone: '8888888888', password: 'Pass123!', role: 'employee');

      expect(authNotifier.state.status, AuthStatus.authenticated);
      expect(authNotifier.state.isRegisterLoading, false);
    });

    test('register sets failure on error', () async {
      stub['register'] = (String? n, String? e, String? p, String? pass, String? r) async =>
        throw const Failure(message: 'Email already exists');

      await authNotifier.register(name: 'Test', email: 'exists@test.com', phone: '7777777777', password: 'Pass123!', role: 'employee');

      expect(authNotifier.state.failure?.message, 'Email already exists');
    });

    test('clearFailure resets failure', () {
      authNotifier.clearFailure();
      expect(authNotifier.state.failure, isNull);
    });
  });

  group('JobProvider', () {
    late Map<String, dynamic> stub;
    late JobNotifier jobNotifier;

    setUp(() {
      stub = {};
      jobNotifier = JobNotifier(FakeJobRepository(stub));
    });

    test('initial state is empty', () {
      expect(jobNotifier.state.jobs, isEmpty);
      expect(jobNotifier.state.recommendedJobs, isEmpty);
      expect(jobNotifier.state.isLoading, false);
    });

    test('fetchJobs loads jobs successfully', () async {
      stub['getJobs'] = ({int page = 1}) async => [_job(title: 'Engineer'), _job(id: '2', title: 'Designer')];

      await jobNotifier.fetchJobs();

      expect(jobNotifier.state.jobs.length, 2);
      expect(jobNotifier.state.isLoading, false);
    });

    test('fetchJobs handles empty list', () async {
      stub['getJobs'] = ({int page = 1}) async => <JobModel>[];

      await jobNotifier.fetchJobs();

      expect(jobNotifier.state.jobs, isEmpty);
      expect(jobNotifier.state.hasMore, false);
    });

    test('loadMoreJobs appends to existing jobs', () async {
      int callCount = 0;
      stub['getJobs'] = ({int page = 1}) async {
        callCount++;
        if (callCount == 1) return List.generate(20, (i) => _job(id: '$i', title: 'Job $i'));
        return [_job(id: '20', title: 'Job 20')];
      };

      await jobNotifier.fetchJobs();
      await jobNotifier.loadMoreJobs();

      expect(jobNotifier.state.jobs.length, 21);
      expect(jobNotifier.state.currentPage, 2);
    });

    test('searchJobs sends correct query', () async {
      stub['searchJobs'] = ({String? query, String? category, String? location, String? jobType}) async =>
        <JobModel>[];

      await jobNotifier.searchJobs(query: 'Python');

      expect(jobNotifier.state.searchQuery, 'Python');
    });

    test('fetchRecommendedJobs loads recommendations', () async {
      stub['getRecommendedJobs'] = ({int limit = 10}) async =>
        [_job(id: '10', title: 'Recommended')];

      await jobNotifier.fetchRecommendedJobs();

      expect(jobNotifier.state.recommendedJobs.length, 1);
      expect(jobNotifier.state.isRecommendedLoading, false);
    });

    test('clearSearch resets search state', () {
      jobNotifier.clearSearch();
      expect(jobNotifier.state.searchQuery, isNull);
      expect(jobNotifier.state.jobs, isEmpty);
    });

    test('clearFailure resets failure', () {
      jobNotifier.clearFailure();
      expect(jobNotifier.state.failure, isNull);
    });
  });

  group('ApplicationProvider', () {
    late Map<String, dynamic> stub;
    late ApplicationNotifier appNotifier;

    setUp(() {
      stub = {};
      appNotifier = ApplicationNotifier(FakeApplicationRepository(stub));
    });

    test('initial state is empty', () {
      expect(appNotifier.state.applications, isEmpty);
      expect(appNotifier.state.isLoading, false);
      expect(appNotifier.state.isApplying, false);
    });

    test('apply succeeds', () async {
      stub['apply'] = ({String? jobId}) async => ApplicationModel(
        id: 'a1', jobId: jobId ?? '', userId: 'u1',
        appliedAt: _now, createdAt: _now, updatedAt: _now,
      );

      final result = await appNotifier.apply(jobId: 'j1');

      expect(result, true);
      expect(appNotifier.state.applications.length, 1);
      expect(appNotifier.state.isApplying, false);
    });

    test('apply handles error', () async {
      stub['apply'] = ({String? jobId}) async =>
        throw const Failure(message: 'Already applied');

      final result = await appNotifier.apply(jobId: 'job1', coverLetter: 'test');

      expect(result, false);
      expect(appNotifier.state.failure?.message, 'Already applied');
    });

    test('withdrawApplication updates status', () async {
      stub['getApplications'] = ({int page = 1}) async => [
        ApplicationModel(id: 'a1', jobId: 'j1', userId: 'u1',
          status: ApplicationStatus.applied,
          appliedAt: _now, createdAt: _now, updatedAt: _now,
        ),
      ];
      stub['withdrawApplication'] = (String id) async {};

      await appNotifier.fetchApplications();
      await appNotifier.withdrawApplication('a1');

      expect(appNotifier.state.applications.first.status, ApplicationStatus.withdrawn);
    });
  });

  group('VoiceProvider', () {
    late Map<String, dynamic> stub;
    late VoiceNotifier voiceNotifier;

    setUp(() {
      stub = {};
      voiceNotifier = VoiceNotifier(FakeVoiceRepository(stub));
    });

    test('initial state is idle', () {
      expect(voiceNotifier.state.isListening, false);
      expect(voiceNotifier.state.isProcessing, false);
      expect(voiceNotifier.state.transcript, isNull);
      expect(voiceNotifier.state.recordingPath, isNull);
    });

    test('setListening updates listening state', () {
      voiceNotifier.setListening(true);
      expect(voiceNotifier.state.isListening, true);
      voiceNotifier.setListening(false);
      expect(voiceNotifier.state.isListening, false);
    });

    test('startRecording begins recording', () async {
      stub['requestMicrophonePermission'] = () async => true;
      stub['startRecording'] = () async => '/tmp/voice.m4a';

      await voiceNotifier.startRecording();

      expect(voiceNotifier.state.isListening, true);
      expect(voiceNotifier.state.recordingPath, '/tmp/voice.m4a');
    });

    test('startRecording handles permission denied', () async {
      stub['requestMicrophonePermission'] = () async => false;

      await voiceNotifier.startRecording();

      expect(voiceNotifier.state.isListening, false);
      expect(voiceNotifier.state.failure, isNotNull);
    });

    test('stopRecording returns path', () async {
      stub['requestMicrophonePermission'] = () async => true;
      stub['startRecording'] = () async => '/tmp/voice.m4a';
      stub['stopRecording'] = () async => '/tmp/voice.m4a';

      await voiceNotifier.startRecording();
      final path = await voiceNotifier.stopRecording();

      expect(path, '/tmp/voice.m4a');
      expect(voiceNotifier.state.isListening, false);
    });

    test('cancelRecording stops without path', () async {
      stub['cancelRecording'] = () async {};

      await voiceNotifier.cancelRecording();

      expect(voiceNotifier.state.isListening, false);
      expect(voiceNotifier.state.recordingPath, isNull);
    });

    test('processCommand processes transcript successfully', () async {
      stub['processVoiceCommand'] = ({String? transcript}) async => VoiceCommandResult(
        type: VoiceCommandType.search, command: 'search driver jobs',
        responseText: 'Found 5 jobs', action: 'search',
        parsedData: {'query': 'driver'},
      );
      stub['textToSpeech'] = ({String? text}) async => 'https://audio.url';

      await voiceNotifier.processCommand(transcript: 'search driver jobs');

      expect(voiceNotifier.state.responseText, 'Found 5 jobs');
      expect(voiceNotifier.state.lastCommand?.type, VoiceCommandType.search);
      expect(voiceNotifier.state.audioUrl, isNotNull);
    });

    test('processCommand handles error', () async {
      stub['processVoiceCommand'] = ({String? transcript}) async =>
        throw const Failure(message: 'Could not process command');

      await voiceNotifier.processCommand(transcript: 'unknown');

      expect(voiceNotifier.state.failure?.message, 'Could not process command');
      expect(voiceNotifier.state.isProcessing, false);
    });

    test('processSpeech performs full pipeline', () async {
      stub['speechToText'] = ({String? audioFilePath}) async => 'search driver jobs';
      stub['processVoiceCommand'] = ({String? transcript}) async => VoiceCommandResult(
        type: VoiceCommandType.search, command: 'search',
        responseText: 'Found jobs',
      );

      await voiceNotifier.processSpeech(audioFilePath: '/tmp/recording.m4a');

      expect(voiceNotifier.state.transcript, 'search driver jobs');
      expect(voiceNotifier.state.isProcessing, false);
    });

    test('clearSession resets all state', () {
      voiceNotifier.setTranscript('test');
      voiceNotifier.setListening(true);
      voiceNotifier.clearSession();

      expect(voiceNotifier.state.isListening, false);
      expect(voiceNotifier.state.transcript, isNull);
      expect(voiceNotifier.state.responseText, isNull);
      expect(voiceNotifier.state.recordingPath, isNull);
    });

    test('setTranscript updates transcript', () {
      voiceNotifier.setTranscript('Hello world');
      expect(voiceNotifier.state.transcript, 'Hello world');
    });

    test('clearFailure resets failure', () async {
      stub['processVoiceCommand'] = ({String? transcript}) async =>
        throw const Failure(message: 'Error');
      await voiceNotifier.processCommand(transcript: 'fail');
      expect(voiceNotifier.state.failure, isNotNull);

      voiceNotifier.clearFailure();
      expect(voiceNotifier.state.failure, isNull);
    });

    test('voiceSearch returns processed query', () async {
      stub['voiceSearch'] = ({String? query}) async => 'driver';

      final result = await voiceNotifier.voiceSearch('driver jobs');

      expect(result, 'driver');
    });
  });

  group('ProfileProvider', () {
    late Map<String, dynamic> stub;
    late ProfileNotifier profileNotifier;

    setUp(() {
      stub = {};
      profileNotifier = ProfileNotifier(FakeProfileRepository(stub));
    });

    test('initial state is idle', () {
      expect(profileNotifier.state.isLoading, false);
      expect(profileNotifier.state.employeeProfile, isNull);
    });

    test('fetchEmployeeProfile loads profile', () async {
      stub['getEmployeeProfile'] = () async => EmployeeProfileModel(
        id: 'p1', userId: 'u1', fullName: 'John Doe',
        skills: ['Flutter', 'Dart'],
        createdAt: _now, updatedAt: _now,
      );

      await profileNotifier.fetchEmployeeProfile();

      expect(profileNotifier.state.employeeProfile?.fullName, 'John Doe');
      expect(profileNotifier.state.isLoading, false);
    });

    test('fetchEmployeeProfile handles error', () async {
      stub['getEmployeeProfile'] = () async =>
        throw const Failure(message: 'Profile not found');

      await profileNotifier.fetchEmployeeProfile();

      expect(profileNotifier.state.failure?.message, 'Profile not found');
    });

    test('updateEmployeeProfile updates state', () async {
      stub['getEmployeeProfile'] = () async => EmployeeProfileModel(
        id: 'p1', userId: 'u1', fullName: 'Old Name',
        createdAt: _now, updatedAt: _now,
      );
      stub['updateEmployeeProfile'] = ({String? fullName}) async => EmployeeProfileModel(
        id: 'p1', userId: 'u1', fullName: fullName ?? '',
        createdAt: _now, updatedAt: _now,
      );

      await profileNotifier.fetchEmployeeProfile();
      await profileNotifier.updateEmployeeProfile(fullName: 'New Name');

      expect(profileNotifier.state.employeeProfile?.fullName, 'New Name');
      expect(profileNotifier.state.successMessage, isNotNull);
    });

    test('clearFailure resets failure', () {
      profileNotifier.clearFailure();
      expect(profileNotifier.state.failure, isNull);
    });

    test('clearSuccess resets success message', () {
      profileNotifier.clearSuccess();
      expect(profileNotifier.state.successMessage, isNull);
    });
  });

  group('NotificationProvider', () {
    late Map<String, dynamic> stub;
    late NotificationNotifier notifNotifier;

    setUp(() {
      stub = {};
      notifNotifier = NotificationNotifier(FakeNotificationRepository(stub));
    });

    test('initial state is empty', () {
      expect(notifNotifier.state.notifications, isEmpty);
      expect(notifNotifier.state.unreadCount, 0);
    });

    test('fetchNotifications loads notifications', () async {
      stub['getNotifications'] = ({int page = 1}) async => [
        NotificationModel(id: 'n1', userId: 'u1', type: NotificationType.jobAlert,
          title: 'New Job', body: 'Check it out', createdAt: _now),
      ];

      await notifNotifier.fetchNotifications(refresh: true);

      expect(notifNotifier.state.notifications.length, 1);
      expect(notifNotifier.state.isLoading, false);
    });

    test('fetchUnreadCount updates count', () async {
      stub['getUnreadCount'] = () async => 5;

      await notifNotifier.fetchUnreadCount();

      expect(notifNotifier.state.unreadCount, 5);
    });

    test('markAsRead updates notification', () async {
      stub['getNotifications'] = ({int page = 1}) async => [
        NotificationModel(id: 'n1', userId: 'u1', type: NotificationType.system,
          title: 'Test', body: 'Body', createdAt: _now),
      ];
      stub['markAsRead'] = (String id) async {};

      await notifNotifier.fetchNotifications(refresh: true);
      await notifNotifier.markAsRead('n1');

      expect(notifNotifier.state.notifications.first.isRead, true);
    });

    test('markAllAsRead clears unread count', () async {
      stub['getNotifications'] = ({int page = 1}) async => <NotificationModel>[];
      stub['markAllAsRead'] = () async {};

      await notifNotifier.fetchNotifications(refresh: true);
      await notifNotifier.markAllAsRead();

      expect(notifNotifier.state.unreadCount, 0);
    });

    test('clearAll clears all notifications', () async {
      stub['getNotifications'] = ({int page = 1}) async => <NotificationModel>[];
      stub['clearAll'] = () async {};

      await notifNotifier.fetchNotifications(refresh: true);
      await notifNotifier.clearAll();

      expect(notifNotifier.state.notifications, isEmpty);
      expect(notifNotifier.state.unreadCount, 0);
    });
  });

  group('LocationProvider', () {
    late LocationNotifier locationNotifier;

    setUp(() {
      locationNotifier = LocationNotifier();
    });

    test('initial state is idle', () {
      expect(locationNotifier.state.isLoading, false);
      expect(locationNotifier.state.position, isNull);
      expect(locationNotifier.state.permissionDenied, false);
    });

    test('clearFailure resets failure', () {
      locationNotifier.clearFailure();
      expect(locationNotifier.state.failure, isNull);
    });
  });

  group('Formatters', () {
    test('currency formats INR correctly', () {
      expect(Formatters.currency(15000.50), '₹15,000.50');
    });

    test('currencyCompact formats large numbers', () {
      expect(Formatters.currencyCompact(150000), '₹1.5L');
    });

    test('date formats correctly', () async {
      await initializeDateFormatting('en_IN');
      expect(Formatters.date(DateTime(2024, 1, 15)), '15 Jan 2024');
    });

    test('relativeTime shows correct units', () {
      expect(Formatters.relativeTime(DateTime.now()), 'Just now');
      expect(Formatters.relativeTime(DateTime.now().subtract(const Duration(minutes: 5))), '5m ago');
      expect(Formatters.relativeTime(DateTime.now().subtract(const Duration(hours: 2))), '2h ago');
    });

    test('jobType converts to display string', () {
      expect(Formatters.jobType('full_time'), 'Full Time');
      expect(Formatters.jobType('part_time'), 'Part Time');
      expect(Formatters.jobType('internship'), 'Internship');
    });

    test('fileSize converts bytes correctly', () {
      expect(Formatters.fileSize(500), '500 B');
      expect(Formatters.fileSize(2048), '2.0 KB');
      expect(Formatters.fileSize(1048576), '1.0 MB');
    });

    test('truncate shortens long strings', () {
      expect(Formatters.truncate('Hello World', 5), 'Hello...');
      expect(Formatters.truncate('Hi', 5), 'Hi');
    });
  });

  group('Validators', () {
    test('email validates correctly', () {
      expect(Validators.email(null), isNotNull);
      expect(Validators.email(''), isNotNull);
      expect(Validators.email('invalid'), isNotNull);
      expect(Validators.email('test@example.com'), isNull);
    });

    test('phone validates correctly', () {
      expect(Validators.phone(null), isNotNull);
      expect(Validators.phone('123'), isNotNull);
      expect(Validators.phone('9876543210'), isNull);
    });

    test('password validates correctly', () {
      expect(Validators.password(null), isNotNull);
      expect(Validators.password('short'), isNotNull);
      expect(Validators.password('nouppercase1!'), isNotNull);
      expect(Validators.password('ValidPass1!'), isNull);
    });

    test('otp validates correctly', () {
      expect(Validators.otp(null), isNotNull);
      expect(Validators.otp('123'), isNotNull);
      expect(Validators.otp('abcdef'), isNotNull);
      expect(Validators.otp('123456'), isNull);
    });
  });
}
