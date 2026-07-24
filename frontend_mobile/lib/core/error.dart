class Failure {
  final String message;
  final int? statusCode;
  final dynamic error;

  const Failure({
    this.message = 'An unexpected error occurred',
    this.statusCode,
    this.error,
  });

  @override
  String toString() => 'Failure(message: $message, statusCode: $statusCode)';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Failure &&
          runtimeType == other.runtimeType &&
          message == other.message &&
          statusCode == other.statusCode;

  @override
  int get hashCode => message.hashCode ^ statusCode.hashCode;
}

class ErrorMessages {
  ErrorMessages._();

  static const String networkError = 'No internet connection. Please check your network.';
  static const String backendOffline = 'Backend server is not running. Please start the server and try again.';
  static const String serverError = 'Server error. Please try again later.';
  static const String timeoutError = 'Request timed out. Please try again.';
  static const String unauthorized = 'Session expired. Please login again.';
  static const String notFound = 'Resource not found.';
  static const String validationError = 'Please check your input and try again.';
  static const String unknownError = 'Something went wrong. Please try again.';
  static const String emailInUse = 'This email is already registered.';
  static const String invalidCredentials = 'Invalid email or password.';
  static const String weakPassword = 'Password is too weak.';
  static const String invalidOtp = 'Invalid OTP. Please try again.';
  static const String expiredOtp = 'OTP has expired. Please request a new one.';
  static const String tooManyAttempts = 'Too many attempts. Please try again later.';
  static const String locationPermissionDenied = 'Location permission is required for nearby jobs.';
  static const String microphonePermissionDenied = 'Microphone permission is required for voice features.';
  static const String storagePermissionDenied = 'Storage permission is required to upload files.';
  static const String uploadFailed = 'Failed to upload file. Please try again.';
  static const String paymentFailed = 'Payment failed. Please try again.';
  static const String subscriptionExpired = 'Your subscription has expired. Please renew.';
  static const String voiceProcessingError = 'Failed to process voice input. Please try again.';
  static const String profileIncomplete = 'Please complete your profile before applying.';
  static const String alreadyApplied = 'You have already applied for this job.';
}

class ServerException implements Exception {
  final String message;
  final int? statusCode;

  const ServerException({this.message = 'Server error', this.statusCode});

  @override
  String toString() => 'ServerException(message: $message, statusCode: $statusCode)';
}

class NetworkException implements Exception {
  final String message;

  const NetworkException({this.message = ErrorMessages.networkError});

  @override
  String toString() => 'NetworkException(message: $message)';
}

class AuthException implements Exception {
  final String message;
  final int? statusCode;

  const AuthException({this.message = ErrorMessages.unauthorized, this.statusCode});

  @override
  String toString() => 'AuthException(message: $message, statusCode: $statusCode)';
}

class ValidationException implements Exception {
  final String message;
  final Map<String, String>? errors;

  const ValidationException({this.message = ErrorMessages.validationError, this.errors});

  @override
  String toString() => 'ValidationException(message: $message)';
}

Failure handleException(dynamic e) {
  if (e is ServerException) {
    return Failure(message: e.message, statusCode: e.statusCode, error: e);
  } else if (e is NetworkException) {
    return Failure(message: e.message, error: e);
  } else if (e is AuthException) {
    return Failure(message: e.message, statusCode: e.statusCode, error: e);
  } else if (e is ValidationException) {
    return Failure(message: e.message, error: e);
  } else if (e is Failure) {
    return e;
  }
  return const Failure(message: ErrorMessages.unknownError);
}
