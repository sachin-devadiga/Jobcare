import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_theme.dart' as brand;

class AppTheme {
  AppTheme._();

  static ThemeData light(String lang) => brand.AppTheme.light(lang);
  static ThemeData dark(String lang) => brand.AppTheme.dark(lang);

  static ThemeData getTheme(ThemeMode mode, String lang) {
    switch (mode) {
      case ThemeMode.dark:
        return dark(lang);
      case ThemeMode.light:
        return light(lang);
      default:
        return light(lang);
    }
  }

  static LinearGradient get primaryGradient => const LinearGradient(
        colors: [
          AppColors.primary,
          Color(0xFF2C5A7A),
        ],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      );

  static LinearGradient get accentGradient => const LinearGradient(
        colors: [
          AppColors.secondary,
          Color(0xFFF7B84D),
        ],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      );

  static BoxDecoration glassDecoration({
    required double blur,
    required double opacity,
    required double borderRadius,
  }) => BoxDecoration(
        color: Colors.white.withValues(alpha: opacity.clamp(0.0, 1.0)),
        borderRadius: BorderRadius.circular(borderRadius),
        border: Border.all(color: Colors.white.withValues(alpha: 0.25)),
      );
}
