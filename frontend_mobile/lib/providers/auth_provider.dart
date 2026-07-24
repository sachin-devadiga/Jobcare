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
    _listenable.notifyListeners();
  }

  Future<void> sendOtp(String phone) async {
    debugPrint('AUTH_ACTION: sendOtp called for $phone');
    state = state.copyWith(isLoginLoading: true, failure: null, otpSent: false);
    
    // MAGIC TEST NUMBER: Use 9876543000 to bypass server
    if (phone.endsWith('000') || phone == '9876543210') {
      debugPrint('AUTH_ACTION: Test Number Detected -> Bypassing Backend');
      await Future.delayed(const Duration(milliseconds: 500));
      state = state.copyWith(isLoginLoading: false, otpSent: true, failure: null);
      return;
    }

    try {
      // 5-second timeout for rapid feedback
      await _authRepository.sendOtp(phone).timeout(const Duration(seconds: 5));
      debugPrint('AUTH_ACTION: OTP Request Success');
      state = state.copyWith(isLoginLoading: false, otpSent: true, failure: null);
    } catch (e) {
      debugPrint('AUTH_ACTION: OTP Request Failed -> $e');
      state = state.copyWith(
        isLoginLoading: false, 
        otpSent: false,
        failure: const Failure(message: 'Cannot reach server. Use number ending in 000 to test without backend.'),
      );
    }
  }

  Future<void> loginWithEmail(String email, String password) async {
    state = state.copyWith(isLoginLoading: true, failure: null);
    try {
      final user = await _authRepository.loginWithEmail(email, password);
      state = state.copyWith(status: AuthStatus.authenticated, user: user, isLoginLoading: false);
    } catch (error) {
      state = state.copyWith(isLoginLoading: false, failure: error is Failure ? error : const Failure(message: 'Unable to sign in'));
    }
  }

  Future<void> loginWithPhone(String phone, String password) async {
    state = state.copyWith(isLoginLoading: true, failure: null);
    try {
      final user = await _authRepository.loginWithPhone(phone, password);
      state = state.copyWith(status: AuthStatus.authenticated, user: user, isLoginLoading: false);
    } catch (error) {
      state = state.copyWith(isLoginLoading: false, failure: error is Failure ? error : const Failure(message: 'Unable to sign in'));
    }
  }

  Future<void> register({required String name, required String email, required String phone, required String password, required String role}) async {
    state = state.copyWith(isRegisterLoading: true, failure: null);
    try {
      final user = await _authRepository.register(name: name, email: email, phone: phone, password: password, role: role);
      state = state.copyWith(status: AuthStatus.authenticated, user: user, isRegisterLoading: false);
    } catch (error) {
      state = state.copyWith(isRegisterLoading: false, failure: error is Failure ? error : const Failure(message: 'Unable to register'));
    }
  }

  Future<void> verifyOtp(String phone, String otp) async {
    debugPrint('AUTH_ACTION: verifyOtp called for $otp');
    state = state.copyWith(isLoginLoading: true, failure: null);
    
    // Master Test OTP: 123456 or 000000
    if (phone.endsWith('000') || phone == '9876543210') {
      if (otp == '123456' || otp == '000000') {
        final now = DateTime.now();
        final testUser = UserModel(
          id: 'test_id',
          email: 'worker@jobcare.voice',
          name: 'Test Worker',
          phone: phone,
          role: UserRole.employee,
          createdAt: now,
          updatedAt: now,
        );
        state = state.copyWith(status: AuthStatus.authenticated, user: testUser, isLoginLoading: false, isNewUser: true, otpSent: false);
        return;
      }
    }

    try {
      final user = await _authRepository.verifyOtp(phone, otp);
      final bool isNew = user.name.contains('User') || user.name == 'Test Worker';
      state = state.copyWith(status: AuthStatus.authenticated, user: user, isLoginLoading: false, isNewUser: isNew, otpSent: false);
    } catch (e) {
      state = state.copyWith(isLoginLoading: false, failure: const Failure(message: 'Invalid OTP. Try 123456 for testing.'));
    }
  }

  void resetOtp() {
    state = state.copyWith(otpSent: false, failure: null, isLoginLoading: false);
  }

  Future<void> updateName(String name) async {
    if (state.user == null) return;
    state = state.copyWith(
      user: state.user!.copyWith(name: name),
      isNewUser: false,
      isLoginLoading: false,
    );
  }

  void checkAuth() {
    state = state.copyWith(status: AuthStatus.unauthenticated);
  }

  Future<void> logout() async {
    try {
      await _authRepository.logout();
    } catch (_) {
      // Clear local state even if the network logout request fails.
    }
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  void skipLogin() {
    final now = DateTime.now();
    final guestUser = UserModel(
      id: 'guest',
      email: 'guest@jobcare.voice',
      name: 'Guest User',
      phone: '0000000000',
      role: UserRole.employee,
      createdAt: now,
      updatedAt: now,
    );
    state = state.copyWith(status: AuthStatus.authenticated, user: guestUser, otpSent: false, isNewUser: false);
  }

  void clearFailure() {
    state = state.copyWith(failure: null);
  }
}
