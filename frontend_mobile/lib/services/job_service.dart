import 'package:dio/dio.dart';
import '../core/error.dart';
import 'api_service.dart';
import '../models/job_model.dart';
import '../models/category_model.dart';

class JobService {
  final ApiService _apiService;

  JobService(this._apiService);

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
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'limit': limit,
      };
      if (category != null) queryParams['category'] = category;
      if (search != null) queryParams['search'] = search;
      if (location != null) queryParams['location'] = location;
      if (jobType != null) queryParams['job_type'] = jobType;
      if (experienceLevel != null) {
        queryParams['experience_level'] = experienceLevel;
      }
      if (salaryMin != null) queryParams['salary_min'] = salaryMin;
      if (salaryMax != null) queryParams['salary_max'] = salaryMax;
      if (sortBy != null) queryParams['sort_by'] = sortBy;
      if (latitude != null) queryParams['latitude'] = latitude;
      if (longitude != null) queryParams['longitude'] = longitude;
      if (radiusKm != null) queryParams['radius_km'] = radiusKm;

      final response = await _apiService.get(
        '/jobs',
        queryParameters: queryParams,
      );
      final data = response.data as Map<String, dynamic>;
      final jobsList = (data['jobs'] ?? []) as List<dynamic>;
      return jobsList
          .map((e) => JobModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<JobModel> getJobById(String id) async {
    try {
      final response = await _apiService.get('/jobs/$id');
      final data = response.data as Map<String, dynamic>;
      return JobModel.fromJson(data['job'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<List<JobModel>> getRecommendedJobs({int limit = 10}) async {
    try {
      final response = await _apiService.get(
        '/jobs/recommended',
        queryParameters: {'limit': limit},
      );
      final data = response.data as Map<String, dynamic>;
      final jobsList = (data['jobs'] ?? []) as List<dynamic>;
      return jobsList
          .map((e) => JobModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<List<JobModel>> getNearbyJobs({
    required double latitude,
    required double longitude,
    double radiusKm = 10,
    int limit = 20,
  }) async {
    try {
      final response = await _apiService.get(
        '/jobs/nearby',
        queryParameters: {
          'latitude': latitude,
          'longitude': longitude,
          'radius_km': radiusKm,
          'limit': limit,
        },
      );
      final data = response.data as Map<String, dynamic>;
      final jobsList = (data['jobs'] ?? []) as List<dynamic>;
      return jobsList
          .map((e) => JobModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<List<JobModel>> getSavedJobs({int page = 1, int limit = 20}) async {
    try {
      final response = await _apiService.get(
        '/jobs/saved',
        queryParameters: {'page': page, 'limit': limit},
      );
      final data = response.data as Map<String, dynamic>;
      final jobsList = (data['jobs'] ?? []) as List<dynamic>;
      return jobsList
          .map((e) => JobModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> saveJob(String jobId) async {
    try {
      await _apiService.post('/jobs/$jobId/save');
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> unsaveJob(String jobId) async {
    try {
      await _apiService.delete('/jobs/$jobId/save');
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<List<JobModel>> searchJobs({
    required String query,
    int page = 1,
    int limit = 20,
    String? category,
    String? location,
    String? jobType,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'query': query,
        'page': page,
        'limit': limit,
      };
      if (category != null) queryParams['category'] = category;
      if (location != null) queryParams['location'] = location;
      if (jobType != null) queryParams['job_type'] = jobType;

      final response = await _apiService.get(
        '/jobs/search',
        queryParameters: queryParams,
      );
      final data = response.data as Map<String, dynamic>;
      final jobsList = (data['jobs'] ?? []) as List<dynamic>;
      return jobsList
          .map((e) => JobModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<List<CategoryModel>> getCategories() async {
    try {
      final response = await _apiService.get('/categories');
      final data = response.data as Map<String, dynamic>;
      final categories = data['categories'] as List<dynamic>;
      return categories
          .map((e) => CategoryModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<List<JobModel>> getJobsByCategory(
    String categoryId, {
    int page = 1,
    int limit = 20,
  }) async {
    try {
      final response = await _apiService.get(
        '/categories/$categoryId/jobs',
        queryParameters: {'page': page, 'limit': limit},
      );
      final data = response.data as Map<String, dynamic>;
      final jobsList = (data['jobs'] ?? []) as List<dynamic>;
      return jobsList
          .map((e) => JobModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<List<String>> getTrendingSkills() async {
    try {
      final response = await _apiService.get('/jobs/trending-skills');
      final data = response.data as Map<String, dynamic>;
      final skills = data['skills'] as List<dynamic>;
      return skills.map((e) => e as String).toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> reportJob(String jobId, {String? reason}) async {
    try {
      await _apiService.post(
        '/jobs/$jobId/report',
        data: {'reason': reason ?? 'inappropriate'},
      );
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<int> getJobApplicantsCount(String jobId) async {
    try {
      final response = await _apiService.get('/jobs/$jobId/applicants/count');
      final data = response.data as Map<String, dynamic>;
      return data['count'] as int;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }
}
