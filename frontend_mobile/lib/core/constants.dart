class AppConstants {
  AppConstants._();

  static const String appName = 'JobCare Voice';
  
  // Use your PC's Local IP here if testing on a real phone (e.g., 192.168.1.5)
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1/'; 
  static const String sarvamBaseUrl = 'https://api.sarvam.ai';
  
  // Reduced timeouts to prevent the "Stuck" feeling
  static const Duration apiTimeout = Duration(seconds: 15);
  static const Duration authTimeout = Duration(seconds: 5); 

  static const String storageKeyToken = 'auth_token';
  static const String storageKeyRefreshToken = 'refresh_token';
  static const String storageKeyUser = 'user_data';
  static const String storageKeyLanguage = 'language';
  static const String storageKeyOnboardingSeen = 'onboarding_seen';

  static const String sarvamApiKey = 'sk_9b2kx6dd_mxkbQZedrPnA0SN4dlXc60DD';
}
