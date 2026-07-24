import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../routes/route_names.dart';
import '../theme/app_colors.dart';
import '../providers/providers.dart';
import '../core/localization.dart';

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  List<_OnboardingPageData> _getPages(String lang) {
    return [
      _OnboardingPageData(
        icon: Icons.mic_rounded,
        title: AppStrings.get('hero_title', lang),
        subtitle: 'Apply by Speaking',
        description: lang == 'hi' 
            ? 'अब टाइप करने की ज़रूरत नहीं। बस माइक बटन दबाएं और बोलें।' 
            : (lang == 'kn' ? 'ಟೈಪ್ ಮಾಡುವ ಅಗತ್ಯವಿಲ್ಲ. ಮೈಕ್ ಬಟನ್ ಒತ್ತಿ ಮತ್ತು ಮಾತನಾಡಿ.' : 'No need to type. Just tap the mic and speak.'),
      ),
      _OnboardingPageData(
        icon: Icons.location_on_rounded,
        title: lang == 'hi' ? 'आपके पास की जॉब्स' : (lang == 'kn' ? 'ನಿಮ್ಮ ಹತ್ತಿರದ ಕೆಲಸಗಳು' : 'Jobs Near You'),
        subtitle: 'Local Opportunities',
        description: lang == 'hi'
            ? 'अपने घर के पास डिलीवरी, ड्राइवर, या सिक्योरिटी की बेस्ट जॉब्स पाएं।'
            : (lang == 'kn' ? 'ನಿಮ್ಮ ಮನೆಯ ಹತ್ತಿರದ ಡೆಲಿವರಿ, ಡ್ರೈವರ್ ಅಥವಾ ಸೆಕ್ಯುರಿಟಿ ಕೆಲಸಗಳನ್ನು ಹುಡುಕಿ.' : 'Find the best delivery, driver, or security jobs near your home.'),
      ),
      _OnboardingPageData(
        icon: Icons.verified_user_rounded,
        title: lang == 'hi' ? '100% वेरिफाइड' : (lang == 'kn' ? '100% ಪರಿಶೀಲಿಸಿದ ಕೆಲಸಗಳು' : '100% Verified'),
        subtitle: 'Trusted Employers',
        description: lang == 'hi'
            ? 'सारी जॉब्स वेरिफाइड हैं। बिना किसी डर के अप्लाई करें।'
            : (lang == 'kn' ? 'ಎಲ್ಲಾ ಕೆಲಸಗಳು ಪರಿಶೀಲಿಸಲ್ಪಟ್ಟಿವೆ. ಯಾವುದೇ ಭಯವಿಲ್ಲದೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ.' : 'All jobs are verified. Apply without any worries.'),
      ),
    ];
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  Future<void> _onFinish() async {
    final storage = ref.read(storageServiceProvider);
    await storage.setOnboardingSeen();
    if (mounted) {
      context.go(RouteNames.languageSelection);
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = ref.watch(languageProvider);
    final pages = _getPages(lang);

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            Align(
              alignment: Alignment.topRight,
              child: TextButton(
                onPressed: _onFinish,
                child: Text(lang == 'hi' ? 'छोड़ें' : (lang == 'kn' ? 'ಬಿಟ್ಟುಬಿಡಿ' : 'Skip'), 
                  style: const TextStyle(color: AppColors.textSecondary, fontSize: 16, fontWeight: FontWeight.w600)),
              ),
            ),
            Expanded(
              child: PageView.builder(
                controller: _pageController,
                onPageChanged: (index) => setState(() => _currentPage = index),
                itemCount: pages.length,
                itemBuilder: (context, index) {
                  final page = pages[index];
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 40),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 200, height: 200,
                          decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.05), shape: BoxShape.circle),
                          child: Icon(page.icon, size: 100, color: AppColors.primary),
                        ),
                        const SizedBox(height: 50),
                        Text(page.title, textAlign: TextAlign.center, 
                          style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: AppColors.primary)),
                        const SizedBox(height: 12),
                        Text(page.description, textAlign: TextAlign.center, 
                          style: const TextStyle(fontSize: 16, color: AppColors.textSecondary, height: 1.5)),
                      ],
                    ),
                  );
                },
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 40),
              child: Column(
                children: [
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: ElevatedButton(
                      onPressed: () {
                        if (_currentPage < pages.length - 1) {
                          _pageController.nextPage(duration: const Duration(milliseconds: 400), curve: Curves.easeInOut);
                        } else {
                          _onFinish();
                        }
                      },
                      child: Text(_currentPage < pages.length - 1 
                        ? (lang == 'hi' ? 'अगला' : (lang == 'kn' ? 'ಮುಂದೆ' : 'NEXT')) 
                        : (lang == 'hi' ? 'शुरू करें' : (lang == 'kn' ? 'ಪ್ರಾರಂಭಿಸಿ' : 'GET STARTED'))),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _OnboardingPageData {
  final IconData icon;
  final String title;
  final String subtitle;
  final String description;
  const _OnboardingPageData({required this.icon, required this.title, required this.subtitle, required this.description});
}
