import 'package:dio/dio.dart';
import '../core/error.dart';
import 'api_service.dart';
import '../models/application_model.dart';

class ApplicationService {
  final ApiService _apiService;

  ApplicationService(this._apiService);

  Future<ApplicationModel> apply({
    required String jobId,
    String? coverLetter,
    String? resumeUrl,
    String? voiceResumeUrl,
  }) async {
    try {
      final response = await _apiService.post(
        '/applications',
        data: {
          'job_id': jobId,
          'cover_letter': coverLetter,
          'resume_url': resumeUrl,
          'voice_resume_url': voiceResumeUrl,
        },
      );
      final data = response.data as Map<String, dynamic>;
      return ApplicationModel.fromJson(
          data['application'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<List<ApplicationModel>> getApplications({
    int page = 1,
    int limit = 20,
    String? status,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'limit': limit,
      };
      if (status != null) queryParams['status'] = status;

      final response = await _apiService.get(
        '/applications',
        queryParameters: queryParams,
      );
      final data = response.data as Map<String, dynamic>;
      final applications = data['applications'] as List<dynamic>;
      return applications
          .map(
              (e) => ApplicationModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<ApplicationModel> getApplicationById(String id) async {
    try {
      final response = await _apiService.get('/applications/$id');
      final data = response.data as Map<String, dynamic>;
      return ApplicationModel.fromJson(
          data['application'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> withdrawApplication(String id) async {
    try {
      await _apiService.put(
        '/applications/$id/withdraw',
      );
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<ApplicationModel> getApplicationForJob(String jobId) async {
    try {
      final response = await _apiService.get('/applications/job/$jobId');
      final data = response.data as Map<String, dynamic>;
      return ApplicationModel.fromJson(
          data['application'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<bool> hasApplied(String jobId) async {
    try {
      final response = await _apiService.get(
        '/applications/check',
        queryParameters: {'job_id': jobId},
      );
      final data = response.data as Map<String, dynamic>;
      return data['has_applied'] as bool;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<int> getApplicationCount({String? status}) async {
    try {
      final queryParams = <String, dynamic>{};
      if (status != null) queryParams['status'] = status;
      final response = await _apiService.get(
        '/applications/count',
        queryParameters: queryParams,
      );
      final data = response.data as Map<String, dynamic>;
      return data['count'] as int;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<List<ApplicationModel>> getInterviews({
    int page = 1,
    int limit = 20,
  }) async {
    try {
      final response = await _apiService.get(
        '/applications/interviews',
        queryParameters: {'page': page, 'limit': limit},
      );
      final data = response.data as Map<String, dynamic>;
      final applications = data['applications'] as List<dynamic>;
      return applications
          .map(
              (e) => ApplicationModel.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> updateApplicationStatus({
    required String id,
    required String status,
    String? feedback,
    int? rating,
  }) async {
    try {
      await _apiService.put(
        '/applications/$id/status',
        data: {
          'status': status,
          'feedback': feedback,
          'rating': rating,
        },
      );
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }
}
