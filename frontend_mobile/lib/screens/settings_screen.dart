import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/providers.dart';
import '../theme/app_colors.dart';
import '../routes/route_names.dart';
import '../core/localization.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lang = ref.watch(languageProvider);

    return Scaffold(
      backgroundColor: AppColors.surface,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text(
          lang == 'hi' ? 'सेटिंग्स' : (lang == 'kn' ? 'ಸೆಟ್ಟಿಂಗ್‌ಗಳು' : 'Settings'), 
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)
        ),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildSection(lang == 'hi' ? 'अकाउंट सेटिंग्स' : (lang == 'kn' ? 'ಖಾತೆ ಸೆಟ್ಟಿಂಗ್‌ಗಳು' : 'Account Settings')),
          _buildSettingTile(
            icon: Icons.language_rounded,
            title: lang == 'hi' ? 'ऐप की भाषा' : (lang == 'kn' ? 'ಅಪ್ಲಿಕೇಶನ್ ಭಾಷೆ' : 'App Language'),
            subtitle: lang == 'hi' ? 'हिन्दी (Hindi)' : (lang == 'kn' ? 'ಕನ್ನಡ (Kannada)' : 'English'),
            onTap: () => context.push('${RouteNames.languageSelection}?from=settings'),
          ),
          _buildSettingTile(
            icon: Icons.notifications_active_outlined,
            title: lang == 'hi' ? 'नोटिफिकेशन' : (lang == 'kn' ? 'ಸೂಚನೆಗಳು' : 'Notifications'),
            subtitle: lang == 'hi' ? 'चालू है' : (lang == 'kn' ? 'ಆನ್ ಆಗಿದೆ' : 'On'),
            onTap: () => context.push(RouteNames.notifications),
          ),
          const SizedBox(height: 24),
          _buildSection(lang == 'hi' ? 'वॉयस असिस्टेंट' : (lang == 'kn' ? 'ವಾಯ್ಸ್ ಅಸಿಸ್ಟೆಂಟ್' : 'Voice Assistant')),
          _buildSettingTile(
            icon: Icons.record_voice_over_rounded,
            title: lang == 'hi' ? 'मदद और गाइड' : (lang == 'kn' ? 'ಸಹಾಯ ಮತ್ತು ಮಾರ್ಗದರ್ಶಿ' : 'Help & Guide'),
            onTap: () => context.push(RouteNames.voiceHelp), // Navigates to Voice Help
          ),
          const SizedBox(height: 24),
          _buildLogoutTile(lang, ref),
        ],
      ),
    );
  }

  Widget _buildSection(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 8, bottom: 8),
      child: Text(title.toUpperCase(), 
        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.textSecondary, letterSpacing: 1)),
    );
  }

  Widget _buildSettingTile({required IconData icon, required String title, String? subtitle, required VoidCallback onTap}) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: ListTile(
        leading: Icon(icon, color: AppColors.primary),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: subtitle != null ? Text(subtitle) : null,
        trailing: const Icon(Icons.chevron_right, size: 20),
        onTap: onTap,
      ),
    );
  }

  Widget _buildLogoutTile(String lang, WidgetRef ref) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red.withOpacity(0.1)),
      ),
      child: ListTile(
        leading: const Icon(Icons.logout, color: Colors.red),
        title: Text(AppStrings.get('logout', lang), style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
        onTap: () => ref.read(authProvider.notifier).logout(),
      ),
    );
  }
}
