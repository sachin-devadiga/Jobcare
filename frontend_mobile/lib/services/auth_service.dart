import 'package:dio/dio.dart';
import '../core/error.dart';
import 'api_service.dart';
import 'storage_service.dart';
import '../models/user_model.dart';

class AuthService {
  final ApiService _apiService;
  final StorageService _storageService;

  AuthService(this._apiService, this._storageService);

  Future<void> sendOtp({required String phone}) async {
    final cleanPhone = phone.replaceAll(RegExp(r'[\s\-\(\)]'), '');
    
    // TEST BYPASS: Instantly succeed if number ends in 000
    if (cleanPhone.endsWith('000')) return;

    try {
      await _apiService.post(
        'auth/phone/request-otp/',
        data: {'phone': cleanPhone},
      );
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionError || e.type == DioExceptionType.connectionTimeout) {
        throw const Failure(message: 'Cannot reach server. Tip: If using a real phone, ensure the IP in AppConstants is your PC\'s local IP. Or use a number ending in 000.');
      }
      throw handleException(e.error);
    }
  }

  Future<UserModel> loginWithEmail({required String email, required String password}) async {
    final response = await _apiService.post('auth/login/', data: {'email': email, 'password': password});
    return _saveAndReturnUser(response.data as Map<String, dynamic>);
  }

  Future<UserModel> loginWithPhone({required String phone, required String password}) async {
    final response = await _apiService.post('auth/login/', data: {'phone': phone, 'password': password});
    return _saveAndReturnUser(response.data as Map<String, dynamic>);
  }

  Future<UserModel> register({required String name, required String email, required String phone, required String password, required String role}) async {
    final response = await _apiService.post('auth/register/', data: {
      'name': name, 'email': email, 'phone': phone, 'password': password,
      'confirm_password': password, 'role': role,
    });
    final payload = response.data as Map<String, dynamic>;
    return UserModel.fromJson(payload['data'] as Map<String, dynamic>);
  }

  Future<UserModel> verifyOtp({
    required String phone,
    required String otp,
    String? name,
  }) async {
    final cleanPhone = phone.replaceAll(RegExp(r'[\s\-\(\)]'), '');

    // TEST BYPASS: Use 123456 as master OTP
    if (cleanPhone.endsWith('000') && (otp == '123456' || otp == '000000')) {
      final now = DateTime.now();
      final user = UserModel(
        id: 'test_user',
        phone: cleanPhone,
        name: name ?? 'Test Worker',
        email: 'test@jobcare.voice',
        role: UserRole.employee,
        createdAt: now,
        updatedAt: now,
      );
      await _saveTokens({
        'access_token': 'test_access_token',
        'refresh_token': 'test_refresh_token',
        'user': user.toJson(),
      });
      return user;
    }

    try {
      final response = await _apiService.post(
        'auth/phone/verify-otp/',
        data: {
          'phone': cleanPhone,
          'otp': otp,
          if (name != null) 'name': name,
        },
      );
      
      final data = response.data as Map<String, dynamic>;
      final authData = data['data'] as Map<String, dynamic>;
      
      await _saveTokens({
        'access_token': authData['access'],
        'refresh_token': authData['refresh'],
        'user': authData['user'],
      });

      return UserModel.fromJson(authData['user'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<UserModel> getCurrentUser() async {
    try {
      final response = await _apiService.get('auth/profile/');
      final data = response.data as Map<String, dynamic>;
      return UserModel.fromJson(data['data'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> logout() async {
    try {
      final refreshToken = await _storageService.readRefreshToken();
      if (refreshToken != null) {
        await _apiService.post('auth/logout/', data: {'refresh': refreshToken});
      }
    } on DioException catch (_) {
    } finally {
      await _storageService.clear();
    }
  }

  Future<void> _saveTokens(Map<String, dynamic> data) async {
    if (data.containsKey('access_token')) {
      await _storageService.writeToken(data['access_token'] as String);
    }
    if (data.containsKey('refresh_token')) {
      await _storageService.writeRefreshToken(data['refresh_token'] as String);
    }
    if (data.containsKey('user') && data['user'] is Map) {
      final user = UserModel.fromJson(data['user'] as Map<String, dynamic>);
      await _storageService.saveUserData(user.toJsonString());
    }
  }

  Future<UserModel> _saveAndReturnUser(Map<String, dynamic> payload) async {
    final data = payload['data'] as Map<String, dynamic>;
    await _saveTokens({
      'access_token': data['access'], 'refresh_token': data['refresh'], 'user': data['user'],
    });
    return UserModel.fromJson(data['user'] as Map<String, dynamic>);
  }
}
