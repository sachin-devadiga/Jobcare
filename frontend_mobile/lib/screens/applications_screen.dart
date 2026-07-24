import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/providers.dart';
import '../providers/application_provider.dart';
import '../providers/job_provider.dart';
import '../models/application_model.dart';
import '../models/job_model.dart';
import '../theme/app_colors.dart';
import '../widgets/shimmer_loading.dart';
import '../widgets/status_badge.dart';
import '../widgets/empty_state.dart';
import '../routes/route_names.dart';
import '../core/localization.dart';

class ApplicationsScreen extends ConsumerStatefulWidget {
  const ApplicationsScreen({super.key});

  @override
  ConsumerState<ApplicationsScreen> createState() => _ApplicationsScreenState();
}

class _ApplicationsScreenState extends ConsumerState<ApplicationsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(applicationProvider.notifier).fetchApplications(refresh: true);
      ref.read(jobProvider.notifier).fetchSavedJobs();
      ref.read(applicationProvider.notifier).fetchInterviews();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final appState = ref.watch(applicationProvider);
    final jobState = ref.watch(jobProvider);
    final lang = ref.watch(languageProvider);

    return Scaffold(
      backgroundColor: AppColors.surface,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text(AppStrings.get('applied', lang), 
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppColors.secondary,
          indicatorWeight: 3,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
          tabs: [
            Tab(text: AppStrings.get('applied', lang)),
            Tab(text: AppStrings.get('saved', lang)),
            Tab(text: AppStrings.get('interviews', lang)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildAppliedTab(appState, lang),
          _buildSavedTab(jobState, lang),
          _buildInterviewsTab(appState, lang),
        ],
      ),
    );
  }

  Widget _buildAppliedTab(ApplicationState state, String lang) {
    if (state.isLoading && state.applications.isEmpty) return const _ListShimmer();
    if (state.applications.isEmpty) {
      return EmptyState(
        icon: Icons.assignment_outlined,
        title: AppStrings.get('no_applications', lang),
        message: AppStrings.get('no_applied_desc', lang),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: state.applications.length,
      itemBuilder: (context, index) => _ApplicationItem(
        application: state.applications[index],
        onTap: () => context.push('${RouteNames.jobDetail}/${state.applications[index].jobId}'),
      ),
    );
  }

  Widget _buildSavedTab(JobState state, String lang) {
    if (state.isSavedLoading) return const _ListShimmer();
    if (state.savedJobs.isEmpty) {
      return EmptyState(
        icon: Icons.bookmark_border_rounded,
        title: AppStrings.get('saved', lang),
        message: AppStrings.get('no_saved_desc', lang),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: state.savedJobs.length,
      itemBuilder: (context, index) => _SavedJobItem(
        job: state.savedJobs[index],
        onTap: () => context.push('${RouteNames.jobDetail}/${state.savedJobs[index].id}'),
        onUnsave: () => ref.read(jobProvider.notifier).toggleSaveJob(state.savedJobs[index].id),
      ),
    );
  }

  Widget _buildInterviewsTab(ApplicationState state, String lang) {
    if (state.isLoading && state.interviews.isEmpty) return const _ListShimmer();
    if (state.interviews.isEmpty) {
      return EmptyState(
        icon: Icons.calendar_today_rounded,
        title: AppStrings.get('interviews', lang),
        message: AppStrings.get('no_interviews_desc', lang),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: state.interviews.length,
      itemBuilder: (context, index) => _InterviewItem(application: state.interviews[index], lang: lang),
    );
  }
}

class _ApplicationItem extends StatelessWidget {
  final ApplicationModel application;
  final VoidCallback onTap;
  const _ApplicationItem({required this.application, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade200),
        ),
        child: Row(
          children: [
            Container(
              width: 44, height: 44,
              decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(8)),
              child: const Icon(Icons.business_rounded, color: AppColors.primary),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(application.job?.title ?? 'Job Title', 
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                  Text(application.job?.company?.name ?? 'Company', 
                    style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
                ],
              ),
            ),
            StatusBadge(status: application.status),
          ],
        ),
      ),
    );
  }
}

class _SavedJobItem extends StatelessWidget {
  final JobModel job;
  final VoidCallback onTap;
  final VoidCallback onUnsave;
  const _SavedJobItem({required this.job, required this.onTap, required this.onUnsave});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade200),
        ),
        child: Row(
          children: [
            Container(
              width: 44, height: 44,
              decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(8)),
              child: const Icon(Icons.bookmark_rounded, color: AppColors.primary),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(job.title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                  Text(job.company?.name ?? 'Company', style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
                ],
              ),
            ),
            IconButton(
              icon: const Icon(Icons.bookmark_remove_rounded, color: AppColors.secondary),
              onPressed: onUnsave,
            ),
          ],
        ),
      ),
    );
  }
}

class _InterviewItem extends StatelessWidget {
  final ApplicationModel application;
  final String lang;
  const _InterviewItem({required this.application, required this.lang});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.primary.withOpacity(0.2), width: 1.5),
      ),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(Icons.videocam_rounded, color: AppColors.primary),
              const SizedBox(width: 12),
              Expanded(
                child: Text('${AppStrings.get('interview_for', lang)} ${application.job?.title}', 
                  style: const TextStyle(fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          const Divider(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(AppStrings.get('tomorrow', lang) + ', 10:30 AM', style: const TextStyle(fontWeight: FontWeight.w600)),
              TextButton(
                onPressed: () async {
                  final link = application.interview?.meetingLink ?? 'https://meet.google.com';
                  final uri = Uri.parse(link);
                  if (await canLaunchUrl(uri)) {
                    await launchUrl(uri, mode: LaunchMode.externalApplication);
                  }
                }, 
                child: Text(AppStrings.get('join_link', lang))
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _ListShimmer extends StatelessWidget {
  const _ListShimmer();
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 4,
      itemBuilder: (context, index) => const ShimmerLoading(width: double.infinity, height: 80, margin: EdgeInsets.only(bottom: 12)),
    );
  }
}
