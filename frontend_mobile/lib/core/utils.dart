import 'package:intl/intl.dart';

class Validators {
  Validators._();

  static String? phone(String? value) {
    if (value == null || value.trim().isEmpty) return 'Mobile number is required';
    final cleanValue = value.replaceAll(RegExp(r'[\s\-\(\)]'), '');
    if (cleanValue.length < 10) return 'Enter a 10-digit mobile number';
    return RegExp(r'^[6-9]\d{9}$').hasMatch(cleanValue) ? null : 'Please enter a valid Indian mobile number';
  }

  static String? name(String? value) {
    if (value == null || value.trim().isEmpty) return 'Name is required';
    return value.trim().length < 2 ? 'Enter your full name' : null;
  }

  static String? otp(String? value) => value != null && RegExp(r'^\d{6}$').hasMatch(value.trim()) ? null : 'Enter 6-digit OTP';

  static String? email(String? value) => value != null && RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(value.trim()) ? null : 'Enter a valid email';

  static String? password(String? value) {
    if (value == null || value.length < 8) return 'Password must be at least 8 characters';
    return RegExp(r'[A-Z]').hasMatch(value) && RegExp(r'[a-z]').hasMatch(value) && RegExp(r'\d').hasMatch(value) && RegExp(r'[^A-Za-z0-9]').hasMatch(value) ? null : 'Use uppercase, lowercase, number and symbol';
  }
}

class Formatters {
  Formatters._();

  static String currency(double amount) => '₹${NumberFormat('#,##,##0.00', 'en_IN').format(amount)}';
  static String dateTime(DateTime date) => DateFormat('dd MMM yyyy, hh:mm a').format(date);
  static String currencyCompact(num amount) {
    if (amount >= 100000) return '₹${(amount / 100000).toStringAsFixed(1)}L';
    if (amount >= 1000) return '₹${(amount / 1000).toStringAsFixed(1)}K';
    return '₹${amount.toStringAsFixed(0)}';
  }
  static String date(DateTime value) => DateFormat('dd MMM yyyy').format(value);
  static String relativeTime(DateTime value) {
    final difference = DateTime.now().difference(value);
    if (difference.inMinutes < 1) return 'Just now';
    if (difference.inHours < 1) return '${difference.inMinutes}m ago';
    if (difference.inDays < 1) return '${difference.inHours}h ago';
    return '${difference.inDays}d ago';
  }
  static String jobType(String value) => value.split('_').map((part) => part.isEmpty ? part : part[0].toUpperCase() + part.substring(1)).join(' ');
  static String fileSize(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }
  static String truncate(String value, int maxLength) => value.length <= maxLength ? value : '${value.substring(0, maxLength)}...';
}

extension StringExtensions on String {
  String capitalize() => isEmpty ? this : this[0].toUpperCase() + substring(1).toLowerCase();
  String get relative => 'Just now';
}
