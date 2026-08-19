class AppConstants {
  AppConstants._();

  static const String appName = 'JobCare Voice';
  
  // Supplied at build time, for example:
  // --dart-define=API_BASE_URL=https://api.blieve.in/api/v1/
  // Never put provider credentials in a mobile application.
  // The default is the dev backend on the host PC's LAN IP (physical device
  // testing). For the Android emulator use:
  // --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1/
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://jobcare-xp3w.onrender.com/api/v1/',
  );
  
  // Reduced timeouts to prevent the "Stuck" feeling
  static const Duration apiTimeout = Duration(seconds: 15);
  static const Duration authTimeout = Duration(seconds: 5); 

  static const String storageKeyToken = 'auth_token';
  static const String storageKeyRefreshToken = 'refresh_token';
  static const String storageKeyUser = 'user_data';
  static const String storageKeyLanguage = 'language';
  static const String storageKeyOnboardingSeen = 'onboarding_seen';

  // OTP delivery channel. 'email' is the temporary channel while Exotel SMS
  // is blocked on DLT approval; flip to 'sms' when DLT clears to use the
  // phone OTP endpoints again. Must match backend AUTH_OTP_CHANNEL.
  static const String otpChannel = 'email';

  // Endpoints for the active OTP channel.
  static String get otpRequestEndpoint =>
      otpChannel == 'sms' ? 'auth/phone/send-otp/' : 'auth/otp/email/request/';

  static String get otpVerifyEndpoint =>
      otpChannel == 'sms' ? 'auth/phone/verify/' : 'auth/otp/email/verify/';

}
