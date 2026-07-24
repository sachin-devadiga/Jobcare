import '../services/job_service.dart';
import '../services/storage_service.dart';
import '../models/job_model.dart';
import '../models/category_model.dart';

class JobRepository {
  final JobService _jobService;
  final StorageService _storageService;

  JobRepository(this._jobService, this._storageService);

  Future<List<JobModel>> getJobs({
    int page = 1,
    int limit = 20,
    String? category,
    String? search,
    String? location,
    String? jobType,
    String? experienceLevel,
    double? salaryMin,
    double? salaryMax,
    String? sortBy,
    double? latitude,
    double? longitude,
    double? radiusKm,
  }) async {
    return await _jobService.getJobs(
      page: page,
      limit: limit,
      category: category,
      search: search,
      location: location,
      jobType: jobType,
      experienceLevel: experienceLevel,
      salaryMin: salaryMin,
      salaryMax: salaryMax,
      sortBy: sortBy,
      latitude: latitude,
      longitude: longitude,
      radiusKm: radiusKm,
    );
  }

  Future<JobModel> getJobById(String id) async {
    return await _jobService.getJobById(id);
  }

  Future<List<JobModel>> getRecommendedJobs({int limit = 10}) async {
    return await _jobService.getRecommendedJobs(limit: limit);
  }

  Future<List<JobModel>> getNearbyJobs({
    required double latitude,
    required double longitude,
    double radiusKm = 10,
    int limit = 20,
  }) async {
    return await _jobService.getNearbyJobs(
      latitude: latitude,
      longitude: longitude,
      radiusKm: radiusKm,
      limit: limit,
    );
  }

  Future<List<JobModel>> getSavedJobs({int page = 1, int limit = 20}) async {
    return await _jobService.getSavedJobs(page: page, limit: limit);
  }

  Future<void> saveJob(String jobId) async {
    await _jobService.saveJob(jobId);
    await _storageService.addSavedJob(jobId);
  }

  Future<void> unsaveJob(String jobId) async {
    await _jobService.unsaveJob(jobId);
    await _storageService.removeSavedJob(jobId);
  }

  Future<bool> isJobSaved(String jobId) async {
    return await _storageService.isJobSaved(jobId);
  }

  Future<List<JobModel>> searchJobs({
    required String query,
    int page = 1,
    int limit = 20,
    String? category,
    String? location,
    String? jobType,
  }) async {
    return await _jobService.searchJobs(
      query: query,
      page: page,
      limit: limit,
      category: category,
      location: location,
      jobType: jobType,
    );
  }

  Future<List<CategoryModel>> getCategories() async {
    return await _jobService.getCategories();
  }

  Future<List<JobModel>> getJobsByCategory(
    String categoryId, {
    int page = 1,
    int limit = 20,
  }) async {
    return await _jobService.getJobsByCategory(categoryId, page: page, limit: limit);
  }

  Future<List<String>> getTrendingSkills() async {
    return await _jobService.getTrendingSkills();
  }

  Future<int> getJobApplicantsCount(String jobId) async {
    return await _jobService.getJobApplicantsCount(jobId);
  }
}
