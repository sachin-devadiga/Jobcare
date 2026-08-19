import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/constants.dart';
import '../core/error.dart';
import '../models/user_model.dart';
import 'api_service.dart';
import 'storage_service.dart';

class AuthService {
  final ApiService _apiService;
  final StorageService _storageService;

  AuthService(
    this._apiService,
    this._storageService,
  );

  Future<void> sendOtp({required String phone, String? email}) async {
    final cleanPhone = phone.replaceAll(RegExp(r'[^0-9+]'), '');
    final normalizedPhone = cleanPhone.startsWith('+') ? cleanPhone : '+91$cleanPhone';
    try {
      final data = <String, dynamic>{'phone': normalizedPhone};
      if (email != null && email.trim().isNotEmpty) {
        data['email'] = email.trim();
      }
      await _apiService.post(AppConstants.otpRequestEndpoint, data: data);
      debugPrint('OTP sent: phone=$normalizedPhone, channel=${AppConstants.otpChannel}');
    } on DioException catch (e) {
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

  Future<void> forgotPassword({required String email}) async {
    try {
      await _apiService.post('auth/forgot-password/', data: {'email': email});
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> resetPassword({
    required String email,
    required String otp,
    required String password,
  }) async {
    try {
      await _apiService.post(
        'auth/reset-password/',
        data: {
          'email': email,
          'otp': otp,
          'password': password,
          'confirm_password': password,
        },
      );
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<UserModel> verifyOtp({
    required String phone,
    required String otp,
    String? name,
  }) async {
    try {
      final cleanPhone = phone.replaceAll(RegExp(r'[^0-9+]'), '');
      final normalizedPhone = cleanPhone.startsWith('+') ? cleanPhone : '+91$cleanPhone';
      final response = await _apiService.post(
        AppConstants.otpVerifyEndpoint,
        data: {
          'phone': normalizedPhone,
          'otp': otp,
          if (name != null && name.isNotEmpty) 'name': name,
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

  Future<UserModel?> restoreSession() async {
    final token = await _storageService.readToken();
    if (token == null || token.isEmpty) return null;
    try {
      return await getCurrentUser();
    } on Failure {
      await _storageService.clear();
      return null;
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
