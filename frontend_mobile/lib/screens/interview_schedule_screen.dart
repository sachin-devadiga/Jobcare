import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/providers.dart';
import '../providers/application_provider.dart';
import '../models/application_model.dart';
import '../theme/app_colors.dart';
import '../widgets/empty_state.dart';
import '../widgets/shimmer_loading.dart';
import '../core/utils.dart';
import '../core/localization.dart';

class InterviewScheduleScreen extends ConsumerStatefulWidget {
  const InterviewScheduleScreen({super.key});

  @override
  ConsumerState<InterviewScheduleScreen> createState() => _InterviewScheduleScreenState();
}

class _InterviewScheduleScreenState extends ConsumerState<InterviewScheduleScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(applicationProvider.notifier).fetchApplications(refresh: true);
      ref.read(applicationProvider.notifier).fetchInterviews();
    });
  }

  IconData _getTypeIcon(String? type) {
    switch (type?.toLowerCase()) {
      case 'in_person': return Icons.person_pin_circle_rounded;
      case 'video': return Icons.videocam_rounded;
      case 'phone': return Icons.phone_rounded;
      default: return Icons.calendar_today_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    final appState = ref.watch(applicationProvider);
    final lang = ref.watch(languageProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        elevation: 0,
        title: Text(AppStrings.get('interviews', lang), 
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: _buildBody(appState, lang),
    );
  }

  Widget _buildBody(ApplicationState state, String lang) {
    if (state.isLoading && state.interviews.isEmpty) {
      return ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: 4,
        itemBuilder: (context, index) => const ShimmerLoading(width: double.infinity, height: 160, margin: EdgeInsets.only(bottom: 12)),
      );
    }

    if (state.interviews.isEmpty) {
      return EmptyState(
        icon: Icons.calendar_month_outlined,
        title: AppStrings.get('interviews', lang),
        message: lang == 'hi' ? 'आपके आने वाले इंटरव्यू यहाँ दिखाई देंगे।' : (lang == 'kn' ? 'ನಿಮ್ಮ ಮುಂಬರುವ ಸಂದರ್ಶನಗಳು ಇಲ್ಲಿ ಕಾಣಿಸಿಕೊಳ್ಳುತ್ತವೆ.' : 'Your upcoming interviews will appear here.'),
      );
    }

    return RefreshIndicator(
      onRefresh: () async => ref.read(applicationProvider.notifier).fetchInterviews(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: state.interviews.length,
        itemBuilder: (context, index) {
          final application = state.interviews[index];
          final interview = application.interview!;
          
          return Container(
            margin: const EdgeInsets.only(bottom: 16),
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.primary.withOpacity(0.1)),
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 10)],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 44, height: 44,
                      decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
                      child: Icon(_getTypeIcon(interview.interviewType), color: AppColors.primary),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(application.job?.title ?? AppStrings.get('interviews', lang), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                          Text(application.job?.company?.name ?? 'Company', style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
                        ],
                      ),
                    ),
                  ],
                ),
                const Divider(height: 32),
                Row(
                  children: [
                    const Icon(Icons.access_time_rounded, size: 16, color: AppColors.primary),
                    const SizedBox(width: 8),
                    Text(Formatters.dateTime(DateTime.parse(interview.scheduledAt!)), style: const TextStyle(fontWeight: FontWeight.w600)),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    const Icon(Icons.location_on_outlined, size: 16, color: Colors.grey),
                    const SizedBox(width: 8),
                    Text(interview.location ?? 'Remote / Office', style: TextStyle(color: Colors.grey.shade700)),
                  ],
                ),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton(
                    onPressed: () => showDialog<void>(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('Interview details'),
                        content: Text('Type: ${interview.interviewType ?? 'scheduled'}\nLocation: ${interview.location ?? 'Remote / Office'}'),
                        actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))],
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: Text(AppStrings.get('see_all', lang), style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
