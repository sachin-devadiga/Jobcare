import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/providers.dart';
import '../providers/job_provider.dart';
import '../routes/route_names.dart';
import '../theme/app_colors.dart';
import '../widgets/job_card.dart';
import '../widgets/shimmer_loading.dart';
import '../widgets/empty_state.dart';
import '../widgets/error_widget.dart';
import '../core/localization.dart';

class JobsScreen extends ConsumerStatefulWidget {
  const JobsScreen({super.key});

  @override
  ConsumerState<JobsScreen> createState() => _JobsScreenState();
}

class _JobsScreenState extends ConsumerState<JobsScreen> {
  final ScrollController _scrollController = ScrollController();
  String _selectedCategory = 'all';

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(jobProvider.notifier).fetchJobs(refresh: true);
    });
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 200) {
      ref.read(jobProvider.notifier).loadMoreJobs();
    }
  }

  void _filterByCategory(String cat) {
    setState(() => _selectedCategory = cat);
    if (cat == 'all') {
      ref.read(jobProvider.notifier).fetchJobs(refresh: true);
    } else {
      ref.read(jobProvider.notifier).searchJobs(query: '', category: cat);
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(jobProvider);
    final lang = ref.watch(languageProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        elevation: 0,
        title: Text(AppStrings.get('find_jobs', lang), 
          style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            icon: const Icon(Icons.tune_rounded, color: Colors.white),
            onPressed: () => _showFilterSheet(lang),
          ),
        ],
      ),
      body: Column(
        children: [
          _buildCategoryBar(lang),
          Expanded(
            child: _buildBody(state, lang),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(JobState state, String lang) {
    if (state.isLoading && state.jobs.isEmpty) {
      return ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: 5,
        itemBuilder: (context, index) => const ShimmerLoading(width: double.infinity, height: 160, margin: EdgeInsets.only(bottom: 16)),
      );
    }

    if (state.jobs.isEmpty) {
      return EmptyState(
        icon: Icons.search_off_rounded,
        title: AppStrings.get('no_jobs_found', lang),
        message: AppStrings.get('try_voice_search', lang),
      );
    }

    return RefreshIndicator(
      onRefresh: () async => ref.read(jobProvider.notifier).fetchJobs(refresh: true),
      child: ListView.builder(
        controller: _scrollController,
        padding: const EdgeInsets.all(16),
        itemCount: state.jobs.length + (state.isLoadingMore ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == state.jobs.length) {
            return const Padding(padding: EdgeInsets.all(20), child: Center(child: CircularProgressIndicator()));
          }
          return JobCard(
            job: state.jobs[index],
            onTap: () => context.push('${RouteNames.jobDetail}/${state.jobs[index].id}'),
          );
        },
      ),
    );
  }

  Widget _buildCategoryBar(String lang) {
    final categories = ['all', 'delivery', 'driver', 'construction', 'security', 'factory'];
    return Container(
      height: 50,
      margin: const EdgeInsets.symmetric(vertical: 12),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final catKey = categories[index];
          final isSelected = _selectedCategory == catKey;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(AppStrings.get(catKey, lang)),
              selected: isSelected,
              onSelected: (selected) {
                if (selected) _filterByCategory(catKey);
              },
              selectedColor: AppColors.primary,
              labelStyle: TextStyle(color: isSelected ? Colors.white : AppColors.primary, fontWeight: FontWeight.bold),
              backgroundColor: AppColors.primary.withOpacity(0.05),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20), side: BorderSide.none),
              showCheckmark: false,
            ),
          );
        },
      ),
    );
  }

  void _showFilterSheet(String lang) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(AppStrings.get('filter_jobs', lang), style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),
            Text(AppStrings.get('salary_range', lang), style: const TextStyle(fontWeight: FontWeight.bold)),
            // In a real app, you'd put a range slider here
            const SizedBox(height: 40),
            ElevatedButton(
              onPressed: () {
                // Apply filter logic
                Navigator.pop(context);
                ref.read(jobProvider.notifier).fetchJobs(refresh: true);
              },
              child: Text(AppStrings.get('apply_filters', lang)),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
