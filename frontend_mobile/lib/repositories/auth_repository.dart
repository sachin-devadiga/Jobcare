import '../services/auth_service.dart';
import '../services/storage_service.dart';
import '../models/user_model.dart';

class AuthRepository {
  final AuthService _authService;
  final StorageService _storageService;

  AuthRepository(this._authService, this._storageService);

  Future<void> sendOtp(String phone, {String? email}) async {
    await _authService.sendOtp(phone: phone, email: email);
  }

  Future<UserModel> loginWithEmail(String email, String password) async {
    return _authService.loginWithEmail(email: email, password: password);
  }

  Future<UserModel> loginWithPhone(String phone, String password) async {
    return _authService.loginWithPhone(phone: phone, password: password);
  }

  Future<UserModel> register({String? name, String? email, String? phone, String? password, String? role}) async {
    return _authService.register(
      name: name ?? '', email: email ?? '', phone: phone ?? '', password: password ?? '', role: role ?? 'employee',
    );
  }

  Future<void> forgotPassword(String email) async {
    await _authService.forgotPassword(email: email);
  }

  Future<void> resetPassword({
    required String email,
    required String otp,
    required String password,
  }) async {
    await _authService.resetPassword(email: email, otp: otp, password: password);
  }

  Future<UserModel> verifyOtp(String phone, String otp, {String? name}) async {
    return await _authService.verifyOtp(phone: phone, otp: otp, name: name);
  }

  Future<UserModel> getCurrentUser() async {
    return await _authService.getCurrentUser();
  }

  Future<UserModel?> restoreSession() async {
    return _authService.restoreSession();
  }

  Future<void> logout() async {
    await _authService.logout();
  }

  Future<bool> isLoggedIn() async {
    final token = await _storageService.readToken();
    return token != null && token.isNotEmpty;
  }

  Future<UserModel?> getSavedUser() async {
    final userData = await _storageService.readUserData();
    if (userData == null) return null;
    try {
      return UserModel.fromJsonString(userData);
    } catch (_) {
      return null;
    }
  }
}
