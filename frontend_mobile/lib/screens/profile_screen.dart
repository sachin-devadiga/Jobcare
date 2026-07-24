import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/providers.dart';
import '../routes/route_names.dart';
import '../theme/app_colors.dart';
import '../widgets/shimmer_loading.dart';
import '../core/localization.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(profileProvider.notifier).fetchEmployeeProfile();
    });
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final profileState = ref.watch(profileProvider);
    final profile = profileState.employeeProfile;
    final user = authState.user;
    final lang = ref.watch(languageProvider);

    return Scaffold(
      backgroundColor: AppColors.surface,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text(AppStrings.get('my_profile', lang), style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: Colors.white),
            onPressed: () => context.push(RouteNames.settings),
          ),
        ],
      ),
      body: profileState.isLoading && profile == null
          ? const _ProfileShimmer()
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  _buildProfileHeader(user, profile, lang),
                  const SizedBox(height: 16),
                  _buildCompletionCard(profile?.completionScore ?? 0.7, lang),
                  const SizedBox(height: 16),
                  _buildActionCard(
                    icon: Icons.mic_rounded,
                    title: AppStrings.get('voice_resume', lang),
                    subtitle: AppStrings.get('voice_resume_pref', lang),
                    onTap: () => context.push(RouteNames.voiceResume),
                    isHighlight: true,
                    lang: lang,
                  ),
                  const SizedBox(height: 16),
                  _buildSectionCard(AppStrings.get('work_experience', lang), Icons.work_outline, () {}),
                  _buildSectionCard(AppStrings.get('education', lang), Icons.school_outlined, () {}),
                  _buildSectionCard(AppStrings.get('skills', lang), Icons.star_outline, () {}),
                  const SizedBox(height: 24),
                  _buildLogoutButton(lang),
                  const SizedBox(height: 100),
                ],
              ),
            ),
    );
  }

  Widget _buildProfileHeader(dynamic user, dynamic profile, String lang) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 35,
            backgroundColor: AppColors.primary.withOpacity(0.1),
            child: const Icon(Icons.person, size: 40, color: AppColors.primary),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(user?.name ?? 'User Name', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(profile?.city ?? AppStrings.get('location_not_set', lang), style: TextStyle(color: Colors.grey.shade600)),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.edit_outlined, color: AppColors.primary),
            onPressed: () => context.push(RouteNames.editProfile),
          ),
        ],
      ),
    );
  }

  Widget _buildCompletionCard(double score, String lang) {
    final int percent = (score * 100).toInt();
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFE3F2FD),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          CircularProgressIndicator(value: score, backgroundColor: Colors.white, color: AppColors.primary),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(AppStrings.get('profile_complete_title', lang, [percent.toString()]), 
                  style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary)),
                Text(AppStrings.get('profile_completion_msg', lang), 
                  style: const TextStyle(fontSize: 12, color: AppColors.primary)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionCard({required IconData icon, required String title, required String subtitle, required VoidCallback onTap, bool isHighlight = false, required String lang}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isHighlight ? AppColors.secondary.withOpacity(0.1) : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: isHighlight ? AppColors.secondary : Colors.grey.shade200),
        ),
        child: Row(
          children: [
            Icon(icon, color: isHighlight ? AppColors.secondary : AppColors.primary),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
                  Text(subtitle, style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Colors.grey),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionCard(String title, IconData icon, VoidCallback onTap) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: ListTile(
        leading: Icon(icon, color: AppColors.primary),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
        trailing: const Icon(Icons.add, color: AppColors.primary),
        onTap: onTap,
      ),
    );
  }

  Widget _buildLogoutButton(String lang) {
    return TextButton(
      onPressed: () => ref.read(authProvider.notifier).logout(),
      child: Text(AppStrings.get('logout', lang), style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
    );
  }
}

class _ProfileShimmer extends StatelessWidget {
  const _ProfileShimmer();
  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.all(16),
      child: Column(children: [ShimmerLoading(width: double.infinity, height: 100), SizedBox(height: 16), ShimmerLoading(width: double.infinity, height: 60)]),
    );
  }
}
