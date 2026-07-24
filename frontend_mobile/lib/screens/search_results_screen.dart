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
import '../widgets/search_bar_widget.dart';
import '../core/localization.dart';

class SearchResultsScreen extends ConsumerStatefulWidget {
  final String query;
  const SearchResultsScreen({super.key, required this.query});

  @override
  ConsumerState<SearchResultsScreen> createState() => _SearchResultsScreenState();
}

class _SearchResultsScreenState extends ConsumerState<SearchResultsScreen> {
  late String _query;
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _query = widget.query;
    if (_query.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _performSearch());
    }
  }

  void _performSearch() {
    ref.read(jobProvider.notifier).searchJobs(query: _query);
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
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => context.pop(),
        ),
        title: Text(
          lang == 'hi' ? ' "$_query" के परिणाम' : (lang == 'kn' ? ' "$_query" ಗೆ ಫಲಿತಾಂಶಗಳು' : 'Results for "$_query"'), 
          style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)
        ),
      ),
      body: Column(
        children: [
          Container(
            color: AppColors.primary,
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
            child: SearchBarWidget(initialValue: _query, onSubmitted: (q) {
              setState(() => _query = q);
              _performSearch();
            }),
          ),
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
        padding: const EdgeInsets.all(20),
        itemCount: 5,
        itemBuilder: (context, index) => const ShimmerLoading(width: double.infinity, height: 120, margin: EdgeInsets.only(bottom: 12)),
      );
    }

    if (state.jobs.isEmpty) {
      return EmptyState(
        icon: Icons.search_off_rounded,
        title: AppStrings.get('no_jobs_found', lang),
        message: lang == 'en' 
            ? 'Try searching with different keywords.' 
            : (lang == 'hi' ? 'कृपया अलग शब्दों के साथ सर्च करें।' : 'ದಯವಿಟ್ಟು ಬೇರೆ ಪದಗಳೊಂದಿಗೆ ಹುಡುಕಿ.'),
      );
    }

    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(20),
      itemCount: state.jobs.length,
      itemBuilder: (context, index) => JobCard(
        job: state.jobs[index],
        onTap: () => context.push('${RouteNames.jobDetail}/${state.jobs[index].id}'),
      ),
    );
  }
}
