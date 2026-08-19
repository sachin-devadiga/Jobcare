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
                  _buildSectionCard(AppStrings.get('work_experience', lang), Icons.work_outline, _editExperiences),
                  _buildSectionCard(AppStrings.get('education', lang), Icons.school_outlined, _editEducation),
                  _buildSectionCard(AppStrings.get('skills', lang), Icons.star_outline, _editSkills),
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

  Future<void> _editSkills() async {
    final profile = ref.read(profileProvider).employeeProfile;
    final value = await _showCollectionEditor(
      title: 'Skills',
      hint: 'One skill per line, e.g. Driving',
      initialValue: profile?.skills.join('\n') ?? '',
    );
    if (value == null) return;
    final skills = value
        .split('\n')
        .map((item) => item.trim())
        .where((item) => item.isNotEmpty)
        .toSet()
        .toList();
    await ref.read(profileProvider.notifier).updateEmployeeProfile(skills: skills);
  }

  Future<void> _editExperiences() async {
    final profile = ref.read(profileProvider).employeeProfile;
    final value = await _showCollectionEditor(
      title: 'Work Experience',
      hint: 'One entry per line: Company | Role',
      initialValue: (profile?.experiences ?? const [])
          .map((item) => '${item.company} | ${item.role}')
          .join('\n'),
    );
    if (value == null) return;
    final now = DateTime.now().toIso8601String();
    final experiences = value.split('\n').map((line) {
      final parts = line.split('|').map((part) => part.trim()).toList();
      return <String, dynamic>{
        'id': 'experience-${parts.join('-').hashCode}',
        'company': parts.isNotEmpty ? parts.first : '',
        'role': parts.length > 1 ? parts[1] : '',
        'start_date': now,
        'is_current': true,
      };
    }).where((item) => item['company'] != '' && item['role'] != '').toList();
    await ref.read(profileProvider.notifier).updateEmployeeProfile(experiences: experiences);
  }

  Future<void> _editEducation() async {
    final profile = ref.read(profileProvider).employeeProfile;
    final value = await _showCollectionEditor(
      title: 'Education',
      hint: 'One entry per line: Institution | Degree',
      initialValue: (profile?.education ?? const [])
          .map((item) => '${item.institution} | ${item.degree}')
          .join('\n'),
    );
    if (value == null) return;
    final now = DateTime.now().toIso8601String();
    final education = value.split('\n').map((line) {
      final parts = line.split('|').map((part) => part.trim()).toList();
      return <String, dynamic>{
        'id': 'education-${parts.join('-').hashCode}',
        'institution': parts.isNotEmpty ? parts.first : '',
        'degree': parts.length > 1 ? parts[1] : '',
        'start_date': now,
        'is_current': false,
      };
    }).where((item) => item['institution'] != '' && item['degree'] != '').toList();
    await ref.read(profileProvider.notifier).updateEmployeeProfile(education: education);
  }

  Future<String?> _showCollectionEditor({
    required String title,
    required String hint,
    required String initialValue,
  }) async {
    return showDialog<String>(
      context: context,
      builder: (_) => _CollectionEditorDialog(
        title: title,
        hint: hint,
        initialValue: initialValue,
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

/// Owns its controller for exactly the lifetime of the modal route. This lets
/// Flutter unmount the TextField before the controller is disposed.
class _CollectionEditorDialog extends StatefulWidget {
  const _CollectionEditorDialog({
    required this.title,
    required this.hint,
    required this.initialValue,
  });

  final String title;
  final String hint;
  final String initialValue;

  @override
  State<_CollectionEditorDialog> createState() => _CollectionEditorDialogState();
}

class _CollectionEditorDialogState extends State<_CollectionEditorDialog> {
  late final TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.initialValue);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.title),
      content: TextField(
        controller: _controller,
        minLines: 5,
        maxLines: 10,
        textCapitalization: TextCapitalization.sentences,
        decoration: InputDecoration(
          hintText: widget.hint,
          border: const OutlineInputBorder(),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: () => Navigator.pop(context, _controller.text),
          child: const Text('Save'),
        ),
      ],
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
