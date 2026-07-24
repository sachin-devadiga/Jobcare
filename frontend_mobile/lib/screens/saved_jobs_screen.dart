import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/providers.dart';
import '../theme/app_colors.dart';
import '../widgets/job_card.dart';
import '../widgets/empty_state.dart';
import '../widgets/shimmer_loading.dart';
import '../routes/route_names.dart';
import '../core/localization.dart';

class SavedJobsScreen extends ConsumerStatefulWidget {
  const SavedJobsScreen({super.key});

  @override
  ConsumerState<SavedJobsScreen> createState() => _SavedJobsScreenState();
}

class _SavedJobsScreenState extends ConsumerState<SavedJobsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(jobProvider.notifier).fetchSavedJobs();
    });
  }

  @override
  Widget build(BuildContext context) {
    final jobState = ref.watch(jobProvider);
    final savedJobs = jobState.savedJobs;
    final lang = ref.watch(languageProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text(
          AppStrings.get('saved', lang),
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18),
        ),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: _buildBody(jobState, savedJobs, lang),
    );
  }

  Widget _buildBody(jobState, List savedJobs, String lang) {
    if (jobState.isSavedLoading) {
      return const _SavedJobsShimmer();
    }

    if (savedJobs.isEmpty) {
      return EmptyState(
        icon: Icons.bookmark_border_rounded,
        title: lang == 'en' ? 'No saved jobs' : (lang == 'hi' ? 'कोई सेव की गई नौकरी नहीं' : 'ಯಾವುದೇ ಉಳಿಸಿದ ಕೆಲಸಗಳಿಲ್ಲ'),
        message: lang == 'en' ? 'Save jobs you like to view them later' : (lang == 'hi' ? 'अपनी पसंद की नौकरियों को बाद में देखने के लिए सेव करें' : 'ನೀವು ಇಷ್ಟಪಡುವ ಕೆಲಸಗಳನ್ನು ನಂತರ ನೋಡಲು ಉಳಿಸಿ'),
      );
    }

    return RefreshIndicator(
      onRefresh: () async {
        await ref.read(jobProvider.notifier).fetchSavedJobs();
      },
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: savedJobs.length,
        itemBuilder: (context, index) {
          final job = savedJobs[index];
          return JobCard(
            job: job,
            onTap: () => context.push('${RouteNames.jobDetail}/${job.id}'),
            onSave: () {
              ref.read(jobProvider.notifier).toggleSaveJob(job.id);
            },
          );
        },
      ),
    );
  }
}

class _SavedJobsShimmer extends StatelessWidget {
  const _SavedJobsShimmer();

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 5,
      itemBuilder: (context, index) {
        return const Padding(
          padding: EdgeInsets.only(bottom: 12),
          child: ShimmerLoading(
            width: double.infinity,
            height: 140,
          ),
        );
      },
    );
  }
}
