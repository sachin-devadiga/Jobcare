import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/app_colors.dart';
import '../core/localization.dart';
import '../providers/providers.dart';

class SearchBarWidget extends ConsumerWidget {
  final ValueChanged<String>? onSubmitted;
  final String? initialValue;

  const SearchBarWidget({
    super.key,
    this.onSubmitted,
    this.initialValue,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lang = ref.watch(languageProvider);
    
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 15,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: TextField(
        onSubmitted: onSubmitted,
        controller: TextEditingController(text: initialValue),
        decoration: InputDecoration(
          hintText: AppStrings.get('search_hint', lang),
          hintStyle: TextStyle(
            color: AppColors.textHint,
            fontSize: 15,
            fontWeight: FontWeight.w500,
          ),
          prefixIcon: const Icon(
            Icons.search_rounded,
            color: AppColors.primary,
            size: 24,
          ),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
        ),
      ),
    );
  }
}
