import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/user_model.dart';
import '../providers/providers.dart';
import '../providers/auth_provider.dart';
import '../providers/job_provider.dart';
import '../providers/location_provider.dart';
import '../providers/notification_provider.dart';
import '../routes/route_names.dart';
import '../theme/app_colors.dart';
import '../widgets/job_card.dart';
import '../widgets/category_chip.dart';
import '../widgets/section_header.dart';
import '../widgets/search_bar_widget.dart';
import '../core/localization.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(jobProvider.notifier).refreshAll();
      ref.read(locationProvider.notifier).getCurrentLocation();
      ref.read(notificationProvider.notifier).fetchUnreadCount();
    });
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final jobState = ref.watch(jobProvider);
    final lang = ref.watch(languageProvider);
    final user = authState.user;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        elevation: 0,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${AppStrings.get('welcome_worker', lang).split(',').first}, ${user?.name.split(' ').first ?? 'Worker'}',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            Text(
              AppStrings.get('find_job_today', lang),
              style: const TextStyle(fontSize: 12, color: Colors.white70),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline_rounded, color: Colors.white),
            onPressed: () => context.push(RouteNames.voiceHelp),
            tooltip: AppStrings.get('voice_help_title', lang),
          ),
          IconButton(
            icon: const Icon(Icons.notifications_none_rounded, color: Colors.white),
            onPressed: () => context.push(RouteNames.notifications),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: CustomScrollView(
        physics: const BouncingScrollPhysics(),
        slivers: [
          SliverToBoxAdapter(
            child: Container(
              color: AppColors.primary,
              padding: const EdgeInsets.fromLTRB(20, 10, 20, 30),
              child: SearchBarWidget(
                onSubmitted: (query) {
                  if (query.isNotEmpty) {
                    context.push('${RouteNames.searchResults}?query=$query');
                  }
                },
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 24),
                  
                  // Wired up Voice Hero Card
                  _buildVoiceHero(lang),
                  
                  const SizedBox(height: 32),
                  SectionHeader(
                    title: AppStrings.get('job_categories', lang),
                    onSeeAll: () => context.push(RouteNames.jobs),
                  ),
                  const SizedBox(height: 16),
                  _buildCategoryList(jobState),

                  const SizedBox(height: 32),
                  SectionHeader(
                    title: AppStrings.get('jobs_for_you', lang),
                    onSeeAll: () => context.push(RouteNames.jobs),
                  ),
                  const SizedBox(height: 16),
                  _buildJobVerticalList(jobState.recommendedJobs),
                  
                  const SizedBox(height: 120),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVoiceHero(String lang) {
    return GestureDetector(
      onTap: () => context.push(RouteNames.voiceAssistant),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [AppColors.primary, Color(0xFF1976D2)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(color: AppColors.primary.withOpacity(0.3), blurRadius: 20, offset: const Offset(0, 10))
          ],
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    AppStrings.get('hero_title', lang),
                    style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w900),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    AppStrings.get('hero_subtitle', lang),
                    style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 14, fontWeight: FontWeight.w500),
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: const BoxDecoration(color: AppColors.secondary, shape: BoxShape.circle),
              child: const Icon(Icons.mic_rounded, color: Colors.black, size: 32),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCategoryList(JobState state) {
    return SizedBox(
      height: 110,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: state.categories.length,
        itemBuilder: (context, index) => CategoryChip(
          category: state.categories[index],
          onTap: () {
            // Navigate to JobsScreen with selected category
            context.push(RouteNames.jobs);
            // Optional: You can pass state or extra to filter directly
          },
        ),
      ),
    );
  }

  Widget _buildJobVerticalList(List<dynamic> jobs) {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: jobs.length,
      itemBuilder: (context, index) => JobCard(
        job: jobs[index],
        onTap: () => context.push('${RouteNames.jobDetail}/${jobs[index].id}'),
      ),
    );
  }
}
