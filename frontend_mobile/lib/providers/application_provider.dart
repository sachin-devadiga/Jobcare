import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/application_model.dart';
import '../repositories/application_repository.dart';
import '../core/error.dart';

class ApplicationState {
  final List<ApplicationModel> applications;
  final List<ApplicationModel> interviews;
  final bool isLoading;
  final bool isApplying;
  final Failure? failure;
  final bool hasMore;
  final int currentPage;

  const ApplicationState({
    this.applications = const [],
    this.interviews = const [],
    this.isLoading = false,
    this.isApplying = false,
    this.failure,
    this.hasMore = true,
    this.currentPage = 1,
  });

  ApplicationState copyWith({
    List<ApplicationModel>? applications,
    List<ApplicationModel>? interviews,
    bool? isLoading,
    bool? isApplying,
    Failure? failure,
    bool? hasMore,
    int? currentPage,
  }) {
    return ApplicationState(
      applications: applications ?? this.applications,
      interviews: interviews ?? this.interviews,
      isLoading: isLoading ?? this.isLoading,
      isApplying: isApplying ?? this.isApplying,
      failure: failure,
      hasMore: hasMore ?? this.hasMore,
      currentPage: currentPage ?? this.currentPage,
    );
  }
}

class ApplicationNotifier extends StateNotifier<ApplicationState> {
  final ApplicationRepository _applicationRepository;

  ApplicationNotifier(this._applicationRepository)
      : super(const ApplicationState());

  Future<void> fetchApplications({bool refresh = false}) async {
    if (refresh) {
      state = state.copyWith(isLoading: true, currentPage: 1, hasMore: true);
    }
    try {
      final applications = await _applicationRepository.getApplications(
        page: state.currentPage,
      );
      state = state.copyWith(
        applications:
            refresh ? applications : [...state.applications, ...applications],
        isLoading: false,
        hasMore: applications.length >= 20,
        failure: null,
      );
    } on Failure catch (e) {
      state = state.copyWith(isLoading: false, failure: e);
    }
  }

  Future<void> loadMoreApplications() async {
    if (state.isLoading || !state.hasMore) return;
    state = state.copyWith(isLoading: true);
    final nextPage = state.currentPage + 1;
    try {
      final applications =
          await _applicationRepository.getApplications(page: nextPage);
      state = state.copyWith(
        applications: [...state.applications, ...applications],
        isLoading: false,
        currentPage: nextPage,
        hasMore: applications.length >= 20,
      );
    } on Failure catch (e) {
      state = state.copyWith(isLoading: false, failure: e);
    }
  }

  Future<void> fetchInterviews() async {
    try {
      final interviews = await _applicationRepository.getInterviews();
      state = state.copyWith(interviews: interviews);
    } on Failure catch (_) {}
  }

  Future<bool> apply({
    required String jobId,
    String? coverLetter,
    String? resumeUrl,
    String? voiceResumeUrl,
  }) async {
    state = state.copyWith(isApplying: true, failure: null);
    try {
      final application = await _applicationRepository.apply(
        jobId: jobId,
        coverLetter: coverLetter,
        resumeUrl: resumeUrl,
        voiceResumeUrl: voiceResumeUrl,
      );
      state = state.copyWith(
        applications: [application, ...state.applications],
        isApplying: false,
      );
      return true;
    } on Failure catch (e) {
      state = state.copyWith(isApplying: false, failure: e);
      return false;
    }
  }

  Future<void> withdrawApplication(String id) async {
    try {
      await _applicationRepository.withdrawApplication(id);
      state = state.copyWith(
        applications: state.applications
            .map((a) =>
                a.id == id ? a.copyWith(status: ApplicationStatus.withdrawn) : a)
            .toList(),
      );
    } on Failure catch (e) {
      state = state.copyWith(failure: e);
    }
  }

  Future<bool> hasApplied(String jobId) async {
    try {
      return await _applicationRepository.hasApplied(jobId);
    } catch (_) {
      return false;
    }
  }

  void clearFailure() {
    state = state.copyWith(failure: null);
  }
}
