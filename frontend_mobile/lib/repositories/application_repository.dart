import '../services/application_service.dart';
import '../models/application_model.dart';

class ApplicationRepository {
  final ApplicationService _applicationService;

  ApplicationRepository(this._applicationService);

  Future<ApplicationModel> apply({
    required String jobId,
    String? coverLetter,
    String? resumeUrl,
    String? voiceResumeUrl,
  }) async {
    return await _applicationService.apply(
      jobId: jobId,
      coverLetter: coverLetter,
      resumeUrl: resumeUrl,
      voiceResumeUrl: voiceResumeUrl,
    );
  }

  Future<List<ApplicationModel>> getApplications({
    int page = 1,
    int limit = 20,
    String? status,
  }) async {
    return await _applicationService.getApplications(
      page: page,
      limit: limit,
      status: status,
    );
  }

  Future<ApplicationModel> getApplicationById(String id) async {
    return await _applicationService.getApplicationById(id);
  }

  Future<void> withdrawApplication(String id) async {
    await _applicationService.withdrawApplication(id);
  }

  Future<bool> hasApplied(String jobId) async {
    return await _applicationService.hasApplied(jobId);
  }

  Future<int> getApplicationCount({String? status}) async {
    return await _applicationService.getApplicationCount(status: status);
  }

  Future<List<ApplicationModel>> getInterviews({
    int page = 1,
    int limit = 20,
  }) async {
    return await _applicationService.getInterviews(page: page, limit: limit);
  }
}
