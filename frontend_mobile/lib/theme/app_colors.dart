import 'package:flutter/material.dart';

class AppColors {
  AppColors._();

  // Primary
  static const Color primary = Color(0xFF1565C0); // Royal Blue (Apna Style)
  static const Color primaryLight = Color(0xFF534BAE);
  static const Color primaryDark = Color(0xFF000051);
  static const Color primaryGradientStart = Color(0xFF1A237E);
  static const Color primaryGradientEnd = Color(0xFF6A1B9A);

  // Secondary
  static const Color secondary = Color(0xFFFFB300); // Amber/Marigold
  static const Color secondaryLight = Color(0xFF62EFFF);
  static const Color secondaryDark = Color(0xFF008BA3);

  // Accent
  static const Color accent = Color(0xFFFF6F00);
  static const Color accentLight = Color(0xFFFFA040);
  static const Color accentDark = Color(0xFFC43E00);

  // Success / Error / Warning / Info
  static const Color success = Color(0xFF2E7D32);
  static const Color error = Color(0xFFD32F2F);
  static const Color warning = Color(0xFFF57C00);
  static const Color info = Color(0xFF0288D1);

  // Surface / Background
  static const Color surfaceLight = Color(0xFFF8FAFC);
  static const Color surfaceDark = Color(0xFF121212);
  static const Color backgroundLight = Color(0xFFFFFFFF);
  static const Color backgroundDark = Color(0xFF0D0D0D);

  // Card
  static const Color cardLight = Color(0xFFFFFFFF);
  static const Color cardDark = Color(0xFF1E293B);
  static const Color cardGlassLight = Color(0xB3FFFFFF);
  static const Color cardGlassDark = Color(0xB31E1E1E);

  // Text
  static const Color textPrimaryLight = Color(0xFF1E293B);
  static const Color textSecondaryLight = Color(0xFF64748B);
  static const Color textHintLight = Color(0xFF94A3B8);
  static const Color textPrimaryDark = Color(0xFFE0E0E0);
  static const Color textSecondaryDark = Color(0xFF9E9E9E);
  static const Color textHintDark = Color(0xFF616161);

  // Divider
  static const Color dividerLight = Color(0xFFE0E0E0);
  static const Color dividerDark = Color(0xFF424242);

  // Chip
  static const Color chipBackgroundLight = Color(0xFFE8EAF6);
  static const Color chipBackgroundDark = Color(0xFF263238);

  // Shimmer
  static const Color shimmerBaseLight = Color(0xFFE0E0E0);
  static const Color shimmerHighlightLight = Color(0xFFF5F5F5);
  static const Color shimmerBaseDark = Color(0xFF2C2C2C);
  static const Color shimmerHighlightDark = Color(0xFF3C3C3C);

  // Gradient combinations
  static const List<Color> primaryGradient = [
    primaryGradientStart,
    primaryGradientEnd,
  ];

  static const List<Color> accentGradient = [
    accent,
    Color(0xFFFF8F00),
  ];

  static const List<Color> successGradient = [
    success,
    Color(0xFF66BB6A),
  ];

  static const List<Color> infoGradient = [
    info,
    Color(0xFF64B5F6),
  ];

  static const List<Color> warningGradient = [
    warning,
    Color(0xFFFFCA28),
  ];

  static const List<Color> sunsetGradient = [
    Color(0xFFFF6F00),
    Color(0xFFE53935),
  ];

  static const List<Color> oceanGradient = [
    Color(0xFF1A237E),
    Color(0xFF00BCD4),
  ];

  static const List<Color> glassGradient = [
    Color(0xB3FFFFFF),
    Color(0x80FFFFFF),
  ];

  static const List<Color> darkGlassGradient = [
    Color(0xB31E1E1E),
    Color(0x801E1E1E),
  ];

  // Chat
  static const Color chatOwnBubble = primary;
  static const Color chatOtherBubble = Color(0xFFF1F5F9);

  // Notification categories
  static const Color notifJobMatch = primary;
  static const Color notifAppStatus = Color(0xFF00897B);

  // Application status pill palette
  static const Color statusApplied = Color(0xFF78909C);
  static const Color statusUnderReview = Color(0xFF42A5F5);
  static const Color statusShortlisted = Color(0xFFAB47BC);
  static const Color statusInterviewScheduled = Color(0xFF00897B);
  static const Color statusSelected = Color(0xFF7CB342);
  static const Color statusOffered = Color(0xFFF57C00);
  static const Color statusHired = Color(0xFF3949AB);
  static const Color statusRejected = Color(0xFFE53935);
  static const Color statusWithdrawn = Color(0xFF9E9E9E);

  // Legacy status colors (kept for backward compatibility)
  static const Color pending = Color(0xFFFFA726);
  static const Color approved = Color(0xFF4CAF50);
  static const Color rejected = Color(0xFFE53935);
  static const Color interviewed = Color(0xFF42A5F5);
  static const Color shortlisted = Color(0xFFAB47BC);
  static const Color hired = Color(0xFF66BB6A);
  static const Color withdrawn = Color(0xFF9E9E9E);

  // Social
  static const Color google = Color(0xFFDB4437);
  static const Color facebook = Color(0xFF4267B2);
  static const Color linkedin = Color(0xFF0077B5);
  static const Color twitter = Color(0xFF1DA1F2);
  static const Color whatsapp = Color(0xFF25D366);

  // Misc
  static const Color rust = Color(0xFFB7410E);
  static const Color verifiedGreen = Color(0xFF3B6D11);

  // Navy/Marigold theme colors
  static const Color navy = primary;
  static const Color marigold = secondary;
  static const Color paper = backgroundLight;
  static const Color ink = textPrimaryLight;

  // Legacy aliases
  static const Color indigo = primary;
  static const Color marigoldAmber = secondary;
  static const Color textPrimary = textPrimaryLight;
  static const Color textSecondary = textSecondaryLight;
  static const Color textHint = textHintLight;
  static const Color surface = surfaceLight;
  static const Color background = backgroundLight;

  // Derived ColorScheme
  static ColorScheme get lightColorScheme => const ColorScheme.light(
        primary: primary,
        onPrimary: Colors.white,
        secondary: secondary,
        onSecondary: Colors.black,
        surface: backgroundLight,
        onSurface: textPrimaryLight,
        error: error,
        onError: Colors.white,
      );
}
