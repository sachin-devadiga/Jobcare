import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/job_model.dart';
import '../models/category_model.dart';
import '../repositories/job_repository.dart';
import '../core/error.dart';

class JobState {
  final List<JobModel> jobs;
  final List<JobModel> recommendedJobs;
  final List<JobModel> nearbyJobs;
  final List<JobModel> savedJobs;
  final List<CategoryModel> categories;
  final List<String> trendingSkills;
  final JobModel? selectedJob;
  final bool isLoading;
  final bool isLoadingMore;
  final bool isRecommendedLoading;
  final bool isNearbyLoading;
  final bool isSavedLoading;
  final Failure? failure;
  final int currentPage;
  final bool hasMore;
  final String? searchQuery;

  const JobState({
    this.jobs = const [],
    this.recommendedJobs = const [],
    this.nearbyJobs = const [],
    this.savedJobs = const [],
    this.categories = const [],
    this.trendingSkills = const [],
    this.selectedJob,
    this.isLoading = false,
    this.isLoadingMore = false,
    this.isRecommendedLoading = false,
    this.isNearbyLoading = false,
    this.isSavedLoading = false,
    this.failure,
    this.currentPage = 1,
    this.hasMore = true,
    this.searchQuery,
  });

  JobState copyWith({
    List<JobModel>? jobs,
    List<JobModel>? recommendedJobs,
    List<JobModel>? nearbyJobs,
    List<JobModel>? savedJobs,
    List<CategoryModel>? categories,
    List<String>? trendingSkills,
    JobModel? selectedJob,
    bool? isLoading,
    bool? isLoadingMore,
    bool? isRecommendedLoading,
    bool? isNearbyLoading,
    bool? isSavedLoading,
    Failure? failure,
    int? currentPage,
    bool? hasMore,
    String? searchQuery,
  }) {
    return JobState(
      jobs: jobs ?? this.jobs,
      recommendedJobs: recommendedJobs ?? this.recommendedJobs,
      nearbyJobs: nearbyJobs ?? this.nearbyJobs,
      savedJobs: savedJobs ?? this.savedJobs,
      categories: categories ?? this.categories,
      trendingSkills: trendingSkills ?? this.trendingSkills,
      selectedJob: selectedJob ?? this.selectedJob,
      isLoading: isLoading ?? this.isLoading,
      isLoadingMore: isLoadingMore ?? this.isLoadingMore,
      isRecommendedLoading: isRecommendedLoading ?? this.isRecommendedLoading,
      isNearbyLoading: isNearbyLoading ?? this.isNearbyLoading,
      isSavedLoading: isSavedLoading ?? this.isSavedLoading,
      failure: failure,
      currentPage: currentPage ?? this.currentPage,
      hasMore: hasMore ?? this.hasMore,
      searchQuery: searchQuery ?? this.searchQuery,
    );
  }
}

class JobNotifier extends StateNotifier<JobState> {
  final JobRepository _jobRepository;

  JobNotifier(this._jobRepository) : super(const JobState());

  Future<void> fetchJobs({bool refresh = false}) async {
    if (refresh) {
      state = state.copyWith(isLoading: true, currentPage: 1, hasMore: true);
    }
    try {
      final jobs = await _jobRepository.getJobs(page: state.currentPage);
      state = state.copyWith(
        jobs: refresh ? jobs : [...state.jobs, ...jobs],
        isLoading: false,
        hasMore: jobs.length >= 20,
        failure: null,
      );
    } on Failure catch (e) {
      state = state.copyWith(isLoading: false, failure: e);
    }
  }

  Future<void> loadMoreJobs() async {
    if (state.isLoadingMore || !state.hasMore) return;
    state = state.copyWith(isLoadingMore: true);
    final nextPage = state.currentPage + 1;
    try {
      final jobs = await _jobRepository.getJobs(page: nextPage);
      state = state.copyWith(
        jobs: [...state.jobs, ...jobs],
        isLoadingMore: false,
        currentPage: nextPage,
        hasMore: jobs.length >= 20,
      );
    } on Failure catch (e) {
      state = state.copyWith(isLoadingMore: false, failure: e);
    }
  }

  Future<void> fetchRecommendedJobs() async {
    state = state.copyWith(isRecommendedLoading: true);
    try {
      final jobs = await _jobRepository.getRecommendedJobs();
      state = state.copyWith(
        recommendedJobs: jobs,
        isRecommendedLoading: false,
      );
    } on Failure catch (_) {
      state = state.copyWith(isRecommendedLoading: false);
    }
  }

  Future<void> fetchNearbyJobs({
    required double latitude,
    required double longitude,
  }) async {
    state = state.copyWith(isNearbyLoading: true);
    try {
      final jobs = await _jobRepository.getNearbyJobs(
        latitude: latitude,
        longitude: longitude,
      );
      state = state.copyWith(nearbyJobs: jobs, isNearbyLoading: false);
    } on Failure catch (_) {
      state = state.copyWith(isNearbyLoading: false);
    }
  }

  Future<void> fetchSavedJobs() async {
    state = state.copyWith(isSavedLoading: true);
    try {
      final jobs = await _jobRepository.getSavedJobs();
      state = state.copyWith(savedJobs: jobs, isSavedLoading: false);
    } on Failure catch (_) {
      state = state.copyWith(isSavedLoading: false);
    }
  }

  Future<void> fetchJobDetail(String id) async {
    state = state.copyWith(isLoading: true);
    try {
      final job = await _jobRepository.getJobById(id);
      state = state.copyWith(selectedJob: job, isLoading: false);
    } on Failure catch (e) {
      state = state.copyWith(isLoading: false, failure: e);
    }
  }

  Future<void> fetchCategories() async {
    try {
      final categories = await _jobRepository.getCategories();
      state = state.copyWith(categories: categories);
    } on Failure catch (_) {}
  }

  Future<void> fetchTrendingSkills() async {
    try {
      final skills = await _jobRepository.getTrendingSkills();
      state = state.copyWith(trendingSkills: skills);
    } on Failure catch (_) {}
  }

  Future<void> toggleSaveJob(String jobId) async {
    final isSaved = await _jobRepository.isJobSaved(jobId);
    try {
      if (isSaved) {
        await _jobRepository.unsaveJob(jobId);
      } else {
        await _jobRepository.saveJob(jobId);
      }
      state = state.copyWith(
        jobs: state.jobs.map((j) {
          if (j.id == jobId) return j.copyWith(isSaved: !isSaved);
          return j;
        }).toList(),
      );
    } on Failure catch (_) {}
  }

  Future<void> searchJobs({
    required String query,
    String? category,
    String? location,
    String? jobType,
  }) async {
    state = state.copyWith(isLoading: true, searchQuery: query);
    try {
      final jobs = await _jobRepository.searchJobs(
        query: query,
        category: category,
        location: location,
        jobType: jobType,
      );
      state = state.copyWith(jobs: jobs, isLoading: false, failure: null);
    } on Failure catch (e) {
      state = state.copyWith(isLoading: false, failure: e);
    }
  }

  Future<void> refreshAll({
    double? latitude,
    double? longitude,
  }) async {
    await Future.wait([
      fetchJobs(refresh: true),
      fetchRecommendedJobs(),
      if (latitude != null && longitude != null)
        fetchNearbyJobs(latitude: latitude, longitude: longitude),
      fetchCategories(),
      fetchTrendingSkills(),
    ]);
  }

  void setSelectedJob(JobModel? job) {
    state = state.copyWith(selectedJob: job);
  }

  void clearSearch() {
    state = state.copyWith(searchQuery: null, jobs: []);
  }

  void clearFailure() {
    state = state.copyWith(failure: null);
  }
}
