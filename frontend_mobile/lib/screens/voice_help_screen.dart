import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/app_colors.dart';
import '../core/localization.dart';
import '../providers/providers.dart';

class VoiceHelpScreen extends ConsumerWidget {
  const VoiceHelpScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lang = ref.watch(languageProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text(
          AppStrings.get('voice_help_title', lang),
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.05),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline_rounded, color: AppColors.primary, size: 28),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Text(
                      AppStrings.get('voice_help_desc', lang),
                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, height: 1.4),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),
            _buildSection(
              title: AppStrings.get('search_examples', lang),
              icon: Icons.search_rounded,
              examples: [
                AppStrings.get('example_search_1', lang),
                AppStrings.get('example_search_2', lang),
                AppStrings.get('example_search_3', lang),
              ],
            ),
            const SizedBox(height: 32),
            _buildSection(
              title: AppStrings.get('nav_examples', lang),
              icon: Icons.navigation_rounded,
              examples: [
                AppStrings.get('example_nav_1', lang),
                AppStrings.get('example_nav_2', lang),
                AppStrings.get('example_nav_3', lang),
              ],
            ),
            const SizedBox(height: 100),
          ],
        ),
      ),
    );
  }

  Widget _buildSection({required String title, required IconData icon, required List<String> examples}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: AppColors.primary, size: 24),
            const SizedBox(width: 12),
            Text(
              title,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppColors.primary),
            ),
          ],
        ),
        const SizedBox(height: 16),
        ...examples.map((example) => Padding(
          padding: const EdgeInsets.only(bottom: 12, left: 36),
          child: Text(
            example,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade800,
              fontWeight: FontWeight.w600,
              fontStyle: FontStyle.italic,
            ),
          ),
        )),
      ],
    );
  }
}
