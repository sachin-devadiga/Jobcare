import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_model.dart';
import '../repositories/auth_repository.dart';
import '../core/error.dart';

enum AuthStatus { initial, authenticated, unauthenticated, loading }

class AuthState {
  final AuthStatus status;
  final UserModel? user;
  final Failure? failure;
  final bool isLoginLoading;
  final bool isNewUser;
  final bool otpSent;
  final bool isRegisterLoading;

  const AuthState({
    this.status = AuthStatus.initial,
    this.user,
    this.failure,
    this.isLoginLoading = false,
    this.isNewUser = false,
    this.otpSent = false,
    this.isRegisterLoading = false,
  });

  AuthState copyWith({
    AuthStatus? status,
    UserModel? user,
    Failure? failure,
    bool? isLoginLoading,
    bool? isNewUser,
    bool? otpSent,
    bool? isRegisterLoading,
  }) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      failure: failure,
      isLoginLoading: isLoginLoading ?? this.isLoginLoading,
      isNewUser: isNewUser ?? this.isNewUser,
      otpSent: otpSent ?? this.otpSent,
      isRegisterLoading: isRegisterLoading ?? this.isRegisterLoading,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _authRepository;
  final ChangeNotifier _listenable = ChangeNotifier();

  AuthNotifier(this._authRepository) : super(const AuthState());

  Listenable get listenable => _listenable;

  @override
  void dispose() {
    _listenable.dispose();
    super.dispose();
  }

  @override
  set state(AuthState value) {
    super.state = value;
    // The router instance is stable and listens to this notifier for redirect
    // updates. Notify it in the same state transition so navigation is not
    // deferred beyond the lifecycle of the current route.
    _listenable.notifyListeners();
  }

  Future<void> checkAuth() async {
    final isLoggedIn = await _authRepository.isLoggedIn();
    if (isLoggedIn) {
      try {
        final user = await _authRepository.getCurrentUser();
        state = state.copyWith(status: AuthStatus.authenticated, user: user);
      } catch (_) {
        state = state.copyWith(status: AuthStatus.unauthenticated);
      }
    } else {
      state = state.copyWith(status: AuthStatus.unauthenticated);
    }
  }

  Future<void> sendOtp(String phone, {String? email}) async {
    state = state.copyWith(isLoginLoading: true, failure: null, otpSent: false);
    try {
      await _authRepository.sendOtp(phone, email: email);
      state = state.copyWith(isLoginLoading: false, otpSent: true);
    } on Failure catch (error) {
      state = state.copyWith(
        isLoginLoading: false,
        failure: Failure(
          message: kDebugMode
              ? error.message
              : 'Unable to send verification code. Please try again.',
        ),
        otpSent: false,
      );
    } catch (error, stackTrace) {
      debugPrint('Unexpected phone authentication error: $error\n$stackTrace');
      state = state.copyWith(
        isLoginLoading: false,
        failure: Failure(
          message: error is TimeoutException
              ? 'Phone authentication timed out'
              : (kDebugMode ? error.toString() : 'Unable to send verification code. Please try again.'),
        ),
        otpSent: false,
      );
    }
  }

  Future<void> loginWithEmail(String email, String password) async {
    state = state.copyWith(isLoginLoading: true, failure: null);
    try {
      final user = await _authRepository.loginWithEmail(email, password);
      state = state.copyWith(
        status: AuthStatus.authenticated,
        user: user,
        isLoginLoading: false,
      );
    } catch (error) {
      state = state.copyWith(
        isLoginLoading: false,
        failure: error is Failure
            ? error
            : const Failure(message: 'Unable to sign in'),
      );
    }
  }

  Future<void> loginWithPhone(String phone, String password) async {
    state = state.copyWith(isLoginLoading: true, failure: null);
    try {
      final user = await _authRepository.loginWithPhone(phone, password);
      state = state.copyWith(
        status: AuthStatus.authenticated,
        user: user,
        isLoginLoading: false,
      );
    } catch (error) {
      state = state.copyWith(
        isLoginLoading: false,
        failure: error is Failure
            ? error
            : const Failure(message: 'Unable to sign in'),
      );
    }
  }

  Future<void> register({
    required String name,
    required String email,
    required String phone,
    required String password,
    required String role,
  }) async {
    state = state.copyWith(isRegisterLoading: true, failure: null);
    try {
      final user = await _authRepository.register(
        name: name,
        email: email,
        phone: phone,
        password: password,
        role: role,
      );
      state = state.copyWith(
        status: AuthStatus.authenticated,
        user: user,
        isRegisterLoading: false,
      );
    } catch (error) {
      state = state.copyWith(
        isRegisterLoading: false,
        failure: error is Failure
            ? error
            : const Failure(message: 'Unable to register'),
      );
    }
  }

  Future<void> forgotPassword(String email) async {
    state = state.copyWith(isLoginLoading: true, failure: null);
    try {
      await _authRepository.forgotPassword(email);
      state = state.copyWith(isLoginLoading: false);
    } catch (error) {
      state = state.copyWith(
        isLoginLoading: false,
        failure: error is Failure
            ? error
            : const Failure(message: 'Unable to send reset code'),
      );
      rethrow;
    }
  }

  Future<void> resetPassword({
    required String email,
    required String otp,
    required String password,
  }) async {
    state = state.copyWith(isLoginLoading: true, failure: null);
    try {
      await _authRepository.resetPassword(email: email, otp: otp, password: password);
      state = state.copyWith(isLoginLoading: false);
    } catch (error) {
      state = state.copyWith(
        isLoginLoading: false,
        failure: error is Failure
            ? error
            : const Failure(message: 'Unable to reset password'),
      );
      rethrow;
    }
  }

  Future<void> verifyOtp(String phone, String otp) async {
    state = state.copyWith(isLoginLoading: true, failure: null);
    try {
      final user = await _authRepository.verifyOtp(phone, otp);
      state = state.copyWith(
        status: AuthStatus.authenticated,
        user: user,
        isLoginLoading: false,
        isNewUser: user.name.trim().isEmpty,
      );
    } catch (e) {
      state = state.copyWith(isLoginLoading: false, failure: const Failure(message: 'Invalid OTP'));
    }
  }

  void resetOtp() {
    state = state.copyWith(otpSent: false, failure: null, isLoginLoading: false);
  }

  Future<void> updateName(String name) async {
    state = state.copyWith(user: state.user?.copyWith(name: name), isNewUser: false);
  }

  Future<void> logout() async {
    try {
      await _authRepository.logout();
    } catch (_) {
      // Clear the local state even if the server session has already expired.
    }
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  void clearFailure() {
    state = state.copyWith(failure: null);
  }

}
