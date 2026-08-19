import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/providers.dart';
import '../routes/route_names.dart';
import '../theme/app_colors.dart';
import '../widgets/voice_ring.dart';

class LanguageSelectionScreen extends ConsumerWidget {
  const LanguageSelectionScreen({super.key, this.returnToSettings = false});

  final bool returnToSettings;

  static const List<_Language> interfaceLanguages = [
    _Language('hi', 'हिन्दी (Hindi)'),
    _Language('kn', 'ಕನ್ನಡ (Kannada)'),
    _Language('en', 'English'),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedLanguage = ref.watch(languageProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const VoiceRing(
                size: 100,
                state: VoiceRingState.idle,
              ),
              const SizedBox(height: 32),
              const Text(
                'Apni bhasha chunein\nअपनी भाषा चुनें',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w900,
                  color: AppColors.primary,
                  height: 1.3,
                ),
              ),
              const SizedBox(height: 40),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 40),
                child: Column(
                  children: interfaceLanguages.map((lang) {
                    final isSelected = selectedLanguage == lang.code;
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: GestureDetector(
                        onTap: () async {
                          await ref
                              .read(languageProvider.notifier)
                              .setLanguage(lang.code);
                          if (!context.mounted) return;

                          if (returnToSettings) {
                            context.pop();
                          } else {
                            context.go(RouteNames.login);
                          }
                        },
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: double.infinity,
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                          decoration: BoxDecoration(
                            color: isSelected ? AppColors.primary : Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(
                              color: isSelected ? AppColors.primary : Colors.grey.shade200,
                              width: 2,
                            ),
                            boxShadow: isSelected ? [
                              BoxShadow(color: AppColors.primary.withOpacity(0.3), blurRadius: 10, offset: const Offset(0, 4))
                            ] : [],
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                lang.name,
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: isSelected ? Colors.white : AppColors.textPrimary,
                                ),
                              ),
                              if (isSelected)
                                const Icon(Icons.check_circle, size: 24, color: Colors.white),
                            ],
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Language {
  final String code;
  final String name;
  const _Language(this.code, this.name);
}
