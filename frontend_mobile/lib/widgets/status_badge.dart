import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/application_model.dart';
import '../theme/app_colors.dart';
import '../providers/providers.dart';

class StatusBadge extends ConsumerWidget {
  final ApplicationStatus status;
  final double fontSize;

  const StatusBadge({
    super.key,
    required this.status,
    this.fontSize = 11,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lang = ref.watch(languageProvider);
    final config = _getConfig(lang);
    
    if (config.isOutline) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: Colors.transparent,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: config.color, width: 1.2),
        ),
        child: Text(
          config.label,
          style: TextStyle(
            color: config.color,
            fontSize: fontSize,
            fontWeight: FontWeight.w600,
          ),
        ),
      );
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: config.color,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        config.label,
        style: TextStyle(
          color: Colors.white,
          fontSize: fontSize,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  _StatusConfig _getConfig(String lang) {
    switch (status) {
      case ApplicationStatus.applied:
        return _StatusConfig(AppColors.statusApplied, _getLabel('applied', lang), isOutline: true);
      case ApplicationStatus.underReview:
        return _StatusConfig(AppColors.statusUnderReview, _getLabel('under_review', lang));
      case ApplicationStatus.shortlisted:
        return _StatusConfig(AppColors.statusShortlisted, _getLabel('shortlisted', lang));
      case ApplicationStatus.interviewScheduled:
        return _StatusConfig(AppColors.statusInterviewScheduled, _getLabel('interview_scheduled', lang));
      case ApplicationStatus.selected:
        return _StatusConfig(AppColors.statusSelected, _getLabel('selected', lang));
      case ApplicationStatus.offered:
        return _StatusConfig(AppColors.statusOffered, _getLabel('offered', lang));
      case ApplicationStatus.hired:
        return _StatusConfig(AppColors.statusHired, _getLabel('hired', lang));
      case ApplicationStatus.rejected:
        return _StatusConfig(AppColors.statusRejected, _getLabel('rejected', lang));
      case ApplicationStatus.withdrawn:
        return _StatusConfig(AppColors.statusWithdrawn, _getLabel('withdrawn', lang));
    }
  }

  String _getLabel(String key, String lang) {
    final map = {
      'applied': {'en': 'Applied', 'hi': 'आवेदन किया', 'kn': 'ಅರ್ಜಿ ಸಲ್ಲಿಸಲಾಗಿದೆ'},
      'under_review': {'en': 'Under Review', 'hi': 'समीक्षा के अधीन', 'kn': 'ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ'},
      'shortlisted': {'en': 'Shortlisted', 'hi': 'शॉर्टलिस्ट किया गया', 'kn': 'ಶಾರ್ಟ್‌ಲಿಸ್ಟ್ ಮಾಡಲಾಗಿದೆ'},
      'interview_scheduled': {'en': 'Interview Scheduled', 'hi': 'इंटरव्यू तय', 'kn': 'ಸಂದರ್ಶನ ನಿಗದಿಯಾಗಿದೆ'},
      'selected': {'en': 'Selected', 'hi': 'चयनित', 'kn': 'ಆಯ್ಕೆಯಾಗಿದ್ದಾರೆ'},
      'offered': {'en': 'Offered', 'hi': 'ऑफर दिया गया', 'kn': 'ಆಫರ್ ನೀಡಲಾಗಿದೆ'},
      'hired': {'en': 'Hired', 'hi': 'नौकरी मिली', 'kn': 'ನೇಮಕಗೊಂಡಿದ್ದಾರೆ'},
      'rejected': {'en': 'Rejected', 'hi': 'अस्वीकृत', 'kn': 'ತಿರಸ್ಕರಿಸಲಾಗಿದೆ'},
      'withdrawn': {'en': 'Withdrawn', 'hi': 'वापस लिया', 'kn': 'ಹಿಂತೆಗೆದುಕೊಳ್ಳಲಾಗಿದೆ'},
    };
    return map[key]?[lang] ?? map[key]?['en'] ?? key;
  }
}

class _StatusConfig {
  final Color color;
  final String label;
  final bool isOutline;

  const _StatusConfig(this.color, this.label, {this.isOutline = false});
}
