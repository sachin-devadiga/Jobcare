import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/app_colors.dart';
import '../providers/providers.dart';

class VerifiedBadge extends ConsumerWidget {
  final bool isVerified;

  const VerifiedBadge({super.key, this.isVerified = false});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (!isVerified) return const SizedBox.shrink();
    final lang = ref.watch(languageProvider);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: AppColors.success,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.check, size: 10, color: Colors.white),
          const SizedBox(width: 3),
          Text(
            lang == 'hi' ? 'वेरिफाइड' : (lang == 'kn' ? 'ಪರಿಶೀಲಿಸಲಾಗಿದೆ' : 'Verified'),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 9,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
